from wx._core import wxEVT_COMMAND_BUTTON_CLICKED
from zoundry.appframework.exceptions import ZAppFrameworkException
from zoundry.appframework.ui.events.propertybook import ZEVT_PB_TAB_SELECTION
from zoundry.appframework.ui.events.propertybook import ZPropertyBookTabSelectionEvent
from zoundry.appframework.ui.util.colorutil import getDefaultControlBackgroundColor
from zoundry.appframework.ui.util.colorutil import getDefaultControlBorderColor
from zoundry.appframework.ui.util.colorutil import getDefaultDialogBackgroundColor
from zoundry.appframework.ui.util.fontutil import getDefaultFont
import wx


# -------------------------------------------------------------------------------------------
# An individual clickable tab in the property book control.
# -------------------------------------------------------------------------------------------
class ZPropertyBookTab(wx.Control):

    def __init__(self, parent, tabName):
        self.tabName = tabName
        self.first = False
        self.active = False
        self.hovering = False # is the user hovering the mouse over the control
        self.clicking = False # is the user clicking the control
        self.font = getDefaultFont()
        # FIXME (EPW) make these colors settable
        self.borderColor = getDefaultControlBorderColor()
        self.tabColor = getDefaultDialogBackgroundColor()
        self.activeColor = getDefaultControlBackgroundColor()
        self.hoverColor = wx.Color(min(self.tabColor.Red() + 20, 255), min(self.tabColor.Green() + 20, 255), min(self.tabColor.Blue(), 255))
        
        wx.Control.__init__(self, parent, wx.ID_ANY, style = wx.NO_BORDER)
        
        self.Bind(wx.EVT_PAINT, self.onPaint, self)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.onEraseBackground, self)
        self.Bind(wx.EVT_ENTER_WINDOW, self.onEnter, self)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.onLeave, self)
        self.Bind(wx.EVT_LEFT_DOWN, self.onLeftClickDown, self)
        self.Bind(wx.EVT_LEFT_UP, self.onLeftClickUp, self)
        
        # FIXME allow the font to be changed - when that is done, size hints must be recalc'd
        winDC = wx.WindowDC(parent)
        winDC.SetFont(self.font)
        (w, h) = winDC.GetTextExtent(tabName)
        self.SetSizeHints(w + 10, h + 10)
        del winDC
    # end __init__()
    
    def setActiveColor(self, color):
        self.activeColor = color
    # end setActiveColor()
    
    def setTabColor(self, color):
        self.tabColor = color
    # end setTabColor()

    def setHoverColor(self, color):
        self.hoverColor = color
    # end setHoverColor()
    
    def setFirst(self, first = True):
        self.first = first
    # end setFirst()
    
    def setActive(self, active = True):
        if self.active != active:
            self.active = active
            self.Refresh()
    # end setActive()

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
            self._fireTabSelectionEvent()
        self.clicking = False
        self.Refresh()
    # end onLeftClickUp()

    def _fireTabSelectionEvent(self):
        event = wx.CommandEvent(wxEVT_COMMAND_BUTTON_CLICKED, self.GetId())
        self.GetEventHandler().AddPendingEvent(event)
    # end _fireTabSelectionEvent()
    
    def onEraseBackground(self, event): #@UnusedVariable
        pass
    # end onEraseBackground()

    def onPaint(self, event):
        (width, height) = self.GetSizeTuple()
        paintDC = wx.BufferedPaintDC(self)
        paintDC.SetBackground(wx.Brush(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DFACE), wx.SOLID))
        paintDC.Clear()

        brush = wx.TRANSPARENT_BRUSH
        if self.active:
            brush = wx.Brush(self.activeColor)
        elif self.hovering:
            brush = wx.Brush(self.hoverColor)
        else:
            brush = wx.Brush(self.tabColor)

        paintDC.SetPen(wx.TRANSPARENT_PEN)
        paintDC.SetBrush(brush)
        paintDC.SetFont(self.font)

        paintDC.DrawRectangle(0, 0, width, height)
        paintDC.DrawText(self.tabName, 5, 5)
        
        paintDC.SetPen(wx.Pen(self.borderColor))
        rightX = width - 1
        bottomY = height - 1
        if self.first:
            paintDC.DrawLine(1, 0, rightX, 0)
        if self.active and self.first:
            paintDC.DrawLine(0, 1, 0, bottomY)
        elif self.active:
            paintDC.DrawLine(0, 0, 0, bottomY)
        else:
            paintDC.DrawLine(rightX, 0, rightX, bottomY)
        paintDC.DrawLine(1, bottomY, rightX, bottomY)
        
        del paintDC
        event.Skip()
    # end onPaint()

