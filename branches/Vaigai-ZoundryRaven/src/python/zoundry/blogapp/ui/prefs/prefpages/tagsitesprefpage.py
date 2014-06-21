from zoundry.blogapp.ui.util.tagsiteutil import serializeTagSiteList
from zoundry.blogapp.ui.util.tagsiteutil import deserializeTagSiteList
from zoundry.appframework.ui.widgets.controls.listex import ZCheckBoxListViewWithButtons
from zoundry.blogapp.ui.common.pubdatawidgets import ZTagspaceListContentProvider
from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.ui.prefs.appprefsdialog import ZApplicationPreferencesPrefPage
from zoundry.blogapp.constants import IZBlogAppUserPrefsKeys
from zoundry.appframework.ui.prefs.appprefsdialog import ZUserPreferencesSession
from zoundry.blogapp.messages import _extstr
import wx
from zoundry.appframework.ui.events.listevents import ZEVT_CHECKBOX_LIST_CHANGE

# ------------------------------------------------------------------------------------
# A session used by the blog publishing pref page.
# ------------------------------------------------------------------------------------
class ZTagPrefPageSession(ZUserPreferencesSession):

    def __init__(self, prefPage, prefs):
        ZUserPreferencesSession.__init__(self, prefPage, prefs)
    # end __init__()

    def getSelectedTagSites(self):
        sitesStr = self.getUserPreference(IZBlogAppUserPrefsKeys.SP_TAG_SITES, u"") #$NON-NLS-1$
        sites = deserializeTagSiteList(sitesStr)
        return sites
    # end getSelectedTagSites()

    def setSelectedTagSites(self, sites):
        sitesStr = serializeTagSiteList(sites)
        self.setUserPreference(IZBlogAppUserPrefsKeys.SP_TAG_SITES, sitesStr)
    # end setSelectedTagSites()

# end ZTagPrefPageSession

# ------------------------------------------------------------------------------
# A user preference page impl for the Ping Sites user prefs section.
# ------------------------------------------------------------------------------
class ZTagSitesPreferencePage(ZApplicationPreferencesPrefPage):

    def __init__(self, parent):
        ZApplicationPreferencesPrefPage.__init__(self, parent)
    # end __init__()

    def _createSession(self):
        return ZTagPrefPageSession(self, getApplicationModel().getUserProfile().getPreferences())
    # end _createSession()

    def createWidgets(self):
        self.staticBox = wx.StaticBox(self, wx.ID_ANY, _extstr(u"tagsitesprefpage.Tag_Sites")) #$NON-NLS-1$
        self.contentProvider = ZTagspaceListContentProvider()
        self.tagSites = ZCheckBoxListViewWithButtons(self.contentProvider, self, wx.ID_ANY)
    # end createWidgets()

    def bindWidgetEvents(self):
        self.Bind(ZEVT_CHECKBOX_LIST_CHANGE, self.onCheckListChange, self.tagSites)
    # end bindWidgetEvents()

    def populateWidgets(self):
        self.contentProvider.setSelectedTagSpaceUrls(self._getSession().getSelectedTagSites())
        self.tagSites.refresh()
    # end populateWidgets()

    def layoutWidgets(self):
        box = wx.StaticBoxSizer(self.staticBox, wx.VERTICAL)
        box.Add(self.tagSites, 1, wx.EXPAND | wx.ALL, 8)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddSizer(box, 1, wx.EXPAND | wx.ALL, 5)
        self.SetAutoLayout(True)
        self.SetSizer(sizer)
        self.Layout()
    # end layoutWidgets()

    def onCheckListChange(self, event):
        sites = self.contentProvider.getSelectedTagSpaceUrls()
        self._getSession().setSelectedTagSites(sites)
        event.Skip()
    # end onCheckListChange()

# end ZTagSitesPreferencePage