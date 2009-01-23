# ------------------------------------------------------------------------------
# Spell check context controller that can be implemented by data models (such as the mshtml control)
# and used by UI dialogs such as a SpellCheck dialog.
# ------------------------------------------------------------------------------
from zoundry.base.util.text.textutil import getNoneString
import sets

class IZSpellCheckContext:

    def initialize(self, spellChecker):
        u"""initialize(IZSpellChecker) - void
        Initialize spellcheck process with the backend IZSpellChecker implementation.
        This method is called eachtime spellcheck is run.""" #$NON-NLS-1$
    # end initialize()

    def cleanup(self):
        u"""cleanup() - void
        Called after completing the spellcheck process to allow the context to clean up any resources.""" #$NON-NLS-1$
    # end cleanup()

    def getWord(self):
        u"""getWord() -> string
            Returns the current word or None if not available.""" #$NON-NLS-1$
    # end getWord()

    def check(self):
        u"""check() -> IZSpellCheckResult
        Performs a spellcheck from the last known location and returns a IZSpellCheckResult object.""" #$NON-NLS-1$
    # end check()

    def ignore(self):
        u"""ignore() -> void
        Ignores the current word i.e. skip to next word.""" #$NON-NLS-1$
    # end ignore()

    def ignoreAll(self):
        u"""ignoreAll() -> void
        Ignores all occurances of the current word.""" #$NON-NLS-1$
    # end ignoreAll()

    def replace(self, replaceWord):
        u"""replace(string) -> void
        Replaces the current word with the replacement.""" #$NON-NLS-1$
    # end replace()

    def replaceAll(self, replaceWord):
        u"""replaceAll(string)
        Replaces all occurances of the current word with the replacement.""" #$NON-NLS-1$
    # end replaceAll()

    def addWord(self, word):
        u"""addWord(string) -> void
        Adds the given word to the personal dictionary via underlying IZSpellChecker object.""" #$NON-NLS-1$
    # end addWord()

# end IZSpellCheckContext

# ------------------------------------------------------------------------------
# Result after running IZSpellCheckContext::check
# ------------------------------------------------------------------------------
class IZSpellCheckResult:

    SPELLCHECKER_NOT_AVAILABLE = 0 # spell check engine is not available or not initialized.
    FINISHED = 1 # spell check completed
    MISSPELL = 2 # misspelled word
    INVERTED_CASE = 3 # caps lock typos. Eg. pYTHON -> should be Python.

    # word location type.
    LOCATION_TYPE_BODY = 0
    LOCATION_TYPE_ATTR = 1

    def isFinished(self):
        u"""isFinished() -> bool
        Returns true if the spell check of the document is complete."""  #$NON-NLS-1$
    # end isFinished()

    def getCode(self):
        u"""getCode() -> int
        Returns result status code such as FINISHED, MISPELLED and INVERTED_CASE."""  #$NON-NLS-1$
    # end getCode()

    def getWordLocationType(self):
        u"""getWordLocationType() -> int
        Returns result's mispelled word location type such as in the body of text or meta data attributes."""  #$NON-NLS-1$
    # end getWordLocationType()

    def getWord(self):
        u"""getWord() -> string
        Returns the mispelled word"""  #$NON-NLS-1$
    # end getWord()

    def getWordContext(self):
        u"""getWordContext() -> string
        Returns sentence enclosing the mispelled word or None if not available."""  #$NON-NLS-1$
    # end getWordContext()

    def setWordContext(self, wordContext):
        u"""setWordContext(string) -> void
        Sets sentence enclosing the mispelled word."""  #$NON-NLS-1$
    # end setWordContext()

    def getRangeInContext(self):
        u"""getRangeInContext() -> (int, int)
        Returns the character positions of the mispelled word with in the context sentence.
        The return value is a tuple(startPos, endPos). The values maybe -1 if the range cannot be located."""  #$NON-NLS-1$
    # end getRangeInContext()

    def setRangeInContext(self, startRangePos, endRangePos): #@UnusedVariable
        u"""setRangeInContext(int, int) -> void
        Sets the character positions of the mispelled word with in the context sentence.
        The values should -1 if the range cannot be located."""  #$NON-NLS-1$
    # end setRangeInContext()

    def getSuggestions(self):
        u"""getSuggestions() -> list
        Returns list of alternate words from the underlying IZSpellChecker."""  #$NON-NLS-1$
    # end getSuggestions()

