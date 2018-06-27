from nipype.interfaces import afni 
from nipype.interfaces import fsl
import nipype.pipeline.engine as pe
import nipype.interfaces.utility as util


def create_aroma(wf_name='create_aroma'):
	preproc = pe.Workflow(name=wf_name)

	inputNode = pe.Node(util.IdentityInterface(fields=['denoise_file','motion_parameters']),name='inputspec')

	inputNode_GuiOpts = pe.Node(util.IdentityInterface(fields=['feat_dir','denoise_type','TR','dim','environ','fnirt_warp_file','mask','mat_file','melodic_dir']),name='GuiOpts')

	outputNode = pe.Node(util.IdentityInterface(fields=['out_dir']),name = 'outputspec')


	try:
		from nipype.interfaces.fsl import ICA_AROMA
		aroma_wf = pe.Node(interface=fsl.ICA_AROMA(),name='aroma_wf')
	except ImportError:
		from nipype.interfaces.fsl import ICA_AROMA
		aroma_wf = pe.Node(interface=fsl.ICA_AROMA(),name='aroma_wf')

	preproc.connect(inputNode,'denoise_file',aroma_wf,'in_file')
	preproc.connect(inputNode,'motion_parameters',aroma_wf,'motion_parameters')
	
	preproc.connect(inputNode_GuiOpts,'feat_dir',aroma_wf,'feat_dir')
	preproc.connect(inputNode_GuiOpts,'denoise_type',aroma_Wf,'denoise_type')
	preproc.connect(inputNode_GuiOpts,'TR',aroma_wf,'TR')
	preproc.connect(inputNode_GuiOpts,'dim',aroma_wf,'dim')
	preproc.connect(inputNode_GuiOpts,'environ',aroma_wf,'environ')
	preproc.connect(inputNode_GuiOpts,'fnirt_warp_file',aroma_wf,'fnirt_warp_file')
	preproc.connect(inputNode_GuiOpts,'mask',aroma_wf,'mask')
	preproc.connect(inputNode_GuiOpts,'mat_file',aroma_wf,'mat_file')
	preproc.connect(inputNode_GuiOpts,'melodic_dir',aroma_wf,'melodic_dir')
	preproc.connect(aroma_wf,'out_dir',outputNode,'out_dir')



