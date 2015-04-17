# CPAC/AWS/aws_utils.py
#
# Contributing authors:
# Daniel Clark

'''
This module contains functions which assist in interacting with AWS
services, including uploading/downloading data and file checking.
'''

# Build a subject list from S3 bucket keys
def build_s3_sublist(bucket_name, anat_fp_template, func_fp_template):
    '''
    Function to build a C-PAC subject list from S3 bucket keys
                     download_dir, output_dir, sublist_name, **kwargs):

    Parameters
    ----------
    bucket_name : string
        string of the bucket name
    anat_fp_template : string
        anatomical filepath pattern with site and subject-level
        directories replaced with a %s wildcard;
        any session folder or filename variation should be captured
        with the * wildcard
    func_fp_template : string
        functional filepath pattern with site and subject-level
        directories replaced with a %s wildcard;
        any session folder or filename variation should be captured
        with the * wildcard
    output_dir : string
        filepath to a local directory where the subject list yaml file
        will be saved to
    sublist_name : string
        name of the subject list
    scan_params_file : string (optional), default=None
        filepath to a scan parameters file containing scan acquisition
        information
    subs_to_include : list (optional), default=None
        a list of strings of subject identifiers to only include;
        these names should match the subject-level folders names
    subs_to_exclude : list (optional), default=None
        a list of strings of subject identifiers to only exclude;
        these names should match the subject-level folders names
    sites_to_include : list (optional), default=None
        a list of strings of site identifiers to only include;
        these names should match the site-level folders names

    Returns
    -------
    None
        this function does not return a value, it downloads the subjects from
        the C-PAC subject list to disk from S3
    '''

    # Import packages
    import fnmatch
    import os
    from CPAC.AWS import fetch_creds

    # Init variables
    subject_list = []
    bucket = fetch_creds.return_bucket(bucket_name)
    anat_prefix = anat_fp_template.split('%s')[0]
    func_prefix = func_fp_template.split('%s')[0]

    # Make sure anat and func prefixes match
    if anat_prefix == func_prefix:
        bucket_prefix = anat_prefix
    else:
        err_msg = 'Anatomical and functional data must sit in the same ' \
                  'base folder.\nAnatomical base: %s\nFunctional base: %s' \
                  % (anat_prefix, func_prefix)
        raise Exception(err_msg)

    # Also check that files are nifti only
    if not (anat_fp_template.endswith('.nii.gz') or \
            anat_fp_template.endswith('.nii')):
        err_msg = 'Template does not look for nifti files. ' \
                  'Convert data to nifti and provide new template.\n' \
                  'Anat template: %s' % anat_fp_template
        raise Exception(err_msg)
    elif not (func_fp_template.endswith('.nii.gz') or \
              func_fp_template.endswith('.nii')):
        err_msg = 'Template does not look for nifti files. ' \
                  'Convert data to nifti and provide new template.\n' \
                  'Func template: %s' % func_fp_template
        raise Exception(err_msg)

    # Collect S3 filepaths
    s3_fpaths = collect_s3_filepaths(bucket, bucket_prefix)

    # Filter out anything that doesn't match template pattern
    anat_pattern = anat_fp_template.replace('%s', '*')
    func_pattern = func_fp_template.replace('%s', '*')

    anat_files = [fpath for fpath in s3_fpaths \
                  if fnmatch.fnmatch(fpath, anat_pattern)]
    func_files = [fpath for fpath in s3_fpaths \
                  if fnmatch.fnmatch(fpath, func_pattern)]

    # Make sure files were found
    if len(anat_files) == 0 or len(func_files) == 0:
        err_msg = 'Unable to find needed files matching file pattern.\n' \
                  'Number of anat files: %s\nNumber of func files: %d' \
                  % (len(anat_files), len(func_files))
        raise Exception(err_msg)

    # Get site, subject, session indices and make sure anat and func match
    site_idx, subject_idx, session_idx = \
            return_template_indices(anat_fp_template, func_fp_template)

    # Now iterate through anatomical and pull matching functional
    print 'Building subject list from found files...'
    for anat_file in anat_files:
        af_list = anat_file.split('/')
        # Get site from anat, and insert into func pattern
        site = af_list[site_idx]
        func_pattern = func_fp_template.replace('%s', site, 1)
        # Get subject_id from anat, and insert into func pattern
        subject = af_list[subject_idx]
        func_pattern = func_pattern.replace('%s', subject, 1)
        # If sessions found, set up func pattern
        if session_idx != subject_idx:
            # Grab session from list and insert into pattern
            session = af_list[session_idx]
            fpattern_list = func_pattern.split('/')
            fpattern_list[session_idx] = session
            func_pattern = '/'.join(fpattern_list)
            # And populate unique_id
            unique_id = session
        # Otherwise, no sessions directories, use site as unique id
        else:
            unique_id = site

        # Subject scans dict
        subject_dict = {'anat' : '', 'rest' : {},
                       'subject_id' : '', 'unique_id' : ''}
        subject_dict ['anat'] = anat_file
        subject_dict['subject_id'] = subject
        subject_dict['unique_id'] = unique_id

        # Pull out all matching functional data and insert into subject dict
        matching_funcs = [func for func in func_files \
                          if fnmatch.fnmatch(func, func_pattern)]
        for func_file in matching_funcs:
            func_list = func_file.split('/')
            func_key = '_'.join(func_list[session_idx+1:]).split('.')[0]
            subject_dict['rest'][func_key] = func_file

        # Finally, append subject dict to overall subject list
        subject_list.append(subject_dict)

    # Return the subject list
    return subject_list


