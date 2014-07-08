from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.global_services import getResourceRegistry
from zoundry.appframework.resources.resourceutils import ZMappedImageList
from zoundry.appframework.ui.util.uiutil import fireRefreshEvent
from zoundry.appframework.ui.widgets.controls.listex import IZListViewExContentProvider
from zoundry.appframework.ui.widgets.controls.listex import ZListViewEx
from zoundry.blogapp.constants import IZBlogAppServiceIDs
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.ui.events.viewevents import ZEVT_VIEW_SELECTION_CHANGED
from zoundry.blogapp.ui.util.viewutil import fireViewSelectionEvent
from zoundry.blogapp.ui.util.viewutil import fireViewUnselectionEvent
from zoundry.blogapp.ui.views.view import ZView
from zoundry.blogapp.ui.views.viewsel import IZViewSelectionTypes
from zoundry.blogapp.ui.views.viewselimpl import ZViewSelection
import wx

UNPUBLISHED_ACCOUNT_ID = u"_unpublished_" #$NON-NLS-1$

# ------------------------------------------------------------------------------
# List view content provider for providing a list of blog folders.
# ------------------------------------------------------------------------------
class ZFolderListProvider(IZListViewExContentProvider):

    def __init__(self):
        self.folders = None
        self.accountId = None
        self.blogId = None
        self.imageList = self._createImageList()

        self.refresh()
    # end __init__()

    def getAccountId(self):
        return self.accountId
    # end getAccountId()

    def getBlogId(self):
        return self.blogId
    # end getBlogId()

    def setAccountId(self, accountId):
        self.accountId = accountId
    # end setAccountId()

    def setBlogId(self, blogId):
        self.blogId = blogId
    # end setBlogId()

    def _createImageList(self):
        # FIXME (EPW) Move icons to a common area and use from there (also change navigator)
        registry = getResourceRegistry()
        imgList = ZMappedImageList()
        for img in [u"posts", u"links", u"images", u"tags"]: #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$ #$NON-NLS-4$ #$NON-NLS-5$ #$NON-NLS-6$ #$NON-NLS-7$ #$NON-NLS-8$
            imgList.addImage(img, registry.getBitmap(u"images/perspectives/standard/navigator/%s.png" % img)) #$NON-NLS-1$

        return imgList
    # end _createImageList

    def refresh(self):
        # Folders is list of tuples:  (folderName, folderIcon, folderType)
        self.folders = []
        if self.accountId == UNPUBLISHED_ACCOUNT_ID or self.blogId is not None:
            self.folders.append( (_extstr(u"foldersbrowser.Posts"), u"posts", IZViewSelectionTypes.BLOG_POSTS_SELECTION) ) #$NON-NLS-2$ #$NON-NLS-1$
            self.folders.append( (_extstr(u"foldersbrowser.Links"), u"links", IZViewSelectionTypes.BLOG_LINKS_SELECTION) ) #$NON-NLS-2$ #$NON-NLS-1$
            self.folders.append( (_extstr(u"foldersbrowser.Images"), u"images", IZViewSelectionTypes.BLOG_IMAGES_SELECTION) ) #$NON-NLS-2$ #$NON-NLS-1$
            self.folders.append( (_extstr(u"foldersbrowser.Tags"), u"tags", IZViewSelectionTypes.BLOG_TAGS_SELECTION) ) #$NON-NLS-2$ #$NON-NLS-1$
            #self.folders.append( (_extstr(u"foldersbrowser.Edited"), u"posts", IZViewSelectionTypes.BLOG_EDITED_SELECTION) ) #vaigai-Zoundry-Raven
    # end refresh()

    def getImageList(self):
        return self.imageList
    # end getImageList()

    def getNumColumns(self):
        return 1
    # end getNumColumns()

    def getNumRows(self):
        return len(self.folders)
    # end getNumRows()

    def getColumnInfo(self, columnIndex): #@UnusedVariable
        return (_extstr(u"foldersbrowser.Folders"), None, None, ZListViewEx.COLUMN_LOCKED | ZListViewEx.COLUMN_RELATIVE, 100) #$NON-NLS-1$
    # end getColumnInfo()

    def getRowText(self, rowIndex, columnIndex): #@UnusedVariable
        return self.folders[rowIndex][0]
    # end getRowText()

    def getRowImage(self, rowIndex, columnIndex): #@UnusedVariable
        return self.imageList[ self.folders[rowIndex][1] ]
    # end getRowImage()

    def getFolderType(self, index):
        return self.folders[index][2]
    # end getFolderType()

