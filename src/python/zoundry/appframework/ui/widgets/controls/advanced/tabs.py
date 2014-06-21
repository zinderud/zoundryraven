from zoundry.appframework.exceptions import ZAppFrameworkException
from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.ui.events.tabevents import ZEVT_TAB_CLOSED
from zoundry.appframework.ui.events.tabevents import ZEVT_TAB_SELECTED
from zoundry.appframework.ui.events.tabevents import ZTabClosedEvent
from zoundry.appframework.ui.events.tabevents import ZTabSelectedEvent
from zoundry.appframework.ui.util.fontutil import getDefaultFont
from zoundry.appframework.ui.util.fontutil import getTextDimensions
from zoundry.appframework.ui.util.fontutil import sizeStringToFit
from zoundry.appframework.ui.widgets.controls.advanced.support.tabctxmenu import ZTabContextMenu
from zoundry.appframework.ui.widgets.controls.advanced.support.tabselpopup import ZTabSelectionPopupWindow
from zoundry.appframework.ui.widgets.controls.common.imgbutton import ZImageButton
import wx

TAB_BORDER_OUTER_COLOR = wx.Color(200, 200, 200)
TAB_BORDER_INNER_COLOR = wx.Color(150, 150, 150)
TAB_GRADIENT_COLORS=[
     (wx.Color(92, 126, 209), 6),
     (wx.Color(96, 129, 210), 4),
     (wx.Color(98, 131, 211), 3),
     (wx.Color(101, 133, 213), 2),
     (wx.Color(104, 136, 213), 2),
     (wx.Color(107, 138, 215), 1),
     (wx.Color(110, 141, 216), 1),
     (wx.Color(112, 144, 217), 1),
     (wx.Color(115, 146, 218), 1),
     (wx.Color(118, 148, 219), 1),
     (wx.Color(120, 151, 220), 1),
     (wx.Color(123, 154, 221), 1),
     (wx.Color(126, 156, 223), 1),
     (wx.Color(129, 159, 223), 1),
     (wx.Color(132, 162, 225), 1),
     (wx.Color(135, 164, 226), 1),
     (wx.Color(138, 167, 227), 1),
     (wx.Color(140, 169, 228), 1),
     (wx.Color(143, 172, 229), 1),
     (wx.Color(146, 175, 231), 1),
     (wx.Color(149, 177, 232), 1),
     (wx.Color(152, 180, 232), 1),
     (wx.Color(154, 183, 234), 1),
     (wx.Color(157, 185, 235), 1),
]
CONTAINER_INNER_BORDER_COLOR = wx.Color(157, 185, 235)
TAB_CONTAINER_INNER_BORDER_COLOR = wx.Color(157, 185, 235)


TOP_LEFT_ARC_OUTER_POINTS = [ (0, 5), (0, 4), (1, 3), (2, 2), (3, 1), (5, 0) ]
TOP_LEFT_ARC_INNER_POINTS = [ (1, 5), (1, 4), (2, 3), (3, 2), (4, 1), (5, 1) ]
TOP_RIGHT_ARC_OUTER_POINTS = [ (0, 0), (2, 1), (3, 2), (4, 3), (5, 4), (5, 5) ]
TOP_RIGHT_ARC_INNER_POINTS = [ (0, 1), (1, 1), (2, 2), (3, 3), (4, 4), (4, 5) ]

# ------------------------------------------------------------------------------
# Convenience method to draw a 6x6 arc in the top left corner of something.
# ------------------------------------------------------------------------------
def _drawTopLeftArc(dc, innerColor, outerColor, arcX, arcY):
    # Draw the outer part
    dc.SetPen(wx.Pen(outerColor))
    points = []
    for (x, y) in TOP_LEFT_ARC_OUTER_POINTS:
        points.append( (x + arcX, y + arcY) )
    dc.DrawPointList(points)

    # Draw the inner part
    dc.SetPen(wx.Pen(innerColor))
    points = []
    for (x, y) in TOP_LEFT_ARC_INNER_POINTS:
        points.append( (x + arcX, y + arcY) )
    dc.DrawPointList(points)
# end _drawTopLeftArc()


