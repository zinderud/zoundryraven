from zoundry.appframework.global_services import getResourceRegistry
from zoundry.appframework.ui.util.colorutil import alphaBlend
from zoundry.appframework.ui.widgets.controls.common.bitmap import ZStaticBitmap
from zoundry.base.exceptions import ZAbstractMethodCalledException
from zoundry.blogapp.ui.views.view import ZView
import wx


# ------------------------------------------------------------------------------
# Holds the art resources needed by the boxed view (drop shadows).
# ------------------------------------------------------------------------------
class ZBoxedViewArt:

    def __init__(self):
        registry = getResourceRegistry()
        self.topRight = registry.getBitmap(u"images/widgets/boxedview/top_right.png") #$NON-NLS-1$
        self.right = registry.getBitmap(u"images/widgets/boxedview/right.png") #$NON-NLS-1$
        self.bottomRight = registry.getBitmap(u"images/widgets/boxedview/bottom_right.png") #$NON-NLS-1$
        self.bottom = registry.getBitmap(u"images/widgets/boxedview/bottom.png") #$NON-NLS-1$
        self.bottomLeft = registry.getBitmap(u"images/widgets/boxedview/bottom_left.png") #$NON-NLS-1$
        
        self.blendColor1 = wx.Colour(0, 0, 0, 122)
        self.blendColor2 = wx.Colour(0, 0, 0, 90)
        self.blendColor3 = wx.Colour(0, 0, 0, 45)
        self.blendColor4 = wx.Colour(0, 0, 0, 13)
    # end __init__()

# end ZBoxedViewArt

BOXED_VIEW_ART = None

def getBoxedViewArt():
    global BOXED_VIEW_ART
    if BOXED_VIEW_ART is None:
        BOXED_VIEW_ART = ZBoxedViewArt()
    return BOXED_VIEW_ART
# end getBoxedViewArt()


