import os
import traceback
from zoundry.appframework.constants import IZAppServiceIDs
from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.services.backgroundtask.backgroundtask import IZBackgroundTaskListener
from zoundry.appframework.services.backgroundtask.backgroundtask import IZBackgroundTaskServiceListener
from zoundry.appframework.ui.events.commonevents import ZEVT_REFRESH
from zoundry.appframework.ui.util.uiutil import fireRefreshEvent
from zoundry.appframework.ui.widgets.controls.common.statusbar import ZStatusBar
from zoundry.appframework.ui.widgets.controls.common.statusbar import ZStatusBarModel
from zoundry.appframework.ui.widgets.controls.common.statusbar import ZStatusBarModelBasedContentProvider
from zoundry.appframework.ui.widgets.controls.progress import ZProgressLabelCtrl
from zoundry.base.util.locking import ZMutex
from zoundry.base.util.types.list import ZSortedSet
from zoundry.blogapp.messages import _extstr

# ------------------------------------------------------------------------------
# The status bar's model.  Monitors running tasks.
# ------------------------------------------------------------------------------
class ZRavenApplicationStatusBarModel:

    def __init__(self):
        self.runningTasks = ZSortedSet()
        self.dirty = True
        self.statusBarModel = self._createStatusBarModel()
    # end __init__()

    def isDirty(self):
        return self.dirty
    # end isDirty()

    def setDirty(self, dirty):
        self.dirty = dirty
    # end setDirty()

    def _createStatusBarModel(self):
        sbModel = ZStatusBarModel()
        sbModel.addPane(u"bgTaskSummaryPane") #$NON-NLS-1$
        sbModel.setPaneWidth(u"bgTaskSummaryPane", -1) #$NON-NLS-1$
        return sbModel
    # end _createStatusBarModel()

    def getTaskService(self):
        return getApplicationModel().getService(IZAppServiceIDs.BACKGROUND_TASK_SERVICE_ID)
    # end getTaskService()

    def getStatusBarModel(self):
        return self.statusBarModel
    # end getStatusBarModel()

    def createStatusBarProvider(self):
        return ZStatusBarModelBasedContentProvider(self.statusBarModel)
    # end createStatusBarProvider()

    def isRunning(self):
        return len(self.runningTasks) > 0
    # end isRunning()

    def addTask(self, task):
        self.runningTasks.append(task)
        self.dirty = True
    # end addTask()

    def removeTask(self, task):
        self.runningTasks.remove(task)
        self.dirty = True
    # end removeTask()

    def getNumRunningTasks(self):
        return len(self.runningTasks)
    # end getNumRunningTasks()

# end ZRavenApplicationStatusBarModel


