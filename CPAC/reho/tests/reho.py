import os
from tempfile import mkdtemp
from shutil import rmtree
import numpy as np
from nibabel import Nifti1Image
import nibabel as nb
from nose.tools import *

from CPAC.reho import create_reho_wf
 
@raises(ValueError)
def test_cluster_size_raise_exception():
    #cluster size has to be in [7, 19, 27]
    #raise value error if user pass wrong value

    tempdir = mkdtemp()
    filename1 = os.path.join(tempdir, 'func.nii')
    f = Nifti1Image(np.random.rand(10, 10, 10, 200), np.eye(4)).to_filename(filename1)

    wf = create_reho_wf(cluster_size=1)
    wf.inputs.inputspec.in_file = f
    wf.run()

    rmtree(tempdir)

def test_cluster_size():
    #does not raise exception if cluster size is accepted value

    tempdir = mkdtemp()
    filename1 = os.path.join(tempdir, 'func.nii')
    Nifti1Image(np.random.rand(10, 10, 10, 200), np.eye(4)).to_filename(filename1)

    wf = create_reho_wf()
    wf.inputs.inputspec.in_file = filename1
    wf.inputs.inputspec.cluster_size = 27
    wf.run()
    assert True

    rmtree(tempdir)


def test_output_is_nii():
    #test if output exist after running the wf
    #and is nifti file

    tempdir = mkdtemp()
    filename1 = os.path.join(tempdir, 'func.nii')
    Nifti1Image(np.random.rand(10, 10, 10, 200), np.eye(4)).to_filename(filename1)

    wf = create_reho_wf()
    wf.inputs.inputspec.in_file = filename1
    wf.inputs.inputspec.cluster_size = 7
    res = wf.run()
    assert os.path.isfile(os.path.join(res.nodes()[0].base_dir, 'reho_wf/reho/reho.nii.gz'))

    rmtree(tempdir)


def test_output_shape():
    #test if the output file has the same shape as the input file
    #but is 3d instead of 4d
    tempdir = mkdtemp()
    filename1 = os.path.join(tempdir, 'func.nii')
    Nifti1Image(np.random.rand(10, 10, 10, 200), np.eye(4)).to_filename(filename1)

    after = nb.load(filename1).shape

    wf = create_reho_wf()
    wf.inputs.inputspec.in_file = filename1
    wf.inputs.inputspec.cluster_size = 7
    res = wf.run()

    out = os.path.join(res.nodes()[0].base_dir, 'reho_wf/reho/reho.nii.gz')
    before = nb.load(out).shape

    #file still has the same shape
    assert after[:3] == before[:3]

    #and it is a 3d file
    assert len(before) == 3

    rmtree(tempdir)
