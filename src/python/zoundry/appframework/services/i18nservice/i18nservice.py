from zoundry.appframework.engine.service import IZService

# ---------------------------------------------------------------------------------------
# Represents a single country code.
# ---------------------------------------------------------------------------------------
class IZCountryCode:

    def getName(self):
        u"""getName() -> string
        Returns the country name.""" #$NON-NLS-1$
    # end getName()
    
    def getCode(self):
        u"""getCode() -> string
        Returns the country code.""" #$NON-NLS-1$
    # end getCode()
    
# end IZCountryCode


# ---------------------------------------------------------------------------------------
# Represents a single language code.  
# ---------------------------------------------------------------------------------------
class IZLanguageCode:

    def getName(self):
        u"""getName() -> string
        Returns the language name.""" #$NON-NLS-1$
    # end getName()

    def getDefaultCode(self):
        u"""getDefaultCode() -> string
        Gets the default (2-character) code for this language.""" #$NON-NLS-1$
    # end getDefaultCode()
    
    def getISO639_1Code(self):
        u""""getISO639_1Code() -> string
        Gets the 2 character ISO 639_1 code for the language.""" #$NON-NLS-1$
    # end getISO639_1Code()

    def getISO639_2Code(self):
        u""""getISO639_2Code() -> string
        Gets the 2 character ISO 639_2 code for the language.""" #$NON-NLS-1$
    # end getISO639_1Code()

    def getCountryCodes(self):
        u"""getCountryCodes() -> string []
        Gets a list of country codes associated with the language.""" #$NON-NLS-1$
    # end getCountryCodes()

# end IZLanguageCode


# ---------------------------------------------------------------------------------------
# This interface defines the internationalization service.  The i18n service is 
# responsible for managing i18n information in the application, including country and
# language codes for all (most) world languages/countries.  In addition, this service
# manages i18n information specific to this application/user profile, including getting
# and setting the current locale, as well as getting a list of "language packs", which
# are String Bundle files for the application.
# ---------------------------------------------------------------------------------------
class IZI18NService(IZService):

    def getCountryCodes(self):
        u"""getCountryCodes() -> IZCountryCode []
        Returns a list of country codes.""" #$NON-NLS-1$
    # end getCountryCodes()

    def getLanguageCodes(self):
        u"""getLanguageCodes() -> IZLanguageCode []
        Returns a list of language codes.""" #$NON-NLS-1$
    # end getLanguageCodes
    
    def findCountryCode(self, countryCodeString):
        u"""findCountryCode(string) -> IZCountryCode
        Given a country code string (us, sv, etc...), this
        method returns the IZCountryCode for that country,
        or None if not found.""" #$NON-NLS-1$
    # end findCountryCode()
    
    def findCountryCodeForLocale(self, locale):
        u"""findCountryCodeForLocale(string) -> IZCountryCode
        Given the locale, returns the appropriate country
        code.  A locale will not always have a country code
        associated with it, in which case None will be
        returned.""" #$NON-NLS-1$
    # end findCountryCodeForLocale()

    def findLanguageCode(self, langCodeString):
        u"""findLanguageCode(string) -> IZLanguageCode
        Given the language code string (en, fr, etc...),
        this returns the IZLanguageCode for that language,
        or None if not found.""" #$NON-NLS-1$
    # end findLanguageCode()
    
    def findLanguageCodeForLocale(self, locale):
        u"""findLanguageCodeForLocale(string) -> IZLanguageCode
        Given the locale, returns the language code for that
        locale.  The locale will always have a language 
        component to it, so this method will probably always
        return a value.  However, if an unknown code is 
        passed, then None will be returned.""" #$NON-NLS-1$
    # end findLanguageCodeForLocale()
    
    def setLocaleOverride(self, localeCode):
        u"""setLocaleOverride(string) -> None
        Sets the current user's locale override.  This will likely 
        require the user to restart the application.""" #$NON-NLS-1$
    # end setLocaleOverride()

    def clearLocaleOverride(self):
        u"""clearLocaleOverride() -> None
        Clears the current user's locale override.  This will likely 
        require the user to restart the application.""" #$NON-NLS-1$
    # end clearLocaleOverride()

    def getLocale(self):
        u"""getLocale() -> 
        Returns the current locale.  This is typically found in
        the user profile.""" #$NON-NLS-1$
    # end getLocale()

    def getDefaultLocale(self):
        u"""getDefaultLocale() -> string
        Returns the default system locale code.""" #$NON-NLS-1$
    # end getDefaultLocale()
    
    def getInstalledLanguagePacks(self):
        u"""getInstalledLanguagePacks() -> string []
        Returns a list of locale strings, one for each installed
        language pack.  A language pack is, effectively, several
        string bundles that contain the text of the application
        for a particular language (to allow speakers of a given
        language to use the application.""" #$NON-NLS-1$
    # end getInstalledLanguagePacks()

# end IZI18NService
