from zoundry.appframework.ui.actions.menuaction import ZMenuAction
from zoundry.appframework.ui.actions.menuaction import ZMenuActionContext
from zoundry.appframework.util.osutilfactory import getOSUtil
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.services.datastore.blogdocumentimpl import ZBlogDocument
from zoundry.blogapp.ui.dialogs.accountprefsdialog import ZAccountManagerDialog
from zoundry.blogapp.ui.menus.main.file_new import ZNewBlogPostMenuAction
from zoundry.blogapp.ui.templates.templatemanager import ZShowTemplateManager
from zoundry.blogapp.ui.templates.templateuiutil import doTemplateDownload
from zoundry.blogapp.ui.util.blogutil import createDefaultPubMetaDataForBlog
from zoundry.blogapp.ui.util.publisherutil import ZPublisherSiteSynchUiUtil
from zoundry.appframework.ui.widgets.dialogs.standarddialogs import ZShowWarnMessage

# ------------------------------------------------------------------------------
# An implementation of a menu action context for menu items in the ZBlog context
# menu (the menu that is displayed when a ZBlog is right-clicked).
# ------------------------------------------------------------------------------
class ZBlogMenuActionContext(ZMenuActionContext):

    def __init__(self, window, blog):
        self.blog = blog
        ZMenuActionContext.__init__(self, window)
    # end __init__()

    def getBlog(self):
        return self.blog
    # end getBlog()

# end ZBlogMenuActionContext


# ------------------------------------------------------------------------------
# The action that gets run when the user clicks on the "Configure..." menu
# option in the Blog context menu.
# ------------------------------------------------------------------------------
class ZBlogConfigureMenuAction(ZMenuAction):

    def __init__(self):
        ZMenuAction.__init__(self)
    # end __init__()

    def getDisplayName(self):
        return _extstr(u"blogactions._Settings") #$NON-NLS-1$
    # end getDisplayName()

    def getDescription(self):
        return _extstr(u"blogactions.SettingsDescription") #$NON-NLS-1$
    # end getDescription()

    def runAction(self, actionContext):
        dialog = ZAccountManagerDialog(actionContext.getParentWindow(), actionContext.getBlog())
        dialog.ShowModal()
        dialog.Destroy()
    # end runAction()

# end ZBlogConfigureMenuAction


# ------------------------------------------------------------------------------
# The action that gets run when the user clicks on the "Download Recent Posts"
# menu option in the Blog context menu.
# ------------------------------------------------------------------------------
class ZDownloadRecentBlogPostsActionBase:

    def _runDownloadBlogPostsAction(self, actionContext):
        # action ctx is either ZBlogMenuActionContext or  ZStandardPerspectiveToolBarActionContext
        numPosts = ZPublisherSiteSynchUiUtil.MAX_POSTS_DOWNLOAD
        if hasattr(self, u'getParameters') and self.getParameters(): #$NON-NLS-1$
            numPosts = self.getParameters().getIntParameter(u"numposts", ZPublisherSiteSynchUiUtil.MAX_POSTS_DOWNLOAD) #$NON-NLS-1$
        blog = actionContext.getBlog()
        if blog:
            ZPublisherSiteSynchUiUtil().downloadPosts(actionContext.getParentWindow(), blog, numPosts )
    # end _runDownloadBlogPostsAction()

# end  ZDownloadRecentBlogPostsActionBase

#---------------------------------------------------------------------------------------
class ZDownloadRecentBlogPostsMenuAction(ZDownloadRecentBlogPostsActionBase, ZMenuAction):

    def __init__(self):
        ZMenuAction.__init__(self)
    # end __init__()

    def getDisplayName(self):
        return _extstr(u"blogactions._DownloadRecentPosts") #$NON-NLS-1$
    # end getDisplayName()

    def getDescription(self):
        return _extstr(u"blogactions.DownloadRecentPostsDescription") #$NON-NLS-1$
    # end getDescription()

    def runAction(self, actionContext):
        self._runDownloadBlogPostsAction(actionContext)
    # end runAction()

# end ZDownloadRecentBlogPostsMenuAction

# ------------------------------------------------------------------------------
# Action to create a new blog post within a blog.
# ------------------------------------------------------------------------------
class ZNewPostInBlogMenuAction(ZNewBlogPostMenuAction):

    def getDisplayName(self):
        return _extstr(u"blogactions.New_Post") #$NON-NLS-1$
    # end getDisplayName()

    def _createDocument(self, actionContext):
        blog = actionContext.getBlog()
        document = ZBlogDocument()
        document.addPubMetaData(createDefaultPubMetaDataForBlog(blog))
        return document
    # end _createDocument()

# end ZNewPostInBlogMenuAction


# ------------------------------------------------------------------------------
# Action to view a blog in the browser.
# ------------------------------------------------------------------------------
class ZViewBlogAction(ZMenuAction):

    def getDisplayName(self):
        return _extstr(u"blogactions._ViewOnline") #$NON-NLS-1$
    # end getDisplayName()

    def getDescription(self):
        return _extstr(u"blogactions.ViewOnlineDescription") #$NON-NLS-1$
    # end getDescription()

    def runAction(self, actionContext):
        blog = actionContext.getBlog()
        url = blog.getUrl()
        if not url:
            msg = _extstr(u"blogactions.CouldNotDetermineURLForBlog") % blog.getName() #$NON-NLS-1$
            title = _extstr(u"blogactions.ProblemOpeningBlogURL") #$NON-NLS-1$
            ZShowWarnMessage(actionContext.getParentWindow(), msg, title)
        else:
            getOSUtil().openUrlInBrowser(url)
    # end runAction()

# end ZViewBlogAction


# ------------------------------------------------------------------------------
# Action to download a blog's template.  Uses a template fetcher to actually
# get and create the template.  See the ZTemplateFetcher class documentation for
# further details.
# ------------------------------------------------------------------------------
class ZDownloadBlogTemplateAction(ZMenuAction):

    def getDisplayName(self):
        return _extstr(u"blogactions.Download_Template") #$NON-NLS-1$
    # end getDisplayName()

    def getDescription(self):
        return _extstr(u"blogactions.DownloadTemplateDescription") #$NON-NLS-1$
    # end getDescription()

    def runAction(self, actionContext):
        blog = actionContext.getBlog()
        templateManager = ZShowTemplateManager()
        doTemplateDownload(templateManager, blog)
    # end runAction()

# end ZDownloadBlogTemplateAction
