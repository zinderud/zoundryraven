from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.ui.events.listevents import ZEVT_CHECKBOX_LIST_CHANGE
from zoundry.appframework.ui.prefs.appprefsdialog import ZApplicationPreferencesPrefPage
from zoundry.appframework.ui.prefs.appprefsdialog import ZUserPreferencesSession
from zoundry.appframework.ui.widgets.controls.listex import ZCheckBoxListViewWithButtons
from zoundry.blogapp.constants import IZBlogAppUserPrefsKeys
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.ui.common.pubdatawidgets import ZPingListContentProvider
from zoundry.blogapp.ui.util.pingsiteutil import deserializePingSiteList
from zoundry.blogapp.ui.util.pingsiteutil import serializePingSiteList
import wx


# ------------------------------------------------------------------------------------
# A session used by the blog publishing pref page.
# ------------------------------------------------------------------------------------
class ZBlogPublishingPrefPageSession(ZUserPreferencesSession):

    def __init__(self, prefPage, prefs):
        ZUserPreferencesSession.__init__(self, prefPage, prefs)
    # end __init__()

    def getSelectedPingSites(self):
        sitesStr = self.getUserPreference(IZBlogAppUserPrefsKeys.SP_PING_SITES, u"") #$NON-NLS-1$
        return deserializePingSiteList(sitesStr)
    # end getSelectedPingSites()

    def setSelectedPingSites(self, sites):
        sitesStr = serializePingSiteList(sites)
        self.setUserPreference(IZBlogAppUserPrefsKeys.SP_PING_SITES, sitesStr)
    # end setSelectedPingSites()

# end ZBlogPublishingPrefPageSession


# ------------------------------------------------------------------------------
# A user preference page impl for the Ping Sites user prefs section.
# ------------------------------------------------------------------------------
class ZPingSitesPreferencePage(ZApplicationPreferencesPrefPage):

    def __init__(self, parent):
        ZApplicationPreferencesPrefPage.__init__(self, parent)
    # end __init__()

    def _createSession(self):
        return ZBlogPublishingPrefPageSession(self, getApplicationModel().getUserProfile().getPreferences())
    # end _createSession()

    def createWidgets(self):
        self.staticBox = wx.StaticBox(self, wx.ID_ANY, _extstr(u"pingsitesprefpage.Ping_Sites")) #$NON-NLS-1$
        self.contentProvider = ZPingListContentProvider()
        self.pingSites = ZCheckBoxListViewWithButtons(self.contentProvider, self, wx.ID_ANY)
    # end createWidgets()

    def bindWidgetEvents(self):
        self.Bind(ZEVT_CHECKBOX_LIST_CHANGE, self.onCheckListChange, self.pingSites)
    # end bindWidgetEvents()

    def populateWidgets(self):
        self.contentProvider.setSelectedPingSites(self._getSession().getSelectedPingSites())
        self.pingSites.refresh()
    # end populateWidgets()

    def layoutWidgets(self):
        box = wx.StaticBoxSizer(self.staticBox, wx.VERTICAL)
        box.Add(self.pingSites, 1, wx.EXPAND | wx.ALL, 8)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddSizer(box, 1, wx.EXPAND | wx.ALL, 5)
        self.SetAutoLayout(True)
        self.SetSizer(sizer)
        self.Layout()
    # end layoutWidgets()

    def onCheckListChange(self, event):
        sites = self.contentProvider.getSelectedPingSites()
        self._getSession().setSelectedPingSites(sites)
        event.Skip()
    # end onCheckListChange()

# end ZPingSitesPreferencePage
