from zoundry.appframework.ui.events.listevents import ZEVT_CHECKBOX_LIST_CHANGE
from zoundry.appframework.ui.widgets.controls.listex import ZRadioBoxListView
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.models.ui.dialogs.mediastoragemodel import ZMediaStorageManagerModel
from zoundry.blogapp.ui.common.mediastoragewidgets import ZMediaStorageCheckBoxListContentProvider
from zoundry.blogapp.ui.dialogs.accountmanpages.acctsubpages.subpage import ZAccountPrefsSubPage
import wx

# ------------------------------------------------------------------------------
# The model used by this page.
# ------------------------------------------------------------------------------
class ZMediaStoragePrefSubPageModel(ZMediaStorageManagerModel):

    def __init__(self):
        ZMediaStorageManagerModel.__init__(self)
    # end __init__()

    # Only include storages that are not internal.
    def _shouldIncludeStorage(self, storage):
        siteId = storage.getMediaSiteId()
        site = self.getService().getMediaSite(siteId)
        return site is not None
    # end _shouldIncludeStorage()

# end ZMediaStoragePrefSubPageModel


# ------------------------------------------------------------------------------
# Implements the account preferences sub-page for media storage options.
# ------------------------------------------------------------------------------
class ZMediaStoragePrefSubPage(ZAccountPrefsSubPage):

    def __init__(self, parent, session):
        self.model = ZMediaStoragePrefSubPageModel()

        ZAccountPrefsSubPage.__init__(self, parent, session)
    # end __init__()

    def _createWidgets(self):
        self._createStoreWidgets(self)
    # end _createWidgets()

    def _createStoreWidgets(self, parent):
        self.staticBox = wx.StaticBox(parent, wx.ID_ANY, _extstr(u"storesubpage.UploadFilesVia")) #$NON-NLS-1$
        self.contentProvider = ZMediaStorageCheckBoxListContentProvider(self.model)
        self.mediaStoresLB = ZRadioBoxListView(self.contentProvider, parent, wx.ID_ANY)

    # end _createStoreWidgets()

    def _bindWidgetEvents(self):
        self.Bind(ZEVT_CHECKBOX_LIST_CHANGE, self.onMediaStorageCheckListChange, self.mediaStoresLB)
    # end _bindWidgetEvents()

    def _populateWidgets(self):
        storeId = self.session.getStoreId()
        self.contentProvider.setSelectedStoreId(storeId)
        self.mediaStoresLB.refreshItems()
    # end _populateWidgets()

    def _layoutWidgets(self):
        sizer = self._createStoreLayout()

        self.SetAutoLayout(True)
        self.SetSizer(sizer)
        self.Layout()
    # end layoutWidgets()

    def _createStoreLayout(self):
        sbSizer = wx.StaticBoxSizer(self.staticBox, wx.VERTICAL)
        sbSizer.Add(self.mediaStoresLB, 1, wx.EXPAND | wx.ALL, 8)

        box = wx.BoxSizer(wx.VERTICAL)
        box.AddSizer(sbSizer, 1, wx.ALL | wx.EXPAND, 5)

        return box
    # end _createStoreLayout()

    def onMediaStorageCheckListChange(self, event):
        storeId = self.contentProvider.getSelectedStoreId()
        if storeId:
            self.session.setStoreId(storeId)
        event.Skip()
    # end onMediaStorageSelected()

# end ZMediaStoragePrefSubPage
