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
from zoundry.blogapp.services.accountstore.account import IZAccount
from zoundry.blogapp.services.accountstore.accountstore import IZAccountStoreListener
from zoundry.blogapp.ui.menus.account.accountmenu import ZAccountMenuActionContext
from zoundry.blogapp.ui.menus.account.accountmenu import ZBlogAccountMenuModel
from zoundry.blogapp.ui.util.viewutil import fireViewSelectionEvent
from zoundry.blogapp.ui.util.viewutil import fireViewUnselectionEvent
from zoundry.blogapp.ui.views.view import ZView
from zoundry.blogapp.ui.views.viewsel import IZViewSelectionTypes
from zoundry.blogapp.ui.views.viewselimpl import ZViewSelection
import wx

# ------------------------------------------------------------------------------
# A special account representing 'unpublished' content.
# ------------------------------------------------------------------------------
class ZUnpublishedAccount(IZAccount):

    def getId(self):
        return -1
    # end getId()

    def getName(self):
        return u"(%s)" % _extstr(u"accountbrowser.Unpublished") #$NON-NLS-1$ #$NON-NLS-2$
    # end getName()

# end ZUnpublishedAccount


# ------------------------------------------------------------------------------
# List view content provider for providing a list of accounts.
# ------------------------------------------------------------------------------
class ZAccountListProvider(IZListViewExContentProvider):

    def __init__(self):
        self.accountStore = getApplicationModel().getService(IZBlogAppServiceIDs.ACCOUNT_STORE_SERVICE_ID)
        self.accounts = None
        self.imageList = self._createImageList()

        self.refresh()
    # end __init__()

    def _createImageList(self):
        # FIXME (EPW) Move account and blog icons to a common area and use from there (also chnage navigator)
        registry = getResourceRegistry()
        imgList = ZMappedImageList()
        imgList.addImage(u"account", registry.getBitmap(u"images/perspectives/standard/navigator/account.png")) #$NON-NLS-1$ #$NON-NLS-2$

        return imgList
    # end _createImageList

    def refresh(self):
        self.accounts = []
        self.accounts.append(ZUnpublishedAccount())
        for account in self.accountStore.getAccounts():
            self.accounts.append(account)
    # end refresh()

    def getImageList(self):
        return self.imageList
    # end getImageList()

    def getNumColumns(self):
        return 1
    # end getNumColumns()

    def getNumRows(self):
        return len(self.accounts)
    # end getNumRows()

    def getColumnInfo(self, columnIndex): #@UnusedVariable
        return (_extstr(u"accountbrowser.Accounts"), None, None, ZListViewEx.COLUMN_LOCKED | ZListViewEx.COLUMN_RELATIVE, 100) #$NON-NLS-1$
    # end getColumnInfo()

    def getRowText(self, rowIndex, columnIndex): #@UnusedVariable
        return self.accounts[rowIndex].getName()
    # end getRowText()

    def getRowImage(self, rowIndex, columnIndex): #@UnusedVariable
        return self.imageList[u"account"] #$NON-NLS-1$
    # end getRowImage()

    def getAccountAtIndex(self, index):
        return self.accounts[index]
    # end getAccountAtIndex()

# end ZAccountListProvider


# ------------------------------------------------------------------------------
# Implements the first of three views in the Browse perspective.  This view
# presents the user with a list of Blogs found in the app.
# ------------------------------------------------------------------------------
class ZAccountBrowseView(ZView, IZAccountStoreListener):

    def __init__(self, parent):
        ZView.__init__(self, parent, wx.ID_ANY)

        self._createWidgets()
        self._layoutWidgets()
        self._populateWidgets()
        self._bindWidgetEvents()

        self._registerAsAccountListener()
    # end __init__()

    def _createWidgets(self):
        self.accountListProvider = ZAccountListProvider()
        self.accountListView = ZListViewEx(self.accountListProvider, self)
    # end _createWidgets()

    def _layoutWidgets(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.accountListView, 1, wx.EXPAND)

        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        self.Layout()
    # end _layoutWidgets()

    def _populateWidgets(self):
        pass
    # end _populateWidgets()

    def _bindWidgetEvents(self):
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onAccountSelected, self.accountListView)
        self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.onAccountRightClick, self.accountListView)
        self._bindRefreshEvent(self.onZoundryRefresh)
    # end _bindWidgetEvents()

    def onZoundryRefresh(self, event):
        self.accountListView.refresh()
        event.Skip()
    # end onZoundryRefresh()

    def onAccountRightClick(self, event):
        account = self._getSelectedAccount()
        if account is not None:
            menu = self._createAccountCtxMenu(account)
            self.PopupMenu(menu)
            menu.Destroy()
        event.Skip()
    # end onAccountRightClick()

    def onAccountSelected(self, event):
        account = self._getSelectedAccount()
        if account is not None:
            selection = None
            if account.getId() == -1:
                selection = ZViewSelection(IZViewSelectionTypes.UNPUBLISHED_ACCOUNT_SELECTION, None)
            else:
                selection = ZViewSelection(IZViewSelectionTypes.ACCOUNT_SELECTION, account.getId())
            fireViewSelectionEvent(selection, self)
        else:
            fireViewUnselectionEvent()
        event.Skip()
    # end onAccountSelected()

    def onAccountAdded(self, account): #@UnusedVariable
        self.accountListProvider.refresh()
        fireRefreshEvent(self)
    # end onAccountAdded()

    def onAccountDeleted(self, account): #@UnusedVariable
        if self._getSelectedAccount().getId() == account.getId():
            selection = ZViewSelection(IZViewSelectionTypes.UNPUBLISHED_ACCOUNT_SELECTION, None)
            fireViewSelectionEvent(selection, self)

        self.accountListProvider.refresh()
        fireRefreshEvent(self)
    # end onAccountDeleted()

    def _createAccountCtxMenu(self, account):
        menuContext = ZAccountMenuActionContext(self, account)
        menuModel = ZBlogAccountMenuModel()
        provider = ZModelBasedMenuContentProvider(menuModel, menuContext)
        eventHandler = ZModelBasedMenuEventHandler(menuModel, menuContext)
        return ZMenu(self, menuModel.getRootNode(), provider, eventHandler)
    # end _createAccountCtxMenu()

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

    def _getSelectedAccount(self):
        itemIndexes = self.accountListView.getSelection()
        if itemIndexes:
            itemIndex = itemIndexes[0]
            return self.accountListProvider.getAccountAtIndex(itemIndex)
        return None
    # end _getSelectedAccount()

# end ZAccountBrowseView
