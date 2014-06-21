from zoundry.appframework.constants import IZAppNamespaces
from zoundry.appframework.services.spellcheck.spellcheck import IZSpellCheckDictionaryLanguage
from zoundry.base.zdom.dom import ZDom

LANG_CODE_ATTR = u"lang-code" #$NON-NLS-1$
DISPLAY_NAME_ATTR = u"display-name" #$NON-NLS-1$
HANDLER_ATTR = u"handler" #$NON-NLS-1$
TYPE_ATTR = u"type" #$NON-NLS-1$
URL_ATTR = u"url" #$NON-NLS-1$


# ---------------------------------------------------------------------------------------
# The implementation of a spell check dictionary language.  This class effectively 
# represents a single element in a "dictionaries.xml" file.
# ---------------------------------------------------------------------------------------
class ZSpellCheckDictionaryLanguage(IZSpellCheckDictionaryLanguage):
    
    def __init__(self, langCode, displayName, dictHandler, dictType, dictUrl):
        self.langCode = langCode
        self.displayName = displayName
        self.dictHandler = dictHandler
        self.dictType = dictType
        self.dictUrl = dictUrl
    # end __init__()

    def getLanguageCode(self):
        return self.langCode
    # end getLanguageCode()

    def getDisplayName(self):
        return self.displayName
    # end getDisplayName()

    def getDictionaryHandler(self):
        return self.dictHandler
    # end getDictionaryHandler()

    def getDictionaryType(self):
        return self.dictType
    # end getDictionaryType()

    def getDictionaryUrl(self):
        return self.dictUrl
    # end getDictionaryUrl()
    
# end ZSpellCheckDictionaryLanguage


# ---------------------------------------------------------------------------------------
# Creates a ZSpellCheckDictionaryLanguage from a node in a dictionaries.xml file.
# ---------------------------------------------------------------------------------------
def _createSpellCheckDictionaryLanguage(node):
    langCode = node.getAttribute(LANG_CODE_ATTR)
    displayName = node.getAttribute(DISPLAY_NAME_ATTR)
    handler = node.getAttribute(HANDLER_ATTR)
    type = node.getAttribute(TYPE_ATTR)
    url = node.getAttribute(URL_ATTR)
    
    return ZSpellCheckDictionaryLanguage(langCode, displayName, handler, type, url)
# end _createSpellCheckDictionaryLanguage


# ---------------------------------------------------------------------------------------
# Loads the information in a dictionaries.xml file.
# ---------------------------------------------------------------------------------------
def loadDictionariesXML(filePath):
    u"""loadDictionariesXML(string) -> IZSpellCheckDictionaryLanguage []
    Loads the dictionaries.xml file at the given path and parses
    it into a list of IZSpellCheckDictionaryLanguage objects.""" #$NON-NLS-1$
    dom = ZDom()
    dom.load(filePath)
    nssMap = { u"ns" : IZAppNamespaces.RAVEN_DICTIONARIES_NAMESPACE } #$NON-NLS-1$
    nodes = dom.selectNodes(u"/ns:dictionaries/ns:dictionary", nssMap) #$NON-NLS-1$
    return map(_createSpellCheckDictionaryLanguage, nodes)
# end loadDictionariesXML()
