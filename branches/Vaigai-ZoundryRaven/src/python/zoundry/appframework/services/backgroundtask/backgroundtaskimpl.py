from zoundry.appframework.constants import IZAppServiceIDs
from zoundry.appframework.exceptions import ZAppFrameworkException
from zoundry.appframework.global_services import getLoggerService
from zoundry.appframework.messages import _extstr
from zoundry.appframework.services.backgroundtask.backgroundtask import IZBackgroundTask
from zoundry.appframework.services.backgroundtask.backgroundtask import IZBackgroundTaskListener
from zoundry.appframework.services.backgroundtask.backgroundtask import IZBackgroundTaskService
from zoundry.appframework.services.backgroundtask.backgroundtaskio import loadBackgroundTask
from zoundry.appframework.services.backgroundtask.backgroundtaskio import saveBackgroundTask
from zoundry.base.exceptions import ZException
from zoundry.base.util.collections import ZListenerSet
from zoundry.base.util.fileutil import deleteFile
from zoundry.base.util.fileutil import getDirectoryListing
from zoundry.base.util.guid import generate
from zoundry.base.util.schematypes import ZSchemaDateTime
from zoundry.base.util.zthread import ZThread
from zoundry.appframework.ui.util.uiutil import ZMethodRunnable
import codecs
import os
import time


# ---------------------------------------------------------------------------------------
# A getDirectoryListing filter that will return only *.task files.
# ---------------------------------------------------------------------------------------
def TASK_FILE_FILTER(path):
    return path.endswith(u".task") #$NON-NLS-1$
# end TASK_FILE_FILTER()


