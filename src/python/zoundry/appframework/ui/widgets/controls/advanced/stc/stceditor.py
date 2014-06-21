from wx.stc import *
from zoundry.appframework.global_services import getResourceRegistry
from zoundry.appframework.services.validation.xhtmlvalidation import IZXhtmlValidationListener
from zoundry.appframework.services.validation.xhtmlvalidation import ZXhtmlValidationMessage
from zoundry.appframework.ui.util.clipboardutil import getTextFromClipboard
from zoundry.appframework.ui.util.uiutil import ZMethodRunnable
from zoundry.appframework.ui.util.uiutil import fireUIExecEvent
from zoundry.appframework.ui.util.xhtmlvalidationutil import ZXhtmlSchemaUiUtil
from zoundry.appframework.ui.widgets.controls.advanced.editcontrol import IZEditControl
from zoundry.appframework.ui.widgets.controls.advanced.editcontrol import IZRichTextEditControl
from zoundry.appframework.ui.widgets.controls.advanced.editcontrol import IZTextEditControl
from zoundry.appframework.ui.widgets.controls.advanced.htmleditcontrol import IZXHTMLEditControl
from zoundry.appframework.ui.widgets.controls.advanced.htmleditcontrol import ZBaseXHTMLEditControl
from zoundry.appframework.ui.widgets.controls.advanced.htmlvalidationlist import ZXhtmlValidationReportListViewContentProvider
from zoundry.appframework.ui.widgets.controls.advanced.htmlvalidationlist import ZXhtmlValidationReportView
from zoundry.appframework.ui.widgets.controls.advanced.stc.stcfindreplacectx import ZStyledXhtmlEditControlFindReplaceTextContext
from zoundry.appframework.ui.widgets.controls.advanced.stc.stcsupport import ZStcAutoCompleteHandler
from zoundry.appframework.ui.widgets.controls.advanced.stc.stcsupport import ZStcLocator
from zoundry.base.css.csscolor import ZCssColor
from zoundry.base.xhtml.xhtmlio import loadXhtmlDocumentFromString
import wx #@Reimport

#================================================================
# REF:
# http://www.yellowbrain.com/stc/index.html
# http://www.flamerobin.org/dokuwiki/doku.php?id=wiki:stc
#
#================================================================

#------------------------------
# Margin marker IDs
#------------------------------
class IZZStyledTextCtrlMarkers:
    MARKER_NONE = 0
    MARKER_OK = 1
    MARKER_WARN = 2
    MARKER_ERROR = 3
    MARKER_ARROW = 4
# end IZZStyledTextCtrlMarkers


#------------------------------
# Scintilla xhtml text editor
#------------------------------
class ZStyledXhtmlEditControl(ZBaseXHTMLEditControl, IZXhtmlValidationListener):

    def __init__(self, parent):
        ZBaseXHTMLEditControl.__init__(self, parent)

        self.stcCtrl = StyledTextCtrl(self, wx.NewId(), style = wx.NO_BORDER | wx.NO_FULL_REPAINT_ON_RESIZE)
        self.stcCtrl.CmdKeyAssign(ord(u'+'), STC_SCMOD_CTRL, STC_CMD_ZOOMIN) #$NON-NLS-1$
        self.stcCtrl.CmdKeyAssign(ord(u'-'), STC_SCMOD_CTRL, STC_CMD_ZOOMOUT) #$NON-NLS-1$

        self.autocompleteLocator = ZStcLocator(self.stcCtrl)
        self.autocompleteHandler = ZStcAutoCompleteHandler()
        self.autocompleteLocatorInfo = None

        self.validationReportProvider = ZXhtmlValidationReportListViewContentProvider()
        self.validationView = ZXhtmlValidationReportView(self, self.validationReportProvider)

        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.stcCtrl, 3, wx.EXPAND)
        box.Add(self.validationView, 2, wx.EXPAND | wx.ALL, 4)
        self.SetAutoLayout(True)
        self.SetSizer(box)
        self.Layout()

        self.contentLoaded = False
        self._setLexer()
        self._setMargins()
        self._setMarkers()
        self._setStyles()
        self._bindStcEvents()
        self._bindWidgetEvents()
    # end __init__()

    def _getCapabilityIdList(self):
        rval = ZBaseXHTMLEditControl._getCapabilityIdList(self)
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

        # rich text editor capabilities
        rval.append(IZRichTextEditControl.ZCAPABILITY_BOLD)
        rval.append(IZRichTextEditControl.ZCAPABILITY_ITALIC)
        rval.append(IZRichTextEditControl.ZCAPABILITY_UNDERLINE)
        rval.append(IZRichTextEditControl.ZCAPABILITY_STRIKETHRU)

        # html domain capabilities
        rval.append(IZXHTMLEditControl.ZCAPABILITY_SCHEMA_AWARE)
        rval.append(IZXHTMLEditControl.ZCAPABILITY_VALIDATE_HTML)
        rval.append(IZXHTMLEditControl.ZCAPABILITY_TIDY_HTML)
        rval.append(IZXHTMLEditControl.ZCAPABILITY_PASTE_HTML)
