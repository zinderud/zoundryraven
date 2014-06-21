from zoundry.appframework.global_services import getResourceRegistry

ART_LOADED = False
HOVER_BORDER_TOPLEFT = None
HOVER_BORDER_TOPRIGHT = None
HOVER_BORDER_BOTTOMLEFT = None
HOVER_BORDER_BOTTOMRIGHT = None
HOVER_BORDER_BORDER = None
HOVER_BORDER_FILL = None
CLICK_BORDER_ART_LOADED = False
CLICK_BORDER_TOPLEFT = None
CLICK_BORDER_TOPRIGHT = None
CLICK_BORDER_BOTTOMLEFT = None
CLICK_BORDER_BOTTOMRIGHT = None
CLICK_BORDER_BORDER = None
CLICK_BORDER_FILL = None
TOGGLE_BORDER_ART_LOADED = False
TOGGLE_BORDER_TOPLEFT = None
TOGGLE_BORDER_TOPRIGHT = None
TOGGLE_BORDER_BOTTOMLEFT = None
TOGGLE_BORDER_BOTTOMRIGHT = None
TOGGLE_BORDER_BORDER = None
TOGGLE_BORDER_FILL = None
ARROW = None

# ------------------------------------------------------------------------------
# Loads the art needed to draw the hover border.
# ------------------------------------------------------------------------------
def _loadArt():
    global ART_LOADED
    global HOVER_BORDER_TOPLEFT
    global HOVER_BORDER_TOPRIGHT
    global HOVER_BORDER_BOTTOMLEFT
    global HOVER_BORDER_BOTTOMRIGHT
    global HOVER_BORDER_BORDER
    global HOVER_BORDER_FILL
    global CLICK_BORDER_TOPLEFT
    global CLICK_BORDER_TOPRIGHT
    global CLICK_BORDER_BOTTOMLEFT
    global CLICK_BORDER_BOTTOMRIGHT
    global CLICK_BORDER_BORDER
    global CLICK_BORDER_FILL
    global TOGGLE_BORDER_TOPLEFT
    global TOGGLE_BORDER_TOPRIGHT
    global TOGGLE_BORDER_BOTTOMLEFT
    global TOGGLE_BORDER_BOTTOMRIGHT
    global TOGGLE_BORDER_BORDER
    global TOGGLE_BORDER_FILL
    global ARROW
    
    if ART_LOADED:
        return True
    
    registry = getResourceRegistry()

    HOVER_BORDER_TOPLEFT = registry.getBitmap(u"images/widgets/toolbar/hover/topleft.png") #$NON-NLS-1$
    HOVER_BORDER_TOPRIGHT = registry.getBitmap(u"images/widgets/toolbar/hover/topright.png") #$NON-NLS-1$
    HOVER_BORDER_BOTTOMLEFT = registry.getBitmap(u"images/widgets/toolbar/hover/bottomleft.png") #$NON-NLS-1$
    HOVER_BORDER_BOTTOMRIGHT = registry.getBitmap(u"images/widgets/toolbar/hover/bottomright.png") #$NON-NLS-1$
    HOVER_BORDER_BORDER = registry.getBitmap(u"images/widgets/toolbar/hover/border.png") #$NON-NLS-1$
    HOVER_BORDER_FILL = registry.getBitmap(u"images/widgets/toolbar/hover/fill.png") #$NON-NLS-1$
    CLICK_BORDER_TOPLEFT = registry.getBitmap(u"images/widgets/toolbar/click/topleft.png") #$NON-NLS-1$
    CLICK_BORDER_TOPRIGHT = registry.getBitmap(u"images/widgets/toolbar/click/topright.png") #$NON-NLS-1$
    CLICK_BORDER_BOTTOMLEFT = registry.getBitmap(u"images/widgets/toolbar/click/bottomleft.png") #$NON-NLS-1$
    CLICK_BORDER_BOTTOMRIGHT = registry.getBitmap(u"images/widgets/toolbar/click/bottomright.png") #$NON-NLS-1$
    CLICK_BORDER_BORDER = registry.getBitmap(u"images/widgets/toolbar/click/border.png") #$NON-NLS-1$
    CLICK_BORDER_FILL = registry.getBitmap(u"images/widgets/toolbar/click/fill.png") #$NON-NLS-1$
    TOGGLE_BORDER_TOPLEFT = registry.getBitmap(u"images/widgets/toolbar/toggle/topleft.png") #$NON-NLS-1$
    TOGGLE_BORDER_TOPRIGHT = registry.getBitmap(u"images/widgets/toolbar/toggle/topright.png") #$NON-NLS-1$
    TOGGLE_BORDER_BOTTOMLEFT = registry.getBitmap(u"images/widgets/toolbar/toggle/bottomleft.png") #$NON-NLS-1$
    TOGGLE_BORDER_BOTTOMRIGHT = registry.getBitmap(u"images/widgets/toolbar/toggle/bottomright.png") #$NON-NLS-1$
    TOGGLE_BORDER_BORDER = registry.getBitmap(u"images/widgets/toolbar/toggle/border.png") #$NON-NLS-1$
    TOGGLE_BORDER_FILL = registry.getBitmap(u"images/widgets/toolbar/toggle/fill.png") #$NON-NLS-1$
    ARROW = registry.getBitmap(u"images/widgets/toolbar/arrow.png") #$NON-NLS-1$
    
    ART_LOADED = True
