from zoundry.blogapp.constants import IZBlogAppExtensionPoints
from zoundry.blogapp.ui.views.standard.ctxview.details.commondetails import ZAbstractDetailsPanelContainer
from zoundry.blogapp.ui.views.standard.ctxview.linkdetails.linkdetailsdefs import ZLinkDetailsPanelDef

# -----------------------------------------------------------------------------------------
# This container class contains one or more instances of a ZLinkDetailsPanel.  Each
# link details container is shown in a separate tab (if there are multiple).
# -----------------------------------------------------------------------------------------
class ZLinkDetailsPanelContainer(ZAbstractDetailsPanelContainer):

    def __init__(self, parent):
        ZAbstractDetailsPanelContainer.__init__(self, parent)
    # end __init__()
    
    def _getExtensionPoint(self):
        return IZBlogAppExtensionPoints.ZEP_ZOUNDRY_STANDARD_LINK_DETAILS_PANEL
    # end _getExtensionPoint()

    def _getExtensionDefClass(self):
        return ZLinkDetailsPanelDef
    # end _getExtensionDefClass()

    def onLinkSelectionChanged(self, linkIDO):
        for (panelName, panel) in self.detailsPanels: #@UnusedVariable
            panel.onSelectionChanged(linkIDO)
    # end onLinkSelectionChanged()

# end ZLinkDetailsPanelContainer
