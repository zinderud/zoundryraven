from wx._core import wxEVT_COMMAND_BUTTON_CLICKED
from zoundry.appframework.ui.util.colorutil import getDefaultControlBorderColor
from zoundry.appframework.ui.widgets.controls.mixins.clickmixin import ZClickableControlMixin
from zoundry.appframework.ui.widgets.controls.mixins.hovermixin import ZHoverableControlMixin
import wx

# --------------------------------------------------------------------------------------------
# Implements a simple image button control.  Should act much like a wx.Button with regard to
# events that are fired.
# --------------------------------------------------------------------------------------------
class ZImageButton(wx.PyControl, ZClickableControlMixin, ZHoverableControlMixin):

    def __init__(self, parent, bitmap, drawDropArrow = False, hoverBitmap = None, drawHoverBox = True, style = wx.NO_BORDER):
        self.bitmap = bitmap
        self.disabledBitmap = None
        self.hoverBitmap = hoverBitmap
        self.drawHoverBox = drawHoverBox
        self.drawDropArrow = drawDropArrow

        self.borderColor = getDefaultControlBorderColor()
        self.hoverBackgroundColor = wx.Color(254, 225, 119)
        self.clickBackgroundColor = wx.Color(251, 209, 61)

        wx.PyControl.__init__(self, parent, wx.ID_ANY, style = style)
        ZClickableControlMixin.__init__(self)
        ZHoverableControlMixin.__init__(self)

        self.Bind(wx.EVT_PAINT, self.onPaint, self)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.onEraseBackground, self)

        sizeW = self.bitmap.GetWidth()
        sizeH = self.bitmap.GetHeight()
        if self.drawHoverBox or self.drawDropArrow:
            sizeW += 4
            sizeH += 4
        self.SetSizeHints(sizeW, sizeH)
    # end __init__()

    def SetDisabledBitmap(self, bitmap):
        self.disabledBitmap = bitmap
    # end SetDisabledBitmap

    def SetBorderColor(self, color):
        self.borderColor = color
    # end SetBorderColor()

    def SetHoverBackgroundColor(self, color):
        self.hoverBackgroundColor = color
    # end SetHoverBackgroundColor()

    def SetClickBackgroundColor(self, color):
        self.clickBackgroundColor = color
    # end SetClickBackgroundColor()

    def onEraseBackground(self, event): #@UnusedVariable
        pass
    # end onEraseBackground()

    def onPaint(self, event):
        (w, h) = self.GetSizeTuple()
        paintDC = wx.BufferedPaintDC(self)
        paintDC.SetBackground(wx.Brush(self.GetParent().GetBackgroundColour(), wx.SOLID))
        paintDC.Clear()

        bitmap = self.bitmap
        if not self.IsEnabled() and self.disabledBitmap is not None:
            bitmap = self.disabledBitmap
        bitmapX = 0
        bitmapY = 0
        if self.drawHoverBox or self.drawDropArrow:
            bitmapX += 2
            bitmapY += 2

        brush = wx.TRANSPARENT_BRUSH
        pen = wx.TRANSPARENT_PEN

        if self._isHovering():
            brush = wx.Brush(self.hoverBackgroundColor)
        if self._isLeftClicking():
            brush = wx.Brush(self.clickBackgroundColor)
        if self._isHovering() or self._isLeftClicking():
            if self.hoverBitmap is not None:
                bitmap = self.hoverBitmap
            pen = wx.Pen(self.borderColor)

        paintDC.SetBrush(brush)
        paintDC.SetPen(pen)
        if self.drawHoverBox:
            paintDC.DrawRectangle(0, 0, w, h)
        paintDC.DrawBitmap(bitmap, bitmapX, bitmapY)

        if self.drawDropArrow:
            # Draw the down arrow
            startX = w - 6
            startY = h - 4
            paintDC.SetPen(wx.BLACK_PEN)
            paintDC.SetBrush(wx.BLACK_BRUSH)
            paintDC.DrawLine(startX, startY, startX + 5, startY)
            paintDC.DrawLine(startX + 1, startY + 1, startX + 4, startY + 1)
            paintDC.DrawPoint(startX + 2, startY + 2)
            # FIXME (EPW) draw a white corona around the drop arrow
#            paintDC.SetPen(wx.WHITE_PEN)
#            paintDC.SetBrush(wx.WHITE_BRUSH)

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
        self._fireButtonEvent()
        return True
    # end _onLeftClick()

    def _fireButtonEvent(self):
        event = wx.CommandEvent(wxEVT_COMMAND_BUTTON_CLICKED, self.GetId())
        self.GetEventHandler().AddPendingEvent(event)
    # end _fireButtonEvent()

# end ZImageButton


# ------------------------------------------------------------------------------
# Overrides the base image button in order to deny focus from the keyboard.
# ------------------------------------------------------------------------------
class ZNoFocusImageButton(ZImageButton):

    def __init__(self, *args, **kw):
        ZImageButton.__init__(self, *args, **kw)
    # end __init__()

    def AcceptsFocusFromKeyboard(self):
        return False
    # end AcceptsFocusFromKeyboard()

# end ZNoFocusImageButton
