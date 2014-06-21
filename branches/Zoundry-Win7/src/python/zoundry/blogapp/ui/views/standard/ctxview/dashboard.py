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
# selected nothing.  Contains common actions such as 'create new account', 'create new
# media storage', etc.
# --------------------------------------------------------------------------------------
class ZDashboardView(ZBoxedView):

    def __init__(self, parent):
        ZBoxedView.__init__(self, parent)
        
        actionReg = getApplicationModel().getActionRegistry()
        self.newAccountAction = actionReg.findAction(IZBlogAppActionIDs.NEW_BLOG_ACCOUNT_ACTION)
        self.newStorageAction = actionReg.findAction(IZBlogAppActionIDs.NEW_MEDIA_STORAGE_ACTION)
        self.settingsAction = actionReg.findAction(IZBlogAppActionIDs.SETTINGS_ACTION)
    # end __init__()

    def _getHeaderBitmap(self):
        return getResourceRegistry().getBitmap(u"images/perspectives/standard/dashboard.png") #$NON-NLS-1$
    # end _getHeaderBitmap()

    def _getHeaderLabel(self):
        return _extstr(u"dashboard.Dashboard") #$NON-NLS-1$
    # end _getHeaderLabel()

    def _createHeaderWidgets(self, parent, widgetList):
        pass
    # end _createHeaderWidgets()

    def _createContentWidgets(self, parent):
        htmlPath = getResourceRegistry().getResourcePath(u"html/perspectives/standard/contextinfo/dashboard.html") #$NON-NLS-1$
        logoPath = getResourceRegistry().getResourcePath(u"images/perspectives/standard/contextinfo/logo.png") #$NON-NLS-1$
        params = {
            u"dashboard" : _extstr(u"dashboard.Dashboard"), #$NON-NLS-1$ #$NON-NLS-2$
            u"zoundry_raven" : _extstr(u"ZoundryRaven"), #$NON-NLS-1$ #$NON-NLS-2$
            u"new_account" : _extstr(u"dashboard.NewBlogAccount"), #$NON-NLS-1$ #$NON-NLS-2$
            u"new_account_desc" : _extstr(u"dashboard.NewBlogAccountDesc"), #$NON-NLS-1$ #$NON-NLS-2$
            u"new_media_storage" : _extstr(u"dashboard.NewMediaStorage"), #$NON-NLS-1$ #$NON-NLS-2$
            u"new_media_storage_desc" : _extstr(u"dashboard.NewMediaStorageDesc"), #$NON-NLS-1$ #$NON-NLS-2$
            u"settings" : _extstr(u"dashboard.Settings"), #$NON-NLS-1$ #$NON-NLS-2$
            u"settings_desc" : _extstr(u"dashboard.SettingsDesc"), #$NON-NLS-1$ #$NON-NLS-2$
            u"logo" : logoPath, #$NON-NLS-1$
            u"newaccount_imgpath" : getResourceRegistry().getResourcePath(u"images/perspectives/standard/contextinfo/dashboard/new_account.png"), #$NON-NLS-1$ #$NON-NLS-2$
            u"newstorage_imgpath" : getResourceRegistry().getResourcePath(u"images/perspectives/standard/contextinfo/dashboard/new_storage.png"), #$NON-NLS-1$ #$NON-NLS-2$
            u"settings_imgpath" : getResourceRegistry().getResourcePath(u"images/perspectives/standard/contextinfo/dashboard/settings.png"), #$NON-NLS-1$ #$NON-NLS-2$
        }
        html = loadStaticHtml(htmlPath, params);

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

    def onNewMediaStorage(self):
        context = ZMenuActionContext(self)
        self.newStorageAction.runAction(context)
    # end onNewMediaStorage()

    def onSettings(self):
        context = ZMenuActionContext(self)
        self.settingsAction.runAction(context)
    # end onSettings()

# end ZDashboardView
