from zoundry.appframework.ui.util.clipboardutil import getPngFileFromClipboard
from pywintypes import IID #@UnresolvedImport
from wx.lib.activexwrapper import MakeActiveXClass
from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.global_services import getLoggerService
from zoundry.appframework.ui.actions.mshtmlcontrol import ZMSHTMLActionContext
from zoundry.appframework.ui.actions.mshtmlcontrol import ZMSHTMLControlDelAction
from zoundry.appframework.ui.actions.mshtmlcontrol import ZMSHTMLControlSelectAllAction
from zoundry.appframework.ui.widgets.controls.advanced.mshtml.dndtarget import ZMshtmlDropTarget
from zoundry.appframework.ui.widgets.controls.advanced.mshtml.mshtmlelements import XHTML_BLOCK_LEVEL_ELEMENTS
from zoundry.appframework.ui.widgets.controls.advanced.mshtml.mshtmlvisitors import ZMshtmlAddTableBordersVisitor
from zoundry.appframework.ui.widgets.controls.advanced.mshtml.mshtmlvisitors import ZMshtmlCheckFlashObjectElementVisitor
from zoundry.appframework.ui.widgets.controls.advanced.mshtml.mshtmlvisitors import ZMshtmlFixImgSrcVisitor
from zoundry.appframework.ui.widgets.controls.advanced.mshtml.mshtmlvisitors import ZMshtmlMsOfficeCleanupVisitor
from zoundry.appframework.ui.widgets.controls.advanced.mshtml.mshtmlvisitors import ZMshtmlRemoveCommentsVisitor
from zoundry.appframework.ui.widgets.controls.advanced.mshtml.mshtmlvisitors import ZMshtmlXhtmlConvertVisitor
from zoundry.appframework.ui.widgets.controls.common.acceleratortable import ZAcceleratorEntry
from zoundry.appframework.ui.widgets.controls.common.acceleratortable import ZAcceleratorTable
from zoundry.appframework.ui.widgets.controls.common.panel import ZTransparentPanel
from zoundry.base.exceptions import ZClassNotFoundException
from zoundry.base.exceptions import ZException
from zoundry.base.util.text.textutil import getNoneString
from zoundry.base.util.text.textutil import getSafeString
from zoundry.base.util.text.unicodeutil import convertToUtf8
from zoundry.base.xhtml.xhtmldoc import XHTML_NSS_MAP
from zoundry.base.xhtml.xhtmldoc import ZXhtmlDocument
from zoundry.base.xhtml.xhtmlio import loadXhtmlDocumentFromString
from zoundry.base.xhtml.xhtmlutil import extractTitle
from zoundry.base.xhtml.xhtmlutil import wrapHtmlBody
from zoundry.base.zdom.dom import ZDom
import codecs
import os
import pythoncom
import time
import win32com
import win32com.client #@Reimport
import wx
import zoundry.appframework.util.zravencom

#------------------------------------------------------------
#
# Contains MSHTML related classes.
#
#------------------------------------------------------------


#-----------------------------------------------------------
# MSHTML Control events
#-----------------------------------------------------------
MSHTML_DOCUMENT_LOADED_EVENT = wx.NewEventType()
MSHTML_UPDATE_UI_EVENT = wx.NewEventType()
MSHTML_SELECTION_CHANGE_EVENT = wx.NewEventType()
MSHTML_CONTEXT_MENU_EVENT = wx.NewEventType()
MSHTML_KEYPRESS_EVENT = wx.NewEventType()
MSHTML_CONTENT_MODIFIED_EVENT = wx.NewEventType()
MSHTML_LINK_CLICK_EVENT = wx.NewEventType()
MSHTML_CLICK_EVENT = wx.NewEventType()
MSHTML_DBL_CLICK_EVENT = wx.NewEventType()


class IZMshtmlEvents:
    ZEVT_MSHTML_DOCUMENT_LOADED = wx.PyEventBinder(MSHTML_DOCUMENT_LOADED_EVENT, 1)
    ZEVT_MSHTML_UPDATE_UI = wx.PyEventBinder(MSHTML_UPDATE_UI_EVENT, 1)
    ZEVT_MSHTML_SELECTION_CHANGE = wx.PyEventBinder(MSHTML_SELECTION_CHANGE_EVENT, 1)
    ZEVT_MSHTML_CONTEXT_MENU = wx.PyEventBinder(MSHTML_CONTEXT_MENU_EVENT, 1)
    ZEVT_MSHTML_CONTENT_MODIFIED = wx.PyEventBinder(MSHTML_CONTENT_MODIFIED_EVENT, 1)
    ZEVT_MSHTML_KEYPRESS = wx.PyEventBinder(MSHTML_KEYPRESS_EVENT, 1)
    ZEVT_MSHTML_LINK_CLICK = wx.PyEventBinder(MSHTML_LINK_CLICK_EVENT, 1)
    ZEVT_MSHTML_CLICK = wx.PyEventBinder(MSHTML_CLICK_EVENT, 1)
    ZEVT_MSHTML_DBL_CLICK = wx.PyEventBinder(MSHTML_DBL_CLICK_EVENT, 1)
# end IZMshtmlEvents

class ZMshtmlEvent(wx.PyCommandEvent):

    def __init__(self, eventType, windowID):
        wx.PyCommandEvent.__init__(self, eventType, windowID)
    # end __init__()

    def Clone(self):
        return self.__class__( self.GetEventType(), self.GetId() )
    # end Clone()

# end ZMshtmlEvent

#----------------------------------------------
# Document Loaded event - fired when the document has been loaded and ready for editing.
#----------------------------------------------
class ZMshtmlDocumentLoadedEvent(ZMshtmlEvent):

    def __init__(self, windowID):
        ZMshtmlEvent.__init__(self, MSHTML_DOCUMENT_LOADED_EVENT, windowID)
    # end __init__()

# end ZMshtmlDocumentLoadedEvent

#----------------------------------------------
# UI update event - used to updte toolbar state etc.
#----------------------------------------------
class ZMshtmlUpdateUIEvent(ZMshtmlEvent):

    def __init__(self, windowID):
        ZMshtmlEvent.__init__(self, MSHTML_UPDATE_UI_EVENT, windowID)
    # end __init__()

