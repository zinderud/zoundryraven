from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.messages import _extstr
from zoundry.appframework.services.ztest.ztest import IZTestListener
from zoundry.appframework.ui.events.commonevents import ZEVT_REFRESH
from zoundry.appframework.ui.events.ztestevents import ZTestCompletedEvent
from zoundry.appframework.ui.events.ztestevents import ZTestFailedEvent
from zoundry.appframework.ui.util.uiutil import fireRefreshEvent
from zoundry.appframework.ui.widgets.controls.htmllist import IZHtmlListBoxContentProvider
from zoundry.appframework.ui.widgets.controls.htmllist import ZHtmlListBox
from zoundry.appframework.ui.widgets.dialogs.standarddialogs import ZShowExceptionMessage
from zoundry.base.util.zthread import ZThread
import wx

# ----------------------------------------------------------------------------------------
# An implementation of a html list box content provider that provides content for the
# Test Progress Panel's html list box control.
# ----------------------------------------------------------------------------------------
class ZTestProgressPanelContentProvider(IZHtmlListBoxContentProvider):

    def __init__(self, ztest):
        self.ztest = ztest
        registry = getApplicationModel().getResourceRegistry()
        self.pendingImagePath = registry.getImagePath(u"images/common/ztest/pending.png") #$NON-NLS-1$
        self.currentImagePath = registry.getImagePath(u"images/common/ztest/current.png") #$NON-NLS-1$
        self.passImagePath = registry.getImagePath(u"images/common/ztest/pass.png") #$NON-NLS-1$
        self.failImagePath = registry.getImagePath(u"images/common/ztest/fail.png") #$NON-NLS-1$
    # end __init__()

    def getNumRows(self):
        return len(self.ztest.getSteps())
    # end getNumRows()

    def getRowHtml(self, rowIndex):
        step = self.ztest.getSteps()[rowIndex]
        imagePath = self.pendingImagePath
        extraHtml = u"" #$NON-NLS-1$
        if step.isExecuting():
            imagePath = self.currentImagePath
            extraHtml = u"<font color='blue'>running</font>" #$NON-NLS-1$
        elif step.isPass():
            imagePath = self.passImagePath
            extraHtml = u"<font color='green'>passed</font>" #$NON-NLS-1$
        elif step.isFail():
            imagePath = self.failImagePath
            extraHtml = u"<font color='red'>failed</font>" #$NON-NLS-1$

        args = ( imagePath, step.getDescription(), extraHtml )
        return u"""<table width="100%%"><tr><td width="1%%" valign="center"><img src="%s" /></td><td align="left" valign="center">%s</td><td align="right">%s</td></table>""" % args #$NON-NLS-1$
    # end getRowHtml()

# end ZTestProgressPanelContentProvider


