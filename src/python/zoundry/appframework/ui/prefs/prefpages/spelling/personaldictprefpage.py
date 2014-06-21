from zoundry.appframework.ui.prefs.appprefsdialog import ZApplicationPreferencesPrefPage
from zoundry.appframework.constants import IZAppServiceIDs
from zoundry.appframework.constants import IZAppUserPrefsKeys
from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.messages import _extstr
from zoundry.appframework.services.spellcheck.spellcheck import IZSpellCheckServiceListener
from zoundry.appframework.ui.util.fontutil import getDefaultFontBold
from zoundry.appframework.ui.widgets.controls.listex import IZListViewExContentProvider
from zoundry.appframework.ui.widgets.controls.listex import ZListViewEx
from zoundry.appframework.ui.widgets.dialogs.input import ZShowDataEntryDialog
import wx

# ------------------------------------------------------------------------------------
# A model used by the personal dictionary user pref page.
# ------------------------------------------------------------------------------------
class ZPersonalDictionaryPrefPageModel:

    def __init__(self):
        self.words = []
        self.dirty = False

        self.appModel = getApplicationModel()
        self.spellcheckService = self.appModel.getService(IZAppServiceIDs.SPELLCHECK_SERVICE_ID)

        self.initFromService()
    # end __init__()
    
    def getSpellcheckService(self):
        u"""getSpellcheckService() -> IZSpellCheckService""" #$NON-NLS-1$
        return self.spellcheckService
    # end getSpellcheckService()

    def initFromService(self):
        u"""initFromService() -> None
        Initializes the internal data from information found in the
        spell checking service.""" #$NON-NLS-1$
        personalDict = self.spellcheckService.getActiveSpellChecker()
        if personalDict is not None:
            self.words = []
            for word in personalDict.getWords():
                self.words.append(word)
            self.words.sort()
        else:
            self.words = []
        self.dirty = False
    # end initFromService()

    def isSpellcheckEnabled(self):
        u"""isSpellcheckEnabled() -> boolean
        Returns True if spellcheck is enabled.""" #$NON-NLS-1$
        return self.spellcheckService.isSpellcheckEnabled()
    # end isSpellcheckEnabled()

    def getWordList(self):
        u"""getWordList() -> string []
        Gets the current personal dictionary word list.""" #$NON-NLS-1$
        return self.words
    # end getWordList()

    def getActiveSpellcheckerLocale(self):
        u"""getActiveSpellcheckerLocale() -> string
        Gets the locale for the currently active spell
        checker.""" #$NON-NLS-1$
        userPrefs = getApplicationModel().getUserProfile().getPreferences()
        return userPrefs.getUserPreference(IZAppUserPrefsKeys.SPELLCHECKER_LANGUAGE, None)
    # end getActiveSpellcheckerLocale()

    def addWord(self, word):
        u"""addWord(string) -> boolean""" #$NON-NLS-1$
        if not word in self.words:
            self.words.append(word)
            self.words.sort()
            self.dirty = True
            return True
        return False
    # end addWord()

    def deleteWord(self, word):
        u"""deleteWord(string) -> boolean""" #$NON-NLS-1$
        if word in self.words:
            self.words.remove(word)
            self.dirty = True
            return True
        return False
    # end deleteWord()
    
    def clearWords(self):
        u"""clearWords() -> None
        Clears all the words in the personal dictionary.""" #$NON-NLS-1$
        self.words = []
        self.dirty = True
    # end clearWords()

    def isDirty(self):
        return self.dirty
    # end isDirty()

    def commit(self):
        u"""commit() -> boolean
        Updates the personal dictionary with the changes made.""" #$NON-NLS-1$
        personalDict = self.spellcheckService.getActiveSpellChecker()
        if personalDict is not None:
            personalDict.clearPersonalDictionary()
            personalDict.addWords(self.words)
            self.dirty = False
            return True
        return False
    # end updatePersonalDictionary()

    def rollback(self):
        u"""rollback() -> None
        Cancels any changes that have been made to the model.""" #$NON-NLS-1$
        self.initFromService()
    # end rollback()

# end ZPersonalDictionaryPrefPageModel


# ------------------------------------------------------------------------------------
# A content provider for the list of personal dictionary words.
# ------------------------------------------------------------------------------------
class ZPersonalDictionaryContentProvider(IZListViewExContentProvider):

    def __init__(self, model):
        self.model = model
    # end __init__()

    def getImageList(self):
        return None
    # end getImageList()

    def getNumColumns(self):
        return 1
    # end getNumColumns()

    def getNumRows(self):
        return len(self.model.getWordList())
    # end getNumRows()

    def getColumnInfo(self, columnIndex): #@UnusedVariable
        return (_extstr(u"personaldictprefpage.Word"), None, 0, ZListViewEx.COLUMN_RELATIVE | ZListViewEx.COLUMN_LOCKED, 100) #$NON-NLS-1$
    # end getColumnInfo()

    def getRowText(self, rowIndex, columnIndex): #@UnusedVariable
        return self.model.getWordList()[rowIndex]
    # end getRowText()

    def getRowImage(self, rowIndex, columnIndex): #@UnusedVariable
        return -1
    # end getRowImage()

# end ZPersonalDictionaryContentProvider


