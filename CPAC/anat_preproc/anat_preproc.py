import os
from nipype.interfaces.afni import preprocess
#from nipype.interfaces.afni import utils as afni_utils
import nipype.pipeline.engine as pe
import nipype.interfaces.afni as afni
import nipype.interfaces.utility as util

def create_skullstrip_wf(qc_figures=False):
    """     
    Raw mprage file is skullstripped.
    
    Returns 
    -------
    wf : workflow
        SkullStripping Workflow
    
    Notes
    -----
    `Source <https://github.com/FCP-INDI/C-PAC/blob/master/CPAC/anat_preproc/anat_preproc.py>`_
    
    Workflow Inputs::
        inputspec.anat : mprage file or a list of mprage nifti file 
            User input anatomical(T1) Image, in any of the 8 orientations
    
    Workflow Outputs::
        outputspec.skullstrip : nifti file
            Skull Stripped mprage file with normalized intensities.
            
    Order of commands:
    
    - SkullStripping the image.  For details see `3dSkullStrip <http://afni.nimh.nih.gov/pub/dist/doc/program_help/3dSkullStrip.html>`_::
    
        3dSkullStrip -input mprage_RPI.nii.gz -o_ply mprage_RPI_3dT.nii.gz
    
    - The skull stripping step modifies the intensity values.
    To get back the original intensity values, we do an element wise product
    of RPI data with step function of skull Stripped data. 
    For details see `3dcalc 
    <http://afni.nimh.nih.gov/pub/dist/doc/program_help/3dcalc.html>`_::
    
        3dcalc -a mprage_RPI.nii.gz -b mprage_RPI_3dT.nii.gz -expr 'a*step(b)'
         -prefix mprage_RPI_3dc.nii.gz

    Examples
    --------
    >>> from CPAC import anat_preproc
    >>> wf = anat_preproc.create_skullstrip_wf()
    >>> wf.inputs.inputspec.anat='mprage.nii.gz'
    >>> wf.run() #doctest: +SKIP     
    """
    wf = pe.Workflow(name='skullstrip')
    in_node = pe.Node(util.IdentityInterface(fields=['anat']),
                        name='inputspec')
    fields = ['skullstrip']
    if qc_figures:
        fields += ['x_fig', 'z_fig']
    out_node = pe.Node(util.IdentityInterface(fields=fields),
                         name='outputspec')

    skullstrip = pe.Node(interface=preprocess.SkullStrip(),
                                  name='anat_skullstrip')
    skullstrip.inputs.outputtype = 'NIFTI_GZ'

    intensity = pe.Node(interface=preprocess.Calc(),
                        name='skullstrip_intensity')
    intensity.inputs.expr = 'a*step(b)'
    intensity.inputs.outputtype = 'NIFTI_GZ'

    wf.connect(in_node, 'anat', skullstrip, 'in_file')
    wf.connect(in_node, 'anat', intensity, 'in_file_a')
    wf.connect(skullstrip, 'out_file', intensity, 'in_file_b')
    wf.connect(skullstrip, 'out_file', out_node, 'skullstrip')

    if qc_figures:
        from CPAC.qc import anat_figure

        fname = os.path.join(os.getcwd(), 'skullstrip')
        qc = pe.Node(util.Function(input_names=['overlay', 'underlay', 'fig_name'],
                                                 output_names=['x_fig', 'z_fig'],
                                                 function=anat_figure),
                                   name='qc_skullstrip')

        qc.inputs.fig_name = fname
        wf.connect(in_node, 'anat', qc, 'overlay')
        wf.connect(skullstrip, 'out_file', qc, 'underlay')

        wf.connect(qc, 'x_fig', out_node, 'x_fig')
        wf.connect(qc, 'z_fig', out_node, 'z_fig')


    return wf


def create_anat_preprocessing_wf():
    """     
    Process T1 scans already skullstripped. 
    Raw mprage file is deobliqued and reoriented into RPI.
    
    Returns 
    -------
    anat_preproc : workflow
        Anatomical Preprocessing Workflow
    
    Notes
    -----
    `Source <https://github.com/FCP-INDI/C-PAC/blob/master/CPAC/anat_preproc/anat_preproc.py>`_
    
    Workflow Inputs::
        inputspec.anat : mprage file or a list of mprage nifti file 
            User input anatomical(T1) Image, in any of the 8 orientations
    
    Workflow Outputs::
        outputspec.brain : nifti file
            RPI oriented anatomical data 
    
    Order of commands:

    - Deobliqing the scans.  For details see `3drefit <http://afni.nimh.nih.gov/pub/dist/doc/program_help/3drefit.html>`_::
    
        3drefit -deoblique mprage.nii.gz
        
    - Re-orienting the Image into Right-to-Left Posterior-to-Anterior Inferior-to-Superior  (RPI) orientation.  For details see `3dresample <http://afni.nimh.nih.gov/pub/dist/doc/program_help/3dresample.html>`_::
    
        3dresample -orient RPI -prefix mprage_RPI.nii.gz -inset mprage.nii.gz 
    
    Examples
    --------
    >>> from CPAC.anat_preproc import create_anat_preprocessing_wf
    >>> wf = create_anat_preproc()
    >>> wf.inputs.inputspec.anat='mprage.nii.gz'
    >>> wf.run() #doctest: +SKIP     
    """
    wf = pe.Workflow(name='anat_preprocessing')
    in_node = pe.Node(util.IdentityInterface(fields=['anat']),
                        name='inputspec')

    out_node = pe.Node(util.IdentityInterface(fields=['brain']),
                         name='outputspec')

    deoblique = pe.Node(interface=preprocess.Refit(),
                         name='anat_deoblique')
    deoblique.inputs.deoblique = True
    wf.connect(in_node, 'anat', deoblique, 'in_file')

    reorient = pe.Node(interface=preprocess.Resample(),
                            name='anat_reorient')
    reorient.inputs.orientation = 'RPI'
    reorient.inputs.outputtype = 'NIFTI_GZ'
    wf.connect(deoblique, 'out_file', reorient, 'in_file')
    wf.connect(reorient, 'out_file', out_node, 'brain')

    return wf    