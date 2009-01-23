from zoundry.appframework.global_services import getLoggerService
from zoundry.appframework.messages import _extstr
from zoundry.appframework.services.backgroundtask.backgroundtask import IZBackgroundTask
from zoundry.appframework.services.backgroundtask.backgroundtask import IZBackgroundTaskListener
from zoundry.appframework.ui.util.uiutil import ZMethodRunnable
from zoundry.appframework.ui.util.uiutil import fireRefreshEvent
from zoundry.appframework.ui.util.uiutil import fireUIExecEvent
from zoundry.appframework.ui.widgets.controls.progress import ZProgressLabelCtrl
from zoundry.appframework.ui.widgets.dialogs.header import ZHeaderDialog
from zoundry.appframework.ui.widgets.dialogs.standarddialogs import ZShowErrorMessage
from zoundry.base.util.locking import ZMutex
from zoundry.base.util.text.textutil import getSafeString
import wx

OPEN = 0
DETACHING = 1
DETACHED = 2

# ------------------------------------------------------------------------------
# Model used by the background task dialog.
# ------------------------------------------------------------------------------
class ZBackgroundTaskProgressDialogModel:

    def __init__(self):
        self.currentWorkAmount = 0
        self.currentWorkText = u"" #$NON-NLS-1$
        self.dialogState = OPEN
        self.running = False
        self.canceling = False
    # end __init__()

    def getDialogState(self):
        return self.dialogState
    # end getDialogState()

    def setDialogState(self, dialogState):
        self.dialogState = dialogState
    # end setDialogState()

    def setDetaching(self):
        if self.dialogState == OPEN:
            self.dialogState = DETACHING
    # end setDetaching()

    def setDetached(self):
        self.dialogState = DETACHED
    # end setDetached()
    
    def isDetaching(self):
        return self.dialogState == DETACHING
    # end isDetaching()

    def isDetached(self):
        return self.dialogState == DETACHED
    # end isDetached()

    def getCurrentWorkAmount(self):
        return self.currentWorkAmount
    # end getCurrentWorkAmount()

    def setCurrentWorkAmount(self, currentWorkAmount):
        self.currentWorkAmount = currentWorkAmount
    # end setCurrentWorkAmount()

    def getCurrentWorkText(self):
        return self.currentWorkText
    # end getCurrentWorkText()

    def setCurrentWorkText(self, currentWorkText):
        self.currentWorkText = currentWorkText
    # end setCurrentWorkText()

    def isRunning(self):
        return self.running
    # end isRunning()

    def setRunning(self, running):
        self.running = running
    # end setRunning()

    def isCanceling(self):
        return self.canceling
    # end isCanceling()

    def setCanceling(self, canceling):
        self.canceling = canceling
    # end setCanceling()

# end ZBackgroundTaskProgressDialogModel


