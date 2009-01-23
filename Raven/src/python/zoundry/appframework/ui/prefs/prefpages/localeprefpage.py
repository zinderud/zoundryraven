from zoundry.appframework.constants import IZAppServiceIDs
from zoundry.appframework.constants import IZAppUserPrefsKeys
from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.messages import _extstr
from zoundry.appframework.resources.resourceutils import ZMappedImageList
from zoundry.appframework.ui.prefs.appprefsdialog import ZApplicationPreferencesPrefPage
from zoundry.appframework.ui.util.fontutil import getDefaultFontBold
from zoundry.appframework.ui.util.resourceutil import getFlagBitmapForLocale
from zoundry.appframework.ui.widgets.controls.list import IZListViewContentProvider
from zoundry.appframework.ui.widgets.controls.list import ZListView
from zoundry.appframework.ui.widgets.dialogs.standarddialogs import ZShowInfoMessage
import wx

# ------------------------------------------------------------------------------------
# The model used by the locale preference page.  This model handles getting and 
# setting all of the data used in the pref page.
# ------------------------------------------------------------------------------------
class ZLocalePreferencePageModel:
    
    def __init__(self):
        self.appModel = getApplicationModel()
        self.i18nService = self.appModel.getService(IZAppServiceIDs.I18N_SERVICE_ID)
        self.userProfile = self.appModel.getUserProfile()
    # end __init__()

    def hasLocaleOverride(self):
        userPrefs = self.userProfile.getPreferences()
        localeOverride = userPrefs.getUserPreference(IZAppUserPrefsKeys.LOCALE, u"") #$NON-NLS-1$
        return localeOverride != u"" #$NON-NLS-1$
    # end hasLocaleOverride()
    
    def getLocaleOverrideIndex(self):
        currentLocale = self.getCurrentLocale()
        for idx in range(0, len(self.getLanguagePacks())):
            locale = self.getLanguagePacks()[idx]
            if locale == currentLocale:
                return idx
        return -1
    # end getLocaleOverrideIndex()
    
    def getLanguagePacks(self):
        return self.i18nService.getInstalledLanguagePacks()
    # end getLanguagePacks()
    
    def getDefaultLocale(self):
        return self.i18nService.getDefaultLocale()
    # end getDefaultLocale()
    
    def getDefaultLocaleName(self):
        localeStr = self.getDefaultLocale()
        return self.getLocaleName(localeStr)
    # end getDefaultLocaleName()
    
    def getLocaleName(self, localeString):
        langCode = self.i18nService.findLanguageCodeForLocale(localeString)
        countryCode = self.i18nService.findCountryCodeForLocale(localeString)
        if countryCode is not None:
            return u"%s (%s)" % (langCode.getName(), countryCode.getName()) #$NON-NLS-1$
        else:
            return langCode.getName()
    # end getLocaleName()
    
    def getCurrentLocale(self):
        return self.i18nService.getLocale()
    # end getCurrentLocale()
    
    def saveChanges(self, overrideFlag, locale):
        if overrideFlag:
            self.i18nService.setLocaleOverride(locale)
        else:
            self.i18nService.clearLocaleOverride()
    # end saveChanges()

# end ZLocalePreferencePageModel


# ------------------------------------------------------------------------------------
# A content provider for the locale list.
# ------------------------------------------------------------------------------------
class ZLocaleListContentProvider(IZListViewContentProvider):

    def __init__(self, model):
        self.model = model
        self.imageMap = self._createImageList()
    # end __init__()

    def _createImageList(self):
        imageList = ZMappedImageList(16, 11)
        for localeStr in self.model.getLanguagePacks():
            bitmap = getFlagBitmapForLocale(localeStr)
            if bitmap is not None:
                imageList.addImage(localeStr, bitmap)

        return imageList
    # end _createImageList()

    def getImageList(self):
        return self.imageMap
    # end getImageList()

    def getNumColumns(self):
        return 1
    # end getNumColumns()

    def getColumnInfo(self, columnIndex): #@UnusedVariable
        return (_extstr(u"localeprefpage.LanguagePack"), None, 0, 325) #$NON-NLS-1$
    # end getColumnInfo()

    def getNumRows(self):
        return len(self.model.getLanguagePacks())
    # end getNumRows()

    def getRowText(self, rowIndex, columnIndex): #@UnusedVariable
        localeCode = self.model.getLanguagePacks()[rowIndex]
        return self.model.getLocaleName(localeCode)
    # end getRowText()

    def getRowImage(self, rowIndex, columnIndex): #@UnusedVariable
        localeCode = self.model.getLanguagePacks()[rowIndex]
        return self.imageMap[localeCode]
    # end getRowImage()

# end ZLocaleListContentProvider


