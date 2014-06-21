from zoundry.blogapp.constants import IZBlogAppExtensionPoints
from zoundry.blogapp.ui.views.standard.ctxview.details.commondetails import ZAbstractDetailsPanelContainer
from zoundry.blogapp.ui.views.standard.ctxview.postdetails.postdetailsdefs import ZBlogPostDetailsPanelDef


# -----------------------------------------------------------------------------------------
# This container class contains one or more instances of a ZBlogPostDetailsPanel.  Each
# blog post details container is shown in a separate tab (if there are multiple).
# -----------------------------------------------------------------------------------------
class ZBlogPostDetailsPanelContainer(ZAbstractDetailsPanelContainer):

    def __init__(self, parent):
        ZAbstractDetailsPanelContainer.__init__(self, parent)
    # end __init__()

    def _getExtensionPoint(self):
        return IZBlogAppExtensionPoints.ZEP_ZOUNDRY_STANDARD_POST_DETAILS_PANEL
    # end _getExtensionPoint()

    def _getExtensionDefClass(self):
        return ZBlogPostDetailsPanelDef
    # end _getExtensionDefClass()

    def onBlogPostSelectionChanged(self, document):
        for (panelName, panel) in self.detailsPanels: #@UnusedVariable
            panel.onSelectionChanged(document)
    # end onBlogPostSelectionChanged()

# end ZBlogPostDetailsPanelContainer
