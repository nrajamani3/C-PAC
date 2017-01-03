import os
import sys
import commands
import nipype.pipeline.engine as pe
import nipype.interfaces.fsl as fsl
import nipype.interfaces.io as nio
import nipype.interfaces.utility as util
from CPAC.qc.qc import *
from CPAC.qc.utils import *

import matplotlib.pyplot as plt
from nilearn import plotting



def anat_figure(fig_name, overlay, underlay):
    slices = [x*5 for x in range(-12,12)]

    #x slices
    fig, ax = plt.subplots(nrows=3, ncols=1, figsize=(7,3))
    display = plotting.plot_anat(anat_img=anat_file, figure=fig, axes=ax[0], display_mode='x', cut_coords=slices[:8])
    display.add_edges(edges_file) 
    display = plotting.plot_anat(anat_img=anat_file, figure=fig, axes=ax[1], display_mode='x', cut_coords=slices[8:16])
    display.add_edges(edges_file) 
    display = plotting.plot_anat(anat_img=anat_file, figure=fig, axes=ax[2], display_mode='x', cut_coords=slices[16:])
    display.add_edges(edges_file)

    plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, hspace = 0, wspace = 0)
    fig.savefig(fig_name+'_x.png', pad_inches = 0, dpi=400)
    display.close()

    #z slices
    fig, ax = plt.subplots(nrows=3, ncols=1)
    display = plotting.plot_anat(anat_img=anat_file, figure=fig, axes=ax[0], display_mode='z', cut_coords=slices[:8])
    display.add_edges(edges_file) 
    display = plotting.plot_anat(anat_img=anat_file, figure=fig, axes=ax[1], display_mode='z', cut_coords=slices[8:16])
    display.add_edges(edges_file) 
    display = plotting.plot_anat(anat_img=anat_file, figure=fig, axes=ax[2], display_mode='z', cut_coords=slices[16:])
    display.add_edges(edges_file) 

    plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, hspace = 0, wspace = 0)
    fig.savefig(fig_name+'_z.png', pad_inches = 0, dpi=400)
    display.close()

    return fig_name+'_x.png', fig_name+'_z.png'

