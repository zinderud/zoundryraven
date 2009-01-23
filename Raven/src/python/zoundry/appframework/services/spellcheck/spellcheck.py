from zoundry.appframework.engine.service import IZService


# ------------------------------------------------------------------------------------
# An interface for a spell check dictionary language.  The spell checker service will
# contain a list of languages that it supports.  The list of languages is a list of
# objects of this type.
# ------------------------------------------------------------------------------------
class IZSpellCheckDictionaryLanguage:

    def getDisplayName(self):
        u"""getDisplayName() -> string
        Returns the display name for this language (English, Spanish, etc).""" #$NON-NLS-1$
    # end getDisplayName()

    def getLanguageCode(self):
        u"""getLanguageCode() -> string
        Gets the language code for this dictionary.""" #$NON-NLS-1$
    # end getLanguageCode()

    def getDictionaryType(self):
        u"""getDictionaryType() -> string
        Gets the dictionary type (for example, 'aspell').""" #$NON-NLS-1$
    # end getDictionaryType()

    def getDictionaryHandler(self):
        u"""getDictionaryHandler() -> string
        Gets the dictionary handler.  This will be an extension ID
        that corresponds to some plugin contribution.""" #$NON-NLS-1$
    # end getDictionaryHandler()

    def getDictionaryUrl(self):
        u"""getDictionaryUrl() -> string
        Returns the URL to use to download the dictionary.""" #$NON-NLS-1$
    # end getDictionaryUrl()

# end IZSpellCheckDictionaryLanguage


# ------------------------------------------------------------------------------------
# Interface for an auto-correct dictionary.  An auto-correct dictionary is responsible
# for maintaining a list of mappings from commonly mis-spelled words to their correct
# spelling.  This list is typically used so that as a user is typing, if they spell
# a word incorrectly, the word is automatically corrected for them.
# ------------------------------------------------------------------------------------
class IZAutoCorrectDictionary:

    def addAutoCorrection(self, word, replacement):
        u"""addAutoCorrection(string, string) -> None
        Adds an auto-correct mapping to the dictionary.""" #$NON-NLS-1$
    # end addAutoCorrection()

    def removeAutoCorrection(self, word):
        u"""removeAutoCorrection(string) -> None
        Removes an auto-correct mapping from the dictionary.""" #$NON-NLS-1$
    # end removeAutoCorrection()

    def getAutoCorrections(self):
        u"""getAutoCorrections() -> map[string -> string]
        Gets all of the auto-correct mappings in the dictionary.""" #$NON-NLS-1$
    # end getAutoCorrections()

    def getAutoCorrection(self, word):
        u"""getAutoCorrection(string) -> string
        Gets the correct spelling for the given mis-spelled word.""" #$NON-NLS-1$
    # end getAutoCorrection()

    def clearAutoCorrections(self):
        u"""clearAutoCorrections() -> None
        Clears all auto-correct mappings.""" #$NON-NLS-1$
    # end clearAutoCorrections()

# end IZAutoCorrectDictionary


# ------------------------------------------------------------------------------------
# Interface for a personal dictionary.  A personal dictionary is a way for the user
# to augment the dictionary for the given language, in order to add correct spellings
# for words the user commonly uses (but aren't in the built-in dictionary for the
# language).
# ------------------------------------------------------------------------------------
class IZPersonalDictionary:

    def addWord(self, word):
        u"""addWord(string) -> None
        Adds the word to the dictionary.""" #$NON-NLS-1$
    # end addWord()
    
    def addWords(self, words):
        u"""addWords(string []) -> None
        Adds multiple words to the ditionary.""" #$NON-NLS-1$
    # end addWords()

    def removeWord(self, word):
        u"""removeWord(string) -> None
        Removes the word from the dictionary.""" #$NON-NLS-1$
    # end removeWord()

    def getWords(self):
        u"""getWords() -> string []
        Gets a list of all words in the dictionary.""" #$NON-NLS-1$
    # end getWords()

    def clearPersonalDictionary(self):
        u"""clearPersonalDictionary() -> None
        Removes all words from the dictionary.""" #$NON-NLS-1$
    # end clearPersonalDictionary()

# end IZPersonalDictionary


# ------------------------------------------------------------------------------------
# This interface is implemented by spell checkers in the system.  Spell checkers are
# managed by the spell checker service.  A spell checker is also an auto-correct
# dictionary and a personal dictionary.  This enables it to fully spell check words
# as well as automatically fix them when possible.
# ------------------------------------------------------------------------------------
class IZSpellChecker(IZAutoCorrectDictionary, IZPersonalDictionary):

    def check(self, word):
        u"""check(string) -> boolean
        Returns True if the word is spelled correctly.""" #$NON-NLS-1$
    # end check()

    def suggest(self, word):
        u"""suggest(string) -> string []
        Returns a list of suggested words for a mis-spelled word.""" #$NON-NLS-1$
    # end suggest()

    def autoCorrect(self, word):
        u"""autoCorrect(string) -> string
        Returns the correct spelling of a mis-spelled word if an auto-correct
        mapping exists for that mis-spelled word.  If no auto-correct mapping
        exists, this returns None.""" #$NON-NLS-1$
    # end autoCorrect()

    def destroy(self):
        u"""destroy() -> None
        Called when the spell checker is no longer needed.""" #$NON-NLS-1$
    # end destroy()

