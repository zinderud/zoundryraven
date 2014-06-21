from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.ui.widgets.controls.advanced.editcontrol import IZEditControlFindReplaceTextContext
from zoundry.base.util.text.textutil import getNoneString
from zoundry.base.util.types.list import ZBoundedMruList
from zoundry.base.util.xml.deserializers import ZXMLToStringListDeserializer
from zoundry.base.util.xml.serializers import ZStringListToXMLSerializer
from zoundry.blogapp.constants import IZUserPropertiesPaths

# In memory version of find/replace history.
gFIND_LIST = []
gREPLACE_LIST = []

# ------------------------------------------------------------------------------
# Base impl. of edit control find replace context
# ------------------------------------------------------------------------------
class ZBaseEditControlFindReplaceTextContext(IZEditControlFindReplaceTextContext):

    def __init__(self):
        self.matchCase = False
        self.matchWholeWord = False
        self.searchForward = True
        self.text = None
        self.findHistory = ZBoundedMruList(10)
        self.replaceHistory = ZBoundedMruList(10)
    # end __init__()

    def loadHistory(self):
        userProps = getApplicationModel().getUserProfile().getProperties()
        deserializer = ZXMLToStringListDeserializer()

        findHistoryNode = userProps.getPropertyNode(IZUserPropertiesPaths.FIND_REPLACE_DIALOG_FIND_LIST)
        if findHistoryNode is not None:
            strListNode = findHistoryNode.selectSingleNode(u"child::*") #$NON-NLS-1$
            if strListNode is not None:
                deserializedList = deserializer.deserialize(strListNode)
                deserializedList.reverse()
                self.findHistory.addAll(deserializedList)
        replaceHistoryNode = userProps.getPropertyNode(IZUserPropertiesPaths.FIND_REPLACE_DIALOG_REPLACE_LIST)
        if replaceHistoryNode is not None:
            strListNode = replaceHistoryNode.selectSingleNode(u"child::*") #$NON-NLS-1$
            if strListNode is not None:
                deserializedList = deserializer.deserialize(strListNode)
                deserializedList.reverse()
                self.replaceHistory.addAll(deserializedList)
    # end _loadHistory()

    def saveHistory(self):
        userProps = getApplicationModel().getUserProfile().getProperties()

        serializer = ZStringListToXMLSerializer()

        findNode = serializer.serialize(self.findHistory)
        userProps.setProperty(IZUserPropertiesPaths.FIND_REPLACE_DIALOG_FIND_LIST, findNode)

        replaceNode = serializer.serialize(self.replaceHistory)
        userProps.setProperty(IZUserPropertiesPaths.FIND_REPLACE_DIALOG_REPLACE_LIST, replaceNode)
    # end saveHistory()

    def initialize(self):
        self.loadHistory()
        self._initialize()
    # end initialize()

    def cleanup(self):
        self.saveHistory()
        self._higlightText(False)
        self._cleanup()
    # end cleanup()

    def reset(self):
        self._reset()
    # end reset()

    def isCaseSensitive(self):
        return self.matchCase
    # end isCaseSensitive

    def setCaseSensitive(self, b):
        self.matchCase = b
    # end setCaseSensitive

    def isMatchWord(self):
        return self.matchWholeWord
    # end isMatchWord()

    def setMatchWord(self, b):
        self.matchWholeWord = b
    # end setMatchWord()

    def isSearchForward(self):
        return self.searchForward
    # end isSearchForward()

    def setSearchForward(self, b):
        self.searchForward = b
    # end setSearchForward()

    def getText(self):
        return self.text
    # end getText()

    def setText(self, text):
        self.text = getNoneString(text)
        if text:
            self.findHistory.add(text)
    # end setText()

    def find(self):
        rval = False
        if self.getText() is not None:
            rval = self._findNext()
            if rval:
                self._higlightText(True)
        return rval
    # end find()

    def replace(self, replaceText):
        if replaceText:
            self.replaceHistory.add(replaceText)
        self._replace(replaceText, False)
    # end replace()

    def replaceAll(self, replaceText):
        if replaceText:
            self.replaceHistory.add(replaceText)
        self._replace(replaceText, True)
    # end replaceAll()

    def getFindTextHistory(self):
        return self.findHistory
    # end getFindTextHistory()

    def getReplaceTextHistory(self):
        return self.replaceHistory
    # end getReplaceTextHistory()

    # -- methods to be implemented by the subclass. --

    def _initialize(self):
        u"""_initialize() -> void
        Called when the find/replace session needs to be initialized.""" #$NON-NLS-1$
    # end _cleanup()

    def _cleanup(self):
        u"""_cleanup() -> void
        Called when the user is done with find/replace.""" #$NON-NLS-1$
    # end _cleanup()

    def _reset(self):
        u"""_reset() -> void
        Called when a new find/replace is started (from the begining).""" #$NON-NLS-1$
    # end _reset()

    def _findNext(self):
        u"""_findNext() -> void
        Find the text. Returns true if found.
        This method must be implemented by the subclass.""" #$NON-NLS-1$
        return False
    # end _findNext()

    def _replace(self, replaceText, replaceAll): #@UnusedVariable
        u"""_replace(string, bool) -> void
        Called when the current text needs to be replaced.""" #$NON-NLS-1$
        pass
    # end _replace()

    def _higlightText(self, on): #@UnusedVariable
        u"""_higlightText(bool) -> void
        Called when the current text needs to be highlighted and brought/scrolled into view.
        If bOn is false, then the current higlight should be switched off.
        """ #$NON-NLS-1$
        pass
    # end _higlightText()


# end ZBaseEditControlSpellCheckContext
