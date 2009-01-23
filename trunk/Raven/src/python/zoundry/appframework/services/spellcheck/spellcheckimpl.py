from zoundry.appframework.constants import IZAppExtensionPoints
from zoundry.appframework.constants import IZAppNamespaces
from zoundry.appframework.constants import IZAppServiceIDs
from zoundry.appframework.constants import IZAppUserPrefsKeys
from zoundry.appframework.exceptions import ZAppFrameworkException
from zoundry.appframework.exceptions import ZRestartApplicationException
from zoundry.appframework.messages import _extstr
from zoundry.appframework.services.backgroundtask.backgroundtask import IZBackgroundTaskListener
from zoundry.appframework.services.backgroundtask.backgroundtaskimpl import ZBackgroundTask
from zoundry.appframework.services.spellcheck.dictionariesio import loadDictionariesXML
from zoundry.appframework.services.spellcheck.spellcheck import IZSpellCheckService
from zoundry.appframework.services.spellcheck.spellcheckdefs import ZSpellCheckDictionaryHandlerDef
from zoundry.appframework.services.spellcheck.spellcheckdefs import ZSpellCheckProviderDef
from zoundry.appframework.services.spellcheck.spellcheckerimpl import ZSpellChecker
from zoundry.appframework.services.spellcheck.spellcheckerimpl import ZSpellCheckerDeserializer
from zoundry.appframework.services.spellcheck.wordlistio import loadWordListXML
from zoundry.base.exceptions import ZException
from zoundry.base.net.http import IZHttpBinaryFileDownloadListener
from zoundry.base.net.http import ZResumableHttpBinaryFileDownload
from zoundry.base.util.classloader import ZClassLoader
from zoundry.base.util.collections import ZListenerSet
from zoundry.base.util.fileutil import getFileMetaData
from zoundry.base.util.schematypes import ZSchemaDateTime
from zoundry.base.xhtml.xhtmltelements import ZUrl
from zoundry.base.zdom.dom import ZDom
import os

SPELLCHECKER_NAMESPACE_MAP = { u"ns" : IZAppNamespaces.RAVEN_SPELLCHECKER_NAMESPACE } #$NON-NLS-1$

# ---------------------------------------------------------------------------------------
# An interface that all spell check providers must implement.  Plugins can contribute
# new spell check providers in cases where the included 'aspell' based provider is not
# sufficient.
# ---------------------------------------------------------------------------------------
class IZSpellCheckProvider:

    def check(self, word):
        u"""check(string) -> boolean
        Returns True if the word is spelled correctly.""" #$NON-NLS-1$
    # end check()

    def suggest(self, word):
        u"""suggest(string) -> string []
        Returns a list of suggested words for a mis-spelled word.""" #$NON-NLS-1$
    # end suggest()

    def destroy(self):
        u"""destroy() -> None
        Called so that the provider can do any resource cleanup at the
        time it is closed/destroyed.""" #$NON-NLS-1$
    # end destroy()

# end IZSpellCheckProvider


# ---------------------------------------------------------------------------------------
# An interface that defines methods for handling/processing dictionary files when they
# are downloaded.  When a spell check provider is contributed via the appropriate
# extension point, the plugin must also provide an implementation of a dictionary
# handler.  This handler is used by the spell check service when a dictionary file is
# downloaded and must be processed.
#
# For example, the Aspell provider also contributes a dictionary handler that unpacks
# the downloaded dictionary file into the spelling/aspell directory so that the aspell
# library can find the appropriate files.
# ---------------------------------------------------------------------------------------
class IZSpellCheckDictionaryHandler:

    def processDictionaryFile(self, dictionaryFilePath):
        u"""processDictionaryFile(string) -> None
        This method is called by the spell check service after it
        has downloaded a new dictionary.  After the download is
        complete, the provider associated with the downloaded file
        is responsible for doing something meaningful with it.""" #$NON-NLS-1$
    # end processDictionaryFile()

# end IZSpellCheckDictionaryHandler