#        rval.append(IZXHTMLEditControl.ZCAPABILITY_INSERT_IMAGE)
#        rval.append(IZXHTMLEditControl.ZCAPABILITY_INSERT_LINK)
        return rval
    # end _getCapabilityIdList()

    def _bindWidgetEvents(self):
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onValidationItemActivated, self.validationView.getListControl())
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onValidationItemSelected, self.validationView.getListControl())
    # end _bindWidgetEvents

    def _getStcControl(self):
        return self.stcCtrl
    # end _getStcControl()

    def _setLexer(self):
        self._getStcControl().SetLexer(STC_LEX_HTML)
    # end _setLexer()

    def _setMargins(self):
        self._getStcControl().SetEdgeMode(STC_EDGE_BACKGROUND)
        self._getStcControl().SetEdgeColumn(256)
        # line numbers in the margin
        self._getStcControl().SetMarginType(0, STC_MARGIN_NUMBER)
        self._getStcControl().SetMarginWidth(0, 22)

        self._getStcControl().SetMarginType(1, STC_MARGIN_SYMBOL)
        self._getStcControl().SetMarginSensitive(1, True)
        self._getStcControl().SetMarginSensitive(0, True)
     # end _setMargins()


    def _setMarkers(self):
        registry = getResourceRegistry()
        self._getStcControl().MarkerDefine(IZZStyledTextCtrlMarkers.MARKER_NONE, STC_MARK_EMPTY)  #$NON-NLS-1$  #$NON-NLS-2$
        self._getStcControl().MarkerDefineBitmap(IZZStyledTextCtrlMarkers.MARKER_OK, registry.getBitmap(u"images/common/ok16x16.gif"))  #$NON-NLS-1$
        self._getStcControl().MarkerDefineBitmap(IZZStyledTextCtrlMarkers.MARKER_WARN, registry.getBitmap(u"images/common/warning16x16.gif"))  #$NON-NLS-1$
        self._getStcControl().MarkerDefineBitmap(IZZStyledTextCtrlMarkers.MARKER_ERROR, registry.getBitmap(u"images/common/error16x16.gif"))  #$NON-NLS-1$
        self._getStcControl().MarkerDefine(IZZStyledTextCtrlMarkers.MARKER_ARROW, STC_MARK_SHORTARROW, u"blue", u"yellow")  #$NON-NLS-1$  #$NON-NLS-2$
    # end _setMarkers()

    def _setStyles(self):
        # Make some styles,  The lexer defines what each style is used for, we
        # just have to define what each style looks like.  This set is adapted from
        # Scintilla sample property files.

        self._getStcControl().StyleClearAll()

        faces = { u'times': u'Times New Roman', #$NON-NLS-2$ #$NON-NLS-1$
                  u'mono' : u'Courier New', #$NON-NLS-2$ #$NON-NLS-1$
                  u'helv' : u'Arial', #$NON-NLS-2$ #$NON-NLS-1$
                  u'other': u'Comic Sans MS', #$NON-NLS-2$ #$NON-NLS-1$
                  u'size' : 10, #$NON-NLS-1$
                  u'size2': 8, #$NON-NLS-1$
                 }


        # Global default styles for all languages
#        self._getStcControl().StyleSetSpec(STC_STYLE_DEFAULT,     u"face:%(mono)s,size:%(size)d" % faces) #$NON-NLS-1$
#        self._getStcControl().StyleSetSpec(STC_STYLE_LINENUMBER,  u"back:#EEEEEE,face:%(helv)s,size:%(size2)d" % faces) #$NON-NLS-1$
#        self._getStcControl().StyleSetSpec(STC_STYLE_CONTROLCHAR, u"face:%(other)s" % faces) #$NON-NLS-1$
#        self._getStcControl().StyleSetSpec(STC_STYLE_BRACELIGHT,  u"fore:#FF0000,back:#FFFFFF,bold") #$NON-NLS-1$
#        self._getStcControl().StyleSetSpec(STC_STYLE_BRACEBAD,    u"fore:#FF00FF,back:#FFFFFF,bold") #$NON-NLS-1$

