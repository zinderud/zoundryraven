import wx

# -------------------------------------------------------------------------------------------
# An interface that must be implemented in order for a class to function as a content
# provider for a Zoundry List View widget.  A content provider provides not only row
# information but also column information (if any).
# -------------------------------------------------------------------------------------------
class IZListViewContentProvider:

    def getImageList(self):
        u"Should return a ZMappedImageList instance." #$NON-NLS-1$
    # end getImageList()

    def getNumColumns(self):
        u"Should return the number of columns the list should have (defaults to 0 if not implemented)." #$NON-NLS-1$
        return 0
    # end getNumColumns()

    def getNumRows(self):
        u"Should return the number of rows the list should have (defaults to 0 if not implemented)." #$NON-NLS-1$
        return 0
    # end getNumRows()

    def getColumnInfo(self, columnIndex):
        u"Should return the column information for the given 0-based column index in the form (label, imageKey, style, width)." #$NON-NLS-1$
    # end getColumnInfo()

    def getRowText(self, rowIndex, columnIndex):
        u"Should return the row text found at the given rowIndex and (optional) columnIndex." #$NON-NLS-1$
    # end getRowText()

    def getRowImage(self, rowIndex, columnIndex):
        u"Should return the row image index found at the given rowIndex and (optional) columnIndex (return -1 for no image)." #$NON-NLS-1$
    # end getRowImage()

# end IZListViewContentProvider


# -------------------------------------------------------------------------------------------
# A Zoundry List View widget.  This widget extends the standard WX widget in order to
# implement a content provider model.
# -------------------------------------------------------------------------------------------
class ZListView(wx.ListCtrl):

    def __init__(self, contentProvider, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.DefaultSize, style = None, validator = wx.DefaultValidator, name = u"ZListView"): #$NON-NLS-1$
        self.contentProvider = contentProvider
        if not style:
            if contentProvider.getNumColumns() > 0:
                style = wx.LC_VIRTUAL | wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_HRULES
            else:
                style = wx.LC_VIRTUAL | wx.LC_LIST | wx.LC_SINGLE_SEL
        wx.ListCtrl.__init__(self, parent, id, pos, size, style, validator, name)
        self.AssignImageList(self.contentProvider.getImageList(), wx.IMAGE_LIST_SMALL)

        if self.contentProvider.getNumColumns() > 0:
            self._createColumns()

        self.SetItemCount(self.contentProvider.getNumRows())
    # end __init__()
    
    def setContentProvider(self, contentProvider):
        self.contentProvider = contentProvider
    # end setContentProvider()

    def refresh(self):
        self.SetItemCount(self.contentProvider.getNumRows())
        if self.contentProvider.getNumRows() == 0:
            self.DeleteAllItems()
        else:
            self.RefreshItems(0, self.contentProvider.getNumRows() - 1)

        # Now update column titles, if necessary
        for colIdx in range(0, self.contentProvider.getNumColumns()):
            lItem = self.GetColumn(colIdx)
            (label, imageKey, style, width) = self.contentProvider.getColumnInfo(colIdx) #@UnusedVariable
            if label != lItem.GetText():
                lItem.SetText(label)
                lItem.SetImage(-1)
                self.SetColumn(colIdx, lItem)
    # end refresh()

    def _createColumns(self):
        for i in range(0, self.contentProvider.getNumColumns()):
            (label, imageKey, style, width) = self.contentProvider.getColumnInfo(i)
            item = self._createListItem(label, imageKey, style, width)
            self.InsertColumnItem(i, item)
    # end _createColumns()

    def OnGetItemText(self, item, column):
        return self.contentProvider.getRowText(item, column)
    # end OnGetItemText()

    def OnGetItemColumnImage(self, item, column):
        return self.contentProvider.getRowImage(item, column)
    # end OnGetItemColumnImage()

    def _createListItem(self, label, imageKey, style, width):
        item = wx.ListItem()
        if label is not None:
            item.SetText(label)
        if imageKey is not None:
            item.SetImage(self.contentProvider.getImageList()[imageKey])
        if width > 0:
            item.SetWidth(width)
        if style > 0:
            item.SetAlign(style)
        return item
    # end _createListItem()

# end ZListView
