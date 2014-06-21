from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.global_services import getResourceRegistry
from zoundry.appframework.ui.widgets.controls.html import ZHTMLControl
from zoundry.blogapp.constants import IZBlogAppActionIDs
from zoundry.blogapp.constants import IZBlogAppServiceIDs
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.ui.actions.blog.blogactions import ZBlogMenuActionContext
from zoundry.blogapp.ui.events.viewevents import ZEVT_VIEW_SELECTION_CHANGED
from zoundry.blogapp.ui.views.boxedview import ZBoxedView
from zoundry.blogapp.ui.views.viewsel import IZViewSelectionTypes
from zoundry.blogapp.util.viewutil import loadStaticHtml
import wx

# --------------------------------------------------------------------------------------
# This class implements the Standard Perspective's ContextInfo View when the user has
# selected a Blog in the Navigator.  When that selection is made, the blog summary
# information is shown.
# --------------------------------------------------------------------------------------
class ZContextInfoBlogSummaryView(ZBoxedView):

    def __init__(self, parent):
        self.accountStore = getApplicationModel().getService(IZBlogAppServiceIDs.ACCOUNT_STORE_SERVICE_ID)
        self.blog = None

        ZBoxedView.__init__(self, parent)
    # end __init__()

    def _getHeaderBitmap(self):
        return getResourceRegistry().getBitmap(u"images/perspectives/standard/blog_summary.png") #$NON-NLS-1$
    # end _getHeaderBitmap()

    def _getHeaderLabel(self):
        return _extstr(u"blogsummary.BlogSummary") #$NON-NLS-1$
    # end _getHeaderLabel()

    def _createHeaderWidgets(self, parent, widgetList):
        pass
    # end _createHeaderWidgets()

    def _createContentWidgets(self, parent):
        self.htmlWidget = ZHTMLControl(parent, style = wx.NO_BORDER)
        self.htmlWidget.SetBorders(0)
        self.htmlWidget.SetPage(u"<html />") #$NON-NLS-1$
    # end _createContentWidgets()

    def _layoutContentWidgets(self):
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.htmlWidget, 1, wx.EXPAND)
        return box
    # end _layoutContentWidgets()

    def refreshContent(self, selection):
        (accountId, blogId) = selection.getData()
        account = self.accountStore.getAccountById(accountId)
        self.blog = account.getBlogById(blogId)
        self._populateWidgets()
    # end refreshContent()

    def _bindWidgetEvents(self):
        ZBoxedView._bindWidgetEvents(self)

        self.Bind(ZEVT_VIEW_SELECTION_CHANGED, self.onSelectionChanged)
    # end _bindWidgetEvents()

    def _populateWidgets(self):
        params = {
              u"blog_summary" : _extstr(u"blogsummary.BlogSummary"), #$NON-NLS-1$ #$NON-NLS-2$
              u"zoundry_raven" : _extstr(u"ZoundryRaven"), #$NON-NLS-1$ #$NON-NLS-2$
              u"configure_blog" : _extstr(u"blogsummary.ConfigureBlog"), #$NON-NLS-1$ #$NON-NLS-2$
              u"configure_blog_desc" : _extstr(u"blogsummary.ConfigureBlogDesc"), #$NON-NLS-1$ #$NON-NLS-2$
              u"new_post" : _extstr(u"blogsummary.NewPost"), #$NON-NLS-1$ #$NON-NLS-2$
              u"new_post_desc" : _extstr(u"blogsummary.NewPostDesc"), #$NON-NLS-1$ #$NON-NLS-2$
              u"view_blog" : _extstr(u"blogsummary.ViewBlog"), #$NON-NLS-1$ #$NON-NLS-2$
              u"view_blog_desc" : _extstr(u"blogsummary.ViewBlogDesc"), #$NON-NLS-1$ #$NON-NLS-2$
              u"blog_name" : self.blog.getName(), #$NON-NLS-1$
              u"configure_imgpath" : getResourceRegistry().getImagePath(u"images/perspectives/standard/contextinfo/blog_summary/configure.png"), #$NON-NLS-1$ #$NON-NLS-2$
              u"newpost_imgpath" : getResourceRegistry().getImagePath(u"images/perspectives/standard/contextinfo/blog_summary/newpost.png"), #$NON-NLS-1$ #$NON-NLS-2$
              u"viewblog_imgpath" : getResourceRegistry().getImagePath(u"images/perspectives/standard/contextinfo/blog_summary/viewblog.png"), #$NON-NLS-1$ #$NON-NLS-2$
        }

        htmlPath = getResourceRegistry().getResourcePath(u"html/perspectives/standard/contextinfo/blog_summary.html") #$NON-NLS-1$
        html = loadStaticHtml(htmlPath, params); #$NON-NLS-1$
        self.htmlWidget.SetPage(html)
    # end _populateWidgets()

    def onSelectionChanged(self, event):
        selection = event.getSelection()
        if selection.getType() == IZViewSelectionTypes.BLOG_SELECTION:
            self.refreshContent(selection)
    # end onSelectionChanged()

    def onNewPost(self):
        self._runBlogAction(IZBlogAppActionIDs.BLOG_NEW_BLOG_POST_ACTION)
    # end onNewPost()

    def onConfigure(self):
        self._runBlogAction(IZBlogAppActionIDs.CONFIGURE_BLOG_ACTION)
    # end onConfigure()

    def onViewBlog(self):
        self._runBlogAction(IZBlogAppActionIDs.VIEW_BLOG_ACTION)
    # end onViewBlog()

    def _runBlogAction(self, actionId):
        action = getApplicationModel().getActionRegistry().findAction(actionId)
        context = ZBlogMenuActionContext(self, self.blog)
        action.runAction(context)
    # end _runBlogAction()

# end ZContextInfoBlogSummaryView
