from zoundry.appframework.messages import _extstr
from zoundry.appframework.services.backgroundtask.backgroundtask import IZBackgroundTaskListener
from zoundry.appframework.ui.events.commonevents import ZEVT_REFRESH
from zoundry.appframework.ui.util.fontutil import getDefaultFontBold
from zoundry.appframework.ui.util.uiutil import fireRefreshEvent
from zoundry.appframework.ui.widgets.controls.common.panel import ZTransparentPanel
import wx

# ------------------------------------------------------------------------------------
# A panel that displays some widgets associated with downloading a dictionary (a
# progress meter, cancel button, etc).
# ------------------------------------------------------------------------------------
class ZDictionaryDownloadPanel(ZTransparentPanel, IZBackgroundTaskListener):
    
    def __init__(self, parent):
        self.parent = parent
        self.complete = False
        self.cancelled = False
        self.task = None

        wx.Panel.__init__(self, parent, wx.ID_ANY)
        
        self._createWidgets()
        self._bindWidgetEvents()
        self._layoutWidgets()
    # end __init__()
    
    def _createWidgets(self):
        self.titleLabel = wx.StaticText(self, wx.ID_ANY, u"") #$NON-NLS-1$
        self.titleLabel.SetFont(getDefaultFontBold())
        self.progressMeter = wx.Gauge(self, wx.ID_ANY, 100, size = wx.Size(-1, 12))
        self.progressText = wx.StaticText(self, wx.ID_ANY, u"") #$NON-NLS-1$
        self.cancelButton = wx.Button(self, wx.ID_ANY, _extstr(u"dictdownloadpanel.Cancel")) #$NON-NLS-1$
    # end _createWidgets()
    
    def _bindWidgetEvents(self):
        self.Bind(wx.EVT_BUTTON, self.onCancelButton, self.cancelButton)
        self.Bind(ZEVT_REFRESH, self.onRefresh, self)
    # end _bindWidgetEvents()

    def _layoutWidgets(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.titleLabel, 0, wx.EXPAND | wx.ALL, 2)
        sizer.Add(self.progressMeter, 0, wx.EXPAND | wx.ALL, 2)
        sizer.Add(self.progressText, 0, wx.EXPAND | wx.ALL, 2)

        panelSizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY), wx.HORIZONTAL)
        panelSizer.AddSizer(sizer, 1, wx.EXPAND | wx.ALL, 5)
        panelSizer.Add(self.cancelButton, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.SetAutoLayout(True)
        self.SetSizer(panelSizer)
        self.Layout()
    # end _layoutWidgets()
    
    def onCancelButton(self, event):
        self.task.cancel()
        event.Skip()
    # end onCancelButton()
    
    def onRefresh(self, event):
        # Null check on the task since it could've been cancelled
        if self.task is not None:
            self.progressMeter.SetValue(self.task.getNumCompletedWorkUnits())
            perc = (self.task.getNumCompletedWorkUnits() * 100) / self.task.getNumWorkUnits()
            self.progressText.SetLabel(u"%s (%d%%)" % (_extstr(u"dictdownloadpanel.Downloading"), perc)) #$NON-NLS-1$ #$NON-NLS-2$
        
        if self.complete:
            self.parent.onDictionaryDownloadComplete(self.task)
            self.task.detachListener(self)
            self.task = None
            self.complete = False
            self.cancelled = False
        elif self.cancelled:
            self.parent.onDictionaryDownloadCancelled()
            self.task.detachListener(self)
            self.task = None
            self.complete = False
            self.cancelled = False

        event.Skip()
    # end onRefresh()
    
    def setTask(self, task):
        self.task = task
        task.attachListener(self)
    # end setTask()
    
    def destroy(self):
        if self.task is not None:
            self.task.detachListener(self)
    # end destroy()

    def onAttached(self, task, numCompletedWorkUnits): #@UnusedVariable
        self.titleLabel.SetLabel(task.getName())
        self.progressMeter.SetRange(task.getNumWorkUnits())
        self.progressMeter.SetValue(numCompletedWorkUnits)
    # end onAttached()

    def onWorkDone(self, task, amount, text): #@UnusedVariable
        fireRefreshEvent(self)
    # end onWorkDone()

    def onComplete(self, task): #@UnusedVariable
        self.complete = True
        fireRefreshEvent(self)
    # end onComplete()

    def onStop(self, task):
        pass # FIXME (EPW) impl?
    # end onStop()

    def onCancel(self, task): #@UnusedVariable
        self.cancelled = True
        fireRefreshEvent(self)
    # end onCancel()

    def onError(self, task, errorMessage, errorDetails):
        pass # FIXME (EPW) impl?
    # end onError()
    
# end ZDictionaryDownloadPanel
