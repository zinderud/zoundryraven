import wx

# ------------------------------------------------------------------------------
# Card sizer implementation.  A card sizer simply sizes everything in it to
# the same size (the full size of the card sizer).  The assumption is that the
# user will hide/show the widgets in the sizer.
# ------------------------------------------------------------------------------
class ZCardSizer(wx.PySizer):

    def __init__(self):
        wx.PySizer.__init__(self)
    # end __init__()

    def CalcMin(self):
        return wx.Size(1, 1)
    # end CalcMin()

    def RecalcSizes(self):
        pos = self.GetPosition()
        size = self.GetSize()
        
        for sizerItem in self.GetChildren():
            sizerItem.SetDimension(pos, size)
    # end RecalcSizes()

# end ZCardSizer
