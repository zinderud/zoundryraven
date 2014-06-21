from locale import getdefaultlocale
from zoundry.appframework.constants import IZAppServiceIDs
from zoundry.appframework.constants import IZAppUserPrefsKeys
from zoundry.appframework.services.i18nservice.i18nservice import IZI18NService
from zoundry.appframework.services.i18nservice.i18nserviceio import loadCountryCodes
from zoundry.appframework.services.i18nservice.i18nserviceio import loadLanguageCodes
from zoundry.base.constants import IZI18NConstants
from zoundry.base.util.fileutil import getDirectoryListing
from zoundry.base.util.i18n import ZLocale
import os
import re
import string


BUNDLE_FILE_PATTERN = re.compile(r"zoundry.blogapp_([^\.]+)\.xml") #$NON-NLS-1$


# ---------------------------------------------------------------------------------------
# An implementation of the i18n service.
# ---------------------------------------------------------------------------------------
class ZI18NService(IZI18NService):

    def __init__(self):
        self.countryCodes = []
        self.langCodes = []
        self.locale = None
    # end __init__()

    def start(self, applicationModel):
        self.applicationModel = applicationModel
        self.logger = applicationModel.getEngine().getService(IZAppServiceIDs.LOGGER_SERVICE_ID)
        
        self.locale = self._configureLocale()

        self._loadCountryCodes()
        self._loadLanguageCodes()
        self.logger.debug(u"I18N Service started [%d country codes, %d language codes loaded]." % (len(self.countryCodes), len(self.langCodes)) ) #$NON-NLS-1$
    # end start()

    def stop(self):
        self.countryCodes = []
        self.langCodes = []
    # end stop()

    def getCountryCodes(self):
        return self.countryCodes
    # end getCountryCodes()

    def getLanguageCodes(self):
        return self.langCodes
    # end getLanguageCodes()
    
    def findCountryCode(self, countryCodeString):
        if countryCodeString is None:
            return None

        countryCodeString = string.lower(countryCodeString)
        for countryCode in self.countryCodes:
            if countryCode.getCode() == countryCodeString:
                return countryCode
        return None
    # end findCountryCode()
    
    def findCountryCodeForLocale(self, locale):
        zlocale = ZLocale(locale)
        return self.findCountryCode(zlocale.getCountryCode())
    # end findCountryCodeForLocale()

    def findLanguageCode(self, langCodeString):
        if langCodeString is None:
            return None

        langCodeString = string.lower(langCodeString)
        for langCode in self.langCodes:
            if langCode.getISO639_1Code() == langCodeString or langCode.getISO639_2Code() == langCodeString:
                return langCode
        return None
    # end findLanguageCode()
    
    def findLanguageCodeForLocale(self, locale):
        zlocale = ZLocale(locale)
        return self.findLanguageCode(zlocale.getLanguageCode())
    # end findLanguageCodeForLocale()

    def setLocaleOverride(self, localeCode):
        userPrefs = self.applicationModel.getUserProfile().getPreferences()
        userPrefs.setUserPreference(IZAppUserPrefsKeys.LOCALE, localeCode)
        self.locale = localeCode
    # end setLocaleOverride()

    def clearLocaleOverride(self):
        userPrefs = self.applicationModel.getUserProfile().getPreferences()
        userPrefs.setUserPreference(IZAppUserPrefsKeys.LOCALE, u"") #$NON-NLS-1$
    # end clearLocaleOverride()

    def getLocale(self):
        return self.locale
    # end getLocale()

    def getDefaultLocale(self):
        (locale, _dummy) = getdefaultlocale()
        return locale
    # end getDefaultLocale()

    def getInstalledLanguagePacks(self):
        sysProfile = self.applicationModel.getSystemProfile()
        bundleDir = sysProfile.getBundleDirectory()
        
        def _filterLangPacks(filePath):
            return re.match(BUNDLE_FILE_PATTERN, os.path.basename(filePath)) is not None
        # end _filterLangPacks()
        
        locales = [ u"en_US" ] #$NON-NLS-1$
        
        files = getDirectoryListing(bundleDir, _filterLangPacks)
        for file in files:
            file = os.path.basename(file)
            match = re.match(BUNDLE_FILE_PATTERN, file)
            localeStr = match.group(1)
            locales.append(localeStr)
        
        return locales
    # end getInstalledLanguagePacks()

    def _loadCountryCodes(self):
        countryCodesFile = self.applicationModel.getResourceRegistry().getResourcePath(u"countrycodes.xml") #$NON-NLS-1$
        self.countryCodes = loadCountryCodes(countryCodesFile)
    # end _loadCountryCodes()

    def _loadLanguageCodes(self):
        langCodesFile = self.applicationModel.getResourceRegistry().getResourcePath(u"langcodes.xml") #$NON-NLS-1$
        self.langCodes = loadLanguageCodes(langCodesFile)
    # end _loadLanguageCodes()

    def _configureLocale(self):
        userPrefs = self.applicationModel.getUserProfile().getPreferences()
        localeOverride = userPrefs.getUserPreference(IZAppUserPrefsKeys.LOCALE, u"") #$NON-NLS-1$
        if localeOverride:
            os.environ[IZI18NConstants.LOCALE_ENV_VAR] = localeOverride
            return localeOverride
        (locale, _dummy) = getdefaultlocale()
        return locale
    # end _configureLocale()

# end ZI18NService
