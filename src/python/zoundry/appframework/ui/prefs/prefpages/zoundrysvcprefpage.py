from zoundry.appframework.messages import _extstr
from zoundry.appframework.ui.prefs.appprefsdialog import ZApplicationPreferencesPrefPage
from zoundry.appframework.constants import IZAppUserPrefsKeys
import wx

# ------------------------------------------------------------------------------
# A user preference page impl for the Zoundry Service user prefs section.
# ------------------------------------------------------------------------------
class ZZoundryServicePreferencePage(ZApplicationPreferencesPrefPage):

    def __init__(self, parent):
        ZApplicationPreferencesPrefPage.__init__(self, parent)
    # end __init__()

    def createWidgets(self):
        self.staticBox = wx.StaticBox(self, wx.ID_ANY, _extstr(u"zoundrysvcprefpage.Zoundry_Service_Settings")) #$NON-NLS-1$
        self.zoundryIdLabel = wx.StaticText(self, wx.ID_ANY, _extstr(u"zoundrysvcprefpage.Zoundry_ID")) #$NON-NLS-1$
        self.zoundryId = wx.TextCtrl(self, wx.ID_ANY)
        descPart1 = _extstr(u"zoundrysvcprefpage.ZoundryServiceDescriptionPart1") #$NON-NLS-1$
        descPart2 = _extstr(u"zoundrysvcprefpage.ZoundryServiceDescriptionPart2") #$NON-NLS-1$
        descPart3 = _extstr(u"zoundrysvcprefpage.ZoundryServiceDescriptionPart3") #$NON-NLS-1$
        self.descriptionLabel = wx.StaticText(self, wx.ID_ANY, u"\n%s\n\n%s\n\n%s" % (descPart1, descPart2, descPart3)) #$NON-NLS-1$
    # end createWidgets()

    def populateWidgets(self):
        id = self.session.getUserPreference(IZAppUserPrefsKeys.ZOUNDRY_ID, u"") #$NON-NLS-1$
        self.zoundryId.SetValue(id)
    # end populateWidgets()

    def bindWidgetEvents(self):
        self.Bind(wx.EVT_TEXT, self.onZoundryIdChanged, self.zoundryId)
    # end bindWidgetEvents()

    def layoutWidgets(self):
        boxSizer = wx.BoxSizer(wx.HORIZONTAL)
        boxSizer.Add(self.zoundryIdLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 2)
        boxSizer.Add(self.zoundryId, 1, wx.EXPAND | wx.ALL, 2)
        
        staticBoxSizer = wx.StaticBoxSizer(self.staticBox, wx.VERTICAL)
        staticBoxSizer.AddSizer(boxSizer, 0, wx.EXPAND | wx.ALL, 2)
        staticBoxSizer.Add(self.descriptionLabel, 1, wx.EXPAND | wx.ALL, 2)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddSizer(staticBoxSizer, 1, wx.EXPAND | wx.ALL, 5)
        self.SetAutoLayout(True)
        self.SetSizer(sizer)
        self.Layout()
    # end layoutWidgets()

    def onZoundryIdChanged(self, event):
        newValue = self.zoundryId.GetValue()
        self.session.setUserPreference(IZAppUserPrefsKeys.ZOUNDRY_ID, newValue)
        self.onSessionChange()
        event.Skip()
    # end onZoundryIdChanged()

# end ZZoundryServicePreferencePage
