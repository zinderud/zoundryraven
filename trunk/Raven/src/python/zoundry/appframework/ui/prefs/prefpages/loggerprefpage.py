from zoundry.appframework.constants import IZAppServiceIDs
from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.messages import _extstr
from zoundry.appframework.ui.dialogs.prefpage import IZUserPreferencePageSession
from zoundry.appframework.ui.prefs.appprefsdialog import ZApplicationPreferencesPrefPage
import wx

# ------------------------------------------------------------------------------------
# Model for the logger user prefs page.
# ------------------------------------------------------------------------------------
class ZLoggerPreferencePageSession(IZUserPreferencePageSession):

    def __init__(self):
        self.loggerService = getApplicationModel().getService(IZAppServiceIDs.LOGGER_SERVICE_ID)
        self.enableDebug = False

        self.initFromService()
    # end __init__()

    def initFromService(self):
        self.enableDebug = self.loggerService.isDebugLoggingEnabled()
    # end initFromService()

    def isDebugLoggingEnabled(self):
        return self.enableDebug
    # end isDebugLoggingEnabled()

    def setDebugEnabled(self, enabled):
        self.enableDebug = enabled
    # end setDebugEnabled()

    def isDirty(self):
        return self.enableDebug != self.loggerService.isDebugLoggingEnabled()
    # end isDirty()

    def apply(self):
        if self.enableDebug:
            self.loggerService.enableDebugLogging()
        else:
            self.loggerService.disableDebugLogging()
    # end apply()

    def rollback(self):
        self.initFromService()
    # end rollback()

# end ZLoggerPreferencePageSession


# ------------------------------------------------------------------------------------
# A user preference page impl for the Logger user prefs section.
# ------------------------------------------------------------------------------------
class ZLoggerPreferencePage(ZApplicationPreferencesPrefPage):

    def __init__(self, parent):
        ZApplicationPreferencesPrefPage.__init__(self, parent)
    # end __init__()

    def _createSession(self):
        return ZLoggerPreferencePageSession()
    # end _createSession()

    def createWidgets(self):
        self.staticBox = wx.StaticBox(self, wx.ID_ANY, _extstr(u"loggerprefpage.LoggerSettings")) #$NON-NLS-1$
        self.logErrorsCB = wx.CheckBox(self, wx.ID_ANY, _extstr(u"loggerprefpage.LogErrors")) #$NON-NLS-1$
        self.logWarningsCB= wx.CheckBox(self, wx.ID_ANY, _extstr(u"loggerprefpage.LogWarnings")) #$NON-NLS-1$
        self.logDebugCB = wx.CheckBox(self, wx.ID_ANY, _extstr(u"loggerprefpage.LogDebuggingMessages")) #$NON-NLS-1$
    # end createWidgets()

    def populateWidgets(self):
        self.logErrorsCB.SetValue(True)
        self.logWarningsCB.SetValue(True)
        self.logErrorsCB.Enable(False)
        self.logWarningsCB.Enable(False)

        self.logDebugCB.SetValue(self.session.isDebugLoggingEnabled())
    # end populateWidgets()

    def bindWidgetEvents(self):
        self.Bind(wx.EVT_CHECKBOX, self.onDebugCB, self.logDebugCB)
    # end bindWidgetEvents()

    def layoutWidgets(self):
        boxSizer = wx.StaticBoxSizer(self.staticBox, wx.VERTICAL)
        boxSizer.Add(self.logErrorsCB, 0, wx.EXPAND | wx.ALL, 3)
        boxSizer.Add(self.logWarningsCB, 0, wx.EXPAND | wx.ALL, 3)
        boxSizer.Add(self.logDebugCB, 0, wx.EXPAND | wx.ALL, 3)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddSizer(boxSizer, 0, wx.EXPAND | wx.ALL, 5)
        self.SetAutoLayout(True)
        self.SetSizer(sizer)
        self.Layout()
    # end layoutWidgets()

    def onDebugCB(self, event):
        self.session.setDebugEnabled(event.IsChecked())
        self.getPrefsDialog().onPrefPageChange()
        event.Skip()
    # end onDebugCB()

    def isValid(self):
        return True
    # end isValid()

# end ZLoggerPreferencePage
