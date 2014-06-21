from zoundry.appframework.global_services import getApplicationModel
from zoundry.base.exceptions import ZException
from zoundry.base.util.fileutil import getDirectoryListing
from zoundry.base.util.i18n import ZLocale
from zoundry.base.util.types.list import ZSortedList
from zoundry.base.zdom.dom import ZDom
from zoundry.blogapp.constants import IZBlogAppServiceIDs
from zoundry.base.util.fileutil import deleteFile
from zoundry.appframework.global_services import getLoggerService
from zoundry.base.util.schematypes import ZSchemaDateTime
import codecs
import shutil
import os

JOURNAL = True
DEBUG = True

BUNDLE_NS = u"http://www.zoundry.com/schemas/2006/06/zbundle.rng" #$NON-NLS-1$
BUNDLE_TEMPLATE = u"""<zb:string-bundle xmlns:zb="http://www.zoundry.com/schemas/2006/06/zbundle.rng" locale="%s" xml:space="preserve" />""" #$NON-NLS-1$

# ------------------------------------------------------------------------------
# The model used by the translation manager.
# ------------------------------------------------------------------------------
class ZTranslationManagerModel:

    def __init__(self):
        systemProfile = getApplicationModel().getSystemProfile()
        self.bundleDirectory = systemProfile.getBundleDirectory()
        self.i18nService = getApplicationModel().getService(IZBlogAppServiceIDs.I18N_SERVICE_ID)

        self.defaultTranslation = self._loadDefaultTranslation(self.bundleDirectory)
        self.defaultTranslation.load()
        self.translations = self._loadTranslations(self.bundleDirectory)
    # end __init__()

    def findCountryCode(self, countryCodeStr):
        return self.i18nService.findCountryCode(countryCodeStr)
    # end findCountryCode()

    def getDefaultTranslation(self):
        return self.defaultTranslation
    # end getDefaultTranslation()

    def getTranslations(self):
        return self.translations
    # end getTranslations()

    def getLanguageCodes(self):
        return self.i18nService.getLanguageCodes()
    # end getLanguageCodes()

    def getNameForLocale(self, locale):
        displayName = u"Unknown Language" #$NON-NLS-1$

        langCode = self.i18nService.findLanguageCode(locale.getLanguageCode())
        if langCode:
            displayName = langCode.getName()

        countryCode = self.i18nService.findCountryCode(locale.getCountryCode())
        if countryCode:
            displayName = u"%s (%s)" % (displayName, countryCode.getName()) #$NON-NLS-1$

        return displayName
    # end getNameForLocale()

    def createNewTranslation(self, localeStr):
        translation = self._findTranslation(localeStr)
        if translation is not None:
            return translation

        locale = ZLocale(localeStr)
        translation = ZTranslation(locale, self.bundleDirectory)
        self.translations.append(translation)
        translation.save(self.defaultTranslation)
        return translation
    # end createNewTranslation()

    def getSystemLocale(self):
        return self.i18nService.getDefaultLocale()
    # end getSystemLocale()

    def _findTranslation(self, localeStr):
        for translation in self.translations:
            if translation.getLocale().toString() == localeStr:
                return translation
        return None
    # end _findTranslation()

    def _loadDefaultTranslation(self, bundleDirectory):
        return ZDefaultTranslation(bundleDirectory)
    # end _loadDefaultTranslation()

    def _loadTranslations(self, bundleDirectory):

        def filterFunc(fileName):
            fileName = os.path.basename(fileName)
            return fileName.startswith(u"zoundry.base_") #$NON-NLS-1$
        # end filterFunc()

        rval = ZSortedList(self)
        for bundleFileName in getDirectoryListing(bundleDirectory, filterFunc, False):
            localeString = self._extractLocale(bundleFileName)
            locale = ZLocale(localeString)
            translation = ZTranslation(locale, bundleDirectory)
            translation.load()
            rval.append(translation)
        return rval
    # end _loadTranslations()

    def _extractLocale(self, bundleFileName):
        bundleFileName = os.path.basename(bundleFileName)
        return bundleFileName[13:bundleFileName.rindex(u".xml")] #$NON-NLS-1$
    # end _extractLocale()

    # ----
    # The following two methods are impls of the IZComparator interface
    # ----

    def compare(self, object1, object2):
        name1 = self.getNameForLocale(object1.getLocale())
        name2 = self.getNameForLocale(object2.getLocale())
        if name1 == name2:
            return 0
        if name1 < name2:
            return -1
        return 1
    # end compare()

    def equals(self, object1, object2):
        return self.compare(object1, object2) == 0
    # end equals()

