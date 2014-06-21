from zoundry.appframework.engine.service import IZService
from zoundry.base.util.zthread import IZRunnable


# ---------------------------------------------------------------------------------------
# This interface defines a background task listener.  When a listener is attached to a
# background task, the background task first seeds the listener with its current data.
# It will then report its progress (work units, errors, etc...) to the attached listener
# as those event occur.
# ---------------------------------------------------------------------------------------
class IZBackgroundTaskListener:

    def onAttached(self, task, numCompletedWorkUnits):
        u"""onAttached(IZBackgroundTask, int) -> None
        Called when the listener is attached to the background task.""" #$NON-NLS-1$
    # end onAttached()

    def onStarted(self, task, workAmount):
        u"""onStarted(IZBackgroundTask, int) -> None
        Called when the task begins.""" #$NON-NLS-1$
    # end onStarted()

    def onWorkDone(self, task, amount, text):
        u"""onWorkDone(IZBackgroundTask, int, string) -> None
        Called during execution of the task when some amount of work has been done.""" #$NON-NLS-1$
    # end onWorkDone()

    def onComplete(self, task):
        u"""onComplete(IZBackgroundTask) -> None
        Called when the task finishes successfully.""" #$NON-NLS-1$
    # end onComplete()

    def onStop(self, task):
        u"""onStop(IZBackgroundTask) -> None
        Called when the task is stopped (but not cancelled).""" #$NON-NLS-1$
    # end onStop()

    def onCancel(self, task):
        u"""onCancel(IZBackgroundTask) -> None
        Called when the task completes due to being cancelled.""" #$NON-NLS-1$
    # end onCancel()

    def onError(self, task, errorMessage, errorDetails):
        u"""onError(IZBackgroundTask, string, string) -> None
        Called when an error occurs in the task.""" #$NON-NLS-1$
    # end onError()

# end IZBackgroundTaskListener


# ---------------------------------------------------------------------------------------
# This interface defines a background task.  A background task is a task that can be
# associated with a progress dialog or optionally minimized to the 'background' of the
# application.  With a suitable user interface, the background task can be monitored
# either in the background or in the foreground.
# ---------------------------------------------------------------------------------------
class IZBackgroundTask(IZRunnable):

    def getId(self):
        u"""getId() -> string
        Returns this background tasks's unique ID.""" #$NON-NLS-1$
    # end getId()

    def setId(self, id):
        u"""setId(string) -> None
        Sets the ID for the task.""" #$NON-NLS-1$
    # end setId()

    def getName(self):
        u"""getName() -> string
        Returns the name (or short description) of the task.""" #$NON-NLS-1$
    # end getName()

    def setName(self, name):
        u"""setName(string) -> None
        Sets the name of the task.""" #$NON-NLS-1$
    # end setName()

    def getStartTime(self):
        u"""getStartTime() -> ZSchemaDateTime
        Returns the time that this background task started.""" #$NON-NLS-1$
    # end getStartTime()

    def setStartTime(self, startTime):
        u"""setStartTime(ZSchemaDateTime) -> None
        Sets the start time of the task.""" #$NON-NLS-1$
    # end setStartTime()

    def getEndTime(self):
        u"""getEndTime() -> ZSchemaDateTime
        Returns the time that this background task ended.""" #$NON-NLS-1$
    # end getEndTime()

    def setEndTime(self, endTime):
        u"""setEndTime(ZSchemaDateTime) -> None
        Sets the start time of the task.""" #$NON-NLS-1$
    # end setEndTime()

    def getNumWorkUnits(self):
        u"""getNumWorkUnits() -> int
        Returns the number of work units for this background task.""" #$NON-NLS-1$
    # end getNumWorkUnits()

    def setNumWorkUnits(self, numWorkUnits):
        u"""setNumWorkUnits(int) -> None
        Sets the number of work units for the task.""" #$NON-NLS-1$
    # end setNumWorkUnits()

    def getNumCompletedWorkUnits(self):
        u"""getNumCompletedWorkUnits() -> int
        Returns the number of work units that have been completed already.""" #$NON-NLS-1$
    # end getNumCompletedWorkUnits()

    def setNumCompletedWorkUnits(self, numCompletedWorkUnits):
        u"""setNumCompletedWorkUnits(int) -> None
        Sets the number of completed work units for the task.""" #$NON-NLS-1$
    # end setNumCompletedWorkUnits()

    def getLogLocation(self):
        u"""getLocation() -> string
        Returns the file that contains the log.""" #$NON-NLS-1$
    # end getLog()

    def setLogLocation(self, logLocation):
        u"""setLogLocation(string) -> None
        Sets the location of the task's log file.""" #$NON-NLS-1$
    # end setLogLocation()

    def getLastLogMessage(self):
        u"""getLastLogMessage() -> string
        Gets the most recent log message.""" #$NON-NLS-1$
    # end getLastLogMessage()

    def getCustomAttributes(self):
        u"""getCustomAttributes() -> map
        Returns a map of custom attributes for serialization.""" #$NON-NLS-1$
    # end getCustomAttributes()

    def setCustomAttributes(self, attributeMap):
        u"""setCustomAttributes(map) -> None
        Sets some custom attributes on the task (deserialization).""" #$NON-NLS-1$
    # end setCustomAttributes()

    def isRunning(self):
        u"""isRunning() -> boolean
        Returns True if the task is currently running.""" #$NON-NLS-1$
    # end isRunning()

    def isCancelled(self):
        u"""isCancelled() -> boolean
        Returns True if the task has been cancelled.""" #$NON-NLS-1$
    # end isCancelled()

    def setCancelled(self, cancelled = True):
        u"""setCancelled(boolean) -> None
        Sets the state of the task to 'cancelled'.""" #$NON-NLS-1$
    # end setCancelled()

    def isComplete(self):
        u"""isComplete -> boolean
        Returns True if the task completed.""" #$NON-NLS-1$
    # end isComplete()

    def isResumable(self):
        u"""isResumable() -> boolean
        Returns True if this task can be paused/resumed.""" #$NON-NLS-1$
    # end isResumable()

    def hasError(self):
        u"""hasError() -> boolean
        Returns True if the task failed (and has errors).""" #$NON-NLS-1$
    # end hasError()
    
    def getError(self):
        u"""getError() -> (string, string)
        Gets the error message and error details, if any.""" #$NON-NLS-1$
    # end getError()
    
    def setError(self, errorMessage, errorDetails):
        u"""setError(string, string) -> None
        Setter for the error information.""" #$NON-NLS-1$
    # end setError()

    def cancel(self):
        u"""cancel() -> None
        Cancels the task.""" #$NON-NLS-1$
    # end cancel()
    
    def cancelAsync(self):
        u"""cancelAsync() -> None
        Same as cancel() except does it asynchronously.""" #$NON-NLS-1$
    # end cancelAsync()

    def stop(self):
        u"""stop() -> None
        Called to stop the task prematurely.""" #$NON-NLS-1$
    # end stop()

    def attachListener(self, listener):
        u"""attachListener(IZBackgroundTaskListener) -> None
        Called to attach a listener to the task.""" #$NON-NLS-1$
    # end attachListener()

    def detachListener(self, listener):
        u"""detachListener(IZBackgroundTaskListener) -> None
        Called to detach a listener from the task.""" #$NON-NLS-1$
    # end detachListener()