# end ZMshtmlUpdateUIEvent

#----------------------------------------------
# Selection change event
#----------------------------------------------
class ZMshtmlSelectionChangeEvent(ZMshtmlEvent):

    def __init__(self, windowID):
        ZMshtmlEvent.__init__(self, MSHTML_SELECTION_CHANGE_EVENT, windowID)
    # end __init__()

# end ZMshtmlSelectionChangeEvent

#----------------------------------------------
# Context menu event
#----------------------------------------------
class ZMshtmlContextMenuEvent(ZMshtmlEvent):

    def __init__(self, windowID, parentWindow, xyPoint):
        self.parentWindow = parentWindow
        self.xyPoint = xyPoint
        ZMshtmlEvent.__init__(self, MSHTML_CONTEXT_MENU_EVENT, windowID)
    # end __init__()

    def getParentWindow(self):
        return self.parentWindow
    # end getParentWindow()

    def getXYPoint(self):
        return self.xyPoint
    # end getXYPoint()

    def Clone(self):
        return self.__class__(self.GetId(), self.getParentWindow(), self.getXYPoint())
    # end Clone()

# end ZMshtmlContextMenuEvent()

#----------------------------------------------
# content modified event
#----------------------------------------------
class ZMshtmlContentModifiedEvent(ZMshtmlEvent):
    def __init__(self, windowID):
        ZMshtmlEvent.__init__(self, MSHTML_CONTENT_MODIFIED_EVENT, windowID)
    # end __init__()

    def Clone(self):
        return self.__class__(self.GetId())
    # end Clone()
# end ZMshtmlContentModifiedEvent()

#----------------------------------------------
# key press event
#----------------------------------------------
class ZMshtmlKeyPressEvent(ZMshtmlEvent):

    def __init__(self, windowID):
        ZMshtmlEvent.__init__(self, MSHTML_KEYPRESS_EVENT, windowID)
    # end __init__()

    def Clone(self):
        return self.__class__(self.GetId())
    # end Clone()
# end ZMshtmlKeyPressEvent()

#----------------------------------------------
# single click event
#----------------------------------------------
class ZMshtmlClickEvent(ZMshtmlEvent):

    def __init__(self, windowID):
        ZMshtmlEvent.__init__(self, MSHTML_CLICK_EVENT, windowID)
    # end __init__()

    def Clone(self):
        return self.__class__(self.GetId())
    # end Clone()
# end ZMshtmlClickEvent()

#----------------------------------------------
# double click event
#----------------------------------------------
class ZMshtmlDblClickEvent(ZMshtmlEvent):

    def __init__(self, windowID):
        ZMshtmlEvent.__init__(self, MSHTML_DBL_CLICK_EVENT, windowID)
    # end __init__()

    def Clone(self):
        return self.__class__(self.GetId())
    # end Clone()
# end ZMshtmlDblClickEvent()

#----------------------------------------------
# Link click event
#----------------------------------------------
class ZMshtmlLinkClickEvent(ZMshtmlEvent):

    def __init__(self, windowID, href):
        self.href = href
        ZMshtmlEvent.__init__(self, MSHTML_LINK_CLICK_EVENT, windowID)
    # end __init__()

    def getHref(self):
        return self.href
    # end getHref()

    def Clone(self):
        return self.__class__(self.GetId(), self.getHref())
    # end Clone()

# end ZMshtmlLinkClickEvent()

#
# Load module
#
mshtmlModule = None
try:
    mshtmlModule = win32com.client.gencache.EnsureModule(u"{3050F1C5-98B5-11CF-BB82-00AA00BDCE0B}", 0, 4, 0) #$NON-NLS-1$ @UndefinedVariable
    if mshtmlModule == None:
        raise
except Exception, e:
    raise ZClassNotFoundException(u"MSHTML Type Library", e) #$NON-NLS-1$

#
# Return codes
#
S_OK = 0
S_FALSE = 1

# ------------------------------------------------------------------------------
# Base class impl Microsoft MSHTML component for viewing and editing.
#
# Note:
# mshtmlCtrl typically refers to the ZMSHTMLControl (a wx.Panel)
# mshtmlIHtmlDocumentCtrl refers to the activex mshtml IHtmlDocument contained in the ZMSHTMLControl
#
# FIXME (PJ) Need method: canRemoveHTMLFormatting
# FIXME (PJ) Need method: getSelectHTMLElementToRemoveFormatting (tag)

