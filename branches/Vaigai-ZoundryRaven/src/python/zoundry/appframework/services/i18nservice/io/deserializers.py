from zoundry.appframework.constants import IZAppNamespaces
from zoundry.appframework.services.i18nservice.i18nservice import IZCountryCode
from zoundry.appframework.services.i18nservice.i18nservice import IZLanguageCode


# ---------------------------------------------------------------------------------------
# Represents a single language code.  
# ---------------------------------------------------------------------------------------
class ZLanguageCode(IZLanguageCode):
    
    def __init__(self, name, defaultCode, iso639_1Code, iso639_2Code, countryCodes):
        self.name = name
        self.defaultCode = defaultCode
        self.iso639_1Code = iso639_1Code
        self.iso639_2Code = iso639_2Code
        self.countryCodes = countryCodes
    # end __init__()

    def getName(self):
        return self.name
    # end getName()

    def getDefaultCode(self):
        return self.defaultCode
    # end getDefaultCode()
    
    def getISO639_1Code(self):
        return self.iso639_1Code
    # end getISO639_1Code()

    def getISO639_2Code(self):
        return self.iso639_2Code
    # end getISO639_1Code()

    def getCountryCodes(self):
        return self.countryCodes
    # end getCountryCodes()

# end IZLanguageCode


# ---------------------------------------------------------------------------------------
# Represents a single country code.
# ---------------------------------------------------------------------------------------
class ZCountryCode(IZCountryCode):

    def __init__(self, name, code):
        self.name = name
        self.code = code
    # end __init__()

    def getName(self):
        return self.name
    # end getName()
    
    def getCode(self):
        return self.code
    # end getCode()
    
# end IZCountryCode


# -----------------------------------------------------------------------------------------
# The interface that all country code file deserializers must implement.
# -----------------------------------------------------------------------------------------
class IZCountryCodesDeserializer:

    def deserialize(self, countryCodesDom):
        u"""deserialize(ZDom) -> IZCountryCode []
        Called to deserialize a dom into a list of country codes.""" #$NON-NLS-1$
    # end deserialize()

# end IZCountryCodesDeserializer


# -----------------------------------------------------------------------------------------
# The interface that all country code file deserializers must implement.
# -----------------------------------------------------------------------------------------
class IZLanguageCodesDeserializer:

    def deserialize(self, languageCodesDom):
        u"""deserialize(ZDom) -> IZLanguageCode []
        Called to deserialize a dom into a list of country codes.""" #$NON-NLS-1$
    # end deserialize()

# end IZLanguageCodesDeserializer


# -----------------------------------------------------------------------------------------
# An implementation of a 2006/11 country codes file deserializer.
# -----------------------------------------------------------------------------------------
class ZCountryCodes200611Deserializer(IZCountryCodesDeserializer):

    def __init__(self):
        self.nssMap = { u"zns" : IZAppNamespaces.RAVEN_COUNTRY_CODES_NAMESPACE_2006_11 } #$NON-NLS-1$
    # end __init__()

    def deserialize(self, countryCodesDom):
        countryCodesDom.setNamespaceMap(self.nssMap)
        countryCodesElem = countryCodesDom.documentElement
        
        return self._deserializeCountryCodes(countryCodesElem)
    # end deserialize()

    def _deserializeCountryCodes(self, countryCodesElem):
        nodes = countryCodesElem.selectNodes(u"zns:country-code") #$NON-NLS-1$
        return map(self._deserializeCountryCode, nodes)
    # end _deserializeCountryCodes

    def _deserializeCountryCode(self, countryCodeElem):
        name = countryCodeElem.getAttribute(u"name") #$NON-NLS-1$
        code = countryCodeElem.getText()
        return ZCountryCode(name, code)
    # end _deserializeCountryCode()

# end ZCountryCodes200611Deserializer


# -----------------------------------------------------------------------------------------
# An implementation of a 2006/11 languages codes file deserializer.
# -----------------------------------------------------------------------------------------
class ZLanguageCodes200611Deserializer(IZLanguageCodesDeserializer):

    def __init__(self):
        self.nssMap = { u"zns" : IZAppNamespaces.RAVEN_LANGUAGE_CODES_NAMESPACE_2006_11 } #$NON-NLS-1$
    # end __init__()

    def deserialize(self, languageCodesDom):
        languageCodesDom.setNamespaceMap(self.nssMap)
        languageCodesElem = languageCodesDom.documentElement
        
        return self._deserializeLanguageCodes(languageCodesElem)
    # end deserialize()
    
    def _deserializeLanguageCodes(self, languageCodesElem):
        nodes = languageCodesElem.selectNodes(u"zns:language") #$NON-NLS-1$
        return map(self._deserializeLanguageCode, nodes)
    # end _deserializeLanguageCodes()
    
    def _deserializeLanguageCode(self, languageCodeElem):
        defaultCode = languageCodeElem.getAttribute(u"default-code") #$NON-NLS-1$
        name = languageCodeElem.getAttribute(u"name") #$NON-NLS-1$
        iso639_1Code = self._deserializeISO639_1Code(languageCodeElem)
        iso639_2Code = self._deserializeISO639_2Code(languageCodeElem)
        countryCodes = self._deserializeCountryCodes(languageCodeElem)
        return ZLanguageCode(name, defaultCode, iso639_1Code, iso639_2Code, countryCodes)
    # end _deserializeLanguageCode()

    def _deserializeISO639_1Code(self, languageCodeElem):
        iso639CodeElem = languageCodeElem.selectSingleNode(u"zns:code[@type = 'iso639_1']") #$NON-NLS-1$
        if iso639CodeElem is not None:
            return iso639CodeElem.getText()
        else:
            return None
    # end _deserializeISO639_1Code()

    def _deserializeISO639_2Code(self, languageCodeElem):
        iso639CodeElem = languageCodeElem.selectSingleNode(u"zns:code[@type = 'iso639_2']") #$NON-NLS-1$
        if iso639CodeElem is not None:
            return iso639CodeElem.getText()
        else:
            return None
    # end _deserializeISO639_1Code()
    
    def _deserializeCountryCodes(self, languageCodeElem):
        nodes = languageCodeElem.selectNodes(u"zns:country-codes/zns:country-code") #$NON-NLS-1$
        return map(self._deserializeCountryCode, nodes)
    # end _deserializeCountryCodes()
    
    def _deserializeCountryCode(self, codeElem):
        return codeElem.getText()
    # end _deserializeCountryCode()

# end ZLanguageCodes200611Deserializer
