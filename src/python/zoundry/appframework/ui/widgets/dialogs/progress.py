from zoundry.appframework.messages import _extstr
from zoundry.appframework.ui.events.progress import ZEVT_PROGRESS_CANCEL
from zoundry.appframework.ui.events.progress import ZEVT_PROGRESS_COMPLETE
from zoundry.appframework.ui.events.progress import ZEVT_PROGRESS_ERROR
from zoundry.appframework.ui.events.progress import ZEVT_PROGRESS_EXCEPTION
from zoundry.appframework.ui.events.progress import ZEVT_PROGRESS_STARTED
from zoundry.appframework.ui.events.progress import ZEVT_PROGRESS_WORKDONE
from zoundry.appframework.ui.events.progress import ZProgressCancelEvent
from zoundry.appframework.ui.events.progress import ZProgressCompleteEvent
from zoundry.appframework.ui.events.progress import ZProgressErrorEvent
from zoundry.appframework.ui.events.progress import ZProgressExceptionEvent
from zoundry.appframework.ui.events.progress import ZProgressStartedEvent
from zoundry.appframework.ui.events.progress import ZProgressWorkDoneEvent
from zoundry.appframework.ui.widgets.dialog import ZBaseDialog
from zoundry.appframework.ui.widgets.dialogs.standarddialogs import ZShowErrorMessage
from zoundry.appframework.ui.widgets.dialogs.standarddialogs import ZShowExceptionMessage
from zoundry.base.exceptions import ZAbstractMethodCalledException
from zoundry.base.util.collections import ZListenerSet
from zoundry.base.util.zthread import IZRunnable
from zoundry.base.util.zthread import ZThread
import wx


# -------------------------------------------------------------------------------------
# An interface that must be supported by objects given to the progress dialog.
# -------------------------------------------------------------------------------------
class IZRunnableProgress(IZRunnable):

    def stop(self):
        u"Called to stop the runnable progress prematurely." #$NON-NLS-1$
    # end stop()

    def addListener(self, listener):
        u"Called to add a listener to the runnable progress." #$NON-NLS-1$
    # end addListener()

    def removeListener(self, listener):
        u"Called to remove a listener from the runnable progress." #$NON-NLS-1$
    # end removeListener()

# end IZRunnableProgress


# -------------------------------------------------------------------------------------
# An interface that must be supported listeners of the runnable progress object.
# -------------------------------------------------------------------------------------
class IZRunnableProgressListener:

    def onStarted(self, workAmount):
        u"Called when the runnable progress begins." #$NON-NLS-1$
    # end onStarted()

    def onWorkDone(self, amount, text):
        u"Called during execution of the runnable progress when some amount of work has been done." #$NON-NLS-1$
    # end onWorkDone()

    def onComplete(self):
        u"Called when the runnable progress finishes successfully." #$NON-NLS-1$
    # end onComplete()

    def onCancel(self):
        u"Called when the runnable progress completes due to being cancelled." #$NON-NLS-1$
    # end onCancel()

    def onError(self, error):
        u"Called when an error ocurrs in the runnable progress." #$NON-NLS-1$
    # end onError()

    def onException(self, exception):
        u"Called when an exception ocurrs in the runnable progress." #$NON-NLS-1$
    # end onException()

# end IZRunnableProgressListener


# -------------------------------------------------------------------------------------
# Base class for IZRunnableProgress implementations.
# -------------------------------------------------------------------------------------
class ZAbstractRunnableProgress(IZRunnableProgress):

    def __init__(self):
        self.cancelled = False
        self.listeners = ZListenerSet()
    # end __init__()

    def isCancelled(self):
        return self.cancelled
    # end isCancelled()

    def run(self):
        try:
            workAmount = self._calculateWork()
            self._fireStartedEvent(workAmount)
            self._doRun()
            self._fireCompleteEvent()
        except Exception, e:
            self._fireExceptionEvent(e)
    # end run()

    def _calculateWork(self):
        raise ZAbstractMethodCalledException(self.__class__, u"_calculateWork") #$NON-NLS-1$
    # end _calculateWork()

    def _doRun(self):
        raise ZAbstractMethodCalledException(self.__class__, u"_doRun") #$NON-NLS-1$
    # end _doRun()

    def stop(self):
        self.cancelled = True
    # end stop()

    def addListener(self, listener):
        self.listeners.addListener(listener)
    # end addListener()

    def removeListener(self, listener):
        self.listeners.removeListener(listener)
    # end removeListener()

    def _fireStartedEvent(self, workAmount):
        self.listeners.doCallback(u"onStarted", [workAmount]) #$NON-NLS-1$
    # end _fireStartedEvent()

    def _fireWorkDoneEvent(self, amount, text):
        self.listeners.doCallback(u"onWorkDone", [amount, text]) #$NON-NLS-1$
    # end _fireWorkDoneEvent()

    def _fireCompleteEvent(self):
        self.listeners.doCallback(u"onComplete") #$NON-NLS-1$
    # end _fireCompleteEvent()

    def _fireCancelEvent(self):
        self.listeners.doCallback(u"onCancel") #$NON-NLS-1$
    # end _fireCancelEvent()

    def _fireErrorEvent(self, error):
        self.listeners.doCallback(u"onError", [error]) #$NON-NLS-1$
    # end _fireErrorEvent()

    def _fireExceptionEvent(self, exception):
        self.listeners.doCallback(u"onException", [exception]) #$NON-NLS-1$
    # end _fireExceptionEvent()

# end ZAbstractRunnableProgress


