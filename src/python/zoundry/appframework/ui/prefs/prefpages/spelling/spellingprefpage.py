from zoundry.appframework.constants import IZAppServiceIDs
from zoundry.appframework.constants import IZAppUserPrefsKeys
from zoundry.appframework.exceptions import ZRestartApplicationException
from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.global_services import getLoggerService
from zoundry.appframework.messages import _extstr
from zoundry.appframework.resources.resourceutils import ZMappedImageList
from zoundry.appframework.ui.dialogs.prefpage import ZUserPreferencePage
from zoundry.appframework.ui.prefs.appprefsdialog import ZApplicationPreferencesPrefPage
from zoundry.appframework.ui.prefs.prefpages.spelling.dictdownloadpanel import ZDictionaryDownloadPanel
from zoundry.appframework.ui.util.resourceutil import getFlagBitmapForLocale
from zoundry.appframework.ui.widgets.controls.list import IZListViewContentProvider
from zoundry.appframework.ui.widgets.controls.list import ZListView
from zoundry.appframework.ui.widgets.dialogs.standarddialogs import ZShowInfoMessage
from zoundry.appframework.ui.widgets.dialogs.standarddialogs import ZShowYesNoMessage
import wx

# ------------------------------------------------------------------------------------
# The model used by the spelling preference page.  This model handles getting and 
# setting all of the data used in the pref page.
# ------------------------------------------------------------------------------------
class ZSpellingPreferencePageModel:

    def __init__(self):
        self.appModel = getApplicationModel()
        self.spellcheckService = self.appModel.getService(IZAppServiceIDs.SPELLCHECK_SERVICE_ID)
        self.i18nService = self.appModel.getService(IZAppServiceIDs.I18N_SERVICE_ID)
        self.userProfile = self.appModel.getUserProfile()
    # end __init__()

    def isSpellcheckEnabled(self):
        u"""isSpellcheckEnabled() -> boolean
        Returns True if spellcheck is enabled.""" #$NON-NLS-1$
        userPrefs = getApplicationModel().getUserProfile().getPreferences()
        return userPrefs.getUserPreferenceBool(IZAppUserPrefsKeys.SPELLCHECKER_ENABLED, False)
    # end isSpellcheckEnabled()

    def getLanguages(self):
        u"""getLanguages() -> IZSpellCheckDictionaryLanguage []
        Gets a list of all the languages.""" #$NON-NLS-1$
        return self.spellcheckService.getSupportedLanguages()
    # end getLanguages()
    
    def findLanguage(self, langCode):
        u"""findLanguage(string) -> IZSpellCheckDictionaryLanguage
        Given a language code, returns the language object.""" #$NON-NLS-1$
        for language in self.getLanguages():
            if language.getLanguageCode() == langCode:
                return language
        return None
    # end findLanguage()

    def getDictionaryDownloadTask(self):
        return self.spellcheckService.getDictionaryDownloadTask()
    # end getDictionaryDownloadTask()

    def getActiveLanguage(self):
        u"""getActiveLanguage() -> IZSpellCheckDictionaryLanguage
        Gets the currently active language or None.""" #$NON-NLS-1$
        for lang in self.getLanguages():
            if self.isActiveLanguage(lang):
                return lang
        return None
    # end getActiveLanguage()
    
    def getLanguageIndex(self, language):
        u"""getLanguageIndex(IZSpellCheckDictionaryLanguage) -> int
        Returns the index into the language list for the given
        language.""" #$NON-NLS-1$
        for idx in range(0, len(self.getLanguages())):
            lang = self.getLanguages()[idx]
            if lang == language:
                return idx
        return -1
    # end getLanguageIndex()

    def isActiveLanguage(self, language):
        u"""isActiveLanguage(IZSpellCheckDictionaryLanguage) -> boolean
        Returns True if the given language is one currently 
        being used for spell checking.  This will return False 
        if spell checking is not enabled or if spell checking
        is enabled for a different language.""" #$NON-NLS-1$
        userPrefs = getApplicationModel().getUserProfile().getPreferences()
        langCode = userPrefs.getUserPreference(IZAppUserPrefsKeys.SPELLCHECKER_LANGUAGE, None)
        return language.getLanguageCode() == langCode
    # end isActiveLanguage()

    def isDefaultLanguage(self, language):
        u"""isDefaultLanguage(IZSpellCheckDictionaryLanguage) -> boolean
        Returns True if the given language matches the current
        locale setting.""" #$NON-NLS-1$
        return language.getLanguageCode() == self.i18nService.getLocale()
    # end isDefaultLanguage()

    def isDictionaryDownloaded(self, language):
        u"""isDictionaryDownloaded(IZSpellCheckDictionaryLanguage) -> boolean
        Returns True if the dictionary has already been downloaded.""" #$NON-NLS-1$
        return self.spellcheckService.isDictionaryDownloaded(language.getLanguageCode())
    # end isDictionaryDownloaded()
    
    def downloadDictionary(self, language):
        u"""downloadDictionary(IZSpellCheckDictionaryLanguage) -> IZBackgroundTask
        Begins downloading the dictionary for the given language.""" #$NON-NLS-1$
        return self.spellcheckService.downloadDictionary(language.getLanguageCode())
    # end downloadDictionary()
    
    def enableSpellCheck(self, language):
        u"""enableSpellCheck(IZSpellCheckDictionaryLanguage) -> boolean
        Enables spell check for the given language.  Returns True
        if a restart of the application is needed.""" #$NON-NLS-1$
        try:
            self.spellcheckService.enableSpellCheck(language.getLanguageCode())
            return False
        except ZRestartApplicationException, ze: #@UnusedVariable
            return True
    # end enableSpellCheck()

    def disableSpellCheck(self):
        u"""disableSpellCheck() -> None
        Disables spellchecking.""" #$NON-NLS-1$
        self.spellcheckService.disableSpellCheck()
    # end disableSpellCheck()

    def getCurrentLocale(self):
        u"""getCurrentLocale() -> string
        Returns the locale currently configured in the i18n service.""" #$NON-NLS-1$
        return self.i18nService.getLocale()
    # end getCurrentLocale()

