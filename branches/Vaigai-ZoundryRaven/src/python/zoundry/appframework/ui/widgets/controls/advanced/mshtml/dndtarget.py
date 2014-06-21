from winerror import S_OK
from zoundry.appframework.constants import IZAppServiceIDs
from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.services.dnd.dndimpl import ZDnDContext
from zoundry.appframework.services.dnd.dndsource import ZCompositeDnDSource
from zoundry.appframework.services.dnd.handlers.htmlhandler import ZHtmlDnDHandler
from zoundry.appframework.ui.util.uiutil import getRootWindowOrDialog
from zoundry.appframework.ui.widgets.controls.advanced.mshtml.dndreaders import ZBlogPostDnDSourceReader
from zoundry.appframework.ui.widgets.controls.advanced.mshtml.dndreaders import ZHDropDnDSourceReader
from zoundry.appframework.ui.widgets.controls.advanced.mshtml.dndreaders import ZHtmlDnDSourceReader
from zoundry.appframework.ui.widgets.controls.advanced.mshtml.dndreaders import ZUrlDnDSourceReader
from zoundry.appframework.util import zravencom
from zoundry.base.xhtml.xhtmlio import loadXhtmlDocumentFromString
import pythoncom
import win32clipboard
import win32com #@UnusedImport

#IID_IDisplayServices = u"{3050F69D-98B5-11CF-BB82-00AA00BDCE0B}" #$NON-NLS-1$

# TYMED (Type of Storage Medium) values
TYMED_HGLOBAL     = 1
TYMED_FILE        = 2
TYMED_ISTREAM     = 4
TYMED_ISTORAGE    = 8
TYMED_GDI         = 16
TYMED_MFPICT      = 32
TYMED_ENHMF       = 64
TYMED_NULL        = 0

#Drop Effect enumeration
DROPEFFECT_NONE   = 0
DROPEFFECT_COPY   = 1
DROPEFFECT_MOVE   = 2
DROPEFFECT_LINK   = 4
DROPEFFECT_SCROLL = 0x80000000

DVASPECT_CONTENT    = 1
DVASPECT_THUMBNAIL  = 2
DVASPECT_ICON       = 4
DVASPECT_DOCPRINT   = 8

DATADIR_GET = 1
DATADIR_SET = 2


def getDnDService():
    return getApplicationModel().getService(IZAppServiceIDs.DND_SERVICE_ID)
# end getDnDService()