def subject_html(folder, subject, skullstripx, skullstripz):
    import shutil
    #copy qcpages_html to output files, rename it to subject name
    src = os.join(folder, 'qcpages_html')
    dst = os.join(folder, 'qc')
    if os.path.exists(os.join(src):
        shutil.rmtree(os.join(src)
    shutil.copytree('qcpages_html', src)
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.move(src, dst)

    #put qc images on subject_name/assets
    assets = os.join(dst, 'assets')
    shutil.copy(skullstripx, assets)
    shutil.copy(skullstripz, assets)


    #change subject name in html

    #done!



def create_montage(wf_name, cbar_name, png_name):

    wf = pe.Workflow(name=wf_name)

    inputNode = pe.Node(util.IdentityInterface(fields=['underlay',
                                                       'overlay']),
                        name='inputspec')

    outputNode = pe.Node(util.IdentityInterface(fields=['axial_png',
                                                        'sagittal_png',
                                                        'resampled_underlay',
                                                        'resampled_overlay']),
                          name='outputspec')


    resample_u = pe.Node(util.Function(input_names=['file_'],
                                       output_names=['new_fname'],
                                       function=resample_1mm),
                           name='resample_u')

    resample_o = resample_u.clone('resample_o')



    montage_a = pe.Node(util.Function(input_names=['overlay',
                                                  'underlay',
                                                  'png_name',
                                                  'cbar_name'],
                                      output_names=['png_name'],
                                      function=montage_axial),
                         name='montage_a')
    montage_a.inputs.cbar_name = cbar_name
    montage_a.inputs.png_name = png_name + '_a.png'


    montage_s = pe.Node(util.Function(input_names=['overlay',
                                                   'underlay',
                                                   'png_name',
                                                   'cbar_name'],
                                      output_names=['png_name'],
                                      function=montage_sagittal),
                                   name='montage_s')
    montage_s.inputs.cbar_name = cbar_name
    montage_s.inputs.png_name = png_name + '_s.png'

    wf.connect(inputNode, 'underlay',
                resample_u, 'file_')

    wf.connect(inputNode, 'overlay',
                resample_o, 'file_')

    wf.connect(resample_u, 'new_fname',
                montage_a, 'underlay')

    wf.connect(resample_o, 'new_fname',
                montage_a, 'overlay')

    wf.connect(resample_u, 'new_fname',
                montage_s, 'underlay')

    wf.connect(resample_o, 'new_fname',
                montage_s, 'overlay')

    wf.connect(resample_u, 'new_fname',
                outputNode, 'resampled_underlay')

    wf.connect(resample_o, 'new_fname',
                outputNode, 'resampled_overlay')

    wf.connect(montage_a, 'png_name',
                outputNode, 'axial_png')

    wf.connect(montage_s, 'png_name',
                outputNode, 'sagittal_png')


    return wf

def create_montage_gm_wm_csf(wf_name, png_name):

    wf = pe.Workflow(name=wf_name)

    inputNode = pe.Node(util.IdentityInterface(fields=['underlay',
                                                       'overlay_csf',
                                                       'overlay_wm',
                                                       'overlay_gm']),
                        name='inputspec')

    outputNode = pe.Node(util.IdentityInterface(fields=['axial_png',
                                                        'sagittal_png',
                                                        'resampled_underlay',
                                                        'resampled_overlay_csf',
                                                        'resampled_overlay_wm',
                                                        'resampled_overlay_gm']),
                          name='outputspec')


    resample_u = pe.Node(util.Function(input_names=['file_'],
                                       output_names=['new_fname'],
                                       function=resample_1mm),
                           name='resample_u')

    resample_o_csf = resample_u.clone('resample_o_csf')
    resample_o_wm = resample_u.clone('resample_o_wm')
    resample_o_gm = resample_u.clone('resample_o_gm')



    montage_a = pe.Node(util.Function(input_names=['overlay_csf',
                                                   'overlay_wm',
                                                   'overlay_gm',
                                                  'underlay',
                                                  'png_name'],
                                      output_names=['png_name'],
                                      function=montage_gm_wm_csf_axial),
                         name='montage_a')
    montage_a.inputs.png_name = png_name + '_a.png'


    montage_s = pe.Node(util.Function(input_names=['overlay_csf',
                                                   'overlay_wm',
                                                   'overlay_gm',
                                                   'underlay',
                                                   'png_name'],
                                      output_names=['png_name'],
                                      function=montage_gm_wm_csf_sagittal),
                                   name='montage_s')
    montage_s.inputs.png_name = png_name + '_s.png'

    wf.connect(inputNode, 'underlay',
                resample_u, 'file_')

    wf.connect(inputNode, 'overlay_csf',
                resample_o_csf, 'file_')

    wf.connect(inputNode, 'overlay_gm',
                resample_o_gm, 'file_')

    wf.connect(inputNode, 'overlay_wm',
                resample_o_wm, 'file_')

    wf.connect(resample_u, 'new_fname',
                montage_a, 'underlay')

    wf.connect(resample_o_csf, 'new_fname',
                montage_a, 'overlay_csf')

    wf.connect(resample_o_gm, 'new_fname',
                montage_a, 'overlay_gm')

    wf.connect(resample_o_wm, 'new_fname',
                montage_a, 'overlay_wm')

    wf.connect(resample_u, 'new_fname',
                montage_s, 'underlay')

    wf.connect(resample_o_csf, 'new_fname',
                montage_s, 'overlay_csf')

    wf.connect(resample_o_gm, 'new_fname',
                montage_s, 'overlay_gm')

    wf.connect(resample_o_wm, 'new_fname',
                montage_s, 'overlay_wm')

    wf.connect(resample_u, 'new_fname',
                outputNode, 'resampled_underlay')

    wf.connect(resample_o_csf, 'new_fname',
                outputNode, 'resampled_overlay_csf')

    wf.connect(resample_o_wm, 'new_fname',
                outputNode, 'resampled_overlay_wm')

    wf.connect(resample_o_gm, 'new_fname',
                outputNode, 'resampled_overlay_gm')

    wf.connect(montage_a, 'png_name',
                outputNode, 'axial_png')

    wf.connect(montage_s, 'png_name',
                outputNode, 'sagittal_png')


    return wf
