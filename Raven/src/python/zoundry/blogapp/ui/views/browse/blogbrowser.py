from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.global_services import getResourceRegistry
from zoundry.appframework.resources.resourceutils import ZMappedImageList
from zoundry.appframework.ui.util.uiutil import fireRefreshEvent
from zoundry.appframework.ui.widgets.controls.common.menu.menu import ZMenu
from zoundry.appframework.ui.widgets.controls.common.menu.menumodel import ZModelBasedMenuContentProvider
from zoundry.appframework.ui.widgets.controls.common.menu.menumodel import ZModelBasedMenuEventHandler
from zoundry.appframework.ui.widgets.controls.listex import IZListViewExContentProvider
from zoundry.appframework.ui.widgets.controls.listex import ZListViewEx
from zoundry.blogapp.constants import IZBlogAppServiceIDs
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.services.accountstore.accountstore import IZAccountStoreListener
from zoundry.blogapp.ui.actions.blog.blogactions import ZBlogMenuActionContext
from zoundry.blogapp.ui.events.viewevents import ZEVT_VIEW_SELECTION_CHANGED
from zoundry.blogapp.ui.menus.blog.blogmenu import ZBlogMenuModel
from zoundry.blogapp.ui.util.viewutil import fireViewUnselectionEvent
from zoundry.blogapp.ui.views.view import ZView
from zoundry.blogapp.ui.views.viewsel import IZViewSelectionTypes
from zoundry.blogapp.ui.views.viewselimpl import ZViewSelection
from zoundry.blogapp.ui.util.viewutil import fireViewSelectionEvent
import wx

# ------------------------------------------------------------------------------
# List view content provider for providing a list of blogs.
# ------------------------------------------------------------------------------
class ZBlogListProvider(IZListViewExContentProvider):

    def __init__(self):
        self.accountStore = getApplicationModel().getService(IZBlogAppServiceIDs.ACCOUNT_STORE_SERVICE_ID)
        self.accountId = None
        self.blogs = None
        self.imageList = self._createImageList()

        self.refresh()
    # end __init__()

    def getAccountId(self):
        return self.accountId
    # end getAccountId()

    def setAccountId(self, accountId):
        self.accountId = accountId
    # end setAccountId()

    def _createImageList(self):
        # FIXME (EPW) Move account and blog icons to a common area and use from there (also chnage navigator)
        registry = getResourceRegistry()
        imgList = ZMappedImageList()
        imgList.addImage(u"blog", registry.getBitmap(u"images/perspectives/standard/navigator/blog.png")) #$NON-NLS-1$ #$NON-NLS-2$

        return imgList
    # end _createImageList

    def refresh(self):
        self.blogs = []
        for account in self.accountStore.getAccounts():
            if account.getId() == self.accountId:
                for blog in account.getBlogs():
                    self.blogs.append(blog)
    # end refresh()

    def getImageList(self):
        return self.imageList
    # end getImageList()

    def getNumColumns(self):
        return 1
    # end getNumColumns()

    def getNumRows(self):
        return len(self.blogs)
    # end getNumRows()

    def getColumnInfo(self, columnIndex): #@UnusedVariable
        return (_extstr(u"blogbrowser.Blogs"), None, None, ZListViewEx.COLUMN_LOCKED | ZListViewEx.COLUMN_RELATIVE, 100) #$NON-NLS-1$
    # end getColumnInfo()

    def getRowText(self, rowIndex, columnIndex): #@UnusedVariable
        return self.blogs[rowIndex].getName()
    # end getRowText()

    def getRowImage(self, rowIndex, columnIndex): #@UnusedVariable
        return self.imageList[u"blog"] #$NON-NLS-1$
    # end getRowImage()

    def getBlogAtIndex(self, index):
        return self.blogs[index]
    # end getBlogAtIndex()

# end ZBlogListProvider


