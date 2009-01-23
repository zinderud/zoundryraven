from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.global_services import getLoggerService
from zoundry.appframework.ui.actions.menuaction import ZMenuAction
from zoundry.appframework.ui.util.clipboardutil import setClipboardText
from zoundry.appframework.util.osutilfactory import getOSUtil
from zoundry.base.util.schematypes import ZSchemaDateTime
from zoundry.blogapp.constants import IZBlogAppServiceIDs
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.ui.editors.editorwin import getEditorWindow
from zoundry.blogapp.ui.util.blogutil import getBlogFromBlogInfo
from zoundry.blogapp.ui.util.publisherutil import ZDeleteEntryUiUtil

# ------------------------------------------------------------------------------
# Base class for blog post actions.
# ------------------------------------------------------------------------------
class ZBlogPostAction(ZMenuAction):

    def __init__(self):
        self.dataStore = None
        self.accountStore = None
    # end __init__()

    def _getDataStore(self):
        if self.dataStore is None:
            self.dataStore = getApplicationModel().getService(IZBlogAppServiceIDs.DATA_STORE_SERVICE_ID)
        return self.dataStore
    # end _getDataStore()

    def _getAccountStore(self):
        if self.accountStore is None:
            self.accountStore = getApplicationModel().getService(IZBlogAppServiceIDs.ACCOUNT_STORE_SERVICE_ID)
        return self.accountStore
    # end _getAccountStore()

# end ZBlogPostAction


# ------------------------------------------------------------------------------
# Implements the "Open" menu item for the blog post context menu.
# ------------------------------------------------------------------------------
class ZOpenBlogPostAction(ZBlogPostAction):

    def __init__(self):
        ZBlogPostAction.__init__(self)
    # end __init__()

    def getDisplayName(self):
        return _extstr(u"postactions.Edit") #$NON-NLS-1$
    # end getDisplayName()

    def getDescription(self):
        return _extstr(u"postactions.EditDescription") #$NON-NLS-1$
    # end getDescription()

    def runAction(self, actionContext):
        docIDO = actionContext.getDocumentIDO()
        docId = docIDO.getId()
        document = self._getDataStore().getDocument(docId)
        editorWindow = getEditorWindow()
        editorWindow.openDocument(document)
        editorWindow.Show()
    # end runAction()

# end ZOpenBlogPostAction


# ------------------------------------------------------------------------------
# Implements the "Open As Unpublished Copy" menu item for the blog post context 
# menu.
# ------------------------------------------------------------------------------
class ZOpenAsUnpublishedBlogPostAction(ZBlogPostAction):

    def __init__(self):
        ZBlogPostAction.__init__(self)
    # end __init__()

    def getDisplayName(self):
        return _extstr(u"postactions.OpenAsUnpublished") #$NON-NLS-1$
    # end getDisplayName()

    def getDescription(self):
        return _extstr(u"postactions.OpenAsUnpublishedDesc") #$NON-NLS-1$
    # end getDescription()

    def runAction(self, actionContext):
        docIDO = actionContext.getDocumentIDO()
        docId = docIDO.getId()
        document = self._getDataStore().getDocument(docId)
        document.setId(None)
        document.setCreationTime(ZSchemaDateTime())
        document.setLastModifiedTime(ZSchemaDateTime())
        document.setPubMetaDataList([])
        document.setBlogInfoList([])
        editorWindow = getEditorWindow()
        editorWindow.openDocument(document)
        editorWindow.Show()
    # end runAction()

# end ZOpenAsUnpublishedBlogPostAction


