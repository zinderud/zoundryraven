from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.messages import _extstr
from zoundry.appframework.ui.events.toolbarevents import ZEVT_TOOL_BUTTON
from zoundry.appframework.ui.events.toolbarevents import ZEVT_TOOL_DROPDOWN_BUTTON
from zoundry.appframework.ui.events.toolbarevents import ZEVT_TOOL_RIGHT_CLICK
from zoundry.appframework.ui.events.toolbarevents import ZEVT_TOOL_TOGGLE_BUTTON
from zoundry.appframework.ui.events.toolbarevents import ZToolBarResizeEvent
from zoundry.appframework.ui.events.toolbarevents import ZToolButtonEvent
from zoundry.appframework.ui.events.toolbarevents import ZToolDropDownEvent
from zoundry.appframework.ui.events.toolbarevents import ZToolRightClickEvent
from zoundry.appframework.ui.events.toolbarevents import ZToolToggleEvent
from zoundry.appframework.ui.util.colorutil import getDefaultDialogBackgroundColor
from zoundry.appframework.ui.util.colorutil import getDisabledTextColor
from zoundry.appframework.ui.util.fontutil import getDefaultFont
from zoundry.appframework.ui.util.fontutil import getTextDimensions
from zoundry.appframework.ui.widgets.controls.common.menu.menu import ZMenu
from zoundry.appframework.ui.widgets.controls.common.menu.menumodel import ZMenuModel
from zoundry.appframework.ui.widgets.controls.common.menu.menumodel import ZModelBasedMenuContentProvider
from zoundry.appframework.ui.widgets.controls.common.menu.menumodel import ZModelBasedMenuEventHandler
from zoundry.appframework.ui.widgets.controls.common.toolbar.toolbaractions import ZResizeToolbarAction
from zoundry.appframework.ui.widgets.controls.common.toolbar.toolbaractions import ZShowTextMenuAction
from zoundry.appframework.ui.widgets.controls.common.toolbar.toolbaractions import ZToolBarMenuContext
from zoundry.appframework.ui.widgets.controls.common.toolbar.toolbarart import drawArrow
from zoundry.appframework.ui.widgets.controls.common.toolbar.toolbarart import drawClickBorder
from zoundry.appframework.ui.widgets.controls.common.toolbar.toolbarart import drawClickSepLine
from zoundry.appframework.ui.widgets.controls.common.toolbar.toolbarart import drawHoverBorder
from zoundry.appframework.ui.widgets.controls.common.toolbar.toolbarart import drawHoverSepLine
from zoundry.appframework.ui.widgets.controls.common.toolbar.toolbarart import drawToggleBorder
from zoundry.appframework.ui.widgets.controls.mixins.clickmixin import ZClickableControlMixin
from zoundry.appframework.ui.widgets.controls.mixins.hovermixin import ZHoverableControlMixin
from zoundry.appframework.global_services import getLoggerService
import wx

ZTOOL_PADDING = 3
ZTOOL_DROPDOWN_PADDING = 11

