import os
import nipype.pipeline.engine as pe
from nipype.interfaces.utility import Function
import nipype.interfaces.fsl as fsl
import nipype.interfaces.utility as util
import nipype.interfaces.ants as ants
from CPAC.seg_preproc.utils import * 

def wire_segmentation_wf(wf, strat, num_strat,PRIORS_CSF,PRIORS_GRAY,PRIORS_WHITE, use_ants, qc_figures=False):
    seg_dict = {'csf':PRIORS_CSF, 'gm':PRIORS_GRAY, 'wm':PRIORS_WHITE}
    node, out_file = strat.get_node_from_resource_pool('anatomical_brain')

    if qc_figures:
        from CPAC.qc import overlay_figure
        fname = os.path.join(os.getcwd(), 'segmentation')
        qc = pe.MapNode(iterfield=['overlays'],interface=util.Function(input_names=['underlay', 'fig_name'],
                                                 output_names=['x_fig', 'z_fig'], function=overlay_figure),
                                   name='qc_segmentation')
        qc.inputs.fig_name = fname
        wf.connect(node, out_file, qc, 'underlay')
    
    for key in seg_dict:
        seg = create_segmentation_wf('seg_preproc_{seg}_{num}'.format(seg=key,num=num_strat), key,use_ants)
        wf.connect(node, out_file, seg, 'inputspec.brain')

        if use_ants:
            node1, out_file1 = strat.get_node_from_resource_pool('ants_initial_xfm')
            wf.connect(node1, out_file1, seg, 'inputspec.standard2highres_init')
            node2, out_file2 = strat.get_node_from_resource_pool('ants_rigid_xfm')
            wf.connect(node2, out_file2, seg, 'inputspec.standard2highres_rig')
            node3, out_file3 = strat.get_node_from_resource_pool('ants_affine_xfm')
            wf.connect(node3, out_file3, seg, 'inputspec.standard2highres_mat')
        else:
            node1, out_file1 = strat.get_node_from_resource_pool('mni_to_anatomical_linear_xfm0')
            wf.connect(node1, out_file1, seg, 'inputspec.standard2highres_mat')

        seg.inputs.inputspec.PRIOR = seg_dict[key]

        strat.append_name(seg.name)
        strat.update_resource_pool({'anatomical_{t}_mask'.format(t=key) : (seg, 'outputspec.{t}_mask'.format(t=key))})

        if qc_figures:
            wf.connect(seg, 'outputspec.{t}_mask'.format(t=key), qc, 'overlays')

    #last segmentation updates probability_maps
    strat.update_resource_pool({'seg_probability_maps': (seg, 'outputspec.probability_maps')})

    if qc_figures:
        strat.update_resource_pool({'images@segmentationx':(qc, 'outputspec.x_fig')})
        strat.update_resource_pool({'images.@segmentationz':(qc, 'outputspec.z_fig')})

    return wf, strat

def create_segmentation_wf(name, segmentation_type, use_ants):
    if segmentation_type not in ('wm', 'gm', 'csf'):
        raise ValueError('Segmentation type must be wm, gm or csf')

    seg_vals = {'wm': pick_wm_2, 'gm': pick_wm_1, 'csf': pick_wm_0 }

    wf = pe.Workflow(name=name)
    in_node = pe.Node(util.IdentityInterface(fields=['brain',
                                                       'standard2highres_init',
                                                       'standard2highres_mat',
                                                       'standard2highres_rig',
                                                       'PRIOR']),
                        name='inputspec')

    out_node = pe.Node(util.IdentityInterface(fields=[ segmentation_type + '_mask',
                                                        'probability_maps']),
                        name='outputspec')

    segment = pe.Node(interface=fsl.FAST(), name='segment')
    segment.inputs.img_type = 1
    segment.inputs.segments = True
    segment.inputs.probability_maps = True
    segment.inputs.out_basename = 'segment'
    segment.interface.estimated_memory_gb = 1.5

    check = pe.Node(name='check_'+ segmentation_type, interface=Function(function=check_if_file_is_empty,
     input_names=['in_file'], output_names=['out_file']))

    #connections
    wf.connect(in_node, 'brain', segment, 'in_files')
    wf.connect(segment, 'probability_maps', out_node, 'probability_maps')

    # get binarize thresholded gm mask
    process = process_segment_map(segmentation_type, use_ants)

    if use_ants:
        wf.connect(in_node, 'standard2highres_init',
                        process, 'inputspec.standard2highres_init')
        wf.connect(in_node, 'standard2highres_rig',
                        process, 'inputspec.standard2highres_rig')

    wf.connect(in_node, 'brain', process, 'inputspec.brain',)
    wf.connect(in_node, 'PRIOR', process, 'inputspec.tissue_prior')
    wf.connect(segment, ('tissue_class_files', seg_vals[segmentation_type]),
                    process, 'inputspec.probability_map')
    wf.connect(in_node, 'standard2highres_mat', process, 'inputspec.standard2highres_mat')
    wf.connect(process, 'outputspec.segment_mask', out_node, segmentation_type+'_mask')

    return wf