# ------------------------------------------------------------------------------
# MShtml editor drop target impl.
# ------------------------------------------------------------------------------
class ZMshtmlDropTarget:
    _com_interfaces_ = [pythoncom.IID_IDropTarget] #@UndefinedVariable
    _public_methods_ = [u"Drop", u"DragEnter", u"DragOver", u"DragLeave"] #$NON-NLS-3$ #$NON-NLS-2$ #$NON-NLS-1$ #$NON-NLS-4$

    def __init__(self, mshtml, oldDropTarget):
        self.mshtml = mshtml
        self.oldDropTarget = oldDropTarget
        self.handled = False
        self.dndSource = None
        self.handlers = None
        self.dndSourceReaders = self._loadDnDSourceReaders()
        self.htmlHandler = ZHtmlDnDHandler()
    # end __init__()

    def _loadDnDSourceReaders(self):
        readers = []
        readers.append(ZHtmlDnDSourceReader())
        readers.append(ZUrlDnDSourceReader())
        readers.append(ZBlogPostDnDSourceReader())
        readers.append(ZHDropDnDSourceReader())
        return readers
    # end _loadDnDSourceReaders()

    # Make sure only image files we support are being dragged.
    def DragEnter(self, dataObject, keyState, point, effect):
        # On drag enter, raise the window to the top
        rootWindow = getRootWindowOrDialog(self.mshtml)
        rootWindow.Raise()
        self.mshtml.SetFocus()
        self.mshtml.selectNone()

        self.handlers = None
        self.handled = False
        self.internalDataObject = None
        self.dndSource = self._createDnDSource(dataObject)

        # Now that we have the DnD source, check if it is supported.
        # Note: Always let mshtml handle HTML sources
        reffect = None
        if self.htmlHandler.canHandle(self.dndSource):
            reffect = self._DoOldDragEnter(dataObject, keyState, point, effect)
        elif self._isDnDSourceSupported(self.dndSource):
            self.handled = True
            reffect = DROPEFFECT_COPY
        else:
            reffect = self._DoOldDragEnter(dataObject, keyState, point, effect)

        return reffect
    # end DragEnter()

    # Old behavior (use the old drop target to handle the drag)
    def _DoOldDragEnter(self, dataObject, keyState, point, effect):
        try:
            reffect = self.oldDropTarget.DragEnter(dataObject, keyState, point, effect)
        except:
            reffect = DROPEFFECT_NONE
        return reffect
    # end _DoOldDragEnter

    def _getIHtmlDocument(self):
        return self.mshtml.getIHTMLDocument()
    # end _getIHtmlDocument()

    def DragOver(self, keyState, point, effect):
        # If the drag is being handled by a Zoundry DnD handler
        if self.handled:
            # Convert from absolute (screen) coords to relative (frame) coords
            (absX, absY) = point
            (relX, relY) = self.mshtml.ScreenToClientXY(absX, absY)
            
            # Some custom C++/COM code to set the caret position in MSHTML
            zravencom.SetMSHTMLCaretPosition(self._getIHtmlDocument()._oleobj_, relX, relY) #@UndefinedVariable

            effect = DROPEFFECT_COPY
        else:
            effect = self.oldDropTarget.DragOver(keyState, point, effect)

        return effect
    # end DragOver()

    def Drop(self, dataObject, keyState, point, effect):
        # If we are handling the drop, then do it.
        if self.handled:
            handler = self.handlers[0]
            context = ZDnDContext(self.mshtml)
            xhtmlDoc = handler.handle(self.dndSource, context)
            if xhtmlDoc is not None:
                if isinstance(xhtmlDoc, str) or isinstance(xhtmlDoc, unicode):
                    xhtmlDoc = loadXhtmlDocumentFromString(xhtmlDoc)
                self.mshtml.onDnDDrop(xhtmlDoc)
            return S_OK

        # If we are not handling it, then let IE do the drop.
        return self.oldDropTarget.Drop(dataObject, keyState, point, effect)
    #end Drop

    def DragLeave(self):
        # If we were handling the drag, then null out our state and return S_OK
        if self.handled:
            self.handled = False
            self.handlers = None
            self.dndSource = None
            return S_OK

        # If we weren't handling the drag, then let IE do whatever it does.
        try:
            return self.oldDropTarget.DragLeave()
        except Exception:
            return S_OK
    # end DragLeave()

    def _createDnDSource(self, dataObject):
        enum = dataObject.EnumFormatEtc()
        formatEtcs = []
        next = enum.Next()
        while next:
            for formatEtc in next:
                formatEtcs.append(formatEtc)
            next = enum.Next()

        #self._printFormatEtcs(formatEtcs)

        dndSource = ZCompositeDnDSource()
        for reader in self.dndSourceReaders:
            formatEtc = (reader.getClipboardFormat(), None, DVASPECT_CONTENT, -1, TYMED_HGLOBAL)
            if formatEtc in formatEtcs:
                stgMedium = dataObject.GetData(formatEtc)
                dndSource.addSource(reader.readDnDSource(stgMedium))

        return dndSource
    # end _createDnDSource()

    def _printFormatEtcs(self, formatEtcs):
        for (format, a, b, c, d) in formatEtcs: #@UnusedVariable
            try:
                print u'Format:', format, win32clipboard.GetClipboardFormatName(format) #$NON-NLS-1$
            except:
                print u'Format not found: ', format #$NON-NLS-1$
    # end _printFormatEtcs()

    def _isDnDSourceSupported(self, dndSource):
        if dndSource is None:
            return False
        self.handlers = getDnDService().getMatchingHandlers(dndSource)
        return len(self.handlers) > 0
    # end _isDnDSourceSupported()

#end ZMshtmlDropTarget