# ------------------------------------------------------------------------------
# The interface for the content provider that is used when creating a ZToolBar.
# ------------------------------------------------------------------------------
class IZToolBarContentProvider:

    def getToolBitmapSizes(self):
        u"""getToolBitmapSizes() -> int[]
        Returns the supported toolbar bitmap sizes.  This
        value will be an OR of the above ZTOOLBAR_BITMAP_SIZE_*
        globals.""" #$NON-NLS-1$
    # end getToolBitmapSizes()

    def getToolBitmapSize(self):
        u"""getToolBitmapSizes() -> int
        Returns the current size of the toolbar's tool
        bitmaps.  This value should be a single one of the
        above ZTOOLBAR_BITMAP_SIZE_* global values.""" #$NON-NLS-1$
    # end getToolBitmapSize()

    def getToolBarNodes(self):
        u"""getToolBarNodes() -> object[]
        Gets the list of toolbar nodes.  The return
        value can be a list of any type.""" #$NON-NLS-1$
    # end getToolBarNodes()

    def getText(self, node):
        u"""getText(object) -> string
        Gets the text associated with the given
        toolbar node.""" #$NON-NLS-1$
    # end getText()

    def getDescription(self, node):
        u"""getDescription(object) -> string
        Gets the description for this toolbar node.""" #$NON-NLS-1$
    # end getDescription()

    def getBitmap(self, node, size):
        u"""getBitmap(object, int) -> wx.Bitmap
        Gets the bitmap associated with the given
        toolbar node.""" #$NON-NLS-1$
    # end getBitmap()

    def getDisabledBitmap(self, node, size):
        u"""getDisabledBitmap(object, int) -> wx.Bitmap
        Gets the bitmap that is shown when a toolbar
        node is disabled.  Return None to let the
        system generate a reasonable bitmap.""" #$NON-NLS-1$
    # end getDisabledBitmap()

    def getHoverBitmap(self, node, size):
        u"""getHoverBitmap(object, int) -> wx.Bitmap
        Gets the bitmap that is shown when the user
        hovers over the tool represented by the given
        node.""" #$NON-NLS-1$
    # end getHoverBitmap()

    def isSeparator(self, node):
        u"""isSeparator(object) -> boolean
        Returns True if this node represents a toolbar
        separator.""" #$NON-NLS-1$
    # end isSeparator()

    def isToggleTool(self, node):
        u"""isToggle(object) -> boolean
        Returns True if the given node represents a
        toggle style toolbar node.""" #$NON-NLS-1$
    # end isToggleTool()

    def isDropDownTool(self, node):
        u"""isDropDownTool(object) -> boolean
        Returns True if the given node represents a
        drop-down style tool.""" #$NON-NLS-1$
    # end isDropDownTool()

    def getDropDownMenuModel(self, node):
        u"""getDropDownMenuModel(object) -> ZMenuModel
        Returns the menu model that should be used
        to display the menu when a user clicks on the
        drop-down arrow portion of a drop-down style
        tool.""" #$NON-NLS-1$
    # end getDropDownMenuModel()

    def isEnabled(self, node):
        u"""isEnabled(object) -> boolean
        Returns True if the given toolbar node is
        currently enabled.""" #$NON-NLS-1$
    # end isEnabled()

    def isDepressed(self, node):
        u"""isDepressed(object) -> boolean
        Returns True if the current state of the
        given toolbar node is 'depressed'.  Only
        valid for toggle style tools.""" #$NON-NLS-1$
    # end isDepressed()

# end IZToolBarContentProvider


# ------------------------------------------------------------------------------
# Empty toolbar impl - useful when planning on setting the toolbar's content
# provider at a later time.
# ------------------------------------------------------------------------------
class ZEmptyToolBarProvider(IZToolBarContentProvider):

    def getToolBitmapSizes(self):
        return []
    # end getToolBitmapSizes()

    def getToolBitmapSize(self):
        return -1
    # end getToolBitmapSize()

    def getToolBarNodes(self):
        return []
    # end getToolBarNodes()

# end ZEmptyToolBarProvider


# ------------------------------------------------------------------------------
# Toolbar event handler interface.
# ------------------------------------------------------------------------------
class IZToolBarEventHandler:

    def onToolClick(self, toolNode):
        u"""onToolClick(object) -> None
        Called when the user clicks on a tool in the
        tool bar (either a normal style tool or the
        left part of a drop-down style tool).""" #$NON-NLS-1$
    # end onToolClick()

    def onToggleToolClick(self, toolNode, depressed):
        u"""onToggleToolClick(object, boolean) -> None
        Called when the user clicks on a toggle-style
        tool bar tool.  The 'depressed' parameter
        indicates whether the tool is now in a
        depressed state.""" #$NON-NLS-1$
    # end onToggleToolClick()

    def onDropDownToolClick(self, toolNode, toolPosition, toolSize):
        u"""onDropDownToolClick(object, (int, int), (int, int)) -> None
        Called when the user clicks on a drop-down
        style tool bar tool.  The toolPosition and
        toolSize parameters provide a helpful way
        to position some sort of menu or transient
        window as the result of the drop-down click.""" #$NON-NLS-1$
    # end onDropDownToolClick()

