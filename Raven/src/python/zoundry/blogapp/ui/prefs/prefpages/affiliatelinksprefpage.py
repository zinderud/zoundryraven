from zoundry.appframework.ui.prefs.appprefsdialog import ZApplicationPreferencesPrefPage
from zoundry.blogapp.constants import IZBlogAppUserPrefsKeys
from zoundry.blogapp.messages import _extstr
import wx

# ------------------------------------------------------------------------------
# A user preference page impl for the affiliate links prefs section.
# ------------------------------------------------------------------------------
class ZAffiliateLinksPreferencePage(ZApplicationPreferencesPrefPage):

    def __init__(self, parent):
        ZApplicationPreferencesPrefPage.__init__(self, parent)
    # end __init__()

    def createWidgets(self):
        self.staticBox = wx.StaticBox(self, wx.ID_ANY, _extstr(u"affiliatelinksprefpage.Affiliate_Links")) #$NON-NLS-1$
        self.affiliateLinksCB = wx.CheckBox(self, wx.ID_ANY, _extstr(u"affiliatelinksprefpage.DontTouchLinks")) #$NON-NLS-1$
        descPart1 = _extstr(u"affiliatelinksprefpage.AffiliateLinksDesc1") #$NON-NLS-1$
        descPart2 = _extstr(u"affiliatelinksprefpage.AffiliateLinksDesc2") #$NON-NLS-1$
        descPart3 = _extstr(u"affiliatelinksprefpage.AffiliateLinksDesc3") #$NON-NLS-1$
        self.descriptionLabel = wx.StaticText(self, wx.ID_ANY, u"\n%s\n\n%s\n\n%s" % (descPart1, descPart2, descPart3)) #$NON-NLS-1$
    # end createWidgets()

    def populateWidgets(self):
        autoCreateLinks = self.session.getUserPreferenceBool(IZBlogAppUserPrefsKeys.AUTO_CONVERT_AFFILIATE_LINKS, True)
        self.affiliateLinksCB.SetValue(not autoCreateLinks)
    # end populateWidgets()

    def bindWidgetEvents(self):
        self.Bind(wx.EVT_CHECKBOX, self.onAffiliateLinksChanged, self.affiliateLinksCB)
    # end bindWidgetEvents()

    def layoutWidgets(self):
        staticBoxSizer = wx.StaticBoxSizer(self.staticBox, wx.VERTICAL)
        staticBoxSizer.Add(self.affiliateLinksCB, 0, wx.EXPAND | wx.ALL, 3)
        staticBoxSizer.Add(self.descriptionLabel, 1, wx.EXPAND | wx.ALL, 3)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddSizer(staticBoxSizer, 1, wx.EXPAND | wx.ALL, 5)
        self.SetAutoLayout(True)
        self.SetSizer(sizer)
        self.Layout()
    # end layoutWidgets()

    def onAffiliateLinksChanged(self, event):
        newValue = self.affiliateLinksCB.IsChecked()
        self.session.setUserPreference(IZBlogAppUserPrefsKeys.AUTO_CONVERT_AFFILIATE_LINKS, not newValue)
        self.onSessionChange()
        event.Skip()
    # end onAffiliateLinksChanged()

# end ZAffiliateLinksPreferencePage
