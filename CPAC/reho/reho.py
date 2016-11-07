# coding: utf-8
import nipype.pipeline.engine as pe
from CPAC.reho.afni_interface import RehoCommand


def create_reho_wf(wf_name='reho_wf', cluster_size=27):
    '''
    Function to create the afni-based ReHo (regional homogeneity)
    workflow

    Parameters
    ----------
    wf_name : string
        the name of the workflow
    cluster_size : integer (optional); default=27
        number of neighbors to use, the value must be 7, 19 or 27

    Returns
    -------
    wf : nipype Workflow
        the initialized nipype workflow for the afni ReHo command

    Examples
    --------
    >>> from CPAC import reho
    >>> wf = reho.create_reho_wf(cluster_size=27)
    >>> wf.inputs.inputspec.in_file = 'rest.nii.gz'
    >>> wf.inputs.inputspec.mask = 'mask.nii.gz'
    >>> wf.run()
    '''

    #validate cluster size
    if cluster_size not in (7,19,27):
        raise ValueError("Cluster size must be 7, 19 or 27")

    wf = pe.Workflow(name=wf_name)

    in_node = pe.Node(util.IdentityInterface(fields=['in_file',
                                                        'mask',
                                                        'cluster_size']),
                         name='inputspec')

    in_node.inputs.cluster_size = cluster_size

    reho_node = pe.Node(RehoCommand(), name='reho')
    reho_node.inputs.out_file = 'reho.nii.gz'

    wf.connect(in_node, 'in_file', reho_node, 'in_file')
    wf.connect(in_node, 'mask', reho_node, 'mask')
    wf.connect(in_node, 'cluster_size', reho_node, 'cluster_size')

    out_node = pe.Node(util.IdentityInterface(fields=['out_file']),
                        name='outputspec')

    wf.connect(reho_node, 'out_file', out_node, 'out_file')

    return wf

