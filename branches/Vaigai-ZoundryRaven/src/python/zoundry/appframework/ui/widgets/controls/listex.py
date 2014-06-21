from wx.lib.mixins.listctrl import CheckListCtrlMixin
from zoundry.appframework.messages import _extstr
from zoundry.appframework.ui.events.listevents import ZCheckBoxListChangeEvent
from zoundry.appframework.ui.events.listevents import ZEVT_CHECKBOX_LIST_CHANGE
from zoundry.appframework.ui.events.listevents import ZPopupListSelectionEvent
from zoundry.appframework.ui.util.uiutil import fireUIExecEvent
from zoundry.appframework.ui.widgets.controls.common.panel import ZTransparentPanel
from zoundry.appframework.ui.widgets.controls.list import IZListViewContentProvider
from zoundry.base.util.zthread import IZRunnable
import wx


# -------------------------------------------------------------------------------------------
# Extension of the base list view content provider to change the contract of the
# getColumnInfo() method.  See documentation of getColumnInfo() for details.
# -------------------------------------------------------------------------------------------
class IZListViewExContentProvider(IZListViewContentProvider):

    def getColumnInfo(self, columnIndex):
        u"""getColumnInfo(int) -> (string, string, int, int, int)
        Should return the column information for the given 0-based column
        index in the form (label, imageKey, style, resizeStyle, width).""" #$NON-NLS-1$
    # end getColumnInfo()

# end IZListViewExContentProvider


# -------------------------------------------------------------------------------------------
# This class represents the information about a single column in the list view.  It is
# created when the list view is initialized and maintains the column meta information
# throughout the life of the list view.
# -------------------------------------------------------------------------------------------
class ZListViewColumn:

    def __init__(self, columnId, label, imageKey, style, resizeStyle, width, relativeWidth):
        self.columnId = columnId
        self.label = label
        self.imageKey = imageKey
        self.style = style
        self.resizeStyle = resizeStyle
        self.width = width
        self.relativeWidth = relativeWidth
    # end __init__()

    def getId(self):
        return self.columnId
    # end getId()

    def hasLabel(self):
        return self.label is not None
    # end hasLabel()

    def getLabel(self):
        return self.label
    # end getLabel()

    def getImageKey(self):
        return self.imageKey
    # end getImageKey()

    def hasImageKey(self):
        return self.imageKey is not None
    # end hasImageKey()

    def getStyle(self):
        return self.style
    # end getStyle()

    def getResizeStyle(self):
        return self.resizeStyle
    # end getResizeStyle()

    def getWidth(self):
        return self.width
    # end getWidth()

    def setWidth(self, width):
        self.width = width
    # end setWidth()

    def getRelativeWidth(self):
        return self.relativeWidth
    # end getRelativeWidth()

    def setRelativeWidth(self, relativeWidth):
        self.relativeWidth = relativeWidth
    # end setRelativeWidth()

    def isAbsolute(self):
        return (self.resizeStyle & ZListViewEx.COLUMN_ABSOLUTE) > 0
    # end isAbsolute()

    def isRelative(self):
        return (self.resizeStyle & ZListViewEx.COLUMN_RELATIVE) > 0
    # end isRelative()

    def isLocked(self):
        return (self.resizeStyle & ZListViewEx.COLUMN_LOCKED) > 0
    # end isLocked()

# end ZListViewColumn


# -------------------------------------------------------------------------------------------
# A little helper runnable that can be posted to/executed on the UI thread in order to exec
# a method on the list view.
# -------------------------------------------------------------------------------------------
class ZListViewRunner(IZRunnable):

    def __init__(self, method):
        self.method = method
    # end __init__()

    def run(self):
        self.method()
    # end run()

# end ZListViewRunner