# ------------------------------------------------------------------------------
# Generic dialog that shows a background task.
# ------------------------------------------------------------------------------
class ZBackgroundTaskProgressDialog(ZHeaderDialog, IZBackgroundTaskListener):

    def __init__(self, parent, bgTask, title, description, imagePath):
        self.title = title
        self.description = description
        self.bgTask = bgTask
        self.imagePath = imagePath

        # This is here for intellisense purposes.
        if self.bgTask is None and False:
            self.bgTask = IZBackgroundTask()

        self.mutex = ZMutex(u"BGTaskDialogMTX") #$NON-NLS-1$

        # Dialog state - can be modified by multiple threads and should
        # be protected by the above mutex.
        self.model = ZBackgroundTaskProgressDialogModel()

        ZHeaderDialog.__init__(self, parent, wx.ID_ANY, title)

        size = self.GetBestSize()
        if size.GetWidth() < 500:
            size.SetWidth(500)
        self.SetSize(size)

        self.bgTask.attachListener(self)
    # end __init__()

    def _createNonHeaderWidgets(self):
        self.progressCtrl = ZProgressLabelCtrl(self, u"") #$NON-NLS-1$
        self.progressGauge = wx.Gauge(self, wx.ID_ANY, self.bgTask.getNumWorkUnits())
        self.progressGauge.SetSizeHints(-1, 16)
        self.workTextCtrl = wx.StaticText(self, wx.ID_ANY, u"") #$NON-NLS-1$

        self.staticLine = wx.StaticLine(self, wx.HORIZONTAL)
    # end _createNonHeaderWidgets()

    def _populateNonHeaderWidgets(self):
        pass
    # end _populateNonHeaderWidgets()

    def _layoutNonHeaderWidgets(self):
        sizer = wx.BoxSizer(wx.VERTICAL)

        sizer.Add(self.progressGauge, 0, wx.EXPAND | wx.ALL, 2)
        sizer.Add(self.progressCtrl, 0, wx.EXPAND | wx.ALL, 2)
        sizer.Add(self.workTextCtrl, 0, wx.EXPAND | wx.ALL, 2)
        sizer.Add(self.staticLine, 0, wx.EXPAND | wx.TOP, 5)

        return sizer
    # end _layoutNonHeaderWidgets()

    def _bindWidgetEvents(self):
        self._bindOkButton(self.onOK)
        self._bindCancelButton(self.onUiCancel)
        self._bindRefreshEvent(self.onRefresh)
    # end _bindWidgetEvents()

    def _getOKButtonLabel(self):
        return _extstr(u"bgtaskprogressdialog.RunInBackground") #$NON-NLS-1$
    # end _getOKButtonLabel()

    def _setInitialFocus(self):
        self.FindWindowById(wx.ID_OK).SetFocus()
    # end _setInitialFocus()

    def _getHeaderTitle(self):
        return self.title
    # end _getHeaderTitle()

    def _getHeaderMessage(self):
        return self.description
    # end _getHeaderMessage()

    def _getHeaderImagePath(self):
        return self.imagePath
    # end _getHeaderImagePath()

    def _doEndModal(self, code):
        try:
            self.EndModal(code)
            return self.bgTask.hasError()
        except Exception, e:
            getLoggerService().exception(e)
        return False
    # end _doEndModal()

    def onRefresh(self, event):
        showError = False
        isDetached = False
        isDetaching = False
        
        self.mutex.acquire()
        try:
            # Refresh the UI
            self.refresh()
            
            isDetached = self.model.isDetached()
            isDetaching = self.model.isDetaching()
        finally:
            self.mutex.release()

        # If we have successfully detached, close the dialog
        if isDetached:
            showError = self._doEndModal(wx.ID_OK)
        # Should we detach from the listener and start closing down?
        elif isDetaching:
            self.bgTask.detachListener(self)
            self.model.setDetached()
            fireRefreshEvent(self)

        # If there was an error - show it.
        if showError:
            (msg, details) = self.bgTask.getError()
            method = ZShowErrorMessage
            args = [None, msg, details]
            runnable = ZMethodRunnable(method, args)
            fireUIExecEvent(runnable, self.GetParent())

        event.Skip()
    # end onRefresh()

    def onOK(self, event): #@UnusedVariable
        self.mutex.acquire()
        try:
            self.model.setDetaching()
            fireRefreshEvent(self)
        finally:
            self.mutex.release()
    # end onOK()

    def onUiCancel(self, event): #@UnusedVariable
        self.mutex.acquire()
        try:
            self.model.setCanceling(True)
            self.model.setDetaching()
            fireRefreshEvent(self)
            fireUIExecEvent(ZMethodRunnable(self._cancelBackgroundTask), self)
        finally:
            self.mutex.release()
    # end onUiCancel()

    def _cancelBackgroundTask(self):
        if self.bgTask and self.bgTask.isRunning():
            self.bgTask.cancelAsync()
    # end _cancelBackgroundTask()

    def refresh(self):
        self.progressCtrl.setLabel(self._formatProgressText())
        self.progressGauge.SetValue(self.model.getCurrentWorkAmount())
        if self.model.isCanceling():
            self.workTextCtrl.SetLabel(_extstr(u"bgtaskprogressdialog.Cancelling")) #$NON-NLS-1$
        else:
            self.workTextCtrl.SetLabel(self.model.getCurrentWorkText())
        if self.model.isRunning() and not self.progressCtrl.isRunning():
            self.progressCtrl.start()
        if not self.model.isRunning() and self.progressCtrl.isRunning():
            self.progressCtrl.stop()
        if not self.model.isRunning():
            self._getOkButton().Show(False)
            self._getCancelButton().SetLabel(_extstr(u"Close")) #$NON-NLS-1$
    # end refresh()

    def _formatProgressText(self):
        # Avoid possible divide by 0 error
        if self.bgTask.getNumWorkUnits() == 0:
            perc = 0
        else:
            perc = (self.bgTask.getNumCompletedWorkUnits() * 100) / self.bgTask.getNumWorkUnits()
        return _extstr(u"bgtaskpanel.RunningPercent") % perc #$NON-NLS-1$
    # end _formatProgressText()

    def onAttached(self, task, numCompletedWorkUnits): #@UnusedVariable
        self.mutex.acquire()
        try:
            self.model.setCurrentWorkText(getSafeString(task.getLastLogMessage()))
            self.model.setCurrentWorkAmount(numCompletedWorkUnits)
            self.model.setRunning(task.isRunning())
        finally:
            self.mutex.release()
            fireRefreshEvent(self)
    # end onAttached()

    def onStarted(self, task, workAmount): #@UnusedVariable
        self.mutex.acquire()
        try:
            self.model.setRunning(True)
        finally:
            self.mutex.release()
            fireRefreshEvent(self)
    # end onStarted()

    def onWorkDone(self, task, amount, text): #@UnusedVariable
        self.mutex.acquire()
        try:
            newWorkAmount = self.model.getCurrentWorkAmount() + amount
            self.model.setCurrentWorkAmount(newWorkAmount)
            self.model.setCurrentWorkText(getSafeString(text))
        finally:
            self.mutex.release()
            fireRefreshEvent(self)
    # end onWorkDone()

    def onComplete(self, task):
        self.mutex.acquire()
        try:
            self.model.setCurrentWorkAmount(task.getNumWorkUnits())
            self.model.setCurrentWorkText(_extstr(u"bgtaskprogressdialog.Done_")) #$NON-NLS-1$
            self.model.setRunning(False)
            self.model.setDetaching()
        finally:
            self.mutex.release()
            fireRefreshEvent(self)
    # end onComplete()

    def onStop(self, task): #@UnusedVariable
        self.mutex.acquire()
        try:
            self.model.setRunning(False)
        finally:
            self.mutex.release()
            fireRefreshEvent(self)
    # end onStop()

    def onCancel(self, task): #@UnusedVariable
        self.mutex.acquire()
        try:
            self.model.setRunning(False)
            self.model.setDetaching()
        finally:
            self.mutex.release()
            fireRefreshEvent(self)
    # end onCancel()

    def onError(self, task, errorMessage, errorDetails): #@UnusedVariable
        self.mutex.acquire()
        try:
            self.model.setRunning(False)
            self.model.setDetaching()
        finally:
            self.mutex.release()
            fireRefreshEvent(self)
    # end onError()

# end ZBackgroundTaskProgressDialog
