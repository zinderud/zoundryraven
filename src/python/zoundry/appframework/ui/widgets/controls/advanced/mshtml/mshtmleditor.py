from zoundry.appframework.ui.util.clipboardutil import hasClipboardBitmap
from zoundry.appframework.ui.widgets.controls.advanced.mshtml.mshtmltablectx import ZMshtmlEditControlTableContext
from zoundry.base.css.csscolor import ZCssColor
from zoundry.base.css.cssfont import ZCssFontInfo
from zoundry.base.util.text.textutil import getNoneString
from zoundry.appframework.ui.widgets.controls.advanced.htmleditcontrol import IZXHTMLEditControlStyleContext
from zoundry.appframework.ui.events.editcontrolevents import ZEditControlClickEvent
from zoundry.appframework.ui.events.editcontrolevents import ZEditControlDoubleClickEvent
from zoundry.appframework.ui.util.clipboardutil import getTextFromClipboard
from zoundry.appframework.ui.widgets.controls.advanced.editcontrol import IZEditControl
from zoundry.appframework.ui.widgets.controls.advanced.editcontrol import IZRichTextEditControl
from zoundry.appframework.ui.widgets.controls.advanced.editcontrol import IZTextEditControl
from zoundry.appframework.ui.widgets.controls.advanced.htmleditcontrol import IZXHTMLEditControl
from zoundry.appframework.ui.widgets.controls.advanced.htmleditcontrol import ZBaseXHTMLEditControl
from zoundry.appframework.ui.widgets.controls.advanced.htmleditcontrol import ZXHTMLEditControlSelection
from zoundry.appframework.ui.widgets.controls.advanced.mshtml.mshtmlcontrol import IZMshtmlEvents
from zoundry.appframework.ui.widgets.controls.advanced.mshtml.mshtmlcontrol import ZMSHTMLControl
from zoundry.appframework.ui.widgets.controls.advanced.mshtml.mshtmlelements import createIZXhtmlElementFromIHTMLElement
from zoundry.appframework.ui.widgets.controls.advanced.mshtml.mshtmlfindreplacectx import ZMshtmlEditControlFindReplaceTextContext
from zoundry.appframework.ui.widgets.controls.advanced.mshtml.mshtmlimglinkctx import ZMshtmlEditControlImageContext
from zoundry.appframework.ui.widgets.controls.advanced.mshtml.mshtmlimglinkctx import ZMshtmlEditControlLinkContext
from zoundry.appframework.ui.widgets.controls.advanced.mshtml.mshtmlspellcheckctx import ZMshtmlEditControlSpellCheckContext
from zoundry.appframework.ui.util.uiutil import getRootWindowOrDialog
from zoundry.appframework.ui.util.uiutil import fireUIExecEvent
from zoundry.appframework.ui.util.uiutil import ZMethodRunnable
import wx

