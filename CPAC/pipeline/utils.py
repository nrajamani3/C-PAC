import os, yaml
import numpy as np
from CPAC.utils import Configuration


def load_configuration(config_file):
    """
    Load the yaml file as a Configuration class.
    """
    yaml_content = yaml.load(open(os.path.realpath(config_file), 'r'))
    return Configuration(yaml_content)

def load_subject_list(subject_list_file):
    """
    Load list of subjects from a file
    """
    with open(subject_list_file, 'r') as f:
        sublist_items   = f.readlines()
        subject_list    = [ line.rstrip('\n') for line in sublist_items \
                                if not (line == '\n') and not line.startswith('#') ]
    return subject_list

def load_paths_from_subject_list(subject_list, subject_infos, remove_duplicates=True):
    """
    Load paths to data based on subject list and info/paths for all possible subjects.
    Order of the paths will be the same as the order of subjects in `subject_list`.
    If any subject is missing a path, then the function will raise an Exception.
    """
    _, _, _, s_paths  = (list(tup) for tup in zip(*subject_infos))
    
    if remove_duplicates: # duplicate paths
        s_paths = list(set(s_paths))
    
    # We get the paths in the order of the requested subjects
    # Any missing paths are saved for later
    ordered_paths = []
    missing_subjs = []
    for sub in subject_list:
        subject_found = False
        for path in s_paths:
            if sub in path:
                ordered_paths.append(path)
                subject_found = True
        if not subject_found:
            missing_subjs.append(sub)
    
    # Fail if any paths are missing
    if missing_subjs:
        print "----"
        print "The following subjects are missing paths (e.g., %s)" % s_paths[0]
        for sub in missing_subjs:
            print sub
        print "----"
        raise Exception("Missing paths for %i subjects" % len(missing_subjs))
    
    return ordered_paths


###
# For cpac_group_analysis_pipeline.py
###

def remove_missing_subjects(conf, subject_infos, odir=None):
    """
    Simple function that checks if the list of subjects actually have data.
    When any subject doesn't have data, this program will exclude those subjects 
    and continue with the remaining ones. A new subject list will be saved and
    will replace the subject list file that is given in `config_file`.
    
    Parameters
    ----------
    conf : object
        The configuration file object containing all the variables specified in the configuration file.
    subject_infos : dict
        Mapping of output types (e.g., functional_mni) to information on each subject's associated output.
        Information on each subject's output is a list of length 4 and this includes pipeline_id, subject_id, 
        scan_id, and subject_path.
    odir : str
        Path for the output directory of the subject file. If this is None, then
        it will default to within the sink directory of the input subject_infos files.
    
    Returns
    -------
    conf : object
        Same as input except the subjectListFile attribute will have been modified.
    """
    
    print "==============="
    print "Filter Subject List"
    
    # Setup
    p_id, s_ids, scan_ids, s_paths  = (list(tup) for tup in zip(*subject_infos))
    if odir is None:
        odir = config.outputModelFilesDirectory
    
    # Load list of subjects
    subject_list = load_subject_list(conf.subjectListFile)
    
    # List of subject paths which do exist
    exist_paths = []
    for sub in subject_list:    # Loop through desired subjects
        for path in s_paths:    # Loop through all subject paths
            if sub in path:     # Is this path of one of the subjects?
                exist_paths.append(sub)
    
    # Check to see if any derivatives of subjects are missing
    # This doesn't do anything except print some information
    test_missing = list(set(subject_list) - set(exist_paths))
    if len(test_missing) >0:
        print "-------------------------------------------"
        print "List of outputs missing for %i/%i subjects:" % (len(test_missing), len(set(subject_list)))
        print list(test_missing)
        print "\n"
        print "..at paths:"
        print os.path.dirname(s_paths[0]).replace(s_ids[0], '*')
        print "-------------------------------------------"
        print '\n'
    
    # Create directory and all sub-directories if needed
    if not os.path.exists(odir):
        os.makedirs(odir)
        print "Creating directory: %s" % odir
    
    # Create a new subject path list within the output directory
    # And set the subject list file to this new file
    try:
        new_sub_file    = os.path.join(odir, os.path.basename(conf.subjectListFile))
        f               = open(new_sub_file, 'w')
        for sub in exist_paths:
            print >>f, sub
        f.close()
        conf.subjectListFile = new_sub_file
        print "Replacing original list with filtered one: %s" % new_sub_file
    except:
        print "Error: Could not open subject list file: %s\n" % new_sub_file
        raise Exception
    
    print "==============="
    
    return new_sub_file


