from zoundry.blogapp.ui.perspectives.standard import ZStandardPerspective
from zoundry.blogapp.ui.views.browse.metabrowser import ZAccountMetaBrowser
from zoundry.blogapp.constants import IZBlogAppUserPrefsKeys

# ------------------------------------------------------------------------------
# The iTunes-like "browse" perspective.  This view of the data will have a three
# panel browse interface on the top.
#
# ::Notes on Events::
#   In order for the toolbar to update based on the selection that the user
#   makes, it is the responsibility of the various views to fire events that
#   the perspective can listen to.
#
#   ZEVT_VIEW_SELECTION_CHANGED:  fired when the user selects something in a 
#      view.  The perspective will update/maintain its "current selection"
#      information based on this event.  If the user "un-selects" something,
#      this event will be fired, possibly with "None" as the selection.
# ------------------------------------------------------------------------------
class ZBrowsePerspective(ZStandardPerspective):

    def __init__(self):
        ZStandardPerspective.__init__(self)
    # end __init__()

    def _createNavigatorView(self, parent):
        self.navView = ZAccountMetaBrowser(parent)
    # end _createNavigatorView()

    def _doSplit(self):
        self.splitterWindow.SplitHorizontally(self.navView, self.ctxView)
        self.splitterWindow.SetMinimumPaneSize(100)
        self.splitterWindow.SetSashSize(8)
        self.splitterWindow.SetSashGravity(0.0)
    # end _doSplit()

#    def createUIPanel(self, parent):
#        panel = ZTransparentPanel(parent, wx.ID_ANY)
#        wx.StaticText(panel, wx.ID_ANY, u"Browse Perspective.")
#        return panel
#    # end createUI()

    def _getUserPrefsKey(self):
        return IZBlogAppUserPrefsKeys.BROWSE_PERSPECTIVE_LAYOUT
    # end _getUserPrefsKey()

# end ZBrowsePerspective