# end IZBackgroundTask


# ---------------------------------------------------------------------------------------
# This interface defines the background task service listener.  A background task service
# listener will be called back whenever a change is made to the data in the background
# task service (e.g. when a task is added or removed).
# ---------------------------------------------------------------------------------------
class IZBackgroundTaskServiceListener:

    def onTaskAdded(self, task):
        u"""onTaskAdded(IZBackgroundTask) -> None
        Called when a task is added to the service.""" #$NON-NLS-1$
    # end onTaskAdded()

    def onTaskRemoved(self, task):
        u"""onTaskRemoved(IZBackgroundTask) -> None
        Called when a task is removed from the service.""" #$NON-NLS-1$
    # end onTaskRemoved()

    def onTaskCancelled(self, task):
        u"""onTaskCancelled(IZBackgroundTask) -> None
        Called when a task is cancelled.""" #$NON-NLS-1$
    # end onTaskCancelled()

    def onTaskResumed(self, task):
        u"""onTaskResumed(IZBackgroundTask) -> None
        Called when a task is resumed.""" #$NON-NLS-1$
    # end onTaskResumed()

# end IZBackgroundTaskServiceListener


# ---------------------------------------------------------------------------------------
# This interface defines the background task service.  The background task service is
# responsible for managing all of the background tasks.  New tasks can be added, running
# tasks can be cancelled, completed/cancelled tasks can be removed, etc etc.
# ---------------------------------------------------------------------------------------
class IZBackgroundTaskService(IZService):

    def getTasks(self):
        u"""getTasks() -> IZBackgroundTask []
        Gets a list of all IZBackgroundTasks.""" #$NON-NLS-1$
    # end getTasks()

    def getTask(self, taskId):
        u"""getTask(string) -> IZBackgroundTask
        Gets an IZBackgroundTask by its unique ID.""" #$NON-NLS-1$
    # end getTask()

    def addTask(self, task):
        u"""addTask(IZBackgroundTask) -> None
        Adds a new task to the service.  This method also
        starts the task running.""" #$NON-NLS-1$
    # end addTask()
    
    # FIXME (EPW) need "pauseTask"

    def cancelTask(self, taskId, removeFlag = False):
        u"""cancelTask(string, boolean?) -> None
        Cancels the running task with the given ID (optionally 
        removing the task).""" #$NON-NLS-1$
    # end cancelTask()

    def removeTask(self, taskId):
        u"""removeTask(string) -> None
        Removes the task with the given ID.  This will throw an 
        exception if the task is still running or not found.""" #$NON-NLS-1$
    # end removeTask()

    def resumeTask(self, taskId, listener = None):
        u"""resumeTask(string, IZBackgroundTaskListener) -> None
        - Resumes a task that was stopped or cancelled (only if the task is resumable).  
        - Raises an exception if the task cannot be resumed.  
        - Returns the task that was resumed.
        - Optionally attaches a provided listener to the task prior to resuming it.""" #$NON-NLS-1$
    # end resumeTask()

    def addListener(self, listener):
        u"""addListener(IZBackgroundTaskServiceListener) -> None
        Adds a background task service listener.""" #$NON-NLS-1$
    # end addListener()

    def removeListener(self, listener):
        u"""removeListener(IZBackgroundTaskServiceListener) -> None
        Removes a background task service listener.""" #$NON-NLS-1$
    # end removeListener()

# end IZBackgroundTaskService

