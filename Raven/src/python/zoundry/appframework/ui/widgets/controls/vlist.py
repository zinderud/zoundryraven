from zoundry.base.exceptions import ZAbstractMethodCalledException
import wx


# -------------------------------------------------------------------------------------------
# An interface that must be implemented in order for a class to function as a content
# provider for a Zoundry Virtual List Box widget.
# -------------------------------------------------------------------------------------------
class IZVListBoxContentProvider:

    def getNumRows(self):
        u"Should return the number of rows the list should have (defaults to 0 if not implemented)." #$NON-NLS-1$
        return 0
    # end getNumRows()

    def getRowItem(self, rowIndex):
        u"Should return the object associated with the given row index." #$NON-NLS-1$
    # end getRowItem()

# end IZVListBoxContentProvider


# -----------------------------------------------------------------------------------------
# An extension of the WX Html List Box, this class uses a content provider to provide the
# information that should be displayed in the box.
# -----------------------------------------------------------------------------------------
class ZVListBox(wx.VListBox):

    def __init__(self, provider, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.DefaultSize, style = 0, name = u"ZVListBox"): #$NON-NLS-1$
        self.provider = provider
        wx.VListBox.__init__(self, parent, id, pos, size, style, name) #$NON-NLS-1$
        self.SetItemCount(self.provider.getNumRows())
    # end __init__()

    def OnDrawItem(self, dc, rect, itemIndex):
        rowItem = self.provider.getRowItem(itemIndex)
        self._onDrawItem(dc, rect, rowItem)
    # end OnDrawItem()

    def OnMeasureItem(self, itemIndex):
        rowItem = self.provider.getRowItem(itemIndex)
        return self._onMeasureItem(rowItem)
    # end OnMeasureItem()
    
    def _onMeasureItem(self, item):
        u"Subclasses must override this method to measure the height of the given item." #$NON-NLS-1$
        raise ZAbstractMethodCalledException(unicode(self.__class__), u"_onMeasureItem") #$NON-NLS-1$
    # end OnMeasureItem()

    def _onDrawItem(self, dc, rect, item):
        u"Subclasses must override this method to draw the given item onto the DC." #$NON-NLS-1$
        raise ZAbstractMethodCalledException(unicode(self.__class__), u"_onDrawItem") #$NON-NLS-1$
    # end _onDrawItem()

# end ZVListBox
