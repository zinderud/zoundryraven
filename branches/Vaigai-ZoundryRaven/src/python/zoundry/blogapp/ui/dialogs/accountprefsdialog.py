from zoundry.blogapp.messages import _extstr
from zoundry.appframework.constants import IZAppUserPrefsKeys
from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.global_services import getResourceRegistry
from zoundry.appframework.resources.resourceutils import ZMappedImageList
from zoundry.appframework.ui.dialogs.mixins import ZPersistentPrefsDialogMixin
from zoundry.appframework.ui.dialogs.prefs import ZDefaultPreferencePage
from zoundry.appframework.ui.dialogs.prefs import ZPreferencesDialog
from zoundry.appframework.ui.util.uiutil import ZMethodRunnable
from zoundry.appframework.ui.util.uiutil import fireUIExecEvent
from zoundry.appframework.ui.widgets.controls.tree import IZTreeViewContentProvider
from zoundry.appframework.ui.widgets.dialogs.standarddialogs import ZShowYesNoMessage
from zoundry.blogapp.models.ui.dialogs.accountmanmodel import ZAccountManagerModel
from zoundry.blogapp.services.accountstore.account import IZAccount
from zoundry.blogapp.services.accountstore.account import IZBlogAccount
from zoundry.blogapp.services.accountstore.account import IZBlogFromAccount
from zoundry.blogapp.services.accountstore.accountstore import IZAccountStoreListener
from zoundry.blogapp.ui.dialogs.accountmanpages.accountpage import ZAccountPrefsPage
from zoundry.blogapp.ui.dialogs.accountmanpages.blogpage import ZBlogPrefsPage
from zoundry.blogapp.ui.util.publisherutil import ZNewPublisherSiteUiUtil
import wx


# ------------------------------------------------------------------------------
# The tree content provider for the account manager's tree view.
# ------------------------------------------------------------------------------
class ZAccountManagerTreeProvider(IZTreeViewContentProvider):

    def __init__(self, model):
        self.model = model
        self.rootNode = object()
        self.imageList = self._createTreeImageList()
    # end __init__()

    def _createTreeImageList(self):
        registry = getResourceRegistry()
        imgList = ZMappedImageList()
        for img in [u"account", u"blog"]: #$NON-NLS-1$ #$NON-NLS-2$
            imgList.addImage(img, registry.getBitmap(u"images/perspectives/standard/navigator/%s.png" % img)) #$NON-NLS-1$

        return imgList
    # end _createTreeImageList()

    def getImageList(self):
        return self.imageList
    # end getImageList()

    def getRootNode(self):
        return self.rootNode
    # end getRootNode()

    def getChildren(self, node):
        if node == self.rootNode:
            return self.model.getAccounts()
        elif isinstance(node, IZBlogAccount):
            return node.getBlogs()
        else:
            return []
    # end getChildren()

    def getLabel(self, node):
        if node == self.rootNode:
            return u"" #$NON-NLS-1$
        elif isinstance(node, IZBlogAccount) or isinstance(node, IZBlogFromAccount):
            return node.getName()
        else:
            return unicode(node)
    # end getLabel()

    def getImageIndex(self, node):
        if isinstance(node, IZBlogAccount):
            return self.imageList[u"account"] #$NON-NLS-1$
        elif isinstance(node, IZBlogFromAccount):
            return self.imageList[u"blog"] #$NON-NLS-1$
        else:
            return -1
    # end getImageIndex()

    def getSelectedImageIndex(self, node): #@UnusedVariable
        return -1
    # end getSelectedImageIndex()

    def getBoldFlag(self, node):
        return isinstance(node, IZBlogAccount)
    # end getBoldFlag()

    def getExpandedFlag(self, node): #@UnusedVariable
        return True
    # end getExpandedFlag()

# end ZAccountManagerTreeProvider