# end ZPropertyBookTab


# -------------------------------------------------------------------------------------------
# A container panel that contains the property book's tabs.
# -------------------------------------------------------------------------------------------
class ZPropertyBookTabContainer(wx.Panel):
    
    def __init__(self, parent, alignment, bgColor, borderColor):
        self.alignment = alignment
        self.tabs = {}
        self.borderColor = borderColor
        self.tabColor = None
        self.tabActiveColor = None
        self.tabHoverColor = None

        wx.Panel.__init__(self, parent, wx.ID_ANY)
        
        self.SetBackgroundColour(bgColor)
        
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add( (10, 10) )
        
        self.Bind(wx.EVT_PAINT, self.onPaint, self)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.onEraseBackground, self)

        self.SetAutoLayout(True)
        self.SetSizer(self.sizer)
        self.Layout()
    # end __init__()
    
    def setBorderColor(self, color):
        self.borderColor = color
    # end setBorderColor()
    
    def setBackgroundColor(self, color):
        self.SetBackgroundColour(color)
    # end setBackgroundColor()
    
    def setTabColor(self, color):
        self.tabColor = color
    # end setTabColor()
    
    def setTabActiveColor(self, color):
        self.tabActiveColor = color
    # end setTabActiveColor()
    
    def setTabHoverColor(self, color):
        self.tabHoverColor = color
    # end setTabActiveColor()
    
    def addTab(self, tabName, activeTab = False):
        tabWidget = self._createTabWidget(tabName)
        self.sizer.Add(tabWidget, 0, wx.EXPAND)
        self.tabs[tabName] = tabWidget
        if activeTab:
            self._setActiveTab(tabName)
        self.Bind(wx.EVT_BUTTON, self.onTabClicked, tabWidget)
        self.Layout()
    # end addTab()
    
    def _createTabWidget(self, tabName):
        tab = ZPropertyBookTab(self, tabName)
        if self.tabColor:
            tab.setTabColor(self.tabColor)
        if self.tabActiveColor:
            tab.setActiveColor(self.tabActiveColor)
        if self.tabHoverColor:
            tab.setHoverColor(self.tabHoverColor)
        if len(self.tabs) == 0:
            tab.setFirst(True)
        return tab
    # end _createTabWidget()

    def _setActiveTab(self, tabName):
        for tname in self.tabs:
            tab = self.tabs[tname]
            tab.setActive(tname == tabName)
    # end _setActiveTab()
    
    def _getTabNameById(self, id):
        for tname in self.tabs:
            tab = self.tabs[tname]
            if tab.GetId() == id:
                return tname
        return None
    # end _getTabNameById()
    
    def onTabClicked(self, event):
        tabName = self._getTabNameById(event.GetId())
        self._setActiveTab(tabName)
        event = ZPropertyBookTabSelectionEvent(self.GetId(), tabName)
        self.GetEventHandler().AddPendingEvent(event)
        event.Skip()
    # end onTabClicked()
    
    def onEraseBackground(self, event): #@UnusedVariable
        pass
    # end onEraseBackground()

    def onPaint(self, event):
        (width, height) = self.GetSizeTuple()
        paintDC = wx.BufferedPaintDC(self)
        paintDC.SetBackground(wx.Brush(self.GetBackgroundColour(), wx.SOLID))
        paintDC.Clear()
        
        pen = wx.Pen(self.borderColor)
        paintDC.SetPen(pen)

        paintDC.DrawLine(width - 1, 0, width - 1, height)
        
        del paintDC
        event.Skip()
    # end onPaint()

# end ZPropertyBookTabContainer


