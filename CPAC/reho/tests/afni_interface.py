import os
from tempfile import mkdtemp
from shutil import rmtree
from nibabel import Nifti1Image
import numpy as np
from CPAC.reho import RehoCommand

#check if Reho class is generating the right afni command
def test_cmd():

    #create mock nii files
    tempdir = mkdtemp()
    filename1 = os.path.join(tempdir, 'func.nii')
    filename2 = os.path.join(tempdir, 'mask.nii')
    Nifti1Image(np.random.rand(10, 10, 10, 200), np.eye(4)).to_filename(filename1)
    Nifti1Image(np.random.rand(10, 10, 10), np.eye(4)).to_filename(filename2)
    
    reho = RehoCommand()
    reho.inputs.in_file = filename1
    reho.inputs.mask = filename2
    reho.inputs.cluster_size = 19
    reho.inputs.out_file = 'out.nii'

    cmd = reho.cmdline
    print cmd
    assert cmd == '3dReHo -nneigh 19 -inset %s -mask %s -prefix out.nii'%(filename1,filename2)
    rmtree(tempdir)
