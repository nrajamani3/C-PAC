import os
import time
from time import strftime
import nipype.pipeline.engine as pe
import nipype.interfaces.fsl as fsl
import nipype.interfaces.io as nio
from nipype.interfaces.afni import preprocess
from   nipype.pipeline.utils import format_dot
import nipype.interfaces.ants as ants
import nipype.interfaces.c3 as c3
from nipype import config
from nipype import logging
from CPAC import network_centrality
from CPAC.network_centrality.utils import merge_lists
logger = logging.getLogger('workflow')
import pkg_resources as p
#import CPAC
from CPAC.anat_preproc.anat_preproc import create_anat_preproc
from CPAC.func_preproc.func_preproc import create_func_preproc
from CPAC.seg_preproc.seg_preproc import create_seg_preproc

from CPAC.registration import create_nonlinear_register, \
                              create_register_func_to_anat, \
                              create_bbregister_func_to_anat, \
                              create_wf_calculate_ants_warp, \
                              create_wf_apply_ants_warp, \
                              create_wf_c3d_fsl_to_itk, \
                              create_wf_collect_transforms
from CPAC.nuisance import create_nuisance, bandpass_voxels

from CPAC.median_angle import create_median_angle_correction
from CPAC.generate_motion_statistics import motion_power_statistics
from CPAC.generate_motion_statistics import fristons_twenty_four
from CPAC.scrubbing import create_scrubbing_preproc
from CPAC.timeseries import create_surface_registration, get_roi_timeseries, \
                            get_voxel_timeseries, get_vertices_timeseries, \
                            get_spatial_map_timeseries
from CPAC.network_centrality import create_resting_state_graphs, get_zscore
from CPAC.utils.datasource import *
from CPAC.utils import Configuration, create_all_qc
### no create_log_template here, move in CPAC/utils/utils.py
from CPAC.qc.qc import create_montage, create_montage_gm_wm_csf
from CPAC.qc.utils import register_pallete, make_edge, drop_percent_, \
                          gen_histogram, gen_plot_png, gen_motion_plt, \
                          gen_std_dev, gen_func_anat_xfm, gen_snr, \
                          generateQCPages, cal_snr_val
from CPAC.utils.utils import extract_one_d, set_gauss, \
                             prepare_symbolic_links, get_scan_params, \
                             get_tr, extract_txt, create_log, \
                             create_log_template, extract_output_mean, \
                             create_output_mean_csv
from CPAC.vmhc.vmhc import create_vmhc
from CPAC.reho.reho import create_reho
from CPAC.alff.alff import create_alff
from CPAC.sca.sca import create_sca, create_temporal_reg
import zlib
import linecache
import csv
import pickle
import commands
#------------------------------------------------------------------------------

class strategy:
    """
    """
    def __init__(self):
        self.resource_pool = {}
        self.leaf_node = None
        self.leaf_out_file = None
        self.name = []

    def append_name(self, name):
        self.name.append(name)

    def get_name(self):
        return self.name

    def set_leaf_properties(self, node, out_file):
        self.leaf_node = node
        self.leaf_out_file = out_file

    def get_leaf_properties(self):
        return self.leaf_node, self.leaf_out_file

    def get_resource_pool(self):
        return self.resource_pool

    def get_node_from_resource_pool(self, resource_key,logger):
        try:
            if resource_key in self.resource_pool:
                return self.resource_pool[resource_key]
        except:
            logger.info('no node for output: ')
            logger.info(resource_key)
            raise

    def update_resource_pool(self, resources,logger):
        for key, value in resources.items():
##            if key in self.resource_pool:
##                logger.info('Warning: %s already exists in resource' \
##                        ' pool with value %s, \nreplacing it with this value %s ' %\
##                         (key, self.resource_pool[key],value))
            self.resource_pool[key] = value
            
            
