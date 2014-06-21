from zoundry.appframework.services.spellcheck.spellcheckcontext import IZSpellCheckContext
from zoundry.appframework.services.spellcheck.spellcheckcontext import ZBaseSpellCheckContext
from zoundry.appframework.ui.events.editcontrolevents import ZEditControlContentModifiedEvent
from zoundry.appframework.ui.events.editcontrolevents import ZEditControlContextMenuEvent
from zoundry.appframework.ui.events.editcontrolevents import ZEditControlSelectionChangeEvent
from zoundry.appframework.ui.events.editcontrolevents import ZEditControlUpdateUIEvent
from zoundry.appframework.ui.widgets.controls.common.panel import ZTransparentPanel
from zoundry.base.util.text.textutil import getNoneString
from zoundry.base.util.types.capabilities import ZCapabilities

# ------------------------------------------------------------------------------
# Interface that must be implemented by edit controls.  An edit control is a
# control that allows the user to edit the content of a IZDocument.  Examples of
# edit controls:  blog post content wysiwyg editor, blog post content xhtml
# editor, etc.
#
# An edit control can fire a variety of events.  Please see IZEditControlEvents
# for details.
# ------------------------------------------------------------------------------
class IZEditControl:

    ZCAPABILITY_CUT = u"zoundry.editcontrol.capability.cut" #$NON-NLS-1$
    ZCAPABILITY_COPY = u"zoundry.editcontrol.capability.copy" #$NON-NLS-1$
    ZCAPABILITY_PASTE = u"zoundry.editcontrol.capability.paste" #$NON-NLS-1$
    ZCAPABILITY_UNDO = u"zoundry.editcontrol.capability.undo" #$NON-NLS-1$
    ZCAPABILITY_REDO = u"zoundry.editcontrol.capability.redo" #$NON-NLS-1$
    ZCAPABILITY_SELECT_ALL = u"zoundry.editcontrol.capability.select-all" #$NON-NLS-1$
    ZCAPABILITY_SELECT_NONE = u"zoundry.editcontrol.capability.select-none" #$NON-NLS-1$

    def setValue(self, value):
        u"""setValue(string) -> None
        Sets the value for this edit control.""" #$NON-NLS-1$
    # end setValue()

    def getValue(self):
        u"""getValue() -> string
        Gets the current value of this edit control.""" #$NON-NLS-1$
    # end getValue()

    def clearState(self):
        u"""clearState() -> None
        Invoked to indicate that the content has been save and any flags (e.g 'dirty') can be cleared.""" #$NON-NLS-1$
    # end clearState()

    def hasCapability(self, capability):
        u"""hasCapability(capabilityId) -> boolean
        Returns True if this edit control has the given
        capability.""" #$NON-NLS-1$
    # end hasCapability()

    def canCut(self):
        u"""canCut() -> boolean
        Returns True if the current edit control selection is
        valid and can be 'cut'.""" #$NON-NLS-1$
    # end canCut()

    def cut(self):
        u"""cut() -> None
        Called to cut the current selection (putting the selected
        content on the clipboard).""" #$NON-NLS-1$
    # end cut()

    def canCopy(self):
        u"""canCopy() -> boolean
        Returns True if the current edit control selection is
        valid and can be copied.""" #$NON-NLS-1$
    # end canCopy()

    def copy(self):
        u"""copy() -> None
        Called to copy the current selection (putting the selected
        content on the clipboard).""" #$NON-NLS-1$
    # end copy()

    def canPaste(self):
        u"""canPaste() -> boolean
        Returns True if the edit control is in a state in which
        content can be pasted from the clipboard.""" #$NON-NLS-1$
    # end canPaste()

    def paste(self):
        u"""paste() -> None
        Called to paste the current clipboard contents into the
        edit control.""" #$NON-NLS-1$
    # end paste()

    def canSelectAll(self):
        u"""canSelectAll() -> boolean
        Returns True if the edit control is in a state in which
        all content can be selected.""" #$NON-NLS-1$
    # end canSelectAll()

    def selectAll(self):
        u"""selectAll() -> None
        Called to select all of the content in the edit control.""" #$NON-NLS-1$
    # end selectAll()

    def selectNone(self):
        u"""selectNone() -> None
        Called to de-select current selection in the content in the edit control.""" #$NON-NLS-1$
    # end selectAll()

    def canUndo(self):
        u"""canUndo() -> boolean
        Returns True if the edit control can undo the last edit action or command.""" #$NON-NLS-1$
    # end canUndo()

    def undo(self):
        u"""undo() -> None
        Called to undo the last edit action or command.""" #$NON-NLS-1$
    # end undo()

    def canRedo(self):
        u"""canRedo() -> boolean
        Returns True if the edit control can redo the last edit action or command.""" #$NON-NLS-1$
    # end canRedo()

    def redo(self):
        u"""undo() -> None
        Called to redo the last edit action or command.""" #$NON-NLS-1$
    # end redo()
    
    def getCaretPosition(self):
        u"""getCaretPosition() -> (int, int)
        Returns current caret position as tuple (row, column) or (-1, -1) if not supported.""" #$NON-NLS-1$
    # end getCaretPosition()

