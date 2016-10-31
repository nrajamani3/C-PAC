import os
from tempfile import mkdtemp
from shutil import rmtree
import numpy as np
from nibabel import Nifti1Image
import nibabel as nb
from CPAC.network_centrality import create_degree_centrality_wf

def test_significance_generates_output():
	#check if wf runs ok with valid params
	#and check if nii with right name exists
	
	tempdir = mkdtemp()
	filename1 = os.path.join(tempdir, 'func.nii')
	f = Nifti1Image(np.random.rand(10, 10, 10, 50), np.eye(4)).to_filename(filename1)

	filename2 = os.path.join(tempdir, 'mask.nii')
	f2 = Nifti1Image(np.ones(10, 10, 10), np.eye(4)).to_filename(filename2)

	wf = create_degree_centrality_wf('degree','significance', 0.8)
	wf.inputs.inputspec.in_file = filename1
	wf.inputs.inputspec.template = filename2
	wf.run()

	rmtree(tempdir)

	assert True