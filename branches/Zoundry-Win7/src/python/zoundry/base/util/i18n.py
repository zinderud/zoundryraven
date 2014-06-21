from locale import getdefaultlocale
from zoundry.base.constants import IZI18NConstants
from zoundry.base.zdom.dom import ZDom
import os

SB_NSS_MAP = {
    u"sb" : u"http://www.zoundry.com/schemas/2006/06/zbundle.rng" #$NON-NLS-1$ #$NON-NLS-2$
}

# Create a string bundle using the given root bundle file and locale.  The actual file that
# gets loaded is determined by appending the locale to the end of the root bundle file name
# (before the file extension).  So, for example, if the root file name is "/Temp/bundle.xml" 
# and the locale is "en_GB", the bundle that gets loaded will be "/Temp/bundle_en_GB.xml".
#
# Note: if the bundle file does not exist, then an empty bundle will be created (no error).
# Note: if "None" is passed for the locale, then the root file itself will be used.
#
class ZStringBundle:

    def __init__(self, rootFileName, locale):
        self.rootFileName = rootFileName
        self.locale = locale
        self.bundleMap = {}

        self._loadBundleFile()
    # end __init__()

    def _loadBundleFile(self):
        fname = self.rootFileName
        
        if self.locale is not None:
            dname = os.path.dirname(fname)
            bname = os.path.basename(fname)
            (name, ext) = os.path.splitext(bname)
            fname = os.path.join(dname, u"%s_%s%s" % (name, self.locale, ext)) #$NON-NLS-1$

        if os.path.isfile(fname):
            self._loadBundle(fname)
    # end _loadBundleFile()

    def _loadBundle(self, bundleFilename):
        # Load the file and read in all its string mappings.
        dom = ZDom()
        dom.load(bundleFilename)
        dom.setNamespaceMap(SB_NSS_MAP)

        nl = dom.selectNodes(u"/sb:string-bundle/sb:string") #$NON-NLS-1$
        for n in nl:
            name = n.getAttribute(u"name") #$NON-NLS-1$
            val = n.getText()
            val = val.replace(u"\\n", u"\n") #$NON-NLS-2$ #$NON-NLS-1$
            val = val.replace(u"\\t", u"\t") #$NON-NLS-2$ #$NON-NLS-1$
            self.bundleMap[name] = val
    # end _loadBundleFile()

    def getString(self, name):
        if self.bundleMap.has_key(name):
            return self.bundleMap[name]
        else:
            return None
    # end getString()

# end ZStringBundle


# ------------------------------------------------------------------------------------
# The bundle collection class holds a map of string bundles.  Each string bundle is
# mapped to its specific locale.  Whenever a string is requested, this class will 
# check all of the appropriate bundles in order, from most specific to least specific.
# This class allows for the possibility of creating the bundle collection prior to 
# actually knowing what the locale will be.  Once the locale is set (in the os.environ), 
# then this class will change which bundle(s) it is actually using to get strings from.
# ------------------------------------------------------------------------------------
class ZBundleCollection:

    def __init__(self, defaultBundleFilename):
        self.defaultBundleFilename = defaultBundleFilename
        self.defaultBundle = self._createBundle(None)
        self.bundles = {}
    # end __init__()
    
    # Gets the current locale list.  This breaks down the current locale into its
    # parts, from most specific to least specific.  For example, if the current locale
    # is en_GB, then this method will return:  ['en_GB', 'en']
    def _getCurrentLocaleList(self):
        currentLocale = self._getCurrentLocale()
        genericLocale = ZLocale(currentLocale).getLanguageCode()
        if currentLocale == genericLocale:
            return [ currentLocale ]
        else:
            return [ currentLocale, genericLocale ]
    # end _getCurrentLocaleList()

    def _getCurrentLocale(self):
        locale = None
        # Try the environment (which should be set up already and can be changed dynamically).
        if IZI18NConstants.LOCALE_ENV_VAR in os.environ:
            locale = os.environ[IZI18NConstants.LOCALE_ENV_VAR]

        # Then try the getdefaultlocale() function.
        if not locale:
            (locale, _dummy) = getdefaultlocale()

        return locale
    # end _getCurrentLocale()

    def _createBundle(self, locale):
        return ZStringBundle(self.defaultBundleFilename, locale)
    # end _createBundle()

    def _getBundle(self, locale):
        bundle = None
        try:
            bundle = self.bundles[locale]
        except:
            bundle = self._createBundle(locale)
            self.bundles[locale] = bundle
        return bundle
    # end getBundle()

    def getString(self, key):
        locales = self._getCurrentLocaleList()
        for locale in locales:
            value = self._getBundle(locale).getString(key)
            if value is not None:
                return value
        
        return self.defaultBundle.getString(key)
    # end getString()

# end ZBundleCollection


# ------------------------------------------------------------------------------------
# Implementation of a locale.  This basically wraps a locale string of the form en_US.
# This class provides access to the generic and specific parts of the locale.
# ------------------------------------------------------------------------------------
class ZLocale:

    def __init__(self, localeString):
        (self.languageCode, self.countryCode) = self._parseLocaleString(localeString)
    # end __init__()
    
    def getLanguageCode(self):
        return self.languageCode
    # end getLanguageCode()
    
    def getCountryCode(self):
        return self.countryCode
    # end getCountryCode()
    
    def hasCountryCode(self):
        return self.countryCode is not None
    # end hasCountryCode()
    
    def toString(self):
        if self.hasCountryCode():
            return u"%s_%s" % (self.languageCode, self.countryCode) #$NON-NLS-1$
        else:
            return self.languageCode
    # end toString()
    
    def _parseLocaleString(self, localeString):
        components = localeString.split(u"_") #$NON-NLS-1$
        countryCode = None
        if (len(components) == 2):
            countryCode = components[1]
        return (components[0], countryCode)
    # end _parseLocaleString()
    
# end ZLocale
