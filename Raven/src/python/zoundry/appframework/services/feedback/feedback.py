from zoundry.appframework.engine.service import IZService

# ------------------------------------------------------------------------------
# Represents some feedback that the user wants to send to Zoundry.
# ------------------------------------------------------------------------------
class IZFeedback:

    def getType(self):
        u"""getType() -> string
        The type of feedback (bug, enhancement, etc).""" #$NON-NLS-1$
    # end getType()

    def getEmail(self):
        u"""getEmail() -> string
        Gets the email address of the user sending the feedback (optional).""" #$NON-NLS-1$
    # end getEmail()

    def getSubject(self):
        u"""getSubject() -> string
        Gets the feedback subject.""" #$NON-NLS-1$
    # end getSubject()

    def getFeedback(self):
        u"""getFeedback() -> string
        Returns the feedback details.""" #$NON-NLS-1$
    # end getFeedback()

    def getTimestamp(self):
        u"""getTimestamp() -> ZSchemaDateTime
        Gets the timestamp that this feedback was created on.""" #$NON-NLS-1$
    # end getTimestamp()

# end IZFeedback


# ------------------------------------------------------------------------------
# This interface defines the feedback service.  The feedback service is
# responsible for sending user feedback about the application to Zoundry LLC.
# ------------------------------------------------------------------------------
class IZFeedbackService(IZService):

    def sendFeedback(self, feedback):
        u"""sendFeedback(IZFeedback) -> ZBackgroundTask
        Sends the feedback in background task.""" #$NON-NLS-1$
    # end sendFeedback()

# end IZFeedbackService