# Get site, subject, session indices of filepath templates
def return_template_indices(anat_fp_template, func_fp_template):
    '''
    Function that will return the index of the site, subject,
    and session-level directories using the '/' path delimiter

    fp_template format: /base/%s/%s/../file.nii.gz

    The first '%s' corresponds to the site-level directory, the second
    '%s' corresponds to the subject-level diretory; any intermediary
    folders after the subject-level directory that contain both
    anatomical and functional data will be considered a session
    directory

    Parameters
    ----------
    anat_fp_template : string
        filepath template of the input data to collect; this must be of
        the form /base/%s/%s/../anat_file.nii.gz
    func_fp_template : string
        filepath template of the input data to collect; this must be of
        the form /base/%s/%s/../func_file.nii.gz

    Returns
    -------
    site_idx : integer
        the site-level directory index
    subject_idx : integer
        the subject-level directory index
    session_idx : integer
        the session-level directory index; if there are no session
        session folders found, this will be the same as subject_idx
    '''

    # Init variables
    anat_fp_list = anat_fp_template.split('/')
    func_fp_list = func_fp_template.split('/')

    # Grab site index and check they are the same
    anat_site_idx = anat_fp_list.index('%s')
    func_site_idx = func_fp_list.index('%s')

    if anat_site_idx == func_site_idx:
        site_idx = anat_site_idx
    else:
        err_msg = 'Anatomical and functional data must be within the same ' \
                  'site folders. Re-organize data or check templates.\n' \
                  'Anat template: %s\nFunc template: %s' \
                  % (anat_fp_template, func_fp_template)
        raise Exception(err_msg)

    # Grab subject index and check they are the same
    anat_sub_idx = anat_fp_list[site_idx+1:].index('%s')
    func_sub_idx = func_fp_list[site_idx+1:].index('%s')

    anat_sub_idx = site_idx + 1 + anat_sub_idx
    func_sub_idx = site_idx + 1 + func_sub_idx

    if anat_sub_idx == func_sub_idx:
        subject_idx = anat_sub_idx
    else:
        err_msg = 'Anatomical and functional data must be within the same ' \
                  'subject folders. Re-organize data or check templates.\n' \
                  'Anat template: %s\nFunc template: %s' \
                  % (anat_fp_template, func_fp_template)
        raise Exception(err_msg)

    # Grab session index, if it exists
    anat_tail_dirs = anat_fp_list[subject_idx+1:]
    func_tail_dirs = func_fp_list[subject_idx+1:]
    # Go through both directory tails and see how long dirs match
    # The last match between the two is the session folder
    session_idx = subject_idx
    for anat_dirname in anat_tail_dirs:
        func_dirname = func_tail_dirs[session_idx-subject_idx]
        if anat_dirname == func_dirname:
            session_idx += 1
        else:
            break

    # Return the indices
    return site_idx, subject_idx, session_idx


# Collect filepaths from S3 bucket
def collect_s3_filepaths(bucket, bucket_prefix):
    '''
    Function to collect all of the files in a directory into a list of
    full paths

    Parameters
    ----------
    bucket : boto.s3.bucket.Bucket
        the S3 bucket to collect filepaths from
    bucket_prefix : string
        prefix to the the location where all of the keys are stored in
        the S3 bucket

    Returns
    -------
    file_paths : list
        a list of filepaths, each filepath is the full S3 keyname
    '''

    # Import packages

    # Init variables
    file_paths = []

    # Print status
    print 'Building list of filepaths...\nbucket: %s\nprefix: %s' \
            % (bucket.name, bucket_prefix)

    # Build the list
    for b_key in bucket.list(prefix=bucket_prefix):
        bkey_name = str(b_key.name)
        file_paths.append(bkey_name)

    # Print finished
    print 'Done!'

    # Return the list
    return file_paths