def create_log_node(workflow,wflow, output, indx, log_dir,scan_id = None):
    """
    """
    if wflow: 
        log_wf = create_log(wf_name = 'log_%s' %wflow.name)
        log_wf.inputs.inputspec.workflow = wflow.name
        log_wf.inputs.inputspec.index = indx
        log_wf.inputs.inputspec.log_dir = log_dir
        workflow.connect(wflow, output, log_wf, 'inputspec.inputs')
    else:
        log_wf = create_log(wf_name = 'log_done_%s'%scan_id, scan_id= scan_id)
        log_wf.inputs.inputspec.workflow = 'DONE'
        log_wf.inputs.inputspec.index = indx
        log_wf.inputs.inputspec.log_dir = log_dir
        log_wf.inputs.inputspec.inputs = log_dir
        return log_wf

    
def populateLogger(message,logger):
    """
    """
    logger.info(message)
    
def logStandardError(sectionName, errLine, errNum,logger):
    """
    """    
    logger.info("\n\n" + 'ERROR: %s - %s' % (sectionName, errLine) + "\n\n" + \
                "Error name: cpac_pipeline_%s" % (errNum) + "\n\n")
        
def logConnectionError(workflow_name, numStrat, resourcePool, errNum,logger):
    """
    """       
    logger.info("\n\n" + 'ERROR: Invalid Connection: %s: %s, resource_pool: %s' \
                % (workflow_name, numStrat, resourcePool) +\
                 "\n\n" + "Error name: cpac_pipeline_%s" % (errNum) + \
                "\n\n" + "This is a pipeline creation error"+\
                " - the workflows have not started yet." + "\n\n")
        
def logStandardWarning(sectionName, warnLine,logger):
    """
    """    
    logger.info("\n\n" + 'WARNING: %s - %s' % (sectionName, warnLine) + "\n\n")
        
def getNodeList(strategy):
    """
    """    
    nodes = []
    for node in strategy.name:
        nodes.append(node[:-2])        
    return nodes
    
    
def inputFilepathsCheck(c):
    # this section checks all of the file paths provided in the pipeline
    # config yaml file and ensures the files exist and are accessible

    pipeline_config_map = c.return_config_elements()                
    wrong_filepath_list = []
    for config_item in pipeline_config_map:

        label = config_item[0]
        val = config_item[1]

        # ensures it is only checking file paths
        if isinstance(val, str) and '/' in val:
            if ('.txt' in val) or ('.nii' in val) or ('.nii.gz' in val) \
                or ('.mat' in val) or ('.cnf' in val) or ('.sch' in val):
                    
                if not os.path.isfile(val):
                    wrong_filepath_list.append((label, val))

    if len(wrong_filepath_list) > 0:
        print '\n\n'
        print 'Whoops! - Filepaths provided do not exist:\n'

        for file_tuple in wrong_filepath_list:
            print file_tuple[0], ' - ', file_tuple[1]

        print '\nPlease double-check your pipeline configuration file.\n\n'
        raise Exception
    
    
def workflowPreliminarySetup(subject_id,c,config,logging,log_dir,logger):
    
    wfname = 'resting_preproc_' + str(subject_id)
    workflow = pe.Workflow(name=wfname)
    workflow.base_dir = c.workingDirectory
    workflow.config['execution'] = {'hash_method': 'timestamp', \
                                    'crashdump_dir': os.path.abspath(c.crashLogDirectory)}
    config.update_config({'logging': {'log_directory': log_dir, 'log_to_file': True}})
    logging.update_logging(config)

    if c.reGenerateOutputs is True:
        cmd = "find %s -name \'*sink*\' -exec rm -rf {} \\;" % os.path.join(c.workingDirectory, wfname)
        commands.getoutput(cmd)
        cmd = "find %s -name \'*link*\' -exec rm -rf {} \\;" % os.path.join(c.workingDirectory, wfname)
        commands.getoutput(cmd)
        cmd = "find %s -name \'*log*\' -exec rm -rf {} \\;" % os.path.join(c.workingDirectory, wfname)
        commands.getoutput(cmd)
        
    return workflow
    
