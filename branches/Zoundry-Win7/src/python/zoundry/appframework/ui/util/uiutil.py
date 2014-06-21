from zoundry.base.util.zthread import IZRunnable
from zoundry.appframework.ui.events.commonevents import ZRefreshEvent
from zoundry.appframework.ui.events.commonevents import ZUIExecEvent

# ------------------------------------------------------------------------------
# Convenience method for getting the root window of a wx widget.
# ------------------------------------------------------------------------------
def getRootWindowOrDialog(wxWindow):
    window = wxWindow
    while window is not None and window.GetParent() is not None:
        window = window.GetParent()
    return window
# end getRootWindowOrDialog()


# ------------------------------------------------------------------------------
# A generic runnable that can be used to run a single arbitrary method.
# ------------------------------------------------------------------------------
class ZMethodRunnable(IZRunnable):

    def __init__(self, method, args = None):
        self.method = method
        self.args = args
    # end __init__()

    def run(self):
        if self.args is None:
            self.method()
        else:
            self.method(*self.args)
    # end run()

# end ZMethodRunnable


# ------------------------------------------------------------------------------
# Convenience function for pushing a UI Exec event on the event queue.  If 
# a window is listening for UIExec events, then that window will pick up the
# event and run the given runnable.
# ------------------------------------------------------------------------------
def fireUIExecEvent(runnable, window):
    u"""fireUIExecEvent(IZRunnable, wx.Window) -> None
    Fires a UI Exec event, which will cause the given IZRunnable
    to be executed on the main UI thread.""" #$NON-NLS-1$
    event = ZUIExecEvent(window.GetId(), runnable)
    window.GetEventHandler().AddPendingEvent(event)
# end fireUIExecEvent()


# ------------------------------------------------------------------------------
# Convenience function for pushing a UI Refresh event on the event queue.
# ------------------------------------------------------------------------------
def fireRefreshEvent(window, data = None):
    u"""fireRefreshEvent(wx.Window) -> None
    Fires a refresh event.""" #$NON-NLS-1$
    event = ZRefreshEvent(window.GetId(), data)
    window.GetEventHandler().AddPendingEvent(event)
# end fireRefreshEvent()