# ------------------------------------------------------------------------------
class ZMSHTMLControlBase(ZTransparentPanel):

    def __init__(self, parent, id):
        ZTransparentPanel.__init__(self, parent, id)
        self.mshtmlIHtmlDocumentCtrl = None
        self.customDoc = None
        self.uiHandler = None
        self.interactive = False
        self.initialized = False
        self._createWidgets()
        self._layoutWidgets()
        self._bindWidgetEvents()
    # end __init__()

    def SetFocus(self):
        try:
            self.getIHTMLDocument().focus()
        except:
            ZTransparentPanel.SetFocus(self)
    # end SetFocus()

    def _fireMshmlEvent(self, event):
        self.GetEventHandler().AddPendingEvent(event)
    # end _fireMshmlEvent()

    def _createWidgets(self):
        # Make an ActiveX class for the MSHTML HTMLDocument
        theClass = MakeActiveXClass(mshtmlModule.HTMLDocument, eventObj = self)
        # Create an instance of that class
        self.mshtmlIHtmlDocumentCtrl = theClass(self, wx.ID_ANY, style = wx.NO_BORDER)
        # create custom Doc
        self.customDoc = self._createICustomDoc(self.mshtmlIHtmlDocumentCtrl)
        # create UI handler
        if self.customDoc:
            self.uiHandler = self._createIUiHandler(self.mshtmlIHtmlDocumentCtrl, self.customDoc)
            self.customDoc.SetUIHandler(win32com.server.util.wrap(self.uiHandler)) #@UndefinedVariable
    # end _createWidgets()

    def _layoutWidgets(self):
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.mshtmlIHtmlDocumentCtrl, 1, wx.EXPAND | wx.ALL)
        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)
        self.Layout()
    # end _layoutWidgets()

    def _bindWidgetEvents(self):
        pass
    # end _bindWidgetEvents()

    def _createICustomDoc(self, mshtmlIHtmlDocumentCtrl):
        customDoc = mshtmlIHtmlDocumentCtrl._oleobj_.QueryInterface(zoundry.appframework.util.zravencom.IID_ICustomDoc) #@UndefinedVariable
        return customDoc
    # end _createICustomDoc()

    def _createIUiHandler(self, mshtmlIHtmlDocumentCtrl, customDoc): #@UnusedVariable
        uiHandler = ZMshtmlUIHandler(self, mshtmlIHtmlDocumentCtrl)
        return uiHandler
    # end _createUiHandler

    def getIHTMLDocument(self):
        u"""getIHTMLDocument() -> reference to MSHTML IHTMLDocument com object.
        """ #$NON-NLS-1$
        return self.mshtmlIHtmlDocumentCtrl
    # end getIHTMLDocument()

    def setXhtmlDocument(self, zxhtmlDocument, bodyOnly = True):
        u"""setXhtmlDocument(ZXhtmlDocument) -> None
        Sets the content of the view control to the given ZXhtmlDocument.""" #$NON-NLS-1$
        xhtmlString = None
        if bodyOnly:
            body = zxhtmlDocument.getBody()
            xhtmlString = body.serialize()
        else:
            xhtmlString = zxhtmlDocument.serialize(pretty = True)
            if zxhtmlDocument.hasDocTypeString():
                xhtmlString = zxhtmlDocument.getDocTypeString() + u"\n" + xhtmlString #$NON-NLS-1$
        self.setHtmlValue( xhtmlString )
    # end setXhtmlDocument()

    def setHtmlValue(self, html):
        u"""setHtmlValue(string) -> None
        Sets the content of the view control to the given
        HTML string.""" #$NON-NLS-1$
        self._loadStringFromFile(html)
    # end setHtmlValue()

    def getHtmlValue(self):
        htmlStr = u"" #$NON-NLS-1$
        if self.getIHTMLDocument() and self.getIHTMLDocument().body:
            htmlStr = u"<html>%s</html>" % self.getIHTMLDocument().body.outerHTML #$NON-NLS-1$
        else:
            htmlStr = u"<html><body><p></p></body></html>" #$NON-NLS-1$
        return htmlStr
    # end getHtmlValue()

    def setFile(self, filename):
        u"""setFile(filename) -> None
        Sets the content of the view control to a .html file.""" #$NON-NLS-1$
        self._loadFile(filename)
    # end setFile()

    def _loadStringFromFile(self, html):
        # MSHTML control requires a <head> and <title> element
        title = getNoneString( extractTitle(html) )
        if not title or html.find(u"<html") == -1: #$NON-NLS-1$
            # case where only the body content is given or the content did not have non-empty <head> and <title> elems.
            # try and create wrapper around the body. Eg:  <html><head><title>ZoundryDocument</title></head><body> CONTENT </body> </html>
            html = wrapHtmlBody(html, u"ZoundryDocument") #$NON-NLS-1$

        # note: \r\n must be replace with \n. Otherwise, in <pre> blocks, the \r' will show up as an extra line.
        html = html.replace(u"\r\n", u"\n")  #$NON-NLS-1$  #$NON-NLS-2$
        # For the test-harness to work, hard code temp dir
        tmpDir = u"c:/temp" #$NON-NLS-1$
        if getApplicationModel():
            userProfile = getApplicationModel().getUserProfile()
            tmpDir = userProfile.getTempDirectory()
        d = str(time.time())

        # For Microsoft Internet Explorer Version 9 (and above?) the file extension for the temporary file must have
        # a ".html" (previously a ".xhtml") extension in order for the blog post to load successfully into the ActiveX
        # mshtml IHtmlDocument. Otherwise, the blog posts will appear to be mal-formatted during previews and fail to
        # load correctly during editing.
        #
        # Chuah TC    23 December 2013
        #
        #fname = os.path.join(tmpDir, u"_z_raven_mshtml_%s_tmp.xhtml" % d) #$NON-NLS-1$
        fname = os.path.join(tmpDir, u"_z_raven_mshtml_%s_tmp.html" % d) #$NON-NLS-1$


        tmpFile = codecs.open(fname, u"w") #$NON-NLS-1$
        try:
            # write the utf-8 byte order marker for wintel platforms.
            tmpFile.write(codecs.BOM_UTF8)
            tmpFile.write( convertToUtf8(html) )
            tmpFile.close()
            self._loadFile(fname)
        finally:
            tmpFile.close()
    # end _loadStringFromFile()

    def _loadFile(self, filename):
        # reset states
        self._setInitialized(False)
        self._setInteractive(False)
        persist = self.mshtmlIHtmlDocumentCtrl._oleobj_.QueryInterface(pythoncom.IID_IPersistFile) #@UndefinedVariable
        persist.Load(filename)
    # end _loadURL()

    def getIHTMLSelectionObject(self):
        # returns current selection object or None if not available.
        return self.getIHTMLDocument().selection
    # end getIHTMLSelectionObject()

    def hasTextSelection(self):
        u"""hasTextSelection() -> bool
        Returns true if any text has been selected.
        """ #$NON-NLS-1$
        selectionObj = self.getIHTMLSelectionObject()
        return selectionObj and selectionObj.type == u"Text" #$NON-NLS-1$
    # end hasTextSelection()

    def getSelectedElement(self, includeNoneType = False):
        u"""getSelectedElement(bool=False) -> IHTMLElement
        Returns currently selected element. If argument is True, and
        there is no text selection, then the element under the caret is returned.
        """ #$NON-NLS-1$
        elementObj = None
        try:
            selectionObj = self.getIHTMLSelectionObject()
            if selectionObj:
                type = selectionObj.type
                if type == u"Control": #$NON-NLS-1$
                    controlRange = selectionObj.createRange()
                    if controlRange:
                        elementObj = controlRange.item(0)
                elif type == u"Text": #$NON-NLS-1$
                    textRange = selectionObj.createRange()
                    if textRange:
                        elementObj = textRange.parentElement()
                elif includeNoneType and type == u"None": #$NON-NLS-1$
                    # add support to get the element under the cursor/caret
                    textRange = selectionObj.createRange()
                    if textRange:
                        elementObj = textRange.parentElement()
                #end if
            #end if
        except:
            pass
        return elementObj
    # end getSelectedElement

    def getSelectedTextRange(self, includeNoneType = False):
        u"""getSelectedTextRange(bool=False) -> IHTMLTextRange
        Returns currently text range for the current selection.
        If argument is True, and there is no selection, then the text range under the caret is returned.
        """ #$NON-NLS-1$
        textRange = None
        try:
            selectionObj = self.getIHTMLSelectionObject()
            if selectionObj:
                type = selectionObj.type
                if type == u"Text": #$NON-NLS-1$
                    textRange = selectionObj.createRange()
                #end if
                elif includeNoneType and type == u"None": #$NON-NLS-1$
                    # add support to get the element under the cursor/caret
                    textRange = selectionObj.createRange()
            #end if
        except:
            pass
        return textRange
    #end getSelectedTextRange

    def getSelectedText(self, includeNoneType = False):
        u"""getSelectedText(bool=False) -> string
        Returns currently text string for the current selection.
        If argument is True, and there is no selection, then the text  under the caret is returned.
        """ #$NON-NLS-1$
        textRange = self.getSelectedTextRange(includeNoneType)
        if textRange:
            return textRange.text
        else:
            return None
    # end getSelectedText()

    def _isInteractive(self):
        return self.interactive
    # end _isInteractive

    def _setInteractive(self, bInteractive):
        self.interactive = bInteractive
    # end _setInteractive()

    def _isInitialized(self):
        return self.initialized
    # end _isInitialized()

    def _setInitialized(self, bInitialized):
        self._disposeIHTMLDocument()
        if bInitialized:
            self._initializeIHTMLDocument()
        self.initialized = bInitialized
    # end _setInitialized()

    def _getDocumentReadyStateValue(self):
        # Returns the state at which point the document is ready for reading or editing.
        return u"complete" #$NON-NLS-1$
    # end _getDocumentReadyStateValue()

    def Ononreadystatechange(self):
        state = self.getIHTMLDocument().readyState
        if state == u"interactive": #$NON-NLS-1$
            self._setInteractive(True)
        if state == self._getDocumentReadyStateValue() and not self._isInitialized():
            self._setInitialized(True)
            event = ZMshtmlDocumentLoadedEvent(self.GetId())
            self._fireMshmlEvent(event)
            event = ZMshtmlUpdateUIEvent(self.GetId())
            self._fireMshmlEvent(event)
    # end Ononreadystatechange()

    def Ononselectionchange(self):
        event = ZMshtmlUpdateUIEvent(self.GetId())
        self._fireMshmlEvent(event)

        event = ZMshtmlSelectionChangeEvent(self.GetId())
        self._fireMshmlEvent(event)
    # end Ononselectionchange()

    def onShowContextMenu(self, x, y):
        pt1 = wx.Point(x, y)
        pt2 = self.getIHTMLDocument().ScreenToClient(pt1)
        event = ZMshtmlContextMenuEvent(self.GetId(), self, pt2)
        self._fireMshmlEvent(event)
    # end onShowContextMenu()

    def _initializeIHTMLDocument(self):
        # called after a document has been loaded and in ready state.
        pass
    # end _initializeMshtml()

    def _disposeIHTMLDocument(self):
        # called when a document is no longed used.
        pass
    # end _disposeIHTMLDocument()

    def execCommand(self, command, param = None):
        if command and param and self._isInitialized():
            self.getIHTMLDocument().execCommand(command, False, param)
        elif command and self._isInitialized():
            self.getIHTMLDocument().execCommand(command)
    # end execCommand()

    def queryCommandEnabled(self, command):
        try:
            if command and self._isInitialized():
                return self.getIHTMLDocument().queryCommandEnabled(command)
        except:
            pass
        return False
    # end queryCommandEnabled()

    def queryCommandValue(self, command):
        if command and self._isInitialized():
            return self.getIHTMLDocument().queryCommandValue(command)
        else:
            return None
    # end queryCommandValue

    def queryCommandState(self, command):
        if command and self._isInitialized():
            return self.getIHTMLDocument().queryCommandState(command)
        else:
            return False
    # end queryCommandState()

