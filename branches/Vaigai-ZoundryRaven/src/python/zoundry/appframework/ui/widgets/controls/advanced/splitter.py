from zoundry.appframework.ui.events.splitterevents import ZSplitterSashPosChangedEvent
from zoundry.appframework.ui.widgets.controls.mixins.hovermixin import ZHoverableControlMixin
from zoundry.base.exceptions import ZAbstractMethodCalledException
import wx

# ------------------------------------------------------------------------------
# Custom sizer used by the splitter window to layout its two children.
# ------------------------------------------------------------------------------
class ZSplitterWindowSizer(wx.PySizer):

    def __init__(self, sashPosition = 100, sashSize = 5):
        self.sashPosition = sashPosition
        self.sashSize = sashSize

        wx.PySizer.__init__(self)
    # end __init__()

    def setSashPosition(self, sashPosition):
        self.sashPosition = sashPosition
    # end setSashPosition()

    def setSashSize(self, sashSize):
        self.sashSize = sashSize
    # end setSashSize()

    def CalcMin(self):
        return wx.Size(1, 1)
    # end CalcMin()

    def RecalcSizes(self):
        if len(self.GetChildren()) != 3:
            return

        pos = self.GetPosition()
        size = self.GetSize()

        leftTopItem = self.GetChildren()[0]
        dividerItem = self.GetChildren()[1]
        rightBottomItem = self.GetChildren()[2]

        self._doRecalcSizes(pos, size, leftTopItem, dividerItem, rightBottomItem)
    # end RecalcSizes()

    def _doRecalcSizes(self, pos, size, leftTopItem, dividerItem, rightBottomItem):
        raise ZAbstractMethodCalledException(self.__class__, u"_doRecalcSizes") #$NON-NLS-1$
    # end _doRecalcSizes()

# end ZSplitterWindowSizer


# ------------------------------------------------------------------------------
# Vertical splitter window sizer.
# ------------------------------------------------------------------------------
class ZVerticalSplitterWindowSizer(ZSplitterWindowSizer):

    def __init__(self, sashPosition = 100, sashSize = 5):
        ZSplitterWindowSizer.__init__(self, sashPosition, sashSize)
    # end __init__()

    def _doRecalcSizes(self, pos, size, leftItem, dividerItem, rightItem):
        (sizerX, sizerY) = pos.Get()
        (sizerW, sizerH) = size.Get()

        halfSashSize = self.sashSize / 2

        leftPos = wx.Point(sizerX, sizerY)
        leftSize = wx.Size(self.sashPosition - halfSashSize, sizerH)

        dividerPos = wx.Point(sizerX + self.sashPosition - halfSashSize, sizerY)
        dividerSize = wx.Size(self.sashSize, sizerH)

        rightPos = wx.Point(dividerPos.Get()[0] + dividerSize.Get()[0], sizerY)
        rightSize = wx.Size(sizerW - (dividerSize.Get()[0] + leftSize.Get()[0]), sizerH)

        leftItem.SetDimension(leftPos, leftSize)
        dividerItem.SetDimension(dividerPos, dividerSize)
        rightItem.SetDimension(rightPos, rightSize)
    # end _doRecalcSizes()

# end ZVerticalSplitterWindowSizer


# ------------------------------------------------------------------------------
# Vertical splitter window sizer.
# ------------------------------------------------------------------------------
class ZHorizontalSplitterWindowSizer(ZSplitterWindowSizer):

    def __init__(self, sashPosition = 100, sashSize = 5):
        ZSplitterWindowSizer.__init__(self, sashPosition, sashSize)
    # end __init__()

    def _doRecalcSizes(self, pos, size, topItem, dividerItem, bottomItem):
        (sizerX, sizerY) = pos.Get()
        (sizerW, sizerH) = size.Get()

        halfSashSize = self.sashSize / 2

        topPos = wx.Point(sizerX, sizerY)
        topSize = wx.Size(sizerW, self.sashPosition - halfSashSize)

        dividerPos = wx.Point(sizerX, sizerY + self.sashPosition - halfSashSize)
        dividerSize = wx.Size(sizerW, self.sashSize)

        bottomPos = wx.Point(sizerX, dividerPos.Get()[1] + dividerSize.Get()[1])
        bottomSize = wx.Size(sizerW, sizerH - (dividerSize.Get()[1] + topSize.Get()[1]))

        topItem.SetDimension(topPos, topSize)
        dividerItem.SetDimension(dividerPos, dividerSize)
        bottomItem.SetDimension(bottomPos, bottomSize)
    # end _doRecalcSizes()