# -------------------------------------------------------------------------------------------
# A Zoundry List View widget.  This widget extends the standard WX widget in order to
# implement a content provider model.  In addition, it supports relative columns and locked
# columns (columns that aren't resizable).
# -------------------------------------------------------------------------------------------
class ZListViewEx(wx.ListCtrl):

    COLUMN_ABSOLUTE = 1
    COLUMN_LOCKED = 2
    COLUMN_RELATIVE = 4

    def __init__(self, contentProvider, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.DefaultSize, style = None, validator = wx.DefaultValidator, name = u"ZListView"): #$NON-NLS-1$
        self.contentProvider = contentProvider
        self.hasRelativeColumn = False
        if not style:
            if contentProvider.getNumColumns() > 0:
                style = wx.LC_VIRTUAL | wx.LC_REPORT | wx.LC_SINGLE_SEL
            else:
                style = wx.LC_VIRTUAL | wx.LC_LIST | wx.LC_SINGLE_SEL
        self.style = style

        # Init the List Control parent
        wx.ListCtrl.__init__(self, parent, id, pos, size, style, validator, name)

        imageList = self.contentProvider.getImageList()
        if imageList is not None:
            self.AssignImageList(imageList, wx.IMAGE_LIST_SMALL)

        self.columnData = []
        if self.contentProvider.getNumColumns() > 0:
            self._createColumns()

        # if this is a virtual list, simply call SetItemCount, otherwise
        # populate manually from the provider
        if style & wx.LC_VIRTUAL:
            self.SetItemCount(self.contentProvider.getNumRows())
        else:
            self._populateList()

        self.SetMinSize(wx.Size(20, 50))
        self.SetSizeHints(20, 50)

        self.Bind(wx.EVT_SIZE, self.onResize, self)
        self.Bind(wx.EVT_LIST_COL_BEGIN_DRAG, self.onColumnBeginDrag, self)
        self.Bind(wx.EVT_LIST_COL_END_DRAG, self.onColumnResize, self)
    # end __init__()

    def setContentProvider(self, contentProvider):
        self.contentProvider = contentProvider
    # end setContentProvider()

    def refresh(self):
        # FIXME (EPW) refresh is currently broken for non-Virtual lists. See also ZCheckBoxListView::refreshItems()
        self.SetItemCount(self.contentProvider.getNumRows())
        if self.contentProvider.getNumRows() == 0:
            self.DeleteAllItems()
        else:
            self.RefreshItems(0, self.contentProvider.getNumRows() - 1)
        
        # Now update column titles, if necessary
        for colIdx in range(0, self.contentProvider.getNumColumns()):
            lItem = self.GetColumn(colIdx)
            (label, imageKey, style, resizeStyle, width) = self.contentProvider.getColumnInfo(colIdx) #@UnusedVariable
            if label != lItem.GetText():
                lItem.SetText(label)
                lItem.SetImage(-1)
                self.SetColumn(colIdx, lItem)
    # end refresh()

    def deselectAll(self):
        idx = self.GetFirstSelected()
        while idx != -1:
            self.Select(idx, False)
            idx = self.GetNextSelected(idx)
    # end deselectAll()

    def _getWidth(self):
        (widgetWidth, h) = self.GetClientSizeTuple() #@UnusedVariable
        return widgetWidth
    # end _getWidth()

    def _createColumns(self):
        widgetWidth = self._getWidth()
        for i in range(0, self.contentProvider.getNumColumns()):
            (label, imageKey, style, resizeStyle, width) = self.contentProvider.getColumnInfo(i)
            # Create the column object and append it to the list of columns.
            column = ZListViewColumn(i, label, imageKey, style, resizeStyle, -1, -1)
            self.columnData.append(column)
            if column.isAbsolute():
                column.setWidth(width)
            else:
                self.hasRelativeColumn = True
                column.setRelativeWidth(width)
                width = int((widgetWidth * column.getRelativeWidth()) / 100)
                column.setWidth(width)

            # Use the column object to create the list item and insert it.
            item = self._createListItem(column)
            self.InsertColumnItem(i, item)
    # end _createColumns()

    def _populateList(self):
        for rowIdx in range(0, self.contentProvider.getNumRows()):
            text = self.contentProvider.getRowText(rowIdx, 0)
            imgIdx = self.contentProvider.getRowImage(rowIdx, 0)
            if imgIdx != -1:
                self.InsertImageStringItem(rowIdx, text, imgIdx)
            else:
                self.InsertStringItem(rowIdx, text)
            for colIdx in range(1, self.contentProvider.getNumColumns()):
                colText = self.contentProvider.getRowText(rowIdx, colIdx)
                colImgIdx = self.contentProvider.getRowImage(rowIdx, colIdx)
                self.SetStringItem(rowIdx, colIdx, colText, colImgIdx)
    # end _populateList()

    def OnGetItemText(self, item, column):
        try:
            return self.contentProvider.getRowText(item, column)
        except:
            return u"" #$NON-NLS-1$
    # end OnGetItemText()

    def OnGetItemColumnImage(self, item, column):
        try:
            return self.contentProvider.getRowImage(item, column)
        except:
            return -1
    # end OnGetItemColumnImage()

    def onColumnBeginDrag(self, event):
        colIdx = event.GetColumn()
        column = self.columnData[colIdx]
        if column.isLocked():
            event.Veto()
        else:
            event.Skip()
    # end onColumnBeginDrag()

    def onColumnResize(self, event):
        if self.hasRelativeColumn and self.GetSizeTuple()[1] >= 30:
            fireUIExecEvent(ZListViewRunner(self._recalculateColumnWidths), self)
            fireUIExecEvent(ZListViewRunner(self._resizeColumns), self)
        event.Skip()
    # end onColumnResize()

    def onResize(self, event):
        if self.hasRelativeColumn and self.GetSizeTuple()[1] >= 30:
            fireUIExecEvent(ZListViewRunner(self._resizeColumns), self)
        event.Skip(True)
    # end onResize()

    def _getEffectiveWidth(self):
        widgetWidth = self._getWidth()
        absSpace = 0
        for column in self.columnData:
            if column.isAbsolute():
                absSpace = absSpace + column.getWidth()
        return widgetWidth - absSpace
    # end _getEffectiveWidth()

    def _recalculateColumnWidths(self):
        column = self._findResizedColumn()
        if column is None:
            return
        if column.isLocked():
            pass # do nothing for locked columns - they shouldn't be resizable
        elif column.isAbsolute():
            column.setWidth(self.GetColumnWidth(column.getId()))
        elif column.isRelative():
            nextColumn = self._findNextColumnForResize(column)
            if nextColumn is not None:
                newWidth = self.GetColumnWidth(column.getId())
                widthDiff = newWidth - column.getWidth()
                widthDiff = min(widthDiff, nextColumn.getWidth() - 2)
                newWidth = column.getWidth() + widthDiff
                column.setRelativeWidth(self._calculateRelativeWidth(newWidth))
                newNextColWidth = self.GetColumnWidth(nextColumn.getId()) - widthDiff
                nextColumn.setRelativeWidth(self._calculateRelativeWidth(newNextColWidth))
                self._smoothRelativeColumnError(column)
    # end _recalculateColumnWidths()

    def _findNextColumnForResize(self, column):
        nextColumnId = column.getId() + 1
        nextColumn = None
        while nextColumnId < len(self.columnData) and nextColumn is None:
            nextColumn = self.columnData[nextColumnId]
            if nextColumn.isLocked():
                nextColumn = None
        return nextColumn
    # end _findNextColumnForResize()

    def _smoothRelativeColumnError(self, column):
        totalRelWidth = 0
        for column in self.columnData:
            if column.isRelative():
                totalRelWidth = totalRelWidth + column.getRelativeWidth()
        relError = 100 - totalRelWidth
        column.setRelativeWidth(column.getRelativeWidth() + relError)
    # end _smoothRelativeColumnError()

    def _calculateRelativeWidth(self, width):
        widgetWidth = self._getEffectiveWidth()
        return (width * 100) / widgetWidth
    # end _calculateRelativeWidth()

    def _resizeColumns(self):
        widgetWidth = self._getEffectiveWidth()
        # Recalc the column sizes
        for column in self.columnData:
            if column.isRelative():
                width = int((widgetWidth * column.getRelativeWidth()) / 100)
                column.setWidth(width)
        # Distribute any error found due to integer math
        self._distributeColumnWidthError()
        # Resize the columns.
        for column in self.columnData:
            self.SetColumnWidth(column.getId(), column.getWidth())
    # end _resizeColumns()

    def _findResizedColumn(self):
        for column in self.columnData:
            oldWidth = column.getWidth()
            currentWidth = self.GetColumnWidth(column.getId())
            if oldWidth != currentWidth:
                return column
        return None
    # end _findResizedColumn()

    def _distributeColumnWidthError(self):
        widgetWidth = self._getWidth()
        totalColWidth = 0
        for column in self.columnData:
            totalColWidth = totalColWidth + column.getWidth()
        columnWidthError = (totalColWidth - widgetWidth) - 2
        # Short return if no error is found.
        if columnWidthError == 0:
            return

        pixels = 1
        if columnWidthError < 0:
            pixels = -1

        columnWidthError = abs(columnWidthError)
        column = self.columnData[0]
        for i in range(0, columnWidthError): #@UnusedVariable
            # Note: don't distribute error to absolute, locked columns
            column = self._getNextColumnForErrorDist(column)
            column.setWidth(column.getWidth() + pixels)
    # end _distributeColumnWidthError()

    def _getNextColumnForErrorDist(self, column):
        nextColumnId = column.getId() + 1
        if self._isLastColumn(column):
            nextColumnId = 0
        nextColumn = self.columnData[nextColumnId]
        if nextColumn.isAbsolute() and nextColumn.isLocked():
            return self._getNextColumnForErrorDist(nextColumn)
        else:
            return nextColumn
    # end _getNextColumnForErrorDist()

    def _isLastColumn(self, column):
        return column.getId() == (len(self.columnData) - 1)
    # end _isLastColumn()

    def _createListItem(self, column):
        item = wx.ListItem()
        if column.hasLabel():
            item.SetText(column.getLabel())
        if column.hasImageKey():
            item.SetImage(self.contentProvider.getImageList()[column.getImageKey()])
        if column.getWidth() > 0:
            item.SetWidth(column.getWidth())
        if column.getStyle() > 0:
            item.SetAlign(column.getStyle())
        return item
    # end _createListItem()

    def getSelection(self):
        u"""getSelection() -> int []
        Gets the indexes of the selected items in the list.""" #$NON-NLS-1$
        rval = []

        idx = self.GetFirstSelected()
        while idx != -1:
            rval.append(idx)
            idx = self.GetNextSelected(idx)

        return rval
    # end getSelection()

