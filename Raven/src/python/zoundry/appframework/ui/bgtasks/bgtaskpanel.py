from zoundry.appframework.global_services import getResourceRegistry
from zoundry.appframework.messages import _extstr
from zoundry.appframework.services.backgroundtask.backgroundtask import IZBackgroundTaskListener
from zoundry.appframework.ui.actions.menuaction import ZMenuActionContext
from zoundry.appframework.ui.bgtasks.bgtaskmenus import createBackgroundTaskErrorMenuNode
from zoundry.appframework.ui.bgtasks.bgtaskmenus import createBackgroundTaskInfoMenuNode
from zoundry.appframework.ui.events.commonevents import ZEVT_REFRESH
from zoundry.appframework.ui.util.fontutil import getDefaultFontBold
from zoundry.appframework.ui.util.uiutil import fireRefreshEvent
from zoundry.appframework.ui.widgets.controls.common.imgbutton import ZImageButton
from zoundry.appframework.ui.widgets.controls.common.menu.menu import ZMenu
from zoundry.appframework.ui.widgets.controls.common.menu.menuimpl import ZActiveModelBasedMenuContentProvider
from zoundry.appframework.ui.widgets.controls.common.menu.menuimpl import ZActiveModelBasedMenuEventHandler
from zoundry.appframework.ui.widgets.controls.common.panel import ZTransparentPanel
from zoundry.appframework.ui.widgets.dialogs.standarddialogs import ZShowNotYetImplementedMessage
from zoundry.base.util.locking import ZMutex
from zoundry.base.util.text.textutil import getSafeString
import wx

# ------------------------------------------------------------------------------
# The model used by the bg task panel.
# ------------------------------------------------------------------------------
class ZBackgroundTaskPanelModel:

    def __init__(self):
        self.currentWorkAmount = 0
        self.currentWorkText = u"" #$NON-NLS-1$
        self.running = False
        self.canceling = False
        self.canceled = False
        self.complete = False
        self.error = None
    # end __init__()

    def init(self, task):
        self.currentWorkAmount = task.getNumCompletedWorkUnits()
        self.currentWorkText = u"" #$NON-NLS-1$
        self.running = task.isRunning()
        self.canceling = False
        self.canceled = task.isCancelled()
        self.complete = task.isComplete()
        self.error = task.getError()
    # end init()

    def getCurrentWorkAmount(self):
        return self.currentWorkAmount
    # end getCurrentWorkAmount()

    def setCurrentWorkAmount(self, currentWorkAmount):
        self.currentWorkAmount = currentWorkAmount
    # end setCurrentWorkAmount()
    
    def incrementWorkAmount(self, workAmount):
        self.currentWorkAmount = self.currentWorkAmount + workAmount
    # end incrementWorkAmount()

    def getCurrentWorkText(self):
        return self.currentWorkText
    # end getCurrentWorkText()

    def setCurrentWorkText(self, currentWorkText):
        self.currentWorkText = currentWorkText
    # end setCurrentWorkText()

    def getError(self):
        return self.error
    # end getError()
    
    def setError(self, error):
        self.error = error
    # end setError()

    def hasError(self):
        return self.error is not None
    # end hasError()

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

    def isCancelled(self):
        return self.canceled
    # end isCancelled()

    def setCanceled(self, canceled):
        self.canceled = canceled
    # end setCanceled()

    def isComplete(self):
        return self.complete
    # end isComplete()

    def setComplete(self, complete):
        self.complete = complete
    # end setComplete()

# end ZBackgroundTaskPanelModel