def runAnatomicalDataGathering(c,subject_id,sub_dict,workflow,\
                                workflow_bit_id,workflow_counter,\
                                strat_list,logger,log_dir):
    """
    """
    num_strat = 0
    strat_list = []
    for gather_anat in c.runAnatomicalDataGathering:
        strat_initial = strategy()
        if gather_anat == 1:
            flow = create_anat_datasource()
            flow.inputs.inputnode.subject = subject_id
            flow.inputs.inputnode.anat = sub_dict['anat']
            anat_flow = flow.clone('anat_gather_%d' % num_strat)
            strat_initial.set_leaf_properties(anat_flow, 'outputspec.anat')
        num_strat += 1
        strat_list.append(strat_initial) 
    return strat_list
    
def runAnatomicalPreprocessing(c,subject_id,sub_dict,workflow,\
                                workflow_bit_id,workflow_counter,\
                                strat_list,logger,log_dir):
    """
    """
    new_strat_list = []
    num_strat = 0
    if 1 in c.runAnatomicalPreprocessing:
        workflow_bit_id['anat_preproc'] = workflow_counter
        for strat in strat_list:
            anat_preproc = create_anat_preproc().clone('anat_preproc_%d' % num_strat)
            try: # connect the new node to the previous leaf                
                node, out_file = strat.get_leaf_properties()
                workflow.connect(node, out_file, anat_preproc, 'inputspec.anat')
            except:
                logConnectionError('Anatomical Preprocessing No valid Previous for strat', \
                                   num_strat, strat.get_resource_pool(), '0001',logger)
                num_strat += 1
                continue

            if 0 in c.runAnatomicalPreprocessing: # we are forking so create a new node                
                new_strat_list,strat=createNewStrategy(strat,new_strat_list) 

            strat.append_name(anat_preproc.name)
            strat.set_leaf_properties(anat_preproc, 'outputspec.brain')
            strat.update_resource_pool({'anatomical_brain':\
                                    (anat_preproc, 'outputspec.brain')},logger)
            strat.update_resource_pool({'anatomical_reorient':\
                                (anat_preproc, 'outputspec.reorient')},logger)            
            create_log_node(workflow,anat_preproc, 'outputspec.brain', \
                            num_strat,log_dir)
            num_strat += 1
    strat_list += new_strat_list
    return strat_list
    
def runRegistrationPreprocessing(c,subject_id,sub_dict,workflow,\
                                workflow_bit_id,workflow_counter,\
                                strat_list,logger,log_dir):
    """
    """
    new_strat_list=[]
    num_strat = 0    
    if 1 in c.runRegistrationPreprocessing:
        workflow_bit_id['anat_mni_register'] = workflow_counter
        for strat in strat_list:
            nodes = getNodeList(strat)
            if 'FSL' in c.regOption:
                num_strat = regOptionFSL(num_strat,strat,workflow,\
                                            logger,c,new_strat_list,log_dir)                    
            if ('ANTS' in c.regOption) and \
                    ('anat_mni_fnirt_register' not in nodes):
                num_strat = regOptionAnts(num_strat,strat,workflow,\
                                            logger,c,new_strat_list,log_dir) 
    strat_list += new_strat_list
    return strat_list 

def regOptionAnts(num_strat,strat,workflow,logger,c,new_strat_list,log_dir):
    """
    """
    ants_reg_anat_mni = create_wf_calculate_ants_warp('anat_mni' \
            '_ants_register_%d' % num_strat)

    try:
        node, out_file = strat.get_leaf_properties()
        workflow.connect(node, out_file, ants_reg_anat_mni,
                'inputspec.anatomical_brain')
        ants_reg_anat_mni = setAntsInputSpecs(ants_reg_anat_mni,c)         

    except:
        logConnectionError('Anatomical Registration (ANTS)', \
            num_strat, strat.get_resource_pool(), '0003',logger)
        raise

    if 0 in c.runRegistrationPreprocessing:
        new_strat_list,strat=createNewStrategy(strat,new_strat_list) 

    strat.append_name(ants_reg_anat_mni.name)
    strat.set_leaf_properties(ants_reg_anat_mni, \
                    'outputspec.normalized_output_brain')
    strat.update_resource_pool({\
                'ants_rigid_xfm':(ants_reg_anat_mni, 'outputspec.ants_rigid_xfm'),\
                'ants_affine_xfm':(ants_reg_anat_mni, 'outputspec.ants_affine_xfm'),\
                'anatomical_to_mni_nonlinear_xfm':(ants_reg_anat_mni, 'outputspec.warp_field'),\
                'mni_to_anatomical_nonlinear_xfm':(ants_reg_anat_mni, 'outputspec.inverse_warp_field'),\
                'anat_to_mni_ants_composite_xfm':(ants_reg_anat_mni, 'outputspec.composite_transform'),\
                'mni_normalized_anatomical':(ants_reg_anat_mni, 'outputspec.normalized_output_brain')},\
                logger)
    create_log_node(workflow,ants_reg_anat_mni, \
                    'outputspec.normalized_output_brain', num_strat,log_dir)          
    num_strat += 1   
    return num_strat
            
              