# ------------------------------------------------------------------------------
# Convenience method to draw a 6x6 arc in the top right corner of something.
# ------------------------------------------------------------------------------
def _drawTopRightArc(dc, innerColor, outerColor, arcX, arcY):
    # Draw the outer part
    dc.SetPen(wx.Pen(outerColor))
    points = []
    for (x, y) in TOP_RIGHT_ARC_OUTER_POINTS:
        points.append( (x + arcX, y + arcY) )
    dc.DrawPointList(points)

    # Draw the inner part
    dc.SetPen(wx.Pen(innerColor))
    points = []
    for (x, y) in TOP_RIGHT_ARC_INNER_POINTS:
        points.append( (x + arcX, y + arcY) )
    dc.DrawPointList(points)
# end _drawTopLeftArc()


# ------------------------------------------------------------------------------
# When using the tab container, new tabs are added by passing in an object of
# this type.  The tab info object contains all of the information that the
# tab container will need to properly render a tab.
# ------------------------------------------------------------------------------
class IZTabInfo:

    def getTitle(self):
        u"""getTitle() -> string
        Returns the title for the tab.""" #$NON-NLS-1$
    # end getTitle()

    def setTitle(self, title):
        u"""setTitle(string) -> None
        Sets the tab's title.""" #$NON-NLS-1$
    # end setTitle()

    def getBitmap(self):
        u"""getBitmap() -> wx.Bitmap
        Returns the bitmap for the tab.""" #$NON-NLS-1$
    # end getBitmap()

# end IZTabInfo


# ------------------------------------------------------------------------------
# A simple implementation of a tab info object.
# ------------------------------------------------------------------------------
class ZTabInfo(IZTabInfo):

    def __init__(self, title, bitmap):
        self.title = unicode(title)
        self.bitmap = bitmap
    # end __init__()

    def getTitle(self):
        return self.title
    # end getTitle()

    def setTitle(self, title):
        self.title = title
    # end setTitle()

    def getBitmap(self):
        return self.bitmap
    # end getBitmap()

# end ZTabInfo