# ------------------------------------------------------------------------------
# The Account Manager dialog.  This dialog allows the user to manage their
# accounts.
# ------------------------------------------------------------------------------
class ZAccountManagerDialog(ZPreferencesDialog, ZPersistentPrefsDialogMixin, IZAccountStoreListener):

    def __init__(self, parent, jumpTo = None):
        self.model = ZAccountManagerModel()
        self.model.getService().addListener(self)
        jumpToPageId = self._resolveJumpTo(jumpTo)

        ZPreferencesDialog.__init__(self, parent, jumpToPageId)
        ZPersistentPrefsDialogMixin.__init__(self, IZAppUserPrefsKeys.ACCOUNT_MANAGER_DIALOG, False)
    # end __init__()

    def _getHeaderTitle(self):
        return _extstr(u"accountprefsdialog.AccountManager") #$NON-NLS-1$
    # end _getHeaderTitle()

    def _getHeaderMessage(self):
        return _extstr(u"accountprefsdialog.AccountManagerDescription") #$NON-NLS-1$
    # end _getHeaderMessage()

    def _getHeaderImagePath(self):
        return u"images/dialogs/account/manager/header_image.png" #$NON-NLS-1$
    # end _getHeaderImagePath()

    def onAccountAdded(self, account): #@UnusedVariable
        self.prefsTreeView.refresh()
    # end onAccountAdded()

    def onAccountChanged(self, account): #@UnusedVariable
        self.prefsTreeView.refresh()
    # end onAccountChange()

    def onAccountDeleted(self, account): #@UnusedVariable
        self.prefsTreeView.refresh()
    # end onAccountDeleted()

    def _resolveJumpTo(self, jumpTo):
        if isinstance(jumpTo, IZBlogAccount) or isinstance(jumpTo, IZBlogFromAccount):
            return jumpTo.getId()
        else:
            return None
    # end _resolveJumpTo()

    def _resolveNodeId(self, treeNode):
        if isinstance(treeNode, IZBlogAccount) or isinstance(treeNode, IZBlogFromAccount):
            return treeNode.getId()
        else:
            return None
    # end _resolveNodeId()

    def _getDefaultPageId(self):
        userPrefs = getApplicationModel().getUserProfile().getPreferences()
        return userPrefs.getUserPreference(IZAppUserPrefsKeys.ACCOUNT_MANAGER_DIALOG + u".page-id", None) #$NON-NLS-1$
    # end _getDefaultPageId()

    def _createTreeProvider(self):
        return ZAccountManagerTreeProvider(self.model)
    # end _createTreeProvider()

    def _createTreeButtons(self, parent):
        self.addAccountButton = wx.Button(parent, wx.ID_ANY, _extstr(u"accountprefsdialog.AddAccount")) #$NON-NLS-1$
        self.removeAccountButton = wx.Button(parent, wx.ID_ANY, _extstr(u"accountprefsdialog.RemoveAccount")) #$NON-NLS-1$
        self.removeAccountButton.Enable(False)
        return [ self.addAccountButton, self.removeAccountButton ]
    # end _createTreeButtons()

    def _bindWidgetEvents(self):
        ZPreferencesDialog._bindWidgetEvents(self)
        
        self.Bind(wx.EVT_BUTTON, self.onAddAccount, self.addAccountButton)
        self.Bind(wx.EVT_BUTTON, self.onRemoveAccount, self.removeAccountButton)

        self.Bind(wx.EVT_TREE_DELETE_ITEM, self.onAccountTreeItemDeleted, self.prefsTreeView)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.onAccountTreeItemChanged, self.prefsTreeView)
    # end _bindWidgetEvents()

    def _createPrefPage(self, parent, selectedNode):
        if isinstance(selectedNode, IZBlogAccount):
            return ZAccountPrefsPage(parent, selectedNode)
        elif isinstance(selectedNode, IZBlogFromAccount):
            return ZBlogPrefsPage(parent, selectedNode)
        return ZDefaultPreferencePage(parent)
    # end _createPrefPage()

    def onAddAccount(self, event):
        ZNewPublisherSiteUiUtil().createNewSite(self)
        event.Skip()
    # end onAddAccount()

    def onRemoveAccount(self, event):
        nodes = self.prefsTreeView.getSelectedNodes()
        if nodes and isinstance(nodes[0], IZAccount):
            account = nodes[0]
            if ZShowYesNoMessage(self, _extstr(u"accountprefsdialog.DeleteAccountNamed") % account.getName(), _extstr(u"accountprefsdialog.DeleteAccount")): #$NON-NLS-2$ #$NON-NLS-1$
                self.model.deleteAccount(account)
        event.Skip()
    # end onRemoveAccount()

    def onAccountTreeItemChanged(self, event):
        self._updateButtonAndPageStates()
        event.Skip()
    # end onAccountTreeItemChanged()
    
    def onAccountTreeItemDeleted(self, event):
        fireUIExecEvent(ZMethodRunnable(self._updateButtonAndPageStates), self)
        event.Skip()
    # end onAccountTreeItemChanged()
    
    def _updateButtonAndPageStates(self):
        nodes = self.prefsTreeView.getSelectedNodes()
        if nodes and isinstance(nodes[0], IZAccount):
            self.removeAccountButton.Enable(True)
        else:
            self.removeAccountButton.Enable(False)
        # if nothing selected, make sure to change the current page
        if not nodes:
            self.currentSelection = None
            self._changePreferencePage()
    # end _updateButtonAndPageStates()
    
    def _getInitialSize(self):
        return wx.Size(550, 450)
    # end _getInitialSize()

    def _destroy(self):
        ZPreferencesDialog._destroy(self)
        
        self.model.getService().removeListener(self)
    # end _destroy()

# end ZAccountManagerDialog