def regOptionFSL(num_strat,strat,workflow,logger,c,new_strat_list,log_dir):
    """
    """
    fnirt_reg_anat_mni = create_nonlinear_register('anat_mni_fnirt_register_%d' % num_strat)
    try:
        node, out_file = strat.get_leaf_properties()
        workflow.connect(node, out_file,
                         fnirt_reg_anat_mni, 'inputspec.input_brain')
        node, out_file = strat.get_node_from_resource_pool('anatomical_reorient',logger)
        workflow.connect(node, out_file,
                         fnirt_reg_anat_mni, 'inputspec.input_skull')
        fnirt_reg_anat_mni = setFnirtInputSpecs(fnirt_reg_anat_mni,c)             
    except:
        logConnectionError('Anatomical Registration (FSL)', \
                           num_strat, strat.get_resource_pool(), '0002',logger)
        raise

    if (0 in c.runRegistrationPreprocessing) or ('ANTS' in c.regOption):
        new_strat_list,strat=createNewStrategy(strat,new_strat_list) 

    strat.append_name(fnirt_reg_anat_mni.name)
    strat.set_leaf_properties(fnirt_reg_anat_mni, 'outputspec.output_brain')
    strat.update_resource_pool({\
                'anatomical_to_mni_linear_xfm':(fnirt_reg_anat_mni, 'outputspec.linear_xfm'),\
                'anatomical_to_mni_nonlinear_xfm':(fnirt_reg_anat_mni, 'outputspec.nonlinear_xfm'),\
                'mni_to_anatomical_linear_xfm':(fnirt_reg_anat_mni, 'outputspec.invlinear_xfm'),\
                'mni_normalized_anatomical':(fnirt_reg_anat_mni, 'outputspec.output_brain')},\
                logger)
    create_log_node(workflow,fnirt_reg_anat_mni, \
                    'outputspec.output_brain', num_strat,log_dir)         
    num_strat += 1 
    return num_strat        
                
                
                
def setFnirtInputSpecs(fnirt_reg_anat_mni,c):
    """
    """
    fnirt_reg_anat_mni.inputs.inputspec.reference_brain = c.template_brain_only_for_anat
    fnirt_reg_anat_mni.inputs.inputspec.reference_skull = c.template_skull_for_anat
    fnirt_reg_anat_mni.inputs.inputspec.fnirt_config = c.fnirtConfig  
    return fnirt_reg_anat_mni

  
def setAntsInputSpecs(ants_reg_anat_mni,c):
    """
    """
    ants_reg_anat_mni.inputs.inputspec. \
        reference_brain = c.template_brain_only_for_anat
    ants_reg_anat_mni.inputs.inputspec.dimension = 3
    ants_reg_anat_mni.inputs.inputspec. \
        use_histogram_matching = True
    ants_reg_anat_mni.inputs.inputspec. \
        winsorize_lower_quantile = 0.01
    ants_reg_anat_mni.inputs.inputspec. \
        winsorize_upper_quantile = 0.99
    ants_reg_anat_mni.inputs.inputspec. \
        metric = ['MI','MI','CC']
    ants_reg_anat_mni.inputs.inputspec.metric_weight = [1,1,1]
    ants_reg_anat_mni.inputs.inputspec. \
        radius_or_number_of_bins = [32,32,4]
    ants_reg_anat_mni.inputs.inputspec. \
        sampling_strategy = ['Regular','Regular',None]
    ants_reg_anat_mni.inputs.inputspec. \
        sampling_percentage = [0.25,0.25,None]
    ants_reg_anat_mni.inputs.inputspec. \
        number_of_iterations = [[1000,500,250,100], \
        [1000,500,250,100], [100,100,70,20]]
    ants_reg_anat_mni.inputs.inputspec. \
        convergence_threshold = [1e-8,1e-8,1e-9]
    ants_reg_anat_mni.inputs.inputspec. \
        convergence_window_size = [10,10,15]
    ants_reg_anat_mni.inputs.inputspec. \
        transforms = ['Rigid','Affine','SyN']
    ants_reg_anat_mni.inputs.inputspec. \
        transform_parameters = [[0.1],[0.1],[0.1,3,0]]
    ants_reg_anat_mni.inputs.inputspec. \
        shrink_factors = [[8,4,2,1],[8,4,2,1],[6,4,2,1]]
    ants_reg_anat_mni.inputs.inputspec. \
        smoothing_sigmas = [[3,2,1,0],[3,2,1,0],[3,2,1,0]]   
    return ants_reg_anat_mni
    
    
