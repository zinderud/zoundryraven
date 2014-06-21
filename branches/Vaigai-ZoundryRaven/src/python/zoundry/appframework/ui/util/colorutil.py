import wx

# ------------------------------------------------------------------------------
# Returns the color of the default control border (e.g. border of a text or list
# control).
# ------------------------------------------------------------------------------
def getDefaultControlBorderColor():
    return wx.Color(123, 158, 189)
# end getDefaultControlBorderColor()


# ------------------------------------------------------------------------------
# Returns the color of the default control background (e.g. background of a text
# or list control).
# ------------------------------------------------------------------------------
def getDefaultControlBackgroundColor():
    # FIXME is this color in the standard WX colors?
    return wx.Color(255, 255, 255)
# end getDefaultControlBackgroundColor()


# ------------------------------------------------------------------------------
# Returns the color of the default window/dialog background (e.g. background of
# a dialog or window).
# ------------------------------------------------------------------------------
def getDefaultDialogBackgroundColor():
    return wx.SystemSettings_GetColour(wx.SYS_COLOUR_3DFACE)
# end getDefaultDialogBackgroundColor())


# ------------------------------------------------------------------------------
# Returns the color of the default window/dialog background (e.g. background of
# a dialog or window).
# ------------------------------------------------------------------------------
def getDisabledTextColor():
    return wx.SystemSettings_GetColour(wx.SYS_COLOUR_GRAYTEXT)
# end getDisabledTextColor())


# ------------------------------------------------------------------------------
# Returns the color of the default pop-down dialog background.
# ------------------------------------------------------------------------------
def getDefaultPopdownDialogBackgroundColor():
    return wx.Color(255, 255, 230)
# end getDefaultPopdownDialogBackgroundColor()


# ------------------------------------------------------------------------------
# Blends a color into another color using alpha blending.
# ------------------------------------------------------------------------------
def alphaBlend(bgColor, blendWithColor):
    maxA = 255
    
    srcR = blendWithColor.Red()
    srcG = blendWithColor.Green()
    srcB = blendWithColor.Blue()
    srcA = blendWithColor.Alpha()
    isrcA = 256 - srcA
    
    bgR = bgColor.Red()
    bgG = bgColor.Green()
    bgB = bgColor.Blue()
    
    r = ((srcR * srcA) + (bgR * isrcA)) / maxA
    g = ((srcG * srcA) + (bgG * isrcA)) / maxA
    b = ((srcB * srcA) + (bgB * isrcA)) / maxA
    
    return wx.Colour(r, g, b)
# end alphaBlend()
