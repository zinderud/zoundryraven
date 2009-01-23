import wx

# ------------------------------------------------------------------------------
# Use this mixin to make a custom control clickable.  Subclasses should
# implement the various "_on*Click*" methods in order to leverage this mixin.
# ------------------------------------------------------------------------------
class ZClickableControlMixin:

    def __init__(self, allowGetFocus = True):
        self.allowGetFocus = allowGetFocus

        self.lclicking = False # is the user left clicking the control
        self.rclicking = False # is the user clicking the control
        self.mclicking = False # is the user clicking the control

        self.Bind(wx.EVT_LEAVE_WINDOW, self.onCCMLeave, self)
        self.Bind(wx.EVT_LEFT_DOWN, self.onCCMLeftClickDown, self)
        self.Bind(wx.EVT_LEFT_UP, self.onCCMLeftClickUp, self)
        self.Bind(wx.EVT_RIGHT_DOWN, self.onCCMRightClickDown, self)
        self.Bind(wx.EVT_RIGHT_UP, self.onCCMRightClickUp, self)
        self.Bind(wx.EVT_MIDDLE_DOWN, self.onCCMMiddleClickDown, self)
        self.Bind(wx.EVT_MIDDLE_UP, self.onCCMMiddleClickUp, self)
    # end __init__()

    def onCCMLeftClickDown(self, event):
        self.lclicking = True
        if self._onLeftClicking(event.GetPositionTuple()):
            self.Refresh()
        if self.allowGetFocus:
            event.Skip()
    # end onCCMLeftClickDown()

    def onCCMLeftClickUp(self, event):
        if self.lclicking:
            self.lclicking = False
            if self._onLeftClick(event.GetPositionTuple()):
                self.Refresh()
        event.Skip()
    # end onCCMLeftClickUp()

    def onCCMRightClickDown(self, event):
        self.rclicking = True
        if self._onRightClicking(event.GetPositionTuple()):
            self.Refresh()
        event.Skip()
    # end onCCMRightClickDown()

    def onCCMRightClickUp(self, event):
        if self.rclicking:
            self.rclicking = False
            if self._onRightClick(event.GetPositionTuple()):
                self.Refresh()
        event.Skip()
    # end onCCMRightClickUp()

    def onCCMMiddleClickDown(self, event):
        self.mclicking = True
        if self._onMiddleClicking(event.GetPositionTuple()):
            self.Refresh()
        event.Skip()
    # end onCCMMiddleClickDown()

    def onCCMMiddleClickUp(self, event):
        if self.mclicking:
            self.mclicking = False
            if self._onMiddleClick(event.GetPositionTuple()):
                self.Refresh()
        event.Skip()
    # end onCCMMiddleClickUp()

    def onCCMLeave(self, event):
        self.lclicking = False
        self.rclicking = False
        self.mclicking = False
        self.Refresh()
        event.Skip()
    # end onCCMCCMLeave()

    def _onLeftClicking(self, mouseXY): #@UnusedVariable
        u"""_onLeftClicking( (int, int) ) -> boolean
        Called by the mixin class when the user starts
        left-clicking on the control.""" #$NON-NLS-1$
        return False
    # end _onLeftClicking()

    def _onLeftClick(self, mouseXY): #@UnusedVariable
        u"""_onLeftClick( (int, int) ) -> boolean
        Called by the mixin class when the user has
        left clicked on the control""" #$NON-NLS-1$
        return False
    # end _onLeftClick()

    def _onRightClicking(self, mouseXY): #@UnusedVariable
        u"""_onRightClicking( (int, int) ) -> boolean
        Called by the mixin class when the user starts
        right-clicking on the control.""" #$NON-NLS-1$
        return False
    # end _onRightClicking()

    def _onRightClick(self, mouseXY): #@UnusedVariable
        u"""_onRightClick( (int, int) ) -> boolean
        Called by the mixin class when the user has
        right clicked on the control""" #$NON-NLS-1$
        return False
    # end _onRightClick()

    def _onMiddleClicking(self, mouseXY): #@UnusedVariable
        u"""_onMiddleClicking( (int, int) ) -> boolean
        Called by the mixin class when the user starts
        right-clicking on the control.""" #$NON-NLS-1$
        return False
    # end _onMiddleClicking()

    def _onMiddleClick(self, mouseXY): #@UnusedVariable
        u"""_onMiddleClick( (int, int) ) -> boolean
        Called by the mixin class when the user has
        right clicked on the control""" #$NON-NLS-1$
        return False
    # end _onMiddleClick()

    def _isLeftClicking(self):
        return self.lclicking
    # end _isLeftClicking()

    def _isRightClicking(self):
        return self.rclicking
    # end _isRightClicking()

    def _isMiddleClicking(self):
        return self.mclicking
    # end _isMiddleClicking()

# end ZClickableControlMixin
