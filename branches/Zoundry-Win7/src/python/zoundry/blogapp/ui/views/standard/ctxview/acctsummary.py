from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.global_services import getResourceRegistry
from zoundry.appframework.ui.widgets.controls.html import ZHTMLControl
from zoundry.blogapp.constants import IZBlogAppServiceIDs
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.ui.dialogs.accountprefsdialog import ZAccountManagerDialog
from zoundry.blogapp.ui.events.viewevents import ZEVT_VIEW_SELECTION_CHANGED
from zoundry.blogapp.ui.util.publisherutil import ZPublisherSiteSynchUiUtil
from zoundry.blogapp.ui.views.boxedview import ZBoxedView
from zoundry.blogapp.ui.views.viewsel import IZViewSelectionTypes
from zoundry.blogapp.util.viewutil import loadStaticHtml
import wx

# --------------------------------------------------------------------------------------
# This class implements the Standard Perspective's ContextInfo View when the user has
# selected a Blog Account in the Navigator.  When that selection is made, the account
# summary information is shown.
# --------------------------------------------------------------------------------------
class ZContextInfoAccountSummaryView(ZBoxedView):

    def __init__(self, parent):
        self.accountStore = getApplicationModel().getService(IZBlogAppServiceIDs.ACCOUNT_STORE_SERVICE_ID)
        self.account = None

        ZBoxedView.__init__(self, parent)
    # end __init__()

    def _getHeaderBitmap(self):
        return getResourceRegistry().getBitmap(u"images/perspectives/standard/account_summary.png") #$NON-NLS-1$
    # end _getHeaderBitmap()

    def _getHeaderLabel(self):
        return _extstr(u"acctsummary.AccountSummary") #$NON-NLS-1$
    # end _getHeaderLabel()

    def _createHeaderWidgets(self, parent, widgetList):
        pass
    # end _createHeaderWidgets()

    def _createContentWidgets(self, parent):
        self.htmlWidget = ZHTMLControl(parent, style = wx.NO_BORDER)
        self.htmlWidget.SetBorders(0)
    # end _createContentWidgets()

    def _layoutContentWidgets(self):
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.htmlWidget, 1, wx.EXPAND)
        return box
    # end _layoutContentWidgets()

    def refreshContent(self, selection):
        accountId = selection.getData()
        self.account = self.accountStore.getAccountById(accountId)
        self._populateWidgets()
    # end refreshContent()

    def _bindWidgetEvents(self):
        ZBoxedView._bindWidgetEvents(self)
        
        self.Bind(ZEVT_VIEW_SELECTION_CHANGED, self.onSelectionChanged)
    # end _bindWidgetEvents()

    def onSelectionChanged(self, event):
        selection = event.getSelection()
        if selection.getType() == IZViewSelectionTypes.ACCOUNT_SELECTION:
            self.refreshContent(selection)
    # end onSelectionChanged()

    def _populateWidgets(self):
        params = {
              u"account_summary" : _extstr(u"acctsummary.AccountSummary"), #$NON-NLS-1$ #$NON-NLS-2$
              u"zoundry_raven" : _extstr(u"ZoundryRaven"), #$NON-NLS-1$ #$NON-NLS-2$
              u"view_settings_desc" : _extstr(u"acctsummary.ViewSettingsDesc"), #$NON-NLS-1$ #$NON-NLS-2$
              u"refresh_account" : _extstr(u"acctsummary.RefreshDesc"), #$NON-NLS-1$ #$NON-NLS-2$
              u"view_settings" : _extstr(u"acctsummary.ViewSettings"), #$NON-NLS-1$ #$NON-NLS-2$
              u"refresh" : _extstr(u"acctsummary.Refresh"), #$NON-NLS-1$ #$NON-NLS-2$
              u"account_name" : self.account.getName(), #$NON-NLS-1$
              u"settings_imgpath" : getResourceRegistry().getImagePath(u"images/perspectives/standard/contextinfo/account_summary/settings.png"), #$NON-NLS-1$ #$NON-NLS-2$
              u"refresh_imgpath" : getResourceRegistry().getImagePath(u"images/perspectives/standard/contextinfo/account_summary/synch.png"), #$NON-NLS-1$ #$NON-NLS-2$
        }

        htmlPath = getResourceRegistry().getResourcePath(u"html/perspectives/standard/contextinfo/account_summary.html") #$NON-NLS-1$
        html = loadStaticHtml(htmlPath, params); #$NON-NLS-1$

        self.htmlWidget.SetPage(html)
    # end _populateWidgets()

    def onViewSettings(self):
        dialog = ZAccountManagerDialog(self, self.account)
        dialog.ShowModal()
        dialog.Destroy()
    # end onViewSettings()

    def onOnlineSync(self):
        ZPublisherSiteSynchUiUtil().synchronizeAccount(self, self.account)
    # end onOnlineSync()

# end ZContextInfoAccountSummaryView
