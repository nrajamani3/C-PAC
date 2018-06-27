import wx
import wx.html
from ..utils.generic_class import GenericClass
from ..utils.constants import control,dtype
from ..utils.validator import CharValidator
import os
import pkg_resources as p


class AromaProcessing(wx.html.HtmlWindow):
    
    def __init__(self,parent,counter = 0):
        from urllib2 import urlopen
        wx.html.HtmlWindow.__init__(self,parent,style = wx.html.HW_SCROLLBAR_AUTO)
        self.SetStandardFonts()
        
        self.counter = counter
        self.LoadPage(p.resource_filename('CPAC', 'GUI/resources/html/anat.html'))
    
    def get_counter(self):
        return self.counter

class AromaWorkflow(wx.html.HtmlWindow):

    def __init__(self,parent,counter = 0):
        wx.ScrolledWindow.__init__(self,parent)
        import os

        self.counter = counter
        self.page = GenericClass(self,"Aroma Workflow")

        self.page.add(label = "Run ICA fsl-Aroma?",
                      control=control.CHOICE_BOX,
                      name='runAroma',
                      type=dtype.STR,
                      comment="Run FSL's ICA-AROMA, which can work by",
                      values=["On","Off","On/Off"],
                      wkf_switch=True)

class AromaOptions(wx.html.HtmlWindow):

    def __init__(self,parent,counter = 0):
        wx.ScrolledWindow.__init__(self,parent)
        import os

        self.counter = counter
        self.page = GenericClass(self, "Aroma options")

        self.page.add(label="Specify the feat directory exists and temporal filtering has not been run",
                      control=control.COMBO_BOX,
                      name='aroma_feat',
                      type=dtype.STR,
                      comment="If a feat directory exists, i.e., if temporal filtering has not been run. This is mutually exclusive with in_file,mat_file,fnirt_warp_file",
                      values="")

        self.page.add(label ="Which stratergy would you like to denoise with?",
                      control=control.CHOICE_BOX,
                      name='aroma_denoise',
                      type=dtype.STR,
                      comment = "Choice of using 'nonaggr','aggr','both' or 'no' to perform ICA aroma",
                      values = ["noaggr","aggr","both","no"])

        self.page.add(label = "Repetition time, TR(s)",
        			  control = control.TEXT_BOX,
        			  name='aroma_TR',
        			  type=dtype.NUM,
        			  comment = "TR specified in seconds. If not specified, this will be taken from the header of the NIFTI file",
        			  values="None",
        			  validator = CharValidator("no-alpha"))


        self.page.add(label="Dimensionality reduction, whie running MELODIC",
        			  control=control.TEXT_BOX,
        			  name='aroma_dim',
        			  type=dtype.NUM,
        			  comment = "An integer or float value, default is automatic",
        			  validator=CharValidator("no-alpha"),
        			  values="")


        self.page.add(label="fnirt_warp_file",
        			  control=control.COMBO_BOX,
        			  name='aroma_fnirt_warp_file',
        			  type=dtype.STR,
        			  comment ="A file name of the warp file describing non-linear registration.This is mutually exclusive with feat_dir",
        			  values="")

        self.page.add(label="mask",
        			  control=control.COMBO_BOX,
        			  name='aroma_mask',
        			  type=dtype.STR,
        			  comment="A file of the volume mask, this is mutually exclusive with feat_dir",
        			  values="")

        self.page.add(label="mat_file",
        			  control=control.COMBO_BOX,
        			  name='aroma_mat',
        			  type=dtype.STR,
        			  comment="Path of a mat file describing the affine registration of the functional data to the structural space.This is mutually exclusive with feat_dir",
        			  values="")

        self.page.add(label="melodic_dir",
        			  control=control.COMBO_BOX,
        			  name='aroma_melodic',
        			  type=dtype.STR,
        			  comment="Path of an existing MELODIC directory, if it has already been run",
        			  values="")
        self.page.set_sizer()
        parent.get_page_list().append(self)


    def get_counter(self):
        return self.counter
