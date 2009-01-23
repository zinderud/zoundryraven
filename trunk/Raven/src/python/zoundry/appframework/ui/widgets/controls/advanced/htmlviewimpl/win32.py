from zoundry.appframework.ui.util.colorutil import getDefaultControlBorderColor
from zoundry.appframework.ui.widgets.controls.advanced.htmlviewimpl.htmlviewimpl import ZBaseHTMLViewControl
from zoundry.appframework.ui.widgets.controls.advanced.mshtml.mshtmlcontrol import IZMshtmlEvents
from zoundry.appframework.ui.widgets.controls.advanced.mshtml.mshtmlcontrol import ZMSHTMLViewControl
from zoundry.base.util.text.textutil import getSafeString
from zoundry.base.util.urlutil import unquote_plus
from zoundry.appframework.util.osutilfactory import getOSUtil
import wx

# ------------------------------------------------------------------------------
# An Internet Explorer-backed implementation of an HTML View control.
# ------------------------------------------------------------------------------
class ZIExploreHTMLViewControl(ZBaseHTMLViewControl):

    def __init__(self, parent, id = wx.ID_ANY, style = wx.NO_BORDER | wx.NO_FULL_REPAINT_ON_RESIZE):
        self.style = style

        ZBaseHTMLViewControl.__init__(self, parent, id, style = wx.NO_BORDER)

        self._createWidgets()
        self._layoutWidgets()
        self._bindWidgetEvents()
    # end __init__()

    def _createWidgets(self):
        self.mstmlViewCtrl = ZMSHTMLViewControl(self, wx.ID_ANY)
    # end _createWidgets()

    def _layoutWidgets(self):
        box = wx.BoxSizer(wx.VERTICAL)
        if self.style & wx.SIMPLE_BORDER:
            box.Add(self.mstmlViewCtrl, 1, wx.EXPAND | wx.ALL, 1)
        else:
            box.Add(self.mstmlViewCtrl, 1, wx.EXPAND)
        self.SetAutoLayout(True)
        self.SetSizer(box)
        self.Layout()
    # end _layoutWidgets()

    def _bindWidgetEvents(self):
        self.Bind(IZMshtmlEvents.ZEVT_MSHTML_LINK_CLICK, self.onLinkClick, self.mstmlViewCtrl)

        self.Bind(wx.EVT_PAINT, self.onPaint, self)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.onEraseBackground, self)
        self.Bind(wx.EVT_SIZE, self.onResize, self)
    # end _bindWidgetEvents()

    def onLinkClick(self, event):
        url = getSafeString( event.getHref() )
        if url.lower().startswith(u"http"): #$NON-NLS-1$
            url = unquote_plus(url)
            osutil = getOSUtil()
            osutil.openUrlInBrowser(url)
    # end onLinkClick()

    def onEraseBackground(self, event): #@UnusedVariable
        pass
    # end onEraseBackground()

    def onPaint(self, event):
        if self.style & wx.SIMPLE_BORDER:
            paintDC = wx.BufferedPaintDC(self)
            paintDC.SetPen(wx.Pen(getDefaultControlBorderColor()))
            paintDC.SetBrush(wx.TRANSPARENT_BRUSH)
            (w, h) = self.GetSizeTuple()
            paintDC.DrawRectangle(0, 0, w, h)
            del paintDC
        event.Skip()
    # end onPaint()

    def onResize(self, event):
        (w, h) = self.GetSizeTuple()
        
        # Refresh the top border
        rect = wx.Rect(0, 0, w, 1)
        self.RefreshRect(rect)
        
        # Refresh the right side border
        rect = wx.Rect(w - 1, 0, w, h)
        self.RefreshRect(rect)
        
        # Refresh the bottom border
        rect = wx.Rect(0, h - 1, w, h)
        self.RefreshRect(rect)
        
        # Refresh the left border
        rect = wx.Rect(0, 0, 1, h)
        self.RefreshRect(rect)

        event.Skip()
    # end onResize()

    def setXhtmlDocument(self, zxhtmlDocument, bodyOnly = True):
        self.mstmlViewCtrl.setXhtmlDocument(zxhtmlDocument, bodyOnly)
    # end setXhtmlDocument()

    def setHtmlValue(self, html):
        self.mstmlViewCtrl.setHtmlValue(html)
    # end setHtmlValue()

    def setFile(self, filename):
        self.mstmlViewCtrl.setFile(filename)
    # end setFile()

    def setLinkCallback(self, functionCallbackHandler):
        self.mstmlViewCtrl.setLinkCallback(functionCallbackHandler)
    # end setLinkCallback

# end ZIExploreHTMLViewControl
