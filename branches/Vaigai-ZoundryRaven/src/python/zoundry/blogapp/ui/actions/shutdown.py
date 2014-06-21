from zoundry.appframework.ui.actions.shutdownaction import IZShutdownAction
from zoundry.appframework.ui.bgtasks.bgtaskmanager import getBackgroundTaskManager
from zoundry.appframework.ui.widgets.dialogs.standarddialogs import ZShowYesNoMessage
from zoundry.blogapp.constants import IZBlogAppServiceIDs
from zoundry.blogapp.constants import IZBlogAppUserPrefsKeys
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.ui.editors.editorwin import getEditorWindow
from zoundry.blogapp.ui.templates.templatemanager import getTemplateManager
from zoundry.blogapp.ui.translation.translationmanager import getTranslationManager


# ----------------------------------------------------------------------------------------
# Implements shutdown action logic for the Raven blog application.  This shutdown action
# handles the following cases:
#
#   1) prompts to cancel any currently running, non-resumable background tasks
#   2) save the current main window size
# ----------------------------------------------------------------------------------------
class ZBlogAppShutdownAction(IZShutdownAction):

    def __init__(self):
        pass
    # end __init__()

    def runAction(self, actionContext):
        bgTaskMan = getBackgroundTaskManager()
        templateMan = getTemplateManager()
        translationMan = getTranslationManager()
        editorWindow = getEditorWindow()
        if bgTaskMan is not None:
            bgTaskMan.Close()
        if editorWindow is not None:
            editorWindow.Close()
        if templateMan is not None:
            templateMan.Close()
        if translationMan is not None:
            translationMan.Close()

        self._stopBackgroundTasks(actionContext)
        self._saveWindowLayout(actionContext)
    # end runAction()

    def shouldShutdown(self, actionContext):
        numBgTasks = self._getNumRunningBackgroundTasks(actionContext)
        if numBgTasks > 0:
            if not ZShowYesNoMessage(actionContext.getWindow(), _extstr(u"shutdown.CancelRunningTasksMessage") % numBgTasks, _extstr(u"shutdown.CancelRunningTasksTitle")): #$NON-NLS-2$ #$NON-NLS-1$
                return False
        editorWindow = getEditorWindow()
        if editorWindow is not None:
            return editorWindow.close()
        return True
    # end shouldShutdown()

    def _stopBackgroundTasks(self, actionContext):
        bgTaskService = actionContext.getApplicationModel().getService(IZBlogAppServiceIDs.BACKGROUND_TASK_SERVICE_ID)
        for task in bgTaskService.getTasks():
            if task.isRunning():
                # Simply stop the task if it is resumable, otherwise cancel it outright.
                if task.isResumable():
                    task.stop()
                else:
                    task.cancel()
    # end _stopBackgroundTasks()

    def _saveWindowLayout(self, actionContext):
        # Save the window size
        window = actionContext.getWindow()
        if window.IsShown() and not window.IsIconized():
            userPrefs = actionContext.getApplicationModel().getUserProfile().getPreferences()
            if not window.IsMaximized():
                (width, height) = window.GetSizeTuple()
                (x, y) = window.GetPositionTuple()
                userPrefs.setUserPreference(IZBlogAppUserPrefsKeys.APPWIN_WIDTH, width)
                userPrefs.setUserPreference(IZBlogAppUserPrefsKeys.APPWIN_HEIGHT, height)
                userPrefs.setUserPreference(IZBlogAppUserPrefsKeys.APPWIN_X, x)
                userPrefs.setUserPreference(IZBlogAppUserPrefsKeys.APPWIN_Y, y)
                userPrefs.setUserPreference(IZBlogAppUserPrefsKeys.APPWIN_MAXIMIZED, False)
            else:
                userPrefs.setUserPreference(IZBlogAppUserPrefsKeys.APPWIN_MAXIMIZED, True)
    # end _saveWindowLayout()

    def _getNumRunningBackgroundTasks(self, actionContext):
        bgTaskService = actionContext.getApplicationModel().getService(IZBlogAppServiceIDs.BACKGROUND_TASK_SERVICE_ID)
        count = 0
        for task in bgTaskService.getTasks():
            if task.isRunning() and not task.isResumable():
                count = count + 1
        return count
    # end _getNumRunningBackgroundTasks()

# end ZBlogAppShutdownAction