# ------------------------------------------------------------------------------
# Implements the "View" menu item for the blog post context menu.
# ------------------------------------------------------------------------------
class ZViewBlogPostAction(ZBlogPostAction):

    def __init__(self):
        ZBlogPostAction.__init__(self)
    # end __init__()

    def getDisplayName(self):
        return _extstr(u"postactions.View") #$NON-NLS-1$
    # end getDisplayName()

    def getDescription(self):
        return _extstr(u"postactions.ViewDescription") #$NON-NLS-1$
    # end getDescription()

    def isEnabled(self, context): #@UnusedVariable
        docIDO = context.getDocumentIDO()
        docId = docIDO.getId()
        document = self._getDataStore().getDocument(docId)
        blogInfo = self._getBlogInfo(context, document)
        if blogInfo is not None:
            pubInfo = blogInfo.getPublishInfo()
            if pubInfo is not None:
                url = pubInfo.getUrl()
                if url:
                    return True
                else:
                    getLoggerService().error(u"Pub URL for doc id '%s' was 'None'." % docId) #$NON-NLS-1$
        return False
    # end isEnabled()

    def runAction(self, actionContext):
        docIDO = actionContext.getDocumentIDO()
        docId = docIDO.getId()
        document = self._getDataStore().getDocument(docId)
        blogInfo = self._getBlogInfo(actionContext, document)
        if blogInfo is not None:
            pubInfo = blogInfo.getPublishInfo()
            if pubInfo is not None:
                url = pubInfo.getUrl()
                self._handleUrlAction(url)
    # end runAction()

    def _handleUrlAction(self, url):
        getOSUtil().openUrlInBrowser(url)
    # end _handleUrlAction()

    def _getBlogInfo(self, context, document):
        if context.getBlogId() is not None:
            return document.getBlogInfo(context.getBlogId())
        elif document.getBlogInfoList():
            return document.getBlogInfoList()[0]
        return None
    # end _getBlogInfo()

# end ZViewBlogPostAction

# ------------------------------------------------------------------------------
# Implements the "Copy Blog Post URL" menu item for the blog post context menu.
# ------------------------------------------------------------------------------
class ZCopyBlogPostUrlAction(ZViewBlogPostAction):

    def __init__(self):
        ZViewBlogPostAction.__init__(self)
    # end __init__()

    def getDisplayName(self):
        return _extstr(u"postactions.CopyPostUrl") #$NON-NLS-1$
    # end getDisplayName()

    def getDescription(self):
        return _extstr(u"postactions.CopyPostUrlDescription") #$NON-NLS-1$
    # end getDescription()


    def _handleUrlAction(self, url):
        setClipboardText(url)
    # end _handleUrlAction()

# end ZCopyBlogPostUrlAction


# ------------------------------------------------------------------------------
# Implements the "Delete" menu item for the blog post context menu.
# ------------------------------------------------------------------------------
class ZDeleteBlogPostAction(ZBlogPostAction):

    def __init__(self):
        ZBlogPostAction.__init__(self)
    # end __init__()

    def getDisplayName(self):
        return _extstr(u"postactions.Delete") #$NON-NLS-1$
    # end getDisplayName()

    def getDescription(self):
        return _extstr(u"postactions.DeleteDescription") #$NON-NLS-1$
    # end getDescription()

    def runAction(self, actionContext):
        docIDO = actionContext.getDocumentIDO()
        if docIDO is not None:
            docId = docIDO.getId()
            document = self._getDataStore().getDocument(docId)
            docList = [document]
            blog = None
            blogId = actionContext.getBlogId()
            if blogId is not None:
                blogInfo = document.getBlogInfo(blogId)
                if blogInfo is not None:
                    blog = getBlogFromBlogInfo(blogInfo)
            ZDeleteEntryUiUtil().deletePosts(actionContext.getParentWindow(), blog, docList)
    # end runAction()

    def _getBlog(self, context, document):
        blogInfo = self._getBlogInfo(context, document)
        if blogInfo is not None:
            account = self._getAccount(blogInfo.getAccountId())
            return account.getBlogById(blogInfo.getBlogId())
        return None
    # end _getBlog()

    def _getBlogInfo(self, context, document):
        if context.getBlogId() is not None:
            return document.getBlogInfo(context.getBlogId())
        return None
    # end _getBlogInfo()

    def _getAccount(self, accountId):
        return self._getAccountStore().getAccountById(accountId)
    # end _getAccount()

# end ZDeleteBlogPostAction
