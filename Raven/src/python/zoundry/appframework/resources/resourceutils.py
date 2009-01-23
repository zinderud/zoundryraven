import wx

# -------------------------------------------------------------
# An image list that is also a map of names to image list 
# indexes.
# -------------------------------------------------------------
class ZMappedImageList(wx.ImageList):

    def __init__(self, width = 16, height = 16):
        wx.ImageList.__init__(self, width, height)
        self.map = {}
    # end __init__()

    # Adds an image to the ImageList with the given label.
    def addImage(self, label, image):
        u"""addImage(string, wxBitmap) -> None
        Adds the image to the image list and creates a mapping 
        from label to that bitmap.""" #$NON-NLS-1$
        
        if label in self.map:
            return self.map[label]

        if label and image:
            idx = self.Add(image)
            self.map[label] = idx
            return idx
        else:
            return -1
    # end addImage()

    def addImageWithColorMask(self, label, image, colorMask):
        if label and image:
            idx = self.AddWithColourMask(image, colorMask)
            self.map[label] = idx
            return idx
        else:
            return -1
    # end addImageWithColorMask()

    def getIndex(self, label):
        return self[label]
    # end getIndex()
    
    def hasLabel(self, label):
        return label in self.map
    # end hasLabel()

    def __getitem__(self, label):
        rVal = -1
        if label and self.map.has_key(label):
            rVal = self.map[label]
        return rVal
    # end __getitem__()

# end ZMappedImageList
