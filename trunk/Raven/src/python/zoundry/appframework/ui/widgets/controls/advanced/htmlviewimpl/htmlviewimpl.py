from zoundry.appframework.ui.widgets.controls.common.panel import ZTransparentPanel


# ------------------------------------------------------------------------------
# The HTML view control must support these methods.  In addition, the following
# events are fired by the HTML View control:
#
# ZEVT_LINK_CLICK:  fired when the user clicks on a link in the page
# ------------------------------------------------------------------------------
class IZHTMLViewControl:

    def setXhtmlDocument(self, zxhtmlDocument, bodyOnly = True):
        u"""setXhtmlDocument(ZXhtmlDocument, boolean) -> None
        Sets the content of the view control to the given ZXhtmlDocument.""" #$NON-NLS-1$
    # end setXhtmlDocument()

    def setHtmlValue(self, html):
        u"""setHtmlValue(string) -> None
        Sets the content of the view control to the given
        HTML string.""" #$NON-NLS-1$
    # end setHtmlValue()

    def setFile(self, filename):
        u"""setFile(filename) -> None
        Sets the content of the view control to a .html file.""" #$NON-NLS-1$
    # end setFile()

    def setLinkCallback(self, functionCallbackHandler):
        u"""setLinkCallback(pythonObject) -> None
        Sets the callback object for function callbacks for links with py:: protocol.""" #$NON-NLS-1$
    # end setLinkCallback()

# end IZHTMLViewControl


# ------------------------------------------------------------------------------
# Base class for HTML View controls.  This control will have an OS-dependent 
# implementation.  The Windows impl, for example, will likely use an embedded
# version of internet explorer.
# ------------------------------------------------------------------------------
class ZBaseHTMLViewControl(ZTransparentPanel, IZHTMLViewControl):

    def __init__(self, *args, **kw):
        ZTransparentPanel.__init__(self, *args, **kw)
    # end __init__()

# end ZBaseHTMLViewControl
