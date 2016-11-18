import os
from tempfile import mkdtemp
from shutil import rmtree
import numpy as np
from nibabel import Nifti1Image
import nibabel as nb
from CPAC import alff

def test_alff():
    tempdir = mkdtemp()
    filename1 = os.path.join(tempdir, 'func.nii')
    f = Nifti1Image(np.random.rand(10, 10, 10, 50), np.eye(4)).to_filename(filename1)

    filename2 = os.path.join(tempdir, 'mask.nii')
    f2 = Nifti1Image(np.ones((10, 10, 10)), np.eye(4)).to_filename(filename2)

    wf = alff.create_alff_wf('alff', [0.1], [0.8])
    wf.inputs.inputspec.in_file = filename1
    wf.inputs.inputspec.mask = filename2
    res = wf.run()
    rmtree(tempdir)
    assert True


def test_iterable():
    tempdir = mkdtemp()
    filename1 = os.path.join(tempdir, 'func.nii')
    f = Nifti1Image(np.random.rand(10, 10, 10, 50), np.eye(4)).to_filename(filename1)

    filename2 = os.path.join(tempdir, 'mask.nii')
    f2 = Nifti1Image(np.ones((10, 10, 10)), np.eye(4)).to_filename(filename2)

    wf = alff.create_alff_wf('alff', [0.1, 0.2, 0.3], [0.5, 0.6, 0.7])
    wf.inputs.inputspec.in_file = filename1
    wf.inputs.inputspec.mask = filename2
    res = wf.run()
    rmtree(tempdir)
    assert True