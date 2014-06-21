from zoundry.appframework.messages import _extstr
from zoundry.appframework.ui.events.ztestevents import ZEVT_ZTEST_COMPLETED
from zoundry.appframework.ui.events.ztestevents import ZEVT_ZTEST_FAILED
from zoundry.appframework.ui.widgets.controls.tpanel import ZTestProgressPanel
from zoundry.appframework.ui.widgets.dialog import ZBaseDialog
import wx


# ----------------------------------------------------------------------------------------
# This dialog is used to show the progress of an IZTest.  An IZTest is any test within
# the application - typically a test of a user's settings for something.  For example,
# the user might set up a FTP Media Storage and choose to Test their settings.  An IZTest
# instance would be created, and this dialog is used to show the progress of that test.
# ----------------------------------------------------------------------------------------
class ZTestProgressDialog(ZBaseDialog):

    def __init__(self, ztest, parent, title, pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE,):
        self.ztest = ztest
        ZBaseDialog.__init__(self, parent, wx.ID_ANY, title, pos = pos, size = size, style = style)
    # end __init__()

    def _createContentWidgets(self):
        self.testPanel = ZTestProgressPanel(self.ztest, self)
        self.bottomStaticLine = wx.StaticLine(self, wx.HORIZONTAL)
    # end _createContentWidgets()

    def _populateContentWidgets(self):
        pass
    # end _populateContentWidgets()

    def _layoutContentWidgets(self):
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.testPanel, 1, wx.EXPAND | wx.ALL, 5)
        box.Add(self.bottomStaticLine, 0, wx.EXPAND | wx.TOP, 5)
        return box
    # end _layoutContentWidgets()

    def _bindWidgetEvents(self):
        self.Bind(ZEVT_ZTEST_COMPLETED, self.onTestPassed, self.testPanel)
        self.Bind(ZEVT_ZTEST_FAILED, self.onTestFailed, self.testPanel)
        
        self._bindCancelButton(self.onCancel)
    # end _bindWidgetEvents()

    def _getButtonTypes(self):
        return ZBaseDialog.CANCEL_BUTTON
    # end _getButtonTypes()

    def onCancel(self, event):
        self.testPanel.cancelTest()
        event.Skip()
    # end onCancel()

    def onTestPassed(self, event):
        cancelButton = self.FindWindowById(wx.ID_CANCEL)
        cancelButton.SetLabel(_extstr(u"Close")) #$NON-NLS-1$
        self.Unbind(wx.EVT_BUTTON, cancelButton)
        event.Skip()
    # end onTestPassed()

    def onTestFailed(self, event):
        cancelButton = self.FindWindowById(wx.ID_CANCEL)
        cancelButton.SetLabel(_extstr(u"Close")) #$NON-NLS-1$
        self.Unbind(wx.EVT_BUTTON, cancelButton)
        event.Skip()
    # end onTestFailed()

    def ShowModal(self):
        self.testPanel.startTest()
        ZBaseDialog.ShowModal(self)
    # end ShowModal()

# end ZTestProgressDialog
