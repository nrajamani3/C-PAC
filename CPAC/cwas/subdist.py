import numpy as np

# TODO:
# - less transposes when computing the distances?
# - better approach to fix autocorrelation issue

#def cpac_corrcoef(X, memory_limit):
#    """
#    Returns Pearson correlation coeffiecients
#    
#    Parameters
#    ----------
#    X : ndarray
#        Each column represents a variable while each row represents an 
#        observation.
#    
#    Returns
#    -------
#    out : ndarray
#        The correlation coefficient matrix of the variables.
#    
#    See Also
#    --------
#    numpy.corrcoef
#    
#    Examples
#    --------
#    >>> import numpy as np
#    >>> from CPAC.cwas.subdist import cpac_corrcoef
#    >>> 
#    >>> ntpts = 100; nvoxs = 200
#    >>> dat         = np.random.random((ntpts, nvoxs))
#    >>> cpac_res    = cpac_corrcoef(dat)
#    >>> numpy_res   = np.corrcoef(dat.T)
#    >>> np.allclose(cpac_res, numpy_res)
#    True
#    """
#    ntpts = X.shape[0]
#    nvoxs = X.shape[1]
#    
#    block_size = calc_blocksize(X, memory_limit)
#    
#    if vox_inds is None:
#        vox_inds = range(X.shape[1])
#    X_norm = norm_cols(X)
#    return ncor(X_norm, vox_inds)


def norm_cols(X):
    """
    Normalize columns of your matrix.
    
    Takes an input matrix likely to be time-points by voxels and normalizes 
    the columns (ie each voxel's timeseries). This involves subtracting the 
    mean from each column and then dividing it by the standard deviation.
    
    Parameters
    ----------
    X : ndarray
        Each column represents a variable while each row represents an 
        observation.
    
    Returns
    -------
    Xn : ndarray
        Matrix normalized by columns
    
    Examples
    --------    
    >>> import numpy as np
    >>> from CPAC.cwas.subdist import norm_cols
    >>> 
    >>> ntpts = 100; nvoxs = 200
    >>> dat         = np.random.random((ntpts, nvoxs))
    >>> dat_norm    = norm_cols(dat)    
    """
    Xc = X - X.mean(0)
    return Xc/np.sqrt( (Xc**2.).sum(0) )


def norm_subjects(subjects_data):
    """
    Normalize columns for each matrix in a list.
    
    Loops through each subject in `subjects_data` and calls on `norm_cols`.
    
    Parameters
    ----------
    subjects_data : list of ndarray
    
    Returns
    -------
    subjects_normed_data : list of ndarray
        List of normalized matrices
    
    Examples
    --------
    >>> import numpy as np
    >>> from CPAC.cwas.subdist import norm_subjects
    >>> 
    >>> nsubs = 10; ntpts = 100; nvoxs = 200
    >>> dat         = [ np.random.random((ntpts, nvoxs)) for i in xrange(nsubs) ]
    >>> dat_norm    = norm_subjects(dat)
    """
    nSubjects = len(subjects_data)
    subjects_data_n = [None] * nSubjects
    for i in range(nSubjects):
        subjects_data_n[i] = norm_cols(subjects_data[i])
    return subjects_data_n


# add a possible 2nd column?
def ncor(normed_data, vox_inds):
    """
    Cross product between a set of columns and the whole matrix.
    
    Typically used to get the correlation between elements in data. To do this, 
    the norm of each column is taken and then the output of that step is used 
    to call this function.
    
    Parameters
    ----------
    normed_data : ndarray
        Can really be any matrix but typically is the output of `norm_cols`.
    vox_inds : list or ndarray
        List/vector of column indices in `normed_data` to use for the cross 
        product.
    
    Returns
    -------
    corr_data : ndarray
        If the input is a normed matrix, then the output are correlations. 
        Otherwise the output is just a cross product.
    
    Examples
    --------
    >>> import numpy as np
    >>> from CPAC.cwas.subdist import norm_cols, ncor
    >>> 
    >>> ntpts = 100; nvoxs = 200
    >>> dat         = np.random.random((ntpts, nvoxs))
    >>> dat_norm    = norm_cols(dat)
    >>> corr_data   = ncor(dat_norm, range(20)) # only get correlations for some voxels
    >>> corr_data.shape
    (20, 200)
    >>> np.allclose(corr_data, np.corrcoef(dat.T))
    True
    """
    #if type(vox_inds) != list or type(vox_inds) != tuple:
    #    vox_inds = [vox_inds]
    return normed_data[:,vox_inds].T.dot(normed_data)