# end IZSpellCheckResult

# ------------------------------------------------------------------------------
# Impl. of  IZSpellCheckContext
# ------------------------------------------------------------------------------
class ZSpellCheckResult(IZSpellCheckResult):

    def __init__(self, code, word):
        self.code = code
        self.word = word
        # words or sentence around misspelled word.
        self.wordContext = None
        # position of misspelled word within context.
        self.startRangePos = -1
        self.endRangePos = -1
        self.wordLocationType = IZSpellCheckResult.LOCATION_TYPE_BODY
        self.suggestionList = []

    def isFinished(self):
        return self.getCode() == IZSpellCheckResult.FINISHED
    # end isFinished()

    def getCode(self):
        return self.code
    # end getCode()

    def getWordLocationType(self):
        return self.wordLocationType
    # end getWordLocationType()

    def setWordLocationType(self, wordLocationType):
        self.wordLocationType = wordLocationType
    # end setWordLocationType()

    def getWord(self):
        return self.word
    # end getWord()

    def getWordContext(self):
        return self.wordContext
    # end getWordContext()

    def setWordContext(self, wordContext):
        self.wordContext = wordContext
    # end setWordContext()

    def getRangeInContext(self):
        return (self.startRangePos, self.endRangePos)
    # end getRangeInContext()

    def setRangeInContext(self, startRangePos, endRangePos):
        self.startRangePos = -1
        if startRangePos is not None and startRangePos >= 0:
            self.startRangePos = startRangePos

        self.endRangePos = -1
        if endRangePos is not None and endRangePos >= self.startRangePos:
            self.endRangePos = endRangePos
    # end setRangeInContext()

    def getSuggestions(self):
        return self.suggestionList
    # end getSuggestions()

    def setSuggestions(self, suggestionList):
        self.suggestionList = suggestionList
    # end setSuggestions()

# end ZSpellCheckResult


# FIXME (PJ) support AUTOCORRECT. ie. check(autocorrect = True))
# FIXME (PJ) import spell check words, auto corrects etc.


#------------------------------------------------
# Global set of words that are flagged as ignore.
#------------------------------------------------
gIGNORE_WORD_SET = sets.Set([])

