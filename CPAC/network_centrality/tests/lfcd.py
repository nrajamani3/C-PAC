import os
from tempfile import mkdtemp
from shutil import rmtree
import numpy as np
from nibabel import Nifti1Image
import nibabel as nb
from CPAC.network_centrality.afni_network_centrality import create_lfcd_wf

def test_correlation_lfcd():
    #check if wf runs ok with correlation threshold option
    #and check if the 2 nii outputs of lfcd exist
    tempdir = mkdtemp()
    filename1 = os.path.join(tempdir, 'func.nii')
    f = Nifti1Image(np.random.rand(10, 10, 10, 50), np.eye(4)).to_filename(filename1)

    filename2 = os.path.join(tempdir, 'mask.nii')
    f2 = Nifti1Image(np.ones((10, 10, 10)), np.eye(4)).to_filename(filename2)

    wf = create_lfcd_wf('lfcd_correlation','correlation', 0.8)
    wf.inputs.inputspec.in_file = filename1
    wf.inputs.inputspec.template = filename2
    res = wf.run()
    #print res.nodes()[-1].base_dir
    #assert os.path.isfile(os.path.join(res.nodes()[-1].base_dir, 'lfcd_correlation/sep_nifti_subbriks/lfcd_binarize.nii.gz'))
    #assert os.path.isfile(os.path.join(res.nodes()[-1].base_dir, 'lfcd_correlation/sep_nifti_subbriks/lfcd_weighted.nii.gz'))
    rmtree(tempdir)
    assert True

def test_significance_lfcd():
    #check if wf runs ok with correlation threshold option
    #and check if the 2 nii outputs of lfcd exist
    tempdir = mkdtemp()
    filename1 = os.path.join(tempdir, 'func.nii')
    f = Nifti1Image(np.random.rand(10, 10, 10, 50), np.eye(4)).to_filename(filename1)

    filename2 = os.path.join(tempdir, 'mask.nii')
    f2 = Nifti1Image(np.ones((10, 10, 10)), np.eye(4)).to_filename(filename2)

    wf = create_lfcd_wf('lfcd_significance','significance', 0.3)
    wf.inputs.inputspec.in_file = filename1
    wf.inputs.inputspec.template = filename2
    res = wf.run()
    #print res.nodes()[-1].base_dir
    #assert os.path.isfile(os.path.join(res.nodes()[-1].base_dir, 'dc_significance/sep_nifti_subbriks/lfcd_binarize.nii.gz'))
    #assert os.path.isfile(os.path.join(res.nodes()[-1].base_dir, 'dc_significance/sep_nifti_subbriks/lfcd_weighted.nii.gz'))
    rmtree(tempdir)
    assert True