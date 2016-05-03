# CPAC/utils/datasource.py
#

'''
This module contains classes and functions used to interface with data
access
'''

# Import packages
import nipype.pipeline.engine as pe
import nipype.interfaces.utility as util


def create_anat_datasource(wf_name='anat_datasource'):
    '''
    Gather anatomical images
    '''

    # Import packages
    import nipype.pipeline.engine as pe
    import nipype.interfaces.utility as util

    # Init workflow
    wf = pe.Workflow(name=wf_name)

    inputnode = pe.Node(util.IdentityInterface(
                                fields=['subject', 'anat', 'creds_path'],
                                mandatory_inputs=True),
                        name='inputnode')

    check_s3_node = pe.Node(util.Function(input_names=['file_path', 'creds_path',
                                                       'img_type'],
                                          output_names=['local_path'],
                                          function=check_for_s3),
                            name='check_for_s3')

    wf.connect(inputnode, 'anat', check_s3_node, 'file_path')
    wf.connect(inputnode, 'creds_path', check_s3_node, 'creds_path')
    check_s3_node.inputs.img_type = 'anat'

    outputnode = pe.Node(util.IdentityInterface(fields=['subject',
                                                        'anat']),
                         name='outputspec')

    wf.connect(inputnode, 'subject', outputnode, 'subject')
    wf.connect(check_s3_node, 'local_path', outputnode, 'anat')

    # Return the workflow
    return wf


def create_func_datasource(wf_name='func_datasource'):
    '''
    '''

    # Import packages
    import nipype.pipeline.engine as pe
    import nipype.interfaces.utility as util

    # Init workflow
    wf = pe.Workflow(name=wf_name)

    # Inputnode
    input_node = pe.Node(util.IdentityInterface(fields=['subject',
                                                        'rest_key'
                                                        'rest_path',
                                                        'creds_path'],
                                               mandatory_inputs=True),
                        name='inputspec')

    # Check for S3 and scan dims
    check_s3_node = pe.Node(util.Function(input_names=['file_path',
                                                       'creds_path',
                                                       'img_type'],
                                          output_names=['local_path'],
                                          function=check_for_s3),
                            name='check_for_s3')
    check_s3_node.inputs.img_type = 'func'
    wf.connect(input_node, 'rest_scan', check_s3_node, 'file_path')
    wf.connect(input_node, 'creds_path', check_s3_node, 'creds_path')

    # Output spec
    output_node = pe.Node(util.IdentityInterface(fields=['subject',
                                                         'rest',
                                                         'scan' ]),
                         name='outputspec')
    wf.connect(input_node, 'subject', output_node, 'subject')
    wf.connect(check_s3_node, 'local_path', output_node, 'rest')
    wf.connect(input_node, 'rest_key', output_node, 'scan')

    # Return the workflow
    return wf


def return_subdict_values(subject_id, subid_dict, log_base_dir):
    '''
    Function to return various attributes from a subject dictionary

    Parameters
    ----------
    subject_id : string
        unique subject identifier key to extract subject-specific dictionary
        from subid_dict
    subid_dict : dictionary
        a dictionary where the keys are subject id strings and values
        are subject-specific dictionaries
    log_base_dir : string
        filepath to the base log directory

    Returns
    -------
    subject_id : string
        unique subject identifier key
    input_creds_path : string
        filepath to the local location of the S3 bucket credentials to
        download input images
    anat_path : string
        filepath to anatomical image
    rest_key : string
        name of scan for functional image
    rest_path : string
        filepath to functional image
    sub_log_dir : string
        directory to subject's log files
    scan_params : dict
        dictionary if it exists, otherwise it is None
    '''

    # Import packages
    import os

    # Get subject dictionary
    try:
        sub_dict = subid_dict[subject_id]
    except KeyError as exc:
        err_msg = 'Subject ID: %s not found in subject list!\nError: %s' \
                  % (subject_id, exc)
        raise Exception(err_msg)

    # Extract credentials path if it exists
    try:
        creds_path = sub_dict['creds_path']
        if creds_path and 'none' not in creds_path.lower():
            if os.path.exists(creds_path):
                input_creds_path = os.path.abspath(creds_path)
            else:
                err_msg = 'Credentials path: "%s" for subject "%s" was not '\
                          'found. Check this path and try again.' % (creds_path, subject_id)
                raise Exception(err_msg)
        else:
            input_creds_path = None
    except KeyError:
        input_creds_path = None

    # Anatomical filepath
    try:
        anat_path = sub_dict['anat']
    except KeyError as exc:
        err_msg = 'Anatomical image not present in subject dictionary!'\
                  '\nError: %s' % exc
        raise Exception(err_msg)

    # Functional filepath
    try:
        rest_path = sub_dict['rest']
        rest_key = sub_dict['rest_key']
    except KeyError as exc:
        err_msg = 'Functional data not found in subject dictionary!\nError: %s' \
                  % (exc)
        raise Exception(err_msg)

    # Scan parameters
    if sub_dict.has_key('scan_parameters'):
        scan_params = sub_dict['scan_parameters']
    else:
        scan_params = None

    # Log directory for subject
    sub_log_dir = os.path.join(log_base_dir, subject_id)
    if not os.path.exists(sub_log_dir):
        os.makedirs(sub_log_dir)

    # Return subject-specific info
    return subject_id, input_creds_path, anat_path,\
           rest_key, rest_path, sub_log_dir, scan_params


