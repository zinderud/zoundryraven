from zoundry.appframework.exceptions import ZAppFrameworkException
from zoundry.appframework.ui.util.colorutil import getDefaultControlBackgroundColor
from zoundry.appframework.ui.util.colorutil import getDefaultControlBorderColor
import wx

# ----------------------------------------------------------------------------------------
# An interface that all panels in the panel list box must implement.
# FIXME (EPW) do something with this (panel list box items should be clickable)
# ----------------------------------------------------------------------------------------
class IZPanelListBoxPanel:

    def onSelected(self):
        u"Called when the user clicks on the panel." #$NON-NLS-1$
    # end onSelected()

    def onDeselected(self):
        u"Called when the user moves away from the panel to another one." #$NON-NLS-1$
    # end onDeselected()

# end IZPanelListBoxPanel


# ----------------------------------------------------------------------------------------
# The interface for the content provider for the panel list box.
# ----------------------------------------------------------------------------------------
class IZPanelListProvider:

    def getNumRows(self):
        u"Should return the number of rows the list should have (defaults to 0 if not implemented)." #$NON-NLS-1$
        return 0
    # end getNumRows()

    def getRowItem(self, rowIndex):
        u"Should return the object associated with the given row index." #$NON-NLS-1$
    # end getRowItem()

    def createItemPanel(self, parent, rowItem):
        u"Called to create a wx.Panel for the given rowItem." #$NON-NLS-1$
    # end createItemPanel()

# end IZPanelListProvider