# ------------------------------------------------------------------------------------
# A user preference page impl for the Locale user prefs section.
# ------------------------------------------------------------------------------------
class ZLocalePreferencePage(ZApplicationPreferencesPrefPage):

    def __init__(self, parent):
        ZApplicationPreferencesPrefPage.__init__(self, parent)
        self.originalProps = {}
        self.selectedLocale = None
        
        self.model = ZLocalePreferencePageModel()
    # end __init__()

    def createWidgets(self):
        self.localeDetailsStaticBox = wx.StaticBox(self, wx.ID_ANY)
        self.defaultLocaleLabel = wx.StaticText(self, wx.ID_ANY, _extstr(u"localeprefpage.DefaultLocale")) #$NON-NLS-1$
        self.defaultLocaleLabel.SetFont(getDefaultFontBold())
        self.defaultLocale = wx.StaticText(self, wx.ID_ANY, u"") #$NON-NLS-1$
        self.defaultLocaleBitmap = wx.StaticBitmap(self, wx.ID_ANY, wx.NullBitmap)
        self.overrideCB = wx.CheckBox(self, wx.ID_ANY, _extstr(u"localeprefpage.OverrideDefaultLocale")) #$NON-NLS-1$
        provider = self._createLocaleListProvider()
        self.localeList = ZListView(provider, self, style = wx.LC_VIRTUAL | wx.LC_REPORT | wx.LC_SINGLE_SEL)
    # end createWidgets()

    def populateWidgets(self):
        hasLocaleOverride = self.model.hasLocaleOverride()
        currentLocale = self.model.getCurrentLocale()

        self.originalProps[u"override-enabled"] = hasLocaleOverride #$NON-NLS-1$
        self.originalProps[u"locale"] = currentLocale #$NON-NLS-1$

        self.defaultLocale.SetLabel(self.model.getDefaultLocaleName())
        bitmap = getFlagBitmapForLocale(currentLocale)
        if bitmap is not None:
            self.defaultLocaleBitmap.SetBitmap(bitmap)
        self.overrideCB.SetValue(hasLocaleOverride)
        self.localeList.Enable(hasLocaleOverride)
        
        if hasLocaleOverride:
            idx = self.model.getLocaleOverrideIndex()
            self.selectedLocale = currentLocale
            self.localeList.Select(idx)
    # end populateWidgets()

    def bindWidgetEvents(self):
        self.Bind(wx.EVT_CHECKBOX, self.onEnableOverride, self.overrideCB)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onLocaleSelected, self.localeList)
    # end bindWidgetEvents()

    def layoutWidgets(self):
        defaultLocaleSizer = wx.StaticBoxSizer(self.localeDetailsStaticBox, wx.HORIZONTAL)
        defaultLocaleSizer.Add(self.defaultLocaleLabel, 0, wx.EXPAND | wx.ALL, 5)
        defaultLocaleSizer.Add(self.defaultLocaleBitmap, 0, wx.EXPAND)
        defaultLocaleSizer.Add(self.defaultLocale, 1, wx.EXPAND | wx.ALL, 5)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddSizer(defaultLocaleSizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)
        sizer.Add(self.overrideCB, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(self.localeList, 1, wx.EXPAND | wx.ALL, 5)

        prefSizer = wx.BoxSizer(wx.VERTICAL)
        prefSizer.AddSizer(sizer, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 3)

        self.SetAutoLayout(True)
        self.SetSizer(prefSizer)
        self.Layout()
    # end layoutWidgets()
    
    def _createLocaleListProvider(self):
        return ZLocaleListContentProvider(self.model)
    # end _createLocaleListProvider()
    
    def onEnableOverride(self, event):
        self.localeList.Enable(event.IsChecked())
        self.getPrefsDialog().onPrefPageChange()
        event.Skip()
    # end onEnableOverride()
    
    def onLocaleSelected(self, event):
        self.selectedLocale = self.model.getLanguagePacks()[event.GetItem().GetId()]
        self.getPrefsDialog().onPrefPageChange()
        event.Skip()
    # end onLocaleSelected()
    
    def isDirty(self):
        if self.originalProps[u"override-enabled"] != self.overrideCB.IsChecked(): #$NON-NLS-1$
            return True
        if self.overrideCB.IsChecked() and self.originalProps[u"locale"] != self._getSelectedLocale(): #$NON-NLS-1$
            return True
        return False
    # end isDirty()
    
    def isValid(self):
        if not self.overrideCB.IsChecked():
            return True
        else:
            return self.selectedLocale is not None
    # end isValid()

    def apply(self):
        ZShowInfoMessage(self, _extstr(u"localeprefpage.ChangesWillTakeEffectAfterRestart"), _extstr(u"localeprefpage.LocaleChanged")) #$NON-NLS-2$ #$NON-NLS-1$
        self.model.saveChanges(self.overrideCB.IsChecked(), self.selectedLocale)
        self.populateWidgets()
        return True
    # end apply()

    def rollback(self):
        self.populateWidgets()
    # end rollback()
    
    def _getSelectedLocale(self):
        return self.selectedLocale
    # end _getSelectedLocale()

# end ZLocalePreferencePage