# ----------------------------------------------------------------------------------------
# This is an extension of a WX Panel which encapsulates the display of the result of a
# IZTest.  This panel contains the visual results of the test.
# ----------------------------------------------------------------------------------------
class ZTestProgressPanel(wx.Panel, IZTestListener):

    def __init__(self, ztest, parent, id = wx.ID_ANY, style = wx.TAB_TRAVERSAL):
        self.ztest = ztest
        self.thread = None
        self.testError = None
        wx.Panel.__init__(self, parent, id = id, style = style)

        self._createWidgets()
        self._bindWidgetEvents()
        self._layoutWidgets()
    # end __init__()

    def _createWidgets(self):
        self.stepListBox = ZHtmlListBox(ZTestProgressPanelContentProvider(self.ztest), self, style = wx.LB_SINGLE | wx.BORDER_SIMPLE)
        self.staticBox = wx.StaticBox(self, wx.ID_ANY, _extstr(u"tpanel.CurrentStatus")) #$NON-NLS-1$
        self.statusCaption1 = wx.StaticText(self, wx.ID_ANY, u"") #$NON-NLS-1$
        self.statusCaption2 = wx.StaticText(self, wx.ID_ANY, u"") #$NON-NLS-1$
    # end _createWidgets()

    def _bindWidgetEvents(self):
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.onDoubleClick, self.stepListBox)
        self.Bind(ZEVT_REFRESH, self.onZoundryRefresh, self)
        self.ztest.addListener(self)
    # end _bindWidgetEvents()

    def _layoutWidgets(self):
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.stepListBox, 1, wx.EXPAND | wx.BOTTOM, 5)
        
        staticSizer = wx.StaticBoxSizer(self.staticBox, wx.VERTICAL)
        staticSizer.Add(self.statusCaption1, 0, wx.EXPAND | wx.ALL, 3)
        staticSizer.Add(self.statusCaption2, 0, wx.EXPAND | wx.ALL, 3)
        
        box.AddSizer(staticSizer, 0, wx.EXPAND | wx.BOTTOM, 5)

        self.SetAutoLayout(True)
        self.SetSizer(box)
    # end _layoutWidgets()

    def getTestError(self):
        return self.testError
    # end getTestError()

    def startTest(self):
        self.thread = ZThread(self.ztest, u"ZTestThread", True) #$NON-NLS-1$
        self.thread.start()
    # end startTest()

    def cancelTest(self):
        self.ztest.removeListener(self)
        self.ztest.cancel()
        self.statusCaption1.SetLabel(_extstr(u"tpanel.TestCancelled")) #$NON-NLS-1$
        self.statusCaption2.SetLabel(u"") #$NON-NLS-1$
    # end cancelTest()
    
    def onDoubleClick(self, event):
        selectedIndex = self.stepListBox.GetSelection()
        step = self.ztest.getSteps()[selectedIndex]
        error = step.getError()
        if error is not None:
            ZShowExceptionMessage(self, error)
        event.Skip()
    # end onDoubleClick()

    def onZoundryRefresh(self, event): #@UnusedVariable
        # Refresh the step ListBox
        self.stepListBox.RefreshAll()
        # Scroll the list box if necessary
        line = self._getCurrentStepLine()
        if not self.stepListBox.IsVisible(line):
            self.stepListBox.ScrollToLine(line)
        # Update the captions
        step = self._getCurrentStep()
        if step:
            self.statusCaption1.SetLabel(_extstr(u"tpanel.RunningTestStepMessage") % (line + 1, len(self.ztest.getSteps()))) #$NON-NLS-1$
            self.statusCaption2.SetLabel(_extstr(u"tpanel.CurrentStep") % step.getDescription()) #$NON-NLS-1$
            pass
        elif self.testError is not None:
            self.statusCaption1.SetLabel(_extstr(u"tpanel.TestFailedMessage")) #$NON-NLS-1$
            self.statusCaption2.SetLabel(u"") #$NON-NLS-1$
        else:
            self.statusCaption1.SetLabel(_extstr(u"tpanel.TestCompletedSuccessfully")) #$NON-NLS-1$
            self.statusCaption2.SetLabel(u"") #$NON-NLS-1$
    # end onZoundryRefresh()

    def onTestStart(self, test): #@UnusedVariable
        fireRefreshEvent(self)
    # end onTestStart()

    def onStepStart(self, test, step): #@UnusedVariable
        fireRefreshEvent(self)
    # end onStepStart()

    def onStepPass(self, test, step): #@UnusedVariable
        fireRefreshEvent(self)
    # end onStepPass()

    def onStepFail(self, test, step, error): #@UnusedVariable
        self.testError = error
        fireRefreshEvent(self)
    # end onStepError()

    def onTestComplete(self, test): #@UnusedVariable
        fireRefreshEvent(self)
        if self.testError is None:
            self._fireTestCompletedEvent()
        else:
            self._fireTestFailedEvent()
    # end onTestComplete()

    def _getCurrentStep(self):
        for step in self.ztest.getSteps():
            if step.isExecuting():
                return step
        return None
    # end _getCurrentStep()

    def _getCurrentStepLine(self):
        counter = 0
        for step in self.ztest.getSteps():
            if step.isExecuting():
                return counter
            counter = counter + 1
        return counter
    # end _getCurrentStepLine()

    def _fireTestCompletedEvent(self):
        event = ZTestCompletedEvent(self.GetId())
        self.GetEventHandler().AddPendingEvent(event)
    # end _fireTestCompletedEvent()

    def _fireTestFailedEvent(self):
        event = ZTestFailedEvent(self.GetId())
        self.GetEventHandler().AddPendingEvent(event)
    # end _fireTestFailedEvent()

# end ZTestProgressPanel