def create_models_for_cwas(conf):
    """
    This runs create_fsl_model and then parses the outputs to remove the header information.
    """
    from glob import glob
    
    # Run 'create_fsl_model' script to extract phenotypic data from
    # the phenotypic file for each of the subjects in the subject list
    try:
        from CPAC.utils import create_fsl_model
        create_fsl_model.run(conf, True)
    except Exception, e:
        print "FSL Group Analysis model not successfully created - error in create_fsl_model script"
        raise
    
    # Paths to the mat, grp, and con outputs
    mat_file = glob(os.path.join(conf.outputModelFilesDirectory, "*.mat"))[0]
    con_file = glob(os.path.join(conf.outputModelFilesDirectory, "*.con"))[0]
    grp_file = glob(os.path.join(conf.outputModelFilesDirectory, "*.grp"))[0]
    
    
    ## Regressors
    
    # Read mat file without FSL header information
    # containing regressors
    mat = np.loadtxt(mat_file, skiprows=5)
    
    
    ## Contrasts
    
    # Read in con file. Can only have one contrast or F-test
    # First get number of lines to skip
    with open(con_file, 'r') as f:
        line_skip = [ i+1 for i,l in enumerate(f.readlines()) if l.strip() == "/Matrix" ][0]
    con = np.loadtxt(con_file, skiprows=line_skip)
    
    # Ensure that only one contrast exists and has 0s and 1s
    if len(con.shape) != 1:
        raise Exception("You can only have one contrast for CWAS. For multiple contrasts, create a new config file.")
    for i in set(con):
        if i not in [0,1]:
            raise Exception("You can only have 0's and 1's in contrasts for CWAS.")
    
    # Convert into a list of column indices
    cols = con.nonzero()
    
    
    ## Strata
    
    # Read in the permutation stratafication file
    strata = np.loadtxt(grp_file, skiprows=4)
    
    # Set to None if all values are the same
    # Otherwise to a list
    if np.all(strata == strata[0]):
        strata = None
    else:
        strata = strata.tolist()
        
        
    return (mat, cols, strata)


###
# For cpac_group_runner.py
###

def gen_file_map(sink_dir, resource_paths=None):
    """
    Generate the mapping of different resources (e.g., functional_mni or sca) 
    to the file paths of those resources across subjects/scans. Note that this
    will only work with functional paths that have a scan_id in their path and
    will fail for any anatomical resources since those are assumed to only have
    one scan.
    
    Parameters
    ----------
    sink_dir : string
        Path to CPAC output or sink directory containing different pipeline 
        directories each with preprocessed data for individual subjects
    resource_paths : None or string or list (default = None)
        Path to file(s) in each subject's CPAC directory containing path information.
        Can include glob-style * or ? that will be expanded and can be a string or list.
        If this is None, then it will autoset to `os.path.join(sink_dir, 'pipeline_*', '*', 'path_files_here', '*.txt')`.
    
    Returns
    -------
    subject_infos : dict
        Mapping of output types (e.g., functional_mni) to information on each subject's associated output.
        Information on each subject's output is a list of length 4 and this includes pipeline_id, subject_id, 
        scan_id, and subject_path.
    """
    import os
    from glob import glob
    from CPAC.pipeline.cpac_group_runner import split_folders
    
    if resource_paths is None:
        resource_paths = os.path.join(sink_dir, 'pipeline_*', '*', 'path_files_here', '*.txt')
    
    if isinstance(resource_paths, str):
        resource_paths = [resource_paths]
    
    # Look through resource paths and expand
    # Then read in file paths
    subject_paths = []
    for resource_path in resource_paths:
        files = glob(os.path.abspath(resource_path))
        for file in files:
            path_list = open(file, 'r').readlines()
            subject_paths.extend([s.rstrip('\r\n') for s in path_list])
    
    if len(subject_paths) == 0:
        raise Exception("No subject paths found based on given resource_paths")
    
    # Remove any duplicate paths
    set_subject_paths   = set(subject_paths)
    subject_paths       = list(set_subject_paths)
    
    # Setup an mapping between resource and path info
    # so a dictionary with a list as the default value
    from collections import defaultdict
    analysis_map    = defaultdict(list)
    
    # Parse each subject path into 4 relevant parts: 
    # pipeline_id, subject_id, scan_id, and subject_path
    for subject_path in subject_paths:
        # Removes the base path
        if subject_path.find(sink_dir) == -1:
            print "WARNING: Couldn't find sink_dir: %s in subject's path: %s" % (sink_dir, subject_path)
        rs_path     = subject_path.replace(sink_dir, "", 1)
        rs_path     = rs_path.lstrip('/')
        
        # Split the path into a list (of folders)
        folders     = split_folders(rs_path)
                
        # If there aren't at least 4 sub-folders, then something is amiss
        if len(folders) < 3:
            raise Exception("Incorrect subject path, need 3-4 but only %i sub-folders found: %s" % (len(folders), subject_path))
        
        # Extract the desired elements
        pipeline_id = folders[0]
        subject_id  = folders[1]
        resource_id = folders[2]    # e.g., functional_mni, falff, etc
        if len(folders) == 3:
            scan_id = ""
        else:
            scan_id = folders[3]
        
        # Add to the mappings (seperate one for group analysis)
        # Note that the key is actually a tuple of the resource_id and key
        key         = subject_path.replace(subject_id, '*')
        analysis_map[(resource_id, key)].append((pipeline_id, subject_id, scan_id, subject_path))
    
    return analysis_map

