import os
from tempfile import mkdtemp
from shutil import rmtree
import numpy as np
from nibabel import Nifti1Image
import nibabel as nb
import nipype.pipeline.engine as pe
from CPAC import alff

def test_falff():
    tempdir = mkdtemp()
    filename1 = os.path.join(tempdir, 'func.nii')
    f = Nifti1Image(np.random.rand(10, 10, 10, 50), np.eye(4)).to_filename(filename1)

    filename2 = os.path.join(tempdir, 'mask.nii')
    f2 = Nifti1Image(np.ones((10, 10, 10)), np.eye(4)).to_filename(filename2)

    wf = alff.create_falff_wf('falff')
    wf.inputs.inputspec.in_file = filename1
    wf.inputs.inputspec.mask = filename2
    wf.inputs.inputspec.alff = filename1
    res = wf.run()
    rmtree(tempdir)
    assert True

def test_alff_falff_together():
    tempdir = mkdtemp()
    filename1 = os.path.join(tempdir, 'func.nii')
    f = Nifti1Image(np.random.rand(10, 10, 10, 50), np.eye(4)).to_filename(filename1)

    filename2 = os.path.join(tempdir, 'mask.nii')
    f2 = Nifti1Image(np.ones((10, 10, 10)), np.eye(4)).to_filename(filename2)

    wf1 = alff.create_alff_wf('alff', [0.01], [0.1])
    wf1.inputs.inputspec.in_file = filename1
    wf1.inputs.inputspec.mask = filename2

    wf2 = alff.create_falff_wf('falff')
    wf2.inputs.inputspec.in_file = filename1
    wf2.inputs.inputspec.mask = filename2
    wf2.inputs.inputspec.alff = filename1

    wf = pe.Workflow(name='alff_falff')
    wf.connect(wf1, 'outputspec.alff_img', wf2, 'inputspec.alff')
    wf.run()
    rmtree(tempdir)
    assert True