# end IZToolBarEventHandler


# ------------------------------------------------------------------------------
# Each tool in the toolbar is represented by an instance of this class.
# ------------------------------------------------------------------------------
class ZTool(wx.PyControl, ZClickableControlMixin, ZHoverableControlMixin):

    def __init__(self, parent, text, description, bitmaps, hoverBitmaps, disabledBitmaps, node):
        self.text = text
        self.description = description
        self.bitmaps = bitmaps
        self.hoverBitmaps = hoverBitmaps
        self.disabledBitmaps = disabledBitmaps
        self.node = node
        self.showTextFlag = True
        self.toolBitmapSize = 16

        wx.PyControl.__init__(self, parent, wx.ID_ANY, style = wx.NO_BORDER)
        ZClickableControlMixin.__init__(self, False)
        ZHoverableControlMixin.__init__(self)

        self.SetFont(getDefaultFont())
        self.SetToolTipString(self.description)
        self._resize()

        self.Bind(wx.EVT_PAINT, self.onPaint, self)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.onEraseBackground, self)
    # end __init__()

    def getNode(self):
        return self.node
    # end getNode()

    def setText(self, text):
        self.text = text
    # end setText()

    def setDescription(self, description):
        self.description = description
        self.SetToolTipString(self.description)
    # end setDescription()

    def showText(self, showTextFlag = True):
        self.showTextFlag = showTextFlag
        self._resize()
    # end showText

    def setToolBitmapSize(self, toolBitmapSize):
        self.toolBitmapSize = toolBitmapSize
        self._resize()
    # end setToolBitmapSize()

    def _calculateSize(self):
        minWidth = self.toolBitmapSize + ZTOOL_PADDING + ZTOOL_PADDING
        minHeight = self.toolBitmapSize + ZTOOL_PADDING + ZTOOL_PADDING

        if self.showTextFlag:
            (w, h) = getTextDimensions(self.text, self)
            tmWidth = w + ZTOOL_PADDING * 4
            tmHeight = h

            minWidth = max(minWidth, tmWidth)
            minHeight = minHeight + tmHeight

        return (minWidth, minHeight)
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

        try:
            self._doPaint(paintDC)
        finally:
            del paintDC

        event.Skip()
    # end onPaint()

    def _doPaint(self, paintDC):
        try:
            self._drawBorder(paintDC)
            self._drawBitmap(paintDC)
            if self.showTextFlag:
                self._drawText(paintDC)
        except Exception, e:
            getLoggerService().exception(e)
    # end _doPaint()

    def _drawBorder(self, paintDC):
        try:
            dc = wx.GCDC(paintDC)
            self._drawGCDCBorder(dc)
        except:
            self._drawBitmapBorder(paintDC)
    # end _drawBorder()

    def _drawGCDCBorder(self, dc):
        (w, h) = self.GetSizeTuple()
        if self._isLeftClicking():
            self._drawGCDCClickBorder(dc, w, h)
        elif self._isHovering():
            self._drawGCDCHoverBorder(dc, w, h)
    # end _drawGCDCBorder()

    def _drawGCDCClickBorder(self, dc, w, h):
        fillColor = wx.Colour(0, 0, 0, 12)
        borderColor = wx.Colour(0, 0, 0, 89)
        dc.SetPen(wx.Pen(borderColor))
        dc.SetBrush(wx.Brush(fillColor))
        rect = wx.Rect(0, 0, w, h)
        dc.DrawRoundedRectangleRect(rect, 3)
    # end _drawGCDCClickBorder()

    def _drawGCDCHoverBorder(self, dc, w, h):
        fillColor = wx.Colour(255, 255, 255, 199)
        borderColor = wx.Colour(0, 0, 0, 30)
        dc.SetPen(wx.Pen(borderColor))
        dc.SetBrush(wx.Brush(fillColor))
        rect = wx.Rect(0, 0, w, h)
        dc.DrawRoundedRectangleRect(rect, 3)
    # end _drawGCDCHoverBorder()

    def _drawBitmapBorder(self, paintDC):
        (w, h) = self.GetSizeTuple()
        if self._isLeftClicking():
            self._drawBitmapClickBorder(paintDC, w, h)
        elif self._isHovering():
            self._drawBitmapHoverBorder(paintDC, w, h)
    # end _drawBitmapBorder()

    def _drawBitmapClickBorder(self, paintDC, w, h):
        drawClickBorder(paintDC, w, h)
    # end _drawBitmapClickBorder()

    def _drawBitmapHoverBorder(self, paintDC, w, h):
        drawHoverBorder(paintDC, w, h)
    # end _drawBitmapHoverBorder()

    def _drawBitmap(self, paintDC):
        bitmap = self._getBitmap()
        if bitmap is not None:
            bmpX = (self._getToolDrawSize()[0] - bitmap.GetWidth()) / 2
            bmpY = ZTOOL_PADDING
            if self._isLeftClicking():
                bmpX += 1
                bmpY += 1
            paintDC.DrawBitmap(bitmap, bmpX, bmpY, False)
    # end _drawBitmap()

    def _drawText(self, paintDC):
        (textW, textH) = getTextDimensions(self.text, self)
        (w, h) = self._getToolDrawSize()
        textX = ZTOOL_PADDING * 2
        textY = h - textH - ZTOOL_PADDING
        if textW < self.toolBitmapSize:
            textX = (w - textW) / 2
        if self._isLeftClicking():
            textX += 1
            textY += 1

        if not self.IsEnabled():
            paintDC.SetTextForeground(getDisabledTextColor())
        paintDC.SetFont(self.GetFont())
        paintDC.DrawText(self.text, textX, textY)
    # end _drawText()

    # Gets the size of the tool for bitmap and text
    # drawing purposes.
    def _getToolDrawSize(self):
        return self.GetSizeTuple()
    # end _getToolDrawSize()

    def _getBitmap(self):
        if not self.IsEnabled() and self.toolBitmapSize in self.disabledBitmaps:
            return self.disabledBitmaps[self.toolBitmapSize]
        if self._isHovering() and self.toolBitmapSize in self.hoverBitmaps:
            return self.hoverBitmaps[self.toolBitmapSize]
        return self.bitmaps[self.toolBitmapSize]
    # end _getBitmap();

    def _fireButtonEvent(self):
        event = ZToolButtonEvent(self.GetId(), self.node)
        self.GetEventHandler().AddPendingEvent(event)
    # end _fireButtonEvent()

    def _onLeftClicking(self, mouseXY): #@UnusedVariable
        return True
    # end _onLeftClicking()

    def _onLeftClick(self, mouseXY): #@UnusedVariable
        self._fireButtonEvent()
        return True
    # end _onLeftClick()

    def _onRightClick(self, mouseXY): #@UnusedVariable
        event = ZToolRightClickEvent(self.GetId(), self.node)
        self.GetEventHandler().AddPendingEvent(event)
    # end _onRightClick()

    def _onHoverBegin(self):
        return True
    # end _onHoverBegin()

    def _onHoverEnd(self):
        return True
    # end _onHoverEnd()

    def isToggle(self):
        return False
    # end isToggle()

    def isDropDown(self):
        return False
    # end isDropDown()

    def AcceptsFocusFromKeyboard(self):
        return False
    # end AcceptsFocusFromKeyboard()