# end ZTranslationManagerModel


# ------------------------------------------------------------------------------
# Represents a single translation.
# ------------------------------------------------------------------------------
class ZTranslation:

    def __init__(self, locale, bundleDirectory):
        self.bundleDirectory = bundleDirectory
        self.locale = locale
        self.bundleStrings = {}
        self.loaded = False
        self.journalFile = None
    # end __init__()

    def getDisplayText(self):
        langCode = self.locale.getLanguageCode()
        countryCode = self.locale.getCountryCode()
        if countryCode:
            return u"%s_%s" % (langCode, countryCode) #$NON-NLS-1$
        else:
            return langCode
    # end getDisplayText()

    def getLocale(self):
        return self.locale
    # end getLocale()

    def isDefault(self):
        return False
    # end isDefault()

    def load(self):
        if not self.loaded:
            self._loadBundleStrings()
            self.loaded = True
    # end load()

    def clear(self):
        self.loaded = False
        self.bundleStrings = {}
        self._journal(u"--clear--") #$NON-NLS-1$
        self._closeJournal()
    # end clear()

    def getBundleStrings(self):
        return self.bundleStrings
    # end getBundleStrings()

    def _loadBundleStrings(self):
        baseFileName = os.path.join(self.bundleDirectory, u"zoundry.base_%s.xml" % self.locale.toString()) #$NON-NLS-1$
        appFrameworkFileName = os.path.join(self.bundleDirectory, u"zoundry.appframework_%s.xml" % self.locale.toString()) #$NON-NLS-1$
        blogAppFileName = os.path.join(self.bundleDirectory, u"zoundry.blogapp_%s.xml" % self.locale.toString()) #$NON-NLS-1$

        self._loadBundleStringsFromFile(baseFileName, self.bundleStrings)
        self._loadBundleStringsFromFile(appFrameworkFileName, self.bundleStrings)
        self._loadBundleStringsFromFile(blogAppFileName, self.bundleStrings)
    # end _loadBundleStrings()

    def _loadBundleStringsFromFile(self, fileName, stringMap):
        nsMap = { u"zb" : u"http://www.zoundry.com/schemas/2006/06/zbundle.rng" } #$NON-NLS-1$ #$NON-NLS-2$
        dom = ZDom()
        dom.load(fileName)
        stringElems = dom.selectNodes(u"/zb:string-bundle/zb:string", nsMap) #$NON-NLS-1$
        for stringElem in stringElems:
            key = stringElem.getAttribute(u"name") #$NON-NLS-1$
            value = stringElem.getText()
            stringMap[key] = value
    # end _loadBundleStringsFromFile()

    def hasBundleString(self, key):
        return key in self.bundleStrings
    # end hasBundleString()

    def setBundleString(self, key, value):
        self.bundleStrings[key] = value
        self._journal(u"--setBundleString-- Key: [[%s]]  Value: [[%s]]", (key, value)) #$NON-NLS-1$
    # end setBundleString()

    def clearBundleString(self, key):
        if key in self.bundleStrings:
            del self.bundleStrings[key]
        self._journal(u"--clearBundleString-- Key: [[%s]]", key) #$NON-NLS-1$
    # end clearBundleString()

    def save(self, defaultTranslation):
        self._journal(u"--save--") #$NON-NLS-1$

        localeStr = self.locale.toString()
        baseFileName = os.path.join(self.bundleDirectory, u"zoundry.base_%s.xml" % localeStr) #$NON-NLS-1$
        appFrameworkFileName = os.path.join(self.bundleDirectory, u"zoundry.appframework_%s.xml" % localeStr) #$NON-NLS-1$
        blogAppFileName = os.path.join(self.bundleDirectory, u"zoundry.blogapp_%s.xml" % localeStr) #$NON-NLS-1$

        if DEBUG:
            outputLogFileName = os.path.join(self.bundleDirectory, u"debug_save_%s.log" % localeStr) #$NON-NLS-1$
            outputLog = open(outputLogFileName, u"w") #$NON-NLS-1$
        self.debug(outputLog, u"Saving translation") #$NON-NLS-1$

        try:
            baseDom = ZDom()
            baseDom.loadXML(BUNDLE_TEMPLATE % localeStr)
            baseDom.documentElement.addTextNode(u"\n") #$NON-NLS-1$
            self.debug(outputLog, u"baseDom created") #$NON-NLS-1$
            appFrameworkDom = ZDom()
            appFrameworkDom.loadXML(BUNDLE_TEMPLATE % localeStr)
            appFrameworkDom.documentElement.addTextNode(u"\n") #$NON-NLS-1$
            self.debug(outputLog, u"appFrameworkDom created") #$NON-NLS-1$
            blogAppDom = ZDom()
            blogAppDom.loadXML(BUNDLE_TEMPLATE % localeStr)
            blogAppDom.documentElement.addTextNode(u"\n") #$NON-NLS-1$
            self.debug(outputLog, u"blogAppDom created") #$NON-NLS-1$

            bundleStrings = self.getBundleStrings()
            keys = bundleStrings.keys()
            keys.sort()
            for key in keys:
                self.debug(outputLog, u"Writing key: %s" % key) #$NON-NLS-1$
                try:
                    value = bundleStrings[key]
                    dom = None
                    if key in defaultTranslation.getBaseKeys():
                        dom = baseDom
                    elif key in defaultTranslation.getAppFrameworkKeys():
                        dom = appFrameworkDom
                    elif key in defaultTranslation.getBlogAppKeys():
                        dom = blogAppDom
                    elem = dom.documentElement
                    stringElem = dom.createElement(u"zb:string", BUNDLE_NS) #$NON-NLS-1$
                    stringElem.setAttribute(u"name", key) #$NON-NLS-1$
                    stringElem.setText(value)
                    elem.addTextNode(u"    ") #$NON-NLS-1$
                    elem.appendChild(stringElem)
                    elem.addTextNode(u"\n") #$NON-NLS-1$
                except Exception, e:
                    getLoggerService().exception(e)
                self.debug(outputLog, u"Done writing key: %s" % key) #$NON-NLS-1$

            self.debug(outputLog, u"Done writing all keys.") #$NON-NLS-1$
            self.debug(outputLog, u"Backing up old translations.") #$NON-NLS-1$
            backup_baseFileName = os.path.join(self.bundleDirectory, u"BACKUP_zoundry.base_%s.xml" % self.locale.toString()) #$NON-NLS-1$
            backup_appFrameworkFileName = os.path.join(self.bundleDirectory, u"BACKUP_zoundry.appframework_%s.xml" % self.locale.toString()) #$NON-NLS-1$
            backup_blogAppFileName = os.path.join(self.bundleDirectory, u"BACKUP_zoundry.blogapp_%s.xml" % self.locale.toString()) #$NON-NLS-1$
            if os.path.exists(baseFileName):
                shutil.copy2(baseFileName, backup_baseFileName)
            if os.path.exists(appFrameworkFileName):
                shutil.copy2(appFrameworkFileName, backup_appFrameworkFileName)
            if os.path.exists(blogAppFileName):
                shutil.copy2(blogAppFileName, backup_blogAppFileName)

            self.debug(outputLog, u"Saving DOMs") #$NON-NLS-1$

            baseDom.save(baseFileName)
            self.debug(outputLog, u"Successfully saved baseDom") #$NON-NLS-1$
            appFrameworkDom.save(appFrameworkFileName)
            self.debug(outputLog, u"Successfully saved appFrameworkDom") #$NON-NLS-1$
            blogAppDom.save(blogAppFileName)
            self.debug(outputLog, u"Successfully saved blogAppDom") #$NON-NLS-1$

            deleteFile(backup_baseFileName)
            deleteFile(backup_appFrameworkFileName)
            deleteFile(backup_blogAppFileName)

            self.debug(outputLog, u"Deleted backup files.") #$NON-NLS-1$
        finally:
            self._closeJournal()
            if DEBUG:
                outputLog.close()
    # end save()

    def debug(self, outputLog, message):
        if DEBUG:
            outputLog.write(message)
            outputLog.write(u"\n") #$NON-NLS-1$
            outputLog.flush()
    # end debug()

    def _openJournal(self):
        localeStr = self.locale.toString()
        journalFileName = os.path.join(self.bundleDirectory, u"journal_%s.log" % localeStr) #$NON-NLS-1$
        self.journalFile = codecs.open(journalFileName, u"a", u"utf8") #$NON-NLS-1$ #$NON-NLS-2$
        self._journal(u"--journal_open--") #$NON-NLS-1$
    # end _openJournal()

    def _journal(self, message, args = None):
        if not JOURNAL:
            return

        if self.journalFile is None:
            self._openJournal()
        if args is None:
            args = ()
        
        journalMessage = message % args
        dom = ZDom()
        dom.loadXML(u"<journalEntry />") #$NON-NLS-1$
        elem = dom.documentElement
        elem.setAttribute(u"timestamp", unicode(ZSchemaDateTime())) #$NON-NLS-1$
        elem.setText(journalMessage)
        
        self.journalFile.write(elem.serialize())
        self.journalFile.write(u"\n") #$NON-NLS-1$
        self.journalFile.flush()
    # end _journal()

    def _closeJournal(self):
        self._journal(u"--journal_close--") #$NON-NLS-1$
        if self.journalFile is not None:
            self.journalFile.close()
            self.journalFile = None
    # end _closeJournal()

