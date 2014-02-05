import os, sys
sys.path.append("/Users/zarrar/Code/C-PAC")

import numpy as np
from numpy.testing import *

from nose.tools import ok_, eq_, raises, with_setup
from nose.plugins.attrib import attr    # http://nose.readthedocs.org/en/latest/plugins/attrib.html

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import utils

def test_gen_file_map():
    """
    So I'm not sure the best way to actually test this.
    For now, this just calls the gen_file_map function and make's sure it 
    returns something reasonable.
    """
    datadir = '/data/Projects/temp_CPAC_Regression_Test/v_0-3-3/out'
    subject_infos = utils.gen_file_map(datadir, 'path_files/*/*.txt')
    

@attr('configs', 'group')
def test_setup_group_list():
    # So setup_group_subject_list
    # will check conf.subjectListFile
    # and see overlap with subject_infos
    
    # the base_path should contain pipeline folders within it!
    sink_dir         = '/data/Projects/temp_CPAC_Regression_Test/v_0-3-3/out'
    config_file      = "files/config_fsl.yml"
    
    curdir           = os.getcwd()
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    analysis_map     = utils.gen_file_map(sink_dir, os.path.join('path_files', '*', '*.txt'))
    analysis_key     = [ (k,v) for k,v in analysis_map.keys()[2:] if k == 'functional_mni' ][0] # pick an element of analysis_map
    conf             = utils.load_configuration(config_file)
    os.chdir(curdir)
    
    old_subject_file = conf.subjectListFile
    old_subjects     = utils.load_subject_list(old_subject_file)
    
    new_subject_file = utils.setup_group_subject_list(config_file, analysis_map[analysis_key], odir='/tmp/cpac_testing')
    new_subjects     = utils.load_subject_list(new_subject_file)
    
    # Old shouldn't be the same as new
    ok_(len(old_subjects) > len(new_subjects))
    
    # Should only match with the first two subjects
    assert_equal(np.array(old_subjects[:2]), np.array(new_subjects))
    
    # Clean up
    os.remove(new_subject_file)
    os.rmdir("/tmp/cpac_testing")
    
    return    
    
def test_load_paths_from_subject_list():
    
    base_path        = '/data/Projects/temp_CPAC_Regression_Test/v_0-3-3/out'
    config_file      = "files/config_fsl.yml"
    
    curdir           = os.getcwd()
    os.chdir(__file__)
    analysis_map     = utils.gen_file_map(base_path, os.path.join('path_files', '*', '*.txt'))
    analysis_key     = [ (k,v) for k,v in analysis_map.keys()[2:] if k == 'functional_mni' ][0] # pick an element
    conf             = utils.load_configuration(config_file)
    os.chdir(curdir)
    
    old_subject_list = utils.load_subject_list(conf.subjectListFile)
    new_subject_file = utils.setup_group_subject_list(config_file, analysis_map[analysis_key], odir="/tmp/cpac_testing")
    new_subject_list = utils.load_subject_list(new_subject_file)
    
    old_func_paths   = utils.load_paths_from_subject_list(old_subject_list, analysis_map[analysis_key])
    new_func_paths   = utils.load_paths_from_subject_list(new_subject_list, analysis_map[analysis_key])
    
    assert_equal(np.array(old_func_paths), np.array(new_func_paths))

