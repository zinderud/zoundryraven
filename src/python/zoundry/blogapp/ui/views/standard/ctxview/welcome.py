from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.global_services import getResourceRegistry
from zoundry.appframework.ui.actions.menuaction import ZMenuActionContext
from zoundry.appframework.ui.widgets.controls.html import ZHTMLControl
from zoundry.blogapp.constants import IZBlogAppActionIDs
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.ui.views.boxedview import ZBoxedView
from zoundry.blogapp.util.viewutil import loadStaticHtml
import wx

# --------------------------------------------------------------------------------------
# This class implements the Standard Perspective's ContextInfo View when the user has
# selected nothing.  When the selection is nothing, then a Welcome page is shown.  The
# welcome page will have some Getting Started type info on it.  Currently static, this
# page may be dynamic depending on what the user currently has configured.
# --------------------------------------------------------------------------------------
class ZWelcomeView(ZBoxedView):

    def __init__(self, parent):
        ZBoxedView.__init__(self, parent)
        
        actionReg = getApplicationModel().getActionRegistry()
        self.newAccountAction = actionReg.findAction(IZBlogAppActionIDs.NEW_BLOG_ACCOUNT_ACTION)
        self.writePostAction = actionReg.findAction(IZBlogAppActionIDs.NEW_BLOG_POST_ACTION)
    # end __init__()

    def _getHeaderBitmap(self):
        return getResourceRegistry().getBitmap(u"images/perspectives/standard/welcome.png") #$NON-NLS-1$
    # end _getHeaderBitmap()

    def _getHeaderLabel(self):
        return _extstr(u"welcome.GettingStarted") #$NON-NLS-1$
    # end _getHeaderLabel()

    def _createHeaderWidgets(self, parent, widgetList):
        pass
    # end _createHeaderWidgets()

    def _createContentWidgets(self, parent):
        htmlPath = getResourceRegistry().getResourcePath(u"html/perspectives/standard/contextinfo/getting_started.html") #$NON-NLS-1$
        logoPath = getResourceRegistry().getResourcePath(u"images/perspectives/standard/contextinfo/logo.png") #$NON-NLS-1$
        params = {
            u"getting_started" : _extstr(u"welcome.GettingStarted"), #$NON-NLS-1$ #$NON-NLS-2$
            u"zoundry_raven" : _extstr(u"ZoundryRaven"), #$NON-NLS-1$ #$NON-NLS-2$
            u"welcome_to_raven" : _extstr(u"welcome.WelcomeToRaven"), #$NON-NLS-1$ #$NON-NLS-2$
            u"create_account" : _extstr(u"welcome.CreateAnAccount"), #$NON-NLS-1$ #$NON-NLS-2$
            u"create_account_desc" : _extstr(u"welcome.CreateAccountDesc"), #$NON-NLS-1$ #$NON-NLS-2$
            u"write_post" : _extstr(u"welcome.WritePost"), #$NON-NLS-1$ #$NON-NLS-2$
            u"write_post_desc" : _extstr(u"welcome.WritePostDesc"), #$NON-NLS-1$ #$NON-NLS-2$
            u"publish" : _extstr(u"welcome.Publish"), #$NON-NLS-1$ #$NON-NLS-2$
            u"publish_desc" : _extstr(u"welcome.PublishDesc"), #$NON-NLS-1$ #$NON-NLS-2$
            u"logo" : logoPath, #$NON-NLS-1$
        }
        html = loadStaticHtml(htmlPath, params)

        self.htmlWidget = ZHTMLControl(parent, style = wx.NO_BORDER)
        self.htmlWidget.SetBorders(0)
        self.htmlWidget.SetPage(html)
    # end _createContentWidgets()

    def _layoutContentWidgets(self):
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.htmlWidget, 1, wx.EXPAND)
        return box
    # end _layoutContentWidgets()

    def onCreateAccount(self):
        context = ZMenuActionContext(self)
        self.newAccountAction.runAction(context)
    # end onCreateAccount()

    def onWritePost(self):
        context = ZMenuActionContext(self)
        self.writePostAction.runAction(context)
    # end onWritePost()

# end ZWelcomeView
