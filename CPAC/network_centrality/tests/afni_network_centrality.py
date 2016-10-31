import os
from tempfile import mkdtemp
from shutil import rmtree
import numpy as np
from nibabel import Nifti1Image
import nibabel as nb
from CPAC.network_centrality.afni_network_centrality import create_degree_centrality_wf

def test_correlation_generates_output():
	#check if wf runs ok with correlation threshold option
	#and check if the 2 nii outputs of degree centrality exist
	tempdir = mkdtemp()
	filename1 = os.path.join(tempdir, 'func.nii')
	f = Nifti1Image(np.random.rand(10, 10, 10, 50), np.eye(4)).to_filename(filename1)

	filename2 = os.path.join(tempdir, 'mask.nii')
	f2 = Nifti1Image(np.ones((10, 10, 10)), np.eye(4)).to_filename(filename2)

	wf = create_degree_centrality_wf('dc_correlation','correlation', 0.8)
	wf.inputs.inputspec.in_file = filename1
	wf.inputs.inputspec.template = filename2
	res = wf.run()
        
	assert os.path.isfile(os.path.join(res.nodes()[-1].base_dir, 'dc_correlation/sep_nifti_subbriks/degree_centrality_binarize.nii.gz'))
        assert os.path.isfile(os.path.join(res.nodes()[-1].base_dir, 'dc_correlation/sep_nifti_subbriks/degree_centrality_weighted.nii.gz'))

        rmtree(tempdir)

def test_sparsity_generates_output():
        #check if wf runs ok with sparsity threshold option
        #and check if the 2 nii outputs of degree centrality exist
        tempdir = mkdtemp()
        filename1 = os.path.join(tempdir, 'func.nii')
        f = Nifti1Image(np.random.rand(10, 10, 10, 50), np.eye(4)).to_filename(filename1)

        filename2 = os.path.join(tempdir, 'mask.nii')
        f2 = Nifti1Image(np.ones((10, 10, 10)), np.eye(4)).to_filename(filename2)

        wf = create_degree_centrality_wf('dc_sparsity','sparsity', 0.5)
        wf.inputs.inputspec.in_file = filename1
        wf.inputs.inputspec.template = filename2
        res = wf.run()
        
        assert os.path.isfile(os.path.join(res.nodes()[-1].base_dir, 'dc_sparsity/sep_nifti_subbriks/degree_centrality_binarize.nii.gz'))
        assert os.path.isfile(os.path.join(res.nodes()[-1].base_dir, 'dc_sparsity/sep_nifti_subbriks/degree_centrality_weighted.nii.gz'))

        rmtree(tempdir)

def test_significance_generates_output():
        #check if wf runs ok with correlation threshold option
        #and check if the 2 nii outputs of degree centrality exist
        tempdir = mkdtemp()
        filename1 = os.path.join(tempdir, 'func.nii')
        f = Nifti1Image(np.random.rand(10, 10, 10, 50), np.eye(4)).to_filename(filename1)

        filename2 = os.path.join(tempdir, 'mask.nii')
        f2 = Nifti1Image(np.ones((10, 10, 10)), np.eye(4)).to_filename(filename2)

        wf = create_degree_centrality_wf('dc_significance','significance', 0.3)
        wf.inputs.inputspec.in_file = filename1
        wf.inputs.inputspec.template = filename2
        res = wf.run()
        
        assert os.path.isfile(os.path.join(res.nodes()[-1].base_dir, 'dc_significance/sep_nifti_subbriks/degree_centrality_binarize.nii.gz'))
        assert os.path.isfile(os.path.join(res.nodes()[-1].base_dir, 'dc_significance/sep_nifti_subbriks/degree_centrality_weighted.nii.gz'))

        rmtree(tempdir)

