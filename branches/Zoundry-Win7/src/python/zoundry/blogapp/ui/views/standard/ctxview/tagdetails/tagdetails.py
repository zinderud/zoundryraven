from zoundry.blogapp.constants import IZBlogAppExtensionPoints
from zoundry.blogapp.ui.views.standard.ctxview.details.commondetails import ZAbstractDetailsPanelContainer
from zoundry.blogapp.ui.views.standard.ctxview.tagdetails.tagdetailsdefs import ZTagDetailsPanelDef

# -----------------------------------------------------------------------------------------
# This container class contains one or more instances of a ZTagDetailsPanel.  Each
# tag details container is shown in a separate tab (if there are multiple).
# -----------------------------------------------------------------------------------------
class ZTagDetailsPanelContainer(ZAbstractDetailsPanelContainer):

    def __init__(self, parent):
        ZAbstractDetailsPanelContainer.__init__(self, parent)
    # end __init__()
    
    def _getExtensionPoint(self):
        return IZBlogAppExtensionPoints.ZEP_ZOUNDRY_STANDARD_TAG_DETAILS_PANEL
    # end _getExtensionPoint()

    def _getExtensionDefClass(self):
        return ZTagDetailsPanelDef
    # end _getExtensionDefClass()

    def onTagSelectionChanged(self, data):
        for (panelName, panel) in self.detailsPanels: #@UnusedVariable
            panel.onSelectionChanged(data)
    # end onTagSelectionChanged()

# end ZTagDetailsPanelContainer
