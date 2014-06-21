from zoundry.appframework.constants import IZAppUserPrefsKeys
from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.messages import _extstr
from zoundry.appframework.services.feedback.feedbackimpl import ZFeedback
from zoundry.appframework.ui.dialogs.mixins import ZPersistentDialogMixin
from zoundry.appframework.ui.widgets.dialog import ZBaseDialog
from zoundry.appframework.ui.widgets.dialogs.header import ZHeaderDialog
import wx

# ------------------------------------------------------------------------------
# The Zoundry Raven About dialog.
# ------------------------------------------------------------------------------
class ZFeedbackDialog(ZHeaderDialog, ZPersistentDialogMixin):

    def __init__(self, parent):
        self.userPrefs = getApplicationModel().getUserProfile().getPreferences()
        self.feedbackEmailUserPrefsKey = IZAppUserPrefsKeys.FEEDBACK_DIALOG + u".email" #$NON-NLS-1$

        ZBaseDialog.__init__(self, parent, wx.ID_ANY, _extstr(u"feedbackdialog.ZoundryRavenFeedback")) #$NON-NLS-1$
        ZPersistentDialogMixin.__init__(self, IZAppUserPrefsKeys.FEEDBACK_DIALOG, True, True)
    # end __init__()

    def setSubject(self, value):
        self.subject.SetValue(value)
    # end setSubject()

    def setDetails(self, details):
        self.feedback.SetValue(details)
    # end setDetails()

    def getFeedback(self):
        type = self.feedbackType.GetValue()
        email = self.email.GetValue()
        subject = self.subject.GetValue()
        feedback = self.feedback.GetValue()
        return ZFeedback(type, email, subject, feedback)
    # end getFeedback()

    def _createNonHeaderWidgets(self):
        self.feedbackTypeLabel = wx.StaticText(self, wx.ID_ANY, u"%s:" % _extstr(u"feedbackdialog.FeedbackType")) #$NON-NLS-1$ #$NON-NLS-2$
        self.emailLabel = wx.StaticText(self, wx.ID_ANY, u"%s:" % _extstr(u"feedbackdialog.Email_optional")) #$NON-NLS-1$ #$NON-NLS-2$
        self.subjectLabel = wx.StaticText(self, wx.ID_ANY, u"%s:" % _extstr(u"feedbackdialog.Subject")) #$NON-NLS-1$ #$NON-NLS-2$
        self.feedbackLabel = wx.StaticText(self, wx.ID_ANY, _extstr(u"feedbackdialog.Feedback")) #$NON-NLS-1$

        self.feedbackType = wx.ComboBox(self, wx.ID_ANY, style = wx.CB_DROPDOWN | wx.CB_READONLY)
        self.email = wx.TextCtrl(self, wx.ID_ANY)
        self.subject = wx.TextCtrl(self, wx.ID_ANY)
        self.feedback = wx.TextCtrl(self, wx.ID_ANY, style = wx.TE_PROCESS_TAB | wx.TE_MULTILINE)

        self.feedback.SetSizeHints(-1, 100)

        self.staticLine = wx.StaticLine(self, wx.HORIZONTAL)
    # end _createNonHeaderWidgets()

    def _populateNonHeaderWidgets(self):
        self.feedbackType.AppendItems([ _extstr(u"feedbackdialog.Bug"), _extstr(u"feedbackdialog.Enhancement"), _extstr(u"feedbackdialog.Praise") ]) #$NON-NLS-3$ #$NON-NLS-2$ #$NON-NLS-1$
        self.feedbackType.SetValue(_extstr(u"feedbackdialog.Bug")) #$NON-NLS-1$

        if self.userPrefs:
            emailValue = self.userPrefs.getUserPreference(self.feedbackEmailUserPrefsKey, u"") #$NON-NLS-1$
            self.email.SetValue(emailValue)
    # end _populateNonHeaderWidgets()

    def _layoutNonHeaderWidgets(self):
        # Flexible grid sizer where all of the label->text ctrl pairs will live
        flexGridSizer = wx.FlexGridSizer(3, 2, 5, 5)
        flexGridSizer.AddGrowableCol(1)

        flexGridSizer.Add(self.feedbackTypeLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        flexGridSizer.Add(self.feedbackType, 0, wx.EXPAND | wx.RIGHT, 5)
        flexGridSizer.Add(self.emailLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        flexGridSizer.Add(self.email, 0, wx.EXPAND | wx.RIGHT, 5)
        flexGridSizer.Add(self.subjectLabel, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        flexGridSizer.Add(self.subject, 0, wx.EXPAND | wx.RIGHT, 5)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddSizer(flexGridSizer, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(self.feedbackLabel, 0, wx.EXPAND | wx.LEFT, 5)
        sizer.Add(self.feedback, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(self.staticLine, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 2)

        return sizer
    # end _layoutNonHeaderWidgets()

    def _getHeaderTitle(self):
        return _extstr(u"feedbackdialog.ZoundryRavenFeedback") #$NON-NLS-1$
    # end _getHeaderTitle()

    def _getHeaderMessage(self):
        return _extstr(u"feedbackdialog.FeedbackDescription") #$NON-NLS-1$
    # end _getHeaderMessage()

    def _getHeaderImagePath(self):
        return u"images/dialogs/feedback/header.png" #$NON-NLS-1$
    # end _getHeaderImagePath()

    def _getHeaderHelpURL(self):
        return u"http://www.zoundry.com" #$NON-NLS-1$
    # end _getHeaderHelpUrl()

    def _bindWidgetEvents(self):
        self._bindOkButton(self.onSendFeedback)
    # end _bindWidgetEvents()

    def _setInitialFocus(self):
        self.subject.SetFocus()
    # end _setInitialFocus()

    def _getOKButtonLabel(self):
        return _extstr(u"feedbackdialog.Send") #$NON-NLS-1$
    # end _getOKButtonLabel()

    def onSendFeedback(self, event):
        if self.userPrefs:
            self.userPrefs.setUserPreference(self.feedbackEmailUserPrefsKey, self.email.GetValue()) #$NON-NLS-1$
        event.Skip()
    # end onSendFeedback()

# end ZFeedbackDialog
