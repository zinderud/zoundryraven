import wx


# -------------------------------------------------------------------------------------------
# An interface that must be implemented in order for a class to function as a content
# provider for a Zoundry HTML List Box widget.
# -------------------------------------------------------------------------------------------
class IZHtmlListBoxContentProvider:

    def getNumRows(self):
        u"Should return the number of rows the list should have (defaults to 0 if not implemented)." #$NON-NLS-1$
        return 0
    # end getNumRows()

    def getRowHtml(self, rowIndex):
        u"Should return the row html fragment (no <html> or <body>) found at the given rowIndex." #$NON-NLS-1$
    # end getRowHtml()

# end IZHtmlListBoxContentProvider


# -----------------------------------------------------------------------------------------
# An extension of the WX Html List Box, this class uses a content provider to provide the
# information that should be displayed in the box.
# -----------------------------------------------------------------------------------------
class ZHtmlListBox(wx.HtmlListBox):

    def __init__(self, provider, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.DefaultSize, style = 0, name = u"ZHtmlListBox"): #$NON-NLS-1$
        self.provider = provider
        wx.HtmlListBox.__init__(self, parent, id, pos, size, style, name) #$NON-NLS-1$
        self.SetItemCount(self.provider.getNumRows())
    # end __init__()

    def OnGetItem(self, itemIndex):
        return self.provider.getRowHtml(itemIndex)
    # end OnGetItem()

# end ZHtmlListBox