#wxSTC_H_DEFAULT = stc_c.wxSTC_H_DEFAULT
#wxSTC_H_TAG = stc_c.wxSTC_H_TAG
#wxSTC_H_TAGUNKNOWN = stc_c.wxSTC_H_TAGUNKNOWN
#wxSTC_H_ATTRIBUTE = stc_c.wxSTC_H_ATTRIBUTE
#wxSTC_H_ATTRIBUTEUNKNOWN = stc_c.wxSTC_H_ATTRIBUTEUNKNOWN
#wxSTC_H_NUMBER = stc_c.wxSTC_H_NUMBER
#wxSTC_H_DOUBLESTRING = stc_c.wxSTC_H_DOUBLESTRING
#wxSTC_H_SINGLESTRING = stc_c.wxSTC_H_SINGLESTRING
#wxSTC_H_OTHER = stc_c.wxSTC_H_OTHER
#wxSTC_H_COMMENT = stc_c.wxSTC_H_COMMENT
#wxSTC_H_ENTITY = stc_c.wxSTC_H_ENTITY
#wxSTC_H_TAGEND = stc_c.wxSTC_H_TAGEND
#wxSTC_H_XMLSTART = stc_c.wxSTC_H_XMLSTART
#wxSTC_H_XMLEND = stc_c.wxSTC_H_XMLEND
#wxSTC_H_SCRIPT = stc_c.wxSTC_H_SCRIPT
#wxSTC_H_ASP = stc_c.wxSTC_H_ASP
#wxSTC_H_ASPAT = stc_c.wxSTC_H_ASPAT
#wxSTC_H_CDATA = stc_c.wxSTC_H_CDATA
#wxSTC_H_QUESTION = stc_c.wxSTC_H_QUESTION
#wxSTC_H_VALUE = stc_c.wxSTC_H_VALUE
#wxSTC_H_XCCOMMENT = stc_c.wxSTC_H_XCCOMMENT

        # Default
        self._getStcControl().StyleSetSpec(STC_H_DEFAULT, u"fore:#000000,face:%(mono)s,size:%(size)d" % faces) #$NON-NLS-1$
        self._getStcControl().StyleSetSpec(STC_H_COMMENT, u"fore:#007F00,face:%(other)s,size:%(size)d" % faces) #$NON-NLS-1$
        self._getStcControl().StyleSetSpec(STC_H_NUMBER, u"fore:#000000,size:%(size)d" % faces) #$NON-NLS-1$
        self._getStcControl().StyleSetSpec(STC_H_DOUBLESTRING, u"fore:#000099,face:%(helv)s,size:%(size)d" % faces) #$NON-NLS-1$
        self._getStcControl().StyleSetSpec(STC_H_SINGLESTRING, u"fore:#000099,face:%(helv)s,size:%(size)d" % faces) #$NON-NLS-1$
        self._getStcControl().StyleSetSpec(STC_H_TAG, u"fore:#7F007F,bold,size:%(size)d" % faces) #$NON-NLS-1$
        self._getStcControl().StyleSetSpec(STC_H_TAGEND, u"fore:#7F007F,bold,size:%(size)d" % faces) #$NON-NLS-1$
        self._getStcControl().StyleSetSpec(STC_H_TAGUNKNOWN, u"fore:#00007f,italic,size:%(size)d" % faces) #$NON-NLS-1$
        self._getStcControl().StyleSetSpec(STC_H_ATTRIBUTE, u"fore:#00000,normal,size:%(size)d" % faces) #$NON-NLS-1$
        self._getStcControl().StyleSetSpec(STC_H_ATTRIBUTEUNKNOWN, u"fore:#007F00,italic,size:%(size)d" % faces) #$NON-NLS-1$

        self._getStcControl().SetCaretForeground(u"BLUE") #$NON-NLS-1$
    # end _setStyles()

    def _bindStcEvents(self):
        # disable right click menu
        self._getStcControl().UsePopUp(0)
        id = self._getStcControl().GetId()
        self._getStcControl().Bind(wx.EVT_RIGHT_UP, self.onRightClick)
        EVT_STC_UPDATEUI(self._getStcControl(), id, self.onSelectionChange)
        EVT_STC_UPDATEUI(self._getStcControl(), id, self.onUpdateUI)
        EVT_STC_CHANGE(self._getStcControl(), id, self.onChange)

        EVT_STC_CHARADDED(self._getStcControl(), id, self.onCharAdded)
        EVT_STC_USERLISTSELECTION(self._getStcControl(), id, self.onUserListSelection)
        wx.EVT_KEY_DOWN(self._getStcControl(), self.onKeyPressed)
        EVT_STC_MARGINCLICK(self._getStcControl(), id, self.onMarginClick)