def runSegmentationPreprocessing(c,subject_id,sub_dict,workflow,\
                                workflow_bit_id,workflow_counter,\
                                strat_list,logger,log_dir):
    """
    """
    new_strat_list = []
    num_strat = 0
    if 1 in c.runSegmentationPreprocessing:
        workflow_bit_id['seg_preproc'] = workflow_counter
        for strat in strat_list:            
            nodes = getNodeList(strat)            
            if 'anat_mni_fnirt_register' in nodes:
                seg_preproc = create_seg_preproc(False, 'seg_preproc_%d' % num_strat)
            elif 'anat_mni_ants_register' in nodes:
                seg_preproc = create_seg_preproc(True, 'seg_preproc_%d' % num_strat)
            try:
                node, out_file = strat.get_node_from_resource_pool('anatomical_brain',logger)
                workflow.connect(node, out_file,
                                 seg_preproc, 'inputspec.brain')
                if 'anat_mni_fnirt_register' in nodes:
                    node, out_file = strat.get_node_from_resource_pool('mni_to_anatomical_linear_xfm',logger)
                    workflow.connect(node, out_file,seg_preproc, 'inputspec.standard2highres_mat')
                elif 'anat_mni_ants_register' in nodes:
                    node, out_file = strat.get_node_from_resource_pool('ants_affine_xfm',logger)
                    workflow.connect(node, out_file,seg_preproc, 'inputspec.standard2highres_mat')
                    node, out_file = strat.get_node_from_resource_pool('ants_rigid_xfm',logger)
                    workflow.connect(node, out_file,seg_preproc, 'inputspec.standard2highres_rig')
                seg_preproc= setSegInputSpecs(seg_preproc,c)
            except:
                logConnectionError('Segmentation Preprocessing', \
                                   num_strat, strat.get_resource_pool(), '0004',logger)
                raise

            if 0 in c.runSegmentationPreprocessing:
                new_strat_list,strat=createNewStrategy(strat,new_strat_list)               

            strat.append_name(seg_preproc.name)
            strat.update_resource_pool({'anatomical_gm_mask' : (seg_preproc, 'outputspec.gm_mask'),
                                        'anatomical_csf_mask': (seg_preproc, 'outputspec.csf_mask'),
                                        'anatomical_wm_mask' : (seg_preproc, 'outputspec.wm_mask'),
                                        'seg_probability_maps': (seg_preproc, 'outputspec.probability_maps'),
                                        'seg_mixeltype': (seg_preproc, 'outputspec.mixeltype'),
                                        'seg_partial_volume_map': (seg_preproc, 'outputspec.partial_volume_map'),
                                        'seg_partial_volume_files': (seg_preproc, 'outputspec.partial_volume_files')},logger)

            create_log_node(workflow,seg_preproc, \
                        'outputspec.partial_volume_map', num_strat,log_dir)
            num_strat += 1
    strat_list += new_strat_list 
    return strat_list   

