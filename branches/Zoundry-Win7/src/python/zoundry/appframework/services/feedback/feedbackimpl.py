from zoundry.appframework.constants import IZAppServiceIDs
from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.messages import _extstr
from zoundry.appframework.services.backgroundtask.backgroundtaskimpl import ZBackgroundTask
from zoundry.appframework.services.feedback.feedback import IZFeedback
from zoundry.appframework.services.feedback.feedback import IZFeedbackService
from zoundry.base.exceptions import ZException
from zoundry.base.net.http import ZSimpleXmlHTTPRequest
from zoundry.base.util.schematypes import ZSchemaDateTime


# ------------------------------------------------------------------------------
# Background task that will send some feedback to the Zoundry feedback endpoint.
# ------------------------------------------------------------------------------
class ZFeedbackBackgroundTask(ZBackgroundTask):

    def __init__(self):
        self.endpoint = None
        self.customAttributes = {}
        self.connection = None

        ZBackgroundTask.__init__(self)
    # end __init__()

    def initialize(self, endpoint, feedback, version):
        self.endpoint = endpoint
        self.feedback = feedback
        self.version = version
        self.setName(_extstr(u"feedbackimpl.SendingFeedback")) #$NON-NLS-1$
        self.setNumWorkUnits(2)
    # end initialize()

    def getCustomAttributes(self):
        return self.customAttributes
    # end getCustomAttributes()

    def setCustomAttributes(self, attributeMap):
        self.customAttributes = attributeMap
    # end setCustomAttributes()

    def isResumable(self):
        return False
    # end isResumable()

    def _doCancel(self):
        if self.connection:
            self.connection.close()
    # end _doCancel()

    def _run(self):
        self._incrementWork(_extstr(u"feedbackimpl.FeedbackInformationGathered_"), 1, True) #$NON-NLS-1$
        self.connection = ZSimpleXmlHTTPRequest(self.endpoint)

        postData = {
                u"name" : u"N/A", #$NON-NLS-2$ #$NON-NLS-1$
                u"email" : self.feedback.getEmail(), #$NON-NLS-1$
                u"title" : self.feedback.getSubject(), #$NON-NLS-1$
                u"description" : self.feedback.getFeedback(), #$NON-NLS-1$
                u"timestamp" : unicode(self.feedback.getTimestamp()), #$NON-NLS-1$
                u"version" : self.version.getFullVersionString(), #$NON-NLS-1$
                u"blogplatform" : u"N/A", #$NON-NLS-1$ #$NON-NLS-2$
                u"reporttype" : self.feedback.getType(), #$NON-NLS-1$
                u"pubsites" : u"N/A", #$NON-NLS-1$ #$NON-NLS-2$
        }
        if self.connection.send(postData):
            self.connection.getResponse()
        else:
            raise ZException(_extstr(u"feedbackimpl.SendingFeedbackFailed")) #$NON-NLS-1$
        self._incrementWork(_extstr(u"feedbackimpl.FeedbackSent"), 1, True) #$NON-NLS-1$
    # end _run()

# end ZFeedbackBackgroundTask


# ------------------------------------------------------------------------------
# Represents some feedback that the user wants to send to Zoundry.
# ------------------------------------------------------------------------------
class ZFeedback(IZFeedback):

    def __init__(self, type, email, subject, feedback):
        self.type = type
        self.email = email
        self.subject = subject
        self.feedback = feedback
        self.timestamp = ZSchemaDateTime()
    # end __init__()

    def getType(self):
        return self.type
    # end getType()

    def getEmail(self):
        return self.email
    # end getEmail()

    def getSubject(self):
        return self.subject
    # end getSubject()

    def getFeedback(self):
        return self.feedback
    # end getFeedback()

    def getTimestamp(self):
        return self.timestamp
    # end getTimestamp()

# end ZFeedback


# ------------------------------------------------------------------------------
# Implementation of the mime type service.
# ------------------------------------------------------------------------------
class ZFeedbackService(IZFeedbackService):

    def __init__(self):
        self.endpoint = u"http://zoundry.com/raven/ravenbugreport.php" #$NON-NLS-1$
    # end __init__()

    def start(self, applicationModel):
        self.logger = applicationModel.getEngine().getService(IZAppServiceIDs.LOGGER_SERVICE_ID)
        self.bgTaskService = applicationModel.getEngine().getService(IZAppServiceIDs.BACKGROUND_TASK_SERVICE_ID)
        self.logger.debug(u"Feedback Service started.") #$NON-NLS-1$
    # end start()

    def stop(self):
        pass
    # end stop()

    def sendFeedback(self, feedback):
        version = getApplicationModel().getVersion()

        task = ZFeedbackBackgroundTask()
        task.initialize(self.endpoint, feedback, version)
        self.bgTaskService.addTask(task)

        return task
    # end sendFeedback()

# end ZFeedbackService