def ncor_subjects(subjects_normed_data, vox_inds):
    """
    For a list of matrices, computes the cross product for each matrix.
    
    For each element of the list, this calls on `ncor` to calculate the cross
    product between a set of columns and the whole matrix. Typically the input
    is a list of normed matrices but this isn't necessary. When the input is a 
    list of normed matrices, then the output are correlation values.
    
    Parameters
    ----------
    subjects_normed_data : list of ndarray
        List of any matrices, typically is the output of `norm_subjects`.
    vox_inds : list or ndarray
        List/vector of column indices in `subjects_normed_data` to use for the cross 
        product.
    
    Returns
    -------
    subjects_corr_data : list of ndarray
        List of matrices from cross products. If input was a normalized matrix, 
        then this reflects correlation values.
    
    Examples
    --------
    >>> import numpy as np
    >>> from CPAC.cwas.subdist import norm_subjects, ncor_subjects
    >>> 
    >>> nsubs = 10; ntpts = 100; nvoxs = 200
    >>> dat         = [ np.random.random((ntpts, nvoxs)) for i in xrange(nsubs) ]
    >>> dat_norm    = norm_subjects(dat)
    >>> corr_data   = ncor_subjects(dat_norm, range(20)) # get correlations for some voxels
    >>> corr_data.shape
    (10, 20, 200)
    """
    nSubjects = len(subjects_normed_data)
    nVoxels   = subjects_normed_data[0].shape[1]
    nSeeds    = len(vox_inds)
    
    S         = np.zeros((nSubjects, nSeeds, nVoxels))
    for i in range(nSubjects):
        S[i] = ncor(subjects_normed_data[i], vox_inds)
    
    ## Prevent infinity for Fischer's Tranfrom of autocorrelation (1s)
    #for j in range(nSeeds):
    #    S[:,j,vox_inds[j]] = S[:,j,vox_inds[j]] - 1e-9
    
    return S


def replace_autocorrelations(mat, new_val=0.99):
    """
    Places a ceiling on maximum values of the matrix
    
    Values greater than `new_val` in `mat` will be set to the `new_val`.
    
    Parameters
    ----------
    mat : ndarray
    new_val : float
        Maximum value to set as the ceiling for the input matrix.
    
    Returns
    -------
    mat_ceil : ndarray
    
    Examples
    --------
    >>> import numpy as np
    >>> from CPAC.cwas.subdist import replace_autocorrelations
    >>> 
    >>> corr_dat    = np.corrcoef(np.random.random((10,100)))
    >>> replace_autocorrelations(corr_dat)    
    """
    mat[mat > new_val] = new_val
    return mat


def fischers_transform(S):
    """
    Fischer's Z transform (just the arctanh of the input matrix)
    """
    return np.arctanh(S)


def compute_distances(Smaps):
    """
    Computes the distance between subject connectivity maps.
    
    For now the function uses a Pearson distance measure: `sqrt(2 * (1 - r))`.
    
    Parameters
    ----------
    Smaps : ndarray
        A matrix where the rows = voxels and columns = subjects.
    
    Returns
    -------
    dmat : ndarray
        A matrix that is subjects x subjects representing the distance between
        each pair of subject connectivity maps.
    
    Examples
    --------
    >>> import numpy as np
    >>> from CPAC.cwas.subdist import compute_distances
    >>> 
    >>> Smaps    = np.random.random((100,10)) # 100 voxs x 10 subs
    >>> dmat0    = compute_distances(Smaps)
    >>> dmat1    = np.sqrt(2. * (1. - np.corrcoef(Smaps.T)))
    >>> np.allclose(dmat0, dmat1)
    """
    Smaps   = norm_cols(Smaps)
    Scorrs  = Smaps.T.dot(Smaps)
    np.fill_diagonal(Scorrs, 1.0)
    dmat    = np.sqrt(2.0 * (1.0 - Scorrs))
    return dmat
