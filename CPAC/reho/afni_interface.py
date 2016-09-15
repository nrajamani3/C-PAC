from nipype.interfaces.afni.base import (AFNICommand, AFNICommandInputSpec,
                                         AFNICommandOutputSpec)
from nipype.interfaces.base import (traits, File)




class RehoInputSpec(AFNICommandInputSpec):
    """Input spec class for 3dReHo command
    """

    in_file = File(desc="input data", argstr="-inset %s", exists=True)

    prefix = File(desc="output file name", argstr="-prefix %s", exists=True)

    mask = File(desc='mask file to mask input data', argstr="-mask %s",
                                            exists=True)

    cluster_size = traits.Int(desc='Cluster size. Must be 7, 19 our 27', argstr='-nneigh %d')



class RehoOutputSpec(AFNICommandOutputSpec):
    """Reho outputspec
    """

    out_file = File(desc='3d nii file with reho')



class Reho(AFNICommand):
    """Performs reho on a 4d dataset using a given maskfile
    via 3dReHo

    For complete details, see the `3dReHo Documentation.
    <https://afni.nimh.nih.gov/pub/dist/doc/program_help/3dReHo.html>

    Examples
    ========

    >>> from nipype.interfaces import afni as afni
    >>> reho = afni.Reho()
    >>> reho.inputs.in_file = 'func_preproc.nii'
    >>> reho.inputs.mask = 'mask.nii'
    >>> reho.inputs.cluster_size = 27 #can be 7, 19 or 27
    >>> reho.inputs.out_file = 'out.nii'
    >>> reho.cmdline
    'TODO: 3dDegreeCentrality -sparsity 1 -mask mask.nii -prefix out.nii func_preproc.nii'
    >>> res = reho.run() # doctest: +SKIP
    """

    _cmd = '3dReHo'
    input_spec = RehoInputSpec
    output_spec = RehoOutputSpec

    # Re-define generated inputs
    # def _list_outputs(self):
    #     # Import packages
    #     import os

    #     # Update outputs dictionary if oned file is defined
    #     outputs = super(DegreeCentrality, self)._list_outputs()
    #     if self.inputs.oned_file:
    #         outputs['oned_file'] = os.path.abspath(self.inputs.oned_file)

    #     return outputs