# end IZSpellChecker


# ------------------------------------------------------------------------------------
# An interface for listening to spell checker events.
# ------------------------------------------------------------------------------------
class IZSpellCheckerListener:
    
    def onAutoCorrectionAdded(self, fromWord, toWord):
        u"""onAutoCorrectionAdded(string, string) -> None
        Called when an auto-correction is added to the spell checker.""" #$NON-NLS-1$
    # end onAutoCorrectionAdded()
    
    def onAutoCorrectionRemoved(self, word):
        u"""onAutoCorrectionRemoved(string) -> None
        Called when an auto-correction is removed from the spell
        checker.""" #$NON-NLS-1$
    # end onAutoCorrectionRemoved()
    
    def onAutoCorrectionsCleared(self):
        u"""onAutoCorrectionsCleared() -> None
        Called when the auto corrections are cleared from the spell
        checker.""" #$NON-NLS-1$
    # end onAutoCorrectionsCleared()
    
    def onPersonalDictionaryWordAdded(self, word):
        u"""onPersonalDictionaryWordAdded(string) -> None
        Called when a word is added to the personal dictionary.""" #$NON-NLS-1$
    # end onPersonalDictionaryWordAdded()

    def onPersonalDictionaryWordRemoved(self, word):
        u"""onPersonalDictionaryWordRemoved(string) -> None
        Called when a word is removed from the spell checker's
        personal dictionary.""" #$NON-NLS-1$
    # end onPersonalDictionaryWordRemoved()
    
    def onPersonalDictionaryCleared(self):
        u"""onPersonalDictionaryCleared() -> None
        Called when the personal dictionary words are 
        cleared.""" #$NON-NLS-1$
    # end onPersonalDictionaryCleared(()
    
# end IZSpellCheckerListener


# ------------------------------------------------------------------------------------
# A listener interface for listening to spell checker service events.
# ------------------------------------------------------------------------------------
class IZSpellCheckServiceListener:

    def onSpellcheckEnabled(self, spellChecker):
        u"""onSpellcheckEnabled(IZSpellChecker) -> None
        Called when spellcheck becomes enabled.""" #$NON-NLS-1$
    # end onSpellcheckEnabled()

    def onSpellcheckDisabled(self):
        u"""onSpellcheckDisabled() -> None
        Called when spellcheck becomes disabled.""" #$NON-NLS-1$
    # end onSpellcheckDisabled()

# end IZSpellCheckServiceListener


# ------------------------------------------------------------------------------------
# The interface for the spell checker service.
# ------------------------------------------------------------------------------------
class IZSpellCheckService(IZService):

    def getSupportedLanguages(self):
        u"""getSupportedLanguages() -> IZSpellCheckDictionaryLanguage []
        Returns a list of languages for which spell checkers exist.""" #$NON-NLS-1$
    # end getSupportedLanguages()

    def isSpellcheckEnabled(self):
        u"""isSpellcheckEnabled() -> boolean
        Returns True if the spellcheck feature is enabled.  If this returns
        True, then a call to getActiveSpellChecker() will return an
        instance of IZSpellChecker.  If this method returns false, then
        getActiveSpellChecker() will return None.""" #$NON-NLS-1$
    # end isSpellcheckEnabled()

    def getActiveSpellChecker(self):
        u"""getActiveSpellChecker() -> IZSpellChecker
        Returns the currently active/enabled spell checker.""" #$NON-NLS-1$
    # end getActiveSpellChecker()

    def enableSpellCheck(self, langCode):
        u"""enableSpellCheck(string) -> IZSpellChecker
        Enables spell checking by settings the active spell checker
        to the one for the given language (and returning it).  This
        method throws an exception if spell check cannot be enabled
        for some reason (e.g. a dictionary is currently being 
        downloaded, or there is no dictionary for the given 
        language).  Raises a ZRestartApplicationException if the
        app needs to be restarted for the change to take effect.""" #$NON-NLS-1$
    # end enableSpellCheck()

    def disableSpellCheck(self):
        u"""disableSpellCheck() -> None
        Disables spell checking.  This will destroy the current spell
        checker (if any) and None it out.  It will also set the user's
        preferences to 'spellcheck-enabled' = False.""" #$NON-NLS-1$
    # end disableSpellCheck()

    def isDictionaryDownloaded(self, langCode):
        u"""isDictionaryDownloaded(string) -> boolean
        Returns True if the dictionary for the given language has been
        downloaded.""" #$NON-NLS-1$
    # end isDictionaryDownloaded()

    def downloadDictionary(self, langCode):
        u"""downloadDictionary(string) -> IZBackgroundTask
        Downloads the dictionary for the given language.  This
        method will create a background task and kick it off.
        The caller is responsible for displaying the background
        task in some meaningful way to the user.""" #$NON-NLS-1$
    # end downloadDictionary()
    
    def getDictionaryDownloadTask(self):
        u"""getDictionaryDownloadTask() -> IZBackgroundTask
        Gets the task responsible for downloading the dictionary.  This
        task will be an in-progress task or None.""" #$NON-NLS-1$
    # end getDictionaryDownloadTask()

# end IZSpellCheckService
