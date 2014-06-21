from zoundry.appframework.resources.resourceutils import ZMappedImageList
from zoundry.appframework.ui.events.listevents import ZEVT_POPUP_LIST_SELECTION
from zoundry.appframework.ui.util.fontutil import getTextDimensions
from zoundry.appframework.ui.widgets.controls.listex import IZListViewExContentProvider
from zoundry.appframework.ui.widgets.controls.listex import ZListViewEx
from zoundry.appframework.ui.widgets.controls.listex import ZPopupListView
import wx

# ------------------------------------------------------------------------------
# Content provider for listing all of the tabs in the drop-down list.
# ------------------------------------------------------------------------------
class ZTabSelectionListContentProvider(IZListViewExContentProvider):
    
    def __init__(self, tabs):
        self.tabs = tabs
        
        self.imageList = self._createImageList()
    # end __init__()

    def _createImageList(self):
        imageList = ZMappedImageList()
        for tab in self.tabs:
            bitmap = tab.getTabInfo().getBitmap()
            if bitmap is not None:
                imageList.addImage(unicode(tab.getTabId()), bitmap)
        return imageList
    # end _createImageList()

    def getImageList(self):
        return self.imageList
    # end getImageList()

    def getNumColumns(self):
        return 1
    # end getNumColumns()

    def getNumRows(self):
        return len(self.tabs)
    # end getNumRows()

    def getColumnInfo(self, columnIndex): #@UnusedVariable
        return (u"", None, None, ZListViewEx.COLUMN_RELATIVE, 100) #$NON-NLS-1$
    # end getColumnInfo()

    def getRowText(self, rowIndex, columnIndex): #@UnusedVariable
        return self.tabs[rowIndex].getTabInfo().getTitle()
    # end getRowText()

    def getRowImage(self, rowIndex, columnIndex): #@UnusedVariable
        tab = self.tabs[rowIndex]
        return self.imageList[unicode(tab.getTabId())]
    # end getRowImage()

# end ZTabSelectionListContentProvider


# ------------------------------------------------------------------------------
# This class implements a popup window that is used to select a tab from a 
# list of tabs.  This is useful when there are more tabs than can be shown
# on the tab bar.
# ------------------------------------------------------------------------------
class ZTabSelectionPopupWindow(wx.PopupTransientWindow):

    def __init__(self, parent, tabs):
        self.parent = parent
        self.tabs = tabs
        
        wx.PopupTransientWindow.__init__(self, parent, style = wx.SIMPLE_BORDER)

        self.SetBackgroundColour(u"#FFFFE6") #$NON-NLS-1$
        
        self._createWidgets()
        self._layoutWidgets()
        self._bindWidgetEvents()
        
        self.SetSize(self.GetBestSize())
        self.Layout()
    # end __init__()
    
    def _createWidgets(self):
        # FIXME (EPW) add a filter/nav bar to the popup to narrow down the search
        self.provider = ZTabSelectionListContentProvider(self.tabs)
        self.tabList = ZPopupListView(self.provider, self, style = wx.LC_VIRTUAL | wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_NO_HEADER | wx.NO_BORDER)
        self.tabList.SetBackgroundColour(u"#FFFFE6") #$NON-NLS-1$
    # end _createWidgets()
    
    def _layoutWidgets(self):
        self.tabList.SetSizeHints(self._getPreferredWidth(), self._getPreferredHeight())

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.tabList, 1, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)
        self.Layout()
    # end _layoutWidgets()
    
    def _bindWidgetEvents(self):
        self.Bind(ZEVT_POPUP_LIST_SELECTION, self.onTabSelected, self.tabList)
    # end _bindWidgetEvents()

    def onTabSelected(self, event):
        idx = event.getListId()
        tab = self.tabs[idx]
        self.parent._fireSelectedEvent(tab)
        self.Dismiss()
        event.Skip()
    # end onTabSelected()
    
    def _getPreferredWidth(self):
        largestW = 50
        largestBmpW = 0
        for tab in self.tabs:
            title = tab.getTabInfo().getTitle()
            (w, h) = getTextDimensions(title, self.tabList) #@UnusedVariable
            largestW = max(w + 10, largestW)
            bitmap = tab.getTabInfo().getBitmap()
            if bitmap is not None:
                largestBmpW = max(largestBmpW, bitmap.GetWidth())
        return largestW + largestBmpW
    # end _getPreferredWidth()
    
    def _getPreferredHeight(self):
        # FIXME (EPW) this logic is not guaranteed to work well for all operating systems
        totalH = 0
        imageH = 0
        imageList = self.provider.getImageList()
        if imageList is not None:
            (ilW, imageH) = imageList.GetSize(0) #@UnusedVariable
        for tab in self.tabs:
            (tabW, tabH) = getTextDimensions(tab.getTabInfo().getTitle(), self.tabList) #@UnusedVariable
            tabH = max(tabH, imageH)
            totalH += tabH + 2
        return totalH
    # end _getPreferredHeight()

# end ZTabSelectionPopupWindow

