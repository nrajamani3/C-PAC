import os
import sys
import commands
import nipype.pipeline.engine as pe
import nipype.algorithms.rapidart as ra
import nipype.interfaces.fsl as fsl
import nipype.interfaces.io as nio
import nipype.interfaces.utility as util
from nipype.interfaces.afni import preprocess


def create_alff(wf_name='alff_wf'):
    pass

def get_opt_string(mask):
    """
    Method to return option string for 3dTstat
    
    Parameters
    ----------
    mask : string (file)
    
    Returns
    -------
    opt_str : string
    
    """
    return " -stdev -mask %s" %mask


def create_alff_wf(wf_name):
    """
    Calculate Amplitude of low frequency oscillations(ALFF) map

    Parameters
    ----------
    wf_name : string
        Workflow name
         
    Returns
    -------
    wf : workflow object
        ALFF workflow

    Notes
    -----
    `Source <https://github.com/FCP-INDI/C-PAC/blob/master/CPAC/alff/alff.py>`_

    Workflow Inputs::
        inputspec.in_file : string (existing nifti file)
            Nuisance signal regressed functional image
        inputspec.mask : string (existing nifti file)
            A mask volume(derived by dilating the motion corrected functional
            volume) in native space

    Workflow Outputs::
        outputspec.alff_img : string (nifti file)
            outputs image containing the sum of the amplitudes in the low
            frequency band
    
    Order of Commands:
                    
    - Calculate ALFF by taking the standard deviation of the input file
     (slice-time, motion corrected and nuisance regressed) ::
        3dTstat -stdev 
                -mask mask.nii.gz 
                -prefix residual_filtered_3dT.nii.gz
                residual_filtered.nii.gz
    
    References
    ----------

    .. [1] Zou, Q.-H., Zhu, C.-Z., Yang, Y., Zuo, X.-N., Long, X.-Y., Cao, 
    Q.-J., Wang, Y.-F., et al. (2008). 
    An improved approach to detection of amplitude of low-frequency
    fluctuation (ALFF) for resting-state fMRI: fractional ALFF. Journal of
    neuroscience methods, 172(1), 137-41. doi:10.10

    Example
    --------

    >>> alff = create_alff('alff')
    >>> alff.inputs.inputspec.in_file = 'func.nii.gz'
    >>> alff.inputs.inputspec.mask= 'mask.nii.gz' 
    >>> alff.run() # doctest: +SKIP
    """

    wf = pe.Workflow(name= wf_name)
    in_node = pe.Node(util.IdentityInterface(fields=['in_file',
                                                     'mask',
                                                      'hp',
                                                      'lp']),
                        name='inputspec')

    out_node = pe.Node(util.IdentityInterface(fields=[ 'alff_img']),
                          name='outputspec')
    
    format_str = pe.Node(util.Function(input_names = ['mask'],
                                            output_names = ['option_string'],
                                            function = get_opt_string), 
                                name = 'get_option_string')
    wf.connect(in_node, 'mask', format_str, 'mask')
    
    #standard deviation over frequency
    stddev_fltrd = pe.Node(interface = preprocess.TStat(),
                            name = 'stddev_fltrd')
    stddev_fltrd.inputs.outputtype = 'NIFTI_GZ'
    wf.connect(in_node, 'in_file', stddev_fltrd, 'in_file')
    wf.connect(format_str, 'option_string', stddev_fltrd, 'options')
    wf.connect(stddev_fltrd, 'out_file', out_node, 'alff_img')
    
    return wf

