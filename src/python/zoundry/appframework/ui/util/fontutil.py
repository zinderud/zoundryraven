import wx

DEFAULT_FONT = None
DEFAULT_FONT_BOLD = None
DEFAULT_FONT_ITALIC = None

# ---------------------------------------------------------------------------------------
# Convenience method that returns the default font.
# ---------------------------------------------------------------------------------------
def getDefaultFont():
    global DEFAULT_FONT
    if DEFAULT_FONT is None:
        DEFAULT_FONT = wx.Font(-1, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False)
    return DEFAULT_FONT
# end getDefaultFont()


# ---------------------------------------------------------------------------------------
# Convenience method that returns the default font, with weight set to BOLD.
# ---------------------------------------------------------------------------------------
def getDefaultFontBold():
    global DEFAULT_FONT_BOLD
    if DEFAULT_FONT_BOLD is None:
        DEFAULT_FONT_BOLD = wx.Font(-1, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False)
    return DEFAULT_FONT_BOLD
# end getDefaultFontBold()


# ---------------------------------------------------------------------------------------
# Convenience method that returns the default font, with weight set to BOLD.
# ---------------------------------------------------------------------------------------
def getDefaultFontItalic():
    global DEFAULT_FONT_ITALIC
    if DEFAULT_FONT_ITALIC is None:
        DEFAULT_FONT_ITALIC = wx.Font(-1, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_NORMAL, False)
    return DEFAULT_FONT_ITALIC
# end getDefaultFontItalic()


# ---------------------------------------------------------------------------------------
# Convenience method that returns the width and height needed to display the given text
# using the given font.
# ---------------------------------------------------------------------------------------
def getFontDimensions(text, font, window):
    u"""getFontDimensions(string, wx.Font, wx.Window) -> (w, h)""" #$NON-NLS-1$
    dc = wx.WindowDC(window)
    dc.SetFont(font)
    (w, h) = dc.GetTextExtent(text)
    return (w, h)
# end getFontDimensions()


# ---------------------------------------------------------------------------------------
# Convenience method that returns the width and height needed to display the given text
# using the window's font.
# ---------------------------------------------------------------------------------------
def getTextDimensions(text, window):
    u"""getTextDimensions(string, wx.Window) -> (w, h)""" #$NON-NLS-1$
    return window.GetTextExtent(text)
# end getTextDimensions()


# ---------------------------------------------------------------------------------------
# Given a string and a width, returns a new string that is truncated (with an ending
# ellipsis) to fit within the given width.
# ---------------------------------------------------------------------------------------
def sizeStringToFit(text, width, window):
    u"""sizeStringToFit(string, int, wx.Window) -> string""" #$NON-NLS-1$
    if getTextDimensions(text, window)[0] <= width:
        return text
    
    for idx in range(len(text) - 3, 0, -1):
        subtext = text[0:idx] + u"..." #$NON-NLS-1$
        if getTextDimensions(subtext, window)[0] <= width:
            return subtext
    
    return u"" #$NON-NLS-1$
# end sizeStringToFit()