#------------------------------------------------
# Base/abstract impl of IZSpellCheckContext
#------------------------------------------------
class ZBaseSpellCheckContext(IZSpellCheckContext):

    NON_ALPHANUM = u""".,<>:;"'/\\[]{}+=-_()*&^%$#@!`|""" #$NON-NLS-1$

    def __init__(self):
        self.spellChecker = None
        self.currentWord = None
        # list of words that have been used with ReplaceAll
        self.replaceAllSet = sets.Set([])
    # end __init__()

    def _getSpellChecker(self):
        u"""_getSpellChecker() -> IZSpellChecker""" #$NON-NLS-1$
        return self.spellChecker
    # end _getSpellChecker()

    def _hasSpellChecker(self):
        u"""_hasSpellChecker() -> bool""" #$NON-NLS-1$
        return self._getSpellChecker() is not None
    # end _hasSpellChecker()

    def _setWord(self, word):
        self.currentWord = word
    # end _setWord

    def _addIgnore(self, word):
        u"""Adds the given word to a global ignore list.""" #$NON-NLS-1$
        word = getNoneString(word)
        if word:
            global gIGNORE_WORD_SET
            gIGNORE_WORD_SET.add(word.lower())
    # end _addIgnore()

    def _shouldIgnore(self, word):
        u"""Returns true if the given word should be ignored.""" #$NON-NLS-1$
        # check the global ignore set as well as per instance replaceAllSet
        word = getNoneString(word)
        if not word:
            return True
        global gIGNORE_WORD_SET
        return word.lower() in gIGNORE_WORD_SET or word in self.replaceAllSet
    # end _shouldIgnore()

    def _getSuggestionList(self, word):
        u"""Returns a list of suggested words for the given word.""" #$NON-NLS-1$
        word = getNoneString(word)
        if word and self._getSpellChecker():
            return self._getSpellChecker().suggest(word)
        else:
            return []
    # end _getSuggestionList()

    def _isCaseInverted(self, word):
        u"""Returns true if the case is inverted. Eg. pYTHON instead of Python.""" #$NON-NLS-1$
        word = getNoneString(word)
        rVal = False
        if word and len(word) > 2 and not word.isdigit():
            invWord = word[0].lower() + word[1:].upper()
            rVal = word == invWord
        return rVal
    # end _isCaseInverted()

    def _isAlphaNum(self, word):
        u"""Returns true if the word contains only non-alpha numeric characters."""  #$NON-NLS-1$
        rVal = False
        word = getNoneString(word)
        if word:
            count = 0
            for c in word:
                if c in ZBaseSpellCheckContext.NON_ALPHANUM:
                    count = count + 1
            rVal = count == len(word)
        return rVal
    # end _isAlphaNum()

    def _isMisspelled(self, word):
        u"""Returns true if the given word is not in the dictionary.""" #$NON-NLS-1$
        word = getNoneString(word)
        if word and self._getSpellChecker():
            return not self._getSpellChecker().check(word)
        else:
            return True
    # end _isMisspelled()

    #------------------------------------------
    # interface methods
    #------------------------------------------

    def initialize(self, spellChecker):
        self.spellChecker = spellChecker
        self._initialize()
    # end initialize()

    def cleanup(self):
        self._cleanup()
    # end cleanup()

    def getWord(self):
        return self.currentWord
    # end getWord()

    def check(self):
        if not self._getSpellChecker():
            return ZSpellCheckResult(IZSpellCheckResult.SPELLCHECKER_NOT_AVAILABLE, None)

        word = self._getNextWord()
        self._setWord(word)
        result = None
        while word is not None:
            word = word.strip()
            self._setWord(word)
            if not word.isdigit() and not self._shouldIgnore(word):
                bInverted = self._isCaseInverted(word)
                bMisspell = self._isMisspelled(word)
                if bInverted or bMisspell:
                    rCode = IZSpellCheckResult.MISSPELL
                    if bInverted:
                        rCode = IZSpellCheckResult.INVERTED_CASE
                    result = ZSpellCheckResult(rCode, word)
                    if bMisspell:
                        result.setSuggestions( self._getSuggestionList(word) )
                    self._prepareResult(result)
                    break
            word = self._getNextWord()
        if word is None:
            result = ZSpellCheckResult(IZSpellCheckResult.FINISHED, None)
        return result
    # end check()

    def ignore(self):
        pass
    # end ignore()

    def ignoreAll(self):
        self._addIgnore( self.getWord() )
    # end ignoreAll()

    def replace(self, replaceWord):
        replaceWord = getNoneString(replaceWord)
        if replaceWord:
            self._replace(replaceWord, False)
    # end replace()

    def replaceAll(self, replaceWord):
        replaceWord = getNoneString(replaceWord)
        if replaceWord:
            self._replace(replaceWord, True)
            # since it has been replaced, we need to add this to a replaceAll set so that it is not looked up again. (i.e. ignored)
            self.replaceAllSet.add(replaceWord)
    # end replaceAll()

    def addWord(self, word):
        word = getNoneString(word)
        if word and self._getSpellChecker():
            self._getSpellChecker().addWord(word)
    # end addWord()

    #------------------------------------------
    # abstract methods
    #------------------------------------------

    def _initialize(self):
        u"""_initialize() - void
        Called when the spellcheck session needs to be initialized to start spellcheck.""" #$NON-NLS-1$
    # end _initialize()

    def _cleanup(self):
        u"""_cleanup() - void
        Called after completing the spellcheck process to allow the context to clean up any resources.""" #$NON-NLS-1$
    # end _cleanup()

    def _prepareResult(self, spellcheckResult): #@UnusedVariable
        u"""Lets the subclass impl. further set additional data (e.g sentence/context) about the result before being returned to the UI code.""" #$NON-NLS-1$
        pass
    # end _prepareResult

    def _getNextWord(self):
        u"""Returns the next word in the document or None if the end is reached.
        This method must be implemented by the subclass.""" #$NON-NLS-1$
        return None
    # end _getNextWord()

    def _replace(self, replaceWord, replaceAll=False): #@UnusedVariable
        u"""Called when the current word needs to be replaced in the document.""" #$NON-NLS-1$
        pass
    # end _replace()

# end ZBaseSpellCheckContext
