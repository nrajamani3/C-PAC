# Import packages
# import os
import sys
import re
import commands
import nipype.pipeline.engine as pe
import nipype.interfaces.utility as util
import nipype.interfaces.fsl as fsl



# TVI Workflow function
def create_tiv_bv_wf(wf_name='tiv_bv_wf'):
    '''
    Workflow that will compute the total intracranial volume (TIV) and total
    brain volume (BV) of an anatomical image, respectively.

    For computing TIV, the inverse of the determinant of the affine transform-
    ation matrix is computed from brain_to_template.mat (shown below).

    For computing brain volume, the white and grey matter segments are added
    together, brain_pve_1 + brain_pve_2 (shown below).

    Brain extraction and bias correction stage:
    
    anat_in --> BET brain extraction (0.2 cutoff) = brain_biased
    brain_biased --> FAST bias field estimation = brain_bias
    anat_in / brain_bias = brain_bias_corrected
    brain_bias_corrected --> BET brain extraction (0.3 cutoff) = final_brain
    
    Registration/Segmentation stage:
    
                   Template
                      |
                      V
    final_brain --> FLIRT = brain_to_template.mat affine matrix
    final_brain --> FAST = brain_pve_1, brain_pve_2

    Resource for this TIV/BV process:
    http://enigma.ini.usc.edu/protocols/imaging-protocols/protocol-for-brain-and-intracranial-volumes/#fsl
    
    Thanks to the folks of the ENIGMA network for providing this workflow.
    
    '''

    # Create workflow
    wf = pe.Workflow(name=wf_name)

    # Input Node
    inputNode = pe.Node(interface=util.IdentityInterface(fields=['reor_brain','flirt_template']),
                        name='inputspec')

    # --- For Brain extraction and bias correction ---
    # Initial brain extraction node
    initBETNode = pe.Node(interface=fsl.BET(),
                          name='init_bet')
    # Setup fractional intensity cutoff
    initBETNode.inputs.frac = 0.2

    # FAST node for calculating bias field
    fastBiasNode = pe.Node(interface=fsl.FAST(),
                       name='fast_bias')
    # Output the estimated bias field
    fastBiasNode.inputs.output_biasfield = True
    # Turn off partial volume estimation
    fastBiasNode.inputs.no_pve = True

    # FSLMATHS node for bias correction
    fslmathsNode = pe.Node(interface=fsl.BinaryMaths(),
                           name='fsl_div')
    # Set the node to perform division
    fslmathsNode.inputs.operation = 'div'

    # Setup final brain extraction node (bias corrected)
    finBETNode = pe.Node(interface=fsl.BET(),
                         name='fin_bet')
    # Setup fractional intensity cutoff
    finBETNode.inputs.frac = 0.3

    # Connect the BET/bias stage of the workflow
    wf.connect(inputNode,'reor_brain',initBETNode,'in_file')
    wf.connect(initBETNode,'out_file',fastBiasNode,'in_files')
    wf.connect(inputNode,'reor_brain',fslmathsNode,'in_file')
    wf.connect(fastBiasNode,'bias_field',fslmathsNode,'operand_file')
    wf.connect(fslmathsNode,'out_file',finBETNode,'in_file')

    # --- For grey/white segmentation ---
    # FLIRT Linear Registration node
    flirtNode = pe.Node(interface=fsl.FLIRT(),
                        name='flirt_reg')

    # FAST Anatomical segmentation (grey/white/csf) node
    fastSegNode = pe.Node(interface=fsl.FAST(),
                          name='fast_seg')

    # Connect the reg/seg stage of the workflow
    wf.connect(finBETNode,'out_file',flirtNode,'in_file')
    wf.connect(inputNode,'flirt_template',flirtNode,'reference')
    wf.connect(finBETNode,'out_file',fastSegNode,'in_files')

    # --- TIV calc. stage ---
    tivNode = pe.Node(util.Function(input_names=['in_matrix'],
                                    output_names=['inv_det'],
                                    function=inv_det),
                      name='tiv_calc')
    
    # Connect the affine matrix to the TIV node
    wf.connect(flirtNode,'out_matrix_file',tivNode,'in_matrix')

    # --- Brain Volume calc. stage ---
    # Tissue volume calculation nodes
    gmVolNode = pe.Node(interface=fsl.ImageStats(),
                        name='gm_vol')
    wmVolNode = pe.Node(interface=fsl.ImageStats(),
                        name='wm_vol')

    # Tell fslstats nodes to compute volume and non-zero mean
    gmVolNode.inputs.op_string = '-V -M'
    wmVolNode.inputs.op_string = '-V -M'

    # Separate input files - create separation nodes
    gmSepNode = pe.Node(interface=util.Select(),name='gm_sep')
    gmSepNode.inputs.index = [1]
    
    wmSepNode = pe.Node(interface=util.Select(),name='wm_sep')
    wmSepNode.inputs.index = [2]
    
    # Connect the output list of segmented volumes to separation nodes
    wf.connect(fastSegNode,'partial_volume_files',gmSepNode,'inlist')
    wf.connect(fastSegNode,'partial_volume_files',wmSepNode,'inlist')
    
    # Connect the WM/GM segments to the volume calculating nodes
    wf.connect(gmSepNode,'out',gmVolNode,'in_file')
    wf.connect(wmSepNode,'out',wmVolNode,'in_file')

    # BV calculation node (combine grey/white tissue)
    bvNode = pe.Node(util.Function(input_names=['gm_stats',
                                               'wm_stats'],
                                   output_names=['gw_vol'],
                                   function=comb_grey_white),
                     name='bv_calc')

    # Connect the grey/white matter output stats to bvNode
    wf.connect(gmVolNode,'out_stat',bvNode,'gm_stats')
    wf.connect(wmVolNode,'out_stat',bvNode,'wm_stats')

    # --- Output stage ---
    # Final outputs node
    outputNode = pe.Node(interface=util.IdentityInterface(fields=['tiv_out',
                                                                  'bv_out']),
                         name='outputspec')

    # Connect the output stage of the workflow
    wf.connect(tivNode,'inv_det',outputNode,'tiv_out')
    wf.connect(bvNode,'gw_vol',outputNode,'bv_out')

    # Return the workflow
    return wf

