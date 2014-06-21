from zoundry.appframework.ui.widgets.controls.advanced.stc.stceditor import ZStyledXhtmlEditControl
from zoundry.base.zdom import tidyutil
from zoundry.blogapp.ui.editors.blogeditorctrls.blogposteditcontrol import IZBlogPostEditControl

# ------------------------------------------------------------------------------
# A concrete implementation of a blog post edit control.  This control uses the
# Scintilla STC component to edit the post content.
# ------------------------------------------------------------------------------
class ZStyledXhtmlBlogPostEditControl(ZStyledXhtmlEditControl, IZBlogPostEditControl):

    def __init__(self, parent):
        ZStyledXhtmlEditControl.__init__(self, parent)
    # end __init__()

    def _getCapabilityIdList(self):
        rval = ZStyledXhtmlEditControl._getCapabilityIdList(self)
        return rval
    # end _getCapabilityIdList()


    def setXhtmlDocument(self, xhtmlDoc):
        # Override base class to show 'pretty print' version of the xhtml document body content.
        body = xhtmlDoc.getBody()
        xhtmlString = body.serialize()
        xhtmlString = tidyutil.tidyHtml(xhtmlString, tidyutil.SOURCE_OPTIONS)
        self.setValue(xhtmlString)
    # end setXhtmlDocument()

    def canRemoveExtendedEntryMarker(self):
        return False
    # end canRemoveExtendedEntryMarker()

    def removeExtendedEntryMarker(self):
        pass
    # removeExtendedEntryMarker()

    def insertExtendedEntryMarker(self):
        pass
    # insertExtendedEntryMarker()

# end ZStyledXhtmlBlogPostEditControl