from zoundry.blogapp.ui.views.browse.accountbrowser import ZAccountBrowseView
from zoundry.blogapp.ui.views.browse.blogbrowser import ZBlogBrowseView
from zoundry.blogapp.ui.views.browse.foldersbrowser import ZFoldersBrowseView
from zoundry.blogapp.ui.views.view import ZView
import wx

# ------------------------------------------------------------------------------
# Implements the 'account browser' of the Browse perspective.  This account
# browser view is a meta-view that simply coordinates/lays out the three views
# at the top of the browse perspective, which is much like the iTunes browse 
# feature.
# ------------------------------------------------------------------------------
class ZAccountMetaBrowser(ZView):

    def __init__(self, parent):
        ZView.__init__(self, parent, wx.ID_ANY)

        self._createWidgets()
        self._layoutWidgets()
        self._populateWidgets()
        self._bindWidgetEvents()
    # end __init__()

    def _createWidgets(self):
        self.accountBrowseView = ZAccountBrowseView(self)
        self.blogBrowseView = ZBlogBrowseView(self)
        self.foldersBrowseView = ZFoldersBrowseView(self)
    # end _createWidgets()

    def _layoutWidgets(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.accountBrowseView, 1, wx.EXPAND | wx.ALL, 2)
        sizer.Add(self.blogBrowseView, 1, wx.EXPAND | wx.ALL, 2)
        sizer.Add(self.foldersBrowseView, 1, wx.EXPAND | wx.ALL, 2)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        self.Layout()
    # end _layoutWidgets()

    def _populateWidgets(self):
        pass
    # end _populateWidgets()

    def _bindWidgetEvents(self):
        pass
    # end _bindWidgetEvents()

    def destroy(self):
        self.accountBrowseView.destroy()
        self.blogBrowseView.destroy()
        self.foldersBrowseView.destroy()
    # end destroy()

# end ZAccountMetaBrowser