# ------------------------------------------------------------------------------
# The panel that displays the information for a given background task.
#
# FIXME (EPW) incomplete impl of ZBackgroundTaskPanel - need to handle Stop,
# Pause, Resume, etc...
# ------------------------------------------------------------------------------
class ZBackgroundTaskPanel(ZTransparentPanel, IZBackgroundTaskListener):

    def __init__(self, parentModel, task, parent):
        self.parentModel = parentModel
        self.model = ZBackgroundTaskPanelModel()
        self.mutex = ZMutex()
        self.task = task

        ZTransparentPanel.__init__(self, parent, wx.ID_ANY)
        self.task.attachListener(self)

        self._initPanel()
        self.refresh()
    # end __init__()

    def _initPanel(self):
        self._createPanelWidgets()
        self._layoutPanelWidgets()
        self._bindWidgetEvents()
        self._populatePanelWidgets()
    # end _initPanel()

    def _createPanelWidgets(self):
        self.titleText = wx.StaticText(self, wx.ID_ANY, self.task.getName())
        self.titleText.SetFont(getDefaultFontBold())

        startTime = u"    %s %s" % (_extstr(u"bgtaskpanel.StartedOn"), self.task.getStartTime().toString(u"%c", True)) #$NON-NLS-2$ #$NON-NLS-1$ #$NON-NLS-3$
        self.startTimeText = wx.StaticText(self, wx.ID_ANY, startTime)

        errorBmp = getResourceRegistry().getBitmap(u"images/dialogs/bgtasks/manager/error-glyph.png") #$NON-NLS-1$
        self.errorGlyph = ZImageButton(self, errorBmp, True)
        infoBmp = getResourceRegistry().getBitmap(u"images/dialogs/bgtasks/manager/info-glyph.png") #$NON-NLS-1$
        self.infoGlyph = ZImageButton(self, infoBmp, True)
        stopBmp = getResourceRegistry().getBitmap(u"images/dialogs/bgtasks/manager/stop-glyph.png") #$NON-NLS-1$
        self.stopGlyph = ZImageButton(self, stopBmp, True)

        # Progress widgets - only visible while task is running.
        self.progressGauge = wx.Gauge(self, wx.ID_ANY, self.task.getNumWorkUnits())
        self.progressGauge.SetSizeHints(-1, 14)
        self.progressText = wx.StaticText(self, wx.ID_ANY, u"") #$NON-NLS-1$
        self.statusText = wx.StaticText(self, wx.ID_ANY, u"") #$NON-NLS-1$

        self.cancelButton = ZImageButton(self, getResourceRegistry().getBitmap(u"images/dialogs/bgtasks/manager/cancel.png")) #$NON-NLS-1$
        self.cancelButton.SetToolTipString(_extstr(u"bgtaskpanel.CancelTask")) #$NON-NLS-1$
        self.pauseButton = ZImageButton(self, getResourceRegistry().getBitmap(u"images/dialogs/bgtasks/manager/pause.png")) #$NON-NLS-1$
        self.pauseButton.SetToolTipString(_extstr(u"bgtaskpanel.PauseTask")) #$NON-NLS-1$

        # Widgets that are only shown when the task is complete
        self.endTimeText = wx.StaticText(self, wx.ID_ANY, u"") #$NON-NLS-1$

        self.removeButton = ZImageButton(self, getResourceRegistry().getBitmap(u"images/dialogs/bgtasks/manager/remove.png")) #$NON-NLS-1$
        self.removeButton.SetToolTipString(_extstr(u"bgtaskpanel.RemoveTask")) #$NON-NLS-1$

        self.staticLine = wx.StaticLine(self)
    # end _createPanelWidgets()

    def _layoutPanelWidgets(self):
        leftSizer = wx.BoxSizer(wx.VERTICAL)
        rightSizer = wx.BoxSizer(wx.HORIZONTAL)

        titleSizer = wx.BoxSizer(wx.HORIZONTAL)
        titleSizer.Add(self.errorGlyph, 0, wx.EXPAND | wx.RIGHT, 5)
        titleSizer.Add(self.infoGlyph, 0, wx.EXPAND | wx.RIGHT, 5)
        titleSizer.Add(self.stopGlyph, 0, wx.EXPAND | wx.RIGHT, 5)
        titleSizer.Add(self.titleText, 1, wx.ALIGN_CENTER_VERTICAL)

        leftSizer.AddSizer(titleSizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 2)
        leftSizer.Add(self.startTimeText, 0, wx.EXPAND | wx.TOP, 2)
        leftSizer.Add(self.progressGauge, 0, wx.EXPAND | wx.ALL, 2)
        leftSizer.Add(self.progressText, 0, wx.EXPAND | wx.ALL, 2)
        leftSizer.Add(self.statusText, 0, wx.EXPAND | wx.ALL, 2)
        leftSizer.Add(self.endTimeText, 0, wx.EXPAND | wx.BOTTOM, 2)

        rightSizer.Add(self.pauseButton, 0, wx.EXPAND | wx.ALL, 2)
        rightSizer.Add(self.cancelButton, 0, wx.EXPAND | wx.ALL, 2)
        rightSizer.Add(self.removeButton, 0, wx.EXPAND | wx.ALL, 2)

        horSizer = wx.BoxSizer(wx.HORIZONTAL)
        horSizer.AddSizer(leftSizer, 1, wx.EXPAND | wx.ALL, 5)
        horSizer.AddSizer(rightSizer, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddSizer(horSizer, 0, wx.EXPAND | wx.ALL, 5)

        panelSizer = wx.BoxSizer(wx.VERTICAL)
        panelSizer.AddSizer(sizer, 0, wx.EXPAND)
        panelSizer.Add(self.staticLine, 0, wx.EXPAND)

        self.SetSizer(panelSizer)
        self.SetAutoLayout(True)
    # end _layoutPanelWidgets()

    def _bindWidgetEvents(self):
        self.Bind(wx.EVT_BUTTON, self.onCancelButton, self.cancelButton)
        self.Bind(wx.EVT_BUTTON, self.onPauseButton, self.pauseButton)
        self.Bind(wx.EVT_BUTTON, self.onRemoveButton, self.removeButton)
        self.Bind(wx.EVT_BUTTON, self.onInfoGlyphButton, self.infoGlyph)
        self.Bind(wx.EVT_BUTTON, self.onErrorGlyphButton, self.errorGlyph)
        self.Bind(wx.EVT_BUTTON, self.onStopGlyphButton, self.stopGlyph)
        self.Bind(ZEVT_REFRESH, self.onZoundryRefresh, self)
    # end _bindWidgetEvents()

    def _populatePanelWidgets(self):
        pass
    # ene _populatePanelWidgets()

    def refresh(self):
        self.statusText.SetLabel(self.model.getCurrentWorkText())
        self.progressText.SetLabel(self._formatProgressText())
        self.progressGauge.SetValue(self.model.getCurrentWorkAmount())

        if self.model.hasError():
            self.errorGlyph.SetToolTipString(getSafeString(self.model.getError()[0]))

        endTime = u"" #$NON-NLS-1$
        if self.model.isComplete() and self.task.getEndTime() is not None:
            endTime = u"%s %s" % (_extstr(u"bgtaskpanel.EndedOn"), self.task.getEndTime().toString(u"%c", True)) #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$
        elif self.model.isCancelled():
            endTime = u"(%s)" % _extstr(u"bgtaskpanel.Cancelled") #$NON-NLS-1$ #$NON-NLS-2$
        endTime = u"    %s" % endTime #$NON-NLS-1$
        self.endTimeText.SetLabel(endTime)

        self._hideShowWidgets()

        self.Layout()
        self.GetParent().Layout()
    # end refresh()

    def _hideShowWidgets(self):
        self.errorGlyph.Show(self.model.hasError())
        self.stopGlyph.Show(self.model.isCancelled())
        self.infoGlyph.Show(not self.model.hasError() and not self.model.isRunning() and not self.model.isCancelled())

        self.endTimeText.Show(self.model.isComplete())

        self.progressGauge.Show(self.model.isRunning())
        self.progressText.Show(self.model.isRunning())
        self.statusText.Show(self.model.isRunning())
        self.pauseButton.Show(self.model.isRunning())
        self.cancelButton.Show(self.model.isRunning())
        self.removeButton.Show(self._shouldShowRemoveButton())
        self.pauseButton.Show(self.model.isRunning() and self.task.isResumable())
    # end _hideShowWidgets()
    
    def _shouldShowRemoveButton(self):
        if self.model.isComplete() or self.model.hasError():
            return True
        if not self.model.isRunning() and not self.task.isResumable():
            return True
        return False
    # end _shouldShowRemoveButton()

    def onPauseButton(self, event):
        ZShowNotYetImplementedMessage(self)
        event.Skip()
    # end onPauseButton()

    def onCancelButton(self, event):
        ZShowNotYetImplementedMessage(self)
        event.Skip()
    # end onCancelButton()

    def onRemoveButton(self, event):
        self.parentModel.removeTask(self.task)
        event.Skip()
    # end onRemoveButton()

    def onInfoGlyphButton(self, event):
        menuNode = createBackgroundTaskInfoMenuNode(self.task)
        self._popupGlyphMenu(menuNode, self.infoGlyph)
        event.Skip()
    # end onInfoGlyphButton()

    def onErrorGlyphButton(self, event):
        menuNode = createBackgroundTaskErrorMenuNode(self.task)
        self._popupGlyphMenu(menuNode, self.errorGlyph)
        event.Skip()
    # end onErrorGlyphButton()

    def onStopGlyphButton(self, event):
        menuNode = createBackgroundTaskInfoMenuNode(self.task)
        self._popupGlyphMenu(menuNode, self.stopGlyph)
        event.Skip()
    # end onInfoGlyphButton()
    
    def onZoundryRefresh(self, event):
        self.refresh()
        event.Skip()
    # end onZoundryRefresh()

    def _popupGlyphMenu(self, menuNode, glyph):
        context = ZMenuActionContext(self)
        provider = ZActiveModelBasedMenuContentProvider(menuNode, context)
        handler = ZActiveModelBasedMenuEventHandler(context)
        menu = ZMenu(self, menuNode, provider, handler)
        (x, y) = glyph.GetPositionTuple() #@UnusedVariable
        (w, h) = glyph.GetSizeTuple() #@UnusedVariable
        self.PopupMenuXY(menu, x, y + h - 1)
    # end _popupGlyphMenu()

    def onAttached(self, task, numCompletedWorkUnits): #@UnusedVariable
        self.mutex.acquire()
        try:
            self.model.init(task)
        finally:
            self.mutex.release()
    # end onAttached()

    def onWorkDone(self, task, amount, text): #@UnusedVariable
        self.mutex.acquire()
        try:
            self.model.incrementWorkAmount(amount)
            self.model.setCurrentWorkText(text)
        finally:
            self.mutex.release()
        fireRefreshEvent(self)
    # end onWorkDone()

    def onComplete(self, task): #@UnusedVariable
        self.mutex.acquire()
        try:
            self.model.setComplete(True)
            self.model.setRunning(False)
        finally:
            self.mutex.release()
        fireRefreshEvent(self)
    # end onComplete()

    def onStop(self, task):
        self.onComplete(task)
    # end onStop()

    def onCancel(self, task): #@UnusedVariable
        self.mutex.acquire()
        try:
            self.model.setCanceled(True)
            self.model.setRunning(False)
        finally:
            self.mutex.release()
        fireRefreshEvent(self)
    # end onCancel()

    def onError(self, task, errorMessage, errorDetails): #@UnusedVariable
        self.mutex.acquire()
        try:
            self.model.setError( (errorMessage, errorDetails) )
            self.model.setRunning(False)
        finally:
            self.mutex.release()
        fireRefreshEvent(self)
    # end onError()

    def _formatProgressText(self):
        # Avoid possible divide by 0 error
        if self.model.getCurrentWorkAmount() == 0:
            perc = 0
        else:
            perc = (self.model.getCurrentWorkAmount() * 100) / self.task.getNumWorkUnits()
        return _extstr(u"bgtaskpanel.RunningPercent") % perc #$NON-NLS-1$
    # end _formatProgressText()

    def destroy(self):
        self.task.detachListener(self)
    # end __del__()

# end ZBackgroundTaskPanel