def createNewStrategy(strat,new_strat_list):
    """
    """
    tmp = strategy()
    tmp.resource_pool = dict(strat.resource_pool)
    tmp.leaf_node = (strat.leaf_node)
    tmp.leaf_out_file = str(strat.leaf_out_file)
    tmp.name = list(strat.name)
    strat = tmp
    new_strat_list.append(strat)
    return new_strat_list,strat
    
def setSegInputSpecs(seg_preproc,c):
    """
    """
    seg_preproc.inputs.inputspec.PRIOR_CSF = c.PRIORS_CSF
    seg_preproc.inputs.inputspec.PRIOR_GRAY = c.PRIORS_GRAY
    seg_preproc.inputs.inputspec.PRIOR_WHITE = c.PRIORS_WHITE

    seg_preproc.inputs.csf_threshold.csf_threshold = \
                            c.cerebralSpinalFluidThreshold
    seg_preproc.inputs.wm_threshold.wm_threshold = \
                            c.whiteMatterThreshold
    seg_preproc.inputs.gm_threshold.gm_threshold = \
                            c.grayMatterThreshold
    seg_preproc.get_node('csf_threshold').iterables = ('csf_threshold',
                            c.cerebralSpinalFluidThreshold)
    seg_preproc.get_node('wm_threshold').iterables = ('wm_threshold',
                            c.whiteMatterThreshold)
    seg_preproc.get_node('gm_threshold').iterables = ('gm_threshold',
                            c.grayMatterThreshold)
    return seg_preproc
    
def runFunctionalDataGathering(c,subject_id,sub_dict,workflow,\
                                workflow_bit_id,workflow_counter,\
                                strat_list,logger,log_dir):
    """
    """
    new_strat_list = []
    num_strat = 0
    if 1 in c.runFunctionalDataGathering:
        for strat in strat_list:
            funcFlow = create_func_datasource(sub_dict['rest'], 'func_gather_%d' % num_strat)
            funcFlow.inputs.inputnode.subject = subject_id
            if 0 in c.runFunctionalDataGathering:
                new_strat_list,strat=createNewStrategy(strat,new_strat_list)
            strat.set_leaf_properties(funcFlow, 'outputspec.rest')
            num_strat += 1

    strat_list += new_strat_list
    return strat_list,funcFlow
   
def setScanParamsInputSpecs(c,sub_dict,num_strat):
    """
    """
    scan_params = pe.Node(util.Function(\
                    input_names=['subject','scan','subject_map','start_indx',\
                                'stop_indx'],
                    output_names=['tr','tpattern','ref_slice','start_indx',\
                                 'stop_indx'],
                    function=get_scan_params),
                    name='scan_params_%d' % num_strat)
    scan_params.inputs.subject_map = sub_dict
    scan_params.inputs.start_indx = c.startIdx
    scan_params.inputs.stop_indx = c.stopIdx                   
    return scan_params

def setConvertTrParams(num_strat):
    """
    """
    convert_tr = pe.Node(util.Function(\
                    input_names=['tr'],
                    output_names=['tr'],
                    function=get_tr),
                    name='convert_tr_%d' % num_strat)
    convert_tr.inputs.tr = c.TR
    return convert_tr

def setFuncPreprocParams(c,func_preproc):
    """
    """
    func_preproc.inputs.inputspec.start_idx = c.startIdx
    func_preproc.inputs.inputspec.stop_idx = c.stopIdx
    return func_preproc
        
