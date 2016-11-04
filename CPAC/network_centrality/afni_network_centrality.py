# CPAC/network_centrality/afni_network_centrality.py
#
# Authors: Daniel Clark


'''
This module contains functions which build and return the network
centrality nipype workflow
'''

# Import packages
import nipype.pipeline.engine as pe
import nipype.interfaces.utility as util
import CPAC.network_centrality.utils as utils

try:
    from nipype.interfaces.afni.preprocess import DegreeCentrality, ECM, LFCD
except ImportError:
    from afni_centrality_interfaces import DegreeCentrality, ECM, LFCD


def create_degree_centrality_wf(wf_name, threshold_option, threshold, 
                                        num_threads=1, memory_gb=1.0):

    '''
    Function to create the afni-basedd degree centrality workflow

    Parameters
    ----------
    wf_name : string
        the name of the workflow
    threshold_option : string
        'significance', 'sparsity', or 'correlation'
    threshold : float
        the threshold value for thresholding the similarity matrix
    num_threads : integer (optional); default=1
        the number of threads to utilize for centrality computation
    memory_gb : float (optional); default=1.0
        the amount of memory the centrality calculation will take (GB)

    Returns
    -------
    degree_centrality_wf : nipype Workflow
        the initialized nipype workflow for the afni degree centrality command
    '''
    # Check the centrality parameters
    t = threshold
    if threshold_option == 'sparsity':
        t = threshold/100.0
    method_option, threshold_option = utils.check_degree_centrality_params(threshold_option, t)
    # Init variables
    wf = pe.Workflow(name=wf_name)

    # Create inputspec node
    in_node = pe.Node(util.IdentityInterface(fields=['in_file',
                                                        'template',
                                                        'threshold']),
                         name='inputspec')

    # Input threshold
    in_node.inputs.threshold = threshold

    # Define main input/function node
    degree_centrality = \
        pe.Node(DegreeCentrality(environ={'OMP_NUM_THREADS' : str(num_threads)}),
                name='degree_centrality')
    degree_centrality.inputs.out_file = 'degree_centrality_merged.nii.gz'
    out_names = ('degree_centrality_binarize', 'degree_centrality_weighted')


    # Limit its num_threads and memory via MultiProc plugin
    degree_centrality.interface.num_threads = num_threads
    degree_centrality.interface.estimated_memory_gb = memory_gb

    # Connect input image and mask template
    wf.connect(in_node, 'in_file',
                          degree_centrality, 'in_file')
    wf.connect(in_node, 'template',
                          degree_centrality, 'mask')

    # If we're doing significance thresholding, convert to correlation
    if threshold_option == 'significance':
        # Check and (possibly) convert threshold
        convert_thr = pe.Node(util.Function(input_names=['datafile',
                                                              'p_value',
                                                              'two_tailed'],
                                                 output_names=['rvalue_threshold'],
                                                 function=utils.convert_pvalue_to_r),
                                   name='convert_threshold')
        # Wire workflow to connect in conversion node
        wf.connect(in_node, 'in_file', convert_thr, 'datafile')
        wf.connect(in_node, 'threshold', convert_thr, 'p_value')
        wf.connect(convert_thr, 'rvalue_threshold', degree_centrality, 'thresh')

    # Sparsity thresholding
    elif threshold_option == 'sparsity':
        wf.connect(in_node, 'threshold', degree_centrality, 'sparsity')
    # Correlation thresholding
    elif threshold_option == 'correlation':
        wf.connect(in_node, 'threshold', degree_centrality, 'thresh')

    # Need to separate sub-briks
    sep_subbriks = pe.Node(util.Function(input_names=['nifti_file', 'out_names'],
                              output_names=['output_niftis'],
                              function=utils.sep_nifti_subbriks),
                name='sep_nifti_subbriks')
    sep_subbriks.inputs.out_names = out_names

    # Connect the degree centrality output image to separate subbriks node
    wf.connect(degree_centrality, 'out_file', sep_subbriks, 'nifti_file')

    # Define outputs node
    out_node = pe.Node(util.IdentityInterface(fields=['outfile_list',
                                                         'oned_output']),
                          name='outputspec')

    wf.connect(sep_subbriks, 'output_niftis', out_node, 'outfile_list')

    return wf


