import wx

# --------------------------------------------------------------------------------
# Custom bitmap control.
# --------------------------------------------------------------------------------
class ZStaticBitmap(wx.PyControl):

    def __init__(self, parent, bitmap):
        self.bitmap = bitmap
        self.backgroundColor = None

        wx.PyControl.__init__(self, parent, wx.ID_ANY, style = wx.NO_BORDER)
        
        if bitmap is not None:
            self.SetSizeHints(bitmap.GetWidth(), bitmap.GetHeight())
        
        self.Bind(wx.EVT_PAINT, self.onPaint, self)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.onEraseBackground, self)
    # end __init__()

    def setBackgroundColor(self, backgroundColor):
        self.backgroundColor = backgroundColor
    # end setBackgroundColor()
    
    def setBitmap(self, bitmap):
        self.bitmap = bitmap
        self.SetSizeHints(bitmap.GetWidth(), bitmap.GetHeight())
    # end setBitmap()
    
    def onEraseBackground(self, event): #@UnusedVariable
        pass
    # end onEraseBackground()

    def onPaint(self, event):
        paintDC = wx.BufferedPaintDC(self)
        if self.backgroundColor is None:
            paintDC.SetBackground(wx.Brush(self.GetParent().GetBackgroundColour(), wx.SOLID))
        else:
            paintDC.SetBackground(wx.Brush(self.backgroundColor, wx.SOLID))
        paintDC.Clear()

        if self.bitmap is not None:
            paintDC.DrawBitmap(self.bitmap, 0, 0)
        
        del paintDC
        event.Skip()
    # end onPaint()

# end ZStaticBitmap
