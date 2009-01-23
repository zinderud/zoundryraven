
#-------------------------------
# Find and replace text dialog model
#-------------------------------
class ZFindReplaceTextModel:

    def __init__(self, findReplaceContext):
        u"""__init__(IZEditControlFindReplaceTextContext)
        Initializes model with the findreplace context.
        """ #$NON-NLS-1$
        self.findReplaceContext = findReplaceContext
        self.initialized = False
        self.lastFindResult = False
    # end __init__()

    def initializeFindReplaceContext(self):
        u"""initializeFindReplaceContext() -> void
        Initialized the edit control findreplace context""" #$NON-NLS-1$
        self.findReplaceContext.initialize()
        self.initialized = True
    # end initializeFindReplaceContext()

    def cleanupFindReplaceContext(self):
        u"""cleanupFindReplaceContext() -> void
        Allows edit control to cleanup any resources.""" #$NON-NLS-1$
        self.initialized = False
        self.findReplaceContext.cleanup()
    # cleanupFindReplaceContext()

    def getFindTextHistory(self):
        u"""getFindTextHistory() -> list
        Returns a list of strings that were used in previous searches.""" #$NON-NLS-1$
        return self.findReplaceContext.getFindTextHistory()
    # end getFindTextHistory()

    def getReplaceTextHistory(self):
        u"""getReplaceTextHistory() -> list
        Returns a list of replace strings that were used in previous searches.""" #$NON-NLS-1$
        return self.findReplaceContext.getReplaceTextHistory()
    # end getReplaceTextHistory()

    def getFindText(self):
        u"""getFindText() -> string
        Returns initial or last search text used.""" #$NON-NLS-1$
        return self.findReplaceContext.getText()
    # end getFindText()

    def find(self, text, matchWord, caseSensitive):
        u"""find(string, bool, bool) -> bool
        Finds the next word and return True on success.""" #$NON-NLS-1$
        found = False
        if self.initialized:
            self.findReplaceContext.setMatchWord(matchWord)
            self.findReplaceContext.setCaseSensitive(caseSensitive)
            self.findReplaceContext.setText(text)
            found = self.findReplaceContext.find()
            if not found:
                # reset, so that the document can be searched again,
                self.findReplaceContext.reset()
        self.lastFindResult = found
        return found
    # end find()

    def getFindResult(self):
        u"""getFindResult() -> bool
        Returns the last result from the last find action. """ #$NON-NLS-1$
        return self.lastFindResult
    # end getFindResult()

    def replace(self, replaceText, replaceAll):
        u"""replace(string, bool) -> void
        Replaces the last text found with the new text""" #$NON-NLS-1$
        if self.initialized and replaceText is not None and self.lastFindResult:
            if replaceAll:
                self.findReplaceContext.replaceAll(replaceText)
            else:
                self.findReplaceContext.replace(replaceText)
    # end replace()

# end ZFindReplaceTextModel
