from wx.html import HtmlWindow #@UnresolvedImport
from zoundry.appframework.util.osutilfactory import getOSUtil
import wx

# FIXME (PJ) move or deprecate ZHTMLControl since ZHTMLViewControl (via IZHTMLViewControl) does the same
# If moving, then impl IZHTMLViewControl and move it to package /zoundry/appframework/ui/widgets/controls/advanced/htmlviewimpl

# -------------------------------------------------------------------------------------
# An extension of the WX HtmlWindow control.  This class adds some magic for calling
# back a handler when a link is clicked.
# -------------------------------------------------------------------------------------
class ZHTMLControl(HtmlWindow):

    def __init__(self, parent, style = 0, size = None, handler = None, pos = None):
        id = wx.ID_ANY
        name = u"ZHTMLControl" #$NON-NLS-1$
        self.handler = handler
        if size and pos:
            HtmlWindow.__init__(self, parent=parent, id=id, name=name, style=style, size=size, pos=pos)
        elif size:
            HtmlWindow.__init__(self, parent=parent, id=id, name=name, style=style, size=size)
        else:
            HtmlWindow.__init__(self, parent=parent, id=id, name=name, style=style)
    # end __init__()

    # FIXME (EPW) Add params to the callback by parsing the query part of the href.
    def OnLinkClicked(self, linkInfo):
        href = linkInfo.GetHref()
        if href.startswith(u"http"): #$NON-NLS-1$
            osutil = getOSUtil()
            osutil.openUrlInBrowser(href)
            return

        meth = None
        # Try the optional handler first
        if self.handler:
            meth = getattr(self.handler, href)
        # Next try the widget's parent
        if not meth or not callable(meth):
            meth = getattr(self.GetParent(), href)

        # If a method was found, call it, otherwise do nothing.
        if meth and callable(meth):
            meth()
    # end OnLinkClicked()

# end ZHTMLControl