def process_segment_map(wf_name, use_ants):

    """
    This is a sub workflow used inside segmentation workflow to process 
    probability maps obtained in segmentation. Steps include overlapping 
    of the prior tissue with probability maps, thresholding and binarizing 
    it and creating a mask thst is used in further analysis.


    Parameters
    ----------
    wf_name : string
        Workflow Name

    Returns
    -------
    preproc : workflow
        Workflow Object for process_segment_map Workflow


    Notes
    -----

    `Source <https://github.com/FCP-INDI/C-PAC/blob/master/CPAC/seg_preproc/seg_preproc.py>`_ 
    

    Workflow Inputs::
    
        inputspec.brain : string (existing nifti file)
            Anatomical image(without skull)
    
        inputspec.standard2highres_mat : string (existing affine transformation .mat file)
            path to transformation matrix from mni space to anatomical space
    
        inputspec.tissue_prior : string (existing nifti file)
            path to FSL Standard Tissue prior image 
            
        inputspec.probability_map : string (nifti file)
            tissue Probability map obtained from fsl FAST
        
    Workflow Outputs::

        outputspec.segment_mni2t1 : string (nifti file)
            path to output CSF prior template(in MNI space) registered to anatomical space
    
        outputspec.segment_mask : string (nifti file)
            path to output image after masking segment_combo with its tissue prior in t1 space
        
        
    Order of commands:
 
    - Register tissue prior in MNI space to t1 space. 
    
    - Threshold and binarize segment probability map 
    
    - Generate segment mask, by applying tissue prior in t1 space to thresholded binarized segment probability map

    
    High Level Graph:
    
    .. image:: ../images/process_segment_map.dot.png
        :width: 1100
        :height: 480
        
    Detailed Graph:
    
    .. image:: ../images/process_segment_map_detailed.dot.png
        :width: 1100
        :height: 480
        
    """

    import nipype.interfaces.utility as util

    wf = pe.Workflow(name=wf_name)

    in_node = pe.Node(util.IdentityInterface(fields=['tissue_prior',
                                                       'brain',
                                                       'probability_map',
                                                       'standard2highres_init',
                                                       'standard2highres_mat',
                                                       'standard2highres_rig']),
                        name='inputspec')

    out_node = pe.Node(util.IdentityInterface(fields=['tissueprior_mni2t1',
                                                        'segment_mask']),
                        name='outputspec')

    if use_ants:
        collect_linear_transforms = pe.Node(util.Merge(3), name='%s_collect_linear_transforms' % (wf_name))
        tissueprior_mni_to_t1 = pe.Node(interface=ants.ApplyTransforms(),
                                        name='%s_prior_mni_to_t1' % (wf_name))
        tissueprior_mni_to_t1.inputs.invert_transform_flags = [True, True, True]
        tissueprior_mni_to_t1.inputs.interpolation = 'NearestNeighbor'
        segment_mask = pe.Node(interface=fsl.MultiImageMaths(),
                               name='%s_mask' % (wf_name))
        segment_mask.inputs.op_string = '-mas %s '

        # mni to t1
        wf.connect(in_node, 'tissue_prior', tissueprior_mni_to_t1, 'input_image')
        wf.connect(in_node, 'brain', tissueprior_mni_to_t1, 'reference_image')

        wf.connect(in_node, 'standard2highres_init', collect_linear_transforms, 'in1')
        wf.connect(in_node, 'standard2highres_rig', collect_linear_transforms, 'in2')
        wf.connect(in_node, 'standard2highres_mat', collect_linear_transforms, 'in3')

        wf.connect(collect_linear_transforms, 'out', tissueprior_mni_to_t1, 'transforms')

        #create segment mask
        wf.connect(in_node, 'probability_map',
                        segment_mask, 'in_file')
        wf.connect(tissueprior_mni_to_t1, 'output_image', 
                        segment_mask, 'operand_files')


        #connect to output nodes
        wf.connect(tissueprior_mni_to_t1, 'output_image', 
                        out_node, 'tissueprior_mni2t1')
        wf.connect(segment_mask, 'out_file', out_node, 'segment_mask')

    else:

        tissueprior_mni_to_t1 = pe.Node(interface=fsl.FLIRT(),
                                        name='%s_prior_mni_to_t1' % (wf_name))
        tissueprior_mni_to_t1.inputs.apply_xfm = True
        tissueprior_mni_to_t1.inputs.interp = 'nearestneighbour'

        segment_mask = pe.Node(interface=fsl.MultiImageMaths(),
                               name='%s_mask' % (wf_name))
        segment_mask.inputs.op_string = ' -bin -mas %s'

        # mni to t1
        wf.connect(in_node, 'tissue_prior',
                        tissueprior_mni_to_t1, 'in_file')
        wf.connect(in_node, 'brain',
                        tissueprior_mni_to_t1, 'reference')
        wf.connect(in_node, 'standard2highres_mat',
                        tissueprior_mni_to_t1, 'in_matrix_file')

        # create segment mask
        wf.connect(in_node, 'probability_map',
                        segment_mask, 'in_file')
        wf.connect(tissueprior_mni_to_t1, 'out_file',
                        segment_mask, 'operand_files')

        # connect to output nodes
        wf.connect(tissueprior_mni_to_t1, 'out_file',
                        out_node, 'tissueprior_mni2t1')
        wf.connect(segment_mask, 'out_file',
                        out_node, 'segment_mask')

    return wf