# Download the subjects
def download_subject_data(subject_list, download_dir):
    '''
    Function to download the subject input files from a C-PAC subject
    list to a directory

    Parameters
    ----------
    subject_list : list
        a list of dictionaries, each of which corresponds to a subject
        data bundle comprising of their various input data filepaths
    download_dir : string
        filepath to a directory to save the subject input data to

    Returns
    -------
    '''


# Get the MD5 sums of files on S3
def md5_sum(bucket, prefix='', filt_str=''):
    '''
    Function to get the filenames and MD5 checksums of files stored in
    an S3 bucket and return this as a dictionary.

    Parameters
    ----------
    bucket : boto.s3.bucket.Bucket instance
        an instance of the boto S3 bucket class to download from
    prefix : string (optional), default=''
        the bucket prefix where all of the file keys are located
    filt_str : string (optional), defualt=''
        a string to filter the filekeys of interest;
        e.g. 'matrix_data' will only return filekeys with the string
        'matrix_data' in their filepath name

    Returns
    -------
    md5_dict : dictionary {str : str}
        a dictionary where the keys are the S3 filename and the values
        are the MD5 checksum values
    '''

    # Init variables
    blist = bucket.list(prefix)
    md5_dict = {}

    # And iterate over keys to copy over new ones
    for fkey in blist:
        filename = str(fkey.key)
        if filt_str in filename:
            md5_sum = str(fkey.etag).strip('"')
            md5_dict[filename] = md5_sum
            print 'filename: %s' % filename
            print 'md5_sum: %s' % md5_sum

    # Return the dictionary
    return md5_dict


# Rename s3 keys from src_list to dst_list
def s3_rename(bucket, src_list, dst_list,
              keep_old=False, overwrite=False, make_public=False):
    '''
    Function to rename files from an AWS S3 bucket via a copy and delete
    process. Uses all keys in src_list as the original names and renames
    the them to the corresponding keys in the dst_list.
    (e.g. src_list[9] --> dst_list[9])

    Parameters
    ----------
    bucket : boto.s3.bucket.Bucket instance
        an instance of the boto S3 bucket class to download from
    src_list : list (str)
        a list of relative paths of the files to delete from the bucket
    dst_list : list (str)
        a list of relative paths of the files to delete from the bucket
    keep_old : boolean (optional), default=False
        flag indicating whether to keep the src_list files
    overwrite : boolean (optional), default=False
        flag indicated whether to overwrite the files in dst_list
    make_public : boolean (optional), default=False
        set to True if files should be publically available on S3
    Returns
    -------
    None
        The function doesn't return any value, it deletes data from
        S3 and prints its progress and a 'done' message upon completion
    '''

    # Check list lengths are equal
    if len(src_list) != len(dst_list):
        raise ValueError('src_list and dst_list are different lengths!')

    # Init variables
    i = 0
    no_files = len(src_list)

    # And iterate over keys to copy over new ones
    for f in src_list:
        src_key = bucket.get_key(f)
        if not src_key:
            print 'source file %s doesnt exist, skipping...' % f
            continue
        dst_key = dst_list[i]
        dst_exists = bucket.get_key(dst_key)
        if not dst_exists or overwrite:
            print 'copying source: ', str(src_key.key)
            print 'to destination: ', dst_key
            src_key.copy(bucket.name, dst_key)
            if make_public:
                print 'making public...'
                dk = bucket.get_key(dst_key)
                dk.make_public()
            if not keep_old:
                src_key.delete()
        else:
            print '%s exists and not overwriting' % dst_key
        i += 1
        per = 100*(float(i)/no_files)
        print 'Done renaming %d/%d\n%f%% complete' % (i, no_files, per)


# Delete s3 keys based on input list
def s3_delete(bucket, in_list):
    '''
    Method to delete files from an AWS S3 bucket that have the same
    names as those of an input list to a local directory.

    Parameters
    ----------
    bucket : boto.s3.bucket.Bucket instance
        an instance of the boto S3 bucket class to download from
    in_list : list (str)
        a list of relative paths of the files to delete from the bucket

    Returns
    -------
    None
        The function doesn't return any value, it deletes data from
        S3 and prints its progress and a 'done' message upon completion
    '''

    # Init variables
    no_files = len(in_list)
    i = 0
    # Iterate over list and delete S3 items
    for f in in_list:
        i += 1
        try:
            print 'attempting to delete %s from %s...' % (f, bucket.name)
            k = bucket.get_key(f)
            k.delete()
            per = 100*(float(i)/no_files)
            print 'Done deleting %d/%d\n%f%% complete' % (i, no_files, per)
        except AttributeError:
            print 'No key found for %s on bucket %s' % (f, bucket.name)

        # Done iterating through list
        print 'done!'


