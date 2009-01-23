import wx

# ------------------------------------------------------------------------------
# Use this mixin to make a custom control hoverable.  Subclasses should 
# implement the various "_on*Hover*" methods in order to leverage this mixin.
# ------------------------------------------------------------------------------
class ZHoverableControlMixin:
    
    def __init__(self):
        self.hovering = False # is the user hovering the mouse over the control

        self.Bind(wx.EVT_ENTER_WINDOW, self.onHCMEnter, self)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.onHCMLeave, self)
    # end __init__()

    def onHCMEnter(self, event): #@UnusedVariable
        self.hovering = True
        if self._onHoverBegin():
            self.Refresh()
        event.Skip()
    # end onHCMEnter()

    def onHCMLeave(self, event): #@UnusedVariable
        self.hovering = False
        if self._onHoverEnd():
            self.Refresh()
        event.Skip()
    # end onHCMLeave()

    def _onHoverBegin(self):
        u"""_onHoverBegin() -> boolean
        Called by the mixin class when the user begins
        hovering over the control.""" #$NON-NLS-1$
        return False
    # end _onHoverBegin()

    def _onHoverEnd(self):
        u"""_onMiddleClick() -> boolean
        Called by the mixin class when the user stops
        hovering over the control.""" #$NON-NLS-1$
        return False
    # end _onHoverEnd()
    
    def _isHovering(self):
        return self.hovering
    # end _isHovering()

# end ZHoverableControlMixin