# end ZTool


# ------------------------------------------------------------------------------
# Implements a toggle tool.
# ------------------------------------------------------------------------------
class ZToggleTool(ZTool):

    def __init__(self, *args, **kw):
        self.toggled = False

        ZTool.__init__(self, *args, **kw)
    # end __init__()

    def toggle(self, toggled = True):
        self.toggled = toggled
    # end toggle()

    def isToggled(self):
        return self.toggled
    # end isToggled()

    def isToggle(self):
        return True
    # end isToggle()

    def _fireToggleEvent(self):
        event = ZToolToggleEvent(self.GetId(), self.node, self.isToggled())
        self.GetEventHandler().AddPendingEvent(event)
    # end _fireToggleEvent()

    def _onLeftClick(self, mouseXY): #@UnusedVariable
        self.toggled = not self.toggled
        self._fireToggleEvent()
        return True
    # end _onLeftClick()

    def _drawGCDCBorder(self, dc):
        (w, h) = self.GetSizeTuple()
        if self.isToggled():
            self._drawGCDCToggleBorder(dc, w, h)

        ZTool._drawGCDCBorder(self, dc)
    # end _drawGCDCBorder()

    def _drawGCDCToggleBorder(self, dc, w, h):
        fillColor = wx.Colour(255, 255, 255, 255)
        borderColor = wx.Colour(123, 154, 173, 255)
        dc.SetPen(wx.Pen(borderColor))
        dc.SetBrush(wx.Brush(fillColor))
        rect = wx.Rect(0, 0, w, h)
        dc.DrawRoundedRectangleRect(rect, 3)
    # end _drawGCDCToggleBorder()

    def _drawBitmapBorder(self, paintDC):
        (w, h) = self.GetSizeTuple()
        if self.isToggled():
            drawToggleBorder(paintDC, w, h)
        ZTool._drawBitmapBorder(self, paintDC)
    # end _drawBitmapBorder()