# end _loadArt


# ------------------------------------------------------------------------------
# Generic function for drawing a line using a bitmap as a pen tip.
# ------------------------------------------------------------------------------
def _drawLine(dc, bitmap, startX, startY, endX, endY):
    while startX < endX or startY < endY:
        dc.DrawBitmap(bitmap, startX, startY)
        if startX < endX:
            startX += 1
        if startY < endY:
            startY += 1
# end _drawLine()


# ------------------------------------------------------------------------------
# Draws a little down arrow for the drop-down tool.
# ------------------------------------------------------------------------------
def drawArrow(dc, x, y):
    _loadArt()
    
    startX = x
    startY = y
    dc.DrawBitmap(ARROW, startX, startY)
#    dc.SetPen(wx.BLACK_PEN)
#    dc.SetBrush(wx.BLACK_BRUSH)
#    points = [ wx.Point(startX, startY), wx.Point(startX + 5, startY), wx.Point(startX + 2, startY + 2) ]
#    dc.DrawPolygon(points)
#    dc.DrawLine(startX, startY, startX + 5, startY)
#    dc.DrawLine(startX + 1, startY + 1, startX + 4, startY + 1)
#    dc.DrawPoint(startX + 2, startY + 2)
# end drawArrow()


# ------------------------------------------------------------------------------
# Generic function for filling in a rectangle using a bitmap as the pen.
# ------------------------------------------------------------------------------
def _fill(dc, bitmap, startX, startY, endX, endY):
    for i in range(startX, endX + 1):
        for j in range(startY, endY + 1):
            dc.DrawBitmap(bitmap, i, j)
# end _fill()


# ------------------------------------------------------------------------------
# Draws the tool hover border.
# ------------------------------------------------------------------------------
def drawHoverBorder(dc, w, h):
    _loadArt()
    
    # Top left
    dc.DrawBitmap(HOVER_BORDER_TOPLEFT, 0, 0)
    # Top right
    dc.DrawBitmap(HOVER_BORDER_TOPRIGHT, w - 3, 0)
    # Bottom left
    dc.DrawBitmap(HOVER_BORDER_BOTTOMLEFT, 0, h - 3)
    # Bottom right
    dc.DrawBitmap(HOVER_BORDER_BOTTOMRIGHT, w - 3, h - 3)
    # Top
    _drawLine(dc, HOVER_BORDER_BORDER, 3, 0, w - 3, 0)
    # Bottom
    _drawLine(dc, HOVER_BORDER_BORDER, 3, h - 1, w - 3, h - 1)
    # Left
    _drawLine(dc, HOVER_BORDER_BORDER, 0, 3, 0, h - 3)
    # Right
    _drawLine(dc, HOVER_BORDER_BORDER, w - 1, 3, w - 1, h - 3)
    # Fill
    _fill(dc, HOVER_BORDER_FILL, 3, 1, w - 3, h - 2)
    _fill(dc, HOVER_BORDER_FILL, 1, 3, 2, h - 3)
    _fill(dc, HOVER_BORDER_FILL, w - 3, 3, w - 2, h - 3)