# Download files from AWS S3 to local machine
def s3_download(bucket, in_list, local_prefix, bucket_prefix=''):
    '''
    Method to download files from an AWS S3 bucket that have the same
    names as those of an input list to a local directory.

    Parameters
    ----------
    bucket : boto.s3.bucket.Bucket instance
        an instance of the boto S3 bucket class to download from
    in_list : list (str)
        a list of relative paths of the files to download from the bucket
    local_prefix : string
        local directory prefix to store the downloaded data
    bucket_prefix : string (optional)
        bucket_prefix, if specified, will be substituted with
        local_prefix; otherwise, the local_prefix will only prepend the
        downloaded files

    Returns
    -------
    None
        The function doesn't return any value, it downloads data from
        S3 and prints its progress and a 'done' message upon completion
    '''

    # Impor packages
    import os

    # Init variables
    no_files = len(in_list)
    i = 0
    # Check for trailing '/'
    if not local_prefix.endswith('/'):
        local_prefix = local_prefix + '/'
    if bucket_prefix and not bucket_prefix.endswith('/'):
        bucket_prefix = bucket_prefix + '/'
    # For each item in the list, try to download it
    for f in in_list:
        i += 1
        remote_filename = bucket.name + ': ' + f
        if bucket_prefix:
            local_filename = f.replace(bucket_prefix, local_prefix)
        else:
            local_filename = os.path.join(local_prefix, f)
        # Check to see if the local folder setup exists or not
        local_folders = os.path.dirname(local_filename)
        if not os.path.isdir(local_folders):
            print 'creating %s on local machine' % local_folders
            os.makedirs(local_folders)
        # Attempt to download the file
        print 'attempting to download %s to %s...' % (remote_filename,
                                                      local_filename)
        try:
            if not os.path.exists(local_filename):
                k = bucket.get_key(f)
                k.get_contents_to_filename(local_filename)
                per = 100*(float(i)/no_files)
                print 'Done downloading %d/%d\n%f%% complete' % (i, no_files, per)
            else:
                print 'File %s already exists, skipping...' % local_filename
        except AttributeError:
            print 'No key found for %s on bucket %s' % (f, bucket.name)

    # Done iterating through list
    print 'done!'


# Upload files to AWS S3
def s3_upload(bucket, src_list, dst_list, make_public=False, overwrite=False):
    '''
    Function to upload a list of data to an S3 bucket

    Parameters
    ----------
    bucket : boto.s3.bucket.Bucket instance
        an instance of the boto S3 bucket class to download from
    src_list : list (str)
        list of filepaths as strings to upload to S3
    dst_list : list (str)
        list of filepaths as strings coinciding with src_list, such
        that src_list[1] gets uploaded to S3 with the S3 path given in
        dst_list[1]
    make_public : boolean (optional), default=False
        set to True if files should be publically available on S3
    overwrite : boolean (optional), default=False
        set to True if the uploaded files should overwrite what is
        already there

    Returns
    -------
    None
        The function doesn't return any value, it uploads data to S3
        and prints its progress and a 'done' message upon completion
    '''

    # Callback function for upload progress update
    def callback(complete, total):
        '''
        Method to illustrate file uploading and progress updates
        '''

        # Import packages
        import sys

        # Write ...'s to the output for loading progress
        sys.stdout.write('.')
        sys.stdout.flush()

    # Init variables
    no_files = len(src_list)
    i = 0

    # Check if the list lengths match 
    if no_files != len(dst_list):
        raise RuntimeError, 'src_list and dst_list must be the same length!'

    # For each source file, upload
    for src_file in src_list:
        # Get destination path
        dst_file = dst_list[i]
        # Print status
        print 'Uploading %s to S3 bucket %s as %s' % \
        (src_file, bucket.name, dst_file)

        # Create a new key from the bucket and set its contents
        k = bucket.new_key(dst_file)
        if k.exists() and not overwrite:
            print 'key %s already exists, skipping...' % dst_file
        else:
            k.set_contents_from_filename(src_file, cb=callback, replace=True)
        # Make file public if set to True
        if make_public:
            print 'make public()'
            k.make_public()
        i += 1
        per = 100*(float(i)/no_files)
        print 'finished file %d/%d\n%f%% complete\n' % \
        (i, no_files, per)

    # Print when finished
    print 'Done!'


# Print status of file progression in loop
def print_loop_status(itr, full_len):
    '''
    Function to print the current percentage completed of a loop
    Parameters
    ----------
    itr : integer
        the current iteration of the loop
    full_len : integer
        the full length of the loop
    Returns
    -------
    None
        the function prints the loop status, but doesn't return a value
    '''

    # Print the percentage complete
    per = 100*(float(itr)/full_len)
    print '%d/%d\n%f%% complete' % (itr, full_len, per)
