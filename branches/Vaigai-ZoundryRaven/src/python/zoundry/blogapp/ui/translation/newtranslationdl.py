from zoundry.blogapp.messages import _extstr
from zoundry.appframework.ui.widgets.dialogs.input import ZDataEntryDialog
import wx #@UnusedImport
import wx.combo #@Reimport

# ------------------------------------------------------------------------------
# The new translation dialog.
# ------------------------------------------------------------------------------
class ZNewTranslationDialog(ZDataEntryDialog):
    
    def __init__(self, parent, model):
        self.model = model

        title = _extstr(u"newtranslationdl.CreateNewTranslation") #$NON-NLS-1$
        label = _extstr(u"newtranslationdl.LanguageLabel") #$NON-NLS-1$

        ZDataEntryDialog.__init__(self, parent, title, label)
    # end __init__()

    def getData(self):
        selection = self.dataWidget.GetSelection()
        return self.dataWidget.GetClientData(selection)
    # end getData()

    def _createDataWidget(self):
        return wx.combo.BitmapComboBox(self, wx.ID_ANY, style = wx.CB_READONLY)
    # end _createDataWidget()

    def _populateDataWidget(self):
        systemLocale = self.model.getSystemLocale()
        for langCode in self.model.getLanguageCodes():
            localeStr = langCode.getDefaultCode()
            displayText = langCode.getName()
            itemId = self.dataWidget.Append(displayText, wx.NullBitmap, localeStr)
            if localeStr == systemLocale:
                self.dataWidget.Select(itemId)
            for countryCodeStr in langCode.getCountryCodes():
                countryCode = self.model.findCountryCode(countryCodeStr)
                localeStr = u"%s_%s" % (langCode.getDefaultCode(), countryCode.getCode().upper()) #$NON-NLS-1$
                displayText = u"%s (%s)" % (langCode.getName(), countryCode.getName()) #$NON-NLS-1$
                itemId = self.dataWidget.Append(displayText, wx.NullBitmap, localeStr)
                if localeStr == systemLocale:
                    self.dataWidget.Select(itemId)
    # end _populateDataWidget()

    def _getHeaderMessage(self):
        return _extstr(u"newtranslationdl.UseThisDialogMsg") #$NON-NLS-1$
    # end _getHeaderMessage()

    def _bindWidgetEvents(self):
        ZDataEntryDialog._bindWidgetEvents(self)
    # end _bindWidgetEvents()

# end ZNewTranslationDialog
