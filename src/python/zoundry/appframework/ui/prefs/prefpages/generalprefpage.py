from zoundry.appframework.ui.prefs.appprefsdialog import ZApplicationPreferencesPrefPage
import wx

# ------------------------------------------------------------------------------------
# A user preference page impl for the General user prefs section.
# ------------------------------------------------------------------------------------
class ZGeneralPreferencePage(ZApplicationPreferencesPrefPage):
    
    def __init__(self, parent):
        ZApplicationPreferencesPrefPage.__init__(self, parent)
    # end __init__()

    def createWidgets(self):
        self.label = wx.StaticText(self, wx.ID_ANY, u"") #$NON-NLS-1$
    # end createWidgets()

    def populateWidgets(self):
        pass
    # end populateWidgets()

    def layoutWidgets(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.label, 1, wx.EXPAND)
        self.SetAutoLayout(True)
        self.SetSizer(sizer)
        self.Layout()
    # end layoutWidgets()

# end ZGeneralPreferencePage
