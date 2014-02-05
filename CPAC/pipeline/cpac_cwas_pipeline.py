import nipype.interfaces.utility as util
import nipype.interfaces.io as nio
import nipype.pipeline.engine as pe

import numpy as np
import re
import os
import sys
import glob
from CPAC.utils import Configuration

def cwas_workflow(c):
    from CPAC.cwas import create_cwas
    import time
        
    try:
        import mkl
        mkl.set_num_threads(c.cwas.threads)
    except ImportError:
        pass
        
    # Load workflow
    wf = pe.Workflow(name='cwas_workflow')
    wf.base_dir = c.workingDirectory
    
    # Setup CWAS set of commands
    cw = create_cwas()
    cw.inputs.inputspec.roi         = c.cwas.prior_mask_file
    cw.inputs.inputspec.subjects    = c.cwas.func_paths
    cw.inputs.inputspec.regressor   = c.cwas.design_mat
    cw.inputs.inputspec.cols        = c.cwas.regressors_of_interest
    cw.inputs.inputspec.f_samples   = c.cwas.n_permutations
    cw.inputs.inputspec.strata      = c.cwas.strata
    cw.inputs.inputspec.parallel_nodes = c.cwas.parallel_nodes
    cw.inputs.inputspec.memory_limit = c.cwas.memory_limit
    cw.inputs.inputspec.dtype       = c.cwas.dtype
    
    # Output directory
    ds = pe.Node(nio.DataSink(), name='cwas_sink')
    ds.inputs.base_directory = os.path.join(c.outputDirectory, "cwas_results")
    ds.inputs.container = ''
    
    # Link F-stats and P-values
    wf.connect(cw, 'outputspec.F_map',
               ds, 'F_map')
    wf.connect(cw, 'outputspec.p_map',
               ds, 'p_map')
    
    # Run CWAS
    start   = time.time()
    wf.run(plugin='MultiProc',
                         plugin_args={'n_procs': c.cwas.parallel_nodes})
    end     = time.time()
    
    # Return time it took
    print 'It took', end-start, 'seconds.'
    return (end-start)


def alt_prep_cwas_workflow(c):
    print 'Preparing CWAS workflow'
    
    from string import Template
    
    if isinstance(c.cwas, dict):
        c.cwas = Configuration(c.cwas)
    
    # Auto-complete base
    fields = ["prior_mask_file", "file_with_functional_paths", "regressor_file"]
    for field in fields:
        s = Template(getattr(c.cwas, field))
        c.cwas.update(field, s.substitute(base=c.cwas.base))
    
    # Read in list of subject functionals
    lines   = open(c.cwas.file_with_functional_paths).readlines()
    spaths  = [ l.strip().strip('"') for l in lines ]
    c.cwas.func_paths = spaths
    
    # Read in design/regressor file
    regressor = np.loadtxt(c.cwas.regressor_file)
    c.cwas.design_mat = regressor
    
    return cwas_workflow(c)


def prep_cwas_workflow(c, subject_infos):
    print 'Preparing CWAS workflow'
    from CPAC.pipeline.utils import load_configuration, \
                                    setup_group_subject_list, \
                                    load_subject_list, \
                                    load_paths_from_subject_list, \
                                    create_models_for_cwas
    
    if isinstance(c.cwas, dict):
        c.cwas = Configuration(c.cwas)
    
    for config_file in c.modelConfigs:
        config              = load_configuration(config_file)
        subject_list        = load_subject_list(config.subjectListFile)
        func_paths          = load_paths_from_subject_list(subject_list, 
                                                           subject_infos)
        mat, cols, strata   = create_models_for_cwas(config)    # generate the regressor etc
        
        # setup for CWAS (only some things)
        c.cwas.func_paths   = func_paths
        c.cwas.design_mat   = mat
        c.cwas.regressors_of_interest = cols
        c.cwas.strata       = strata
        
        # call CWAS
        cwas_workflow(c)
        

def run(config, subject_infos):
    import re
    import commands
    commands.getoutput('source ~/.bashrc')
    import os
    import sys
    import pickle
    import yaml

    c = Configuration(yaml.load(open(os.path.realpath(config), 'r')))

    prep_cwas_workflow(c, pickle.load(open(subject_infos, 'r') ))