# ---------------------------------------------------------------------------------------
# Base class for a background task.  This base class does a lot of the basics that all
# tasks will need to do (listener management, callbacks, start time, id, etc).
# ---------------------------------------------------------------------------------------
class ZBackgroundTask(IZBackgroundTask):

    def __init__(self):
        self.id = None
        self.name = None
        self.startTime = ZSchemaDateTime()
        self.endTime = None
        self.error = None
        self.numWorkUnits = 0
        self.numCompletedWorkUnits = 0
        self.logLocation = None
        self.logFile = None
        self.running = False
        self.stopped = True
        self.cancelled = False
        self.lastMessage = None
        self.listeners = ZListenerSet()
        self.logger = getLoggerService()
    # end __init__()

    def getId(self):
        return self.id
    # end getId()

    def setId(self, id):
        self.id = id
    # end setId()

    def getName(self):
        return self.name
    # end getName()

    def setName(self, name):
        self.name = name
    # end setName()

    def getStartTime(self):
        return self.startTime
    # end getStartTime()

    def setStartTime(self, startTime):
        self.startTime = startTime
    # end setStartTime()

    def getEndTime(self):
        return self.endTime
    # end getEndTime()

    def setEndTime(self, endTime):
        self.endTime = endTime
    # end setEndTime()

    def getNumWorkUnits(self):
        return self.numWorkUnits
    # end getNumWorkUnits()

    def setNumWorkUnits(self, numWorkUnits):
        self.numWorkUnits = numWorkUnits
    # end setNumWorkUnits()

    def getNumCompletedWorkUnits(self):
        return self.numCompletedWorkUnits
    # end getNumCompletedWorkUnits()

    def setNumCompletedWorkUnits(self, numCompletedWorkUnits):
        self.numCompletedWorkUnits = numCompletedWorkUnits
    # end setNumCompletedWorkUnits()

    def getLogLocation(self):
        return self.logLocation
    # end getLog()

    def setLogLocation(self, logLocation):
        self.logLocation = logLocation
    # end setLog()

    def getLogFile(self):
        if self.logFile is None and self.logLocation is not None:
            self.logFile = codecs.open(self.logLocation, u"aa", u"utf-8") #$NON-NLS-2$ #$NON-NLS-1$
        return self.logFile
    # end getLogFile()

    def getLastLogMessage(self):
        return self.lastMessage
    # end getLastLogMessage()

    def getCustomAttributes(self):
        raise ZAppFrameworkException(u"Subclass should implement this!") #$NON-NLS-1$
    # end getCustomAttributes()

    def setCustomAttributes(self, attributeMap):
        raise ZAppFrameworkException(u"Subclass should implement this!") #$NON-NLS-1$
    # end setCustomAttributes()

    def isRunning(self):
        return self.running
    # end isRunning()

    def isCancelled(self):
        return self.cancelled
    # end isCancelled()

    def setCancelled(self, cancelled = True):
        self.cancelled = cancelled
    # end setCancelled()

    def isComplete(self):
        return self.numCompletedWorkUnits == self.numWorkUnits
    # end isComplete()

    def isResumable(self):
        raise ZAppFrameworkException(u"Subclass should implement this!") #$NON-NLS-1$
    # end isResumable()

    def getError(self):
        return self.error
    # end getError()

    def setError(self, errorMessage, errorDetails):
        self.error = (errorMessage, errorDetails)
    # end setError()

    def hasError(self):
        return self.error is not None
    # end hasError()

    def stop(self):
        self.logger.debug(u"[bgtask.%s] Stopping task." % (self.getName())) #$NON-NLS-1$
        self.stopped = True

        # This should really be a wait/notify
        while self.running:
            time.sleep(0.25)
    # end stop()

    def _doCancel(self):
        u"Subclasses can override in order to provide additional cancel logic." #$NON-NLS-1$
    # end _doCancel()

    def cancel(self):
        self.logger.debug(u"[bgtask.%s] Cancelling task." % (self.getName())) #$NON-NLS-1$
        self.stopped = True
        self.cancelled = True

        self._doCancel()

        # This should really be a wait/notify
        while self.running:
            time.sleep(0.25)

        # Notify the listeners.
        self.listeners.doCallback(u"onCancel", [self]) #$NON-NLS-1$
    # end cancel()

    def cancelAsync(self):
        thread = ZThread(ZMethodRunnable(self.cancel), u"CancelTask", True) #$NON-NLS-1$
        thread.start()
    # end cancelAsync()

    def attachListener(self, listener):
        self.listeners._acquireMutex()
        try:
            self.listeners.append(listener)
            listener.onAttached(self, self.numCompletedWorkUnits)
        finally:
            self.listeners._releaseMutex()
    # end attachListener()

    def detachListener(self, listener):
        self.listeners.remove(listener)
    # end detachListener()

    # Convenience method to indicate that work has been done.
    #
    # message: the message to send to the listeners (and optionally log)
    # amount: amount of work that was done
    # logMessage: flag indicating whether this message should be logged (useful for tasks that do a LOT
    #             of work but only want to log certain vital messages)
    def _incrementWork(self, message, amount = 1, logMessage = True):
        if self.isCancelled():
            return
        self.lastMessage = message
        self.numCompletedWorkUnits = self.numCompletedWorkUnits + amount
        self.listeners.doCallback(u"onWorkDone", [self, amount, message]) #$NON-NLS-1$
        if logMessage:
            self._writeToLog(message)

        if self.numCompletedWorkUnits == self.numWorkUnits:
            self.stopped = True
            self.endTime = ZSchemaDateTime()
            self.listeners.doCallback(u"onComplete", [self]) #$NON-NLS-1$
    # end _incrementWork()

    # Convenience method to raise an error message.  This will notify the listeners of the
    # error, cancel the task, and log the error message.
    def _raiseError(self, errorMessage, errorDetails):
        self.logger.error(errorMessage)
        self.error = (errorMessage, errorDetails)
        self.listeners.doCallback(u"onError", [self, errorMessage, errorDetails]) #$NON-NLS-1$
        self._writeToLog(_extstr(u"backgroundtaskimpl.ErrorInTask") % errorMessage) #$NON-NLS-1$
        self._writeToLog(errorDetails)
        self.endTime = ZSchemaDateTime()
        self.stopped = True
        self.cancelled = True
    # end _raiseError()

    # Reports an exception (when the _run() method throws).
    def _reportException(self, exception):
        if not isinstance(exception, ZException):
            exception = ZException(_extstr(u"backgroundtaskimpl.UnexpectedBGTaskError") % self.getName(), exception) #$NON-NLS-1$
        self.logger.exception(exception)

        self._raiseError(exception.getMessage(), exception.getStackTrace())
    # end _reportException()

    def _writeToLog(self, message):
        self.logger.debug(u"[bgtask.%s] %s" % (self.getName(), message)) #$NON-NLS-1$
        if message is not None and self.getLogFile() is not None:
            self.getLogFile().write(message)
            self.getLogFile().write(u"\n") #$NON-NLS-1$
            self.getLogFile().flush()
    # end _writeToLog()

    def run(self):
        self._writeToLog(u"[bgtask.%s] Task started: %s" % (self.getName(), unicode(ZSchemaDateTime()))) #$NON-NLS-1$
        # Send the 'onStarted' event.
        self._fireStartEvent()

        # Run the actual task logic here.
        try:
            self._run()
        except ZException, ze:
            self._reportException(ze)
        except Exception, e:
            self._reportException(ZException(_extstr(u"backgroundtaskimpl.ErrorExecingTask") % self.getName(), e)) #$NON-NLS-1$

        # Send the 'onStop' event if not complete.
        self._fireStopEvent()
    # end run()

    def _fireStopEvent(self):
        try:
            if not self.isComplete():
                self.listeners.doCallback(u"onStop", [self]) #$NON-NLS-1$
            self.running = False
        finally:
            if self.logFile is not None:
                self._writeToLog(u"Task stopped: %s" % (unicode(ZSchemaDateTime()))) #$NON-NLS-1$
                self.logFile.close()
    # end _fireStopEvent()

    def _fireStartEvent(self):
        self.running = True
        self.stopped = False
        self.listeners.doCallback(u"onStarted", [self, self.numWorkUnits]) #$NON-NLS-1$
    # end _fireStartEvent()

    def _run(self):
        raise ZAppFrameworkException(u"Subclass should implement this!") #$NON-NLS-1$
    # end _run()