# end ZHorizontalSplitterWindowSizer


# ------------------------------------------------------------------------------
# The control used as the divider between the two halves of the splitter
# window.
# ------------------------------------------------------------------------------
class ZSplitterWindowDivider(wx.PyControl, ZHoverableControlMixin):

    def __init__(self, parent):
        self.parent = parent

        wx.PyControl.__init__(self, parent, wx.ID_ANY, style = wx.NO_BORDER)
        ZHoverableControlMixin.__init__(self)

        # FIXME (EPW) impl. custom painting of sash window divider
#        self.Bind(wx.EVT_PAINT, self.onPaint, self)
#        self.Bind(wx.EVT_ERASE_BACKGROUND, self.onEraseBackground, self)
    # end __init__()

    def onEraseBackground(self, event): #@UnusedVariable
        pass
    # end onEraseBackground()

    def onPaint(self, event):
        paintDC = wx.BufferedPaintDC(self)
        if self._isHovering():
            paintDC.SetBackground(wx.Brush(self.hoverBGColor, wx.SOLID))
        else:
            paintDC.SetBackground(wx.Brush(self.GetParent().GetBackgroundColour(), wx.SOLID))
        paintDC.Clear()
        del paintDC
        event.Skip()
    # end onPaint()

    def _onHoverBegin(self):
        self.parent.onDividerHoverBegin()
        return True
    # end _onHoverBegin()

    def _onHoverEnd(self):
        self.parent.onDividerHoverEnd()
        return True
    # end _onHoverEnd()

# end ZSplitterWindowDivider