# end ZMSHTMLControl


# ------------------------------------------------------------------------------
# Read only imple of mshtml control.
# ------------------------------------------------------------------------------
class ZMSHTMLViewControl(ZMSHTMLControlBase):
    u"""
    MSHTML based  html viewer with support for function callbacks.
    To have a link callback a function in your python class, include a
    href in the format py::function().

    For example, <a href="py::foo()">foo</a> and <a href="py::bar('hello',3)">foo</a>

    Next, set the function call back in the mshtml control. Eg:

    class MyLinkFunctions:
        def foo():
            # do some work and
            # return True if the IZMshtmlEvents.ZEVT_MSHTML_LINK_CLICK should be propergated. False otherwise.
            return True

        def bar(stringArg, intArg):
            # do some work ...
            # if you expect stringArg to be utf8, then run convertToUnicode(stringArg) before using it.
            return False

    htmlViewer = ZMSHTMLViewControl(parentWindow)
    handler = MyLinkFunctions()
    htmlViewer.setLinkCallback(handler)

    """ #$NON-NLS-1$

    def __init__(self, parent, id = wx.ID_ANY):
        ZMSHTMLControlBase.__init__(self, parent, id)
        # optional function callback object to process py::function methods.
        self.linkClickCallback = None
        self.Bind(IZMshtmlEvents.ZEVT_MSHTML_LINK_CLICK, self.onInternalLinkClick, self)
    # end __init__()

    def _initializeIHTMLDocument(self):
        visitor = ZMshtmlFixImgSrcVisitor()
        visitor.visit( self.getIHTMLDocument() )
        ZMSHTMLControlBase._initializeIHTMLDocument(self)
    # end _initializeMshtml()

    def setLinkCallback(self, callback):
        self.linkClickCallback = callback
    # end setLinkCallback()

    def onInternalLinkClick(self, event):
        # handle special cases where we need to call back pyMethod.
        skipEvent = True
        if self.linkClickCallback is not None:
            href = event.getHref()
            if href.lower().startswith(u"py::"): #$NON-NLS-1$
                theFunctionCall = u"self.linkClickCallback.%s" % href[4:] #$NON-NLS-1$
                try:
                    skipEvent = eval(theFunctionCall)
                except:
                    print u"Function eval error: %s" % theFunctionCall #$NON-NLS-1$
        # let the other event handlers process event as well.
        if skipEvent is not None and skipEvent == True:
            event.Skip()
    # end onInternalLinkClick()

    def Ononclick(self):
        ele = self.getIHTMLDocument().activeElement
        if ele and ele.tagName == u"A": #$NON-NLS-1$
            href = ele.getAttribute(u"href") #$NON-NLS-1$
            event = ZMshtmlLinkClickEvent(self.GetId(), href)
            self._fireMshmlEvent(event)
        return False
    # end Ononclick()