# end drawHoverBorder()


# ------------------------------------------------------------------------------
# Draws the tool click border.
# ------------------------------------------------------------------------------
def drawClickBorder(dc, w, h):
    _loadArt()
    
    # Top left
    dc.DrawBitmap(CLICK_BORDER_TOPLEFT, 0, 0)
    # Top right
    dc.DrawBitmap(CLICK_BORDER_TOPRIGHT, w - 3, 0)
    # Bottom left
    dc.DrawBitmap(CLICK_BORDER_BOTTOMLEFT, 0, h - 3)
    # Bottom right
    dc.DrawBitmap(CLICK_BORDER_BOTTOMRIGHT, w - 3, h - 3)
    # Top
    _drawLine(dc, CLICK_BORDER_BORDER, 3, 0, w - 3, 0)
    # Bottom
    _drawLine(dc, CLICK_BORDER_BORDER, 3, h - 1, w - 3, h - 1)
    # Left
    _drawLine(dc, CLICK_BORDER_BORDER, 0, 3, 0, h - 3)
    # Right
    _drawLine(dc, CLICK_BORDER_BORDER, w - 1, 3, w - 1, h - 3)
    # Fill
    _fill(dc, CLICK_BORDER_FILL, 3, 1, w - 3, h - 2)
    _fill(dc, CLICK_BORDER_FILL, 1, 3, 2, h - 3)
    _fill(dc, CLICK_BORDER_FILL, w - 3, 3, w - 2, h - 3)
# end drawClickBorder()


# ------------------------------------------------------------------------------
# Draws the tool toggle border.
# ------------------------------------------------------------------------------
def drawToggleBorder(dc, w, h):
    _loadArt()
    
    # Top left
    dc.DrawBitmap(TOGGLE_BORDER_TOPLEFT, 0, 0)
    # Top right
    dc.DrawBitmap(TOGGLE_BORDER_TOPRIGHT, w - 3, 0)
    # Bottom left
    dc.DrawBitmap(TOGGLE_BORDER_BOTTOMLEFT, 0, h - 3)
    # Bottom right
    dc.DrawBitmap(TOGGLE_BORDER_BOTTOMRIGHT, w - 3, h - 3)
    # Top
    _drawLine(dc, TOGGLE_BORDER_BORDER, 3, 0, w - 3, 0)
    # Bottom
    _drawLine(dc, TOGGLE_BORDER_BORDER, 3, h - 1, w - 3, h - 1)
    # Left
    _drawLine(dc, TOGGLE_BORDER_BORDER, 0, 3, 0, h - 3)
    # Right
    _drawLine(dc, TOGGLE_BORDER_BORDER, w - 1, 3, w - 1, h - 3)
    # Fill
    _fill(dc, TOGGLE_BORDER_FILL, 3, 1, w - 3, h - 2)
    _fill(dc, TOGGLE_BORDER_FILL, 1, 3, 2, h - 3)
    _fill(dc, TOGGLE_BORDER_FILL, w - 3, 3, w - 2, h - 3)
# end drawToggleBorder()


# ------------------------------------------------------------------------------
# Draws the drop-down style toolbar tool's separator line (when hovering).
# ------------------------------------------------------------------------------
def drawHoverSepLine(dc, startX, startY, endX, endY):
    _loadArt()
    _drawLine(dc, HOVER_BORDER_BORDER, startX, startY, endX, endY)
# end drawHoverSepLine()


# ------------------------------------------------------------------------------
# Draws the drop-down style toolbar tool's separator line (when clicking).
# ------------------------------------------------------------------------------
def drawClickSepLine(dc, startX, startY, endX, endY):
    _loadArt()
    _drawLine(dc, CLICK_BORDER_BORDER, startX, startY, endX, endY)
# end drawClickSepLine()