# ------------------------------------------------------------------------------
# Represents a single tab in the tab bar.
#
# FIXME (EPW) use click and hover mixins
# FIXME (EPW) use ProcessEvent technique for handling veto-able events (see ZToolBook impl)
#
# Events (Note: attach a tab container listener for more events):
#   ZEVT_TAB_CLOSED:  fired when the user closes the tab
#   ZEVT_TAB_SELECTED:  fired when the user selects a tab
# ------------------------------------------------------------------------------
class ZTab(wx.Panel):

    def __init__(self, parent, tabInfo, selected = False):
        self.parent = parent
        self.tabInfo = tabInfo
        self.selected = selected
        self.firstTab = False
        self.wingmanTab = False
        self.hovering = False # is the user hovering the mouse over the control
        self.clicking = False # is the user clicking the control
        self.middleClicking = False # is the user middle-clicking the control
        self.borderColor = TAB_BORDER_INNER_COLOR
        self.selBGColorStart = wx.Color(157, 185, 235)
        self.selBGColorEnd = wx.Color(157, 185, 235)

        wx.Panel.__init__(self, parent, wx.ID_ANY)

        self.preferredWidth = self._calculatePreferredWidth()

        self.SetFont(getDefaultFont())
        self.closeButtonBitmap = getApplicationModel().getResourceRegistry().getBitmap(u"images/widgets/tabcontainer/close.png") #$NON-NLS-1$
        self.closeHoverButtonBitmap = getApplicationModel().getResourceRegistry().getBitmap(u"images/widgets/tabcontainer/close.png") #$NON-NLS-1$

        self.SetSize(wx.Size(self.preferredWidth, -1))

        self.Bind(wx.EVT_PAINT, self.onPaint, self)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.onEraseBackground, self)
        self.Bind(wx.EVT_ENTER_WINDOW, self.onEnter, self)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.onLeave, self)
        self.Bind(wx.EVT_LEFT_DOWN, self.onLeftClickDown, self)
        self.Bind(wx.EVT_LEFT_UP, self.onLeftClickUp, self)
        self.Bind(wx.EVT_MIDDLE_DOWN, self.onMiddleClickDown, self)
        self.Bind(wx.EVT_MIDDLE_UP, self.onMiddleClickUp, self)
        self.Bind(wx.EVT_RIGHT_UP, self.onRightClick, self)

        # FIXME (EPW) show the tooltip string only if the title is truncated
        self.SetToolTipString(self.tabInfo.getTitle())
    # end __init__()

    def getTabBar(self):
        return self.parent
    # end getTabBar()

    def _calculatePreferredWidth(self):
        titleWidth = getTextDimensions(self.tabInfo.getTitle(), self)[0]
        if self.tabInfo.getBitmap() is not None:
            titleWidth += self.tabInfo.getBitmap().GetWidth() + 2
        return titleWidth + 4 + 4 + 16 + 4
    # end _calculatePreferredWidth()

    def setWingman(self, wingmanTab):
        self.wingmanTab = wingmanTab
    # end setWingman()

    def getPreferredWidth(self):
        return self.preferredWidth
    # end getPreferredWidth()

    def getTabInfo(self):
        return self.tabInfo
    # end getTabInfo()

    def getTabId(self):
        return self.GetId()
    # end getTabId()

    def isSelected(self):
        return self.selected
    # end isSeleted()

    def setSelected(self, selected):
        self.selected = selected
    # end setSelected()

    def setName(self, name):
        self.tabInfo.setTitle(name)
    # end setName()

    def onEraseBackground(self, event): #@UnusedVariable
        pass
    # end onEraseBackground()

    def onPaint(self, event):
        (w, h) = self.GetSizeTuple()
        (fontW, fontH) = self.GetTextExtent(self.tabInfo.getTitle()) #@UnusedVariable
        paintDC = wx.BufferedPaintDC(self)
        paintDC.SetBackground(wx.Brush(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DFACE), wx.SOLID))
        paintDC.Clear()

        pen = wx.Pen(self.borderColor)
        paintDC.SetPen(pen)

        if self.selected:
            paintDC.DrawLine(0, 6, 0, h) # left
            _drawTopLeftArc(paintDC, self.borderColor, TAB_BORDER_OUTER_COLOR, 0, 0) # top left
            _drawTopRightArc(paintDC, self.borderColor, TAB_BORDER_OUTER_COLOR, w - 6, 0) # top right
            paintDC.DrawLine(w - 1, 6, w - 1, h) # right
            paintDC.DrawLine(6, 0, w - 6, 0) # top
            self._drawTabBackground(paintDC)
        else:
            if not self.wingmanTab:
                paintDC.DrawLine(w - 1, 0, w - 1, h) # right line
            paintDC.DrawLine(0, h - 1, w, h - 1) # bottom line

        paintDC.SetFont(getDefaultFont())

        # Now draw the bitmap and title.
        labelX = 4
        bitmap = self.tabInfo.getBitmap()
        if bitmap is not None:
            paintDC.DrawBitmap(bitmap, 4, (h - bitmap.GetHeight()) / 2)
            labelX += bitmap.GetWidth() + 4
        labelW = w - labelX - 20
        title = sizeStringToFit(self.tabInfo.getTitle(), labelW, self)
        if self.selected:
            paintDC.SetTextForeground(wx.Color(255, 255, 255))
        elif self.hovering:
            paintDC.SetTextForeground(wx.Color(113, 114, 235))
        paintDC.DrawText(title, labelX, (h - fontH) / 2)

        del paintDC

        event.Skip()
    # end onPaint()

    def _drawTabBackground(self, paintDC):
        (w, h) = self.GetSizeTuple() #@UnusedVariable

        startY = 1
        for (color, maskPix) in TAB_GRADIENT_COLORS:
            pen = wx.Pen(color)
            paintDC.SetPen(pen)
            leftX = 0 + maskPix
            rightX = w - maskPix
            paintDC.DrawLine(leftX, startY, rightX, startY)
            del pen
            startY += 1
    # end _drawTabBackground()

    def onEnter(self, event): #@UnusedVariable
        self.hovering = True
        self.Layout()
        self.Refresh()
    # end onEnter()

    def onLeave(self, event): #@UnusedVariable
        self.hovering = False
        self.clicking = False
        self.middleClicking = False
        self.Layout()
        self.Refresh()
    # end onLeave()

    def onLeftClickDown(self, event): #@UnusedVariable
        self.clicking = True
        self.Refresh()
    # end onLeftClickDown()

    def onLeftClickUp(self, event): #@UnusedVariable
        if self.clicking:
            self._fireSelectedEvent()
        self.clicking = False
        self.Refresh()
    # end onLeftClickUp()

    def onMiddleClickDown(self, event): #@UnusedVariable
        self.middleClicking = True
        self.Refresh()
    # end onMiddleClickDown()

    def onMiddleClickUp(self, event): #@UnusedVariable
        if self.middleClicking:
            self._fireClosedEvent()
        self.middleClicking = False
        self.Refresh()
    # end onMiddleClickUp()

    def onRightClick(self, event):
        menu = ZTabContextMenu(self)
        self.PopupMenu(menu)
        event.Skip()
    # end onRightClick()

    def recalculateSize(self):
        self.preferredWidth = self._calculatePreferredWidth()
    # end recalculateSize()

    def _fireClosedEvent(self):
        event = ZTabClosedEvent(self.GetId(), self.getTabId())
        self.GetEventHandler().AddPendingEvent(event)
    # end _fireClosedEvent()

    def _fireSelectedEvent(self):
        if not self.selected:
            event = ZTabSelectedEvent(self.GetId(), self.getTabId())
            self.GetEventHandler().AddPendingEvent(event)
    # end _fireSelectedEvent()

