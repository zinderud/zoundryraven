from zoundry.appframework.constants import IZAppServiceIDs
from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.services.spellcheck.spellcheckcontext import IZSpellCheckResult
from zoundry.base.util.text.textutil import getSafeString

#-------------------------------
# Spellchecker dialog model
#-------------------------------
class ZSpellCheckModel:

    def __init__(self, spellcheckContext):
        u"""
        __init__(IZEditControlSpellCheckContext)
        Initializes model with the spellcheck context.
        """ #$NON-NLS-1$
        self.spellcheckContext = spellcheckContext
        self.spellcheckResult = None
        self.spellcheckService = getApplicationModel().getService(IZAppServiceIDs.SPELLCHECK_SERVICE_ID)
        self.initialized = False
    # end __init__()

    def isSpellcheckEnabled(self):
        u"""isSpellcheckEnabled() -> boolean
        Returns True if the spellcheck feature is enabled.  """ #$NON-NLS-1$
        return self.spellcheckService.isSpellcheckEnabled()
        # IZSpellChecker = getActiveSpellChecker
    # end isSpellcheckEnabled()

    def initializeSpellcheckContext(self):
        u"""initializeSpellcheckContext() -> void
        Initialized the spellcheck context with IZSpellChecker.""" #$NON-NLS-1$
        if self.isSpellcheckEnabled() and not self.initialized and self.spellcheckContext:
            self.spellcheckContext.initialize( self.spellcheckService.getActiveSpellChecker() )
            self.initialized = True
    # end initializeSpellcheckContext()

    def cleanupSpellcheckContext(self):
        u"""cleanupSpellcheckContext() -> void
        Allows spellcheck context to clean up any resources.""" #$NON-NLS-1$
        self.initialized = False
        if self.spellcheckContext:
            self.spellcheckContext.cleanup()
    # cleanupSpellcheckContext()

    def getSpellCheckResult(self):
        u"""getSpellCheckResult() -> IZSpellCheckResult or None
        Returns the IZSpellCheckResult from the last time check() was run.
        Returns None if spell check was not run. """ #$NON-NLS-1$
        return self.spellcheckResult
    # end getSpellCheckResult()

    def checkNextWord(self):
        self.spellcheckResult = None
        if self.initialized:
            self.spellcheckResult = self.spellcheckContext.check()
        return self.spellcheckResult
    # end checkNextWord()

    def ignore(self, ignoreAll):
        if self.initialized and ignoreAll:
            self.spellcheckContext.ignoreAll()
        elif self.initialized:
            self.spellcheckContext.ignore()
    # end ignore()

    def replace(self, replaceWord, replaceAll):
        if self.initialized and replaceWord and replaceAll:
            self.spellcheckContext.replaceAll(replaceWord)
        elif self.initialized and replaceWord:
            self.spellcheckContext.replace(replaceWord)
    # end replace()

    def addWord(self):
        if self.initialized and self.spellcheckContext.getWord():
            # add current word to personal dictionary.
            newWord = self.spellcheckContext.getWord()
            self.spellcheckContext.addWord(newWord)
    # end addWord()

    def getSuggestions(self, spellCheckResult):
        u"""getSuggestions(IZSpellCheckResult) -> list
        Returns list of strings that are alternate suggestions based on the current result.
        """ #$NON-NLS-1$
        if not spellCheckResult:
            return []

        sList = spellCheckResult.getSuggestions()
        # if the error was inverted case, then add the corrected version to the suggestion list.
        if spellCheckResult.getCode() == IZSpellCheckResult.INVERTED_CASE and spellCheckResult.getWord():
            try:
                sList.insert(0, spellCheckResult.getWord().title())
            except:
                pass
        return sList
    # end getCurrentSuggestions()

    def getMisspelledWordData(self, spellCheckResult):
        u"""getMisspelledWordData(IZSpellCheckResult) -> (string, int, int)
        Returns tuple (misspelled_sentence, startPos, endPos) based on the current result.
        The misspelled_sentence includes the misspelled word and any surrounding words.
        startPos and endPos are the character position of the misspelled word within
        the misspelled_sentence.
        """ #$NON-NLS-1$
        sentence = u"" #$NON-NLS-1$
        startPos = 0
        endPos = 0
        if spellCheckResult:
            try:
                if spellCheckResult.getWordContext():
                    sentence = spellCheckResult.getWordContext()
                    (startPos, endPos) = spellCheckResult.getRangeInContext()
                else:
                    sentence = getSafeString( spellCheckResult.getWord() ).strip()
                    endPos = len(sentence)
            except:
                pass
        #
        return (sentence, startPos, endPos)
    # end getMisspelledWordData()

# end ZSpellCheckModel