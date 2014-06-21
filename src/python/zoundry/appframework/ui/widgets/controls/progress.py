from zoundry.appframework.global_services import getApplicationModel
import wx #@UnusedImport
import wx.lib.throbber #@Reimport @UnusedImport


# ------------------------------------------------------------------------------
# Progress throbber.  This widget is often used instead of a progress meter
# when we don't know how long an operation will take.  Instead, we simply show
# this little spinning throbber widget and, hopefully, some text that changes
# as work is done.
# ------------------------------------------------------------------------------
class ZProgressIconCtrl(wx.PyControl):

    def __init__(self, parent, useSmallIcons = False):
        self.useSmallIcons = useSmallIcons
        self.bitmaps = self._loadBitmaps()
        self.backgroundColor = None
        self.currIdx = 0
        self.timerId = wx.NewId()
        self.timer = None

        size = wx.Size(self.bitmaps[0].GetWidth(), self.bitmaps[0].GetHeight())
        wx.Control.__init__(self, parent, wx.ID_ANY, style = wx.NO_BORDER, size = size)
        self.SetSizeHintsSz(size)
        self.SetMinSize(size)

        self.Bind(wx.EVT_PAINT, self.onPaint, self)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.onEraseBackground, self)
        self.Bind(wx.EVT_WINDOW_DESTROY, self.onDestroy, self)
        wx.EVT_TIMER(self, self.timerId, self.onTimer)
    # end __init__()

    def isRunning(self):
        return self.timer is not None and self.timer.IsRunning()
    # end isRunning()

    def _loadBitmaps(self):
        bitmaps = []
        prefix = u"" #$NON-NLS-1$
        if self.useSmallIcons:
            prefix = u"sm-" #$NON-NLS-1$
        for i in range(1, 9):
            bitmaps.append( getApplicationModel().getResourceRegistry().getBitmap(u"images/common/progress/%sprogress-icon-%d.png" % (prefix, i)) ) #$NON-NLS-1$
        return bitmaps
    # end _loadBitmaps()

    def setBackgroundColor(self, backgroundColor):
        self.backgroundColor = backgroundColor
    # end setBackgroundColor()

    def onEraseBackground(self, event): #@UnusedVariable
        pass
    # end onEraseBackground()

    def onPaint(self, event):
        paintDC = wx.BufferedPaintDC(self)
        if self.backgroundColor is None:
            paintDC.SetBackground(wx.Brush(self.GetParent().GetBackgroundColour(), wx.SOLID))
        else:
            paintDC.SetBackground(wx.Brush(self.backgroundColor, wx.SOLID))
        paintDC.Clear()

        paintDC.DrawBitmap(self.bitmaps[self.currIdx], 0, 0)

        del paintDC
        event.Skip()
    # end onPaint()

    def onDestroy(self, event):
        if self.timer is not None and self.timer.IsRunning():
            self.timer.Stop()
        event.Skip()
    # end onDestroy()

    def onTimer(self, event):
        self.currIdx = (self.currIdx + 1) % 8
        self.Refresh()
        event.Skip()
    # end onTimer()

    def start(self):
        if self.timer is None:
            self.timer = wx.Timer(self, self.timerId)
        if not self.timer.IsRunning():
            self.timer.Start(85)
    # end start()

    def stop(self):
        if self.timer is not None and self.timer.IsRunning():
            self.timer.Stop()
    # end stop()

# end ZProgressIconCtrl


# ------------------------------------------------------------------------------------------
# Composite for a progress animation control with a text lable
# ------------------------------------------------------------------------------------------
class ZProgressLabelCtrl(wx.Panel):

    def __init__(self, parent, text = None, useSmallIcons = False):
        if text is None:
            text = u"" #$NON-NLS-1$

        wx.Panel.__init__(self, parent, wx.ID_ANY)

        self.label = wx.StaticText(self, wx.ID_ANY, text)
        self.animateControl = ZProgressIconCtrl(self, useSmallIcons)
        self.animateControl.Show(False)

        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(self.animateControl, 0, wx.ALIGN_RIGHT | wx.RIGHT, 5)
        box.Add(self.label, 1, wx.EXPAND | wx.ALIGN_LEFT )

        self.SetSizeHints(-1, self.animateControl.GetSizeTuple()[1])
        self.SetAutoLayout(True)
        self.SetSizer(box)
        self.Layout()
    # end __init__()

    def isRunning(self):
        return self.animateControl.isRunning()
    # end isRunning()

    def setLabel(self, text):
        self.label.SetLabel(text)
    # end setLabel()

    def start(self):
        self.animateControl.Show(True)
        if not self.IsShown():
            self.Show(True)
        self.animateControl.start()
        self.Layout()
    # end __init__()

    def stop(self):
        self.animateControl.Show(False)
        self.Layout()
        self.animateControl.stop()
    # end start()

    def Show(self, bShow):
        wx.Panel.Show(self, bShow)
        if bShow:
            self.start()
        else:
            self.stop()
        if self.GetParent():
            self.GetParent().Layout()
    # end Show()

# end ZProgressLabelCtrl
