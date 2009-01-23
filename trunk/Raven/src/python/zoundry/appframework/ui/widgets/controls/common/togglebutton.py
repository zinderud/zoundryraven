from wx._core import wxEVT_COMMAND_TOGGLEBUTTON_CLICKED
from zoundry.appframework.ui.util.colorutil import getDefaultControlBorderColor
from zoundry.appframework.ui.widgets.controls.mixins.clickmixin import ZClickableControlMixin
from zoundry.appframework.ui.widgets.controls.mixins.hovermixin import ZHoverableControlMixin
import wx

# ------------------------------------------------------------------------------
# Implements a simple image toggle button control.  Should act much like a
# wx.ToggleButton with regard to events that are fired.
# ------------------------------------------------------------------------------
class ZToggleButton(wx.PyControl, ZClickableControlMixin, ZHoverableControlMixin):

    def __init__(self, parent, bitmap, toggledBitmap = None, style = wx.NO_BORDER):
        self.bitmap = bitmap
        self.disabledBitmap = None
        self.toggledBitmap = toggledBitmap
        self.disabledToggledBitmap = None
        self.toggled = False

        self.borderColor = getDefaultControlBorderColor()
        self.toggledBorderColor = getDefaultControlBorderColor()
        self.hoverBackgroundColor = wx.Color(254, 225, 119)
        self.clickBackgroundColor = wx.Color(251, 209, 61)
        self.toggledBackgroundColor = wx.Color(249, 249, 249)

        wx.PyControl.__init__(self, parent, wx.ID_ANY, style = style)
        ZClickableControlMixin.__init__(self)
        ZHoverableControlMixin.__init__(self)

        self.Bind(wx.EVT_PAINT, self.onPaint, self)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.onEraseBackground, self)

        sizeW = self.bitmap.GetWidth() + 4
        sizeH = self.bitmap.GetHeight() + 4
        self.SetSizeHints(sizeW, sizeH)
    # end __init__()

    def SetDisabledBitmap(self, bitmap):
        self.disabledBitmap = bitmap
    # end SetDisabledBitmap()

    def SetToggledBitmap(self, bitmap):
        self.toggledBitmap = bitmap
    # end SetToggledBitmap()

    def SetDisabledToggledBitmap(self, bitmap):
        self.disabledToggledBitmap = bitmap
    # end SetDisabledToggledBitmap()

    def SetBorderColor(self, color):
        self.borderColor = color
    # end SetBorderColor()

    def SetHoverBackgroundColor(self, color):
        self.hoverBackgroundColor = color
    # end SetHoverBackgroundColor()

    def SetClickBackgroundColor(self, color):
        self.clickBackgroundColor = color
    # end SetClickBackgroundColor()

    def SetToggledBackgroundColor(self, color):
        self.toggledBackgroundColor = color
    # end SetToggledBackgroundColor()
    
    def SetToggledBorderColor(self, color):
        self.toggledBorderColor = color
    # end SetToggledBorderColor()
    
    def IsToggled(self):
        return self.toggled
    # end IsToggled()
    
    def Toggle(self, toggled = True):
        self.toggled = toggled
        self.Refresh()
    # end Toggle()

    def onEraseBackground(self, event): #@UnusedVariable
        pass
    # end onEraseBackground()

    def onPaint(self, event):
        (w, h) = self.GetSizeTuple()
        paintDC = wx.BufferedPaintDC(self)
        paintDC.SetBackground(wx.Brush(self.GetParent().GetBackgroundColour(), wx.SOLID))
        paintDC.Clear()

        bitmap = self.bitmap
        if self.toggled and self.IsEnabled() and self.toggledBitmap is not None:
            bitmap = self.toggledBitmap
        elif not self.IsEnabled() and not self.toggled and self.disabledBitmap is not None:
            bitmap = self.disabledBitmap
        elif not self.IsEnabled() and self.toggled and self.disabledToggledBitmap is not None:
            bitmap = self.disabledToggledBitmap
        elif not self.IsEnabled() and self.toggled and self.disabledBitmap is not None:
            bitmap = self.disabledBitmap

        bitmapX = 2
        bitmapY = 2
        brush = wx.TRANSPARENT_BRUSH
        pen = wx.TRANSPARENT_PEN

        if self.toggled:
            brush = wx.Brush(self.toggledBackgroundColor)
        if self._isHovering():
            brush = wx.Brush(self.hoverBackgroundColor)
        if self._isLeftClicking():
            brush = wx.Brush(self.clickBackgroundColor)
        if self._isHovering() or self._isLeftClicking():
            pen = wx.Pen(self.borderColor)
        elif self.toggled:
            pen = wx.Pen(self.toggledBorderColor)

        paintDC.SetBrush(brush)
        paintDC.SetPen(pen)
        paintDC.DrawRectangle(0, 0, w, h)
        paintDC.DrawBitmap(bitmap, bitmapX, bitmapY)

        del paintDC

        event.Skip()
    # end onPaint()

    def _onHoverBegin(self):
        return True
    # end _onHoverBegin()

    def _onHoverEnd(self):
        return True
    # end _onHoverEnd()

    def _onLeftClicking(self, mouseXY): #@UnusedVariable
        return True
    # end _onLeftClicking()

    def _onLeftClick(self, mouseXY): #@UnusedVariable
        self._fireToggleButtonEvent()
        if self.toggled:
            self.toggled = False
        else:
            self.toggled = True
        self.Refresh()
        return True
    # end _onLeftClick()

    def _fireToggleButtonEvent(self):
        event = wx.CommandEvent(wxEVT_COMMAND_TOGGLEBUTTON_CLICKED, self.GetId())
        self.GetEventHandler().AddPendingEvent(event)
    # end _fireToggleButtonEvent()

# end ZToggleButton


# ------------------------------------------------------------------------------
# Overrides the base toggle button in order to deny focus from the keyboard.
# ------------------------------------------------------------------------------
class ZNoFocusToggleButton(ZToggleButton):

    def __init__(self, *args, **kw):
        ZToggleButton.__init__(self, *args, **kw)
    # end __init__()

    def AcceptsFocusFromKeyboard(self):
        return False
    # end AcceptsFocusFromKeyboard()

# end ZNoFocusToggleButton
