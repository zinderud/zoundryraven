from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.ui.widgets.controls.advanced.mshtml.mshtmlcontrol import IZMshtmlEvents
from zoundry.appframework.ui.widgets.controls.advanced.mshtml.mshtmleditor import ZMshtmlEditControl
from zoundry.appframework.ui.widgets.controls.advanced.mshtml.mshtmluiproxies import ZMshtmlExtendedEntryMarkerProxy
from zoundry.appframework.ui.widgets.controls.advanced.mshtml.mshtmlvisitors import ZMshtmlExtEntryMarker2CommentZDomVisitor
from zoundry.appframework.ui.widgets.controls.advanced.mshtml.mshtmlvisitors import ZMshtmlRemoveCommentsVisitor
from zoundry.appframework.ui.widgets.controls.advanced.mshtml.mshtmlvisitors import ZMshtmlRemoveEmptyElementZDomVisitor
from zoundry.appframework.ui.widgets.controls.advanced.mshtml.mshtmlvisitors import ZMshtmlRemoveUnSelectableZDomVisitor
from zoundry.appframework.ui.widgets.controls.advanced.mshtml.mshtmlvisitors import ZMshtmlTextMoreComment2ExtEntryMarkerVisitor
from zoundry.appframework.ui.widgets.controls.advanced.mshtml.mshtmlvisitors import ZMshtmlWrapEmbedElementZDomVisitor
from zoundry.base.util.text.textutil import getNoneString
from zoundry.blogapp.constants import IZBlogAppUserPrefsKeys
from zoundry.blogapp.ui.editors.blogeditorctrls.blogposteditcontrol import IZBlogPostEditControl

# ------------------------------------------------------------------------------
# A concrete implementation of a blog post edit control.  This control uses the
# Microsoft MSHTML component to edit the post content.
# ------------------------------------------------------------------------------
class ZMSHTMLBlogPostEditControl(ZMshtmlEditControl, IZBlogPostEditControl):

    def __init__(self, parent):
        ZMshtmlEditControl.__init__(self, parent)
    # end __init__()

    def _bindWidgetEvents(self):
        ZMshtmlEditControl._bindWidgetEvents(self)
        self.Bind(IZMshtmlEvents.ZEVT_MSHTML_DOCUMENT_LOADED, self.onDocumentLoaded, self._getMshtmlControl())
    # end _bindWidgetEvents()

    def _getCapabilityIdList(self):
        rval = ZMshtmlEditControl._getCapabilityIdList(self)
        rval.append(IZBlogPostEditControl.ZCAPABILITY_EXTENDED_ENTRY_MARKER)
        return rval
    # end _getCapabilityIdList()

    def onDocumentLoaded(self, event): #@UnusedVariable
        # convert <!-- more --> to special markers
        doc = self._getMshtmlControl().getIHTMLDocument()
        visitor = ZMshtmlTextMoreComment2ExtEntryMarkerVisitor()
        visitor.visit(doc)
        # run visitors to remove remaining <!-- more --> comments (eliminate repeats/duplicates if any)
        visitor = ZMshtmlRemoveCommentsVisitor([ZMshtmlRemoveCommentsVisitor.TEXT_MORE_RE,])
        visitor.visit(doc)
        # font
        self._setEditorFonts()
        # get snap shot of initial content to compare with later content to see if document has been modified.
        self.clearState()
        event.Skip()
    # end onDocumentLoaded()

    def _setEditorFonts(self):
        try:
            userPrefs = getApplicationModel().getUserProfile().getPreferences()
            fontName = getNoneString(userPrefs.getUserPreference(IZBlogAppUserPrefsKeys.EDITOR_FONT_NAME, u"")) #$NON-NLS-1$
            fontSize = getNoneString(userPrefs.getUserPreference(IZBlogAppUserPrefsKeys.EDITOR_FONT_SIZE, u"")) #$NON-NLS-1$
            if fontName:
                self._getMshtmlControl().getIHTMLDocument().body.style.fontFamily = fontName
            if fontSize:
                self._getMshtmlControl().getIHTMLDocument().body.style.fontSize = fontSize
        except:
            pass
    # end _setEditorFonts()

    def setXhtmlDocument(self, xhtmlDoc):
        # override to run visitor to remove empty <a> elements
        visitor = ZMshtmlRemoveEmptyElementZDomVisitor([u"a"]) #$NON-NLS-1$
        visitor.visit(xhtmlDoc.getDom())
        ZMshtmlEditControl.setXhtmlDocument(self, xhtmlDoc)
    # end setXhtmlDocument()

    def getXhtmlDocument(self):
        xhtmlDoc = ZMshtmlEditControl.getXhtmlDocument(self)
        # run visitor to convert special marker to a <!-- more --> comment
        zdom = xhtmlDoc.getDom()
        visitor = ZMshtmlExtEntryMarker2CommentZDomVisitor()
        visitor.visit(zdom)
        # run embed wrapper visitor
        visitor = ZMshtmlWrapEmbedElementZDomVisitor()
        visitor.visit(zdom)
        # run visitor to remove empty elements.
        visitor = ZMshtmlRemoveEmptyElementZDomVisitor([u"a"]) #$NON-NLS-1$
        visitor.visit(zdom)
        # remove 'unselectable' attribute
        visitor = ZMshtmlRemoveUnSelectableZDomVisitor()
        visitor.visit(zdom)

        return xhtmlDoc
    # end getXhtmlDocument()

    def canRemoveExtendedEntryMarker(self):
        mshtmlElem = self._getMshtmlControl().getSelectedElement()
        if mshtmlElem and (mshtmlElem.tagName == u"IMG" or mshtmlElem.tagName == u"HR"): #$NON-NLS-1$ #$NON-NLS-2$
            return mshtmlElem.getAttribute(u"id") == ZMshtmlExtendedEntryMarkerProxy.EXTENDED_ENTRY_MARKER_ID #$NON-NLS-1$
        return False
    # end canRemoveExtendedEntryMarker()

    def removeExtendedEntryMarker(self):
        mshtmlElem = self._getMshtmlControl().getSelectedElement(True)
        if mshtmlElem:
            marker = ZMshtmlExtendedEntryMarkerProxy()
            marker.removeExtendedEntry( mshtmlElem )
    # removeExtendedEntryMarker()

    def insertExtendedEntryMarker(self):
        mshtmlElem = self._getMshtmlControl().getSelectedElement(True)
        if mshtmlElem:
            marker = ZMshtmlExtendedEntryMarkerProxy()
            marker.insertExtendedEntry( mshtmlElem )
    # insertExtendedEntryMarker()
# end ZMSHTMLBlogPostEditControl


