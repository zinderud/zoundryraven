from wx._core import wxEVT_COMMAND_BUTTON_CLICKED
from zoundry.appframework.global_services import getResourceRegistry
from zoundry.appframework.ui.events.detailspanel import ZDetailsPanelCollapsedEvent
from zoundry.appframework.ui.events.detailspanel import ZDetailsPanelExpandedEvent
import wx

# ---------------------------------------------------------------------------------------
# A class that implements the little gripper at the bottom of the details panel widget.
# This gripper is used to expand and collapse the details panel.
# ---------------------------------------------------------------------------------------
class ZDetailsButton(wx.Control):
    
    def __init__(self, parent):
        self.hovering = False # is the user hovering the mouse over the control
        self.clicking = False
        self.pulledDown = False

        wx.Control.__init__(self, parent, wx.ID_ANY, style = wx.NO_BORDER)
        
        self.pullDownBitmap = getResourceRegistry().getBitmap(u"images/widgets/detailspanel/pulldown.png") #$NON-NLS-1$
        self.pullDownBitmapHover = getResourceRegistry().getBitmap(u"images/widgets/detailspanel/pulldown_hover.png") #$NON-NLS-1$
        self.pullUpBitmap = getResourceRegistry().getBitmap(u"images/widgets/detailspanel/pullup.png") #$NON-NLS-1$
        self.pullUpBitmapHover = getResourceRegistry().getBitmap(u"images/widgets/detailspanel/pullup_hover.png") #$NON-NLS-1$
        
        self.Bind(wx.EVT_PAINT, self.onPaint, self)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.onEraseBackground, self)
        self.Bind(wx.EVT_ENTER_WINDOW, self.onEnter, self)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.onLeave, self)
        self.Bind(wx.EVT_LEFT_DOWN, self.onLeftClickDown, self)
        self.Bind(wx.EVT_LEFT_UP, self.onLeftClickUp, self)
        
        self.SetSizeHints(self.pullDownBitmap.GetWidth(), self.pullDownBitmap.GetHeight() + 2)
    # end __init__()
    
    def setPulledDown(self, pulledDown):
        self.pulledDown = pulledDown
        self.Refresh()
    # end setPulledDown()
    
    def onEraseBackground(self, event): #@UnusedVariable
        pass
    # end onEraseBackground()
    
    def onPaint(self, event):
        (w, h) = self.GetSizeTuple()
        bmpW = self.pullDownBitmap.GetWidth()
        bmpH = self.pullDownBitmap.GetHeight()
        paintDC = wx.BufferedPaintDC(self)
        paintDC.SetBackground(wx.Brush(self.GetParent().GetBackgroundColour(), wx.SOLID))
        paintDC.Clear()
        
        # Choose the bitmap to draw
        bmp = self.pullUpBitmap
        if self.pulledDown and self.hovering:
            bmp = self.pullUpBitmapHover
        elif not self.pulledDown and not self.hovering:
            bmp = self.pullDownBitmap
        elif not self.pulledDown and self.hovering:
            bmp = self.pullDownBitmapHover

        x = (w / 2) - (bmpW / 2)
        y = (h / 2) - (bmpH / 2)
        paintDC.SetPen(wx.Pen(wx.Color(100, 100, 100), 1, wx.DOT))
        paintDC.DrawLine(0, 0, w, 0)
        paintDC.DrawBitmap(bmp, x, y + 1)
        
        del paintDC
        
        event.Skip()
    # end onPaint()

    def onEnter(self, event): #@UnusedVariable
        self.hovering = True
        self.Refresh()
    # end onEnter()

    def onLeave(self, event): #@UnusedVariable
        self.hovering = False
        self.clicking = False
        self.Refresh()
    # end onLeave()

    def onLeftClickDown(self, event): #@UnusedVariable
        self.clicking = True
        self.Refresh()
    # end onLeftClickDown()

    def onLeftClickUp(self, event): #@UnusedVariable
        if self.clicking:
            self._fireButtonEvent()
        self.clicking = False
        self.Refresh()
    # end onLeftClickUp()

    def _fireButtonEvent(self):
        event = wx.CommandEvent(wxEVT_COMMAND_BUTTON_CLICKED, self.GetId())
        self.GetEventHandler().AddPendingEvent(event)
    # end _fireButtonEvent()

# end ZDetailsButton


# ---------------------------------------------------------------------------------------
# A custom panel implementation that has a (initially hidden) "details" section to it.
# When the user clicks on the "more details" button at the bottom of the panel, the
# hidden details section becomes visible.
# ---------------------------------------------------------------------------------------
class ZDetailsPanel(wx.Panel):

    def __init__(self, parent):
        self.mainWidget = None
        self.detailsWidget = None
        self.pulledDown = False

        wx.Panel.__init__(self, parent, wx.ID_ANY)
        
        self.mainWidgetSizer = wx.BoxSizer(wx.VERTICAL)
        self.detailsWidgetSizer = wx.BoxSizer(wx.VERTICAL)

        self.detailsButton = self._createDetailsButton()

        self.panelSizer = wx.BoxSizer(wx.VERTICAL)
        self.panelSizer.AddSizer(self.mainWidgetSizer, 1, wx.EXPAND)
        self.panelSizer.AddSizer(self.detailsWidgetSizer, 0, wx.EXPAND)
        self.panelSizer.Add(self.detailsButton, 0, wx.EXPAND)
        
        self.Bind(wx.EVT_BUTTON, self.onDetailsButtonClicked, self.detailsButton)
        self.Bind(wx.EVT_SIZE, self.onResize, self)
        
        self.SetAutoLayout(True)
        self.SetSizer(self.panelSizer)
        self.Layout()
    # end __init__()

    def setMainWidget(self, widget):
        self.mainWidget = widget
        self.mainWidgetSizer.Add(widget, 0, wx.EXPAND)
        self.Layout()
    # end setMainWidget()

    def setDetailsWidget(self, widget):
        self.detailsWidget = widget
        self.detailsWidgetSizer.Add(widget, 0, wx.EXPAND)
        if not self.pulledDown:
            self.detailsWidget.Show(False)
        self.Layout()
    # end setDetailsWidget()
    
    def onDetailsButtonClicked(self, event):
        if self.pulledDown:
            self.pulledDown = False
            self.detailsWidget.Show(False)
            self._fireCollapsedEvent()
        else:
            self.pulledDown = True
            self.detailsWidget.Show(True)
            self._fireExpandedEvent()
        
        self.detailsButton.setPulledDown(self.pulledDown)
        self._setInternalSize()
        self.Layout()
        event.Skip()
    # end onDetailsButtonClicked()
    
    def onResize(self, event):
        self.detailsButton.Refresh()
        event.Skip()
    # end onResize()

    def _createDetailsButton(self):
        return ZDetailsButton(self)
    # end _createDetailsButton()
    
    def _setInternalSize(self):
        (w, h) = self.GetBestSizeTuple() #@UnusedVariable
        self.SetSize(wx.Size(-1, h))
    # end _setInternalSize()

    def _fireExpandedEvent(self):
        event = ZDetailsPanelExpandedEvent(self.GetId())
        self.GetEventHandler().AddPendingEvent(event)
    # end _fireExpandedEvent()

    def _fireCollapsedEvent(self):
        event = ZDetailsPanelCollapsedEvent(self.GetId())
        self.GetEventHandler().AddPendingEvent(event)
    # end _fireCollapsedEvent()

# end ZDetailsPanel