# end IZEditControl

# ------------------------------------------------------------------------------
# Rich text editor interface
# ------------------------------------------------------------------------------
class IZTextEditControl(IZEditControl):
    ZCAPABILITY_FIND_TEXT       = u"zoundry.editcontrol.capability.find" #$NON-NLS-1$
    ZCAPABILITY_FINDREPLACE     = u"zoundry.editcontrol.capability.find-and-replace" #$NON-NLS-1$
    ZCAPABILITY_SPELLCHECK      = u"zoundry.editcontrol.capability.spellcheck" #$NON-NLS-1$

    def createSpellCheckContext(self):
        u"""createSpellCheckContext() -> IZEditControlSpellCheckContext
        Returns an instance of IZEditControlSpellCheckContext or None if spellcheck capability is not supported.""" #$NON-NLS-1$
    # end createSpellCheckContext()

    def createFindReplaceContext(self):
        u"""createFindReplaceContext() -> IZEditControlFindReplaceTextContext
        Returns an instance of IZEditControlFindReplaceTextContext or None if find/replace capability is not supported.""" #$NON-NLS-1$
    # end createFindReplaceContext()

# end IZTextEditControl

# ------------------------------------------------------------------------------
# Edit control spell check context
# ------------------------------------------------------------------------------
class IZEditControlSpellCheckContext(IZSpellCheckContext):

    def highlightWord(self, on):
        u"""highlightWord(bool) - void
        Highlights the currently misspelled word when on=True and deselects/unhighlights when on=False""" #$NON-NLS-1$
    # end highlightWord()

# end IZEditControlSpellCheckContext

# ------------------------------------------------------------------------------
# Edit control find replace context
# ------------------------------------------------------------------------------
class IZEditControlFindReplaceTextContext:

    def initialize(self):
        u"""initialize() - void
        Initialize find/replace process.
        This method is called eachtime find/replace is run.""" #$NON-NLS-1$
    # end initialize()

    def cleanup(self):
        u"""cleanup() - void
        Called after completing the find/replace process to allow the context to clean up any resources.""" #$NON-NLS-1$
    # end cleanup()

    def reset(self):
        u"""reset() - void
        Called when a new find text process is started. Implementations can use this method to reset cursors/pointers etc.""" #$NON-NLS-1$
    # end reset()

    def isCaseSensitive(self):
        u"""isCaseSensitive() -> bool
        Returns true if the search is case sensitive.""" #$NON-NLS-1$
    # end isCaseSensitive

    def setCaseSensitive(self, b):
        u"""setCaseSensitive(bool) -> void
        Sets the case sensitive flag.""" #$NON-NLS-1$
    # end setCaseSensitive

    def isMatchWord(self):
        u"""isMatchWord() -> bool
        Returns true if the search should match whole word.""" #$NON-NLS-1$
    # end isMatchWord()

    def setMatchWord(self, b):
        u"""setMatchWord(bool) -> void
        Sets the match whole word flag.""" #$NON-NLS-1$
    # end setMatchWord()

    def isSearchForward(self):
        u"""isSearchForward() -> bool
        Returns true if the search direction is forward/down""" #$NON-NLS-1$
    # end isSearchForward()

    def setSearchForward(self, b):
        u"""setSearchForward(bool) -> void
        Sets the search direction.""" #$NON-NLS-1$
    # end setSearchForward()

    def getText(self):
        u"""getText() -> string
        Returns the current find text.""" #$NON-NLS-1$
    # end getText()

    def setText(self, text):
        u"""setText(string) -> void
        Sets the current find text.""" #$NON-NLS-1$
    # end  setText()

    def find(self):
        u"""find() -> bool
        Finds from the last known location. Returns True if found or False otherwise.""" #$NON-NLS-1$
    # end find()

    def replace(self, replaceText):
        u"""replace(string) -> void
        Replaces the current text with the replacement.""" #$NON-NLS-1$
    # end replace()

    def replaceAll(self, replaceText):
        u"""replaceAll(string) -> void
        Replaces all occurances of the current word with the replacement.""" #$NON-NLS-1$
    # end replaceAll()

    def getFindTextHistory(self):
        u"""getFindTextHistory() -> list
        Returns list of previously used search terms.""" #$NON-NLS-1$
    # end getFindTextHistory()

    def getReplaceTextHistory(self):
        u"""getReplaceTextHistory() -> list
        Returns list of previously used replace terms.""" #$NON-NLS-1$
    # end getReplaceTextHistory()