# end ZListViewEx


# ------------------------------------------------------------------------------
# Custom list view that auto-selects an item when the user hovers over it, and
# fires a ZEVT_POPUP_LIST_SELECTION when the user clicks an item in the list.
# ------------------------------------------------------------------------------
class ZPopupListView(ZListViewEx):

    def __init__(self, *args, **kw):
        ZListViewEx.__init__(self, *args, **kw)

        self.Bind(wx.EVT_MOTION, self.onMotion)
        self.Bind(wx.EVT_LEFT_DOWN, self.onLeftDown)
    # end __init__()

    def onMotion(self, event):
        item, flags = self.HitTest(event.GetPosition()) #@UnusedVariable
        if item >= 0:
            self.Select(item)
            self.curitem = item
    # end onMotion()

    def onLeftDown(self, event):
        selection = self.getSelection()
        if selection is not None and len(selection) > 0:
            event = ZPopupListSelectionEvent(self.GetId(), selection[0])
            self.GetEventHandler().AddPendingEvent(event)
        event.Skip()
    # end onLeftDown()

# end ZPopupListView


# ------------------------------------------------------------------------------
# Extends the list view ex interface in order to add check box list specific
# methods.
# ------------------------------------------------------------------------------
class IZCheckBoxListViewContentProvider(IZListViewExContentProvider):

    def isChecked(self, rowIndex):
        u"""isChecked(int) -> boolean
        Should return True if the item in the given row is
        checked.""" #$NON-NLS-1$
    # end isChecked()

    def setChecked(self, rowIndex, checked):
        u"""setChecked(int, boolean) -> void
       Sets the checked status given the row index.""" #$NON-NLS-1$
    # end setChecked

