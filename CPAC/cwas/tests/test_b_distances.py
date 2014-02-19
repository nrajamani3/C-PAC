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


class TestDistances:
    @attr('cwas', 'distances', 'simulation')
    def test_computing_distances_on_simulated_data(self, nsubs=20, ntpts=100, nvoxs=200):
        """
        Test for `compute_distances` on simulated data.
        """
        from CPAC.cwas.subdist import norm_subjects, ncor_subjects, \
                                      replace_autocorrelations, \
                                      fischers_transform, \
                                      compute_distances
        
        dat         = [ np.random.random((ntpts, nvoxs)) for i in xrange(nsubs) ]
        
        dat_norm    = norm_subjects(dat)
        corr_data   = ncor_subjects(dat_norm, range(nvoxs))
        corr_data   = replace_autocorrelations(corr_data)
        corr_data   = fischers_transform(corr_data)
        
        for i in xrange(nvoxs):
            ref_sim     = np.corrcoef(corr_data[:,i,:])
            ref         = np.sqrt(2. * (1. - ref_sim))
            comp        = compute_distances(corr_data[:,i,:].T)
            
            assert_allclose(ref, comp)
    
    @attr('cwas', 'distances', 'simulation', 'r')
    def test_computing_distances_on_simulated_data_against_r(self, nsubs=20, nvoxs=200):
        from CPAC.cwas.subdist import compute_distances
        from rpy2_header import *
        base        = importr('base')
        bigmemory   = importr('bigmemory')
        connectir   = importr('connectir')

        seedMaps_np = np.random.random((nvoxs, nsubs))

        seedMaps_r  = base.as_matrix(seedMaps_np)
        seedMaps    = bigmemory.as_big_matrix(seedMaps_r)
        dmats       = bigmemory.big_matrix(nsubs**2, nvoxs, init=0)
        ref         = np.array(connectir.test_sdist(seedMaps, dmats, 1)).reshape(nsubs,nsubs)
        
        comp = compute_distances(seedMaps_np)

        assert_allclose(ref, comp)
        