def check_for_s3(file_path, creds_path, dl_dir=None, img_type='anat'):
    '''
    Function to check if a filepath is on S3 or not; if it is, download
    it and return the local downloaded file path

    Parameters
    ----------
    file_path : string
        filepath of the input to download (must start with 's3://')
    creds_path : string
        local filepath to the credentials used to access private files
        stored in S3
    dl_dir : string (optional); default=None
        local directory to download s3 file to, if not specified, the
        file will be downloaded to the current directory
    img_type : string (optional); default='anat'
        type of image; acceptable arguments are 'anat' or 'func'; this
        parameter indicates the file type so that its dimensionality
        can be checked prior to downloading

    Returns
    -------
    local_path : string
        local filepath to the input image file
    '''

    # Import packages
    import os
    import nibabel as nib
    import botocore.exceptions

    from indi_aws import fetch_creds

    # Init variables
    s3_str = 's3://'
    if dl_dir is None:
        dl_dir = os.getcwd()

    # Explicitly lower-case the "s3"
    if file_path.lower().startswith(s3_str):
        file_path_sp = file_path.split('/')
        file_path_sp[0] = file_path_sp[0].lower()
        file_path = '/'.join(file_path_sp)

    # Check for s3 string in filepaths
    if file_path.startswith(s3_str):
        # Get bucket name and bucket object
        bucket_name = file_path.replace(s3_str, '').split('/')[0]
        bucket = fetch_creds.return_bucket(creds_path, bucket_name)

        # Extract relative key path from bucket and local path
        s3_prefix = os.path.join(s3_str, bucket_name)
        s3_key = file_path.replace(s3_prefix, '').lstrip('/')
        local_path = os.path.join(dl_dir, os.path.basename(s3_key))

        # Get local directory and create folders if they dont exist
        local_dir = os.path.dirname(local_path)
        if not os.path.exists(local_dir):
            os.makedirs(local_dir)

        # Download file
        try:
            bucket.download_file(Key=s3_key, Filename=local_path)
        except botocore.exceptions.ClientError as exc:
            error_code = int(exc.response['Error']['Code'])
            if error_code == 403:
                err_msg = 'Access to bucket: "%s" is denied; using credentials '\
                          'in subject list: "%s"; cannot access the file "%s"'\
                          % (bucket_name, creds_path, file_path)
                raise Exception(err_msg)
            elif error_code == 404:
                err_msg = 'Bucket: "%s" does not exist; check spelling and try '\
                          'again' % bucket_name
                raise Exception(err_msg)
            else:
                err_msg = 'Unable to connect to bucket: "%s". Error message:\n%s'\
                          % (bucket_name, exc)
        except Exception as exc:
            err_msg = 'Unable to connect to bucket: "%s". Error message:\n%s'\
                      % (bucket_name, exc)
            raise Exception(err_msg)

    # Otherwise just return what was passed in
    else:
        local_path = file_path

    # Check image dimensionality
    img_nii = nib.load(local_path)
    if img_type == 'anat':
        if len(img_nii.shape) != 3:
            raise IOError('File: %s must be an anatomical image with 3 '\
                          'dimensions but %d dimensions found!' % len(img_nii.shape))
    elif img_type == 'func':
        if len(img_nii.shape) != 4:
            raise IOError('File: %s must be a functional image with 4 '\
                          'dimensions but %d dimensions found!' % len(img_nii.shape))

    # Return the local path
    return local_path