##        EVT_STC_START_DRAG(self._getStcControl(), id, self.OnStartDrag)
##        EVT_STC_DRAG_OVER(self._getStcControl(), id, self.OnDragOver)
#        EVT_STC_DO_DROP(self._getStcControl(), id, self.OnDoDrop)
##        EVT_STC_MARGINCLICK(self._getStcControl(),id, self.OnMarginClick)


    # end _bindStcEvents()

    def _matchBraces(self):
        p1 = self._getStcControl().GetCurrentPos()
        c1 = self._getStcControl().GetCharAt(p1)
        p2 = p1 - 1
        if p2 < 0:
            p2 = 0
        c2 = self._getStcControl().GetCharAt(p2)
        openBrace = [ord(u"<"), ord(u"\""), ord(u"'")] #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$
        closeBrace = [ord(u">"),ord(u"\""), ord(u"'")] #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$
        if (c2 in openBrace or c2 in closeBrace) or (c1 in openBrace or c1 in closeBrace):
            p = p1
            if c2 in openBrace or c2 in closeBrace:
                p  = p - 1
            q = self._getStcControl().BraceMatch(p)
            if q == STC_INVALID_POSITION:
                self._getStcControl().BraceBadLight(p);
            else:
                self._getStcControl().BraceHighlight(p,q);
        else:
            self._getStcControl().BraceBadLight(STC_INVALID_POSITION);
    # end _matchBraces

    def onKeyPressed(self, event):
        self._resetMarkerHighLighting()
        if self._getStcControl().CallTipActive():
            self._getStcControl().CallTipCancel()
        key = event.GetKeyCode()
        event.Skip()
        if key == 32 and event.ControlDown():
            if event.ShiftDown():
                self._showCallTip()
            else:
                self._showXhtmlAutoComplete(False)
    # end OnKeyPressed

    def _showCallTip(self):
        pos = self._getStcControl().GetCurrentPos()
        text = self.autocompleteHandler.getCallTip(self.autocompleteLocator)
        if text:
            self._getStcControl().CallTipSetBackground(u"yellow")#$NON-NLS-1$
            self._getStcControl().CallTipShow(pos, text)
    # end _showCallTip

    def _showXhtmlAutoComplete(self, autoHide=False):
        if self._getStcControl().CallTipActive():
            self._getStcControl().CallTipCancel()

        pos = self._getStcControl().GetCurrentPos() #@UnusedVariable
        if not self._getStcControl().AutoCompActive():
            (lst, self.autocompleteLocatorInfo) = self.autocompleteHandler.getAutocompleteList(self.autocompleteLocator)

            if lst and len(lst) > 0:
                lst.sort()  # Python sorts are case sensitive
                self._getStcControl().AutoCompSetAutoHide(autoHide)
                self._getStcControl().AutoCompSetIgnoreCase(False)  # so this needs to match
                self._getStcControl().AutoCompSetSeparator(ord(u"|"))#$NON-NLS-1$
                #self.AutoCompShow(0, u"|".join(lst))  #$NON-NLS-1$
                try:
                    self._getStcControl().UserListShow(self.autocompleteLocatorInfo.locationType, u"|".join(lst))  #$NON-NLS-1$
                except:
                    pass
    # end _showXhtmlAutoComplete()

    def onCharAdded(self, event): #@UnusedVariable
        p = self._getStcControl().GetCurrentPos()
        # if autocomp is active and the char sequence is "</" then cancel autocomplete so that the new autocomplete list for '</' can be shown.
        if self._getStcControl().AutoCompActive() and p > 1 and self._getStcControl().GetCharAt(p-1) == ord(u"/") and self._getStcControl().GetCharAt(p-2) == ord(u"<"): #$NON-NLS-1$  #$NON-NLS-2$
            self._getStcControl().AutoCompCancel()

        if not self._getStcControl().AutoCompActive():
            # xhtml
            if p > 0 and self._getStcControl().GetCharAt(p-1) == ord(u"<"): #$NON-NLS-1$
                self._showXhtmlAutoComplete(True)
            elif p > 1 and self._getStcControl().GetCharAt(p-1) == ord(u"/") and self._getStcControl().GetCharAt(p-2) == ord(u"<"): #$NON-NLS-1$  #$NON-NLS-2$
                self._showXhtmlAutoComplete(True)
            # http://
            elif p > 8 and (self._getStcControl().GetTextRange(p-7,p).lower() == u"http://" or self._getStcControl().GetTextRange(p-8,p).lower() == u"https://") : #$NON-NLS-1$  #$NON-NLS-2$
                lst = self.autocompleteHandler.getHrefList(self.autocompleteLocator,True)
                if lst and len(lst) > 0:
                    # remove leading http://
                    for i in range(len(lst)):
                        if lst[i].startswith(u"http://"): #$NON-NLS-1$
                            lst[i] = lst[i][7:]
                        elif lst[i].startswith(u"https://"): #$NON-NLS-1$
                            lst[i] = lst[i][8:]
                    lst.sort()
                    if self._getStcControl().CallTipActive():
                        self._getStcControl().CallTipCancel()

                    self._getStcControl().AutoCompSetAutoHide(True)
                    self._getStcControl().AutoCompSetIgnoreCase(False)
                    self._getStcControl().AutoCompSetSeparator(ord(u"^"))#$NON-NLS-1$
                    try:
                        self._getStcControl().AutoCompShow(0, u"^".join(lst))  #$NON-NLS-1$
                    except:
                        pass
    # end onCharAdded

    def onUserListSelection(self, evt):
        lType =  evt.GetListType()
        text = evt.GetText()
        if text and len(text.strip()) > 0:
            p1 = self._getStcControl().AutoCompPosStart()
            p2 = self._getStcControl().GetCurrentPos()
            if lType == ZStcLocator.OPENTAG:
                if self.autocompleteHandler.isEmptyTag(text):
                    if text == u"img": #$NON-NLS-1$
                        text = text + u' src="" alt=""' #$NON-NLS-1$
                    text = text + u" />" #$NON-NLS-1$
                else:
                    text = text + u" " #$NON-NLS-1$
            elif lType == ZStcLocator.CLOSETAG:
                text = text + u'>' #$NON-NLS-1$
            elif lType == ZStcLocator.INSIDETAG:
                text = text + u'="' #$NON-NLS-1$
            elif lType == ZStcLocator.ATTRVALUE and self.autocompleteLocatorInfo.attributeName and self.autocompleteLocatorInfo.attributeName.lower() == u"style" : #$NON-NLS-1$
                text = text + u':' #$NON-NLS-1$
            elif lType == ZStcLocator.ATTRVALUE and self.autocompleteLocatorInfo.attributeName and self.autocompleteLocatorInfo.attributeName.lower() == u"href" : #$NON-NLS-1$
                if text.lower().strip() == ZStcAutoCompleteHandler.ALL_POSTS_HREF.lower():
                    pass
                    #text = self._showPostsDialog()
            elif lType == ZStcLocator.SUBATTRNAME:
                if text.strip().lower() == ZStcAutoCompleteHandler.CUSTOM_COLORS.lower():
                    text = self._showColorChooserDialog()
                if text and len(text) > 0:
                    text = text + u'; ' #$NON-NLS-1$
            if p1 >=0 and p2 > p1:
                self._getStcControl().SetSelection(p1,p2)
                self._getStcControl().ReplaceSelection(text)
            else:
                self._getStcControl().AddText(text)
    # end onUserListSelection

    def _showColorChooserDialog(self):
        rVal = u""  #$NON-NLS-1$
        dlg = wx.ColourDialog(self)
        dlg.CentreOnParent()
        dlg.GetColourData().SetChooseFull(True)
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetColourData().GetColour().Get() #RGB tuple
            color = ZCssColor(red = data[0], blue = data[2], green = data[1])
            rVal = color.getCssColor().upper()
        dlg.Destroy()
        return rVal
    # end _showColorChooserDialog()

    def onUpdateUI(self, event): #@UnusedVariable
        self._fireUpdateUIEvent()
        # check for matching braces
        self._matchBraces()
        event.Skip()
    # end onUpdateUI()

    def onChange(self, event): #@UnusedVariable
        if self.contentLoaded:
            self._fireContentModifiedEvent()
    # end onChange()

    def onSelectionChange(self, event): #@UnusedVariable
        selection = None
        self._fireSelectionChangeEvent(selection)
        event.Skip()
    # end onSelectionChange()

    def onRightClick(self, event):
        xyPoint = event.GetPosition()
        self._fireContextMenuEvent(self, xyPoint)
    # end onRightClick()
    
    def setValue(self, value):
        self.clearValidation()
        # we need to reset the undo buffer otherwise the last undo will remove the text.
        self._getStcControl().EmptyUndoBuffer()        
        self._internalSetValue(value)
    # end setValue

    def _internalSetValue(self, value):
        self.contentLoaded = False
        self._getStcControl().SetText(value)
        # set line break to be \n
        self._getStcControl().SetEOLMode(STC_EOL_LF)
        self._getStcControl().ConvertEOLs(STC_EOL_LF)
        self.contentLoaded = True
        self._fireUpdateUIEvent()
    # end _internalSetValue

    def getValue(self):
        return self._getStcControl().GetText()
    # end getValue()

    def getCaretPosition(self):
        pos = self._getStcControl().GetCurrentPos()
        col = self._getStcControl().GetColumn(pos) + 1
        row = self._getStcControl().LineFromPosition(pos) + 1
        return (row,col)
    # end getCaretPosition()
    
    def clearState(self):
        pass
    # end clearState()

    def hasSelection(self):
        (start,end) = self._getStcControl().GetSelection()
        return start != end
    # hasSelection()

    def canCut(self):
        return self.hasSelection()
    # end canCut()

    def cut(self):
        self._getStcControl().Cut()
    # end cut()

    def canCopy(self):
        return self.canCut()
    # end canCopy()

    def copy(self):
        self._getStcControl().Copy()
    # end copy()

    def canPaste(self):
        return self._getStcControl().CanPaste()
    # end canPaste()

    def paste(self):
        self._getStcControl().Paste()
    # end paste()

    def canSelectAll(self):
        return True
    # end canSelectAll()

    def selectAll(self):
        self._getStcControl().SelectAll()
    # end selectAll()

    def selectNone(self):
        (start,end) = self._getStcControl.GetSelection() #@UnusedVariable
        self.SetSelection(start,start)
    # selectNone()

    def canUndo(self):
        return self._getStcControl().CanUndo()
    # end canUndo()

    def undo(self):
        self._getStcControl().Undo()
    # end undo()

    def canRedo(self):
        return self._getStcControl().CanRedo()
    # end canRedo()

    def redo(self):
        self._getStcControl().Redo()
    # end redo()

    def isFormattingEnabled(self, capabilityId): #@UnusedVariable
        if self.hasCapability(capabilityId):
            return True
        else:
            return False
    # end isFormattingEnabled()

    def getFormattingState(self, capabilityId): #@UnusedVariable
        return False
    # end getFormattingState()

    def applyFormatting(self, capabilityId, customData): #@UnusedVariable
        if capabilityId == IZRichTextEditControl.ZCAPABILITY_BOLD:
            self._wrapSelectionWithTag(u"strong") #$NON-NLS-1$
        elif capabilityId == IZRichTextEditControl.ZCAPABILITY_ITALIC:
            self._wrapSelectionWithTag(u"em") #$NON-NLS-1$
        elif capabilityId == IZRichTextEditControl.ZCAPABILITY_UNDERLINE:
            self._wrapSelectionWithTag(u"span", u"text-decoration: underline") #$NON-NLS-1$, #$NON-NLS-2$
        elif capabilityId == IZRichTextEditControl.ZCAPABILITY_STRIKETHRU:
            self._wrapSelectionWithTag(u"del") #$NON-NLS-1$
    # end applyFormatting()

    def canPasteXhtml(self):
        return self.canPaste()
    # end canPasteXhtml()

    def pasteXhtml(self):
        # get text from clipboard and insert xhtml
        content = getTextFromClipboard()
        if content:
            xhtmlDoc = loadXhtmlDocumentFromString(content)
            if xhtmlDoc:
                html = u"" #$NON-NLS-1$
                for node in xhtmlDoc.getBody().selectNodes(u"child::*"): #$NON-NLS-1$
                    html = html + node.serialize()
                self._insertHtml(html, 0)
    # end pasteXhtml()

    def canInsertXhtml(self):
        return True
    # end canInsertXhtml

    def insertXhtml(self, xhtmlString): #@UnusedVariable
        self._insertHtml(xhtmlString, 0)
    # end insertXhtml

    def createFindReplaceContext(self):
        selectedText = self._getStcControl().GetSelectedText()
        return ZStyledXhtmlEditControlFindReplaceTextContext(self._getStcControl(), selectedText)
    # end createFindReplaceContext()

    def _wrapSelectionWithTag(self, tag, style = None):
        s = u"" #$NON-NLS-1$
        startTag = tag
        if style and tag:
            startTag = tag + u' style="%s" ' % style #$NON-NLS-1$
        posOffset = 0
        if self.hasSelection() and tag:
            s = u"<%s>%s</%s>" % (startTag, self._getStcControl().GetSelectedText(), tag) #$NON-NLS-1$
        elif tag:
            s = u"<%s></%s>" % (startTag, tag) #$NON-NLS-1$
            posOffset = len(startTag) + 2
        self._insertHtml(s, posOffset)
    #end _wrapSelectionWithTag()

    def _insertHtml(self, html, posOffset):
        if not html:
            return
        pos = self._getStcControl().GetCurrentPos()
        if self.hasSelection():
            self._getStcControl().ReplaceSelection(html)
        else:
            self._getStcControl().AddText(html)
        if posOffset > 0:
            self._getStcControl().EnsureCaretVisible()
            self._getStcControl().SetCurrentPos(pos + posOffset)
            pos = self._getStcControl().GetCurrentPos()
            self._getStcControl().SetSelectionStart(pos)
            self._getStcControl().EnsureCaretVisible()
    # end _insertHtml()

    def onMarginClick(self, evt):
        self._resetMarkerHighLighting()
        if evt.GetMargin() == 1:
            pos = evt.GetPosition()
            line = self._getStcControl().LineFromPosition(evt.GetPosition())
            self._handleMarkerMarginClicked(pos, line)
        evt.Skip()
    # end onMarginClick

    def _handleMarkerMarginClicked(self, pos, line): #@UnusedVariable
        # called when the user clicked on a marker on the margin.
        self._highlightMarkerLine(-1)
        # find marker by line number:
        line = line + 1 # adjust for 0 based index
        for zxhtmlValidationMessage in self.validationReportProvider.getValidationMessages(): #@UnusedVariable
            if zxhtmlValidationMessage.getLine() == line:
                # FIXME hightlight message in list control
                pass
    # end  _handleMarkerMarginClicked

    def _highlightMarkerLine(self, aLineNum, aColNum=-1):
        self._getStcControl().MarkerDeleteAll(IZZStyledTextCtrlMarkers.MARKER_ARROW)
        if aLineNum < 0:
            return

        self._getStcControl().MarkerAdd(aLineNum, IZZStyledTextCtrlMarkers.MARKER_ARROW)
        self._getStcControl().EnsureCaretVisible()
        pos = self._getStcControl().PositionFromLine(aLineNum)
        if aColNum >= 0:
            p = pos + aColNum
            if p <= self._getStcControl().GetTextLength():
                pos = p
        self._getStcControl().SetCurrentPos(pos)
        self._getStcControl().SetSelectionStart(pos)
        self._getStcControl().EnsureCaretVisible()
        self._getStcControl().SetCaretLineBack(wx.Colour(red=255, green=255, blue=102))
        self._getStcControl().SetCaretLineVisible(True)
    # end _highlightMarkerLine()

    def _resetMarkerHighLighting(self):
        if self._getStcControl().GetCaretLineVisible():
            self._getStcControl().SetCaretLineVisible(False)
    # end _resetMarkerHighLighting()

    def _clearAllMarkers(self):
        self._getStcControl().MarkerDeleteAll(IZZStyledTextCtrlMarkers.MARKER_NONE)
        self._getStcControl().MarkerDeleteAll(IZZStyledTextCtrlMarkers.MARKER_OK)
        self._getStcControl().MarkerDeleteAll(IZZStyledTextCtrlMarkers.MARKER_WARN)
        self._getStcControl().MarkerDeleteAll(IZZStyledTextCtrlMarkers.MARKER_ERROR)
        self._getStcControl().MarkerDeleteAll(IZZStyledTextCtrlMarkers.MARKER_ARROW)
        self._resetMarkerHighLighting()
    # end _clearAllMarkers()

    def _addValidationMessageMarker(self, zxhtmlValidationMessage):
        if not zxhtmlValidationMessage:
            return
        symbol = IZZStyledTextCtrlMarkers.MARKER_NONE
        if zxhtmlValidationMessage.getSeverity() == ZXhtmlValidationMessage.SUCCESS:
            symbol = IZZStyledTextCtrlMarkers.MARKER_OK
        elif zxhtmlValidationMessage.getSeverity() == ZXhtmlValidationMessage.WARNING:
            symbol = IZZStyledTextCtrlMarkers.MARKER_WARN
        elif zxhtmlValidationMessage.getSeverity() == ZXhtmlValidationMessage.ERROR:
            symbol = IZZStyledTextCtrlMarkers.MARKER_ERROR
        elif zxhtmlValidationMessage.getSeverity() == ZXhtmlValidationMessage.FATAL:
            symbol = IZZStyledTextCtrlMarkers.MARKER_ERROR

        if zxhtmlValidationMessage.getLine() > 0:
            self._getStcControl().MarkerAdd(zxhtmlValidationMessage.getLine() - 1, symbol)
    # end _addValidationMessageMarker()

    def schemaValidate(self):
        # IZXHTMLEditControl impl.
        fireUIExecEvent(ZMethodRunnable(self._showViewAndRunValidation), self)
    # end schemaValidate

    def _showValidationView(self):
        if not self.validationView.IsShown():
            self.validationView.Show(True)
            self.Layout()
    # end _showValidationView

    def _hideValidationView(self):
        if self.validationView.IsShown():
            self.validationView.Show(False)
            self.Layout()
    # end _hideValidationView

    def _showViewAndRunValidation(self):
        self._showValidationView()
        fireUIExecEvent(ZMethodRunnable(self._runValidation), self)
    # end _showViewAndRunValidation

    def _runValidation(self):
        self._clearValidation()
        ZXhtmlSchemaUiUtil().validateHtmlBody(None, self.getValue(), self )
    # end _runValidation

    def _clearValidation(self):
        # IZXHTMLEditControl impl.
        self._clearAllMarkers()
        self.validationReportProvider.clearValidationMessages()
        self.validationView.getListControl().refresh()
    # end _clearValidation

    def clearValidation(self):
        # IZXHTMLEditControl impl.
        self._clearValidation()
        self._hideValidationView()
    # end clearValidation

    def runTidy(self):
        # IZXHTMLEditControl impl.
        fireUIExecEvent(ZMethodRunnable(self._internalRunTidy), self)
    # end runTidy

    def _internalRunTidy(self):
        self._showValidationView()
        self._clearValidation()
        (success, htmlResult, messageList) = ZXhtmlSchemaUiUtil().tidyHtmlBody(None, self.getValue(), self ) #@UnusedVariable
        if success:
            self._getStcControl().SetText(htmlResult)
    # end _internalRunTidy

    def onValidationItemSelected(self, event):
        index = event.GetIndex()
        zxhtmlValidationMessage = self.validationReportProvider.getValidationMessage(index)
        if zxhtmlValidationMessage:
            self._highlightMarkerLine(zxhtmlValidationMessage.getLine()-1, zxhtmlValidationMessage.getColumn())
    # end onValidationItemSelected

    def onValidationItemActivated(self, event): #@UnusedVariable
        pass
    # end onValidationItemActivated

    def onXhtmlValidationStart(self):
        pass
    # end onXhtmlValidationStart

    def onXhtmlValidationEnd(self, messageCount):
        if messageCount == 0:
            m = ZXhtmlValidationMessage(ZXhtmlValidationMessage.SUCCESS, -1,-1, u"Completed successfully.") #$NON-NLS-1$
            self.validationReportProvider.addValidationMessage(m)
        else:
            m = ZXhtmlValidationMessage(ZXhtmlValidationMessage.ERROR, -1, -1, u"Completed with problems.") #$NON-NLS-1$
            self.validationReportProvider.addValidationMessage(m)
        self.validationView.getListControl().refresh()
    # end onXhtmlValidationEnd

    def onXhtmlValidationMessage(self, zxhtmlValidationMessage): #@UnusedVariable
        self.validationReportProvider.addValidationMessage(zxhtmlValidationMessage)
        self._addValidationMessageMarker(zxhtmlValidationMessage)
    # end onXhtmlValidationMessage

    def onXhtmlValidationException(self, exception): #@UnusedVariable
        pass
    # end onXhtmlValidationException

# end ZStyledXhtmlEditControl
