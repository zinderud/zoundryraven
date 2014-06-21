from zoundry.appframework.constants import IZAppNamespaces
from zoundry.appframework.services.spellcheck.dictionariesio import ZSpellCheckDictionaryLanguage
from zoundry.appframework.services.spellcheck.spellcheck import IZSpellChecker
from zoundry.base.util.classloader import ZClassLoader
from zoundry.base.util.collections import ZListenerSet
from zoundry.base.zdom.dom import ZDom
import os
import string

# -------------------------------------------------------------------------------------
# Deserializes a spell checker.  Takes a path to the spell checker directory, and
# returns an ZSpellChecker object.
# -------------------------------------------------------------------------------------
class ZSpellCheckerDeserializer:
    
    def deserialize(self, path):
        u"""deserialize(string) -> ZSpellChecker""" #$NON-NLS-1$
        fpath = os.path.join(path, u"spellchecker.xml") #$NON-NLS-1$
        dom = ZDom()
        dom.load(fpath)
        dom.setNamespaceMap({ u"ns" : IZAppNamespaces.RAVEN_SPELLCHECKER_NAMESPACE }) #$NON-NLS-1$
        spellcheckerElem = dom.documentElement
        
        dictionaryLanguage = self._deserializeDictionaryLanguage(spellcheckerElem)
        provider = self._deserializeProvider(spellcheckerElem, dictionaryLanguage)
        personalWordList = self._deserializePersonalDictionary(spellcheckerElem)
        autoCorrections = self._deserializeAutoCorrections(spellcheckerElem)
        
        return ZSpellChecker(path, dictionaryLanguage, provider, personalWordList, autoCorrections)
    # end deserialize()
    
    def _deserializeDictionaryLanguage(self, spellcheckerElem):
        languageElem = spellcheckerElem.selectSingleNode(u"ns:language") #$NON-NLS-1$
        langCode = languageElem.getAttribute(u"lang-code") #$NON-NLS-1$
        dictHandler = languageElem.getAttribute(u"handler") #$NON-NLS-1$
        dictType = languageElem.getAttribute(u"type") #$NON-NLS-1$
        dispName = languageElem.getAttribute(u"display-name") #$NON-NLS-1$
        url = languageElem.getAttribute(u"url") #$NON-NLS-1$
        return ZSpellCheckDictionaryLanguage(langCode, dispName, dictHandler, dictType, url)
    # end _deserializeDictionaryLanguage()
    
    def _deserializeProvider(self, spellcheckerElem, dictionaryLanguage):
        providerElem = spellcheckerElem.selectSingleNode(u"ns:provider") #$NON-NLS-1$
        providerClassname = providerElem.getText()
        providerClass = ZClassLoader().loadClass(providerClassname)
        return providerClass(dictionaryLanguage)
    # end _deserializeProvider()
    
    def _deserializePersonalDictionary(self, spellcheckerElem):
        personalWordList = []

        personalDictionaryWordElems = spellcheckerElem.selectNodes(u"ns:personal-dictionary/ns:word") #$NON-NLS-1$
        for wordElem in personalDictionaryWordElems:
            word = wordElem.getText()
            personalWordList.append(word)
        
        return personalWordList
    # end _deserializePersonalDictionary()
    
    def _deserializeAutoCorrections(self, spellcheckerElem):
        autoCorrections = {}
        
        autoCorrectionElems = spellcheckerElem.selectNodes(u"ns:auto-corrections/ns:auto-correction") #$NON-NLS-1$
        for acElem in autoCorrectionElems:
            key = acElem.getAttribute(u"word") #$NON-NLS-1$
            value = acElem.getText()
            autoCorrections[key] = value
        
        return autoCorrections
    # end _deserializeAutoCorrections()
    
# end ZSpellCheckerDeserializer


