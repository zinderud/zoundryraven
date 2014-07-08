from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.ui.actions.toolbaraction import ZDropDownToolBarAction
from zoundry.appframework.ui.actions.toolbaraction import ZToolBarAction
from zoundry.appframework.ui.widgets.controls.common.menu.menumodel import ZPluginMenuBarModel
from zoundry.appframework.ui.widgets.dialogs.standarddialogs import ZShowYesNoMessage
from zoundry.appframework.util.osutilfactory import getOSUtil
from zoundry.blogapp.constants import IZBlogAppServiceIDs
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.services.datastore.blogdocumentimpl import ZBlogDocument
from zoundry.blogapp.ui.actions.blog.blogactions import ZDownloadRecentBlogPostsActionBase
from zoundry.blogapp.ui.editors.editorwin import getEditorWindow
from zoundry.blogapp.ui.menus.main.file_new import ZNewBlogSiteMenuAction
from zoundry.blogapp.ui.menus.main.file_new import ZNewMediaStorageMenuAction
from zoundry.blogapp.ui.util.blogutil import createDefaultPubMetaData
from zoundry.blogapp.ui.util.blogutil import createDefaultPubMetaDataForBlog
from zoundry.blogapp.ui.util.blogutil import getBlogFromIds
from zoundry.blogapp.ui.util.blogutil import getBlogPostUrl
from zoundry.blogapp.ui.util.publisherutil import ZDeleteEntryUiUtil
from zoundry.blogapp.ui.util.publisherutil import ZPublishEntryUiUtil
from zoundry.blogapp.ui.views.viewsel import IZViewSelectionTypes

# ------------------------------------------------------------------------------
# Toolbar action for the "Write" toolbar item in the Standard Perspective.
# ------------------------------------------------------------------------------
class ZWriteToolBarAction(ZToolBarAction):

    VALID_TYPES = [
            IZViewSelectionTypes.BLOG_SELECTION,
            IZViewSelectionTypes.BLOG_IMAGES_SELECTION,
            IZViewSelectionTypes.BLOG_LINKS_SELECTION,
            IZViewSelectionTypes.BLOG_POSTS_SELECTION,
            IZViewSelectionTypes.BLOG_TAGS_SELECTION,
            IZViewSelectionTypes.BLOG_EDITED_SELECTION,
    ]

    def __init__(self):
        self.accountStore = None
    # end __init__()

    def getAccountStore(self):
        if self.accountStore is None:
            self.accountStore = getApplicationModel().getService(IZBlogAppServiceIDs.ACCOUNT_STORE_SERVICE_ID)
        return self.accountStore
    # end getAccountStore()

    def isEnabled(self, context): #@UnusedVariable
        # The "Write" toolbar is always active.
        return True
    # end isEnabled()

    def runAction(self, actionContext):
        viewSelection = actionContext.getViewSelection()
        document = ZBlogDocument()
        pubMetaData = self._createPubMetaData(viewSelection)
        if pubMetaData:
            document.addPubMetaData(pubMetaData)

        editorWindow = getEditorWindow()
        editorWindow.openDocument(document)
        editorWindow.Show()
    # end runAction()

    def _createPubMetaData(self, selection):
        if selection is not None and selection.getType() in ZWriteToolBarAction.VALID_TYPES:
            (accountId, blogId) = selection.getData()
            if blogId is not None:
                return createDefaultPubMetaData(accountId, blogId)

        accountStore = getApplicationModel().getService(IZBlogAppServiceIDs.ACCOUNT_STORE_SERVICE_ID)
        accounts = accountStore.getAccounts()
        if accounts and len(accounts) == 1:
            account = accounts[0]
            blogs = account.getBlogs()
            if blogs and len(blogs) == 1:
                blog = blogs[0]
                return createDefaultPubMetaDataForBlog(blog)

        return None
    # end _createPubMetaData()

# end ZWriteToolBarAction


# ------------------------------------------------------------------------------
# Toolbar action for the "New Blog Account" toolbar item in the Standard Perspective.
# ------------------------------------------------------------------------------
class ZNewAccountToolBarAction(ZToolBarAction, ZNewBlogSiteMenuAction):

    def runAction(self, actionContext):
        ZNewBlogSiteMenuAction.runAction(self, actionContext)
    # end runAction()

# end ZNewAccountToolBarAction


# ------------------------------------------------------------------------------
# Toolbar action for the "New Media Storage" toolbar item in the Standard Perspective.
# ------------------------------------------------------------------------------
class ZNewMediaStorageToolBarAction(ZToolBarAction, ZNewMediaStorageMenuAction):

    def runAction(self, actionContext):
        ZNewMediaStorageMenuAction.runAction(self, actionContext)
    # end runAction()

# end ZNewMediaStorageToolBarAction