# end ZTab


# ------------------------------------------------------------------------------
# The bar at the top of the tab container.  This tab bar contains the actual
# clickable tab items.
#
# Events:
#   ZEVT_TAB_CLOSED:  fired when the user closes the tab
#   ZEVT_TAB_SELECTED:  fired when the user selects a tab
# ------------------------------------------------------------------------------
class ZTabBar(wx.Panel):

    def __init__(self, parent):
        self.tabs = []
        self.selectedTab = None
        self.totalPreferredWidth = 0
        self.minimumTabWidth = 80
        self.maximumTabWidth = 300
        self.borderColor = TAB_BORDER_INNER_COLOR

        wx.Panel.__init__(self, parent, wx.ID_ANY)

        self._createWidgets()
        self._layoutWidgets()
        self._bindWidgetEvents()
    # end __init__()

    def getNumTabs(self):
        return len(self.tabs)
    # end getNumTabs()

    def _createWidgets(self):
        tabSelBitmap = getApplicationModel().getResourceRegistry().getBitmap(u"images/widgets/tabcontainer/tabselection.png") #$NON-NLS-1$
        tabSelHoverBitmap = getApplicationModel().getResourceRegistry().getBitmap(u"images/widgets/tabcontainer/tabselection_hover.png") #$NON-NLS-1$
        self.tabSelMenuButton = ZImageButton(self, tabSelBitmap, False, tabSelHoverBitmap, False)
    # end _createWidgets()

    def _layoutWidgets(self):
        self.SetSizeHints(-1, 25)

        self.barSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.tabSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.tabSizer.AddSpacer(10)
        self.barSizer.AddSizer(self.tabSizer, 1, wx.EXPAND | wx.RIGHT, 4)
        self.barSizer.Add(self.tabSelMenuButton, 0, wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)

        self.SetSizer(self.barSizer)
        self.SetAutoLayout(True)
        self.Layout()
    # end _layoutWidgets()

    def _bindWidgetEvents(self):
        self.Bind(wx.EVT_PAINT, self.onPaint, self)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.onEraseBackground, self)
        self.Bind(wx.EVT_BUTTON, self.onSelectionMenuButton, self.tabSelMenuButton)
        self.Bind(wx.EVT_SIZE, self.onResize, self)
    # end _bindWidgetEvents()

    def addTab(self, tabInfo):
        u"""addTab(IZTabInfo) -> string
        Adds a tab to the tab bar, returns the ID of the new
        tab.""" #$NON-NLS-1$
        tab = ZTab(self, tabInfo, False)
        self.tabSizer.Add(tab, 0, wx.EXPAND)
        self.tabs.append(tab)
        self.totalPreferredWidth += self._getPreferredTabWidth(tab.getPreferredWidth())
        self.Bind(ZEVT_TAB_CLOSED, self.onTabClosed, tab)
        self.Bind(ZEVT_TAB_SELECTED, self.onTabSelected, tab)
        self.refresh()
        return tab.getTabId()
    # end addTab()

    def removeTab(self, tabId):
        u"""removeTab(int) -> None
        Removes the tab with the given tab ID from the
        tab bar.""" #$NON-NLS-1$
        tab = self._getTabById(tabId)
        if tab is None:
            raise ZAppFrameworkException(u"No tab with id '%s' found." % unicode(tabId)) #$NON-NLS-1$
        self.totalPreferredWidth -= self._getPreferredTabWidth(tab.getPreferredWidth())
        self.Unbind(ZEVT_TAB_CLOSED, tab)
        self.Unbind(ZEVT_TAB_SELECTED, tab)
        self._removeTab(tabId)
        self.tabSizer.Remove(tab)
        tab.Destroy()
        if tab == self.selectedTab:
            self.selectedTab = None
        self.refresh()
    # end removeTab()

    def selectTab(self, tabId):
        tab = self._getTabById(tabId)
        if tab is None:
            raise ZAppFrameworkException(u"No tab with id '%s' found." % unicode(tabId)) #$NON-NLS-1$
        if self.selectedTab is not None:
            self.selectedTab.setSelected(False)
        tab.setSelected(True)
        self.selectedTab = tab
        self.refresh()
    # end selectTab()
    
    def setTabName(self, tabId, name):
        tab = self._getTabById(tabId)
        tab.setName(name)
        tab.recalculateSize()
    # end setTabName()

    def _getTabById(self, tabId):
        for tab in self.tabs:
            if tab.getTabId() == tabId:
                return tab
        return None
    # end _getTabById()

    def _removeTab(self, tabId):
        for tab in self.tabs:
            if tab.getTabId() == tabId:
                self.tabs.remove(tab)
                return True
        return False
    # end _removeTab()

    def onEraseBackground(self, event): #@UnusedVariable
        pass
    # end onEraseBackground()

    def onPaint(self, event):
        (w, h) = self.GetSizeTuple()
        paintDC = wx.BufferedPaintDC(self)
        paintDC.SetBackground(wx.Brush(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DFACE), wx.SOLID))
        paintDC.Clear()

        pen = wx.Pen(self.borderColor)
        brush = wx.TRANSPARENT_BRUSH

        paintDC.SetPen(pen)
        paintDC.SetBrush(brush)

        paintDC.DrawLine(0, h - 1, w - 1, h - 1)

        del paintDC

        event.Skip()
    # end onPaint()

    def onTabClosed(self, event):
        self._fireClosedEvent(self._getTabById(event.getTabId()))
        event.Skip()
    # end onTabClosed()

    def onTabSelected(self, event):
        self._fireSelectedEvent(self._getTabById(event.getTabId()))
        event.Skip()
    # end onTabSelected()

    def onSelectionMenuButton(self, event):
        popup = ZTabSelectionPopupWindow(self, self.tabs)

        button = self.tabSelMenuButton
        pos = button.ClientToScreen( (0,0) )
        buttonSize =  button.GetSize()
        popup.Position(pos, (0, buttonSize[1]))

        popup.Popup()
        event.Skip()
    # end onSelectionMenuButton()

    def onResize(self, event):
        self.refresh()
        event.Skip()
    # end onResize()
    
    def refresh(self):
        self._resizeTabs()
        self.Refresh()
        self.Layout()
    # end refresh()

    def _resizeTabs(self):
        availableWidth = self._getAvailableTabWidth()
        if availableWidth < 0:
            return

        # if we have enough room for all tabs, then use the preferred size
        # for each tab
        if self.totalPreferredWidth <= availableWidth:
            self.tabSelMenuButton.Show(False)
            for tab in self.tabs:
                tabWidth = self._getPreferredTabWidth(tab.getPreferredWidth())
                tab.SetSize(wx.Size(tabWidth, -1))
                tab.SetSizeHints(tabWidth, -1, tabWidth, -1)
                tab.Show(True)
                tab.setWingman(False)
            if len(self.tabs) > 0:
                self._determineWingman()
            return

        self.tabSelMenuButton.Show(True)
        # else, run the tab resizing algorithm:
        # 1) assign a width percentage to all tabs
        # 2) resize all tabs so that they conform to their percentage
        #    of the available space (but tabs do not go smaller than the
        #    minimum tab size)
        # 3) if total tab width is still greater than available space, then
        #    hide some tabs (never hide the selected tab)

        # Do (1) and (2) now.
        totalActualTabWidth = 0
        for tab in self.tabs:
            tab.Show(True)
            tab.setWingman(False)
            tabPreferredWidth = self._getPreferredTabWidth(tab.getPreferredWidth())
            tabWidthPerc = float(tabPreferredWidth) / float(self.totalPreferredWidth)
            tabWidth = int(float(availableWidth) * tabWidthPerc)
            tabWidth = min(tabPreferredWidth, tabWidth)
            tabWidth = max(tabWidth, self.minimumTabWidth)
            tab.SetSize(wx.Size(tabWidth, -1))
            tab.SetSizeHints(tabWidth, -1, tabWidth, -1)
            totalActualTabWidth += tabWidth

        # Do (3) above now.
        if totalActualTabWidth > availableWidth:
            for idx in range(len(self.tabs) - 1, 0, -1):
                tab = self.tabs[idx]
                if not tab.isSelected():
                    tab.Show(False)
                    totalActualTabWidth -= tab.GetSize()[0]
                    if totalActualTabWidth <= availableWidth:
                        break

        self._determineWingman()
        self.tabSizer.Layout()
    # end _resizeTabs()

    def _determineWingman(self):
        prevTab = None
        for tab in self.tabs:
            if tab.isSelected():
                break
            if tab.IsShown():
                prevTab = tab
        if prevTab is not None:
            prevTab.setWingman(True)
    # end _determineWingman()

    def _getPreferredTabWidth(self, width):
        return min(width, self.maximumTabWidth)
    # end _getPreferredTabWidth()

    def _getAvailableTabWidth(self):
        return self.GetSizeTuple()[0] - self.tabSelMenuButton.GetSizeTuple()[0] - 10
    # end _getAvailableTabWidth()

    def _getTabs(self):
        return self.tabs
    # end _getTabs()

    def _fireClosedEvent(self, tab):
        event = ZTabClosedEvent(self.GetId(), tab.getTabId())
        self.GetEventHandler().AddPendingEvent(event)
    # end _fireClosedEvent()

    def _fireSelectedEvent(self, tab):
        event = ZTabSelectedEvent(self.GetId(), tab.getTabId())
        self.GetEventHandler().AddPendingEvent(event)
    # end _fireSelectedEvent()