# -------------------------------------------------------------------------------------------
# This is a Property Book widget.  This widget is much like a Notebook, but with a cleaner
# visual style.  In addition, tabs in the property book can only be on the left or the right.
# -------------------------------------------------------------------------------------------
class ZPropertyBook(wx.Panel):

    def __init__(self, parent, alignment = wx.ALIGN_LEFT, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.DefaultSize, style = 0, name = u"ZPropertyBook"): #$NON-NLS-1$
        self.tabs = {}
        self.tabAreaBGColor = getDefaultDialogBackgroundColor()
        self.bgColor = getDefaultControlBackgroundColor()
        self.borderColor = getDefaultControlBorderColor()

        wx.Panel.__init__(self, parent, wx.ID_ANY, pos, size, style, name)
        
        self.SetBackgroundColour(self.bgColor)
        
        # Create a tab container, sizer to store the panels, and the overall property book sizer
        self.tabContainer = ZPropertyBookTabContainer(self, alignment, self.tabAreaBGColor, self.borderColor)
        self.tabPanelSizer = wx.BoxSizer(wx.VERTICAL)
        self.bookSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.bookSizer.Add(self.tabContainer, 0, wx.EXPAND)
        self.bookSizer.AddSizer(self.tabPanelSizer, 1, wx.EXPAND | wx.ALL, 3)
        
        self.Bind(ZEVT_PB_TAB_SELECTION, self.onTabSelection, self.tabContainer)
        self.Bind(wx.EVT_PAINT, self.onPaint, self)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.onEraseBackground, self)
        self.Bind(wx.EVT_SIZE, self.onResize, self)
        
        self.SetAutoLayout(True)
        self.SetSizer(self.bookSizer)
        self.Layout()
    # end __init__()
    
    def setBorderColor(self, color):
        self.borderColor = color
        self.tabContainer.setBorderColor(color)
    # end setBorderColor()
    
    def setBackgroundColor(self, color):
        self.bgColor = color
        wx.Panel.SetBackgroundColour(self, color)
    # end setBackgroundColor()
    
    def setTabAreaBackgroundColor(self, color):
        self.tabAreaBGColor = color
        self.tabContainer.setBackgroundColor(color)
    # end setTabAreaBackgroundColor()
    
    def setTabActiveColor(self, color):
        self.tabContainer.setTabActiveColor(color);
    # end setTabActiveColor()
    
    def setTabHoverColor(self, color):
        self.tabContainer.setTabHoverColor(color)
    # end setTabHoverColor()
    
    def setTabColor(self, color):
        self.tabContainer.setTabColor(color)
    # end setTabColor()
    
    def addTab(self, tabName, tabPanel):
        if tabName in self.tabs:
            raise ZAppFrameworkException(u"A tab named '%s' already exists." % tabName) #$NON-NLS-1$
        if not tabPanel.GetParent() == self:
            raise ZAppFrameworkException(u"The panel's parent must be the Property Book.") #$NON-NLS-1$
        
        firstTab = False
        if len(self.tabs) == 0:
            firstTab = True
        
        self.tabContainer.addTab(tabName, firstTab)
        self.tabPanelSizer.Add(tabPanel, 1, wx.EXPAND)
        self.tabs[tabName] = tabPanel
        
        if not firstTab:
            tabPanel.Show(False)
        
        self.Layout()
    # end addTab()
    
    def _setActiveTab(self, tabName):
        for tname in self.tabs:
            tpanel = self.tabs[tname]
            tpanel.Show(tname == tabName)
    # end _setActiveTab()
    
    def onTabSelection(self, event):
        self._setActiveTab(event.getTabName())
        self.Layout()
        event.Skip()
    # end onTabSelection()
    
    def onResize(self, event):
        self.Refresh()
        event.Skip()
    # end onResize()
    
    def onEraseBackground(self, event): #@UnusedVariable
        pass
    # end onEraseBackground()

    def onPaint(self, event):
        (width, height) = self.GetSizeTuple()
        (tcWidth, tcHeight) = self.tabContainer.GetSizeTuple() #@UnusedVariable
        paintDC = wx.BufferedPaintDC(self)
        paintDC.SetBackground(wx.Brush(self.GetBackgroundColour(), wx.SOLID))
        paintDC.Clear()
        
        pen = wx.Pen(self.borderColor)
        paintDC.SetPen(pen)

        paintDC.DrawLine(tcWidth, 0, width - 1, 0)
        paintDC.DrawLine(width - 1, 0, width - 1, height)
        paintDC.DrawLine(tcWidth, height - 1, width - 1, height - 1)
        
        del paintDC
        event.Skip()
    # end onPaint()
    
# end ZPropertyBook
