from zoundry.appframework.constants import IZAppServiceIDs
from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.messages import _extstr
from zoundry.appframework.ui.dialogs.bgtaskprogressdialog import ZBackgroundTaskProgressDialog
from zoundry.appframework.ui.dialogs.feedbackdialog import ZFeedbackDialog
import wx

# ------------------------------------------------------------------------------
# Feedback utility class - used to share code between various places that need
# show the send feedback dialog.
# ------------------------------------------------------------------------------
class ZFeedbackUtil:

    def doFeedback(self, parent, subject = None, details = None):
        feedback = None

        # Open the feedback dialog
        dialog = ZFeedbackDialog(parent)
        if subject is not None:
            dialog.setSubject(subject)
        if details is not None:
            dialog.setDetails(details)
        if dialog.ShowModal() == wx.ID_OK:
            feedback = dialog.getFeedback()
        dialog.Destroy()

        # If the resulting feedback is not None, then initiate the
        # feedback (hit the Zoundry endpoint) and display the result
        # as a background task in the bg task dialog.
        if feedback is not None:
            feedbackService = getApplicationModel().getService(IZAppServiceIDs.FEEDBACK_SERVICE_ID)
            bgTask = feedbackService.sendFeedback(feedback)
            if bgTask is not None:
                title = _extstr(u"feedbackutil.SendingFeedback") #$NON-NLS-1$
                description = _extstr(u"feedbackutil.SendingFeedbackMsg") #$NON-NLS-1$
                imagePath = u"images/dialogs/bgtask/header_image.png" #$NON-NLS-1$
                dialog = ZBackgroundTaskProgressDialog(parent, bgTask, title, description, imagePath)
                dialog.ShowModal()
                dialog.Destroy()
    # end doFeedback()

# end ZFeedbackUtil
