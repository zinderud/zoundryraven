from zoundry.blogapp.services.accountstore.accounttutil import ZAccountUtil
from zoundry.appframework.constants import IZAppServiceIDs
from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.ui.actions.startupaction import IZStartupAction
from zoundry.appframework.ui.bgtasks.bgtaskmanager import ZShowBackgroundTaskManager
from zoundry.appframework.ui.util.uiutil import ZMethodRunnable
from zoundry.appframework.ui.util.uiutil import fireUIExecEvent
from zoundry.appframework.ui.widgets.dialogs.standarddialogs import ZShowYesNoMessage
from zoundry.base.util.fileutil import deleteDirectory
from zoundry.base.util.fileutil import getFileMetaData
from zoundry.base.util.schematypes import ZSchemaDateTime
from zoundry.blogapp.constants import IZBlogAppServiceIDs
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.ui.editors.editorwin import getEditorWindow
from zoundry.appframework.global_services import getLoggerService
import os

# ------------------------------------------------------------------------------
# Filter function used when deleting temp files.  Deletes only temp files older
# than today.
# ------------------------------------------------------------------------------
def tempFileFilter(filePath):
    if os.path.isfile(filePath):
        (shortFileName, absolutePath, fileSize, timeStamp) = getFileMetaData(filePath) #@UnusedVariable
        today = ZSchemaDateTime()
        today.setHour(0)
        today.setMinutes(0)
        today.setSeconds(0)
        return timeStamp < today
    else:
        return False
# end tempFileFilter()


# ------------------------------------------------------------------------------
# Implements startup action logic for the Raven blog application.
# ------------------------------------------------------------------------------
class ZBlogAppStartupAction(IZStartupAction):

    def __init__(self):
        pass
    # end __init__()

    def runAction(self, actionContext): #@UnusedVariable
        if self._backgroundTasksRunning():
            ZShowBackgroundTaskManager()
        fireUIExecEvent(ZMethodRunnable(self._recoverCrashSnapshots), actionContext.getWindow())
        fireUIExecEvent(ZMethodRunnable(self._deleteTempFiles), actionContext.getWindow())
        fireUIExecEvent(ZMethodRunnable(self._createAccountMediaStores), actionContext.getWindow())
    # end runAction()

    def _backgroundTasksRunning(self):
        bgTaskService = getApplicationModel().getService(IZAppServiceIDs.BACKGROUND_TASK_SERVICE_ID)
        for task in bgTaskService.getTasks():
            if task.isRunning():
                return True
        return False
    # end _backgroundTasksRunning()

    def _deleteTempFiles(self):
        tempDir = getApplicationModel().getUserProfile().getTempDirectory()
        try:
            deleteDirectory(tempDir, False, tempFileFilter)
        except Exception, e:
            getLoggerService().exception(e)
    # end _deleteTempFiles()

    def _recoverCrashSnapshots(self):
        crashRecoveryService = getApplicationModel().getService(IZBlogAppServiceIDs.CRASH_RECOVERY_SERVICE_ID)
        snapshots = crashRecoveryService.getRecoverySnapshots()
        if snapshots:
            title = _extstr(u"startup.RecoverTitle") #$NON-NLS-1$
            msg = _extstr(u"startup.RecoverMessage") % len(snapshots) #$NON-NLS-1$
            if ZShowYesNoMessage(getApplicationModel().getTopWindow(), msg, title):
                for document in snapshots:
                    editorWindow = getEditorWindow()
                    editorWindow.openDocument(document)
                    editorWindow.Show()
            crashRecoveryService.clearRecoverySnapshot()
    # end _recoverCrashSnapshots()
    
    def _createAccountMediaStores(self):
        # assigm media stores if needed to accounts that do not have any (e.g via WLW imports)
        try:
            accStore = getApplicationModel().getService(IZBlogAppServiceIDs.ACCOUNT_STORE_SERVICE_ID)
            ZAccountUtil().autoAssignMediaStores(accStore)
        except:
            pass
    # end _createAccountMediaStores()
        

# end ZBlogAppStartupAction
