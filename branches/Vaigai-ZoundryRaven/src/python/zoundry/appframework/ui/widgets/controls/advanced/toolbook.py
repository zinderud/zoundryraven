from zoundry.appframework.ui.events.toolbookevents import ZEVT_TOOLBOOK_SELECTED
from zoundry.appframework.ui.events.toolbookevents import fireToolBookSelectedEvent
from zoundry.appframework.ui.events.toolbookevents import fireToolBookSelectingEvent
from zoundry.appframework.ui.util.fontutil import getTextDimensions
from zoundry.appframework.ui.util.colorutil import getDefaultControlBackgroundColor
from zoundry.appframework.ui.util.fontutil import getDefaultFont
from zoundry.appframework.ui.widgets.controls.common.panel import ZTransparentPanel
from zoundry.appframework.ui.widgets.controls.mixins.clickmixin import ZClickableControlMixin
from zoundry.appframework.ui.widgets.controls.mixins.hovermixin import ZHoverableControlMixin
import wx

TOOL_PADDING_LEFT = 4
TOOL_PADDING_RIGHT = 4
TOOL_PADDING_TOP = 2
TOOL_PADDING_BOTTOM = 2


# ------------------------------------------------------------------------------
# A single tool in the tool book's tool area.
# ------------------------------------------------------------------------------
class ZToolBookTool(wx.PyControl, ZClickableControlMixin, ZHoverableControlMixin):

    def __init__(self, parent, text, description, bitmap, hoverBitmap, selectedBitmap, data):
        self.parent = parent
        self.text = text
        self.description = description
        self.bitmap = bitmap
        self.hoverBitmap = hoverBitmap
        self.selectedBitmap = selectedBitmap
        self.data = data
        
        self.selected = False
        
        self.selectedBackgroundColor = wx.Color(200, 200, 225)
        self.hoverBackgroundColor = wx.Color(225, 225, 250)

        wx.PyControl.__init__(self, parent, wx.ID_ANY, style = wx.NO_BORDER)
        ZClickableControlMixin.__init__(self, False)
        ZHoverableControlMixin.__init__(self)

        self.SetFont(getDefaultFont())

        self._resize()

        self.Bind(wx.EVT_PAINT, self.onPaint, self)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.onEraseBackground, self)
    # end __init__()
    
    def setSelected(self, selected):
        self.selected = selected
        self.Refresh()
    # end setSelected()

    def _calculateSize(self):
        (textW, textH) = getTextDimensions(self.text, self)

        width = max(self.bitmap.GetWidth(), textW) + TOOL_PADDING_LEFT + TOOL_PADDING_RIGHT
        height = self.bitmap.GetHeight() + 3 + textH + TOOL_PADDING_TOP + TOOL_PADDING_BOTTOM
        
        return (width, height)
    # end _calculateSize()
    
    def _resize(self):
        (w, h) = self._calculateSize()
        self.SetSizeHints(w, h, w, h)
        self.SetSize(wx.Size(w, h))
    # end _resize()

    def onEraseBackground(self, event): #@UnusedVariable
        pass
    # end onEraseBackground()

    def onPaint(self, event):
        paintDC = wx.BufferedPaintDC(self)
        paintDC.SetBackground(wx.Brush(self.GetParent().GetBackgroundColour(), wx.SOLID))
        paintDC.Clear()
        
        # 1) draw background [hover, selected, none]
        self._drawBackground(paintDC)
        # 2) draw bitmap [hover, selected, none]
        self._drawBitmap(paintDC)
        # 3) draw label
        self._drawLabel(paintDC)

        del paintDC
        event.Skip()
    # end onPaint()
    
    def _drawBackground(self, paintDC):
        bgColor = self._getBackgroundColor()
        if bgColor is not None:
            (w, h) = self.GetSizeTuple()
            paintDC.SetBrush(wx.Brush(bgColor, wx.SOLID))
            paintDC.SetPen(wx.TRANSPARENT_PEN)
            paintDC.DrawRectangle(0, 0, w, h)
    # end _drawBackground()

    def _drawBitmap(self, paintDC):
        bitmap = self._getBitmap()

        (w, h) = self.GetSizeTuple() #@UnusedVariable
        x = (w - bitmap.GetWidth()) / 2
        y = TOOL_PADDING_TOP

        paintDC.DrawBitmap(self.bitmap, x, y)
    # end _drawBitmap()

    def _drawLabel(self, paintDC):
        (w, h) = self.GetSizeTuple()
        (textW, textH) = getTextDimensions(self.text, self)
        x = (w - textW) / 2
        y = h - textH - TOOL_PADDING_BOTTOM

        paintDC.SetFont(self.GetFont())
        paintDC.DrawText(self.text, x, y)
    # end _drawLabel()
    
    def _getBitmap(self):
        if self.selected and self.selectedBitmap:
            return self.selectedBitmap
        if self._isHovering() and self.hoverBitmap:
            return self.hoverBitmap
        return self.bitmap
    # end _getBitmap()
    
    def _getBackgroundColor(self):
        if self.selected:
            return self.selectedBackgroundColor
        if self._isHovering():
            return self.hoverBackgroundColor
        return None
    # end _getBackgroundColor()

    def _onLeftClick(self, mouseXY): #@UnusedVariable
        # If not already selected, do the selection logic
        if not self.selected and self.parent.onToolSelecting(self):
            self.selected = True
            self.parent.onToolSelected(self)
            return True
    # end _onLeftClick()
    
    def _onHoverBegin(self):
        return True
    # end _onHoverBegin()

    def _onHoverEnd(self):
        return True
    # end _onHoverEnd()