# ----------------------------------------------------------------------------------------
# Internal representation of the panel list box.  This is needed so that the panel list
# box's border can be properly drawn (around the scroll bar).
# ----------------------------------------------------------------------------------------
class ZPanelListBoxInternal(wx.ScrolledWindow):

    def __init__(self, provider, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.HSCROLL | wx.VSCROLL, name=  u"ZPanelListBoxInternal"): #$NON-NLS-1$
        self.provider = provider

        style = style | wx.NO_BORDER
        wx.ScrolledWindow.__init__(self, parent, id, pos, size, style, name)

        self.numRows = self.provider.getNumRows()
        self.data = []

        self._createPanels()
        self._layoutPanels()
        self._bindWidgetEvents()

        # FIXME need a better default here
        self.SetScrollRate(0, 10)
    # end __init__()

    def _createPanels(self):
        for i in range(0, self.numRows):
            item = self.provider.getRowItem(i)
            panel = self.provider.createItemPanel(self, item)
            self.data.append( (item, panel) )
    # end _createPanels()

    def _layoutPanels(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        for (item, panel) in self.data: #@UnusedVariable
            sizer.Add(panel, 0, wx.EXPAND | wx.ALL, 1)

        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        self.Layout()
    # end _layoutPanels()

    def _bindWidgetEvents(self):
        # FIXME in order to select an item in the list, need to push a custom event handler onto every child widget
        self.Bind(wx.EVT_LEFT_DOWN, self.onLDown)
    # end _bindWidgetEvents()

    def onLDown(self, event):
        event.Skip()
    # end onLDown()

    def Refresh(self):
        self._syncPanelList()
        wx.ScrolledWindow.Refresh(self)
        self.Layout()
    # end Refresh()

    def Layout(self):
        wx.ScrolledWindow.Layout(self)
        size = self.GetBestVirtualSize();
        self.SetVirtualSize(size);
        
        # Make sure all of the panels are the right width, regardless of what *they* want.
        for (item, panel) in self.data: #@UnusedVariable
            size = panel.GetSize()
            width = self.GetSizeTuple()[0]
            height = size.GetHeight()
            panel.SetSize(wx.Size(width, height))
    # end Layout()

    def _syncPanelList(self):
        lastIndex = 0
        for i in range(0, self.provider.getNumRows()):
            newItem = self.provider.getRowItem(i)
            if i >= len(self.data):
                self._insertItem(i, newItem)
            else:
                (oldItem, oldPanel) = self.data[i] #@UnusedVariable
                if not oldItem == newItem:
                    self._syncPanelItem(i, newItem)
            lastIndex = i + 1
        # Now delete any trailing items
        if lastIndex < len(self.data):
            self._deleteItems(lastIndex, len(self.data))
        self.numRows = self.provider.getNumRows()
        if len(self.data) != self.numRows:
            raise ZAppFrameworkException(u"Sync'd list (%d) != provider's numRows (%d)" % (len(self.data), self.numRows)) #$NON-NLS-1$
    # end _syncPanelList()

    def _syncPanelItem(self, index, newItem):
        if self._isNewItem(newItem):
            self._insertItem(index, newItem)
        else:
            self._deleteItems(index, self._findItemIndex(newItem))
    # end _syncPanelItem()

    # Returns True if the item does not already exist in the data list.
    def _isNewItem(self, item):
        for (dataItem, dataPanel) in self.data: #@UnusedVariable
            if dataItem == item:
                return False
        return True
    # end _isNewItem()

    # Returns the index of the given item.
    def _findItemIndex(self, item):
        for i in range(0, len(self.data)):
            (dataItem, dataPanel) = self.data[i] #@UnusedVariable
            if dataItem == item:
                return i
        return -1
    # end _findItemIndex()

    # Inserts the item at the given index.
    def _insertItem(self, index, newItem):
        panel = self.provider.createItemPanel(self, newItem)
        self.data.insert( index, (newItem, panel) )
        sizer = self.GetSizer()
        sizer.Insert(index, panel, 0, wx.EXPAND | wx.ALL, 1)
    # end _insertItem()

    # Deletes all items between 'startIndex' (inclusive) and 'endIndex' (exclusive)
    def _deleteItems(self, startIndex, endIndex):
        indexes = range(startIndex, endIndex)
        indexes.reverse()
        for i in indexes:
            (item, panel) = self.data[i] #@UnusedVariable
            sizer = self.GetSizer()
            sizer.Detach(panel)
            # Bug in wx?  If I Destroy the panel, the app crashes - so instead, I just detach and Hide it.  Note
            # there will be no way to Show it again, but I don't want to anyway.
            panel.Show(False)
            del self.data[i]
    # end _deleteItems()

    def getPanelData(self):
        return self.data
    # end getPanelData()

# end ZPanelListBoxInternal


# ----------------------------------------------------------------------------------------
# A base class for a custom panel-based list box.  The idea here is that this control is a
# list box that is comprised of a list of panels.  The control itself delegates much of
# the functionality to the associated list box provider.
# ----------------------------------------------------------------------------------------
class ZPanelListBox(wx.Panel):

    def __init__(self, provider, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.HSCROLL | wx.VSCROLL, name = u"ZPanelListBox"): #$NON-NLS-1$
        self.provider = provider
        self.backgroundColor = getDefaultControlBackgroundColor()
        self.borderColor = getDefaultControlBorderColor()
        self.style = style

        style = wx.NO_BORDER
        wx.Panel.__init__(self, parent, id, pos, size, style, name)

        self._createInternalRepresentation()
        self._layoutInternalRepresentation()

        self.SetBackgroundColor(self.backgroundColor)

        self.Bind(wx.EVT_PAINT, self.onPaint, self)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.onEraseBackground, self)
    # end __init__()

    def SetBackgroundColor(self, color):
        self.backgroundColor = color
        wx.Panel.SetBackgroundColour(self, color)
        self.internalRepresentation.SetBackgroundColour(color)
    # end SetBackgroundColor()

    def SetBorderColor(self, color):
        self.borderColor = color
    # end SetBorderColor()

    def _createInternalRepresentation(self):
        self.internalRepresentation = ZPanelListBoxInternal(self.provider, self, style = self.style | wx.NO_BORDER)
    # end _createPanels()

    def _layoutInternalRepresentation(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.internalRepresentation, 1, wx.EXPAND | wx.ALL, 1)

        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        self.Layout()
    # end _layoutPanels()
    
    def onEraseBackground(self, event): #@UnusedVariable
        pass
    # end onEraseBackground()

    def onPaint(self, event):
        (width, height) = self.GetSizeTuple()
        paintDC = wx.BufferedPaintDC(self)
        paintDC.SetBackground(wx.Brush(self.backgroundColor, wx.SOLID))
        paintDC.Clear()

        # Draw the background and border
        brush = wx.Brush(self.backgroundColor)
        paintDC.SetPen(wx.Pen(self.borderColor, 1, wx.SOLID))
        paintDC.SetBrush(brush)
        paintDC.DrawRectangle(0, 0, width, height)

        del paintDC
        event.Skip()
    # end onPaint

    def Refresh(self):
        self.internalRepresentation.Refresh()
        wx.Panel.Refresh(self)
    # end Refresh()

# end ZPanelListBox
