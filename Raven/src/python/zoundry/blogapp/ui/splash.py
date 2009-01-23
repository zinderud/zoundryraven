from zoundry.appframework.global_services import getResourceRegistry
from zoundry.appframework.ui.events.commonevents import ZEVT_UIEXEC
from zoundry.appframework.ui.util.uiutil import fireUIExecEvent
from zoundry.appframework.ui.widgets.controls.common.bitmap import ZStaticBitmap
from zoundry.base.util.schematypes import ZSchemaDateTime
from zoundry.base.util.zthread import IZRunnable
from zoundry.blogapp import version
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.startup import IRavenApplicationStartupListener
from zoundry.appframework.ui.util.fontutil import getDefaultFontBold
from zoundry.appframework.util.portableutil import isPortableEnabled
import wx

# -------------------------------------------------------------------------------------------
# This is the window that opens when the application is starting up.  This startup
# (or splash) window will show the startup progress as well as a startup/welcome
# image.  This window is also a listener to startup events from the RavenApplicationStartup
# object and its appearance will change based on those events.
# -------------------------------------------------------------------------------------------
class ZStartupWindow(wx.Frame, IRavenApplicationStartupListener):

    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, _extstr(u"splash.StartingZoundryRaven"), size=(-1, 290), #$NON-NLS-1$
                          style = wx.MINIMIZE_BOX | wx.FRAME_TOOL_WINDOW | wx.CAPTION | wx.NO_FULL_REPAINT_ON_RESIZE)
        self._createWidgets()
        self._bindWidgetEvents()
        
        width = self.panel.GetBestSizeTuple()[0]
        self.SetSizeWH(width, -1)
        
        self.CentreOnScreen()
        self.Show(True)
    # end __init__()

    def _createWidgets(self):
        self.panel = wx.Panel(self, wx.ID_ANY)
        
        self.splashPanel = self._createSplashPanel(self.panel)

        self.staticLine = wx.StaticLine(self.panel)

        self.labelOne = wx.StaticText(self.panel, wx.ID_ANY, _extstr(u"splash.OverallProgress")) #$NON-NLS-1$
        self.progressOne = wx.Gauge(self.panel, wx.ID_ANY, 100, size = (-1, 16), style = wx.GA_HORIZONTAL | wx.GA_SMOOTH)
        self.labelTwo = wx.StaticText(self.panel, wx.ID_ANY, _extstr(u"splash.CurrentProgress")) #$NON-NLS-1$
        self.progressTwo = wx.Gauge(self.panel, wx.ID_ANY, 100, size = (-1, 16), style = wx.GA_HORIZONTAL | wx.GA_SMOOTH)

        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.splashPanel, 0, wx.EXPAND)
        box.Add(self.staticLine, 0, wx.EXPAND)
        box.Add(self.labelOne, 0, wx.EXPAND | wx.ALL, 3)
        box.Add(self.progressOne, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
        box.Add(self.labelTwo, 0, wx.EXPAND | wx.ALL, 3)
        box.Add(self.progressTwo, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
        self.panel.SetAutoLayout(True)
        self.panel.SetSizer(box)
    # end _createWidgets()

    def _bindWidgetEvents(self):
        self.Bind(ZEVT_UIEXEC, self.onUIExec)
    # end _bindWidgetEvents()
    
    def _createSplashPanel(self, parent):
        ver = version.ZVersion()
        verDate = ZSchemaDateTime(ver.getBuildDate())

        panel = wx.Panel(parent, wx.ID_ANY)
        panel.SetBackgroundColour(wx.WHITE)
        splashFilename = u"splash.png" #$NON-NLS-1$
        if isPortableEnabled():
            splashFilename = u"splash_portable.png" #$NON-NLS-1$
        bitmap = getResourceRegistry().getBitmap(u"images/splash/%s" % splashFilename) #$NON-NLS-1$
        splashImage = ZStaticBitmap(panel, bitmap)
        
        versionLabelLabel = wx.StaticText(panel, wx.ID_ANY, u"%s: " % _extstr(u"splash.Version")) #$NON-NLS-1$ #$NON-NLS-2$
        versionLabelLabel.SetFont(getDefaultFontBold())
        versionLabel = wx.StaticText(panel, wx.ID_ANY, ver.getFullVersionString())
        dateLabelLabel = wx.StaticText(panel, wx.ID_ANY, u"%s: " % _extstr(u"splash.BuiltOn")) #$NON-NLS-1$ #$NON-NLS-2$
        dateLabelLabel.SetFont(getDefaultFontBold())
        dateLabel = wx.StaticText(panel, wx.ID_ANY, verDate.toString(localTime = True))
        
        verAndDateSizer = wx.BoxSizer(wx.HORIZONTAL)
        verAndDateSizer.Add(versionLabelLabel, 0, wx.EXPAND | wx.RIGHT, 2)
        verAndDateSizer.Add(versionLabel, 0, wx.EXPAND | wx.RIGHT, 10)
        verAndDateSizer.Add(dateLabelLabel, 0, wx.EXPAND | wx.RIGHT, 2)
        verAndDateSizer.Add(dateLabel, 0, wx.EXPAND)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(splashImage, 0, wx.EXPAND)
        sizer.AddSizer(verAndDateSizer, 0, wx.EXPAND | wx.ALL, 5)
        
        panel.SetSizer(sizer)
        panel.SetAutoLayout(True)
        
        return panel
    # end _createSplashPanel()

    def onUIExec(self, event):
        event.getRunnable().run()
    # end onUIExec()

    def rasStart(self, totalTasks):
        class ZRASStart(IZRunnable):
            def __init__(self, ref):
                self.ref = ref
            def run(self):
                self.ref.taskNum = 0
                self.ref.progressOne.SetRange(totalTasks)
                self.ref.progressOne.SetValue(0)
                self.ref.progressOne.Refresh()
                self.ref.progressTwo.SetValue(0)
                self.ref.progressTwo.Refresh()
        # end ZRASStart

        # Queue some work to be done on the UI thread.
        fireUIExecEvent(ZRASStart(self), self)
    # end rasStart()

    def rasTaskStart(self, taskName, totalSubTasks):
        class ZRASTaskStart(IZRunnable):
            def __init__(self, ref):
                self.ref = ref
            def run(self):
                self.ref.subtaskNum = 0
                self.ref.labelOne.SetLabel(_extstr(u"splash.OverallProgress2") % taskName) #$NON-NLS-1$
                self.ref.labelOne.Refresh()
                self.ref.progressTwo.SetRange(totalSubTasks)
                self.ref.progressTwo.SetValue(0)
                self.ref.progressTwo.Refresh()
            # end run()
        # end ZRASTaskStart

        # Queue some work to be done on the UI thread.
        fireUIExecEvent(ZRASTaskStart(self), self)
    # end rasTaskStart()

    def rasSubTaskStart(self, subTaskName):
        class ZRASSubTaskStart(IZRunnable):
            def __init__(self, ref):
                self.ref = ref
            def run(self):
                self.ref.labelTwo.SetLabel(_extstr(u"splash.CurrentProgress2") % subTaskName) #$NON-NLS-1$
                self.ref.labelTwo.Refresh()
        # end ZRASSubTaskStart

        # Queue some work to be done on the UI thread.
        fireUIExecEvent(ZRASSubTaskStart(self), self)
    # end rasSubTaskStart()

    def rasSubTaskEnd(self):
        class ZRASSubTaskEnd(IZRunnable):
            def __init__(self, ref):
                self.ref = ref
            def run(self):
                self.ref.subtaskNum += 1
                self.ref.labelTwo.SetLabel(_extstr(u"splash.Complete")) #$NON-NLS-1$
                self.ref.labelTwo.Refresh()
                self.ref.progressTwo.SetValue(self.ref.subtaskNum)
                self.ref.progressTwo.Refresh()
        # end ZRASSubTaskEnd

        # Queue some work to be done on the UI thread.
        fireUIExecEvent(ZRASSubTaskEnd(self), self)
    # end rasSubTaskEnd()

    def rasTaskEnd(self):
        class ZRASTaskEnd(IZRunnable):
            def __init__(self, ref):
                self.ref = ref
            def run(self):
                self.ref.taskNum += 1
                self.ref.labelOne.SetLabel(_extstr(u"splash.Complete")) #$NON-NLS-1$
                self.ref.labelOne.Refresh()
                self.ref.progressOne.SetValue(self.ref.taskNum)
                self.ref.progressOne.Refresh()
        # end ZRASTaskEnd

        # Queue some work to be done on the UI thread.
        fireUIExecEvent(ZRASTaskEnd(self), self)
    # end rasTaskEnd()

    def rasEnd(self):
        class ZRASEnd(IZRunnable):
            def __init__(self, ref):
                self.ref = ref
            def run(self):
                self.ref.Close()
                self.ref.Refresh()
        # end ZRASEnd

        # Queue some work to be done on the UI thread.
        fireUIExecEvent(ZRASEnd(self), self)
    # end rasEnd()

# end ZStartupWindow
