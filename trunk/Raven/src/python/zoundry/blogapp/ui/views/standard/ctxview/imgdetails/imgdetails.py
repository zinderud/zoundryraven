from zoundry.blogapp.constants import IZBlogAppExtensionPoints
from zoundry.blogapp.ui.views.standard.ctxview.details.commondetails import ZAbstractDetailsPanelContainer
from zoundry.blogapp.ui.views.standard.ctxview.imgdetails.imgdetailsdefs import ZImageDetailsPanelDef


# -----------------------------------------------------------------------------------------
# This container class contains one or more instances of a ZImageDetailsPanel.  Each
# image details container is shown in a separate tab (if there are multiple).
# -----------------------------------------------------------------------------------------
class ZImageDetailsPanelContainer(ZAbstractDetailsPanelContainer):

    def __init__(self, parent):
        ZAbstractDetailsPanelContainer.__init__(self, parent)
    # end __init__()
    
    def _getExtensionPoint(self):
        return IZBlogAppExtensionPoints.ZEP_ZOUNDRY_STANDARD_IMAGE_DETAILS_PANEL
    # end _getExtensionPoint()

    def _getExtensionDefClass(self):
        return ZImageDetailsPanelDef
    # end _getExtensionDefClass()

    def onImageSelectionChanged(self, data):
        for (panelName, panel) in self.detailsPanels: #@UnusedVariable
            panel.onSelectionChanged(data)
    # end onImageSelectionChanged()

# end ZImageDetailsPanelContainer
