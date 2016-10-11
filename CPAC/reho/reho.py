# coding: utf-8
import os
import sys
import re
import commands
import nipype.pipeline.engine as pe
import nipype.interfaces.fsl as fsl
import nipype.interfaces.utility as util
from CPAC.reho.utils import *
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
    >>> wf = reho.create_reho_wf()
    >>> wf.inputs.inputspec.in_file = 'rest.nii.gz'
    >>> wf.inputs.inputspec.mask = 'mask.nii.gz'
    >>> wf.inputs.inputspec.cluster_size = 27
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



def create_reho():

    """
    Regional Homogeneity(ReHo) approach to fMRI data analysis

    This workflow computes the ReHo map, z-score on map

    Parameters
    ----------

    None

    Returns
    -------
    reHo : workflow
        Regional Homogeneity Workflow

    Notes
    -----

    `Source <https://github.com/FCP-INDI/C-PAC/blob/master/CPAC/reho/reho.py>`_

    Workflow Inputs: ::

        inputspec.rest_res_filt : string (existing nifti file)
            Input EPI 4D Volume

        inputspec.rest_mask : string (existing nifti file)
            Input Whole Brain Mask of EPI 4D Volume

        inputspec.cluster_size : integer
            For a brain voxel the number of neighbouring brain voxels to use for KCC.
            Possible values are 27, 19, 7. Recommended value 27


    Workflow Outputs: ::

        outputspec.raw_reho_map : string (nifti file)

        outputspec.z_score : string (nifti file)


    ReHo Workflow Procedure:

    1. Generate ReHo map from the input EPI 4D volume, EPI mask and cluster_size
    2. Compute Z score of the ReHo map by subtracting mean and dividing by standard deviation


    Workflow Graph:

    .. image:: ../images/reho.dot.png
        :width: 500

    Detailed Workflow Graph:

    .. image:: ../images/reho_detailed.dot.png
        :width: 500
        
    References
    ---------- 
    .. [1] Zang, Y., Jiang, T., Lu, Y., He, Y.,  Tian, L. (2004). Regional homogeneity approach to fMRI data analysis. NeuroImage, 22(1), 394, 400. doi:10.1016/j.neuroimage.2003.12.030

    Examples
    --------
    >>> from CPAC import reho
    >>> wf = reho.create_reho()
    >>> wf.inputs.inputspec.rest_res_filt = '/home/data/Project/subject/func/rest_res_filt.nii.gz'
    >>> wf.inputs.inputspec.rest_mask = '/home/data/Project/subject/func/rest_mask.nii.gz'
    >>> wf.inputs.inputspec.cluster_size = 27
    >>> wf.run()
    """




    reHo = pe.Workflow(name='reHo')
    inputNode = pe.Node(util.IdentityInterface(fields=[
                                                'cluster_size',
                                                'rest_res_filt',
                                                'rest_mask'
                                                ]),
                        name='inputspec')


    outputNode = pe.Node(util.IdentityInterface(fields=[
                                                    'raw_reho_map']),
                                                    #'z_score']),
                        name='outputspec')


    raw_reho_map = pe.Node(util.Function(input_names=['in_file', 'mask_file', 'cluster_size'],
                                   output_names=['out_file'],
                     function=compute_reho),
                     name='reho_map')


    reHo.connect(inputNode, 'rest_res_filt',
                    raw_reho_map, 'in_file')
    reHo.connect(inputNode, 'rest_mask',
                    raw_reho_map, 'mask_file')
    reHo.connect(inputNode, 'cluster_size',
                    raw_reho_map, 'cluster_size')

    reHo.connect(raw_reho_map, 'out_file',
                 outputNode, 'raw_reho_map')



    return reHo