# end ZSpellingPreferencePageModel


# ------------------------------------------------------------------------------------
# The content provider for the languages list box.
# ------------------------------------------------------------------------------------
class ZLanguagesListProvider(IZListViewContentProvider):
    
    def __init__(self, model):
        self.model = model
        self.imageList = self._createImageList()
        
        self.columnInfo = [
               (_extstr(u"spellingprefpage.Language"), None, wx.ALIGN_CENTER_VERTICAL, 250), #$NON-NLS-1$
               (_extstr(u"spellingprefpage.Ready"), None, 0, 50), #$NON-NLS-1$
        ]
    # end __init__()

    def _createImageList(self):
        imageList = ZMappedImageList(16, 11)
        for language in self.model.getLanguages():
            langCode = language.getLanguageCode()
            bitmap = getFlagBitmapForLocale(langCode)
            if bitmap is not None:
                imageList.addImage(langCode, bitmap)

        return imageList
    # end _createImageList()

    def getImageList(self):
        return self.imageList
    # end getImageList()

    def getNumColumns(self):
        return 2
    # end getNumColumns()

    def getNumRows(self):
        return len(self.model.getLanguages())
    # end getNumRows()

    def getColumnInfo(self, columnIndex):
        return self.columnInfo[columnIndex]
    # end getColumnInfo()

    def getRowText(self, rowIndex, columnIndex):
        language = self.model.getLanguages()[rowIndex]
        if columnIndex == 0:
            return language.getDisplayName()
        elif columnIndex == 1:
            if self.model.isDictionaryDownloaded(language):
                return _extstr(u"spellingprefpage.yes") #$NON-NLS-1$
            else:
                return _extstr(u"spellingprefpage.no") #$NON-NLS-1$
    # end getRowText()

    def getRowImage(self, rowIndex, columnIndex):
        language = self.model.getLanguages()[rowIndex]
        if columnIndex == 0:
            return self.imageList[language.getLanguageCode()]
        return -1
    # end getRowImage()
    