# ---------------------------------------------------------------------------------------
# The implementation of the spellcheck service.
# ---------------------------------------------------------------------------------------
class ZSpellCheckService(IZSpellCheckService, IZBackgroundTaskListener):

    def __init__(self):
        self.logger = None
        self.spellingDirectory = None
        self.dictionaryDownloadDirectory = None
        self.dictionaryDownloadTask = None
        self.listeners = ZListenerSet()

        self.languages = []
        self.handlers = []
        self.providers = []
        self.builtInDictionary = []
        self.spellChecker = None
    # end __init__()

    def addListener(self, listener):
        self.listeners.append(listener)
    # end addListener()

    def removeListener(self, listener):
        self.listeners.remove(listener)
    # end removeListener()

    def _getSpellcheckDirectory(self):
        return self.applicationModel.getUserProfile().getDirectory(u"spellcheck") #$NON-NLS-1$
    # end _getSpellcheckDirectory()

    def _getDictionaryDownloadDirectory(self):
        return os.path.join(self.spellingDirectory, u"dict-download") #$NON-NLS-1$
    # end _getDictionaryDownloadDirectory()

    def start(self, applicationModel):
        self.applicationModel = applicationModel
        self.logger = applicationModel.getEngine().getService(IZAppServiceIDs.LOGGER_SERVICE_ID)
        self.spellingDirectory = self._getSpellcheckDirectory()
        self.dictionaryDownloadDirectory = self._getDictionaryDownloadDirectory()

        self._loadLanguages()
        self._loadHandlers()
        self._loadProviders()
        self._loadBuiltInDictionary()
        try:
            self._loadSpellchecker()
        except Exception, e:
            self.logger.exception(e)
            self.disableSpellCheck()
        self.logger.debug(u"Spellcheck Service started [%d languages loaded]." % len(self.languages)) #$NON-NLS-1$

        # FIXME re-attach to dictionary download task on startup
    # end start()

    def stop(self):
        if self.spellChecker:
            self.spellChecker.destroy()
            self.spellChecker = None
    # end stop()

    def _loadLanguages(self):
        resourceReg = self.applicationModel.getResourceRegistry()
        dictionariesXMLPath = resourceReg.getResourcePath(u"spellcheck/dictionaries.xml") #$NON-NLS-1$
        self.languages = loadDictionariesXML(dictionariesXMLPath)
    # end _loadLanguages()

    def _loadHandlers(self):
        extensionPoints = self.applicationModel.getPluginRegistry().getExtensions(IZAppExtensionPoints.ZEP_SPELLCHECK_HANDLER)
        self.handlers = map(ZSpellCheckDictionaryHandlerDef, extensionPoints)
    # end _loadHandlers()

    def _loadProviders(self):
        extensionPoints = self.applicationModel.getPluginRegistry().getExtensions(IZAppExtensionPoints.ZEP_SPELLCHECK_PROVIDER)
        self.providers = map(ZSpellCheckProviderDef, extensionPoints)
    # end _loadProviders()

    def _loadBuiltInDictionary(self):
        resourceReg = self.applicationModel.getResourceRegistry()
        wordListXMLPath = resourceReg.getResourcePath(u"spellcheck/blog-word-list.xml") #$NON-NLS-1$
        self.builtInDictionary = loadWordListXML(wordListXMLPath)
    # end _loadBuiltInDictionary()

    def _loadSpellchecker(self):
        userPrefs = self.applicationModel.getUserProfile().getPreferences()
        enabled = userPrefs.getUserPreferenceBool(IZAppUserPrefsKeys.SPELLCHECKER_ENABLED, False)
        if enabled:
            langCode = userPrefs.getUserPreference(IZAppUserPrefsKeys.SPELLCHECKER_LANGUAGE, u"en_US") #$NON-NLS-1$
            self.spellChecker = self._loadSpellcheckerImpl(langCode)
            self.spellChecker.setBuiltInDictionary(self.builtInDictionary)
    # end _loadSpellchecker()

    def _loadSpellcheckerImpl(self, langCode):
        path = os.path.join(self.spellingDirectory, langCode)
        spellCheckerFile = os.path.join(path, u"spellchecker.xml") #$NON-NLS-1$
        if os.path.isfile(spellCheckerFile):
            deserializer = ZSpellCheckerDeserializer()
            return deserializer.deserialize(path)
        else:
            return self._createSpellcheckerImpl(langCode)
    # end _loadSpellcheckerImpl()

    def _createSpellcheckerImpl(self, langCode):
        path = os.path.join(self.spellingDirectory, langCode)
        dictionaryLang = self._getDictionaryLanguage(langCode)
        provider = self._createProvider(dictionaryLang)

        return ZSpellChecker(path, dictionaryLang, provider)
    # end _createSpellcheckerImpl()

    def _getDictionaryLanguage(self, langCode):
        for dictLang in self.languages:
            if dictLang.getLanguageCode() == langCode:
                return dictLang
        return None
    # end _getDictionaryLanguage()

    def _createProvider(self, dictionaryLang):
        type = dictionaryLang.getDictionaryType()
        providerDef = self._getProviderDef(type)
        providerClass = providerDef.getClass()
        return providerClass(dictionaryLang)
    # end _createProvider()

    def _createHandler(self, dictionaryLang):
        handlerId = dictionaryLang.getDictionaryHandler()
        handlerDef = self._getHandlerDef(handlerId)
        handlerClass = handlerDef.getClass()
        return handlerClass()
    # end _createHandler()

    def _getHandlerDef(self, handlerId):
        for handlerDef in self.handlers:
            if handlerDef.getId() == handlerId:
                return handlerDef
        return None
    # end _getHandlerDef()

    def _getProviderDef(self, providerId):
        for providerDef in self.providers:
            if providerDef.getId() == providerId:
                return providerDef
        return None
    # end _getProviderDef()

    def getSupportedLanguages(self):
        return self.languages
    # end getSupportedLanguages()

    def isSpellcheckEnabled(self):
        return self.spellChecker is not None
    # end isSpellcheckEnabled()

    def getActiveSpellChecker(self):
        return self.spellChecker
    # end getActiveSpellChecker()

    def enableSpellCheck(self, langCode):
        if self.dictionaryDownloadTask is not None:
            raise ZAppFrameworkException(_extstr(u"spellcheckimpl.CannotEnableDownloadInProgress")) #$NON-NLS-1$

        if self.spellChecker is not None:
            self.disableSpellCheck()

        userPrefs = self.applicationModel.getUserProfile().getPreferences()
        userPrefs.setUserPreference(IZAppUserPrefsKeys.SPELLCHECKER_ENABLED, True)
        userPrefs.setUserPreference(IZAppUserPrefsKeys.SPELLCHECKER_LANGUAGE, langCode)

        self.logger.debug(u"Enabled spell checking for langcode '%s'." % langCode) #$NON-NLS-1$

        try:
            self._loadSpellchecker()
        except Exception, e:
            # Bug fix: if the spell checker fails to load with "No word lists can
            # be found for the language", then we probably simply need to restart
            # the application.  ASpell appears to load all of the available word
            # lists the first time it is loaded, so if new ones are downloaded
            # later, the app has to be restarted for them to be picked up.
            errorMsg = unicode(e)
            if errorMsg.startswith(u"No word lists can be found for the language"): #$NON-NLS-1$
                raise ZRestartApplicationException()
            else:
                self.logger.exception(e)
                raise e

        for listener in self.listeners:
            listener.onSpellcheckEnabled(self.spellChecker)

        return self.spellChecker
    # end enableSpellCheck()

    def disableSpellCheck(self):
        if self.spellChecker is not None:
            self.spellChecker.destroy()
            self.spellChecker = None
        userPrefs = self.applicationModel.getUserProfile().getPreferences()
        userPrefs.setUserPreference(IZAppUserPrefsKeys.SPELLCHECKER_ENABLED, False)

        self.logger.debug(u"Disabled spell checking.") #$NON-NLS-1$

        for listener in self.listeners:
            listener.onSpellcheckDisabled()
    # end disableSpellCheck()

    def isDictionaryDownloaded(self, langCode):
        dictLang = self._getDictionaryLanguage(langCode)
        urlStr = dictLang.getDictionaryUrl()
        url = ZUrl(urlStr)
        dictFileName = url.getFile()

        downloadDictFilePath = os.path.join(self.dictionaryDownloadDirectory, dictFileName)
        downloadDictMetaFilePath = downloadDictFilePath + u".xml" #$NON-NLS-1$
        return os.path.isfile(downloadDictMetaFilePath)
    # end isDictionaryDownloaded()

    def downloadDictionary(self, langCode):
        if self.dictionaryDownloadTask is not None:
            raise ZAppFrameworkException(_extstr(u"spellcheckimpl.CannotDownloadDownloadInProgress")) #$NON-NLS-1$

        dictLang = self._getDictionaryLanguage(langCode)
        urlStr = dictLang.getDictionaryUrl()
        url = ZUrl(urlStr)
        dictFileName = url.getFile()

        # Create the download dir if it does not exist.
        if not os.path.exists(self.dictionaryDownloadDirectory):
            os.makedirs(self.dictionaryDownloadDirectory)

        # Now create the dictionary download background task and start it.
        handler = self._createHandler(dictLang)
        downloadDictFilePath = os.path.join(self.dictionaryDownloadDirectory, dictFileName)
        downloadDictMetaFilePath = downloadDictFilePath + u".xml" #$NON-NLS-1$
        self.dictionaryDownloadTask = ZDownloadDictionaryTask()
        self.dictionaryDownloadTask.initializeTaskParams(dictLang, url, downloadDictFilePath, downloadDictMetaFilePath, handler)
        bgTaskService = self.applicationModel.getService(IZAppServiceIDs.BACKGROUND_TASK_SERVICE_ID)
        bgTaskService.addTask(self.dictionaryDownloadTask)
        self.dictionaryDownloadTask.attachListener(self)
        return self.dictionaryDownloadTask
    # end downloadDictionary()

    def getDictionaryDownloadTask(self):
        return self.dictionaryDownloadTask
    # end getDictionaryDownloadTask()

    def onComplete(self, task):
        self.logger.debug(u"Dictionary download for langcode %s completed successfully." % task.getLanguageCode()) #$NON-NLS-1$
        task.detachListener(self)
        self.dictionaryDownloadTask = None
        try:
            self.enableSpellCheck(task.getLanguageCode())
        except ZRestartApplicationException, ze: #@UnusedVariable
            self.logger.debug(u"An application restart is needed for spell checking to become active.") #$NON-NLS-1$
            # FIXME (EPW) handle this by adding a notification to the notification service (TBD)
            pass
    # end onComplete()

    def onStop(self, task):
        task.detachListener(self)
        self.dictionaryDownloadTask = None
    # end onStop()

    def onCancel(self, task):
        task.detachListener(self)
        self.dictionaryDownloadTask = None
        self.logger.debug(u"User cancelled dictionary download (langcode %s)." % task.getLanguageCode()) #$NON-NLS-1$
    # end onCancel()

    def onError(self, task, errorMessage, errorDetails): #@UnusedVariable
        task.detachListener(self)
        self.dictionaryDownloadTask = None
        self.logger.error(u"Error downloading dictionary for langcode %s: '%s'" % (task.getLanguageCode(), unicode(errorMessage))) #$NON-NLS-1$
    # end onError()