# end IZCheckBoxListViewContentProvider


# ------------------------------------------------------------------------------
# List view with checkboxes.  Extends the list view ex, using the same content
# provider.
# ------------------------------------------------------------------------------
class ZCheckBoxListView(ZListViewEx, CheckListCtrlMixin):

    def __init__(self, contentProvider, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.DefaultSize, style = None, validator = wx.DefaultValidator, name = u"ZCheckBoxListView"): #$NON-NLS-1$
        self.fireEventsFlag = True
        if not style:
            if contentProvider.getNumColumns() > 0:
                style = wx.LC_REPORT | wx.LC_SINGLE_SEL
            else:
                style = wx.LC_LIST | wx.LC_SINGLE_SEL
        ZListViewEx.__init__(self, contentProvider, parent, id, pos, size, style, validator, name)
        CheckListCtrlMixin.__init__(self)

        # Now really populate.
        self._populateCheckListItems()

        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onItemActivated)
    # end __init__()

    # FIXME (EPW) fix in base class
    def _populateCheckListItems(self):
        # Now really populate.
        self.fireEventsFlag = False
        ZListViewEx._populateList(self)
        for rowIdx in range(0, self.contentProvider.getNumRows()):
            if self.contentProvider.isChecked(rowIdx):
                self.ToggleItem(rowIdx)
        self.fireEventsFlag = True
    # end _populateCheckListItems()

    def refreshItems(self):
        # Deletes and re-populates items based on the provider content.
        # This is a work around for providers that are initially empty and later populated with data. The refresh() method
        # will not work (for virtual controls) since the GetItemCount() is 0.)
        self.DeleteAllItems()
        self._populateCheckListItems()
    # end refreshItems()

    def OnCheckItem(self, index, checked): #@UnusedVariable
        self.contentProvider.setChecked(index, checked)
        if self.fireEventsFlag:
            self._fireCheckBoxListChangeEvent(index)
    # end OnCheckItem()

    def onItemActivated(self, event):
        listIdx = event.GetIndex()
        self.ToggleItem(listIdx)
        event.Skip()
    # end onItemActivated()

    def checkAll(self):
        for idx in range(0, self.GetItemCount()):
            if not self.IsChecked(idx):
                self.ToggleItem(idx)
    # end checkAll()

    def uncheckAll(self):
        for idx in range(0, self.GetItemCount()):
            if self.IsChecked(idx):
                self.ToggleItem(idx)
    # end uncheckAll()

    # Override to NOT populate in the base class's c'tor.
    def _populateList(self):
        pass
    # end _populateList()

    def getCheckedItems(self):
        u"""getCheckedItems() -> int[]
        Returns a list of the items that are checked.""" #$NON-NLS-1$
        rval = []
        for rowIdx in range(self.contentProvider.getNumRows()):
            if self.IsChecked(rowIdx):
                rval.append(rowIdx)
        return rval
    # end getCheckedItems()

    def _fireCheckBoxListChangeEvent(self, listId):
        event = ZCheckBoxListChangeEvent(self.GetId(), listId, self.IsChecked(listId))
        self.GetEventHandler().AddPendingEvent(event)
    # end _fireCheckBoxListChangeEvent()