# Return the afni eigenvector centrality workflow
def create_eigenvector_centrality_wf(wf_name, threshold_option,
                              threshold, num_threads=1, memory_gb=1.0):
    '''
    Function to create the afni-based Eigenvector centrality workflow

    Parameters
    ----------
    wf_name : string
        the name of the workflow
    threshold_option : string
        'significance', 'sparsity', or 'correlation'
    threshold : float
        the threshold value for thresholding the similarity matrix
    num_threads : integer (optional); default=1
        the number of threads to utilize for centrality computation
    memory_gb : float (optional); default=1.0
        the amount of memory the centrality calculation will take (GB)

    Returns
    -------
    wf : nipype Workflow
        the initialized nipype workflow for the afni eigenvector centrality command
    '''
    # Check the centrality parameters
    t = threshold
    if threshold_option == 'sparsity':
        t = threshold/100.0
    #uses the same validations as degree centrality
    method_option, threshold_option = utils.check_degree_centrality_params(threshold_option, t)

    # Init variables
    wf = pe.Workflow(name=wf_name)

    # Create inputspec node
    in_node = pe.Node(util.IdentityInterface(fields=['in_file', 'template',
                                                        'threshold']),
                         name='inputspec')

    in_node.inputs.threshold = threshold

    # Define main input/function node

    eig_centrality = pe.Node(ECM(environ={'OMP_NUM_THREADS': str(num_threads)}),
            name='eigenvector_centrality')
    eig_centrality.inputs.out_file = 'eigenvector_centrality_merged.nii.gz'
    eig_centrality.inputs.memory = memory_gb
    out_names = ('eigenvector_centrality_binarize',
                 'eigenvector_centrality_weighted')
    
    # Limit its num_threads and memory via MultiProc plugin
    eig_centrality.interface.num_threads = num_threads
    eig_centrality.interface.estimated_memory_gb = memory_gb

    # Connect input image and mask tempalte
    wf.connect(in_node, 'in_file', eig_centrality, 'in_file')
    wf.connect(in_node, 'template', eig_centrality, 'mask')

    # If we're doing significance thresholding, convert to correlation
    if threshold_option == 'significance':
        # Check and (possibly) convert threshold
        convert_thr = pe.Node(util.Function(input_names=['datafile',
                                                              'p_value',
                                                              'two_tailed'],
                                                 output_names=['rvalue_threshold'],
                                                 function=utils.convert_pvalue_to_r),
                                   name='convert_threshold')
        # Wire workflow to connect in conversion node
        wf.connect(in_node, 'in_file', convert_thr, 'datafile')
        wf.connect(in_node, 'threshold', convert_thr, 'p_value')
        wf.connect(convert_thr, 'rvalue_threshold', eig_centrality, 'thresh')

    # Sparsity thresholding
    elif threshold_option == 'sparsity':
        centrality_wf.connect(in_node, 'threshold', eig_centrality, 'sparsity')

    # Correlation thresholding
    elif threshold_option == 'correlation':
        centrality_wf.connect(in_node, 'threshold', eig_centrality, 'thresh')

    # Need to separate sub-briks
    sep_subbriks = \
        pe.Node(util.Function(input_names=['nifti_file', 'out_names'],
                              output_names=['output_niftis'],
                              function=utils.sep_nifti_subbriks),
                name='sep_nifti_subbriks')
    sep_subbriks.inputs.out_names = out_names

    # Connect the degree centrality output image to separate subbriks node
    wf.connect(eig_centrality, 'out_file', sep_subbriks, 'nifti_file')

    # Define outputs node
    out_node = pe.Node(util.IdentityInterface(fields=['outfile_list',
                                                         'oned_output']),
                          name='outputspec')

    wf.connect(sep_subbriks, 'output_niftis', out_node, 'outfile_list')

    # Return the eigenvector centrality workflow
    return wf