# end ZSpellCheckService


# ---------------------------------------------------------------------------------------
# An implementation of a background task that downloads the dictionary located at the
# given URL.  In addition, this task is responsible for invoking the handler once the
# file is downloaded.  If the handler successfully handles the dictionary, then the task
# writes out the meta data file to indicate that the dictionary was successfully
# downloaded and installed/handled.
# ---------------------------------------------------------------------------------------
class ZDownloadDictionaryTask(ZBackgroundTask, IZHttpBinaryFileDownloadListener):

    def __init__(self):
        ZBackgroundTask.__init__(self)
        self.handler = None
        self.request = None
        self.customAttributes = {}
    # end __init__()

    def getLanguageCode(self):
        return self.customAttributes[u"lang-code"] #$NON-NLS-1$
    # end getLanguageCode()

    def _getHandler(self):
        if self.handler is None:
            handlerClassName = self.customAttributes[u"handler-class"] #$NON-NLS-1$
            handlerClass = ZClassLoader().loadClass(handlerClassName)
            self.handler = handlerClass()
        return self.handler
    # end _getHandler()

    def _getDictionaryUrl(self):
        return self.customAttributes[u"url"] #$NON-NLS-1$
    # end _getDictionaryUrl()

    def _getDownloadDictFilePath(self):
        return self.customAttributes[u"dict-file-path"] #$NON-NLS-1$
    # end _getDownloadDictFilePath()

    def _getDownloadDictMetaFilePath(self):
        return self.customAttributes[u"dict-meta-path"] #$NON-NLS-1$
    # end _getDownloadDictMetaFilePath()

    def initializeTaskParams(self, dictionaryLanguage, dictionaryUrl, downloadDictFilePath, downloadDictMetaFilePath, handler):
        u"""initializeTaskParams(IZSpellCheckDictionaryLanguage, ZUrl, string, string, IZSpellCheckDictionaryHandler) -> None
        Initializes the task's parameters.""" #$NON-NLS-1$

        self.handler = handler

        self.setName(u"%s (%s)" % (_extstr(u"spellcheckimpl.DownloadingDictionary"), dictionaryLanguage.getDisplayName())) #$NON-NLS-1$ #$NON-NLS-2$
        self.customAttributes[u"url"] = dictionaryUrl.toString() #$NON-NLS-1$
        self.customAttributes[u"lang-code"] = dictionaryLanguage.getLanguageCode() #$NON-NLS-1$
        self.customAttributes[u"dict-file-path"] = downloadDictFilePath #$NON-NLS-1$
        self.customAttributes[u"dict-meta-path"] = downloadDictMetaFilePath #$NON-NLS-1$
        self.customAttributes[u"handler-class"] = unicode(handler.__class__) #$NON-NLS-1$
    # end _initializeTaskParams()

    def _getInitialWorkUnits(self):
        pass
    # end _getInitialWorkUnits()

    def getCustomAttributes(self):
        return self.customAttributes
    # end getCustomAttributes()

    def setCustomAttributes(self, attributeMap):
        self.customAttributes = attributeMap
    # end setCustomAttributes()

    def isResumable(self):
        return True
    # end isResumable()

    def _doCancel(self):
        if self.request is not None:
            self.request.cancel()
    # end _doCancel()

    def run(self):
        try:
            self._run()
        except ZException, ze:
            self._reportException(ze)
        except Exception, e:
            self._reportException(ZException(_extstr(u"spellcheckimpl.UnexpectedErrorDownloadingDictionary"), e)) #$NON-NLS-1$
        self._fireStopEvent()
    # end run()

    def _run(self):
        fileSize = 0
        # Resume the download, if possible.
        outputFilePath = self._getDownloadDictFilePath()
        if os.path.isfile(outputFilePath):
            (shortFile, absFile, fileSize, timestamp) = getFileMetaData(outputFilePath) #@UnusedVariable

        self.request = ZResumableHttpBinaryFileDownload(self._getDictionaryUrl(), self._getDownloadDictFilePath(), fileSize, self)
        if not self.request.send():
            raise ZAppFrameworkException(_extstr(u"spellcheckimpl.ErrorDownloadingDictionary") % self.request.getHttpStatusMessage()) #$NON-NLS-1$

        if not self.stopped:
            # Use the handler to process the resulting file.
            self._getHandler().processDictionaryFile(outputFilePath)
            # Create the "all done" file.
            self._createMetaDataFile()
            self._incrementWork(_extstr(u"spellcheckimpl.DictionaryDownloadedAndProcessed"), 500, True) #$NON-NLS-1$
            self._writeToLog(u"Task complete.") #$NON-NLS-1$
    # end _run()

    def _createMetaDataFile(self):
        dom = ZDom()
        dom.loadXML(u"<dictionary-download />") #$NON-NLS-1$
        rootElem = dom.documentElement
        rootElem.setAttribute(u"content-type", self.customAttributes[u"content-type"]) #$NON-NLS-1$ #$NON-NLS-2$
        rootElem.setAttribute(u"content-length", unicode(self.totalBytes)) #$NON-NLS-1$
        rootElem.setAttribute(u"timestamp", unicode(ZSchemaDateTime())) #$NON-NLS-1$
        dom.save(self._getDownloadDictMetaFilePath(), True)
    # end _createMetaDataFile()

    def transferStarted(self, contentType, contentLength):
        self.bytesDownloaded = 0
        self.totalBytes = contentLength
        self.customAttributes[u"content-type"] = contentType #$NON-NLS-1$
        self.setNumWorkUnits(contentLength + 1000)
        self._fireStartEvent()
    # end transferStarted()

    def transferBlock(self, blockLength):
        self.bytesDownloaded = self.bytesDownloaded + blockLength
        self._incrementWork(_extstr(u"spellcheckimpl.DownloadedOfBytes") % (self.bytesDownloaded, self.totalBytes), blockLength, True) #$NON-NLS-1$
    # end transferBlock()

    def transferComplete(self):
        self._incrementWork(_extstr(u"spellcheckimpl.DictionaryDownloaded"), 500, False) #$NON-NLS-1$
    # end transferComplete()

    def transferError(self, zexception):
        self._reportException(zexception)
    # end transferError()

    def transferCancelled(self):
        pass
    # end transferCancelled()

# end ZDownloadDictionaryTask