# ------------------------------------------------------------------------------
# Custom splitter window.
# ------------------------------------------------------------------------------
class ZSplitterWindow(wx.PyPanel):

    def __init__(self, parent):
        self.sashPosition = 100
        self.newSashPosition = self.sashPosition
        self.sashSize = 4
        self.minimumPaneSize = 50
        self.sizer = None
        self.vertical = False
        self.pointOfRef = None
        self.sashPointOfRef = self.sashPosition
        self.dragging = False

        self.widget1 = None
        self.widget2 = None

        wx.Panel.__init__(self, parent, wx.ID_ANY, style = wx.NO_BORDER)

        self.divider = ZSplitterWindowDivider(self)

        self.divider.Bind(wx.EVT_LEFT_DOWN, self.onLeftDown, self.divider)
        self.divider.Bind(wx.EVT_LEFT_DCLICK, self.onLeftDoubleClick, self.divider)
        self.divider.Bind(wx.EVT_LEFT_UP, self.onLeftUp, self.divider)
        self.divider.Bind(wx.EVT_MOTION, self.onMouseMove, self.divider)
        self.divider.Bind(wx.EVT_MOUSE_CAPTURE_LOST, self.onMouseCaptureLost, self.divider)
        self.Bind(wx.EVT_IDLE, self.onIdle)
    # end __init__()

    def onIdle(self, event):
        if self.newSashPosition != self.sashPosition:
            self.reLayout()
        event.Skip()
    # end onIdle()

    def ReplaceWindow(self, oldWidget, newWidget):
        w1 = self.widget1
        w2 = self.widget2
        if w1 == oldWidget:
            w1 = newWidget
        elif w2 == oldWidget:
            w2 = newWidget
        if self.vertical:
            self.SplitVertically(w1, w2)
        else:
            self.SplitHorizontally(w1, w2)
    # end ReplaceWindow()

    def SplitHorizontally(self, topWidget, bottomWidget, splitSize = None):
        if splitSize is not None:
            self.SetSashPosition(splitSize)

        self.widget1 = topWidget
        self.widget2 = bottomWidget

        self.vertical = False
        self.sizer = ZHorizontalSplitterWindowSizer(self.sashPosition, self.sashSize)

        self.sizer.Add(topWidget)
        self.sizer.Add(self.divider)
        self.sizer.Add(bottomWidget)

        self.SetAutoLayout(True)
        self.SetSizer(self.sizer)
        self.reLayout()
    # end SplitHorizontally()

    def SplitVertically(self, leftWidget, rightWidget, splitSize = None):
        if splitSize is not None:
            self.SetSashPosition(splitSize)

        self.widget1 = leftWidget
        self.widget2 = rightWidget

        self.vertical = True
        self.sizer = ZVerticalSplitterWindowSizer(self.sashPosition, self.sashSize)

        self.sizer.Add(leftWidget)
        self.sizer.Add(self.divider)
        self.sizer.Add(rightWidget)

        self.SetAutoLayout(True)
        self.SetSizer(self.sizer)
        self.reLayout()
    # end SplitVertically()

    def SetMinimumPaneSize(self, minimumPaneSize):
        self.minimumPaneSize = minimumPaneSize
    # end SetMinimumPaneSize()

    def SetSashSize(self, sashSize):
        self.sashSize = sashSize
        self.reLayout()
    # end SetSashSize()

    def SetSashPosition(self, sashPosition):
        self.newSashPosition = self._boundSashPosition(sashPosition)
        self.reLayout()
    # end SetSashPosition()

    def SetSashGravity(self, gravity):
        pass
    # end SetSashGravity()

    def GetSashPosition(self):
        return self.sashPosition
    # end GetSashPosition()

    def reLayout(self):
        if self.newSashPosition != self.sashPosition:
            self.sashPosition = self.newSashPosition
        if self.sizer is not None:
            self.sizer.setSashPosition(self.sashPosition)
            self.sizer.setSashSize(self.sashSize)
            self.Layout()
    # end reLayout()

    def onDividerHoverBegin(self):
        if self.isVertical():
            self.SetCursor(wx.StockCursor(wx.CURSOR_SIZEWE))
        else:
            self.SetCursor(wx.StockCursor(wx.CURSOR_SIZENS))
    # end onDividerHoverBegin()

    def onDividerHoverEnd(self):
        if not self.isDragging():
            self.SetCursor(wx.STANDARD_CURSOR)
    # end onDividerHoverEnd()

    def onLeftDoubleClick(self, event):
        event.Skip()
    # end onLeftDoubleClick()

    def onLeftDown(self, event):
        self.dragging = True
        if self.vertical:
            self.divider.SetCursor(wx.StockCursor(wx.CURSOR_SIZEWE))
        else:
            self.divider.SetCursor(wx.StockCursor(wx.CURSOR_SIZENS))

        self.sashPointOfRef = self.sashPosition
        self.pointOfRef = wx.GetMousePosition()

        self.divider.CaptureMouse()
        event.Skip()
    # end onLeftDown()

    def onLeftUp(self, event):
        if self.dragging:
            self.dragging = False
            self.divider.ReleaseMouse()
            self._fireSashPositionChangeEvent()
            self.Refresh()
        event.Skip()
    # end onLeftUp()

    def onMouseCaptureLost(self, event):
        if self.dragging:
            self.dragging = False
            self.divider.SetCursor(wx.STANDARD_CURSOR)
            self._fireSashPositionChangeEvent()
            self.Refresh()
        event.Skip()
    # end onMouseCaptureLost()

    def onMouseMove(self, event):
        if self.dragging:
            newSashPosition = self.sashPosition
            currentPos = wx.GetMousePosition()
            if self.vertical:
                posDiff = currentPos.Get()[0] - self.pointOfRef.Get()[0]
                newSashPosition = self.sashPointOfRef + posDiff
            else:
                posDiff = currentPos.Get()[1] - self.pointOfRef.Get()[1]
                newSashPosition = self.sashPointOfRef + posDiff
            self.newSashPosition = self._boundSashPosition(newSashPosition)
        event.Skip()
    # end onMouseMove()

    def _boundSashPosition(self, newSashPosition):
        minSashPos = self.minimumPaneSize
        maxSashPos = self.GetSizeTuple()[0] - self.minimumPaneSize

        if not self.vertical:
            minSashPos = self.minimumPaneSize
            maxSashPos = self.GetSizeTuple()[1] - self.minimumPaneSize

        if maxSashPos <= minSashPos:
            return newSashPosition

        if newSashPosition < minSashPos:
            return minSashPos
        elif newSashPosition > maxSashPos:
            return maxSashPos
        else:
            return newSashPosition
    # end _isValidSashPosition()

    def _fireSashPositionChangeEvent(self):
        event = ZSplitterSashPosChangedEvent(self)
        self.GetEventHandler().AddPendingEvent(event)
    # end _fireSashPositionChangeEvent()

    def isVertical(self):
        return self.vertical
    # end isVertical()

    def isDragging(self):
        return self.dragging
    # end isDragging()

# end ZSplitterWindow
