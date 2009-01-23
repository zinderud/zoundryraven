from wx._controls import EVT_TEXT
from zoundry.appframework.ui.prefs.appprefsdialog import ZApplicationPreferencesPrefPage
from zoundry.appframework.ui.widgets.controls.validating.standard.textctrl import ZValidatingTextCtrl
from zoundry.appframework.ui.widgets.controls.validating.validatingctrl import ZBaseControlValidator
import wx

class ZValue1Validator(ZBaseControlValidator):

    def __init__(self):
        ZBaseControlValidator.__init__(self)
    # end __init__()

    def _isValid(self, value):
        if not value:
            return self._setReason(u"Value1 cannot be empty.") #$NON-NLS-1$

        return True
    # end _isValid()

# end ZValue1Validator

class ZValue2Validator(ZBaseControlValidator):

    def __init__(self):
        ZBaseControlValidator.__init__(self)
    # end __init__()

    def _isValid(self, value):
        if value != u"VALUE2": #$NON-NLS-1$
            return self._setReason(u"Value2 must be 'VALUE2'.") #$NON-NLS-1$

        return True
    # end _isValid()

# end ZValue2Validator


class ZTestPreferencePage(ZApplicationPreferencesPrefPage):

    def __init__(self, parent):
        ZApplicationPreferencesPrefPage.__init__(self, parent)
    # end __init__()

    def createWidgets(self):
        self.label1 = wx.StaticText(self, wx.ID_ANY, u"Label 1:") #$NON-NLS-1$
        self.value1 = ZValidatingTextCtrl(ZValue1Validator(), self)
        self.label2 = wx.StaticText(self, wx.ID_ANY, u"Label 2:") #$NON-NLS-1$
        self.value2 = ZValidatingTextCtrl(ZValue2Validator(), self)

        self._bindEvents()
    # end createWidgets()

    def populateWidgets(self):
        value1 = self.userPrefs.getUserPreference(u"zoundry.test.pref.value1", u"") #$NON-NLS-1$ #$NON-NLS-2$
        value2 = self.userPrefs.getUserPreference(u"zoundry.test.pref.value2", u"") #$NON-NLS-1$ #$NON-NLS-2$

        self.value1.SetValue(value1)
        self.value2.SetValue(value2)
    # end populateWidgets()

    def layoutWidgets(self):
        sizer = wx.FlexGridSizer(3, 2, 5, 5)
        sizer.AddGrowableCol(1)
        sizer.Add(self.label1, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        sizer.Add(self.value1, 0, wx.EXPAND | wx.RIGHT, 5)
        sizer.Add(self.label2, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        sizer.Add(self.value2, 0, wx.EXPAND | wx.RIGHT, 5)
        self.SetAutoLayout(True)
        self.SetSizer(sizer)
        self.Layout()
    # end layoutWidgets()

    def _bindEvents(self):
        self.Bind(EVT_TEXT, self.onValue1Change, self.value1)
        self.Bind(EVT_TEXT, self.onValue2Change, self.value2)

        self._bindValidatingWidget(self.value1)
        self._bindValidatingWidget(self.value2)
    # end _bindEvents()

    def onValue1Change(self, event): #@UnusedVariable
        self.userPrefs.setUserPreference(u"zoundry.test.pref.value1", self.value1.GetValue()) #$NON-NLS-1$
    # end onValue1Change

    def onValue2Change(self, event): #@UnusedVariable
        self.userPrefs.setUserPreference(u"zoundry.test.pref.value2", self.value2.GetValue()) #$NON-NLS-1$
    # end onValue2Change

# end ZTestPreferencePage