# end ZLanguagesListProvider


# ------------------------------------------------------------------------------------
# A user preference page impl for the Logger user prefs section.
# ------------------------------------------------------------------------------------
class ZSpellingPreferencePage(ZApplicationPreferencesPrefPage):

    def __init__(self, parent):
        ZApplicationPreferencesPrefPage.__init__(self, parent)
        self.originalProps = {}
        self.selectedLanguage = None
        
        self.model = ZSpellingPreferencePageModel()
    # end __init__()

    def createWidgets(self):
        self.dictionaryDownloadPanel = ZDictionaryDownloadPanel(self)
        self.enableSpellCheckCB = wx.CheckBox(self, wx.ID_ANY, _extstr(u"spellingprefpage.EnableSpellcheck")) #$NON-NLS-1$
        provider = ZLanguagesListProvider(self.model)
        self.langListBox = ZListView(provider, self, style = wx.LC_VIRTUAL | wx.LC_REPORT | wx.LC_SINGLE_SEL)
    # end createWidgets()

    def populateWidgets(self):
        spellcheckEnabled = self.model.isSpellcheckEnabled()
        currentLanguage = self.model.getActiveLanguage()
        downloadTask = self.model.getDictionaryDownloadTask()
        # FIXME (EPW) there is a problem when closing the pref page and then re-opening it while the download is still in progress (unknown problem at this point)
        if downloadTask is not None and downloadTask.isRunning():
            self.dictionaryDownloadPanel.Show(True)
            self.dictionaryDownloadPanel.setTask(downloadTask)
            
            self.enableSpellCheckCB.SetValue(True)
            self.enableSpellCheckCB.Enable(False)
            self.langListBox.Enable(False)
        else:
            self.dictionaryDownloadPanel.Show(False)
            self.originalProps[u"spellcheck-enabled"] = spellcheckEnabled #$NON-NLS-1$
            self.originalProps[u"language"] = currentLanguage #$NON-NLS-1$

            self.enableSpellCheckCB.Enable(True)
            self.langListBox.Enable(True)

            self.enableSpellCheckCB.SetValue(spellcheckEnabled)
            self.langListBox.Enable(spellcheckEnabled)

            if spellcheckEnabled:
                idx = self.model.getLanguageIndex(currentLanguage)
                self.selectedLanguage = currentLanguage
                self.langListBox.Select(idx)
            else:
                currentLocale = self.model.getCurrentLocale()
                localeLang = self.model.findLanguage(currentLocale)
                idx = self.model.getLanguageIndex(localeLang)
                if idx is not None and idx >= 0:
                    self.selectedLanguage = self.model.getLanguages()[idx]
                    self.langListBox.Select(idx)
    # end populateWidgets()

    def bindWidgetEvents(self):
        self.Bind(wx.EVT_CHECKBOX, self.onEnableSpellCheck, self.enableSpellCheckCB)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onLanguageSelected, self.langListBox)
    # end bindWidgetEvents()

    def layoutWidgets(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.dictionaryDownloadPanel, 0, wx.EXPAND | wx.ALL, 2)
        sizer.Add(self.enableSpellCheckCB, 0, wx.EXPAND | wx.ALL, 2)
        sizer.Add(self.langListBox, 1, wx.EXPAND | wx.ALL, 2)

        prefSizer = wx.BoxSizer(wx.VERTICAL)
        prefSizer.AddSizer(sizer, 1, wx.EXPAND | wx.ALL, 5)

        self.SetAutoLayout(True)
        self.SetSizer(prefSizer)
        self.Layout()
    # end layoutWidgets()
    
    def onEnableSpellCheck(self, event):
        self.langListBox.Enable(event.IsChecked())
        self.getPrefsDialog().onPrefPageChange()
    # end onEnableSpellCheck()

    def onLanguageSelected(self, event):
        self.selectedLanguage = self.model.getLanguages()[event.GetItem().GetId()]
        self.getPrefsDialog().onPrefPageChange()
        event.Skip()
    # end onLanguageSelected()
    
    def onDictionaryDownloadComplete(self, task):
        langCode = task.getLanguageCode()
        self.selectedLanguage = self.model.findLanguage(langCode)
        self.originalProps[u"spellcheck-enabled"] = True #$NON-NLS-1$
        self.originalProps[u"language"] = self.selectedLanguage #$NON-NLS-1$

        self.langListBox.refresh()

        self.dictionaryDownloadPanel.Show(False)
        self.enableSpellCheckCB.SetValue(True)
        self.enableSpellCheckCB.Enable(True)
        self.langListBox.Enable(True)

        self.Layout()
        self.getPrefsDialog().onPrefPageChange()
    # end onDictionaryDownloadComplete()
    
    def onDictionaryDownloadFailed(self):
        pass
    # end onDictionaryDownloadFailed()
    
    def onDictionaryDownloadCancelled(self):
        self.populateWidgets()
        self.Layout()
        self.getPrefsDialog().onPrefPageChange()
    # end onDictionaryDownloadCancelled()

    def isDirty(self):
        # If we are downloading a dictionary, then we are NOT dirty
        downloadTask = self.model.getDictionaryDownloadTask()
        if downloadTask is not None and downloadTask.isRunning():
            return False

        if self.originalProps[u"spellcheck-enabled"] != self.enableSpellCheckCB.IsChecked(): #$NON-NLS-1$
            return True
        if self.enableSpellCheckCB.IsChecked() and self.originalProps[u"language"] != self.selectedLanguage: #$NON-NLS-1$
            return True
        return False
    # end isDirty()
    
    def isValid(self):
        if not self.enableSpellCheckCB.IsChecked():
            return True
        else:
            return self.selectedLanguage is not None
    # end isValid()

    def apply(self):
        if self.enableSpellCheckCB.IsChecked():
            if self.model.isDictionaryDownloaded(self.selectedLanguage):
                self._enableSpellCheck()
                return True
            else:
                if ZShowYesNoMessage(self, _extstr(u"spellingprefpage.DownloadVerifyMessage"), _extstr(u"spellingprefpage.DownloadDictionary")): #$NON-NLS-2$ #$NON-NLS-1$
                    self._startDictionaryDownload()
                    return True
                else:
                    # Veto the apply() if the user said "no" to the download.
                    return False
        else:
            self.model.disableSpellCheck()
            return True
    # end apply()

    def _enableSpellCheck(self):
        if self.model.enableSpellCheck(self.selectedLanguage):
            ZShowInfoMessage(self, _extstr(u"spellingprefpage.AppMustBeRestartedMessage"), _extstr(u"spellingprefpage.RestartNeeded")) #$NON-NLS-2$ #$NON-NLS-1$
        self.populateWidgets()
    # end _enableSpellCheck()

    def _startDictionaryDownload(self):
        busyIndicator = wx.BusyCursor()
        task = self.model.downloadDictionary(self.selectedLanguage)
        self.dictionaryDownloadPanel.Enable(True)
        self.dictionaryDownloadPanel.setTask(task)
        self.originalProps[u"spellcheck-enabled"] = True #$NON-NLS-1$
        self.originalProps[u"language"] = self.selectedLanguage #$NON-NLS-1$
        self.dictionaryDownloadPanel.Show(True)
        self.enableSpellCheckCB.Enable(False)
        self.langListBox.Enable(False)
        self.Layout()
        del busyIndicator
    # end _startDictionaryDownload()

    def rollback(self):
        getLoggerService().debug(u"rollback") #$NON-NLS-1$
        self.populateWidgets()
    # end rollback()
    
    def destroy(self):
        ZUserPreferencePage.destroy(self)
        self.dictionaryDownloadPanel.destroy()
    # end destroy()

# end ZSpellingPreferencePage