def create_falff_wf(wf_name):
    """
    Calculate fractional Amplitude of low frequency oscillations(FALFF) map

    Parameters
    ----------
    wf_name : string
        Workflow name
         
    Returns
    -------
    wf : workflow object
        FALFF workflow

    Notes
    -----
    `Source <https://github.com/FCP-INDI/C-PAC/blob/master/CPAC/alff/alff.py>`_

    Workflow Inputs::
        inputspec.in_file : string (existing nifti file)
            Nuisance signal regressed functional image
        inputspec.mask : string (existing nifti file)
            A mask volume(derived by dilating the motion corrected functional
            volume) in native space

    Workflow Outputs::
        outputspec.falff_img : string (nifti file)
            outputs image containing the sum of the amplitudes in the low
            frequency band divided by the amplitude of the total frequency

    Order of Commands:

    - Calculate ALFF by taking the standard deviation of the input file
     (slice-time, motion corrected and nuisance regressed) ::
        3dTstat -stdev 
                -mask mask.nii.gz 
                -prefix residual_filtered_3dT.nii.gz
                residual_filtered.nii.gz
                                  
    - Calculate the standard deviation of the unfiltered file ::
        3dTstat -stdev 
                -mask mask.nii.gz 
                -prefix residual_3dT.nii.gz
                residual.nii.gz
  
    - Calculate fALFF ::
        3dcalc -a mask.nii.gz 
               -b alff.nii.gz
               -c residual_3dT.nii.gz  
               -expr '(1.0*bool(a))*((1.0*b)/(1.0*c))' -float
    
    References
    ----------

    .. [1] Zou, Q.-H., Zhu, C.-Z., Yang, Y., Zuo, X.-N., Long, X.-Y., Cao, 
    Q.-J., Wang, Y.-F., et al. (2008). 
    An improved approach to detection of amplitude of low-frequency
    fluctuation (ALFF) for resting-state fMRI: fractional ALFF. Journal of
    neuroscience methods, 172(1), 137-41. doi:10.10

    Example
    --------
    >>> from CPAC import alff
    >>> falff = alff.create_falff('falff')
    >>> falff.inputs.inputspec.in_file = 'func.nii.gz'
    >>> falff.inputs.inputspec.mask= 'mask.nii.gz' 
    >>> falff.run() # doctest: +SKIP
    """
    wf = pe.Workflow(name= wf_name)
    in_node = pe.Node(util.IdentityInterface(fields=['in_file',
                                                     'mask',
                                                     'alff']),
                        name='inputspec')

    out_node = pe.Node(util.IdentityInterface(fields=['falff_img']),
                          name='outputspec')

    format_str = pe.Node(util.Function(input_names = ['mask'],
                                            output_names = ['option_string'],
                                            function = get_opt_string), 
                                name = 'get_option_string')
    wf.connect(in_node, 'mask', format_str, 'mask')
    
    #standard deviation over frequency
    stddev_fltrd = pe.Node(interface = preprocess.TStat(),
                            name = 'stddev_fltrd')
    stddev_fltrd.inputs.outputtype = 'NIFTI_GZ'
    wf.connect(in_node, 'in_file', stddev_fltrd, 'in_file')
    wf.connect(format_str, 'option_string', stddev_fltrd, 'options')
    
    #standard deviation of the unfiltered nuisance corrected image
    stddev_unfltrd = pe.Node(interface = preprocess.TStat(),
                            name = 'stddev_unfltrd')
    stddev_unfltrd.inputs.outputtype = 'NIFTI_GZ'
    wf.connect(in_node, 'in_file', stddev_unfltrd, 'in_file')
    wf.connect(format_str, 'option_string', stddev_unfltrd, 'options')
    
    #falff calculations
    falff = pe.Node(interface = preprocess.Calc(), name = 'falff')
    falff.inputs.args = '-float'
    falff.inputs.expr = '(1.0*bool(a))*((1.0*b)/(1.0*c))'
    falff.inputs.outputtype = 'NIFTI_GZ'
    wf.connect(in_node, 'mask', falff, 'in_file_a')
    wf.connect(stddev_fltrd, 'out_file', falff, 'in_file_b')
    wf.connect(stddev_unfltrd, 'out_file', falff, 'in_file_c')
    wf.connect(falff, 'out_file', out_node, 'falff_img')

    return wf