def create_roi_mask_dataflow(masks, wf_name='datasource_roi_mask'):


    import nipype.interfaces.io as nio
    import os

    wf = pe.Workflow(name=wf_name)  

    mask_dict = {}

    for mask_file in masks:

        mask_file = mask_file.rstrip('\r\n')

        if not os.path.exists(mask_file):
            err = '\n\n[!] CPAC says: One of your ROI/mask specification ' \
                  'files (under ROI TSE Options) does not have a correct ' \
                  'path or does not exist.\nTip: If all the paths are okay, '\
                  'then ensure there are no whitespaces or blank lines in ' \
                  'your ROI specification file.\n\n'
            raise Exception(err)

        if mask_file.strip() == '' or mask_file.startswith('#'):
            continue

        base_file = os.path.basename(mask_file)
        base_name = ''
        if base_file.endswith('.nii'):
            base_name = os.path.splitext(base_file)[0]
        elif(base_file.endswith('.nii.gz')):
            base_name = os.path.splitext(os.path.splitext(base_file)[0])[0]
        else:
            err = "\n\n[!] CPAC says: One of your ROI/mask specification " \
                  "files (under ROI TSE options) does not have '.nii' or " \
                  "'.nii.gz' as an extension.\n\nMask file: %s\n\n" \
                  % mask_file
            raise Exception(err)

        if not (base_name in mask_dict):
            mask_dict[base_name] = mask_file
        else:
            err = "\n\n[!] CPAC says: You have two or more ROI/mask files " \
            "with the same name - please make sure these files are named " \
            "differently.\n\nDuplicate name: %s\n\n" % mask_file
            raise Exception(err)


    inputnode = pe.Node(util.IdentityInterface(
                            fields=['mask'],
                            mandatory_inputs=True),
                    name='inputspec')

    inputnode.iterables = [('mask', mask_dict.keys())]

    selectmask = pe.Node(util.Function(input_names=['scan', 'rest_dict'],
                                       output_names=['out_file'],
                                       function=get_rest),
                         name='select_mask')
    selectmask.inputs.rest_dict = mask_dict

    outputnode = pe.Node(util.IdentityInterface(fields=['out_file']),
                         name='outputspec')

    wf.connect(inputnode, 'mask',
               selectmask, 'scan')

    wf.connect(selectmask, 'out_file',
               outputnode, 'out_file')

    return wf



def create_spatial_map_dataflow(spatial_maps, wf_name='datasource_maps'):

    import nipype.interfaces.io as nio
    import os

    wf = pe.Workflow(name=wf_name)
    
    spatial_map_dict = {}
    
    for spatial_map_file in spatial_maps:

        spatial_map_file = spatial_map_file.rstrip('\r\n')

        if not os.path.exists(spatial_map_file):
            print "\n\n" + "ERROR: One of your spatial map files (under Spatial" + \
            " Regression options) does not have a correct path or does not exist." + \
            "\n" + "Tip: If all the paths are okay, then ensure there are no" + \
            " whitespaces or blank lines in your spatial map specification file." + \
            "\n\n" + "Error name: datasource_0001" + "\n\n"
            raise Exception

        base_file = os.path.basename(spatial_map_file)
        base_name = ''
        try:
            if base_file.endswith('.nii'):
                base_name = os.path.splitext(base_file)[0]
            elif(base_file.endswith('.nii.gz')):
                base_name = os.path.splitext(os.path.splitext(base_file)[0])[0]
            else:
                raise Exception("File extension not in  .nii and .nii.gz File: %s" % spatial_map_file)
        except Exception, e:
            print('error in spatial_map_dataflow: ', e)

        if not (base_name in spatial_map_dict):
            spatial_map_dict[base_name] = spatial_map_file
        else:
            raise ValueError('Files with same name not allowed %s %s' % (spatial_map_file, spatial_map_dict[base_name]))

    inputnode = pe.Node(util.IdentityInterface(
                            fields=['spatial_map'],
                            mandatory_inputs=True),
                    name='inputspec')

    inputnode.iterables = [('spatial_map', spatial_map_dict.keys())]

    select_spatial_map = pe.Node(util.Function(input_names=['scan', 'rest_dict'],
                                       output_names=['out_file'],
                                       function=get_rest),
                         name='select_spatial_map')
    select_spatial_map.inputs.rest_dict = spatial_map_dict

    wf.connect(inputnode, 'spatial_map',
               select_spatial_map, 'scan')

    return wf



def create_grp_analysis_dataflow(wf_name='gp_dataflow'):

        import nipype.pipeline.engine as pe
        import nipype.interfaces.utility as util
        from CPAC.utils import select_model_files

        wf = pe.Workflow(name=wf_name)

        inputnode = pe.Node(util.IdentityInterface(fields=['ftest',
                                                           'grp_model',
                                                           'model_name'],
                                                   mandatory_inputs=True),
                            name='inputspec')

        selectmodel = pe.Node(util.Function(input_names=['model',
                                                         'ftest',
                                                         'model_name'],
                                           output_names=['fts_file',
                                                         'con_file',
                                                         'grp_file',
                                                         'mat_file'],
                                           function=select_model_files),
                             name='selectnode')

        wf.connect(inputnode, 'ftest',
                   selectmodel, 'ftest')
        wf.connect(inputnode, 'grp_model',
                   selectmodel, 'model')
        wf.connect(inputnode, 'model_name', selectmodel, 'model_name')



        outputnode = pe.Node(util.IdentityInterface(fields=['fts',
                                                            'grp',
                                                            'mat',
                                                            'con'],
                                mandatory_inputs=True),
                    name='outputspec')

        wf.connect(selectmodel, 'mat_file',
                   outputnode, 'mat')
        wf.connect(selectmodel, 'grp_file',
                   outputnode, 'grp') 
        wf.connect(selectmodel, 'fts_file',
                   outputnode, 'fts')
        wf.connect(selectmodel, 'con_file',
                   outputnode, 'con')


        return wf
