from zoundry.appframework.ui.events.commonevents import ZEVT_UIEXEC
import wx

# ------------------------------------------------------------------------------
# Panel impl where, when asked for the parent background colour, returns the
# parent background color.
# ------------------------------------------------------------------------------
class ZTransparentPanel(wx.Panel):

    def __init__(self, *args, **kw):
        wx.Panel.__init__(self, *args, **kw)
    # end __init__()

    def GetBackgroundColour(self):
        return self.GetParent().GetBackgroundColour()
    # end GetBackgroundColour()

    def SetBackgroundColour(self, color): #@UnusedVariable
        pass
    # end SetBackgroundColour()

    def GetBackgroundColor(self):
        return self.GetParent().GetBackgroundColour()
    # end GetBackgroundColour()

    def SetBackgroundColor(self, color): #@UnusedVariable
        pass
    # end SetBackgroundColour()

# end ZTransparentPanel


# ------------------------------------------------------------------------------
# Smart version of the transparent panel.  This implementation includes
# UI exec event handling.
# ------------------------------------------------------------------------------
class ZSmartTransparentPanel(ZTransparentPanel):

    def __init__(self, *args, **kw):
        ZTransparentPanel.__init__(self, *args, **kw)
        self.Bind(ZEVT_UIEXEC, self.onUIExec)
    # end __init__()

    def onUIExec(self, event):
        event.getRunnable().run()
    # end onUIExec()

# end ZSmartTransparentPanel