# end ZTranslation


# ------------------------------------------------------------------------------
# The default translation.
# ------------------------------------------------------------------------------
class ZDefaultTranslation(ZTranslation):

    def __init__(self, bundleDirectory):
        ZTranslation.__init__(self, None, bundleDirectory)
    # ene __init__()

    def isDefault(self):
        return True
    # end isDefault()

    def _loadBundleStrings(self):
        baseFileName = os.path.join(self.bundleDirectory, u"zoundry.base.xml") #$NON-NLS-1$
        appFrameworkFileName = os.path.join(self.bundleDirectory, u"zoundry.appframework.xml") #$NON-NLS-1$
        blogAppFileName = os.path.join(self.bundleDirectory, u"zoundry.blogapp.xml") #$NON-NLS-1$

        self._loadBundleStringsFromFile(baseFileName, self.bundleStrings)
        self._loadBundleStringsFromFile(appFrameworkFileName, self.bundleStrings)
        self._loadBundleStringsFromFile(blogAppFileName, self.bundleStrings)
    # end _loadBundleStrings()

    def getBaseKeys(self):
        fileName = os.path.join(self.bundleDirectory, u"zoundry.base.xml") #$NON-NLS-1$
        bundleStrings = {}
        self._loadBundleStringsFromFile(fileName, bundleStrings)
        return bundleStrings.keys()
    # end getBaseKeys()

    def getAppFrameworkKeys(self):
        fileName = os.path.join(self.bundleDirectory, u"zoundry.appframework.xml") #$NON-NLS-1$
        bundleStrings = {}
        self._loadBundleStringsFromFile(fileName, bundleStrings)
        return bundleStrings.keys()
    # end getAppFrameworkKeys()

    def getBlogAppKeys(self):
        fileName = os.path.join(self.bundleDirectory, u"zoundry.blogapp.xml") #$NON-NLS-1$
        bundleStrings = {}
        self._loadBundleStringsFromFile(fileName, bundleStrings)
        return bundleStrings.keys()
    # end getBlogAppKeys()

    def save(self, defaultTranslation):
        raise ZException(u"Cannot save the default translation.") #$NON-NLS-1$
    # end save()

# end ZDefaultTranslation