# end IZEditControlSpellCheckContext

# ------------------------------------------------------------------------------
# Rich text editor interface
# ------------------------------------------------------------------------------
class IZRichTextEditControl(IZTextEditControl):

    # Define formatting capabilitings
    ZCAPABILITY_BOLD            = u"zoundry.editcontrol.capability.formatting.bold" #$NON-NLS-1$
    ZCAPABILITY_ITALIC          = u"zoundry.editcontrol.capability.formatting.italic" #$NON-NLS-1$
    ZCAPABILITY_UNDERLINE       = u"zoundry.editcontrol.capability.formatting.underline" #$NON-NLS-1$
    ZCAPABILITY_STRIKETHRU      = u"zoundry.editcontrol.capability.formatting.strikethru" #$NON-NLS-1$
    ZCAPABILITY_ALIGN_LEFT      = u"zoundry.editcontrol.capability.formatting.align.left" #$NON-NLS-1$
    ZCAPABILITY_ALIGN_RIGHT     = u"zoundry.editcontrol.capability.formatting.align.right" #$NON-NLS-1$
    ZCAPABILITY_ALIGN_CENTER    = u"zoundry.editcontrol.capability.formatting.align.center" #$NON-NLS-1$
    ZCAPABILITY_JUSTIFY         = u"zoundry.editcontrol.capability.formatting.justify" #$NON-NLS-1$
    ZCAPABILITY_ORDERED_LIST    = u"zoundry.editcontrol.capability.formatting.list.ordered" #$NON-NLS-1$
    ZCAPABILITY_UNORDERED_LIST  = u"zoundry.editcontrol.capability.formatting.list.unordered" #$NON-NLS-1$
    ZCAPABILITY_INDENT          = u"zoundry.editcontrol.capability.formatting.indent" #$NON-NLS-1$
    ZCAPABILITY_OUTDENT         = u"zoundry.editcontrol.capability.formatting.outdent" #$NON-NLS-1$
    ZCAPABILITY_FONT_NAME       = u"zoundry.editcontrol.capability.formatting.font.name" #$NON-NLS-1$
    ZCAPABILITY_FONT_SIZE       = u"zoundry.editcontrol.capability.formatting.font.size" #$NON-NLS-1$
    ZCAPABILITY_COLOR           = u"zoundry.editcontrol.capability.formatting.color.foreground" #$NON-NLS-1$
    ZCAPABILITY_BACKGROUND      = u"zoundry.editcontrol.capability.formatting.color.background" #$NON-NLS-1$

    def isFormattingEnabled(self, capabilityId):
        u"""isFormattingEnabled(capabilityId) -> boolean
        Returns True if the formatting capability (e.g. bold) is enabled.""" #$NON-NLS-1$
    # end isFormattingEnabled()

    def getFormattingState(self, capabilityId):
        u"""getFormattingState(capabilityId) -> boolean
        Returns True if the formatting (e.g. bold) state is active/depressed.""" #$NON-NLS-1$
    # end getFormattingState()

    def applyFormatting(self, capabilityId, customData):
        u"""applyFormatting(capabilityId) -> void
        Applies the given formatting e.g. Bold on the current selection.""" #$NON-NLS-1$
    # end applyFormatting()

# end IZRichTextEditControl

# ------------------------------------------------------------------------------
# Selection context
# ------------------------------------------------------------------------------
class IZEditControlSelection:

    def isEmpty(self):
        u"""isEmpty() -> bool
        Returns true if the selection is empty.""" #$NON-NLS-1$
        pass
# end IZEditControlSelection

# ------------------------------------------------------------------------------
# text selection context
# ------------------------------------------------------------------------------
class IZTextEditControlSelection(IZEditControlSelection):

    def getSelectedText(self):
        u"""getSelectedText() -> string
        Returns selected text string.""" #$NON-NLS-1$
        pass
# end IZTextEditControlSelection

