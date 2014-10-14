import commands
import os
import nipype.pipeline.engine as pe
from CPAC.utils.utils import create_log,create_log_template

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
            if key in self.resource_pool:
                logger.info('Warning key %s already exists in resource' \
                        ' pool, replacing with %s ' % (key, value))
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
        logger.info(cmd)
        commands.getoutput(cmd)
        cmd = "find %s -name \'*link*\' -exec rm -rf {} \\;" % os.path.join(c.workingDirectory, wfname)
        logger.info(cmd)
        commands.getoutput(cmd)
        cmd = "find %s -name \'*log*\' -exec rm -rf {} \\;" % os.path.join(c.workingDirectory, wfname)
        logger.info(cmd)
        commands.getoutput(cmd)
        
    return workflow
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