# end ZCheckBoxListView


# ------------------------------------------------------------------------------
# List view with radio (single select).  Extends the list view ex, using the same content
# provider.
# ------------------------------------------------------------------------------
class ZRadioBoxListView(ZCheckBoxListView):

    def __init__(self, contentProvider, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.DefaultSize, style = None, validator = wx.DefaultValidator, name = u"ZRadioBoxListView"): #$NON-NLS-1$
        ZCheckBoxListView.__init__(self, contentProvider, parent, id, pos, size, style, validator, name)
    # end __init__()

    # FIXME (EPW) fix in base class
    def _populateCheckListItems(self):
        # Now really populate.
        self.fireEventsFlag = False
        ZListViewEx._populateList(self)
        for rowIdx in range(0, self.contentProvider.getNumRows()):
            # check only one item
            if self.contentProvider.isChecked(rowIdx):
                self.ToggleItem(rowIdx)
                break
        self.fireEventsFlag = True
    # end _populateCheckListItems()

    def OnCheckItem(self, index, checked): #@UnusedVariable
        self.contentProvider.setChecked(index, checked)
        if self.fireEventsFlag:
            self._fireCheckBoxListChangeEvent(index)
    # end OnCheckItem()

    def CheckItem(self, index, check = True):
        if self.IsChecked(index):
            return
        # deselect all but the curent index
        for rowIdx in range(0, self.contentProvider.getNumRows()):
            if self.IsChecked(rowIdx):
                ZCheckBoxListView.CheckItem(self, rowIdx, False)
        # check new item
        ZCheckBoxListView.CheckItem(self, index, check)
    # end CheckItem

    def checkAll(self):
        pass
    # end checkAll()

    def uncheckAll(self):
        pass
    # end uncheckAll()

# end ZRadioBoxListView

