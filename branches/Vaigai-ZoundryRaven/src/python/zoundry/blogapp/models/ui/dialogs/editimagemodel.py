from zoundry.base.util.text.textutil import getNoneString
from zoundry.base.util.types.attrmodel import ZModelWithNoneValueAttributes
from zoundry.base.css.cssparse import parseCssBorderProperty
from zoundry.base.css.cssparse import parseCssRectangleProperty
from zoundry.base.util.text.textutil import getSafeString
from zoundry.appframework.ui.util.clipboardutil import getUrlFromClipboard

# ------------------------------------------------------------------------------------
# Model used by the edit image dialog.
# ------------------------------------------------------------------------------------
class ZEditImageModel(ZModelWithNoneValueAttributes):

    def __init__(self, imageAttrMap):
        ZModelWithNoneValueAttributes.__init__(self)
        self.editMode = False
        if imageAttrMap is not None:
            self.editMode = True
            for (n,v) in imageAttrMap.iteritems():
                self.setAttribute(n,v)
        if not self.getAttribute(u"src"): #$NON-NLS-1$ 
            url = getUrlFromClipboard()
            if url:
                self.setAttribute(u"src", url) #$NON-NLS-1$
    # end __init__
    
    def getImageAttributes(self):     
        attrs = {}
        for (n,v) in self.getAttributes():
            # skip 'style' since there should be separate attrs for border and margin.
            if n != u"style": #$NON-NLS-1$
                attrs[n] = v
        return attrs    
    # end getImageAttributes()

    def isEditMode(self):
        return self.editMode
    # end isEditMode
    
    def getMargins(self):
        # returns tuple(string, string, string, string)
        margin = getSafeString(self.getAttribute(u"margin")) #$NON-NLS-1$
        return parseCssRectangleProperty(margin)
    # end getMargins()
    
    def setMargins(self, top, right, bottom,  left):
        top = getNoneString(top)
        right = getNoneString(right)
        bottom = getNoneString(bottom)
        left = getNoneString(left)
        margins = None
        if top or right or bottom or left:
            # atleast one margin was specified.
            if not top:
                top = u"0px"#$NON-NLS-1$
            if not right:
                right = u"0px"#$NON-NLS-1$
            if not bottom:
                bottom = u"0px"#$NON-NLS-1$
            if not left:
                left = u"0px" #$NON-NLS-1$
            margins = u"%s %s %s %s" % (top, right, bottom, left)#$NON-NLS-1$
        self.setAttribute(u"margin", margins) #$NON-NLS-1$
            
    # end setMargins()

    def getBorder(self):
        # returns tuple(stringWidth, stringStyle, cssColor)
        border = getSafeString(self.getAttribute(u"border")) #$NON-NLS-1$
        return parseCssBorderProperty(border)
    # end getBorder()
    
    def setBorder(self, width, style, hexRgbColor):
        border = None #$NON-NLS-1$
        if style and style != u"none": #$NON-NLS-1$
            border = u"%s %s %s" % (width, style, hexRgbColor) #$NON-NLS-1$
        self.setAttribute(u"border", border) #$NON-NLS-1$
    # end setBorder()

# end ZEditImageModel