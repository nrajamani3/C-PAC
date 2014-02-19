#!/usr/bin/env python

import os, sys
from os import path as op
import numpy as np
import nibabel as nib

from numpy.testing import *
from nose.tools import ok_, eq_, raises, with_setup
from nose.plugins.attrib import attr    # http://nose.readthedocs.org/en/latest/plugins/attrib.html

import sys
sys.path.insert(1, "/Users/zarrar/Code/C-PAC")

#import sys
#sys.path.insert(0, '/home2/data/Projects/CPAC_Regression_Test/nipype-installs/fcp-indi-nipype/running-install/lib/python2.7/site-packages')
#sys.path.insert(1, "/home2/data/Projects/CPAC_Regression_Test/2013-05-30_cwas/C-PAC")
#sys.path.append("/home/data/PublicProgram/epd-7.2-2-rh5-x86_64/lib/python2.7/site-packages")

class TestNormalize:
    @attr('cwas', 'transformation', 'normalize', 'stimulation')
    def test_normalize_on_simulated_single_subject(self, nrows=200, ncols=100):
        """
        Test for `norm_cols` on simulated data
        """
        
        from CPAC.cwas.subdist import norm_cols
        from scipy.stats.mstats import zscore
        
        seedMaps    = np.random.random((nrows, ncols))

        ref         = zscore(seedMaps)/np.sqrt(nrows)
        comp        = norm_cols(seedMaps)
        
        assert_allclose(ref, comp)
    
    @attr('cwas', 'transformation', 'normalize', 'stimulation', 'r')
    def test_normalize_on_simulated_single_subject_against_r(self, nrows=200, ncols=200):
        """
        Test for `norm_cols` on simulated data against version in R
        """
        
        from CPAC.cwas.subdist import norm_cols
        from rpy2_header import *
        
        base        = importr('base')
        bigmemory   = importr('bigmemory')
        connectir   = importr('connectir')
        bigextensions  = importr('bigextensions')

        seedMaps_np = np.random.random((nrows, ncols))
        seedMaps_r  = base.as_matrix(seedMaps_np)
        seedMaps_b  = bigmemory.as_big_matrix(seedMaps_r)

        ref         = bigextensions.scale_fast(seedMaps_b, True)
        ref         = np.array(bigmemory.as_matrix(ref)) / np.sqrt(nrows-1)
        comp        = norm_cols(seedMaps_np)

        assert_allclose(ref, comp)
        

class TestConnectivity:
    @attr('cwas', 'connectivity', 'simulation')
    def test_correlations_on_simulated_single_subject(self, ntpts=100, nvoxs=200):
        """
        Test for `ncor` on simulated data.
        """
        from CPAC.cwas.subdist import norm_cols, ncor
        
        dat         = np.random.random((ntpts, nvoxs))
        dat_norm    = norm_cols(dat)
    
        ref         = np.corrcoef(dat.T)
        comp        = ncor(dat_norm, range(nvoxs))
    
        assert_allclose(ref, comp)

    
    @attr('cwas', 'connectivity', 'real', 'single-subject')
    def test_correlations_on_real_single_subject(self, sfile=None, mfile=None, sample_nvoxs=500):
        """
        Test for `ncor` on real data.
        """
        import random
        from CPAC.cwas.subdist import norm_cols, ncor
        from CPAC.cwas.tests.utils import path_to_data
        
        if sfile is None:
            sfile = path_to_data("functional_mni_4mm.nii.gz")
        if mfile is None:
            mfile = path_to_data("mask_gray_4mm.nii.gz")
    
        dat         = nib.load(sfile).get_data().astype('float64')
        mask        = nib.load(mfile).get_data().astype('bool')
        
        # Only use a subsample of voxels for testing
        subset_inds = np.array(random.sample(range(mask.sum()), sample_nvoxs))
        mask_inds   = tuple([ inds[subset_inds] for inds in np.where(mask) ])
        
        # Constrain voxels to those found in the subset of the mask
        # then norm the columns
        dat         = dat[mask_inds].T    
        dat_norm    = norm_cols(dat)
        
        ref         = np.corrcoef(dat.T)
        comp        = ncor(dat_norm, range(sample_nvoxs))
        
        assert_allclose(ref, comp)
    
    
    @attr('cwas', 'connectivity', 'simulation', 'multiple-subjects')
    def test_correlations_on_simulated_multiple_subjects(self, ntpts=100, nvoxs=200, nsubs=4):
        """
        Test for `ncor_subjects` on simulated data.
        """
        from CPAC.cwas.subdist import norm_subjects, ncor_subjects
        
        dat         = [ np.random.random((ntpts, nvoxs)) for i in xrange(nsubs) ]
        dat_norm    = norm_subjects(dat)
        
        ref         = [ np.corrcoef(sdat.T) for sdat in dat ]
        comp        = ncor_subjects(dat_norm, range(nvoxs))
    
        assert_allclose(ref, comp)

    
    @attr('cwas', 'connectivity', 'real', 'multiple-subjects')
    def test_correlations_on_real_multiple_subjects(self, sfile=None, mfile=None, sample_nvoxs=500, nsubs=4):
        """
        Test for `ncor_subjects` on real data.
        """
        import random
        from CPAC.cwas.subdist import norm_subjects, ncor_subjects
        from CPAC.cwas.tests.utils import path_to_data
        
        if sfile is None:
            sfile = path_to_data("functional_mni_4mm.nii.gz")
        if mfile is None:
            mfile = path_to_data("mask_gray_4mm.nii.gz")
    
        dat             = nib.load(sfile).get_data().astype('float64')
        mask            = nib.load(mfile).get_data().astype('bool')
        
        # Only use a subsample of voxels for testing
        subset_inds     = np.array(random.sample(range(mask.sum()), sample_nvoxs))
        mask_inds       = tuple([ inds[subset_inds] for inds in np.where(mask) ])
        
        # Each subject is just a duplicate for simplicity
        # only use select voxels in mask
        subjects_data   = [ dat[mask_inds].T for i in xrange(nsubs) ]
        
        # Norm the subject's functional data time-series
        subjects_normed = norm_subjects(subjects_data)
        
        ref             = [ np.corrcoef(dat.T) for dat in subjects_data ]
        comp            = ncor_subjects(subjects_normed, range(sample_nvoxs))
        
        assert_allclose(ref, comp)


class TestConnectivityTransformation():
    @attr('cwas', 'connectivity', 'transformation', 'simulation')
    def test_set_ceiling_for_matrix_values(self, ntpts=100, nvoxs=200):
        """
        Test `replace_autocorrelations` on simulated data.
        (This could fail due to correlations randomly being >0.99.)
        """
        from CPAC.cwas.subdist import replace_autocorrelations
        
        dat         = np.random.random((ntpts, nvoxs))
        corr_dat    = np.corrcoef(dat.T)
        
        ref         = corr_dat.copy()
        np.fill_diagonal(ref, 0.99)
        
        comp        = corr_dat.copy()
        replace_autocorrelations(comp)
            
        assert_allclose(ref, comp)
    
    @attr('cwas', 'connectivity', 'transformation', 'simulation')
    def test_fischer_z_transfer(self, nvoxs=200):
        """
        Test `fischers_transform` on simulated data.
        """
        from CPAC.cwas.subdist import fischers_transform
        
        dat         = np.random.random((nvoxs, nvoxs))
        
        ref         = 0.5 * np.log((1.+dat)/(1.-dat)) # = arctanh(dat)
        comp        = fischers_transform(dat)
                    
        assert_allclose(ref, comp)