# ------------------------------------------------------------------------------
# List view with checkboxes and "check all"/"uncheck all" buttons.  This is a
# composite control, using the ZCheckBoxListView and two wx.Buttons.
# ------------------------------------------------------------------------------
class ZCheckBoxListViewWithButtons(ZTransparentPanel):

    def __init__(self, contentProvider, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.DefaultSize, style = None, validator = wx.DefaultValidator, name = u"ZCheckBoxListView"): #$NON-NLS-1$
        self.contentProvider = contentProvider
        self.style = style
        self.validator = validator

        ZTransparentPanel.__init__(self, parent, id, pos = pos, size = size, name = name)

        self._createWidgets()
        self._layoutWidgets()
        self._bindWidgetEvents()
    # end __init__()

    def _createWidgets(self):
        self.checkBoxListView = ZCheckBoxListView(self.contentProvider, self, style = self.style, validator = self.validator)
        self.checkAllButton = wx.Button(self, wx.ID_ANY, _extstr(u"listex.CheckAll")) #$NON-NLS-1$
        self.uncheckAllButton = wx.Button(self, wx.ID_ANY, _extstr(u"listex.UncheckAll")) #$NON-NLS-1$
    # end _createWidgets()

    def _layoutWidgets(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        buttonBox = wx.BoxSizer(wx.VERTICAL)
        buttonBox.Add(self.checkAllButton, 0, wx.BOTTOM, 5)
        buttonBox.Add(self.uncheckAllButton, 0)

        sizer.Add(self.checkBoxListView, 1, wx.EXPAND | wx.RIGHT, 5)
        sizer.AddSizer(buttonBox, 0)

        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        self.Layout()
    # end _layoutWidgets()

    def _bindWidgetEvents(self):
        self.Bind(wx.EVT_BUTTON, self.onCheckAll, self.checkAllButton)
        self.Bind(wx.EVT_BUTTON, self.onUncheckAll, self.uncheckAllButton)
        self.Bind(ZEVT_CHECKBOX_LIST_CHANGE, self.onPropagateEvent, self.checkBoxListView)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onPropagateEvent, self.checkBoxListView)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onPropagateEvent, self.checkBoxListView)
        self.Bind(wx.EVT_LIST_ITEM_FOCUSED, self.onPropagateEvent, self.checkBoxListView)
        self.Bind(wx.EVT_LIST_ITEM_MIDDLE_CLICK, self.onPropagateEvent, self.checkBoxListView)
        self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.onPropagateEvent, self.checkBoxListView)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onPropagateEvent, self.checkBoxListView)
        self.Bind(wx.EVT_LIST_BEGIN_DRAG, self.onPropagateEvent, self.checkBoxListView)
        self.Bind(wx.EVT_LIST_BEGIN_LABEL_EDIT, self.onPropagateEvent, self.checkBoxListView)
        self.Bind(wx.EVT_LIST_BEGIN_RDRAG, self.onPropagateEvent, self.checkBoxListView)
        self.Bind(wx.EVT_LIST_COL_BEGIN_DRAG, self.onPropagateEvent, self.checkBoxListView)
        self.Bind(wx.EVT_LIST_COL_CLICK, self.onPropagateEvent, self.checkBoxListView)
        self.Bind(wx.EVT_LIST_COL_DRAGGING, self.onPropagateEvent, self.checkBoxListView)
        self.Bind(wx.EVT_LIST_COL_END_DRAG, self.onPropagateEvent, self.checkBoxListView)
        self.Bind(wx.EVT_LIST_COL_RIGHT_CLICK, self.onPropagateEvent, self.checkBoxListView)
        self.Bind(wx.EVT_LIST_DELETE_ALL_ITEMS, self.onPropagateEvent, self.checkBoxListView)
        self.Bind(wx.EVT_LIST_DELETE_ITEM, self.onPropagateEvent, self.checkBoxListView)
        self.Bind(wx.EVT_LIST_END_LABEL_EDIT, self.onPropagateEvent, self.checkBoxListView)
        self.Bind(wx.EVT_LIST_INSERT_ITEM, self.onPropagateEvent, self.checkBoxListView)
        self.Bind(wx.EVT_LIST_KEY_DOWN, self.onPropagateEvent, self.checkBoxListView)
    # end _bindWidgetEvents()

    def onCheckAll(self, event):
        self.checkBoxListView.checkAll()
        event.Skip()
    # end onCheckAll()

    def onUncheckAll(self, event):
        self.checkBoxListView.uncheckAll()
        event.Skip()
    # end onUncheckAll()

    def getCheckedItems(self):
        return self.checkBoxListView.getCheckedItems()
    # end getCheckedItems()

    def refresh(self):
        self.checkBoxListView.refreshItems()
    # end refresh()

    def onPropagateEvent(self, event):
        # Propagate the event
        event.SetId(self.GetId())
        self.GetEventHandler().AddPendingEvent(event)
    # end onPropagateEvent()

# end ZCheckBoxListViewWithButtons
