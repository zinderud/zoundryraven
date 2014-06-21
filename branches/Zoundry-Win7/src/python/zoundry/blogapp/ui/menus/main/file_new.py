from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.ui.actions.menuaction import ZMenuAction
from zoundry.blogapp.constants import IZBlogAppServiceIDs
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.services.datastore.blogdocumentimpl import ZBlogDocument
from zoundry.blogapp.ui.editors.editorwin import getEditorWindow
from zoundry.blogapp.ui.util.blogutil import createDefaultPubMetaDataForBlog
from zoundry.blogapp.ui.util.mediastorageutil import ZMediaStorageUtil
from zoundry.blogapp.ui.util.publisherutil import ZNewPublisherSiteUiUtil

# ------------------------------------------------------------------------------
# This is the action implementation for the File->New->Blog Post main menu item.
# ------------------------------------------------------------------------------
class ZNewBlogPostMenuAction(ZMenuAction):

    def getDisplayName(self):
        return _extstr(u"file_new._BlogPost") #$NON-NLS-1$
    # end getDisplayName()

    def getDescription(self):
        return _extstr(u"file_new.BlogPostDescription") #$NON-NLS-1$
    # end getDescription()

    def runAction(self, actionContext): #@UnusedVariable
        document = self._createDocument(actionContext)
        editorWindow = getEditorWindow()
        editorWindow.openDocument(document)
        editorWindow.Show()
    # end runAction()

    def _createDocument(self, actionContext): #@UnusedVariable
        document = ZBlogDocument()

        accountStore = getApplicationModel().getService(IZBlogAppServiceIDs.ACCOUNT_STORE_SERVICE_ID)
        accounts = accountStore.getAccounts()
        if accounts and len(accounts) == 1:
            account = accounts[0]
            blogs = account.getBlogs()
            if blogs and len(blogs) == 1:
                blog = blogs[0]
                document.addPubMetaData(createDefaultPubMetaDataForBlog(blog))

        return document
    # end _createDocument()

# end ZNewBlogPostMenuAction


# ------------------------------------------------------------------------------
# This is the action implementation for the File->New->Media Storage main menu
# item.
# ------------------------------------------------------------------------------
class ZNewMediaStorageMenuAction(ZMenuAction):

    def getDisplayName(self):
        return _extstr(u"file_new._MediaStorage") #$NON-NLS-1$
    # end getDisplayName()

    def getDescription(self):
        return _extstr(u"file_new.MediaStorageDescription") #$NON-NLS-1$
    # end getDescription()

    def runAction(self, actionContext):
        ZMediaStorageUtil().createNewMediaStorage(actionContext.getParentWindow())
    # end runAction()

# end ZNewMediaStorageMenuAction


# ------------------------------------------------------------------------------
# Action implementation for the File->New->BlogSite
# ------------------------------------------------------------------------------
class ZNewBlogSiteMenuAction(ZMenuAction):

    def getDisplayName(self):
        return _extstr(u"file_new._BlogAccount") #$NON-NLS-1$
    # end getDisplayName()

    def getDescription(self):
        return _extstr(u"file_new.BlogAccountDescription") #$NON-NLS-1$
    # end getDescription()

    def runAction(self, actionContext):
        ZNewPublisherSiteUiUtil().createNewSite( actionContext.getParentWindow() )
    # end runAction()

# end ZNewBlogSiteMenuAction


class ZTestNewBlogSiteMenuAction(ZMenuAction):

    def getDisplayName(self):
        return u"&Test Blog Account..." #$NON-NLS-1$
    # end getDisplayName()

    def getDescription(self):
        return u"Test blog account creation." #$NON-NLS-1$
    # end getDescription()

    def runAction(self, actionContext):
        ZNewPublisherSiteUiUtil().createTestAccount( actionContext.getParentWindow() )
    # end runAction()

# end ZNewBlogSiteMenuAction