# end ZTabBar


# ------------------------------------------------------------------------------
# A listener inteface for the tab container.
# ------------------------------------------------------------------------------
class IZTabContainerListener:

    def onTabClosing(self, tabId):
        u"""onTabClosing(int) -> boolean
        Called when the container is about to close a tab.
        Returns True if the listener is veto'ing the
        closing of the tab.""" #$NON-NLS-1$
    # end onTabClosing()

    def onTabClosed(self, tabId):
        u"""onTabClosed(int) -> None
        Called when the container closes a tab.""" #$NON-NLS-1$
    # end onTabClosed()

    def onTabSelectionChanging(self, fromTabId, toTabId):
        u"""onTabSelectionChanging(int, int) -> boolean
        Called when the container is about to change which
        tab is selected.  Returns True if the listener is
        veto'ing the selection of the tab.""" #$NON-NLS-1$
    # end onTabSelectionChanging()

    def onTabSelectionChanged(self, fromTabId, toTabId):
        u"""onTabSelectionChanged(int, int) -> None
        Called when the container changes from one tab
        to another tab.""" #$NON-NLS-1$
    # end onTabSelectionChanged()

# end IZTabContainerListener


# ------------------------------------------------------------------------------
# A default tab container listener implementation.
# ------------------------------------------------------------------------------
class ZDefaultTabContainerListener(IZTabContainerListener):

    def onTabClosing(self, tabId): #@UnusedVariable
        return False
    # end onTabClosing()

    def onTabSelectionChanging(self, fromTabId, toTabId): #@UnusedVariable
        return False
    # end onTabSelectionChanging()