# end ZMSHTMLViewControl



# ------------------------------------------------------------------------------
# Accelerator table for the MSHTML control.
# ------------------------------------------------------------------------------
class ZMSHTMLControlAcceleratorTable(ZAcceleratorTable):

    def __init__(self, editControl):
        self.editControl = editControl

        # Cannot contribute to this accelerator table - it is built-in only to
        # support the DEL key.
        ZAcceleratorTable.__init__(self, None)
    # end __init__()

    def _createActionContext(self):
        return ZMSHTMLActionContext(self.editControl)
    # end _createActionContext()

    def _loadAdditionalEntries(self):
        return [
            ZAcceleratorEntry(wx.ACCEL_NORMAL, wx.WXK_DELETE, ZMSHTMLControlDelAction()),
            ZAcceleratorEntry(wx.ACCEL_CTRL, ord(u'A'), ZMSHTMLControlSelectAllAction()) #$NON-NLS-1$
        ]
    # end _loadAdditionalEntries()

# end ZMSHTMLControlAcceleratorTable


# ------------------------------------------------------------------------------
# Editable impl of mshtml control.
# ------------------------------------------------------------------------------
class ZMSHTMLControl(ZMSHTMLControlBase):

    def __init__(self, parent, id = wx.ID_ANY):
        ZMSHTMLControlBase.__init__(self, parent, id)

        # originalHtmlContent:
        # html content when the document is first loaded.
        # this will be used to compare with current content to see if the
        # content is dirty/modified. (Ideally we should use the MSHTML Edit Designer or IPersistStream to query this)
        self.originalHtmlContent = None
    # end __init__()

    def _createWidgets(self):
        self.acceleratorTable = ZMSHTMLControlAcceleratorTable(self)
        self.SetAcceleratorTable(self.acceleratorTable)
        ZMSHTMLControlBase._createWidgets(self)
    # end _createWidgets()

    def _bindWidgetEvents(self):
        ZMSHTMLControlBase._bindWidgetEvents(self)
        self.acceleratorTable.bindTo(self)
    # end _bindWidgetEvents

    def _setOriginalHtmlContent(self, htmlContent):
        self.originalHtmlContent = htmlContent
    # end _setoriginalHtmlContent

    def _getOriginalHtmlContent(self):
        return self.originalHtmlContent
    # end _getOriginalHtmlContent

    def _initializeIHTMLDocument(self):
        # override to set edit mode on and run clean up visitors
        #self.execCommand(u"MultipleSelection", True) #$NON-NLS-1$
        self.execCommand(u"LiveResize", True) #$NON-NLS-1$
        self._runStandardCleanupVisitors()
        # Document has been loaded. Take a snapshot of the document content.
        self._createInitialContentSnapshot()
    # end _initializeMshtml()

    def Ononreadystatechange(self):
        # override base to set design mode on 'complete' and then wait for design mode to be ready.
        # prior to firing initialize()
        state = self.getIHTMLDocument().readyState
        mode = self.getIHTMLDocument().designMode
        if state == u"interactive": #$NON-NLS-1$
            self._setInteractive(True)
        elif mode != u"On" and state == self._getDocumentReadyStateValue() and not self._isInitialized(): #$NON-NLS-1$
            # basic doc has loaded. Now, set design mode = On.
            self.getIHTMLDocument().designMode = u"On" #$NON-NLS-1$
        elif mode == u"On" and state == self._getDocumentReadyStateValue() and not self._isInitialized(): #$NON-NLS-1$
            # doc is in design mode and it has finished loading.
            self._setInitialized(True)
            event = ZMshtmlDocumentLoadedEvent(self.GetId())
            self._fireMshmlEvent(event)
            event = ZMshtmlUpdateUIEvent(self.GetId())
            self._fireMshmlEvent(event)
    # end Ononreadystatechange()

    def _disposeIHTMLDocument(self):
        # called when a document is no longed used.
        self._setOriginalHtmlContent(None)
    # end _disposeIHTMLDocument()

    def _createInitialContentSnapshot(self):
        if self.getIHTMLDocument() and self.getIHTMLDocument().body:
            self._setOriginalHtmlContent( self.getIHTMLDocument().body.outerHTML )
        else:
            self._setOriginalHtmlContent(u"" )#$NON-NLS-1$
    # end _createInitialContentSnapshot()

    def _isModified(self):
        rval = False
        if self._getOriginalHtmlContent() is not None and self.getIHTMLDocument() and self.getIHTMLDocument().body:
            currHtmlContent = self.getIHTMLDocument().body.outerHTML
            rval = currHtmlContent != self._getOriginalHtmlContent()
        return rval
    # end _isModified()

    def _createIUiHandler(self, mshtmlIHtmlDocumentCtrl, customDoc): #@UnusedVariable
        uiHandler = ZMshtmlEditUIHandler(self, mshtmlIHtmlDocumentCtrl)
        return uiHandler
    # end _createUiHandler()

    def _runMshtmlVisitors(self, visitorList):
        # Runs list of visitors.
        for visitor in visitorList:
            visitor.visit( self.getIHTMLDocument() )
    # end _runMshtmlVisitors()

    def _runStandardCleanupVisitors(self):
        visitors = []
        visitors.append( ZMshtmlXhtmlConvertVisitor() )
        visitors.append( ZMshtmlRemoveCommentsVisitor(ZMshtmlRemoveCommentsVisitor.FRAGMENT_PATTERNS) )
        visitors.append( ZMshtmlMsOfficeCleanupVisitor() )
        visitors.append( ZMshtmlCheckFlashObjectElementVisitor() )
        visitors.append( ZMshtmlAddTableBordersVisitor() )
        visitors.append( ZMshtmlFixImgSrcVisitor() )
        #visitors.append( ZMshtmlSetUnSelectableOnVisitor() )
        self._runMshtmlVisitors(visitors)
    # end _runStandardCleanupVisitors()

    def _runImgCleanupVisitor(self):
        visitors = []
        visitors.append( ZMshtmlFixImgSrcVisitor() )
        self._runMshtmlVisitors(visitors)
    # end _runImgCleanupVisitor

    def getHtmlValue(self):
        # override to first run clean up.
        self._runStandardCleanupVisitors()
        return ZMSHTMLControlBase.getHtmlValue(self)
    # end  getHtmlValue()

    def _fireContentModified(self):
        event = ZMshtmlContentModifiedEvent( self.GetId() )
        self._fireMshmlEvent( event )
    # end _fireContentModified

    def onDeleteKey(self):
        self.execCommand(u"Delete") #$NON-NLS-1$
    # end onDeleteKey()

    def Ononkeypress(self):
        event = ZMshtmlKeyPressEvent( self.GetId() )
        self._fireMshmlEvent( event )
        self._fireContentModified()
        return True
    # end Ononkeypress

    def Ononclick(self):
        event = ZMshtmlClickEvent( self.GetId() )
        self._fireMshmlEvent( event )
        return False
    # Ononclick()

    def Onondblclick(self):
        event = ZMshtmlDblClickEvent( self.GetId() )
        self._fireMshmlEvent( event )
        return False
    # Onondblclick()

    def onDnDDrop(self, xhtmlDoc):
        self.insertHtml(xhtmlDoc)
    # end onDnDDrop()

    def execCommand(self, command, param = None):
        # re-map some html format tags
        if command and command == u"FormatHtmlTag" and param:  #$NON-NLS-1$
            # FIXME (PJ) add mapping for strong, italic, underline
            if param == u"ol": #$NON-NLS-1$
                command  = u"InsertOrderedList" #$NON-NLS-1$
            elif param == u"ul": #$NON-NLS-1$
                command  = u"InsertUnorderedList" #$NON-NLS-1$
            elif param == u"strike" or param == u"del": #$NON-NLS-1$ #$NON-NLS-2$
                command  = u"StrikeThrough" #$NON-NLS-1$
            elif param == u"blockquote": #$NON-NLS-1$
                command  = u"Indent" #$NON-NLS-1$
            elif param == u"hr": #$NON-NLS-1$
                command  = u"InsertHorizontalRule" #$NON-NLS-1$
            elif param == u"b": #$NON-NLS-1$
                command  = u"Bold" #$NON-NLS-1$
            elif param == u"i": #$NON-NLS-1$
                command  = u"Italic" #$NON-NLS-1$
            elif param == u"u": #$NON-NLS-1$
                command  = u"Underline" #$NON-NLS-1$


        hasText = self.hasTextSelection()
        if hasText and command and command == u"InsertOrderedList": #$NON-NLS-1$
            self._applyListMarkup(u"ol")  #$NON-NLS-1$
        elif hasText and command and command == u"InsertUnorderedList":  #$NON-NLS-1$
            self._applyListMarkup(u"ul")  #$NON-NLS-1$
        elif hasText and command and command == u"Indent":  #$NON-NLS-1$
            self._applyBlockQuote()  #$NON-NLS-1$
        elif hasText and command and command == u"StrikeThrough":  #$NON-NLS-1$
            self._applyStrikeThrough()  #$NON-NLS-1$
        elif hasText and command and command == u"Underline":  #$NON-NLS-1$
            self._applyUnderline()  #$NON-NLS-1$
        elif command and command == u"FormatHtmlTag" and param:  #$NON-NLS-1$
            self._markupSelection(param)
        else:
            ZMSHTMLControlBase.execCommand(self, command, param)
            # Assume exec command modifies the document.
            self._fireContentModified()
    # end execCommand()

    def _getContentBodyNode(self, content):
        # returns zdom ZNode representing xhtml:body given html string, ZDom or ZHtmlDocument object.
        bodyNode = None
        if isinstance(content, basestring):
            content = loadXhtmlDocumentFromString(content)
        if isinstance(content, ZXhtmlDocument):
            bodyNode = content.getBody()
        elif isinstance(content, ZDom):
            content.setNamespaceMap(XHTML_NSS_MAP)
            bodyNode = content.selectSingleNode(u"//xhtml:body") #$NON-NLS-1$
        return bodyNode
    # end _getContentBodyNode()

    def _serializeChildren(self, zdomNode):
        rval = u"" #$NON-NLS-1$
        nodes = zdomNode.selectNodes(u"child::*") #$NON-NLS-1$
        for node in nodes:
            rval = rval + node.serialize()
        return rval
    # end _serializeChildren()

    def _insertBlockLevelHTML(self, ele, htmlFrag, where):
        # inserts html at a block level element.
        blockEle = self._findBlockLevelElement(ele)
        if blockEle:
            # force insert to 'beforeEnd' (incase 'afterEnd' is requested) where elem is at top <body> level.
            # (also, default value for 'where' is 'beforeEnd'.
            if blockEle.tagName == u"BODY" or not where: #$NON-NLS-1$
                where = u"beforeEnd" #$NON-NLS-1$
            blockEle.insertAdjacentHTML(where, htmlFrag)
    # end _insertBlockLevelHTML

    def _insertHtmlFragment(self, html, where = None):
        htmlFrag = u'''<!DOCTYPE/><HTML><BODY><!-- StartFragment-->''' + html + u''' <!-- EndFragment--></BODY></HTML>''' #$NON-NLS-2$ #$NON-NLS-1$
        ele = self.getSelectedElement()
        if ele:
            self._insertBlockLevelHTML(ele, htmlFrag, where )
        else:
            tr = self.getSelectedTextRange(True)
            # if position is under caret and where = 'afterEnd', then paste at end of container element.
            if tr and where and where == u"afterEnd" : #$NON-NLS-1$
                self._insertBlockLevelHTML(tr.parentElement(), htmlFrag, where )
            elif tr:
                tr.pasteHTML(htmlFrag)

        self._runStandardCleanupVisitors()
        self._fireContentModified()
    # end _insertHtmlFragment()

    def _insertText(self, text):
        if not text:
            return
        tr = self.getSelectedTextRange(True)
        ele = self.getSelectedElement()
        if tr:
            tr.text = text
        elif ele:
            ele.innerText = text
        self._fireContentModified()
    # end _insertText

    def _applyStrikeThrough(self):
        currValue = ZMSHTMLControlBase.queryCommandValue(self, u"StrikeThrough") #$NON-NLS-1$
        ZMSHTMLControlBase.execCommand(self, u"StrikeThrough", None) #$NON-NLS-1$
        newValue = ZMSHTMLControlBase.queryCommandValue(self, u"StrikeThrough") #$NON-NLS-1$
        if currValue and newValue == currValue:
            # StrikeThrough value was True prior to execCommand, but after the command, the value
            # is still the same. This should be false if strike thru should be removed.
            tr = self.getSelectedTextRange(True)
            if tr:
                ele = tr.parentElement()
                if ele and ele.tagName == u"DEL": #$NON-NLS-1$
                    # apply to currenly selected element
                    ele.outerHTML = ele.innerHTML
                    self._fireContentModified()
    # end _applyStrikeThrough()

    def _applyUnderline(self):
        currValue = ZMSHTMLControlBase.queryCommandValue(self, u"Underline") #$NON-NLS-1$
        ZMSHTMLControlBase.execCommand(self, u"Underline", None) #$NON-NLS-1$
        newValue = ZMSHTMLControlBase.queryCommandValue(self, u"Underline") #$NON-NLS-1$
        if currValue and newValue == currValue:
            # Underline value was True prior to execCommand, but after the command, the value
            # is still the same. This should be false if underline should be removed.
            # Remove CSS style.
            tr = self.getSelectedTextRange()
            if tr:
                ele = tr.parentElement()
                if ele and ele.style and u"underline" == ele.style.textDecoration: #$NON-NLS-1$
                    ele.style.textDecoration = u"none" #$NON-NLS-1$
                    self._fireContentModified()
    # end _applyUnderline()

    def _applyBlockQuote(self):
        self._markupSelection(u"blockquote") #$NON-NLS-1$

    def _applyListMarkup(self, listTag):
        handleLocallly = False
        tr = self.getSelectedTextRange()
        if tr:
            ele = tr.parentElement()
            if ele and tr.text == ele.innerText and ele.tagName != u"BODY": #$NON-NLS-1$
                pass
            elif ele and ele.outerHTML == tr.htmlText:
                pass
            else:
                html = tr.htmlText.strip(u"\n\r\ ") #$NON-NLS-1$
                # handle locally if selection is a text fragment (i.e does not have <P> etc)
                handleLocallly = html and html[0] != u"<" #$NON-NLS-1$

        if handleLocallly:
            # listTag = ou | ul on a text selection (instead of whole para)
            listTag = getSafeString(listTag).lower()
            if listTag not in (u"ol", u"ul"): #$NON-NLS-1$ #$NON-NLS-2$
                listTag = u"ul" #$NON-NLS-1$
            openTag = u"<%s><li>" % listTag #$NON-NLS-1$
            closeTag = u"</li></%s>" % listTag #$NON-NLS-1$
            self._wrapSelection(openTag, closeTag)

        elif listTag in (u"ol", u"ul"): #$NON-NLS-1$ #$NON-NLS-2$
            # Let IE handle it. IE will take care of handling multiple paras into a multline bullet
            if listTag == u"ol":             #$NON-NLS-1$
                ZMSHTMLControlBase.execCommand(self, u"InsertOrderedList", None) #$NON-NLS-1$
            else:
                ZMSHTMLControlBase.execCommand(self, u"InsertUnOrderedList", None) #$NON-NLS-1$
            # Assume exec command modifies the document.
            self._fireContentModified()
    # end _applyListMarkup()

    def _markupSelection(self, xhtmlTag, cssStyle = None):
        # wrap given xhtml tag around current selection.
        if getNoneString(cssStyle):
            openTag = u"""<%s style="%s">""" % (xhtmlTag, cssStyle) #$NON-NLS-1$
        else:
            openTag = u"""<%s>""" % xhtmlTag #$NON-NLS-1$
        closeTag = u"""</%s>""" % xhtmlTag #$NON-NLS-1$
        self._wrapSelection(openTag, closeTag)
    # end _markupSelection()

    def _wrapSelection(self, openTag, closeTag):
        tr = self.getSelectedTextRange()
        if tr:
            ele = tr.parentElement()
            if ele and tr.text == ele.innerText and ele.tagName != u"BODY": #$NON-NLS-1$
                # apply to currenly selected element
                html = u"%s%s%s" %(openTag, ele.outerHTML, closeTag) #$NON-NLS-1$
                tr.pasteHTML(html)
            elif ele and ele.outerHTML == tr.htmlText:
                ele.innerHTML = u"%s%s%s" %(openTag, tr.text, closeTag) #$NON-NLS-1$
            else:
                html = u"%s%s%s" %(openTag, getSafeString(tr.htmlText), closeTag) #$NON-NLS-1$
                tr.pasteHTML(html)
            self._fireContentModified()
        else:
            frag = u"%sInsertText%s" % (openTag, closeTag) #$NON-NLS-1$
            self._insertHtmlFragment(frag)

    # end  _wrapSelection()