# ------------------------------------------------------------------------------------
# A user preference page impl for the Logger user prefs section.
# ------------------------------------------------------------------------------------
class ZPersonalDictionaryPreferencePage(ZApplicationPreferencesPrefPage, IZSpellCheckServiceListener):

    def __init__(self, parent):
        self.model = ZPersonalDictionaryPrefPageModel()
        ZApplicationPreferencesPrefPage.__init__(self, parent)
        
        self.model.getSpellcheckService().addListener(self)
    # end __init__()

    def createWidgets(self):
        self.warningMsg = wx.StaticText(self, wx.ID_ANY, _extstr(u"personaldictprefpage.SpellCheckingMustBeEnabled")) #$NON-NLS-1$
        self.warningMsg.SetFont(getDefaultFontBold())
        self.staticBox = wx.StaticBox(self, wx.ID_ANY)
        provider = ZPersonalDictionaryContentProvider(self.model)
        self.personalDictionaryListView = ZListViewEx(provider, self)
        self.addButton = wx.Button(self, wx.ID_ANY, _extstr(u"personaldictprefpage.Add")) #$NON-NLS-1$
        self.removeButton = wx.Button(self, wx.ID_ANY, _extstr(u"personaldictprefpage.Remove")) #$NON-NLS-1$
        self.clearButton = wx.Button(self, wx.ID_ANY, _extstr(u"personaldictprefpage.Clear")) #$NON-NLS-1$
    # end createWidgets()

    def populateWidgets(self):
        self._refreshButtonStates()
        isEnabled = self.model.isSpellcheckEnabled()
        self.warningMsg.Show(not isEnabled)
        self.personalDictionaryListView.Enable(isEnabled)
        self.addButton.Enable(isEnabled)
        self.removeButton.Enable(isEnabled)
        self.clearButton.Enable(isEnabled)
    # end populateWidgets()

    def bindWidgetEvents(self):
        self.Bind(wx.EVT_BUTTON, self.onAddWord, self.addButton)
        self.Bind(wx.EVT_BUTTON, self.onRemoveWord, self.removeButton)
        self.Bind(wx.EVT_BUTTON, self.onClear, self.clearButton)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onWordSelected, self.personalDictionaryListView)
    # end bindWidgetEvents()

    def layoutWidgets(self):
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer.Add(self.addButton, 0, wx.EXPAND | wx.ALL, 2)
        buttonSizer.Add(self.removeButton, 0, wx.EXPAND | wx.ALL, 2)
        buttonSizer.Add(self.clearButton, 0, wx.EXPAND | wx.ALL, 2)

        sizer = wx.StaticBoxSizer(self.staticBox, wx.VERTICAL)
        sizer.Add(self.personalDictionaryListView, 1, wx.EXPAND | wx.ALL, 5)
        sizer.AddSizer(buttonSizer, 0, wx.EXPAND | wx.ALL, 1)
        
        prefSizer = wx.BoxSizer(wx.VERTICAL)
        prefSizer.Add(self.warningMsg, 0, wx.EXPAND | wx.ALL, 2)
        prefSizer.AddSizer(sizer, 1, wx.EXPAND | wx.ALL, 5)

        self.SetAutoLayout(True)
        self.SetSizer(prefSizer)
        self.Layout()
    # end layoutWidgets()
    
    def onAddWord(self, event):
        word = ZShowDataEntryDialog(self, _extstr(u"personaldictprefpage.AddPersonalDictionaryWord"), _extstr(u"personaldictprefpage.Word")) #$NON-NLS-2$ #$NON-NLS-1$
        if word is not None:
            self.model.addWord(word)
            self.personalDictionaryListView.refresh()
            self._refreshButtonStates()
            self.getPrefsDialog().onPrefPageChange()
        event.Skip()
    # end onAddWord()

    def onRemoveWord(self, event):
        selection = self.personalDictionaryListView.getSelection()
        if selection:
            selectedWord = self.model.getWordList()[selection[0]]
            if self.model.deleteWord(selectedWord):
                self.personalDictionaryListView.refresh()
                self._refreshButtonStates()
                self.getPrefsDialog().onPrefPageChange()
        event.Skip()
    # end onRemoveWord()

    def onClear(self, event):
        self.model.clearWords()
        self.personalDictionaryListView.refresh()
        self._refreshButtonStates()
        self.getPrefsDialog().onPrefPageChange()
        event.Skip()
    # end onClear()

    def onWordSelected(self, event):
        self._refreshButtonStates()
        event.Skip()
    # end onWordSelected()
    
    def onSpellcheckEnabled(self, spellChecker): #@UnusedVariable
        self.rollback()
    # end onSpellcheckEnabled()

    def onSpellcheckDisabled(self):
        self.rollback()
    # end onSpellcheckDisabled()

    def _refreshButtonStates(self):
        self.removeButton.Enable(self.personalDictionaryListView.GetSelectedItemCount() > 0)
        self.clearButton.Enable(len(self.model.getWordList()) > 0)
    # end _refreshButtonStates()

    def isDirty(self):
        return self.model.isDirty()
    # end isDirty()

    def isValid(self):
        return True
    # end isValid()

    def apply(self):
        self.model.commit()
        return True
    # end apply()

    def rollback(self):
        self.model.rollback()
        self.personalDictionaryListView.refresh()
        self.populateWidgets()
    # end rollback()
    
    def destroy(self):
        self.model.getSpellcheckService().removeListener(self)
    # end destroy()

# end ZPersonalDictionaryPreferencePage