# CSV create/merge/write function
def csv_merge_write(voldic_in,tiv_in,bv_in):
    
    # Import packages
    import os
    
    # Define the output csv file
    csv_out_file = os.path.join(os.getcwd(),'seg_vols.csv')
    
    # Open CSV file for writing
    f = open(csv_out_file,'wb')
    f.write('Segment name,' + 'No. of Voxels,' + 'Volume (mm^3),' + 
            'Est. TIV factor,' + 'Est. BV (mm^3)' + '\n')
    # Iterate through the different segments to get their volumes
    ctr = 0
    for seg, label in voldic_in.iteritems():
        if ctr == 0:
            f.write(str(seg) + ',' + str(label[0]) + ',' + str(label[1]) + ',' +
                    str(tiv_in) + ',' + str(bv_in) + '\n')
        else:
            f.write(str(seg) + ',' + str(label[0]) + ',' + str(label[1]) + '\n')
        ctr+=1
    f.close()
    
    return csv_out_file


# Combine grey/white matter volumes function
def comb_grey_white(gm_stats,wm_stats):
    '''
    Function which computes the total brain volume by combining the grey and
    white matter volumes and scaling each by their non-zero voxel means
    
    Inputs:
    gm_stats: list
              [number_of_voxels,volume_in_mm3,non_zero_mean_intensity]

    wm_stats: list
              [number_of_voxels,volume_in_mm3,non_zero_mean_intensity]

    Outputs:
    gw_vol: float
            Combined grey and white matter volumes (scaled by avg intensities)
    '''
    
    # Multiply the non-zero voxel intensity means by g/w matter vol (mm^3)
    gm_vol = gm_stats[1]*gm_stats[2]
    wm_vol = wm_stats[1]*wm_stats[2]

    # Combine to form the total brain volume
    gw_vol = float(gm_vol + wm_vol)
    
    # Return the brain volume
    return gw_vol

