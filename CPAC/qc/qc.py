import os
import sys
import commands
import nipype.pipeline.engine as pe
import nipype.interfaces.fsl as fsl
import nipype.interfaces.io as nio
import nipype.interfaces.utility as util
from CPAC.qc.qc import *
from CPAC.qc.utils import *
import nibabel as nb
import numpy as np
 
def edge_figure(overlay, underlay, fig_name):
    import matplotlib.pyplot as plt
    from nilearn import plotting
    
    slices = [x*5 for x in range(-12,12)]

    #x slices
    fig, ax = plt.subplots(nrows=3, ncols=1, figsize=(7,3))
    display = plotting.plot_anat(anat_img=underlay, figure=fig, axes=ax[0], display_mode='x', cut_coords=slices[:8])
    display.add_edges(overlay) 
    display = plotting.plot_anat(anat_img=underlay, figure=fig, axes=ax[1], display_mode='x', cut_coords=slices[8:16])
    display.add_edges(overlay) 
    display = plotting.plot_anat(anat_img=underlay, figure=fig, axes=ax[2], display_mode='x', cut_coords=slices[16:])
    display.add_edges(overlay)

    plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, hspace = 0, wspace = 0)
    fig.savefig(fig_name+'_x.png', pad_inches = 0, dpi=400)
    display.close()

    #z slices
    fig, ax = plt.subplots(nrows=3, ncols=1)
    display = plotting.plot_anat(anat_img=underlay, figure=fig, axes=ax[0], display_mode='z', cut_coords=slices[:8])
    display.add_edges(overlay) 
    display = plotting.plot_anat(anat_img=underlay, figure=fig, axes=ax[1], display_mode='z', cut_coords=slices[8:16])
    display.add_edges(overlay) 
    display = plotting.plot_anat(anat_img=underlay, figure=fig, axes=ax[2], display_mode='z', cut_coords=slices[16:])
    display.add_edges(overlay) 

    plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, hspace = 0, wspace = 0)
    fig.savefig(fig_name+'_z.png', pad_inches = 0, dpi=400)
    display.close()

    return fig_name+'_x.png', fig_name+'_z.png'

def overlay_figure(overlays, underlay, fig_name):
    import nibabel as nb
    import matplotlib.pyplot as plt
    from nilearn import plotting

    affine = nb.load(overlays[0]).get_affine()
    result = None
    for i, overlay in enumerate(overlays):
        #load data
        overlay = nb.load(overlay).get_data()
        #change masks values to draw different color for each one
        overlay[overlay == 1] = i+1

        #add overlays together
        if result is None:
            result = overlay
        else:
            result += overlay

    #create new img
    result = nb.Nifti1Image(result, affine)
    
    slices = [x*5 for x in range(-12,12)]

    #x slices
    fig, ax = plt.subplots(nrows=3, ncols=1, figsize=(7,3))
    display = plotting.plot_roi(roi_img=result, bg_img=underlay, figure=fig, axes=ax[0], display_mode='x',cmap=plt.cm.prism, cut_coords=slices[:8]) 
    display = plotting.plot_roi(roi_img=result, bg_img=underlay, figure=fig, axes=ax[1], display_mode='x',cmap=plt.cm.prism, cut_coords=slices[8:16])
    display = plotting.plot_roi(roi_img=result, bg_img=underlay, figure=fig, axes=ax[2], display_mode='x',cmap=plt.cm.prism, cut_coords=slices[16:])

    plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, hspace = 0, wspace = 0)
    fig.savefig(fig_name+'_x.png', pad_inches = 0, dpi=400)
    display.close()

    #z slices
    fig, ax = plt.subplots(nrows=3, ncols=1)
    display = plotting.plot_roi(roi_img=result, bg_img=underlay, figure=fig, axes=ax[0], display_mode='z',cmap=plt.cm.prism, cut_coords=slices[:8])
    display = plotting.plot_roi(roi_img=result, bg_img=underlay, figure=fig, axes=ax[1], display_mode='z',cmap=plt.cm.prism, cut_coords=slices[8:16])
    display = plotting.plot_roi(roi_img=result, bg_img=underlay, figure=fig, axes=ax[2], display_mode='z',cmap=plt.cm.prism, cut_coords=slices[16:])

    plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, hspace = 0, wspace = 0)
    fig.savefig(fig_name+'_z.png', pad_inches = 0, dpi=400)
    display.close()

    return fig_name+'_x.png', fig_name+'_z.png'


def create_subject_html(path, images):
    import shutil
    import CPAC
    #copy qcpages_html to log files
    src = os.path.join(path, 'qcpages_template')
    dst = os.path.join(path, 'qc')
    if os.path.exists(os.path.join(src)):
        shutil.rmtree(os.path.join(src))
    r = os.path.realpath(os.path.join(CPAC.__path__[0], 'resources', 'qcpages_template'))
    shutil.copytree(r, src)
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.move(src, dst)

    #put qc images on qc/images
    images_dst = os.path.join(dst, 'images')
    shutil.copytree(images, images_dst)

    #substitute dummy data for real data
    subhtml = os.path.join(dst, 'index.html')
    html = ''
    with open(subhtml, 'r+')as html_file:
        html = html_file.read()

        #change subject name in html
        sub_name = path.split('/')[-1]
        html = html.replace('subjectname', sub_name, 1)

    #save it again
    with open(subhtml, 'w') as html_file:
        html_file.write(html)

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
