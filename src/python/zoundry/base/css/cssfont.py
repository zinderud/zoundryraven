from zoundry.base.util.text.textutil import getNoneString


# ------------------------------------------------------------------------------
# Encapsulates css font information.
# ------------------------------------------------------------------------------
class ZCssFontInfo:

    def __init__(self):
        self.fontSize = None
        self.fontName = None
    # end __init__

    def getFontName(self):
        u"""getFontName() -> string or None
        """ #$NON-NLS-1$
        return self.fontName
    # end getFontName

    def setFontName(self, fontName):
        u"""setFontName(string) -> void
        """ #$NON-NLS-1$
        self.fontName = getNoneString(fontName)
    # end setFontName

    def getFontSize(self):
        u"""getFontSize() -> string or None
        """ #$NON-NLS-1$
        return self.fontSize
    # end getFontSize

    def setFontSize(self, fontSize):
        u"""setFontSize(string) -> void
        """ #$NON-NLS-1$
        self.fontSize = getNoneString(fontSize)
    # end setFontSize

# end ZCssFontInfo

#--------------------------------------------------------------------------------------------
# Enum of font sizes
#--------------------------------------------------------------------------------------------
class ZCssFontSizes:
        CSS_SIZES = [u"xx-small", u"x-small", u"small", u"medium", u"large", u"x-large", u"xx-large"] #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$ #$NON-NLS-4$ #$NON-NLS-5$ #$NON-NLS-6$ #$NON-NLS-7$
# end ZCssFontSizes