# Inverse of determinant calculation function
def inv_det(in_matrix):
    '''
    Function that computes the inverse determinant of a matrix
    '''
    # Import packages
    import numpy as np
    import scipy.linalg as la

    mat = np.array([])
    # Loop until error
    with open(in_matrix) as f:
        for i,line in enumerate(f):
            linelist = line.split()
            print linelist
            array = np.array(linelist,dtype='float64')
            # If we haven't written to the matrix yet
            if len(mat) == 0:
                mat = np.concatenate((mat,array))
            # Otherwise, stack vertically to form matrix
            else:
                mat = np.vstack((mat,array))
                
    # Find the determinant of the input matrix
    det_mat = la.det(mat)
    # ... and compute the inverse
    inv_det = 1.0/det_mat

    # Return the inverse-determinant
    return inv_det


# Voxel counter and volume compute function
def vol_ctr(seg_nifti_file):
    ''' 
    Function which calculates the volume in voxels and mm^3 of a segmented
    nifti file (calculated by fsl's run_first_all command).
    '''

    # Import packages
    import numpy as np
    import nibabel as nb

    # Segment labels dictionary
    labels = {'Left-Thalamus-Proper':10,
              'Left-Caudate':11,
              'Left-Putamen':12,
              'Left-Pallidum':13,
              'Brain-Stem':16,
              'Left-Hippocampus':17,
              'Left-Amygdala':18,
              'Left-Accumbens-area':26,
              'Right-Thalamus-Proper':49,
              'Right-Caudate':50,
              'Right-Putamen':51,
              'Right-Pallidum':52,
              'Right-Hippocampus':53,
              'Right-Amygdala':54,
              'Right-Accumbens-area':58}
    
    # Get data and header info
    segments = nb.load(seg_nifti_file)
    header = segments.get_header()
    seg_data = segments.get_data()
    dims = header.get_zooms()
    # Get mm^3
    mm_3 = dims[0]*dims[1]*dims[2]
    vol_dic = {}
   
    # Iterate through the different segments to get their volumes
    for seg, label in labels.iteritems():
        no_vox = np.count_nonzero(seg_data==label)
        vol_mm3 = no_vox*mm_3
        vol_dic[seg] = [no_vox,vol_mm3]

    # Return the volume segments dictionary
    return vol_dic


def pick_wm_0(probability_maps):

    """
    Returns the csf probability map from the list of segmented probability maps

    Parameters
    ----------

    probability_maps : list (string)
        List of Probability Maps

    Returns
    -------

    file : string
        Path to segment_prob_0.nii.gz is returned

    """

    import sys
    import os

    if(isinstance(probability_maps, list)):

        if(len(probability_maps) == 1):
            probability_maps = probability_maps[0]
        for file in probability_maps:
            print file
            if file.endswith("prob_0.nii.gz"):

                return file
    return None


def pick_wm_1(probability_maps):

    """
    Returns the gray matter probability map from the list of segmented probability maps

    Parameters
    ----------

    probability_maps : list (string)
        List of Probability Maps

    Returns
    -------

    file : string
        Path to segment_prob_1.nii.gz is returned

    """
    import sys
    import os

    if(isinstance(probability_maps, list)):

        if(len(probability_maps) == 1):
            probability_maps = probability_maps[0]
        for file in probability_maps:
            print file
            if file.endswith("prob_1.nii.gz"):

                return file
    return None


def pick_wm_2(probability_maps):

    """
    Returns the white matter probability map from the list of segmented probability maps

    Parameters
    ----------

    probability_maps : list (string)
        List of Probability Maps

    Returns
    -------

    file : string
        Path to segment_prob_2.nii.gz is returned

    """
    import sys
    import os
    if(isinstance(probability_maps, list)):

        if(len(probability_maps) == 1):
            probability_maps = probability_maps[0]
        for file in probability_maps:
            print file
            if file.endswith("prob_2.nii.gz"):

                return file
    return None


