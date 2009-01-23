from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.messages import _extstr
from zoundry.appframework.ui.util.uiutil import getRootWindowOrDialog
from zoundry.appframework.ui.widgets.dialog import ZBaseDialog
from zoundry.appframework.ui.widgets.dialogs.error import ZErrorDialog
from zoundry.appframework.ui.widgets.dialogs.error import ZExceptionDialog
from zoundry.appframework.ui.widgets.dialogs.error import ZExceptionWithFeedbackDialog
from zoundry.appframework.ui.widgets.dialogs.standarddialogsupport import ZStandardDialogAcceleratorTable
from zoundry.base.exceptions import ZException
import os
import wx


# -----------------------------------------------------------------------------------------
# Base class for all standard dialogs.
# -----------------------------------------------------------------------------------------
class ZStandardDialog(ZBaseDialog):

    def __init__(self, parent, title, caption, buttonMask, imageName):
        self.caption = caption
        self.buttonMask = buttonMask
        self.imageName = imageName
        ZBaseDialog.__init__(self, parent, wx.ID_ANY, title, style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        (w, h) = self.GetBestSizeTuple()
        w = min(max(w, 350), 500)
        self.SetSize(wx.Size(w, h))
        self.Layout()
    # end __init__()

    def _createContentWidgets(self):
        self.topPanel = wx.Panel(self, wx.ID_ANY)
        self.topPanel.SetBackgroundColour(wx.WHITE)

        self._createStandardDialogWidgets()

        self.staticLine = wx.StaticLine(self, wx.HORIZONTAL)
    # end _createContentWidgets()

    def _createStandardDialogWidgets(self):
        self.captionText = wx.StaticText(self.topPanel, wx.ID_ANY, self.caption)
        self.image = None
        bitmap = self._getBitmap()
        if bitmap:
            self.image = wx.StaticBitmap(self.topPanel, wx.ID_ANY, bitmap)

        self.accelTable = ZStandardDialogAcceleratorTable(self, self._getButtonTypes())
        self.SetAcceleratorTable(self.accelTable)
    # end _createStandardDialogWidgets()

    def _layoutContentWidgets(self):
        sizer = self._layoutTopPanel()

        self.topPanel.SetSizer(sizer)
        self.topPanel.SetAutoLayout(True)

        vertSizer = wx.BoxSizer(wx.VERTICAL)
        vertSizer.Add(self.topPanel, 1, wx.EXPAND)
        vertSizer.Add(self.staticLine, 0, wx.EXPAND)
        return vertSizer
    # end _layoutContentWidgets()

    def _layoutTopPanel(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        if self.image:
            sizer.Add(self.image, 0, wx.LEFT | wx.TOP | wx.BOTTOM, 10)

        sizer.Add(self.captionText, 1, wx.EXPAND | wx.ALL | wx.ALIGN_CENTER, 10)
        return sizer
    # end _layoutTopPanel()

    def _bindWidgetEvents(self):
        self.Bind(wx.EVT_BUTTON, self.onYes, None, wx.ID_YES)
        self.Bind(wx.EVT_BUTTON, self.onNo, None, wx.ID_NO)

        self.accelTable.bindTo(self)
    # end _bindWidgetEvents()

    def onYes(self, event):
        self.EndModal(wx.ID_YES)
        event.Skip()
    # end onYes()

    def onNo(self, event):
        self.EndModal(wx.ID_NO)
        event.Skip()
    # end onNo()

    def _getBitmap(self):
        if not self.imageName:
            return None
        path = os.path.join(u"images", u"widgets", u"standard_dialog", self.imageName + u".png") #$NON-NLS-3$ #$NON-NLS-2$ #$NON-NLS-1$ #$NON-NLS-4$
        return getApplicationModel().getResourceRegistry().getBitmap(path)
    # end _getBitmap()

    def _getButtonTypes(self):
        return self.buttonMask
    # end _getButtonTypes()

# end ZStandardDialog


# ------------------------------------------------------------------------------
# A yes/no dialog that also has a checkbox for "Remember this decision".
# ------------------------------------------------------------------------------
class ZPersistentYesNoDialog(ZStandardDialog):

    def __init__(self, parent, title, caption, prefsId, canRememberNoOption = False):
        self.prefsId = prefsId
        self.canRememberNoOption = canRememberNoOption

        ZStandardDialog.__init__(self, parent, title, caption, ZBaseDialog.YES_BUTTON | ZBaseDialog.NO_BUTTON, u"question") #$NON-NLS-1$
    # end __init__()

    def _createContentWidgets(self):
        ZStandardDialog._createContentWidgets(self)

        self.decisionCB = wx.CheckBox(self, wx.ID_ANY, _extstr(u"standarddialogs.RememberDecision")) #$NON-NLS-1$
    # end _createContentWidgets()

    def _layoutContentWidgets(self):
        sizer = wx.BoxSizer(wx.VERTICAL)

        sizer.AddSizer(ZStandardDialog._layoutContentWidgets(self), 1, wx.EXPAND)
        sizer.Add(self.decisionCB, 0, wx.EXPAND | wx.ALL, 4)

        return sizer
    # end _layoutContentWidgets()

    def _bindWidgetEvents(self):
        ZStandardDialog._bindWidgetEvents(self)

        self.Bind(wx.EVT_CHECKBOX, self.onDecisionCB, self.decisionCB)
    # end _bindWidgetEvents()

    def onYes(self, event):
        if self.decisionCB.IsChecked():
            self._remember(wx.ID_YES)
        ZStandardDialog.onYes(self, event)
    # end onYes()

    def onNo(self, event):
        if self.canRememberNoOption and self.decisionCB.IsChecked():
            self._remember(wx.ID_NO)
        ZStandardDialog.onNo(self, event)
    # end onNo()

    def onDecisionCB(self, event):
        event.Skip()
    # end onDecisionCB()

    def ShowModal(self):
        userPrefs = getApplicationModel().getUserProfile().getPreferences()
        value = userPrefs.getUserPreferenceInt(u"zoundry.appframework.ui.dialogs.decisions." + self.prefsId, None) #$NON-NLS-1$
        if value is not None:
            return value
        else:
            return ZStandardDialog.ShowModal(self)
    # end ShowModal()

    def _remember(self, value):
        userPrefs = getApplicationModel().getUserProfile().getPreferences()
        userPrefs.setUserPreference(u"zoundry.appframework.ui.dialogs.decisions." + self.prefsId, value) #$NON-NLS-1$
    # end _remember()

# end ZPersistentYesNoDialog

def ZShowYesNoMessage(parent, question, title):
    parent = getRootWindowOrDialog(parent)
    dlg = ZStandardDialog(parent, title, question, ZBaseDialog.YES_BUTTON | ZBaseDialog.NO_BUTTON, u"question") #$NON-NLS-1$
    dlg.CenterOnParent()
    result = dlg.ShowModal() == wx.ID_YES
    dlg.Destroy()
    if parent is not None:
        parent.RemoveChild(dlg)
    return result
# end YesNoMessage()

def ZShowPersistentYesNoMessage(parent, question, title, prefsId, canRememberNoOption = False):
    parent = getRootWindowOrDialog(parent)
    dlg = ZPersistentYesNoDialog(parent, title, question, prefsId, canRememberNoOption) #$NON-NLS-1$
    dlg.CenterOnParent()
    result = dlg.ShowModal() == wx.ID_YES
    dlg.Destroy()
    if parent is not None:
        parent.RemoveChild(dlg)
    return result
# end ZShowPersistentYesNoMessage()

def ZShowYesNoCancelMessage(parent, question, title):
    parent = getRootWindowOrDialog(parent)
    dlg = ZStandardDialog(parent, title, question, ZBaseDialog.YES_BUTTON | ZBaseDialog.NO_BUTTON | ZBaseDialog.CANCEL_BUTTON, u"question") #$NON-NLS-1$
    dlg.CentreOnParent()
    result = dlg.ShowModal()
    dlg.Destroy()
    if parent is not None:
        parent.RemoveChild(dlg)
    return result
# end YesNoCancelMessage()

def ZShowInfoMessage(parent, message, title):
    parent = getRootWindowOrDialog(parent)
    dlg = ZStandardDialog(parent, title, message, ZBaseDialog.OK_BUTTON, u"information") #$NON-NLS-1$
    dlg.CentreOnParent()
    dlg.ShowModal()
    dlg.Destroy()
    if parent is not None:
        parent.RemoveChild(dlg)
# end InfoMessage()

def ZShowWarnMessage(parent, message, title):
    parent = getRootWindowOrDialog(parent)
    dlg = ZStandardDialog(parent, title, message, ZBaseDialog.OK_BUTTON, u"warning") #$NON-NLS-1$
    dlg.CentreOnParent()
    dlg.ShowModal()
    dlg.Destroy()
    if parent is not None:
        parent.RemoveChild(dlg)
# end WarnMessage()

def ZShowErrorMessage(parent, message, details):
    parent = getRootWindowOrDialog(parent)
    dlg = ZErrorDialog(parent, message, details)
    dlg.CentreOnScreen()
    dlg.ShowModal()
    dlg.Destroy()
    if parent is not None:
        parent.RemoveChild(dlg)
# end ErrorMessage()

def ZShowExceptionMessage(parent, zexception):
    parent = getRootWindowOrDialog(parent)
    if not isinstance(zexception, ZException):
        zexception = ZException(rootCause = zexception)
    dlg = ZExceptionDialog(parent, zexception)
    dlg.CentreOnScreen()
    dlg.ShowModal()
    dlg.Destroy()
    if parent is not None:
        parent.RemoveChild(dlg)
# end ZExceptionMessage()


# ------------------------------------------------------------------------------
# Action to show an error message with an option to send feedback.
# ------------------------------------------------------------------------------
def ZShowExceptionWithFeedback(parent, zexception):
    if not isinstance(zexception, ZException):
        zexception = ZException(rootCause = zexception)

    dlg = ZExceptionWithFeedbackDialog(parent, zexception)
    dlg.CentreOnParent()
    rval = dlg.ShowModal()
    dlg.Destroy()
    if parent is not None:
        parent.RemoveChild(dlg)

    if rval == wx.ID_OK:
        from zoundry.appframework.ui.util.feedbackutil import ZFeedbackUtil
        ZFeedbackUtil().doFeedback(parent, zexception.getMessage(), zexception.getStackTrace())
# end ZShowExceptionWithFeedback


# FIXME (EPW) Remove this when development is complete.
def ZShowNotYetImplementedMessage(parent):
    ZShowInfoMessage(parent, u"Not yet implemented.", u"Warning") #$NON-NLS-2$ #$NON-NLS-1$
# end ZShowNotYetImplementedMessage()