# -------------------------------------------------------------------------------------
# Serializes a spell checker to file.  Takes a ZSpellChecker object and a path to the 
# spell checker directory, and saves the spell checker to that directory.
# -------------------------------------------------------------------------------------
class ZSpellCheckerSerializer:
    
    def serialize(self, spellChecker, path):
        u"""serialize(ZSpellChecker, string) -> None
        Serializes a spell checker to a string.  The path is a directory.""" #$NON-NLS-1$
        dom = ZDom()
        dom.loadXML(u"""<spellchecker xmlns="%s" />""" % IZAppNamespaces.RAVEN_SPELLCHECKER_NAMESPACE) #$NON-NLS-1$
        spellCheckerElem = dom.documentElement
        self._serializeDictionaryLanguage(spellCheckerElem, spellChecker.dictionaryLang)
        self._serializeProvider(spellCheckerElem, spellChecker.provider)
        self._serializePersonalDictionary(spellCheckerElem, spellChecker.personalWordList)
        self._serializeAutoCorrections(spellCheckerElem, spellChecker.autoCorrections)
        
        if not os.path.isdir(path):
            os.makedirs(path)
        filePath = os.path.join(path, u"spellchecker.xml") #$NON-NLS-1$
        dom.save(filePath, True)
    # end serialize()

    def _serializeDictionaryLanguage(self, parentElem, dictionaryLang):
        languageElem = self._createElement(parentElem, u"language") #$NON-NLS-1$
        languageElem.setAttribute(u"lang-code", dictionaryLang.getLanguageCode()) #$NON-NLS-1$
        languageElem.setAttribute(u"handler", dictionaryLang.getDictionaryHandler()) #$NON-NLS-1$
        languageElem.setAttribute(u"type", dictionaryLang.getDictionaryType()) #$NON-NLS-1$
        languageElem.setAttribute(u"display-name", dictionaryLang.getDisplayName()) #$NON-NLS-1$
        languageElem.setAttribute(u"url", dictionaryLang.getDictionaryUrl()) #$NON-NLS-1$
        parentElem.appendChild(languageElem)
    # end _serializeDictionaryLanguage()

    def _serializeProvider(self, parentElem, provider):
        providerElem = self._createElement(parentElem, u"provider") #$NON-NLS-1$
        providerElem.setText(unicode(provider.__class__))
        parentElem.appendChild(providerElem)
    # end _serializeProvider()

    def _serializePersonalDictionary(self, parentElem, personalWordList):
        personalDictElem = self._createElement(parentElem, u"personal-dictionary") #$NON-NLS-1$
        for word in personalWordList:
            wordElem = self._createElement(personalDictElem, u"word") #$NON-NLS-1$
            wordElem.setText(word)
            personalDictElem.appendChild(wordElem)
        parentElem.appendChild(personalDictElem)
    # end _serializePersonalDictionary()
    
    def _serializeAutoCorrections(self, parentElem, autoCorrections):
        autoCorrectionsElem = self._createElement(parentElem, u"auto-corrections") #$NON-NLS-1$
        for acKey in autoCorrections:
            acValue = autoCorrections[acKey]
            autoCorrectionElem = self._createElement(autoCorrectionsElem, u"auto-correction") #$NON-NLS-1$
            autoCorrectionElem.setAttribute(u"word", acKey) #$NON-NLS-1$
            autoCorrectionElem.setText(acValue)
            autoCorrectionsElem.appendChild(autoCorrectionElem)
        parentElem.appendChild(autoCorrectionsElem)
    # end _serializeAutoCorrections()

    def _createElement(self, parentElem, tagName):
        return parentElem.ownerDocument.createElement(tagName, IZAppNamespaces.RAVEN_SPELLCHECKER_NAMESPACE)
    # end _createElement()
    
# end ZSpellCheckerSerializer