##def functionalMasking3dAutoMask(slice_timing,workflow,scan_params,convert_tr,\
##                                num_strat):
##    """
##    """
##    if slice_timing:
##        func_preproc = create_func_preproc(slice_timing_correction=True, \
##                                           use_bet=False, \
##                                           wf_name='func_preproc_automask_%d' % num_strat)
##        workflow.connect(funcFlow, 'outputspec.subject',
##                         scan_params, 'subject')
##        workflow.connect(funcFlow, 'outputspec.scan',
##                         scan_params, 'scan')                   
##        workflow.connect(scan_params, 'tr',
##                         func_preproc, 'scan_params.tr')
##        workflow.connect(scan_params, 'ref_slice',
##                         func_preproc, 'scan_params.ref_slice')
##        workflow.connect(scan_params, 'tpattern',
##                         func_preproc, 'scan_params.acquisition')
##        workflow.connect(scan_params, 'start_indx',
##                         func_preproc, 'inputspec.start_idx')
##        workflow.connect(scan_params, 'stop_indx',
##                         func_preproc, 'inputspec.stop_idx')
##        workflow.connect(scan_params, 'tr',
##                         convert_tr, 'tr')
##    else:
##        func_preproc = create_func_preproc(slice_timing_correction=False, \
##                    wf_name='func_preproc_automask_%d' % num_strat)
##        func_preproc = setFuncPreprocParams(c,func_preproc)
##    try:
##        node, out_file = strat.get_leaf_properties()
##        workflow.connect(node, out_file, func_preproc, 'inputspec.rest')
##    except:
##        logConnectionError('Functional Preprocessing', \
##                           num_strat, strat.get_resource_pool(), '0005',logger)
##        num_strat += 1
##        continue
##       
##    return num_strat    
##    
##    
##def runFunctionalPreprocessing(c,subject_id,sub_dict,workflow,\
##                                workflow_bit_id,workflow_counter,\
##                                strat_list,logger,log_dir):
##    """
##    """
##    new_strat_list = []
##    num_strat = 0
##    if 1 in c.runFunctionalPreprocessing:
##        workflow_bit_id['func_preproc'] = workflow_counter
##        slice_timing = sub_dict.get('scan_parameters')
##        scan_params = setScanParamsInputSpecs(c,sub_dict,num_strat)
##        convert_tr = setConvertTrParams(num_strat) 
##        for strat in strat_list:            
##            if '3dAutoMask' in c.functionalMasking:  
##                num_strat = functionalMasking3dAutoMask(slice_timing,\
##                                                        workflow,scan_params)               
##                
##                if (0 in c.runFunctionalPreprocessing) or ('BET' in c.functionalMasking):
##        new_strat_list,strat=createNewStrategy(strat,new_strat_list)
##    strat.append_name(func_preproc.name)
##    strat.set_leaf_properties(func_preproc, 'outputspec.preprocessed')
##
##    # add stuff to resource pool if we need it
##    if slice_timing:
##        strat.update_resource_pool({'slice_timing_corrected': (func_preproc, 'outputspec.slice_time_corrected')},logger)
##    strat.update_resource_pool({'mean_functional':(func_preproc, 'outputspec.example_func')},logger)
##    strat.update_resource_pool({'functional_preprocessed_mask':(func_preproc, 'outputspec.preprocessed_mask')},logger)
##    strat.update_resource_pool({'movement_parameters':(func_preproc, 'outputspec.movement_parameters')},logger)
##    strat.update_resource_pool({'max_displacement':(func_preproc, 'outputspec.max_displacement')},logger)
##    strat.update_resource_pool({'preprocessed':(func_preproc, 'outputspec.preprocessed')},logger)
##    strat.update_resource_pool({'functional_brain_mask':(func_preproc, 'outputspec.mask')},logger)
##    strat.update_resource_pool({'motion_correct':(func_preproc, 'outputspec.motion_correct')},logger)
##    strat.update_resource_pool({'coordinate_transformation':(func_preproc, 'outputspec.oned_matrix_save')},logger)
##
##    create_log_node(workflow,func_preproc, 'outputspec.preprocessed', num_strat,log_dir)
##    num_strat += 1
##        strat_list += new_strat_list
##        new_strat_list = []
##            
##
##        for strat in strat_list:            
##            nodes = getNodeList(strat)            
##            if ('BET' in c.functionalMasking) and ('func_preproc_automask' not in nodes):
##
##                slice_timing = sub_dict.get('scan_parameters')
##                # a node which checks if scan _parameters are present for each scan
##                scan_params = pe.Node(util.Function(input_names=['subject',
##                                                                 'scan',
##                                                                 'subject_map',
##                                                                 'start_indx',
##                                                                 'stop_indx'],
##                                                   output_names=['tr',
##                                                                 'tpattern',
##                                                                 'ref_slice',
##                                                                 'start_indx',
##                                                                 'stop_indx'],
##                                                   function=get_scan_params),
##                                     name='scan_params_%d' % num_strat)
##
##                convert_tr = pe.Node(util.Function(input_names=['tr'],
##                                                   output_names=['tr'],
##                                                   function=get_tr),
##                                     name='convert_tr_%d' % num_strat)
##
##                # if scan parameters are available slice timing correction is
##                # turned on
##                if slice_timing:
##
##                    func_preproc = create_func_preproc(slice_timing_correction=True, \
##                                                       use_bet=True, \
##                                                       wf_name='func_preproc_bet_%d' % num_strat)
##
##                    # getting the scan parameters
##                    workflow.connect(funcFlow, 'outputspec.subject',
##                                     scan_params, 'subject')
##                    workflow.connect(funcFlow, 'outputspec.scan',
##                                     scan_params, 'scan')
##                    scan_params.inputs.subject_map = sub_dict
##                    scan_params.inputs.start_indx = c.startIdx
##                    scan_params.inputs.stop_indx = c.stopIdx
##
##                    # passing the slice timing correction parameters
##                    workflow.connect(scan_params, 'tr',
##                                     func_preproc, 'scan_params.tr')
##                    workflow.connect(scan_params, 'ref_slice',
##                                     func_preproc, 'scan_params.ref_slice')
##                    workflow.connect(scan_params, 'tpattern',
##                                     func_preproc, 'scan_params.acquisition')
##
##                    workflow.connect(scan_params, 'start_indx',
##                                     func_preproc, 'inputspec.start_idx')
##                    workflow.connect(scan_params, 'stop_indx',
##                                     func_preproc, 'inputspec.stop_idx')
##
##                    workflow.connect(scan_params, 'tr',
##                                     convert_tr, 'tr')
##                else:
##                    func_preproc = create_func_preproc(slice_timing_correction=False, \
##                                                       use_bet=True, \
##                                                       wf_name='func_preproc_bet_%d' % num_strat)
##                    func_preproc.inputs.inputspec.start_idx = c.startIdx
##                    func_preproc.inputs.inputspec.stop_idx = c.stopIdx
##
##                    convert_tr.inputs.tr = c.TR
##
##                node = None
##                out_file = None
##                try:
##                    node, out_file = strat.get_leaf_properties()
##                    workflow.connect(node, out_file, func_preproc, 'inputspec.rest')
##
##                except:
##                    logConnectionError('Functional Preprocessing', \
##                                       num_strat, strat.get_resource_pool(), '0005',logger)
##                    num_strat += 1
##                    continue
##
##                if 0 in c.runFunctionalPreprocessing:
##                    new_strat_list,strat=createNewStrategy(strat,new_strat_list)
##
##                strat.append_name(func_preproc.name)
##                strat.set_leaf_properties(func_preproc, 'outputspec.preprocessed')
##
##                # add stuff to resource pool if we need it
##                if slice_timing:
##                    strat.update_resource_pool({'slice_timing_corrected': (func_preproc, 'outputspec.slice_time_corrected')},logger)
##                strat.update_resource_pool({'mean_functional':(func_preproc, 'outputspec.example_func')},logger)
##                strat.update_resource_pool({'functional_preprocessed_mask':(func_preproc, 'outputspec.preprocessed_mask')},logger)
##                strat.update_resource_pool({'movement_parameters':(func_preproc, 'outputspec.movement_parameters')},logger)
##                strat.update_resource_pool({'max_displacement':(func_preproc, 'outputspec.max_displacement')},logger)
##                strat.update_resource_pool({'preprocessed':(func_preproc, 'outputspec.preprocessed')},logger)
##                strat.update_resource_pool({'functional_brain_mask':(func_preproc, 'outputspec.mask')},logger)
##                strat.update_resource_pool({'motion_correct':(func_preproc, 'outputspec.motion_correct')},logger)
##                strat.update_resource_pool({'coordinate_transformation':(func_preproc, 'outputspec.oned_matrix_save')},logger)
##
##
##                create_log_node(workflow,func_preproc, 'outputspec.preprocessed', num_strat,log_dir)
##                num_strat += 1
##
##
##    strat_list += new_strat_list
##    return strat_list

























    
    
    
    
    
    
    
    
    
    
    