# ------------------------------------------------------------------------------
# The basic WYSIWSY HTML Editor : IZXHTMLEditControl impl. based on IE MSHTML control.
# ------------------------------------------------------------------------------
class ZMshtmlEditControl(ZBaseXHTMLEditControl) :

    RICHTEXT_FORMAT_COMMANDS = {}
    RICHTEXT_FORMAT_COMMANDS[IZRichTextEditControl.ZCAPABILITY_BOLD] = u"Bold" #$NON-NLS-1$
    RICHTEXT_FORMAT_COMMANDS[IZRichTextEditControl.ZCAPABILITY_ITALIC] = u"Italic" #$NON-NLS-1$
    RICHTEXT_FORMAT_COMMANDS[IZRichTextEditControl.ZCAPABILITY_UNDERLINE] = u"Underline" #$NON-NLS-1$
    RICHTEXT_FORMAT_COMMANDS[IZRichTextEditControl.ZCAPABILITY_STRIKETHRU] = u"StrikeThrough" #$NON-NLS-1$
    RICHTEXT_FORMAT_COMMANDS[IZRichTextEditControl.ZCAPABILITY_ALIGN_LEFT] = u"JustifyLeft" #$NON-NLS-1$
    RICHTEXT_FORMAT_COMMANDS[IZRichTextEditControl.ZCAPABILITY_ALIGN_RIGHT] = u"JustifyRight" #$NON-NLS-1$
    RICHTEXT_FORMAT_COMMANDS[IZRichTextEditControl.ZCAPABILITY_ALIGN_CENTER] = u"JustifyCenter" #$NON-NLS-1$
    RICHTEXT_FORMAT_COMMANDS[IZRichTextEditControl.ZCAPABILITY_JUSTIFY] = u"JustifyFull" #$NON-NLS-1$
    RICHTEXT_FORMAT_COMMANDS[IZRichTextEditControl.ZCAPABILITY_ORDERED_LIST] = u"InsertOrderedList" #$NON-NLS-1$
    RICHTEXT_FORMAT_COMMANDS[IZRichTextEditControl.ZCAPABILITY_UNORDERED_LIST] = u"InsertUnorderedList" #$NON-NLS-1$
    RICHTEXT_FORMAT_COMMANDS[IZRichTextEditControl.ZCAPABILITY_INDENT] = u"Indent" #$NON-NLS-1$
    RICHTEXT_FORMAT_COMMANDS[IZRichTextEditControl.ZCAPABILITY_OUTDENT] = u"Outdent" #$NON-NLS-1$
    RICHTEXT_FORMAT_COMMANDS[IZRichTextEditControl.ZCAPABILITY_FONT_NAME] = u"FontName" #$NON-NLS-1$
    RICHTEXT_FORMAT_COMMANDS[IZRichTextEditControl.ZCAPABILITY_FONT_SIZE] = u"FontSize" #$NON-NLS-1$
    RICHTEXT_FORMAT_COMMANDS[IZRichTextEditControl.ZCAPABILITY_COLOR] = u"ForeColor" #$NON-NLS-1$
    RICHTEXT_FORMAT_COMMANDS[IZRichTextEditControl.ZCAPABILITY_BACKGROUND] = u"BackColor" #$NON-NLS-1$
    

    def __init__(self, parent):
        ZBaseXHTMLEditControl.__init__(self, parent)
        self.mshtmlCtrl = None
        self.linkContext = None
        self.imageContext = None
        self.tableContext = None
        self._createWidgets()
        self._layoutWidgets()
        self._bindWidgetEvents()
    # end __init__()

    def _getCapabilityIdList(self):
        u"""_getCapabilityIdList() -> list
        Returns list of supported capabilites.""" #$NON-NLS-1$
        rval = ZBaseXHTMLEditControl._getCapabilityIdList(self)

        # editor capabilities
        rval.append(IZEditControl.ZCAPABILITY_CUT)
        rval.append(IZEditControl.ZCAPABILITY_COPY)
        rval.append(IZEditControl.ZCAPABILITY_PASTE)
        rval.append(IZEditControl.ZCAPABILITY_UNDO)
        rval.append(IZEditControl.ZCAPABILITY_REDO)
        rval.append(IZEditControl.ZCAPABILITY_SELECT_ALL)
        rval.append(IZEditControl.ZCAPABILITY_SELECT_NONE)
        # text editor capabilities
        rval.append(IZTextEditControl.ZCAPABILITY_FIND_TEXT)
        rval.append(IZTextEditControl.ZCAPABILITY_FINDREPLACE)
        rval.append(IZTextEditControl.ZCAPABILITY_SPELLCHECK)
        # rich text editor capabilities
        rval.append(IZRichTextEditControl.ZCAPABILITY_FONT_NAME)
        rval.append(IZRichTextEditControl.ZCAPABILITY_FONT_SIZE)
        rval.append(IZRichTextEditControl.ZCAPABILITY_COLOR)
        rval.append(IZRichTextEditControl.ZCAPABILITY_BACKGROUND)

        rval.append(IZRichTextEditControl.ZCAPABILITY_BOLD)
        rval.append(IZRichTextEditControl.ZCAPABILITY_ITALIC)
        rval.append(IZRichTextEditControl.ZCAPABILITY_UNDERLINE)
        rval.append(IZRichTextEditControl.ZCAPABILITY_STRIKETHRU)
        rval.append(IZRichTextEditControl.ZCAPABILITY_ALIGN_LEFT)
        rval.append(IZRichTextEditControl.ZCAPABILITY_ALIGN_RIGHT)
        rval.append(IZRichTextEditControl.ZCAPABILITY_ALIGN_CENTER)
        rval.append(IZRichTextEditControl.ZCAPABILITY_JUSTIFY)
        rval.append(IZRichTextEditControl.ZCAPABILITY_ORDERED_LIST)
        rval.append(IZRichTextEditControl.ZCAPABILITY_UNORDERED_LIST)
        rval.append(IZRichTextEditControl.ZCAPABILITY_INDENT)
        rval.append(IZRichTextEditControl.ZCAPABILITY_OUTDENT)
        # html domain capabilities
        rval.append(IZXHTMLEditControl.ZCAPABILITY_PASTE_HTML)
        rval.append(IZXHTMLEditControl.ZCAPABILITY_INSERT_IMAGE)
        rval.append(IZXHTMLEditControl.ZCAPABILITY_EDIT_IMAGE)
        rval.append(IZXHTMLEditControl.ZCAPABILITY_INSERT_LINK)
        rval.append(IZXHTMLEditControl.ZCAPABILITY_EDIT_LINK)
        rval.append(IZXHTMLEditControl.ZCAPABILITY_INSERT_TABLE)
        rval.append(IZXHTMLEditControl.ZCAPABILITY_EDIT_TABLE)
        rval.append(IZXHTMLEditControl.ZCAPABILITY_INSERT_HTML)
        rval.append(IZXHTMLEditControl.ZCAPABILITY_FORMAT_HTML)
        rval.append(IZXHTMLEditControl.ZCAPABILITY_SCHEMA_AWARE)

        return rval
    # end _getCapabilityIdList()

    def SetFocus(self):
        self._getMshtmlControl().SetFocus()
    # end SetFocus()

    def _getMshtmlControl(self):
        return self.mshtmlCtrl
    # end _getMshtmlControl()

    def _createWidgets(self):
        self.mshtmlCtrl = ZMSHTMLControl(self, wx.NewId())
    # end _createWidgets()

    def _layoutWidgets(self):
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.mshtmlCtrl, 1, wx.EXPAND)
        self.SetAutoLayout(True)
        self.SetSizer(box)
        self.Layout()
    # end _layoutWidgets()

    def _bindWidgetEvents(self):
        self.Bind(IZMshtmlEvents.ZEVT_MSHTML_UPDATE_UI, self.onUpdateUI, self._getMshtmlControl())
        self.Bind(IZMshtmlEvents.ZEVT_MSHTML_SELECTION_CHANGE, self.onSelectionChange, self._getMshtmlControl())
        self.Bind(IZMshtmlEvents.ZEVT_MSHTML_CONTEXT_MENU, self.onContextMenu, self._getMshtmlControl())
        self.Bind(IZMshtmlEvents.ZEVT_MSHTML_CLICK, self.onClick, self._getMshtmlControl())
        self.Bind(IZMshtmlEvents.ZEVT_MSHTML_DBL_CLICK, self.onDoubleClick, self._getMshtmlControl())
        self.Bind(IZMshtmlEvents.ZEVT_MSHTML_CONTENT_MODIFIED, self.onContentModified, self._getMshtmlControl())
        #self.Bind(IZMshtmlEvents.ZEVT_MSHTML_KEYPRESS, self.onKeyPress, self._getMshtmlControl())

        rootWindow = getRootWindowOrDialog(self)
        self.Bind(wx.EVT_ACTIVATE, self.onActivate, rootWindow)
    # end _bindWidgetEvents()

    def onActivate(self, event):
        if event.GetActive():
            fireUIExecEvent(ZMethodRunnable(self.onActivateStageTwo), self)
        event.Skip()
    # end onActivate()

    def onActivateStageTwo(self):
        rootWindow = getRootWindowOrDialog(self)
        focusWindow = rootWindow.FindFocus()
        if focusWindow == self.mshtmlCtrl.getIHTMLDocument():
            self.mshtmlCtrl.SetFocus()
    # end onActivateStageTwo()

    def onUpdateUI(self, event): #@UnusedVariable
        self._fireUpdateUIEvent()
    # end onUpdateUI()

    def onContentModified(self, event): #@UnusedVariable
        if self._getMshtmlControl()._getOriginalHtmlContent() and self._getMshtmlControl()._isModified():
            # Note: current mshtml code for _isModified is to compare the current content
            # with the original content instead of checking for key strokes or looking at the changes at
            # document object model. Hence, for now, fire "content-modified" event to notify parents
            # and call mshtml::_setOriginalHtmlContent(None) so that subsequent calls to mshtml_isModified()
            # return false. Bottom line: _getMshtmlControl()._isModified() should be invoked only once.
            self._getMshtmlControl()._setOriginalHtmlContent(None)
            self._fireContentModifiedEvent()
    # end onContentModified

    def onKeyPress(self, event): #@UnusedVariable
        pass
    # end onKeyPress

    def onSelectionChange(self, event): #@UnusedVariable
        selection = self.getCurrentSelection()
        self._fireSelectionChangeEvent(selection)
    # end onSelectionChange()

    def onContextMenu(self, event):
        # FIXME (PJ) SEL_CHANGE context menu - support for querying current selection.
        self._fireContextMenuEvent(event.getParentWindow(), event.getXYPoint())
    # end onContextMenu()

    def onClick(self, event): #@UnusedVariable
        event = ZEditControlClickEvent(self.GetId(), self)
        self._fireEvent(event)
    # end onDoubleClick

    def onDoubleClick(self, event): #@UnusedVariable
        event = ZEditControlDoubleClickEvent(self.GetId(), self)
        self._fireEvent(event)
    # end onDoubleClick

    def getCurrentSelection(self):
        mshtmlElem = self._getMshtmlControl().getSelectedElement(True)
        selectedText = None
        izXhtmlElementImpl = None
        if mshtmlElem:
            selectedText = self._getMshtmlControl().getSelectedText()
            # izXhtmlElementImpl is either IZXhtmlElement, IZXhtmlLink or IZXhtmlImage
            izXhtmlElementImpl = createIZXhtmlElementFromIHTMLElement(mshtmlElem)

        styleCtx = ZMshtmlEditControlStyleContext(self._getMshtmlControl(), mshtmlElem, self._getMshtmlControl().getSelectedTextRange() )
        selection = ZMshtmlEditControlSelection(selectedText, izXhtmlElementImpl, styleCtx)
        return selection
    # end getCurrentSelection

    def setValue(self, value):
        self._getMshtmlControl().setHtmlValue(value)
    # end setValue()

    def getValue(self):
        return self._getMshtmlControl().getHtmlValue()
    # end getValue()

    def clearState(self):
        self._getMshtmlControl()._createInitialContentSnapshot()
    # end clearState()

    def canCut(self):
        return self._getMshtmlControl().queryCommandEnabled(u"Cut") #$NON-NLS-1$
    # end canCut()

    def cut(self):
        self._getMshtmlControl().execCommand(u"Cut") #$NON-NLS-1$
    # end cut()

    def canCopy(self):
        bCopy = self._getMshtmlControl().queryCommandEnabled(u"Copy") #$NON-NLS-1$
        # Feb 23, 2005.
        # work around bug where IE returns Copy state enabled when the control receives focus.
        # (eg: place the cursor on the document and Copy is enabled.) (seen since ZBW build 57).
        bCopy = self.canCut() and bCopy
        return bCopy
    # end canCopy()

    def copy(self):
        self._getMshtmlControl().execCommand(u"Copy") #$NON-NLS-1$
    # end copy()

    def canPaste(self):
        rval = self._getMshtmlControl().queryCommandEnabled(u"Paste") #$NON-NLS-1$
        if not rval:
            # test for clipboard image
            rval = hasClipboardBitmap()
        return rval
    # end canPaste()

    def paste(self):
        self._getMshtmlControl().paste() #$NON-NLS-1$
    # end paste()

    def canPasteXhtml(self):
        return self.canPaste()
    # end canPasteXhtml()

    def pasteXhtml(self):
        content = getTextFromClipboard()
        return self._getMshtmlControl().paste(content, True)
    # end pasteXhtml()

    def canInsertXhtml(self):
        return True
    # end canInsertXhtml

    def insertXhtml(self, xhtmlString): #@UnusedVariable
        return self._getMshtmlControl().insertHtml(xhtmlString, u"afterEnd") #$NON-NLS-1$
    # end insertXhtml

    def canSelectAll(self):
        return True
    # end canSelectAll()

    def selectAll(self):
        self._getMshtmlControl().selectAll()
    # end selectAll()

    def selectNone(self):
        self._getMshtmlControl().selectNone()
    # selectNone()

    def canUndo(self):
        return self._getMshtmlControl().queryCommandEnabled(u"Undo") #$NON-NLS-1$
    # end canUndo()

    def undo(self):
        self._getMshtmlControl().execCommand(u"Undo") #$NON-NLS-1$
    # end undo()

    def canRedo(self):
        return self._getMshtmlControl().queryCommandEnabled(u"Redo") #$NON-NLS-1$
    # end canRedo()

    def redo(self):
        self._getMshtmlControl().execCommand(u"Redo") #$NON-NLS-1$
    # end redo()

    def isFormattingEnabled(self, capabilityId):
        if ZMshtmlEditControl.RICHTEXT_FORMAT_COMMANDS.has_key(capabilityId):
            return  True
        return False
    # end isFormattingEnabled()

    def getFormattingState(self, capabilityId):
        if ZMshtmlEditControl.RICHTEXT_FORMAT_COMMANDS.has_key(capabilityId):
            return self._getMshtmlControl().queryCommandState( ZMshtmlEditControl.RICHTEXT_FORMAT_COMMANDS[capabilityId] )
        return False
    # end getFormattingState()

    def applyFormatting(self, capabilityId, customData): #@UnusedVariable
        if ZMshtmlEditControl.RICHTEXT_FORMAT_COMMANDS.has_key(capabilityId):
            return self._getMshtmlControl().execCommand( ZMshtmlEditControl.RICHTEXT_FORMAT_COMMANDS[capabilityId] )
        elif IZXHTMLEditControl.ZCAPABILITY_FORMAT_HTML == capabilityId:
            return self._getMshtmlControl().execCommand(u"FormatHtmlTag", customData) #$NON-NLS-1$
    # end applyFormatting()

    def getLinkContext(self):
        if self.linkContext is None:
            self.linkContext = ZMshtmlEditControlLinkContext( self )
        return self.linkContext
    # end getLinkContext

    def getImageContext(self):
        if self.imageContext is None:
            self.imageContext = ZMshtmlEditControlImageContext( self )
        return self.imageContext
    # end getImageContext

    def getTableContext(self):
        if self.tableContext is None:
            self.tableContext = ZMshtmlEditControlTableContext( self )
        return self.tableContext
    # end getTableContext()

    def createSpellCheckContext(self):
        return ZMshtmlEditControlSpellCheckContext(self)
    # end createSpellCheckContext()

    def createFindReplaceContext(self):
        selectedText = self._getMshtmlControl().getSelectedText()
        return ZMshtmlEditControlFindReplaceTextContext(self, selectedText)
    # end createFindReplaceContext()