# ------------------------------------------------------------------------------
# Extends the ZView class, adding a specific visual style.  This class should
# be extended by views that want to have the flat/boxed visual look and feel
# featured by the Standard Perspective.
# ------------------------------------------------------------------------------
class ZBoxedView(ZView):

    def __init__(self, parent):
        ZView.__init__(self, parent, wx.ID_ANY, style = wx.NO_FULL_REPAINT_ON_RESIZE | wx.CLIP_CHILDREN)

        self.headerWidgets = []
        self.headerIcon = None
        self.headerLabel = None
        self.headerSizer = None
        self.contentSizer = None

        self._createWidgets()
        self._bindWidgetEvents()
        self._layoutWidgets()
    # end __init__()

    def _createWidgets(self):
        self.headerIcon = self._createHeaderIcon()
        self.headerLabel = self._createHeaderLabel()
        self.headerSpacer = wx.StaticText(self, wx.ID_ANY, u"") #$NON-NLS-1$

        self._createHeaderWidgets(self, self.headerWidgets)
        self._createContentWidgets(self)
    # end _createWidgets()

    def _createHeaderIcon(self):
        return ZStaticBitmap(self, self._getHeaderBitmap())
    # end _createHeaderIcon()

    def _createHeaderLabel(self):
        return wx.StaticText(self, wx.ID_ANY, self._getHeaderLabel())
    # end _createHeaderLabel()

    def _bindWidgetEvents(self):
        self.Bind(wx.EVT_PAINT, self.onPaint, self)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.onEraseBackground, self)
        self.Bind(wx.EVT_SIZE, self.onResize, self)
    # end _bindWidgetEvents()

    def _layoutWidgets(self):
        self.headerSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.headerSizer.SetMinSize(wx.Size(-1, 22))
        self.headerSizer.Add(self.headerIcon, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, 2)
        self.headerSizer.Add(self.headerLabel, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, 2)
        self.headerSizer.Add(self.headerSpacer, 1, wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, 2)

        for headerWidget in self.headerWidgets:
            self.headerSizer.Add(headerWidget, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, 2)

        self.contentSizer = self._layoutContentWidgets()

        viewSizer = wx.BoxSizer(wx.VERTICAL)
        viewSizer.AddSizer(self.headerSizer, 0, wx.ALL | wx.EXPAND, 2)
        viewSizer.AddSizer(self.contentSizer, 1, wx.TOP | wx.EXPAND, 2)

        borderSizer = wx.BoxSizer(wx.VERTICAL)
        borderSizer.AddSizer(viewSizer, 1, wx.ALL | wx.EXPAND, 1)

        dropShadowSizer = wx.BoxSizer(wx.VERTICAL)
        dropShadowSizer.AddSizer(borderSizer, 1, wx.EXPAND | wx.RIGHT | wx.BOTTOM, 4)

        self.SetSizer(dropShadowSizer)
        self.SetAutoLayout(True)
    # end _layoutWidgets()

    def _getHeaderBitmap(self):
        u"""_getHeaderBitmap() -> wx.Bitmap
        Returns the bitmap to use for the header.""" #$NON-NLS-1$
        raise ZAbstractMethodCalledException(self.__class__, u"_getHeaderBitmap") #$NON-NLS-1$
    # end _getHeaderBitmap()

    def _getHeaderLabel(self):
        u"""_getHeaderLabel() -> string
        Returns the label to use in the view header.""" #$NON-NLS-1$
        raise ZAbstractMethodCalledException(self.__class__, u"_getHeaderLabel") #$NON-NLS-1$
    # end _getHeaderLabel()

    def _createHeaderWidgets(self, parent, widgetList):
        u"""_createHeaderWidgets(wx.Widget, list) -> None
        Creates the widgets that will be contributed to the view header area.""" #$NON-NLS-1$
        raise ZAbstractMethodCalledException(self.__class__, u"_createHeaderWidgets") #$NON-NLS-1$
    # end _createHeaderWidgets()

    def _createContentWidgets(self, parent):
        u"""_createContentWidgets(wx.Widget) -> None
        Creates the widgets that will be contributed to the view's content area.""" #$NON-NLS-1$
        raise ZAbstractMethodCalledException(self.__class__, u"_createContentWidgets") #$NON-NLS-1$
    # end _createContentWidgets()

    def _layoutContentWidgets(self):
        u"""_layoutContentWidgets() -> wx.Sizer
        Returns the label to use in the view header.""" #$NON-NLS-1$
        raise ZAbstractMethodCalledException(self.__class__, u"_layoutContentWidgets") #$NON-NLS-1$
    # end _layoutContentWidgets()

    def onResize(self, event):
        (w, h) = self.GetSizeTuple()
        headerBottom = self.contentSizer.GetPositionTuple()[1]
        
        # Refresh the header
        rect = wx.Rect(0, 0, w, headerBottom)
        self.RefreshRect(rect)
        
        # Refresh the right side border
        rect = wx.Rect(w - 5, 0, 5, h)
        self.RefreshRect(rect)
        
        # Refresh the bottom border
        rect = wx.Rect(0, h - 5, w, h - 5)
        self.RefreshRect(rect)
        
        # Refresh the left border
        rect = wx.Rect(0, 0, 1, h)
        self.RefreshRect(rect)

        event.Skip()
    # end onResize()

    def onEraseBackground(self, event): #@UnusedVariable
        pass
    # end onEraseBackground()

    def onPaint(self, event):
        headerBottom = self.contentSizer.GetPositionTuple()[1] - 1

        (w, h) = self.GetSizeTuple()
        paintDC = wx.BufferedPaintDC(self)
        paintDC.SetBackground(wx.Brush(self.GetBackgroundColour(), wx.SOLID))
        paintDC.Clear()

        pen = wx.Pen(wx.Colour(130, 130, 130))
        brush = wx.TRANSPARENT_BRUSH

        # Draw dark/outer border
        paintDC.SetPen(pen)
        paintDC.SetBrush(brush)
        paintDC.DrawRectangle(0, 0, w - 4, h - 4)
        paintDC.DrawLine(0, headerBottom, w - 4, headerBottom)

        # Draw the white border highlights
        paintDC.SetPen(wx.WHITE_PEN)
        paintDC.DrawLine(1, 1, w - 5, 1)
        paintDC.DrawLine(1, 1, 1, headerBottom - 1)

        self._drawDropShadow(paintDC)

        del paintDC

        event.Skip()
    # end onPaint()

    # FIXME (EPW) cache the blended colors so they don't need to be created every time we paint
    # FIXME (EPW) generalize this drop shadow code so that it can be used by other widgets
    def _drawDropShadow(self, paintDC):
        (w, h) = self.GetSizeTuple() #@UnusedVariable
        art = getBoxedViewArt()
        
        bgColor = self.GetBackgroundColour()
        blendedColor1 = alphaBlend(bgColor, art.blendColor1)
        blendedColor2 = alphaBlend(bgColor, art.blendColor2)
        blendedColor3 = alphaBlend(bgColor, art.blendColor3)
        blendedColor4 = alphaBlend(bgColor, art.blendColor4)
        
        rightX = w - 4
        bottomY = h - 4

        brush = wx.TRANSPARENT_BRUSH
        paintDC.SetBrush(brush)

        # Top Right
        paintDC.DrawBitmap(art.topRight, rightX, 0)
        # Right and bottom
        paintDC.SetPen(wx.Pen(blendedColor1))
        paintDC.DrawLine(rightX, 4, rightX, bottomY)
        paintDC.DrawLine(4, bottomY, rightX, bottomY)
        paintDC.SetPen(wx.Pen(blendedColor2))
        paintDC.DrawLine(rightX + 1, 4, rightX + 1, bottomY)
        paintDC.DrawLine(4, bottomY + 1, rightX, bottomY + 1)
        paintDC.SetPen(wx.Pen(blendedColor3))
        paintDC.DrawLine(rightX + 2, 4, rightX + 2, bottomY)
        paintDC.DrawLine(4, bottomY + 2, rightX, bottomY + 2)
        paintDC.SetPen(wx.Pen(blendedColor4))
        paintDC.DrawLine(rightX + 3, 4, rightX + 3, bottomY)
        paintDC.DrawLine(4, bottomY + 3, rightX, bottomY + 3)
        # Bottom Right
        paintDC.DrawBitmap(art.bottomRight, rightX, bottomY)
        # Bottom Left
        paintDC.DrawBitmap(art.bottomLeft, 0, bottomY)
    # end _drawDropShadow()

# end ZBoxedView
