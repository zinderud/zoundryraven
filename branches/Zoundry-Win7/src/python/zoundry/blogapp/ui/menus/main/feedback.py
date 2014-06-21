from zoundry.appframework.ui.actions.menuaction import ZMenuAction
from zoundry.appframework.ui.util.feedbackutil import ZFeedbackUtil
from zoundry.blogapp.messages import _extstr

# -------------------------------------------------------------------------------------
# This is the action implementation for the Help->About main menu item.
# -------------------------------------------------------------------------------------
class ZFeedbackMenuAction(ZMenuAction):

    def getDisplayName(self):
        return _extstr(u"feedback.SendFeedback") #$NON-NLS-1$
    # end getDisplayName()

    def getDescription(self):
        return _extstr(u"feedback.SendFeedbackDescription") #$NON-NLS-1$
    # end getDescription()

    def runAction(self, actionContext):
        ZFeedbackUtil().doFeedback(actionContext.getParentWindow())
    # end runAction()

# end ZFeedbackMenuAction
