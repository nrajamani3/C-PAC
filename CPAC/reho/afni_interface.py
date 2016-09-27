import os
from nipype.interfaces.afni.base import (AFNICommand, AFNICommandInputSpec,
                                         AFNICommandOutputSpec)
from nipype.interfaces.base import (traits, File)




class RehoInputSpec(AFNICommandInputSpec):
    """Input spec class for 3dReHo command
    """

    in_file = File(desc="input data", argstr="-inset %s", exists=True)

    #out_file = File(desc="output file name", argstr="-prefix %s_reho.nii.gz")

    mask = File(desc='mask file to mask input data', argstr="-mask %s",
                                            exists=True)

    cluster_size = traits.Int(desc='Cluster size. Must be 7, 19 our 27', argstr='-nneigh %d')



class RehoOutputSpec(AFNICommandOutputSpec):
    """Reho outputspec
    """

    out_file = File(desc='3d nii file with reho')



class RehoCommand(AFNICommand):
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
    '3dReHo -nneigh 19 -inset func_preproc.nii -mask mask.nii -prefix out.nii'
    >>> res = reho.run() # doctest: +SKIP
    """

    _cmd = '3dReHo'
    input_spec = RehoInputSpec
    output_spec = AFNICommandOutputSpec

    # Re-define generated inputs
    #def _list_outputs(self):
    #    outputs = self.output_spec().get()
    #    outputs["out_file"] = os.path.abspath(self.inputs.out_file)
    #    return outputs

   # def aggregate_outputs(self, runtime=None, needed_outputs=None):
   #     outputs = self._outputs()
   #     outputs.out_file = self.inputs.out_file
   #     return outputs