# ------------------------------------------------------------------------------
# Custom status bar implementation for the main Raven application window.
# ------------------------------------------------------------------------------
class ZRavenApplicationStatusBar(ZStatusBar, IZBackgroundTaskServiceListener, IZBackgroundTaskListener):

    def __init__(self, parent):
        applicationModel = getApplicationModel()
        userProfile = applicationModel.getUserProfile()
        debugFilePath = os.path.join(userProfile.getLogDirectory(), u"ZRavenApplicationStatusBar.log") #$NON-NLS-1$
        self.debugFile = open(debugFilePath, u"wa") #$NON-NLS-1$
        self._debugMsg(u"== New Debug Session ==") #$NON-NLS-1$

        self.progressCtrl = None
        self.model = ZRavenApplicationStatusBarModel()
        self.mutex = ZMutex(u"ZAppStatusBarMTX") #$NON-NLS-1$
        self._debugMsg(u"Begin Call Super ZStatusBar.__init__") #$NON-NLS-1$
        ZStatusBar.__init__(self, parent, self.model.createStatusBarProvider())
        self._debugMsg(u"Done Call Super ZStatusBar.__init__") #$NON-NLS-1$
        # Attach to any already-running tasks.
        for task in self.model.getTaskService().getTasks():
            if task.isRunning():
                self._debugMsg(u"Attaching self as listner to task %s - %s" % (task.getId(), task.getName()) ) #$NON-NLS-1$
                task.attachListener(self)
        # Listen for new tasks that may show up.
        self._debugMsg(u"Attaching self as listner to task service") #$NON-NLS-1$
        self.model.getTaskService().addListener(self)
        self._debugMsg(u"End  ZRavenApplicationStatusBar.__init__") #$NON-NLS-1$
    # end __init__()

    def _debugMsg(self, msg):
        try:
            self.debugFile.write(u"*****>>>>> %s\n" % msg) #$NON-NLS-1$
            self.debugFile.flush()
        except:
            pass
    # end _debugMsg()

    def _debugProgressCtrl(self):
        if not self.progressCtrl:
            stack = traceback.extract_stack()
            self._debugMsg( unicode(stack) )
        return self.progressCtrl is not None
    # end _debugProgressCtrl()

    def _createCustomWidgets(self):
        self.progressCtrl = ZProgressLabelCtrl(self, u"", True) #$NON-NLS-1$
        self._debugMsg(u"Done _createCustomWidgets") #$NON-NLS-1$
    # end _createCustomWidgets()

    def _bindCustomWidgets(self):
        self.Bind(ZEVT_REFRESH, self.onRefresh, self)
        self._debugMsg(u"Done _bindCustomWidgets") #$NON-NLS-1$
    # end _bindCustomWidgets()

    def _refreshPane(self, paneIdx):
        if not self._debugProgressCtrl():
            return
        if paneIdx == 0:
            numTasks = self.model.getNumRunningTasks()
            progressText = u"%d %s" % (numTasks, _extstr(u"appstatusbar.RunningTasks")) #$NON-NLS-1$ #$NON-NLS-2$
            if numTasks == 0:
                progressText = _extstr(u"appstatusbar.NoRunningTasks") #$NON-NLS-1$
            self.progressCtrl.setLabel(progressText)
    # end _refreshPane()

    def _repositionPane(self, paneIdx, rect):
        if not self._debugProgressCtrl():
            return
        if paneIdx == 0:
            self.progressCtrl.SetPosition( (rect.x + 4, rect.y + 1) )
            self.progressCtrl.SetSize( (rect.width - 5, rect.height - 2) )
    # end _repositionPane()

    def onRefresh(self, event):
        self.mutex.acquire()
        try:
            if self._debugProgressCtrl() and self.model.isDirty():
                if self.model.isRunning():
                    self.progressCtrl.start()
                else:
                    self.progressCtrl.stop()
                self.refresh()
                self.model.setDirty(False)
        finally:
            self.mutex.release()
        event.Skip()
    # end onRefresh()

    def onTaskAdded(self, task):
        self.mutex.acquire()
        try:
            task.attachListener(self)
        finally:
            self.mutex.release()
        fireRefreshEvent(self)
    # end onTaskAdded()

    def onTaskRemoved(self, task):
        self.mutex.acquire()
        try:
            self.model.removeTask(task)
            task.detachListener(self)
        finally:
            self.mutex.release()
        fireRefreshEvent(self)
    # end onTaskRemoved()

    def onAttached(self, task, numCompletedWorkUnits): #@UnusedVariable
        self.mutex.acquire()
        try:
            if task.isRunning():
                self.model.addTask(task)
        finally:
            self.mutex.release()
        fireRefreshEvent(self)
    # end onAttached()

    def onStarted(self, task, workAmount): #@UnusedVariable
        self.mutex.acquire()
        try:
            self.model.addTask(task)
        finally:
            self.mutex.release()
        fireRefreshEvent(self)
    # end onStarted()

    def onComplete(self, task):
        self.mutex.acquire()
        try:
            self.model.removeTask(task)
        finally:
            self.mutex.release()
        fireRefreshEvent(self)
    # end onComplete()

    def onStop(self, task):
        self.mutex.acquire()
        try:
            self.model.removeTask(task)
        finally:
            self.mutex.release()
        fireRefreshEvent(self)
    # end onStop()

    def onCancel(self, task):
        self.mutex.acquire()
        try:
            self.model.removeTask(task)
        finally:
            self.mutex.release()
        fireRefreshEvent(self)
    # end onCancel()

    def onError(self, task, errorMessage, errorDetails): #@UnusedVariable
        self.mutex.acquire()
        try:
            self.model.removeTask(task)
        finally:
            self.mutex.release()
        fireRefreshEvent(self)
    # end onError()

    def reposition(self):
        self._debugMsg(u"start 'reposition()'") #$NON-NLS-1$
        try:
            ZStatusBar.reposition(self)
        finally:
            self._debugMsg(u"end 'reposition()'") #$NON-NLS-1$
    # end reposition()

# end ZCustomStatusBar