# end ZDefaultTabContainerListener


# ------------------------------------------------------------------------------
# A widget that implements a tab container, much like a notebook.  The tab
# container is a fully custom implementation, however.
#
# FIXME (EPW) fire events, instead of IZTabContainerListener  container should fire events, internal widgets used by the container should have callbacks - see ZToolBook
# ------------------------------------------------------------------------------
class ZTabContainer(wx.Panel):

    def __init__(self, parent, listener = None):
        self.listener = listener
        if self.listener is None:
            self.listener = ZDefaultTabContainerListener()
        self.tabPanelMap = {}
        self.selectedTabId = None
        self.intBorderColor = TAB_CONTAINER_INNER_BORDER_COLOR
        self.borderColor = TAB_BORDER_INNER_COLOR

        wx.Panel.__init__(self, parent, wx.ID_ANY)

        self._createWidgets()
        self._layoutWidgets()
        self._bindWidgetEvents()
    # end __init__()

    def setListener(self, listener):
        self.listener = listener
    # end setListener()

    def _createWidgets(self):
        self.tabBar = ZTabBar(self)
    # end _createWidgets()

    def _layoutWidgets(self):
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.tabBar, 0, wx.EXPAND)
        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)
        self.Layout()
    # end _layoutWidgets()

    def _bindWidgetEvents(self):
        self.Bind(wx.EVT_SIZE, self.onResize, self)
        self.Bind(ZEVT_TAB_CLOSED, self.onTabClosed, self.tabBar)
        self.Bind(ZEVT_TAB_SELECTED, self.onTabSelected, self.tabBar)
        self.Bind(ZEVT_TAB_CLOSED, self.onTabClosedSelf, self)
        self.Bind(ZEVT_TAB_SELECTED, self.onTabSelectedSelf, self)
    # end _bindWidgetEvents()

    def Layout(self):
        self.tabBar.Show(self.hasMultipleTabs())
        wx.Panel.Layout(self)
    # end Layout()

    def hasMultipleTabs(self):
        return self.tabBar.getNumTabs() > 1
    # end hasMultipleTabs()

    def addTab(self, tabInfo, tabPanel):
        u"""addTab(IZTabInfo, wx.Panel) -> None
        Called to add a tab to the tab container.""" #$NON-NLS-1$
        tabId = self.tabBar.addTab(tabInfo)
        self.tabPanelMap[tabId] = tabPanel
        self.sizer.Add(tabPanel, 1, wx.EXPAND | wx.ALL, 0)
        tabPanel.Show(False)
        self.Layout()
        self.Refresh()
        return tabId
    # end addTab()

    def selectTab(self, tabId):
        self._fireSelectedEvent(tabId)
    # end selectTab()

    def _selectTab(self, tabId):
        if not tabId in self.tabPanelMap:
            raise ZAppFrameworkException(u"Tab with id '%s' does not exist." % unicode(tabId)) #$NON-NLS-1$
        self.tabBar.selectTab(tabId)
        tabPanel = self.tabPanelMap[tabId]
        if self.selectedTabId is not None:
            oldTabPanel = self.tabPanelMap[self.selectedTabId]
            oldTabPanel.Show(False)
        self.selectedTabId = tabId
        tabPanel.Show(True)
        self.Layout()
        self.Refresh()
    # end selectTab()

    def removeTab(self, tabId):
        self._fireClosedEvent(tabId)
    # end removeTab(tabId)

    def _removeTab(self, tabId):
        if not tabId in self.tabPanelMap:
            raise ZAppFrameworkException(u"Tab with id '%s' does not exist." % unicode(tabId)) #$NON-NLS-1$
        tabPanel = self.tabPanelMap[tabId]
        del self.tabPanelMap[tabId]
        self.sizer.Remove(tabPanel)
        tabPanel.Destroy()
        self.tabBar.removeTab(tabId)
        # If the one being removed was the selected tab, then select a
        # new ('scuse me) tab
        if self.selectedTabId == tabId:
            self.selectedTabId = self._getFirstTabId()
            if self.selectedTabId is not None:
                self.selectTab(self.selectedTabId)
    # end removeTab()

    def setTabName(self, tabId, name):
        self.tabBar.setTabName(tabId, name)
        self.tabBar.refresh()
    # end setTabName()

    def getSelectedTabId(self):
        return self.selectedTabId
    # end getSelectedTabId()

    def _getFirstTabId(self):
        for tabId in self.tabPanelMap:
            return tabId
        return None
    # end _getFirstTabId()

    def drawWithTabBar(self, paintDC, w, h):
        borderY = self.tabBar.GetSizeTuple()[1]
        self.drawBorder(paintDC, w, h, borderY)
    # end drawWithTabBar()

    def drawWithNoTabBar(self, paintDC, w, h):
        self.drawBorder(paintDC, w, h, 0, True)
    # end drawWithNoTabBar()

    def drawBorder(self, paintDC, w, h, borderY, drawOuterTop = False):
        pen = wx.Pen(self.borderColor, 1)
        brush = wx.TRANSPARENT_BRUSH
        paintDC.SetBrush(brush)
        topAdjust = 0

        # Draw the outer border (1 pixel border)
        paintDC.SetPen(pen)
        if drawOuterTop:
            paintDC.DrawLine(0, borderY, w, borderY) # top
            topAdjust = 1
        paintDC.DrawLine(0, h - 1, w, h - 1) # bottom
        paintDC.DrawLine(0, borderY, 0, h) # left
        paintDC.DrawLine(w - 1, borderY, w - 1, h) # right

        # Draw the inner border (2 pixel border)
        pen = wx.Pen(self.intBorderColor, 1)
        paintDC.SetPen(pen)
        # top
        paintDC.DrawLine(1, borderY + topAdjust, w - 1, borderY + topAdjust)
        paintDC.DrawLine(1, borderY + 1 + topAdjust, w - 1, borderY + 1 + topAdjust)
        # bottom
        paintDC.DrawLine(1, h - 3, w - 1, h - 3)
        paintDC.DrawLine(1, h - 2, w - 1, h - 2)
        # left
        paintDC.DrawLine(1, borderY + topAdjust, 1, h - 1)
        paintDC.DrawLine(2, borderY + topAdjust, 2, h - 1)
        # right
        paintDC.DrawLine(w - 3, borderY + topAdjust, w - 3, h - 1)
        paintDC.DrawLine(w - 2, borderY + topAdjust, w - 2, h - 1)
    # end drawWithTabBar()

    def onResize(self, event):
        self.Layout()
        self.Refresh()
        event.Skip()
    # end onResize()

    def onTabClosedSelf(self, event):
        self._removeTab(event.getTabId())
        self.listener.onTabClosed(event.getTabId())
        event.Skip()
    # end onTabClosedSelf()

    def onTabSelectedSelf(self, event):
        # Note: this check is needed due to the order in which events
        # will come in if the user chooses the "Close All" menu option
        # when right-clicking on a tab.  In that case, it is possible
        # that a selection event will come in after all of the close
        # events have been processed (and thus all of the tabs are gone)
        if event.getTabId() in self.tabPanelMap:
            oldTabId = self.selectedTabId
            self._selectTab(event.getTabId())
            self.listener.onTabSelectionChanged(oldTabId, event.getTabId())
        event.Skip()
    # end onTabSelectedSelf()

    def onTabClosed(self, event):
        if not self.listener.onTabClosing(event.getTabId()):
            self._fireClosedEvent(event.getTabId())
        event.Skip()
    # end onTabClosed()

    def onTabSelected(self, event):
        if not self.listener.onTabSelectionChanging(self.selectedTabId, event.getTabId()):
            self._fireSelectedEvent(event.getTabId())
        event.Skip()
    # end onTabSelected()

    def _fireClosedEvent(self, tabId):
        event = ZTabClosedEvent(self.GetId(), tabId)
        self.GetEventHandler().AddPendingEvent(event)
    # end _fireClosedEvent()

    def _fireSelectedEvent(self, tabId):
        event = ZTabSelectedEvent(self.GetId(), tabId)
        self.GetEventHandler().AddPendingEvent(event)
    # end _fireSelectedEvent()

# end ZTabContainer
