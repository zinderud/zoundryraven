from zoundry.appframework.constants import IZAppServiceIDs
from zoundry.appframework.global_services import getApplicationModel

# ----------------------------------------------------------------------------------------------
# Convenience method for comparing two background tasks using their start times.
# ----------------------------------------------------------------------------------------------
def _cmpTasks(task1, task2):
    return cmp(task1.getStartTime(), task2.getStartTime()) * -1
# end _cmpTasks()


# ----------------------------------------------------------------------------------------------
# A model for the background task manager window.
# ----------------------------------------------------------------------------------------------
class ZBackgroundTaskManagerModel:

    def __init__(self):
        self.service = getApplicationModel().getService(IZAppServiceIDs.BACKGROUND_TASK_SERVICE_ID)
    # end __init__()

    def getBackgroundTasks(self):
        tasks = self.service.getTasks()
        return self._sortByStartTime(tasks)
    # end getBackgroundTasks()

    def getService(self):
        return self.service
    # end getService()

    def removeTask(self, task):
        u"Removes a single task." #$NON-NLS-1$
        self.service.removeTask(task.getId())
    # end removeTask()

    def cleanUpTasks(self):
        u"Called to remove all tasks that are complete." #$NON-NLS-1$
        for task in self.getBackgroundTasks():
            if task.isCancelled() or task.isComplete():
                self.removeTask(task)
    # end cleanUpTasks()

    def cancelTask(self, task):
        u"Called to cancel the given task." #$NON-NLS-1$
        self.service.cancelTask(task.getId())
    # end cancelTask()

    def resumeTask(self, task):
        u"Called to resume the given task." #$NON-NLS-1$
        self.service.resumeTask(task.getId())
    # end resumeTask()
    
    def _sortByStartTime(self, tasks):
        tasksCopy = []
        for task in tasks:
            tasksCopy.append(task)
        tasksCopy.sort(_cmpTasks)
        return tasksCopy
    # end _sortByStartTime()

# end ZBackgroundTaskManagerModel