# ------------------------------------------------------------------------------
# Implements the second of three views in the Browse perspective.  This view
# presents the user with a list of Blogs found in the selected account.
# ------------------------------------------------------------------------------
class ZBlogBrowseView(ZView, IZAccountStoreListener):

    def __init__(self, parent):
        ZView.__init__(self, parent, wx.ID_ANY)

        self._createWidgets()
        self._layoutWidgets()
        self._populateWidgets()
        self._bindWidgetEvents()

        self._registerAsAccountListener()
    # end __init__()

    def _createWidgets(self):
        self.blogListProvider = ZBlogListProvider()
        self.blogListView = ZListViewEx(self.blogListProvider, self)
    # end _createWidgets()

    def _layoutWidgets(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.blogListView, 1, wx.EXPAND)

        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        self.Layout()
    # end _layoutWidgets()

    def _populateWidgets(self):
        pass
    # end _populateWidgets()

    def _bindWidgetEvents(self):
        self.Bind(ZEVT_VIEW_SELECTION_CHANGED, self.onViewSelection)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onBlogSelected, self.blogListView)
        self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.onBlogRightClick, self.blogListView)
        self._bindRefreshEvent(self.onZoundryRefresh)
    # end _bindWidgetEvents()

    def onBlogRightClick(self, event):
        blog = self._getSelectedBlog()
        if blog is not None:
            menu = self._createBlogCtxMenu(blog)
            self.PopupMenu(menu)
            menu.Destroy()
        event.Skip()
    # end onBlogRightClick()

    def _createBlogCtxMenu(self, blog):
        menuContext = ZBlogMenuActionContext(self, blog)
        menuModel = ZBlogMenuModel()
        provider = ZModelBasedMenuContentProvider(menuModel, menuContext)
        eventHandler = ZModelBasedMenuEventHandler(menuModel, menuContext)
        return ZMenu(self, menuModel.getRootNode(), provider, eventHandler)
    # end _createBlogCtxMenu()

    def onViewSelection(self, event):
        selection = event.getSelection()
        if selection.getType() == IZViewSelectionTypes.ACCOUNT_SELECTION:
            accountId = selection.getData()
            self.blogListProvider.setAccountId(accountId)
            self.blogListProvider.refresh()
            self.blogListView.refresh()
            self.blogListView.deselectAll()
        elif selection.getType() == IZViewSelectionTypes.UNPUBLISHED_ACCOUNT_SELECTION:
            self.blogListProvider.setAccountId(None)
            self.blogListProvider.refresh()
            self.blogListView.refresh()
            self.blogListView.deselectAll()

        event.Skip()
    # end onViewSelection()

    def onBlogSelected(self, event):
        blog = self._getSelectedBlog()
        if blog is not None:
            account = blog.getAccount()
            accountId = account.getId()
            blogId = blog.getId()
            selection = ZViewSelection(IZViewSelectionTypes.BLOG_SELECTION, (accountId, blogId))
            fireViewSelectionEvent(selection, self)
        else:
            fireViewUnselectionEvent()
        event.Skip()
    # end onBlogSelected()

    def onZoundryRefresh(self, event):
        self.blogListView.refresh()
        event.Skip()
    # end onZoundryRefresh()

    def onAccountChanged(self, account):
        if account.getId() == self.blogListProvider.getAccountId():
            self.blogListProvider.refresh()
            fireRefreshEvent(self)
    # end onAccountChanged()

    def onAccountDeleted(self, account):
        if account.getId() == self.blogListProvider.getAccountId():
            self.blogListProvider.setAccountId(None)
            self.blogListProvider.refresh()
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

    def _getSelectedBlog(self):
        itemIndexes = self.blogListView.getSelection()
        if itemIndexes:
            itemIndex = itemIndexes[0]
            return self.blogListProvider.getBlogAtIndex(itemIndex)
        return None
    # end _getSelectedBlog()

# end ZBlogBrowseView