# end ZMshtmlEditControl


# ------------------------------------------------------------------------------
# base implementation of a html element selection.
# ------------------------------------------------------------------------------
class ZMshtmlEditControlSelection(ZXHTMLEditControlSelection):

    def __init__(self, text, izelement, styleContext):
        ZXHTMLEditControlSelection.__init__(self, text, izelement)
        self.styleContext = styleContext
    # end __init__()


    def getStyleContext(self):
        return self.styleContext
    # end getStyleContext()

# end ZMshtmlEditControlSelection


# ------------------------------------------------------------------------------
# MSHTML impl. CSS style context of the current element or selection
# ------------------------------------------------------------------------------
class ZMshtmlEditControlStyleContext(IZXHTMLEditControlStyleContext):

    def __init__(self, mshtmlControl, mshtmlIHTMLElement, mshtmlIHTMLTextRange):
        self.mshtmlControl = mshtmlControl
        self.mshtmlIHTMLElement = mshtmlIHTMLElement
        self.mshtmlIHTMLTextRange = mshtmlIHTMLTextRange
        self.cssColor = None
        self.cssBgColor = None
        self.fontInfo = None
        self.hasCSSFontSize = False
        self.hasCSSFontName = False
        self.firstTime = True
    # end __init__

    def _getElement(self):
        elem = None
        if self.mshtmlIHTMLTextRange:
            elem = self.mshtmlIHTMLTextRange.parentElement()
        else:
            elem = self.mshtmlIHTMLElement
        return elem
    # end _getElement()

    def _getProperties(self):
        if not self.firstTime:
            return
        self.firstTime = False
        elem = self._getElement()
        if not elem or not elem.style:
            return