# Return the afni lfcd workflow
def create_lfcd_wf(wf_name, threshold_option,
                              threshold, num_threads=1, memory_gb=1.0):
    '''
    Function to create the afni-based lfcd workflow

    Parameters
    ----------
    wf_name : string
        the name of the workflow
    threshold_option : string
        'significance' or 'correlation'
    threshold : float
        the threshold value for thresholding the similarity matrix
    num_threads : integer (optional); default=1
        the number of threads to utilize for centrality computation
    memory_gb : float (optional); default=1.0
        the amount of memory the centrality calculation will take (GB)

    Returns
    -------
    wf : nipype Workflow
        the initialized nipype workflow for the afni lfcd command
    '''
    method_option, threshold_option = \
        utils.check_lfcd_params(threshold_option, threshold)

    # Init variables
    wf = pe.Workflow(name=wf_name)

    # Create inputspec node
    in_node = pe.Node(util.IdentityInterface(fields=['in_file',
                                                        'template',
                                                        'threshold']),
                         name='inputspec')

    # Input threshold
    in_node.inputs.threshold = threshold

    # Define main input/function node
    lfcd = pe.Node(LFCD(environ={'OMP_NUM_THREADS' : str(num_threads)}),
                    name='lfcd')
    lfcd.inputs.out_file = 'lfcd_merged.nii.gz'
    out_names = ('lfcd_binarize', 'lfcd_weighted')

    # Limit its num_threads and memory via MultiProc plugin
    lfcd.interface.num_threads = num_threads
    lfcd.interface.estimated_memory_gb = memory_gb

    # Connect input image and mask tempalte
    wf.connect(in_node, 'in_file', lfcd, 'in_file')
    wf.connect(in_node, 'template', lfcd, 'mask')

    # If we're doing significance thresholding, convert to correlation
    if threshold_option == 'significance':
        # Check and (possibly) convert threshold
        convert_thr = pe.Node(util.Function(input_names=['datafile',
                                                              'p_value',
                                                              'two_tailed'],
                                                 output_names=['rvalue_threshold'],
                                                 function=utils.convert_pvalue_to_r),
                                   name='convert_threshold')
        # Wire workflow to connect in conversion node
        wf.connect(in_node, 'in_file', convert_thr, 'datafile')
        wf.connect(in_node, 'threshold', convert_thr, 'p_value')
        wf.connect(convert_thr, 'rvalue_threshold', lfcd, 'thresh')

    # Correlation thresholding
    elif threshold_option == 'correlation':
        wf.connect(in_node, 'threshold', lfcd, 'thresh')

    # Need to separate sub-briks
    sep_subbriks = \
        pe.Node(util.Function(input_names=['nifti_file', 'out_names'],
                              output_names=['output_niftis'],
                              function=utils.sep_nifti_subbriks),
                name='sep_nifti_subbriks')
    sep_subbriks.inputs.out_names = out_names

    # Connect the degree centrality output image to separate subbriks node
    wf.connect(lfcd, 'out_file', sep_subbriks, 'nifti_file')

    # Define outputs node
    out_node = pe.Node(util.IdentityInterface(fields=['outfile_list',
                                                         'oned_output']),
                          name='outputspec')

    wf.connect(sep_subbriks, 'output_niftis', out_node, 'outfile_list')

    # Return the lfcd workflow
    return wf