# end ZBackgroundTask


# ---------------------------------------------------------------------------------------
# The implementation of the background task service.  This concrete implementation
# will manage all of the background tasks in the application.  This includes those tasks
# that are complete and those that are still running.
# ---------------------------------------------------------------------------------------
class ZBackgroundTaskService(IZBackgroundTaskService, IZBackgroundTaskListener):

    def __init__(self):
        self.logger = None
        self.tasksDirectory = None
        self.tasks = []
        self.listeners = ZListenerSet()
    # end __init__()

    def _getTasksDirectory(self, applicationModel):
        return applicationModel.getUserProfile().getDirectory(u"bgtasks") #$NON-NLS-1$
    # end _getTasksDirectory()

    def addListener(self, listener):
        self.listeners.append(listener)
    # end addListener()

    def removeListener(self, listener):
        self.listeners.remove(listener)
    # end removeListener()

    def start(self, applicationModel):
        self.logger = applicationModel.getEngine().getService(IZAppServiceIDs.LOGGER_SERVICE_ID)
        self.tasksDirectory = self._getTasksDirectory(applicationModel)
        self.tasks = self._loadTasks()
        self.logger.debug(u"Background Task Service started [%d tasks loaded]." % len(self.tasks)) #$NON-NLS-1$
    # end start()

    def stop(self):
        # First, stop all tasks.
        for task in self.tasks:
            if task.isRunning():
                task.stop()

        self.tasks = []
    # end stop()

    def getTasks(self):
        return self.tasks
    # end getTasks()

    def getTask(self, taskId):
        for task in self.tasks:
            if task.getId() == taskId:
                return task
        return None
    # end getTask()

    def addTask(self, task):
        task.setId(generate())
        taskLogFilename = os.path.join(self.tasksDirectory, task.getId() + u".task.log") #$NON-NLS-1$
        task.setLogLocation(taskLogFilename)
        self.tasks.append(task)

        self.listeners.doCallback(u"onTaskAdded", [task]) #$NON-NLS-1$
        self._resumeTask(task)

        # Wait until the num work units has been set by the task (but only
        # wait for up to 30 seconds).
        numWaits = 0
        while task.getNumWorkUnits() <= 0 and numWaits < 60:
            time.sleep(0.5)
            numWaits = numWaits + 1
        if task.getNumWorkUnits() <= 0:
            raise ZAppFrameworkException(_extstr(u"backgroundtaskimpl.TaskFailedToStartError") % task.getName()) #$NON-NLS-1$
    # end addTask()

    def cancelTask(self, taskId, removeFlag = False):
        task = self.getTask(taskId)
        if task is None:
            raise ZAppFrameworkException(_extstr(u"backgroundtaskimpl.FailedToCancelDoesNotExist") % taskId) #$NON-NLS-1$
        task.cancel()
        task.detachListener(self)
        self.listeners.doCallback(u"onTaskCancelled", [task]) #$NON-NLS-1$
        if removeFlag:
            self.removeTask(taskId)
    # end cancelTask()

    def removeTask(self, taskId):
        task = self.getTask(taskId)
        if task is None:
            raise ZAppFrameworkException(_extstr(u"backgroundtaskimpl.FailedToRemoveDoesNotExist") % taskId) #$NON-NLS-1$
        if task.isRunning():
            raise ZAppFrameworkException(_extstr(u"backgroundtaskimpl.FailedToRemoveStillRunning") % taskId) #$NON-NLS-1$
        self.tasks.remove(task)

        self._removeTask(task)

        self.listeners.doCallback(u"onTaskRemoved", [task]) #$NON-NLS-1$
    # end removeTask()

    def resumeTask(self, taskId, listener = None):
        task = self.getTask(taskId)
        if task is None:
            raise ZAppFrameworkException(_extstr(u"backgroundtaskimpl.FailedToResumeTaskNotFound") % taskId) #$NON-NLS-1$
        if task.isRunning():
            raise ZAppFrameworkException(_extstr(u"backgroundtaskimpl.FailedToResumeTaskAlreadyRunning") % taskId) #$NON-NLS-1$
        if task.isComplete():
            raise ZAppFrameworkException(_extstr(u"backgroundtaskimpl.FailedToResumeTaskComplete") % taskId) #$NON-NLS-1$
        if not task.isResumable():
            raise ZAppFrameworkException(_extstr(u"backgroundtaskimpl.FailedToResumeTaskNotResumable") % taskId) #$NON-NLS-1$
        if listener is not None:
            task.attachListener(listener)
        self._resumeTask(task)

        self.listeners.doCallback(u"onTaskResumed", [task]) #$NON-NLS-1$

        return task
    # end resumeTask()

    def _loadTasks(self):
        tasks = []

        taskFiles = getDirectoryListing(self.tasksDirectory, TASK_FILE_FILTER)
        for taskFile in taskFiles:
            try:
                task = self._loadTask(taskFile)
                # Restart any resumable (but not cancelled) tasks.
                if task.isResumable() and not task.isCancelled() and not task.isComplete() and not task.hasError():
                    self._resumeTask(task)
                tasks.append(task)
            except Exception, e:
                self.logger.exception(e)

        return tasks
    # end _loadTasks()

    def _saveBackgroundTasks(self):
        for task in self.tasks:
            self._saveTask(task)
    # end _saveBackgroundTasks()

    def _loadTask(self, taskFile):
        task = loadBackgroundTask(taskFile)
        if task is not None:
            taskLogFilename = taskFile + u".log" #$NON-NLS-1$
            task.setLogLocation(taskLogFilename)
        return task
    # end _loadTask()

    def _resumeTask(self, task):
        task.attachListener(self)
        name = u"bgtask:id:%s" % str(task.getId()) #$NON-NLS-1$
        thread = ZThread(task, name, True)
        thread.start()
    # end _resumeTask()

    def _saveTask(self, task):
        taskXmlFilename = os.path.join(self.tasksDirectory, task.getId() + u".task") #$NON-NLS-1$
        saveBackgroundTask(task, taskXmlFilename)
    # end _saveTask()

    def _removeTask(self, task):
        taskXmlFilename = os.path.join(self.tasksDirectory, task.getId() + u".task") #$NON-NLS-1$
        deleteFile(taskXmlFilename)
        taskLogFilename = taskXmlFilename + u".log" #$NON-NLS-1$
        deleteFile(taskLogFilename)
    # end _removeTask()

    # Nothing to do when the listener is attached.
    def onAttached(self, task, numCompletedWorkUnits): #@UnusedVariable
        pass
    # end onAttached()

    def onStarted(self, task, workAmount): #@UnusedVariable
        self._saveTask(task)
    # end onStarted()

    # Do nothing when work is done - only persist when changing states.
    def onWorkDone(self, task, amount, text): #@UnusedVariable
        pass
    # end onWorkDone()

    def onComplete(self, task):
        self._saveTask(task)
    # end onComplete()

    def onStop(self, task):
        self._saveTask(task)
    # end onStop()

    def onCancel(self, task):
        self._saveTask(task)
    # end onCancel()

    def onError(self, task, errorMessage, errorDetails): #@UnusedVariable
        self._saveTask(task)
    # end onError()

# end ZBackgroundTaskService