# ------------------------------------------------------------------------------
# Toolbar action for the "Delete" toolbar item in the Standard Perspective.
# ------------------------------------------------------------------------------
class ZDeleteToolBarAction(ZToolBarAction):

    VALID_TYPES = [ IZViewSelectionTypes.ACCOUNT_SELECTION, IZViewSelectionTypes.DOCUMENT_SELECTION ]

    def isEnabled(self, context): #@UnusedVariable
        selection = context.getViewSelection()
        return selection is not None and (selection.getType() in ZDeleteToolBarAction.VALID_TYPES)
    # end isEnabled()

    def runAction(self, actionContext):
        window = actionContext.getParentWindow()
        documentSelection = actionContext.getViewSelection()
        if documentSelection.getType() == IZViewSelectionTypes.DOCUMENT_SELECTION:
            (zblog, zblogDocument) = documentSelection.getData()
            docList = [zblogDocument]
            ZDeleteEntryUiUtil().deletePosts(window, zblog, docList)
        elif documentSelection.getType() == IZViewSelectionTypes.ACCOUNT_SELECTION:
            accountId = documentSelection.getData()
            if accountId:
                accountStore = getApplicationModel().getService(IZBlogAppServiceIDs.ACCOUNT_STORE_SERVICE_ID)
                account = accountStore.getAccountById(accountId)
                if account is not None and ZShowYesNoMessage(window, _extstr(u"accountprefsdialog.DeleteAccountNamed") % account.getName(), _extstr(u"accountprefsdialog.DeleteAccount")): #$NON-NLS-2$ #$NON-NLS-1$
                    accountStore.removeAccount(account)
    # end runAction()

# end ZDeleteToolBarAction


# ------------------------------------------------------------------------------
# Toolbar action for the "Publish" toolbar item in the Standard Perspective.
# ------------------------------------------------------------------------------
class ZPublishToolBarAction(ZToolBarAction):

    def isEnabled(self, context): #@UnusedVariable
        selection = context.getViewSelection()
        return selection is not None and selection.getType() == IZViewSelectionTypes.DOCUMENT_SELECTION
    # end isEnabled()

    def runAction(self, actionContext):
        window = actionContext.getParentWindow()
        documentSelection = actionContext.getViewSelection()
        (zblog, zblogDocument) = documentSelection.getData()

        # Reload the document content, in case it has changed since the view
        # selection event was fired.
        docId = zblogDocument.getId()
        zblogDocument = getApplicationModel().getService(IZBlogAppServiceIDs.DATA_STORE_SERVICE_ID).getDocument(docId)

        # FIXME (PJ) check if doc already opened in editor. Warn user if already in edit mode!
        ZPublishEntryUiUtil().publishPost(window, zblog, zblogDocument)
    # end runAction()

# end ZPublishToolBarAction


# ------------------------------------------------------------------------------
# Toolbar action for the "Download" toolbar item in the Standard Perspective.
# ------------------------------------------------------------------------------
class ZDownloadToolBarAction(ZDownloadRecentBlogPostsActionBase, ZDropDownToolBarAction):

    def __init__(self):
        self.menuModel = None
    # end __init__

    def isEnabled(self, context): #@UnusedVariable
        return context.getBlog() is not None
    # end isEnabled()

    def runAction(self, actionContext):
        self._runDownloadBlogPostsAction(actionContext)
    # end runAction()

    def _createMenuModel(self, toolBarActionContext): #@UnusedVariable
        if self.menuModel is None:
            self.menuModel = ZPluginMenuBarModel(u"zoundry.blogapp.ui.core.menu.perspective.all.blogmenu.downloadrecent") #$NON-NLS-1$
        return self.menuModel
    # end _createMenuModel()

# end ZDownloadToolBarAction


# ------------------------------------------------------------------------------
# Toolbar action for the "View (online)" toolbar item in the Standard Perspective.
# ------------------------------------------------------------------------------
class ZViewOnlineToolBarAction(ZToolBarAction):

    def __init__(self):
        self.enabledTypes = [ IZViewSelectionTypes.BLOG_SELECTION, IZViewSelectionTypes.LINK_SELECTION, IZViewSelectionTypes.IMAGE_SELECTION ]
    # end __init__()

    def isEnabled(self, context): #@UnusedVariable
        selection = context.getViewSelection()
        if selection is None:
            return False
        type = selection.getType()
        if type in self.enabledTypes:
            return True
        if type == IZViewSelectionTypes.DOCUMENT_SELECTION:
            (blog, document) = selection.getData() #@UnusedVariable
            return blog is not None
        return False
    # end isEnabled()

    def runAction(self, actionContext):
        selection = actionContext.getViewSelection()
        url = None
        if selection.getType() == IZViewSelectionTypes.BLOG_SELECTION:
            (accountId, blogId) = selection.getData()
            blog = getBlogFromIds(accountId, blogId)
            url = blog.getUrl()
        elif selection.getType() == IZViewSelectionTypes.DOCUMENT_SELECTION:
            (blog, document) = selection.getData()
            url = getBlogPostUrl(document, blog.getId())
        elif selection.getType() == IZViewSelectionTypes.LINK_SELECTION:
            url = selection.getData()[1].getUrl()
        elif selection.getType() == IZViewSelectionTypes.IMAGE_SELECTION:
            url = selection.getData()[1].getUrl()

        if url is not None:
            getOSUtil().openUrlInBrowser(url)
    # end runAction()

# end ZViewOnlineToolBarAction