# Return the afni centrality/lfcd workflow
def create_afni_centrality_wf(wf_name, method_option, threshold_option,
                              threshold, num_threads=1, memory_gb=1.0):
    '''
    Function to create the afni-based centrality workflow

    Parameters
    ----------
    wf_name : string
        the name of the workflow
    method_option : string
        'degree', 'eigenvector', or 'lfcd'
    threshold_option : string
        'significance', 'sparsity', or 'correlation'
    threshold : float
        the threshold value for thresholding the similarity matrix
    num_threads : integer (optional); default=1
        the number of threads to utilize for centrality computation
    memory_gb : float (optional); default=1.0
        the amount of memory the centrality calculation will take (GB)

    Returns
    -------
    centrality_wf : nipype Workflow
        the initialized nipype workflow for the afni centrality command
    '''

    # Import packages
    import nipype.pipeline.engine as pe
    import nipype.interfaces.utility as util
    import CPAC.network_centrality.utils as utils

    # Check the centrality parameters
    test_thresh = threshold
    if threshold_option == 'sparsity':
        test_thresh = threshold/100.0
    method_option, threshold_option = \
        utils.check_centrality_params(method_option, threshold_option, test_thresh)

    # Init variables
    centrality_wf = pe.Workflow(name=wf_name)

    # Create inputspec node
    input_node = pe.Node(util.IdentityInterface(fields=['in_file',
                                                        'template',
                                                        'threshold']),
                         name='inputspec')

    # Input threshold
    input_node.inputs.threshold = threshold

    # Define main input/function node
    # Degree centrality
    if method_option == 'degree':
        afni_centrality_node = \
            pe.Node(DegreeCentrality(environ={'OMP_NUM_THREADS' : str(num_threads)}),
                    name='afni_centrality')
        afni_centrality_node.inputs.out_file = 'degree_centrality_merged.nii.gz'
        out_names = ('degree_centrality_binarize', 'degree_centrality_weighted')
    # Eigenvector centrality
    elif method_option == 'eigenvector':
        afni_centrality_node = \
        pe.Node(ECM(environ={'OMP_NUM_THREADS' : str(num_threads)}),
                name='afni_centrality')
        afni_centrality_node.inputs.out_file = 'eigenvector_centrality_merged.nii.gz'
        afni_centrality_node.inputs.memory = memory_gb # 3dECM input only
        out_names = ('eigenvector_centrality_binarize',
                     'eigenvector_centrality_weighted')
    # lFCD
    elif method_option == 'lfcd':
        afni_centrality_node = \
            pe.Node(LFCD(environ={'OMP_NUM_THREADS' : str(num_threads)}),
                    name='afni_centrality')
        afni_centrality_node.inputs.out_file = 'lfcd_merged.nii.gz'
        out_names = ('lfcd_binarize', 'lfcd_weighted')

    # Limit its num_threads and memory via MultiProc plugin
    afni_centrality_node.interface.num_threads = num_threads
    afni_centrality_node.interface.estimated_memory_gb = memory_gb

    # Connect input image and mask tempalte
    centrality_wf.connect(input_node, 'in_file',
                          afni_centrality_node, 'in_file')
    centrality_wf.connect(input_node, 'template',
                          afni_centrality_node, 'mask')

    # If we're doing significan thresholding, convert to correlation
    if threshold_option == 'significance':
        # Check and (possibly) conver threshold
        convert_thr_node = pe.Node(util.Function(input_names=['datafile',
                                                              'p_value',
                                                              'two_tailed'],
                                                 output_names=['rvalue_threshold'],
                                                 function=utils.convert_pvalue_to_r),
                                   name='convert_threshold')
        # Wire workflow to connect in conversion node
        centrality_wf.connect(input_node, 'in_file',
                              convert_thr_node, 'datafile')
        centrality_wf.connect(input_node, 'threshold',
                              convert_thr_node, 'p_value')
        centrality_wf.connect(convert_thr_node, 'rvalue_threshold',
                              afni_centrality_node, 'thresh')
    # Sparsity thresholding
    elif threshold_option == 'sparsity':
        # Check to make sure it's not lFCD
        if method_option == 'lfcd':
            err_msg = 'Sparsity thresholding is not supported for lFCD'
            raise Exception(err_msg)
        # Otherwise, connect threshold to sparsity input
        centrality_wf.connect(input_node, 'threshold',
                              afni_centrality_node, 'sparsity')
    # Correlation thresholding
    elif threshold_option == 'correlation':
        centrality_wf.connect(input_node, 'threshold',
                              afni_centrality_node, 'thresh')

    # Need to seprate sub-briks
    sep_subbriks_node = \
        pe.Node(util.Function(input_names=['nifti_file', 'out_names'],
                              output_names=['output_niftis'],
                              function=utils.sep_nifti_subbriks),
                name='sep_nifti_subbriks')
    sep_subbriks_node.inputs.out_names = out_names

    # Connect the degree centrality output image to seperate subbriks node
    centrality_wf.connect(afni_centrality_node, 'out_file',
                          sep_subbriks_node, 'nifti_file')

    # Define outputs node
    output_node = pe.Node(util.IdentityInterface(fields=['outfile_list',
                                                         'oned_output']),
                          name='outputspec')

    centrality_wf.connect(sep_subbriks_node, 'output_niftis',
                          output_node, 'outfile_list')

    # Return the centrality workflow
    return centrality_wf