# end ZToolBookTool


# ------------------------------------------------------------------------------
# The area in which the tool icons live.
# ------------------------------------------------------------------------------
class ZToolBookToolArea(wx.Panel):
    
    def __init__(self, parent):
        self.parent = parent
        self.tools = []
        self.selectedTool = None

        wx.Panel.__init__(self, parent, wx.ID_ANY)
        self.SetBackgroundColour(getDefaultControlBackgroundColor())
        
        self.toolSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.toolSizer.AddSpacer(10)
        
        self.SetAutoLayout(True)
        self.SetSizer(self.toolSizer)
        self.Layout()
    # end __init__()

    def addTool(self, text, description, bitmap, hoverBitmap = None, selectedBitmap = None, data = None):
        u"""addTool(string, wx.Bitmap, wx.Bitmap, wx.Bitmap, object) -> id
        Adds a tool to the tool area and returns the new 
        tool's ID.""" #$NON-NLS-1$
        
        tool = ZToolBookTool(self, text, description, bitmap, hoverBitmap, selectedBitmap, data)
        self.tools.append(tool)
        self.toolSizer.Add(tool, 0)
        self.toolSizer.AddSpacer(3)
        
        if self.selectedTool is None:
            self.selectedTool = tool
            tool.setSelected(True)

        self.Refresh()
        self.Layout()
        
        return tool.GetId()
    # end addTool()
    
    def onToolSelecting(self, tool):
        event = fireToolBookSelectingEvent(self.parent, tool.GetId(), True)
        return not event.isVetoed()
    # end onToolSelecting()

    def onToolSelected(self, tool):
        if self.selectedTool is not None:
            self.selectedTool.setSelected(False)
            self.selectedTool = tool
        fireToolBookSelectedEvent(self.parent, tool.GetId())
    # end onToolSelected()

# end ZToolBookToolArea


# ------------------------------------------------------------------------------
# Implements a tool book.  This class is much like the standard wxToolBook, but
# looks nicer (doesn't use an actual tool bar, for instance).  The look
# of this control was originally modelled after the prefs toolbook control in
# firefox 2.x.
# ------------------------------------------------------------------------------
class ZToolBook(ZTransparentPanel):

    def __init__(self, parent):
        self.currentPage = None
        self.toolIdToPageMap = {}

        ZTransparentPanel.__init__(self, parent, wx.ID_ANY)
        
        self.toolArea = ZToolBookToolArea(self)
        self.separator = wx.StaticLine(self, wx.ID_ANY)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.toolArea, 0, wx.EXPAND)
        sizer.Add(self.separator, 0, wx.EXPAND)
        
        self.toolPageSizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddSizer(self.toolPageSizer, 1, wx.EXPAND)

        self.Bind(ZEVT_TOOLBOOK_SELECTED, self.onToolSelected, self)
        
        self.SetAutoLayout(True)
        self.SetSizer(sizer)
        self.Layout()
    # end __init__()

    def addPage(self, page, label, description, bitmap, hoverBitmap = None, selectedBitmap = None, data = None):
        toolId = self.toolArea.addTool(label, description, bitmap, hoverBitmap, selectedBitmap, data)
        self.toolPageSizer.Add(page, 1, wx.EXPAND)
        self.toolIdToPageMap[toolId] = page
        if self.currentPage is None:
            self.currentPage = page
        else:
            page.Show(False)
            self.Layout()
    # end addPage()
    
    def onToolSelected(self, event):
        if self.currentPage is not None:
            self.currentPage.Show(False)
        self.currentPage = self.toolIdToPageMap[event.getToolId()]
        self.currentPage.Show(True)
        self.Layout()
    # end onToolSelected()

# end ZToolBook
