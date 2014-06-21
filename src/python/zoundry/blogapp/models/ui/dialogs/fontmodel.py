from zoundry.base.css.cssfont import ZCssFontInfo
from zoundry.base.util.text.textutil import getNoneString
from zoundry.base.util.types.attrmodel import ZModelWithNoneValueAttributes


# ------------------------------------------------------------------------------------
# Model used by the font settings dialog.
# ------------------------------------------------------------------------------------
class ZFontModel(ZModelWithNoneValueAttributes):

    def __init__(self, styleContext):
        ZModelWithNoneValueAttributes.__init__(self)
        # styleContext: instance of IZXHTMLEditControlStyleContext
        self.fontName = None
        self.fontSize = None
        self.setFontInfo( styleContext.getFontInfo() )
        self.cssColor = styleContext.getColor()
        self.cssBgColor = styleContext.getBackgroundColor()
    # end __init__

    def getFontInfo(self):
        fontInfo = ZCssFontInfo()
        fontInfo.setFontName( self.getFontName() )
        fontInfo.setFontSize( self.getFontSize())
        return fontInfo
    # end getFontInfo

    def setFontInfo(self, cssFontInfo):
        if cssFontInfo:
            self.setFontName( cssFontInfo.getFontName() )
            self.setFontSize( cssFontInfo.getFontSize() )
    # end setFontInfo

    def getFontName(self):
        return self.fontName
    # end getFontName()

    def setFontName(self, fontName):
        self.fontName = getNoneString(fontName)
    # end setFontName

    def getFontSize(self):
        return self.fontSize
    # end getFontSize()

    def setFontSize(self, fontSize):
        self.fontSize = getNoneString(fontSize)
    # end setFontSize

    def getColor(self):
        return self.cssColor
    # end getColor()

    def setColor(self, cssColor):
        self.cssColor = cssColor
    # end setColor

    def getBackground(self):
        return self.cssBgColor
    # end getBackground()

    def setBackground(self, cssColor):
        self.cssBgColor = cssColor
    # end  setBackground()
# end ZFontModel())