# -------------------------------------------------------------------------------------
# Extends the ZThread class in order to handle unexpected exceptions by calling
# onException() on the listener.
# -------------------------------------------------------------------------------------
class ZProgressDialogThread(ZThread):

    def __init__(self, runnable, listener):
        self.listener = listener
        ZThread.__init__(self, runnable, u"ProgressDialogThread") #$NON-NLS-1$
    # end __init__()

    def _handleException(self, zexception): #@UnusedVariable
        self.listener.onException(zexception)
    # end _handleException()

# end ZProgressDialogThread


# -------------------------------------------------------------------------------------
# A convenience function for running a IZRunnableProgress inside of a standard progress
# dialog.  The return value is either ID_OK or ID_CANCEL.
# -------------------------------------------------------------------------------------
def ZShowProgressDialog(parent, title, runnable):
    dialog = ZProgressDialog(parent, title, runnable)
    dialog.CentreOnScreen()
    rval = dialog.ShowModal()
    dialog.Destroy()
    return rval
# end ZShowProgressDialog()


# -------------------------------------------------------------------------------------
# A generic dialog for showing progress.  This dialog must be created with a title and
# an instance of IZRunnableProgress.
# -------------------------------------------------------------------------------------
class ZProgressDialog(ZBaseDialog, IZRunnableProgressListener):

    def __init__(self, parent, title, runnableProgress):
        self.runnableProgress = runnableProgress
        self.runnableProgress.addListener(self)
        self.thread = ZProgressDialogThread(self.runnableProgress, self)

        ZBaseDialog.__init__(self, parent, wx.ID_ANY, title)
        self.Fit()
        self.thread.start()
    # end __init__()

    def _createContentWidgets(self):
        self.gauge = wx.Gauge(self, wx.ID_ANY, style = wx.GA_HORIZONTAL | wx.GA_SMOOTH, size = wx.Size(350, 16))
        self.text = wx.StaticText(self, wx.ID_ANY, u"") #$NON-NLS-1$
        self.staticLine = wx.StaticLine(self)
    # end _createContentWidgets()

    def _populateContentWidgets(self):
        self.gauge.SetValue(0)
    # end _populateContentWidgets()

    def _layoutContentWidgets(self):
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.gauge, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 8)
        box.Add(self.text, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)
        box.Add(self.staticLine, 0, wx.EXPAND)

        return box
    # end _layoutContentWidgets()

    def _bindWidgetEvents(self):
        self.Bind(wx.EVT_BUTTON, self.OnCancel, id = wx.ID_CANCEL)

        self.Bind(ZEVT_PROGRESS_STARTED, self.onProgressStarted, self)
        self.Bind(ZEVT_PROGRESS_WORKDONE, self.onProgressWorkDone, self)
        self.Bind(ZEVT_PROGRESS_COMPLETE, self.onProgressComplete, self)
        self.Bind(ZEVT_PROGRESS_CANCEL, self.onProgressCancel, self)
        self.Bind(ZEVT_PROGRESS_ERROR, self.onProgressError, self)
        self.Bind(ZEVT_PROGRESS_EXCEPTION, self.onProgressException, self)
    # end _bindWidgetEvents()

    def _getButtonTypes(self):
        return ZBaseDialog.CANCEL_BUTTON
    # end _getButtonTypes()

    def OnCancel(self, event): #@UnusedVariable
        self._enableCancelButton(False)
        self.runnableProgress.stop()
    # end onCancel()

    def onProgressStarted(self, event):
        self.gauge.SetRange(event.getWorkAmount())
        event.Skip()
    # end onProgressStarted()

    def onProgressWorkDone(self, event):
        self.text.SetLabel(event.getText())
        self.gauge.SetValue(self.gauge.GetValue() + event.getAmount())
        event.Skip()
    # end onProgressWorkDone()

    def onProgressComplete(self, event):
        self.gauge.SetValue(self.gauge.GetRange())
        self.EndModal(wx.ID_OK)
        event.Skip()
    # end onProgressComplete()

    def onProgressCancel(self, event):
        self.EndModal(wx.ID_CANCEL)
        event.Skip()
    # end onProgressCancel()

    def onProgressError(self, event):
        ZShowErrorMessage(self, _extstr(u"progress.ErrorEncountered"), event.getError()) #$NON-NLS-1$
        self.EndModal(wx.ID_CANCEL)
        event.Skip()
    # end onProgressError()

    def onProgressException(self, event):
        ZShowExceptionMessage(self, event.getException())
        self.EndModal(wx.ID_CANCEL)
        event.Skip()
    # end onProgressException()

    def EndModal(self, id):
        self.runnableProgress.removeListener(self)
        ZBaseDialog.EndModal(self, id)
    # end EndModal()

    # *********************************************************************************
    # The next several methods represent the IZRunnableProgressListener interface...
    # *********************************************************************************

    def onStarted(self, workAmount):
        event = ZProgressStartedEvent(self.GetId(), workAmount)
        self.GetEventHandler().AddPendingEvent(event)
    # end onStarted()

    def onWorkDone(self, amount, text):
        event = ZProgressWorkDoneEvent(self.GetId(), amount, text)
        self.GetEventHandler().AddPendingEvent(event)
    # end onWorkDone()

    def onComplete(self):
        event = ZProgressCompleteEvent(self.GetId())
        self.GetEventHandler().AddPendingEvent(event)
    # end onComplete()

    def onCancel(self):
        event = ZProgressCancelEvent(self.GetId())
        self.GetEventHandler().AddPendingEvent(event)
    # end onCancel()

    def onError(self, error):
        event = ZProgressErrorEvent(self.GetId(), error)
        self.GetEventHandler().AddPendingEvent(event)
    # end onError()

    def onException(self, exception):
        event = ZProgressExceptionEvent(self.GetId(), exception)
        self.GetEventHandler().AddPendingEvent(event)
    # end onException()

# end ZProgressDialog()