# ------------------------------------------------------------------------------
# base implementation of a selection.
# ------------------------------------------------------------------------------
class ZEditControlSelection(IZEditControlSelection):

    def __init__(self, empty):
        self.empty = empty
    # end __init__()

    def isEmpty(self):
        return self.empty
    # end isEmpty()

# end ZEditControlSelection()


# ------------------------------------------------------------------------------
# base implementation of a text selection.
# ------------------------------------------------------------------------------
class ZTextEditControlSelection(ZEditControlSelection, IZTextEditControlSelection):

    def __init__(self, text):
        self.text = text
        ZEditControlSelection.__init__(self, getNoneString(text) == None )
    # end __init__()

    def getSelectedText(self):
        return self.text
    # end getSelectedText()

# end ZTextEditControlSelection


# ------------------------------------------------------------------------------
# base implementation of IZEditControlSpellCheckContext.
# ------------------------------------------------------------------------------

class ZBaseEditControlSpellCheckContext(ZBaseSpellCheckContext, IZEditControlSpellCheckContext):

    def _cleanup(self):
        # override to turn off any highlighting.
        self.highlightWord(False)
        ZBaseSpellCheckContext._cleanup(self)
    # end _cleanup()

    def _prepareResult(self, spellcheckResult): #@UnusedVariable
        # override to turn on highlighting on the current word.
        self.highlightWord(True)
        ZBaseSpellCheckContext._prepareResult(self, spellcheckResult)
    # end _prepareResult

    def highlightWord(self, on): #@UnusedVariable
        pass
    # end highlightWord()

# end ZBaseEditControlSpellCheckContext


# ------------------------------------------------------------------------------
# A base class for all edit controls.  This class extends wx.Panel and provides
# some basic functionality, such as event firing.
# ------------------------------------------------------------------------------
class ZBaseEditControl(ZTransparentPanel, IZEditControl):

    def __init__(self, *args, **kw):
        ZTransparentPanel.__init__(self, *args, **kw)
        self.capabilities = self._createCapabilities()
    # end __init__()

    def _createCapabilities(self):
        cmap = {}
        for capabilityId in self._getCapabilityIdList():
            cmap[capabilityId] = True
        capabilities = ZCapabilities(cmap)
        return capabilities
    # end _createCapabilities()

    def _getCapabilityIdList(self):
        u"""_getCapabilityIdList() -> list
        Returns list of supported capabilites.""" #$NON-NLS-1$
        rval = []
        return rval
    # end _getCapabilityIdList()

    def getCapabilities(self):
        u"""getCapabilities() -> IZCapabilities
        Returns IZCapabilities impl.""" #$NON-NLS-1$
        return self.capabilities
    # end getCapabilities()

    def addCapability(self, capability):
        self.getCapabilities()._addCapability(capability)
    # end addCapability()

    def _fireEvent(self, event):
        self.GetEventHandler().AddPendingEvent(event)
    # end _fireEvent()

    def _fireContentModifiedEvent(self):
        event = ZEditControlContentModifiedEvent(self.GetId(), self)
        self._fireEvent(event)
    # end _fireContentModifiedEvent()

    def _fireUpdateUIEvent(self):
        event = ZEditControlUpdateUIEvent(self.GetId(), self)
        self._fireEvent(event)
    # end _fireUpdateUIEvent()

    def _fireSelectionChangeEvent(self, izEditControlSelection):
        event = ZEditControlSelectionChangeEvent(self.GetId(), self, izEditControlSelection)
        self._fireEvent(event)
    # end _fireSelectionChangeEvent()

    def _fireContextMenuEvent(self, parentWindow, xyPoint):
        event = ZEditControlContextMenuEvent(self.GetId(), self,  parentWindow, xyPoint)
        self._fireEvent(event)
    # end _fireContextMenuEvent()

    #
    # --- interface impl. --
    #
    def hasCapability(self, capabilityId):
        return self.getCapabilities().hasCapability(capabilityId)
    # end hasCapability()

    def isFormattingEnabled(self, capabilityId): #@UnusedVariable
        return False
    # end isFormattingEnabled()

    def getFormattingState(self, capabilityId): #@UnusedVariable
        return False
    # end getFormattingState()

    def applyFormatting(self, capabilityId, customData): #@UnusedVariable
        pass
    # end applyFormatting()

    def createSpellCheckContext(self):
        return None
    # end createSpellCheckContext()

    def createFindReplaceContext(self):
        return None
    # end createFindReplaceContext()
    
    def getCaretPosition(self):
        return (-1, -1)
    # end getCaretPosition()
    
# end ZBaseEditControl