# end ZToggleTool


# ------------------------------------------------------------------------------
# Implements a drop-down style tool.
# ------------------------------------------------------------------------------
class ZDropDownTool(ZTool):

    def __init__(self, *args, **kw):
        ZTool.__init__(self, *args, **kw)
    # end __init__()

    def _calculateSize(self):
        (minWidth, minHeight) = ZTool._calculateSize(self)
        return (minWidth + ZTOOL_DROPDOWN_PADDING, minHeight)
    # end _calculateSize()

    def _drawGCDCBorder(self, dc):
        ZTool._drawGCDCBorder(self, dc)
        self._drawArrow(dc)
    # end _drawGCDCBorder()

    def _drawGCDCClickBorder(self, dc, w, h):
        ZTool._drawGCDCClickBorder(self, dc, w, h)

        (startX, startY, endX, endY) = self._getSepLineBounds()
        drawClickSepLine(dc, startX, startY, endX, endY)
    # end _drawGCDCClickBorder()

    def _drawGCDCHoverBorder(self, dc, w, h):
        ZTool._drawGCDCHoverBorder(self, dc, w, h)

        (startX, startY, endX, endY) = self._getSepLineBounds()
        drawHoverSepLine(dc, startX, startY, endX, endY)
    # end _drawGCDCHoverBorder()

    def _drawBitmapBorder(self, paintDC):
        ZTool._drawBitmapBorder(self, paintDC)
        self._drawArrow(paintDC)
    # end _drawBitmapBorder()

    def _drawBitmapClickBorder(self, paintDC, w, h):
        ZTool._drawBitmapClickBorder(self, paintDC, w, h)

        (startX, startY, endX, endY) = self._getSepLineBounds()
        drawClickSepLine(paintDC, startX, startY, endX, endY)
    # end _drawBitmapClickBorder()

    def _drawBitmapHoverBorder(self, paintDC, w, h):
        ZTool._drawBitmapHoverBorder(self, paintDC, w, h)

        (startX, startY, endX, endY) = self._getSepLineBounds()
        drawHoverSepLine(paintDC, startX, startY, endX, endY)
    # end _drawBitmapHoverBorder()

    def _drawArrow(self, paintDC):
        (w, h) = self.GetSizeTuple()
        x = w - 8
        y = h / 2 - 2
        drawArrow(paintDC, x, y)
    # end _drawArrow()

    def _getSepLineBounds(self):
        (w, h) = self.GetSizeTuple()
        startY = 2
        endY = h - 2
        x = w - ZTOOL_DROPDOWN_PADDING
        return (x, startY, x, endY)
    # end _getSepLineBounds()

    # Gets the size of the tool for bitmap and text
    # drawing purposes.
    def _getToolDrawSize(self):
        (w, h) = ZTool._getToolDrawSize(self)
        return (w - ZTOOL_DROPDOWN_PADDING, h)
    # end _getToolDrawSize()

    def _onLeftClick(self, mouseXY): #@UnusedVariable
        mouseX = mouseXY[0]
        sepLineX = self._getSepLineBounds()[0]
        if mouseX >= sepLineX:
            self._fireDropDownEvent()
            return True
        else:
            return ZTool._onLeftClick(self, mouseXY)
    # end _onLeftClick()

    def _fireDropDownEvent(self):
        event = ZToolDropDownEvent(self.GetId(), self.node, self.GetScreenPositionTuple(), self.GetSizeTuple())
        self.GetEventHandler().AddPendingEvent(event)
    # end _fireDropDownEvent()

    def isDropDown(self):
        return True
    # end isDropDown()

