from zoundry.appframework.ui.prefs.appprefsdialog import ZApplicationPreferencesPrefPage
from zoundry.appframework.ui.widgets.dialogs.standarddialogs import ZShowInfoMessage
from zoundry.blogapp.constants import IZUserPrefsDefaults
from zoundry.blogapp.constants import IZBlogAppUserPrefsKeys
from zoundry.blogapp.messages import _extstr
import wx

# ------------------------------------------------------------------------------------
# A user preference page impl for the General user prefs section.
# ------------------------------------------------------------------------------------
class ZTrayPreferencePage(ZApplicationPreferencesPrefPage):

    def __init__(self, parent):
        ZApplicationPreferencesPrefPage.__init__(self, parent)
    # end __init__()

    def createWidgets(self):
        self.staticBox = wx.StaticBox(self, wx.ID_ANY, _extstr(u"trayprefpage.TrayIcon")) #$NON-NLS-1$
        self.alwaysShowTrayIconCB = wx.CheckBox(self, wx.ID_ANY, _extstr(u"trayprefpage.AlwaysShowTrayIcon")) #$NON-NLS-1$
        self.hideAppWindowCB = wx.CheckBox(self, wx.ID_ANY, _extstr(u"trayprefpage.HideAppWindowOnMinimize")) #$NON-NLS-1$
    # end createWidgets()

    def bindWidgetEvents(self):
        self.Bind(wx.EVT_CHECKBOX, self.onAlwaysShowCB, self.alwaysShowTrayIconCB)
        self.Bind(wx.EVT_CHECKBOX, self.onHideWhenMinCB, self.hideAppWindowCB)
    # end bindWidgetEvents()

    def populateWidgets(self):
        isAlwaysShow = self.session.getUserPreferenceBool(IZBlogAppUserPrefsKeys.SYSTRAY_ALWAYS_SHOW, IZUserPrefsDefaults.SYSTRAY_ALWAYS_SHOW)
        isHideWhenMin = self.session.getUserPreferenceBool(IZBlogAppUserPrefsKeys.SYSTRAY_HIDE_WHEN_MINIMIZED, IZUserPrefsDefaults.SYSTRAY_HIDE_WHEN_MINIMIZED)

        self.alwaysShowTrayIconCB.SetValue(isAlwaysShow)
        self.hideAppWindowCB.SetValue(isHideWhenMin)
    # end populateWidgets()

    def layoutWidgets(self):
        boxSizer = wx.StaticBoxSizer(self.staticBox, wx.VERTICAL)
        boxSizer.Add(self.alwaysShowTrayIconCB, 0, wx.EXPAND | wx.ALL, 3)
        boxSizer.Add(self.hideAppWindowCB, 0, wx.EXPAND | wx.ALL, 3)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddSizer(boxSizer, 0, wx.EXPAND | wx.ALL, 5)
        self.SetAutoLayout(True)
        self.SetSizer(sizer)
        self.Layout()
    # end layoutWidgets()

    def onAlwaysShowCB(self, event):
        isAlwaysShow = self.alwaysShowTrayIconCB.GetValue()
        self.session.setUserPreference(IZBlogAppUserPrefsKeys.SYSTRAY_ALWAYS_SHOW, isAlwaysShow)
        event.Skip()
    # end onAlwaysShowCB()

    def onHideWhenMinCB(self, event):
        isHideApp = self.hideAppWindowCB.GetValue()
        self.session.setUserPreference(IZBlogAppUserPrefsKeys.SYSTRAY_HIDE_WHEN_MINIMIZED, isHideApp)
        event.Skip()
    # end onHideWhenMinCB()

    def apply(self):
        ZShowInfoMessage(self, _extstr(u"trayprefpage.RequiredRestartMessage"), _extstr(u"trayprefpage.RequiredRestartTitle")) #$NON-NLS-2$ #$NON-NLS-1$
        return ZApplicationPreferencesPrefPage.apply(self)
    # end apply()

# end ZTrayPreferencePage