#
#    # Permit applying of html formatting (block quote etc) on Div and P tags only
#    def canApplyHtmlFormatting(self):
#        selObj = self.getSelectedElement()
#        if (selObj):
#            return True
#        return False

    def _isBlockLevelElement(self, ele):
        u"""Returns true of the given element is a XHTML block level element.""" #$NON-NLS-1$
        if not ele or not ele.tagName:
            return False
        tag = ele.tagName.lower().strip()
        if tag in XHTML_BLOCK_LEVEL_ELEMENTS:
            return True
        else:
            return False
    # end _isBlockLevelElement

    def _findBlockLevelElement(self, ele):
        while ele.tagName != u"BODY" and not self._isBlockLevelElement(ele): #$NON-NLS-1$
            ele = ele.parentElement
        if ele.tagName == u"BODY" or self._isBlockLevelElement(ele): #$NON-NLS-1$
            return ele
        else:
            return None
    # end _findBlockLevelElement()

    def insertImage(self, filepath):
        ele = self.getSelectedElement(True)
        if ele:
            try:
                where = u"afterEnd" #$NON-NLS-1$
                if ele.tagName == u"BODY" or self._isBlockLevelElement(ele): #$NON-NLS-1$
                    where = u"beforeEnd" #$NON-NLS-1$

                imgNode = self.getIHTMLDocument().createElement(u"img") #$NON-NLS-1$
                # QI for IHTMLElement
                ele = win32com.client.Dispatch(ele, IID(u'{3050F1D8-98B5-11CF-BB82-00AA00BDCE0B}')) #$NON-NLS-1$
                ele.insertAdjacentElement(where,imgNode)
                # QI for IHTMLImgElement
                imgNode = win32com.client.Dispatch(imgNode, IID(u'{3050F240-98B5-11CF-BB82-00AA00BDCE0B}')) #$NON-NLS-1$
                imgNode.src = filepath
                bodyElement = self.getIHTMLDocument().body
                # QI for IHTMLBodyElement
                bodyElement = win32com.client.Dispatch(bodyElement, IID(u'{3050F1D8-98B5-11CF-BB82-00AA00BDCE0B}')) #$NON-NLS-1$
                controlRange = bodyElement.createControlRange()
                controlRange.add(imgNode)
                controlRange.select()
                self._fireContentModified()
            except:
                self.execCommand(u"InsertImage", filepath) #$NON-NLS-1$

    def insertHtml(self, content, where = None):
        bodyNode = self._getContentBodyNode(content)
        if bodyNode:
            html = self._serializeChildren(bodyNode)
            self._insertHtmlFragment(html, where)
    # end insertHtml()

    def paste(self, content = None, asXhtml = False):
        if content and asXhtml:
            # paste given content as xhtml
            self.insertHtml(content)
        elif content and isinstance(content, basestring):
            # paste given content as plain text
            self._insertText(content)
        else:
            # paste from clipboard
            # 1st, check if its an image
            pngFilepath = getPngFileFromClipboard(copyToResourceStore=True)
            if pngFilepath:
                self.execCommand(u"InsertImage", pngFilepath) #$NON-NLS-1$
            else:
                self.execCommand(u"Paste") #$NON-NLS-1$
            # clean up any code such as ms office
            self._runStandardCleanupVisitors()
    # end paste()

    def selectAll(self):
        self.execCommand(u"SelectAll") #$NON-NLS-1$
    #end SelectAll()

    def selectNone(self):
        try:
            selectionObj = self.getIHTMLSelectionObject()
            if selectionObj:
                selectionObj.empty()
            #end if
        except:
            self.exception()
    # end SelectNone()