# end ZDropDownTool


# ------------------------------------------------------------------------------
# A content provider based (and owner-drawn) implementation of a Toolbar.
# ------------------------------------------------------------------------------
class ZToolBar(wx.Panel):

    STYLE_SHOW_TEXT = 1
    STYLE_DIVIDER = 2

    def __init__(self, contentProvider, eventHandler, parent, style = 0):
        self.style = style
        self.tools = []
        self.contentProvider = contentProvider
        if self.contentProvider is None:
            self.contentProvider = ZEmptyToolBarProvider()
        self.eventHandler = eventHandler
        self.showTextFlag = False
        self.toolSize = self.contentProvider.getToolBitmapSize()

        wx.Panel.__init__(self, parent, wx.ID_ANY)
        self.SetBackgroundColour(getDefaultDialogBackgroundColor())

        self._createWidgets()
        self._layoutWidgets()
        self._bindWidgetEvents()

        if style & ZToolBar.STYLE_SHOW_TEXT:
            self.showText(True)
        else:
            self.showText(False)

        self.refresh()
    # end __init__()

    def _createWidgets(self):
        validSizes = self.contentProvider.getToolBitmapSizes()
        for node in self.contentProvider.getToolBarNodes():
            if self.contentProvider.isSeparator(node):
                self.tools.append(wx.StaticLine(self, wx.ID_ANY, style = wx.VERTICAL))
            else:
                text = self.contentProvider.getText(node)
                description = self.contentProvider.getDescription(node)
                bitmaps = self._getBitmaps(node, validSizes)
                hoverBitmaps = self._getHoverBitmaps(node, validSizes)
                disabledBitmaps = self._getDisabledBitmaps(node, validSizes)
                if self.contentProvider.isToggleTool(node):
                    tool = ZToggleTool(self, text, description, bitmaps, hoverBitmaps, disabledBitmaps, node)
                    tool.toggle(self.contentProvider.isDepressed(node))
                elif self.contentProvider.isDropDownTool(node):
                    tool = ZDropDownTool(self, text, description, bitmaps, hoverBitmaps, disabledBitmaps, node)
                else:
                    tool = ZTool(self, text, description, bitmaps, hoverBitmaps, disabledBitmaps, node)
                tool.setToolBitmapSize(self.toolSize)
                tool.showText(self.showTextFlag)
                tool.Enable(self.contentProvider.isEnabled(node))
                self.tools.append(tool)

        if self.style & ZToolBar.STYLE_DIVIDER:
            self.divider = wx.StaticLine(self, wx.HORIZONTAL)
        self.contextMenuModel = self._createContextMenuModel()
    # end _createWidgets()

    def _getBitmaps(self, node, validSizes):
        bitmaps = {}
        for validSize in validSizes:
            bmp = self.contentProvider.getBitmap(node, validSize)
            if bmp is not None:
                bitmaps[validSize] = bmp
        return bitmaps
    # end _getBitmaps()

    def _getHoverBitmaps(self, node, validSizes):
        bitmaps = {}
        for validSize in validSizes:
            bmp = self.contentProvider.getHoverBitmap(node, validSize)
            if bmp is not None:
                bitmaps[validSize] = bmp
        return bitmaps
    # end _getHoverBitmaps()

    def _getDisabledBitmaps(self, node, validSizes):
        bitmaps = {}
        for validSize in validSizes:
            bmp = self.contentProvider.getDisabledBitmap(node, validSize)
            if bmp is not None:
                bitmaps[validSize] = bmp
        return bitmaps
    # end _getDisabledBitmaps()

    def _createContextMenuModel(self):
        menuModel = ZMenuModel()
        validSizes = self.contentProvider.getToolBitmapSizes()
        if len(validSizes) > 1:
            subMenuID = menuModel.addMenu(_extstr(u"toolbar.ToolSize"), 0) #$NON-NLS-1$
            for vsize in validSizes:
                menuID = menuModel.addMenuItemWithAction(u"%d x %d" % (vsize, vsize), 0, ZResizeToolbarAction(vsize), subMenuID) #$NON-NLS-1$
                menuModel.setMenuItemCheckbox(menuID, True)
            menuModel.addSeparator(0)
        menuID = menuModel.addMenuItemWithAction(_extstr(u"toolbar.ShowText"), 0, ZShowTextMenuAction()) #$NON-NLS-1$
        menuModel.setMenuItemCheckbox(menuID, True)
        return menuModel
    # end _createContextMenuModel()

    def _layoutWidgets(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        for tool in self.tools:
            if isinstance(tool, ZTool):
                sizer.Add(tool, 0, wx.ALL, 1)
            else:
                sizer.Add(tool, 0, wx.EXPAND | wx.ALL, 5)

        if self.style & ZToolBar.STYLE_DIVIDER:
            hsizer = sizer
            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.AddSizer(hsizer, 0, wx.EXPAND)
            sizer.Add(self.divider, 0, wx.EXPAND)

        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        self.Layout()
    # end _layoutWidgets()

    def _bindWidgetEvents(self):
        self.Bind(wx.EVT_LEFT_DOWN, self.onLeftClick, self)
        self.Bind(wx.EVT_RIGHT_UP, self.onRightClick, self)
        self._bindToolEvents()
    # end _bindWidgetEvents()

    def _bindToolEvents(self):
        for tool in self.tools:
            if isinstance(tool, ZTool):
                self.Bind(ZEVT_TOOL_RIGHT_CLICK, self.onRightClick, tool)
                if tool.isToggle():
                    self.Bind(ZEVT_TOOL_TOGGLE_BUTTON, self.onToggleButton, tool)
                elif tool.isDropDown():
                    self.Bind(ZEVT_TOOL_DROPDOWN_BUTTON, self.onDropDownButton, tool)
                    self.Bind(ZEVT_TOOL_BUTTON, self.onToolButton, tool)
                else:
                    self.Bind(ZEVT_TOOL_BUTTON, self.onToolButton, tool)
    # end _bindToolEvents()

    def isShowText(self):
        return self.showTextFlag
    # end isShowText()

    def showText(self, showFlag = True):
        self.showTextFlag = showFlag
        for tool in self.tools:
            if isinstance(tool, ZTool):
                tool.showText(showFlag)
        self.Layout()
        self.Refresh()
        self._fireResizeEvent()
    # end showText()

    def setToolSize(self, size):
        self.toolSize = size
        for tool in self.tools:
            if isinstance(tool, ZTool):
                tool.setToolBitmapSize(size)
        self.Layout()
        self.Refresh()
        self._fireResizeEvent()
    # end setToolSize()

    def getToolSize(self):
        return self.toolSize
    # end getToolSize()

    def onToggleButton(self, event):
        self.eventHandler.onToggleToolClick(event.getToolNode(), event.isToggled())
        event.Skip()
    # end onToggleButton()

    def onDropDownButton(self, event):
        self.eventHandler.onDropDownToolClick(event.getToolNode(), event.getPosition(), event.getSize())
        event.Skip()
    # end onDropDownButton()

    def onToolButton(self, event):
        self.eventHandler.onToolClick(event.getToolNode())
        event.Skip()
    # end onToolButton()

    def onLeftClick(self, event): #@UnusedVariable
        # Note: do not Skip() the event - eating it here prevents
        # the toolbar from ever stealing focus.
        pass
    # end onLeftClick()

    def onRightClick(self, event):
        menuContext = ZToolBarMenuContext(self)
        menuProvider = ZModelBasedMenuContentProvider(self.contextMenuModel, menuContext)
        eventHandler = ZModelBasedMenuEventHandler(self.contextMenuModel, menuContext)
        menu = ZMenu(self, self.contextMenuModel.getRootNode(), menuProvider, eventHandler)
        self.PopupMenu(menu)
        event.Skip()
    # end onRightClick()

    def setContentProvider(self, contentProvider, eventHandler):
        self.contentProvider = contentProvider
        self.eventHandler = eventHandler

        self.DestroyChildren()
        self.tools = []
        toolSize = self.contentProvider.getToolBitmapSize()
        if self.toolSize == -1:
            self.toolSize = toolSize
        self._createWidgets()
        self._layoutWidgets()
        self._bindToolEvents()
    # end setContentProvider()

    def refresh(self):
        modelNodes = self.contentProvider.getToolBarNodes()
        for modelNode in modelNodes:
            self._updateToolInfo(modelNode)
            # FIXME (EPW) support new tool node or tool node deleted
        self.Refresh()
    # end refresh()

    def _updateToolInfo(self, modelNode):
        if self.contentProvider.isSeparator(modelNode):
            return

        tool = self._findTool(modelNode)
        tool.Enable(self.contentProvider.isEnabled(modelNode))
        if self.contentProvider.isToggleTool(modelNode):
            tool.toggle(self.contentProvider.isDepressed(modelNode))
        tool.setDescription(self.contentProvider.getDescription(modelNode))
        tool.setText(self.contentProvider.getText(modelNode))
    # end _updateToolInfo()

    def _findTool(self, modelNode):
        for tool in self.tools:
            if isinstance(tool, ZTool):
                if tool.getNode() == modelNode:
                    return tool
        return None
    # end _findTool()

    def _fireResizeEvent(self):
        event = ZToolBarResizeEvent(self.GetId())
        self.GetEventHandler().AddPendingEvent(event)
    # end _fireResizeEvent()

# end ZToolBar


# ------------------------------------------------------------------------------
# Extends the base tool bar and adds persistence capabilities.  Simply construct
# this class with a user prefs ID that it can use to save/restore its own
# state.
# ------------------------------------------------------------------------------
class ZPersistentToolBar(ZToolBar):

    def __init__(self, prefsId, contentProvider, eventHandler, parent, style = 0):
        # Turn this flag on/off to change whether changes to the toolbar
        # get written to the user prefs.  This is useful to turn off when
        # initially un-persisting the toolbar settings.
        self.persistenceOn = False
        self.prefsId = prefsId
        self.userPrefs = getApplicationModel().getUserProfile().getPreferences()
        ZToolBar.__init__(self, contentProvider, eventHandler, parent, style)

        self._loadToolBarSettings()
        self.persistenceOn = True
    # end __init__()

    def _loadToolBarSettings(self):
        size = self.userPrefs.getUserPreferenceInt(self.prefsId + u".size", None) #$NON-NLS-1$
        showText = self.userPrefs.getUserPreferenceBool(self.prefsId + u".show-text", None) #$NON-NLS-1$

        if size is not None:
            self.setToolSize(size)
        if showText is not None:
            self.showText(showText)
    # end _loadToolBarSettings()

    def showText(self, showFlag = True):
        ZToolBar.showText(self, showFlag)

        if self.persistenceOn:
            self.userPrefs.setUserPreference(self.prefsId + u".show-text", showFlag) #$NON-NLS-1$
    # end showText()

    def setToolSize(self, size):
        ZToolBar.setToolSize(self, size)

        if self.persistenceOn:
            self.userPrefs.setUserPreference(self.prefsId + u".size", size) #$NON-NLS-1$
    # end setToolSize()

# end ZPersistentToolBar