#        print "---"
#        print "IN", len(elem.innerText)
#        print "TR", len(self.mshtmlIHTMLTextRange.text)
#        print "IN}%s{" % elem.innerText
#        print "TR}%s{" % self.mshtmlIHTMLTextRange.text
        bgColor = None
        color = None
        fontSize = None
        fontName = None
        self.hasCSSFontSize = False
        self.hasCSSFontName = False

        # walk up the ladder and build css font properties
        while (elem != None):
            if not self.hasCSSFontSize and getNoneString(elem.style.fontSize):
                self.hasCSSFontSize = True
            if not self.hasCSSFontName and getNoneString(elem.style.fontFamily):
                self.hasCSSFontName = True

            if not bgColor:
                bgColor = getNoneString( elem.style.backgroundColor )
            if not color:
                color = getNoneString(elem.style.color)
            if not fontName:
                fontName = self.mshtmlControl.queryCommandValue(u"FontName") #$NON-NLS-1$
            if not fontSize:
                fontSize = getNoneString(elem.style.fontSize)
            if elem.tagName == u"BODY": #$NON-NLS-1$
                break
            if (color and bgColor and fontSize and fontName):
                break
            elem = elem.parentElement
        # end while
        if color:
            self.cssColor = ZCssColor(color)
        if bgColor:
            self.cssBgColor = ZCssColor(bgColor)
        self.fontInfo = ZCssFontInfo()
        self.fontInfo.setFontName(fontName)
        self.fontInfo.setFontSize(fontSize)
    # end _getProperties()

    def applyStyle(self, cssFontInfo, cssColor, cssBgColor):
        elem = self._getElement()
        if not elem or not elem.style or not self.mshtmlIHTMLTextRange:
            return

        removeFont = self.getFontInfo().getFontName() and not cssFontInfo.getFontName()
        removeSize = self.getFontInfo().getFontSize() and not cssFontInfo.getFontSize()
        removeColor = self.getColor() and not cssColor
        removeBackground = self.getBackgroundColor() and not cssBgColor
        handled = True
        if self.mshtmlIHTMLTextRange.text == elem.innerText and elem.tagName != u"BODY" and elem.tagName != u"P": #$NON-NLS-2$ #$NON-NLS-1$
            # apply to currently selected element
            if removeFont:
                # reset font name
                elem.style.fontFamily = u'' #$NON-NLS-1$
            elif cssFontInfo.getFontName() and cssFontInfo.getFontName() != self.getFontInfo().getFontName():
                # set new font size
                elem.style.fontFamily = cssFontInfo.getFontName()

            if removeSize:
                # reset font size
                elem.style.fontSize = u'' #$NON-NLS-1$
            elif cssFontInfo.getFontSize() and cssFontInfo.getFontSize() != self.getFontInfo().getFontSize():
                # set new font size
                elem.style.fontSize = cssFontInfo.getFontSize()

            if removeColor:
                elem.style.color = u"" #$NON-NLS-1$
            elif cssColor and self.getColor() and cssColor.getCssColor() != self.getColor().getCssColor():
                elem.style.color = cssColor.getCssColor()
            elif cssColor:
                elem.style.color = cssColor.getCssColor()

            if removeBackground:
                elem.style.backgroundColor = u"" #$NON-NLS-1$
            elif cssBgColor and self.getBackgroundColor() and cssBgColor.getCssColor() != self.getBackgroundColor().getCssColor():
                elem.style.backgroundColor = cssBgColor.getCssColor()
            elif cssBgColor:
                elem.style.backgroundColor = cssBgColor.getCssColor()
            # Remove SPAN tag if there is no style applied.
            if elem.tagName == u"SPAN" and not ( getNoneString(elem.style.cssText) or getNoneString(elem.className) ): #$NON-NLS-1$
                elem.outerHTML = elem.innerHTML

        elif self.mshtmlIHTMLTextRange.htmlText:
            # apply on the text range
            s = u"" #$NON-NLS-1$
            if elem.outerHTML == self.mshtmlIHTMLTextRange.htmlText:
                s = elem.innerHTML
            else:
                s = self.mshtmlIHTMLTextRange.htmlText

            style = u''    #$NON-NLS-1$
            if cssFontInfo.getFontName() and cssFontInfo.getFontName() != self.getFontInfo().getFontName():
                style = style + u"font-family:" + cssFontInfo.getFontName() + u"; " #$NON-NLS-2$ #$NON-NLS-1$
            if cssFontInfo.getFontSize() and cssFontInfo.getFontSize() != self.getFontInfo().getFontSize():
                style = style + u"font-size:" + cssFontInfo.getFontSize() + u"; " #$NON-NLS-2$ #$NON-NLS-1$
            if cssColor and (not self.getColor() or ( cssColor.getCssColor() != self.getColor().getCssColor() ) ):
                style = style + u"color:" + cssColor.getCssColor() + u"; " #$NON-NLS-2$ #$NON-NLS-1$
            if cssBgColor and (not self.getBackgroundColor() or (cssBgColor.getCssColor() != self.getBackgroundColor().getCssColor()) ):
                style = style + u"background-color:" + cssBgColor.getCssColor() + u"; " #$NON-NLS-2$ #$NON-NLS-1$
            if style:
                html = u'<SPAN style="%s" >%s</SPAN>' % (style, s) #$NON-NLS-1$
                self.mshtmlIHTMLTextRange.pasteHTML(html)
        else:
            handled = False
        if handled:
            self.mshtmlControl._fireContentModified()
    # end _setProperties

    def getFontInfo(self):
        if not self.fontInfo:
            self._getProperties()
        return self.fontInfo
    # end getFontInfo

    def setFontInfo(self, fontInfo):
        self.fontInfo = fontInfo
        self.applyStyle(fontInfo, None, None)
    # end setFontInfo

    def getColor(self):
        if not self.cssColor:
            self._getProperties()
        return self.cssColor
    # end getColor

    def setColor(self, cssColor):
        self.cssColor = cssColor
        self.applyStyle(None, cssColor, None)
    # end setColor

    def getBackgroundColor(self):
        if not self.cssBgColor:
            self._getProperties()
        return self.cssBgColor
    # end getBackgroundColor

    def setBackgroundColor(self, cssColor):
        self.cssBgColor = cssColor
        self.applyStyle(None, None, cssColor)
    # end setBackgroundColor

# end ZMshtmlEditControlStyleContext