# end ZFolderListProvider


# ------------------------------------------------------------------------------
# Implements the third of three views in the Browse perspective.  This view
# presents the user with the list of folders (posts, links, images, etc) to
# narrow down their selection.
# ------------------------------------------------------------------------------
class ZFoldersBrowseView(ZView):

    def __init__(self, parent):
        ZView.__init__(self, parent, wx.ID_ANY)

        self._createWidgets()
        self._layoutWidgets()
        self._populateWidgets()
        self._bindWidgetEvents()

        self._registerAsAccountListener()
    # end __init__()

    def _createWidgets(self):
        self.folderListProvider = ZFolderListProvider()
        self.folderListView = ZListViewEx(self.folderListProvider, self)
    # end _createWidgets()

    def _layoutWidgets(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.folderListView, 1, wx.EXPAND)

        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        self.Layout()
    # end _layoutWidgets()

    def _populateWidgets(self):
        pass
    # end _populateWidgets()

    def _bindWidgetEvents(self):
        self.Bind(ZEVT_VIEW_SELECTION_CHANGED, self.onViewSelection)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onFolderSelected, self.folderListView)
        self._bindRefreshEvent(self.onZoundryRefresh)
    # end _bindWidgetEvents()

    def onViewSelection(self, event):
        selection = event.getSelection()
        if selection.getType() == IZViewSelectionTypes.BLOG_SELECTION:
            (accountId, blogId) = selection.getData()
            self._refreshListView(accountId, blogId)
        elif selection.getType() == IZViewSelectionTypes.UNPUBLISHED_ACCOUNT_SELECTION:
            self._refreshListView(UNPUBLISHED_ACCOUNT_ID, None)
        elif selection.getType() == IZViewSelectionTypes.ACCOUNT_SELECTION:
            self._refreshListView(None, None)

        event.Skip()
    # end onViewSelection()

    def _refreshListView(self, accountId, blogId):
        self.folderListProvider.setAccountId(accountId)
        self.folderListProvider.setBlogId(blogId)
        self.folderListProvider.refresh()
        self.folderListView.refresh()
        self.folderListView.deselectAll()
    # end _refreshListView()

    def onFolderSelected(self, event):
        folderType = self._getSelectedFolderType()
        if folderType is not None:
            accountId = self.folderListProvider.getAccountId()
            blogId = self.folderListProvider.getBlogId()
            if accountId == UNPUBLISHED_ACCOUNT_ID:
                accountId = None
                blogId = None
            selection = ZViewSelection(folderType, (accountId, blogId))
            fireViewSelectionEvent(selection, self)
        else:
            fireViewUnselectionEvent()
        event.Skip()
    # end onFolderSelected()

    def onZoundryRefresh(self, event):
        self.folderListView.refresh()
        event.Skip()
    # end onZoundryRefresh()

    def onAccountDeleted(self, account):
        if account.getId() == self.folderListProvider.getAccountId():
            self.folderListProvider.setAccountId(None)
            self.folderListProvider.setBlogId(None)
            self.folderListProvider.refresh()
            fireRefreshEvent(self)
    # end onAccountDeleted()

    def _registerAsAccountListener(self):
        accountStore = getApplicationModel().getService(IZBlogAppServiceIDs.ACCOUNT_STORE_SERVICE_ID)
        accountStore.addListener(self)
    # end _registerAsAccountListener()

    def _unregisterAsAccountListener(self):
        accountStore = getApplicationModel().getService(IZBlogAppServiceIDs.ACCOUNT_STORE_SERVICE_ID)
        accountStore.removeListener(self)
    # end _unregisterAsAccountListener()

    def destroy(self):
        self._unregisterAsAccountListener()
    # end destroy()

    def _getSelectedFolderType(self):
        itemIndexes = self.folderListView.getSelection()
        if itemIndexes:
            itemIndex = itemIndexes[0]
            return self.folderListProvider.getFolderType(itemIndex)
        return None
    # end _getSelectedFolderType()

# end ZFoldersBrowseView