# ---------------------------------------------------------------------------------------
# Implementation of a IZSpellChecker.  This class uses a spell check provider in order
# to supply the implementation of the check() and suggest() methods.
# ---------------------------------------------------------------------------------------
class ZSpellChecker(IZSpellChecker):

    def __init__(self, directoryPath, dictionaryLang, provider, personalWordList = None, autoCorrections = None):
        self.directoryPath = directoryPath
        self.listeners = ZListenerSet()
        self.builtInDictionary = []
        self.dictionaryLang = dictionaryLang # An IZSpellCheckDictionaryLanguage
        self.provider = provider # An IZSpellCheckProvider
        self.personalWordList = personalWordList # A List of strings
        self.autoCorrections = autoCorrections # A Map of string -> string
        
        if self.personalWordList is None:
            self.personalWordList = []
        if self.autoCorrections is None:
            self.autoCorrections = {}
    # end __init__()

    def addListener(self, listener):
        self.listeners.append(listener)
    # end addListener()

    def removeListener(self, listener):
        self.listeners.remove(listener)
    # end removeListener()
    
    def setBuiltInDictionary(self, builtInDictionary):
        self.builtInDictionary = builtInDictionary
    # end setBuiltInDictionary()

    def check(self, word):
        lword = string.lower(word)
        
        # Check the built-in dictionary
        if lword in self.builtInDictionary:
            return True
        # Check the personal dictionary
        if lword in self.personalWordList:
            return True
        
        # Use the provider
        return self.provider.check(word)
    # end check()

    def suggest(self, word):
        return self.provider.suggest(word)
    # end suggest()
    
    def autoCorrect(self, word):
        lword = string.lower(word)
        if lword in self.autoCorrections:
            newWord = self.autoCorrections[lword]
            if self._isCapitalized(word):
                newWord = string.capitalize(newWord)
            return newWord
        return None
    # end autoCorrect()

    def destroy(self):
        self.provider.destroy()
    # end destroy()

    def addAutoCorrection(self, word, replacement):
        self.autoCorrections[string.lower(word)] = replacement
        self._save()
        for listener in self.listeners:
            listener.onAutoCorrectionAdded(word, replacement)
    # end addAutoCorrection()

    def removeAutoCorrection(self, word):
        lword = string.lower(word)
        if lword in self.autoCorrections:
            del self.autoCorrections[lword]
            self._save()
            for listener in self.listeners:
                listener.onAutoCorrectionRemoved(word)
    # end removeAutoCorrection()

    def getAutoCorrections(self):
        return self.autoCorrections
    # end getAutoCorrections()

    def getAutoCorrection(self, word):
        lword = string.lower(word)
        if lword in self.autoCorrections:
            return self.autoCorrections[lword]
        return None
    # end getAutoCorrection()

    def clearAutoCorrections(self):
        self.autoCorrections = {}
        self._save()
        for listener in self.listeners:
            listener.onAutoCorrectionsCleared()
    # end clearAutoCorrections()

    def addWord(self, word):
        lword = string.lower(word)
        if not lword in self.personalWordList:
            self.personalWordList.append(lword)
            self._save()
            for listener in self.listeners:
                listener.onPersonalDictionaryWordAdded(word)
    # end addWord()
    
    def addWords(self, words):
        for word in words:
            lword = string.lower(word)
            if not lword in self.personalWordList:
                self.personalWordList.append(lword)
                for listener in self.listeners:
                    listener.onPersonalDictionaryWordAdded(word)
        self._save()
    # end addWords()

    def removeWord(self, word):
        lword = string.lower(word)
        if not lword in self.personalWordList:
            del self.personalWordList[lword]
            self._save()
            for listener in self.listeners:
                listener.onPersonalDictionaryWordRemoved(word)
    # end removeWord()

    def getWords(self):
        return self.personalWordList
    # end getWords()

    def clearPersonalDictionary(self):
        self.personalWordList = []
        self._save()
        for listener in self.listeners:
            listener.onPersonalDictionaryCleared()
    # end clearPersonalDictionary()

    def _save(self):
        serializer = ZSpellCheckerSerializer()
        serializer.serialize(self, self.directoryPath)
    # end _save()
    
    def _isCapitalized(self, word):
        return word == string.capitalize(word)
    # end _isCapitalized()

# end ZSpellChecker