# end ZMSHTMLControl

CONTEXT_MENU_DEFAULT = 2
CONTEXT_MENU_CONTROL = 4
CONTEXT_MENU_TABLE = 8
CONTEXT_MENU_TEXTSELECT = 16
CONTEXT_MENU_ANCHOR = 48
CONTEXT_MENU_UNKNOWN= 32

# --------------------------------------------------------------
#  Standard UI handler imple.
# --------------------------------------------------------------
class ZMshtmlUIHandler:
    _com_interfaces_ = [zoundry.appframework.util.zravencom.IID_IDocHostUIHandler] #@UndefinedVariable
    _public_methods_ = [u"ShowContextMenu", u"GetDropTarget"] #$NON-NLS-1$ #$NON-NLS-2$

    def __init__(self, mshtmlCtrl, mshtmlIHtmlDocumentCtrl):
        self.mshtmlCtrl = mshtmlCtrl
        self.mshtmlIHtmlDocumentCtrl = mshtmlIHtmlDocumentCtrl
        self.dropTarget = None
    # end __init__()

    # create an IDropTarget object
    def GetDropTarget(self, oldDropTarget): #@UnusedVariable
        return oldDropTarget
    #end GetDropTarget

    def ShowContextMenu(self, dwID, x, y, cmdTarget, dispElement): #@UnusedVariable
        self.mshtmlCtrl.onShowContextMenu(x,y)
        return S_OK
    #end ShowContextMenu

# end ZMshtmlUIHandler


# --------------------------------------------------------------
#  Standard UI handler impl for the editable mshtml control.
# --------------------------------------------------------------
class ZMshtmlEditUIHandler(ZMshtmlUIHandler):

    def __init__(self, mshtmlCtrl, mshtmlIHtmlDocumentCtrl):
        ZMshtmlUIHandler.__init__(self, mshtmlCtrl, mshtmlIHtmlDocumentCtrl)
        self.dropTarget = None
    # end __init__()

    # create an IDropTarget object
    def GetDropTarget(self, oldDropTarget): #@UnusedVariable
        if self.dropTarget != None:
            return self.dropTarget
        try:
            oldDropTargetDispatch = oldDropTarget.QueryInterface(pythoncom.IID_IDropTarget) #@UndefinedVariable
            dropTarget = ZMshtmlDropTarget(self.mshtmlCtrl, oldDropTargetDispatch)
            self.dropTarget = win32com.server.util.wrap(dropTarget, pythoncom.IID_IDropTarget) #@UndefinedVariable
            return self.dropTarget
        except Exception, e:
            ze = ZException(rootCause = e)
            getLoggerService().exception(ze)
            return oldDropTarget
    #end GetDropTarget

#end ZMshtmlEditUIHandler
