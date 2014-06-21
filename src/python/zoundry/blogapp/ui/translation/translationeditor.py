from zoundry.appframework.global_services import getResourceRegistry
from zoundry.appframework.resources.resourceutils import ZMappedImageList
from zoundry.appframework.ui.dialogs.mixins import ZPersistentDialogMixin
from zoundry.appframework.ui.util.resourceutil import getEmptyFlagBitmap
from zoundry.appframework.ui.util.resourceutil import getFlagBitmapForLocale
from zoundry.appframework.ui.widgets.controls.common.bitmap import ZStaticBitmap
from zoundry.appframework.ui.widgets.controls.listex import IZListViewExContentProvider
from zoundry.appframework.ui.widgets.controls.listex import ZListViewEx
from zoundry.appframework.ui.widgets.dialogs.header import ZHeaderDialog
from zoundry.base.util.types.list import ZSortedSet
from zoundry.blogapp.constants import IZBlogAppUserPrefsKeys
from zoundry.blogapp.messages import _extstr
from zoundry.appframework.ui.widgets.dialogs.standarddialogs import ZShowYesNoMessage
from zoundry.base.util.text.textutil import getSafeString
import wx

# ------------------------------------------------------------------------------
# Model used by the translation editor.
# ------------------------------------------------------------------------------
class ZTranslationEditorModel:

    def __init__(self, translation, defaultTranslation):
        self.translation = translation
        self.defaultTranslation = defaultTranslation
        self.showOnlyUntranslated = False
        self.dirty = False

        self.allKeys = ZSortedSet()
        self.untranslatedKeys = ZSortedSet()

        self._initKeys()
    # end __init__()

    def _initKeys(self):
        translationBundleStrings = self.translation.getBundleStrings()
        defaultBundleStrings = self.defaultTranslation.getBundleStrings()

        for key in defaultBundleStrings.keys():
            self.allKeys.add(key)
            if not key in translationBundleStrings:
                self.untranslatedKeys.add(key)
    # end _initKeys()

    def save(self):
        self.translation.save(self.defaultTranslation)
    # end save()

    def isDirty(self):
        return self.dirty
    # end isDirty()
    
    def setDirty(self, dirty):
        self.dirty = dirty
    # end setDirty()

    def getTranslation(self):
        return self.translation
    # end getTranslation()

    def getDefaultTranslation(self):
        return self.defaultTranslation
    # end getDefaultTranslation()

    def setShowOnlyUntranslated(self, value):
        self.showOnlyUntranslated = value
    # end setShowOnlyUntranslated()

    def getAllKeys(self):
        return self.allKeys
    # end getAllKeys()

    def getUntranslatedKeys(self):
        return self.untranslatedKeys
    # end getUntranslatedKeys()

    def getKeys(self):
        if self.showOnlyUntranslated:
            return self.untranslatedKeys
        else:
            return self.allKeys
    # end getKeys()

    def getNumStrings(self):
        return len(self.getKeys())
    # end getNumStrings()

    def getTranslationValue(self, key):
        translationBundleStrings = self.translation.getBundleStrings()
        if key in translationBundleStrings:
            return translationBundleStrings[key]
        return u"" #$NON-NLS-1$
    # end getTranslationValue()

    def getDefaultValue(self, key):
        defaultBundleStrings = self.defaultTranslation.getBundleStrings()
        if key in defaultBundleStrings:
            return defaultBundleStrings[key]
        return u"" #$NON-NLS-1$
    # end getDefaultValue()

    def setTranslationValue(self, key, value):
        self.dirty = True
        if not value:
            self.translation.clearBundleString(key)
            self.untranslatedKeys.add(key)
        else:
            self.translation.setBundleString(key, value)
            if key in self.untranslatedKeys:
                self.untranslatedKeys.remove(key)
    # end setTranslationValue()

# end ZTranslationEditorModel


# ------------------------------------------------------------------------------
# List provider for displaying the list of bundle strings.
# ------------------------------------------------------------------------------
class ZStringBundleProvider(IZListViewExContentProvider):

    def __init__(self, model):
        self.model = model

        self.imageMap = self._createImageMap()
        self.columnInfo = self._createColumnInfo()
    # end __init__()

    def _createColumnInfo(self):
        cstyle = wx.LIST_FORMAT_LEFT
        columnInfo = [
            (_extstr(u"translationeditor.BundleKey"), None, cstyle, ZListViewEx.COLUMN_RELATIVE, 40), #$NON-NLS-1$
            (_extstr(u"translationeditor.TranslatedValue"), None, cstyle, ZListViewEx.COLUMN_RELATIVE, 60) #$NON-NLS-1$
        ]
        return columnInfo
    # end _createColumnInfo()

    def _createImageMap(self):
        imageList = ZMappedImageList()
        bitmap = getResourceRegistry().getBitmap(u"images/dialogs/translation/editor/checked.png") #$NON-NLS-1$
        imageList.addImage(u"checked", bitmap) #$NON-NLS-1$
        bitmap = getResourceRegistry().getBitmap(u"images/dialogs/translation/editor/unchecked.png") #$NON-NLS-1$
        imageList.addImage(u"unchecked", bitmap) #$NON-NLS-1$
        return imageList
    # end _createImageMap()

    def getImageList(self):
        return self.imageMap
    # end getImageList()

    def getNumColumns(self):
        return len(self.columnInfo)
    # end getNumColumns()

    def getNumRows(self):
        return self.model.getNumStrings()
    # end getNumRows()

    def getColumnInfo(self, columnIndex):
        return self.columnInfo[columnIndex]
    # end getColumnInfo()

    def getRowText(self, rowIndex, columnIndex): #@UnusedVariable
        if columnIndex == 0:
            return self._getKey(rowIndex)
        else:
            return self._getValue(rowIndex)
    # end getRowText()

    def getRowImage(self, rowIndex, columnIndex): #@UnusedVariable
        if columnIndex == 0:
            key = self._getKey(rowIndex)
            if not key in self.model.getUntranslatedKeys():
                return self.imageMap[u"checked"] #$NON-NLS-1$
            else:
                return self.imageMap[u"unchecked"] #$NON-NLS-1$
        return -1
    # end getRowImage()

    def _getKey(self, rowIndex):
        return self.model.getKeys()[rowIndex]
    # end _getKey()

    def _getValue(self, rowIndex):
        key = self._getKey(rowIndex)
        return self.model.getTranslationValue(key)
    # end _getValue()

# end ZStringBundleProvider


# ------------------------------------------------------------------------------
# The translation editor dialog.
# ------------------------------------------------------------------------------
class ZTranslationEditor(ZHeaderDialog, ZPersistentDialogMixin):

    def __init__(self, parent, translation, defaultTranslation, translationDisplayName):
        self.translationDisplayName = translationDisplayName
        self.model = ZTranslationEditorModel(translation, defaultTranslation)
        style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER

        ZHeaderDialog.__init__(self, parent, wx.ID_ANY, _extstr(u"translationeditor.EditTranslation_") % translationDisplayName, style = style) #$NON-NLS-1$
        ZPersistentDialogMixin.__init__(self, IZBlogAppUserPrefsKeys.TRANSLATION_DIALOG, True, True)

        self.selectedKey = None
        self.selectedValue = None
    # end __init__()

    def GetBestSize(self):
        return wx.Size(600, 500)
    # end GetBestSize()

    def _createNonHeaderWidgets(self):
        self.showOnlyCB = wx.CheckBox(self, wx.ID_ANY, _extstr(u"translationeditor.ShowOnlyUntranslated")) #$NON-NLS-1$
        self.listProvider = ZStringBundleProvider(self.model)
        self.listBox = ZListViewEx(self.listProvider, self, wx.ID_ANY)
        bitmap = getFlagBitmapForLocale(u"en_US") #$NON-NLS-1$
        self.englishFlag = ZStaticBitmap(self, bitmap)
        self.englishLabel = wx.StaticText(self, wx.ID_ANY, _extstr(u"translationeditor.EnglishValue")) #$NON-NLS-1$
        bitmap = getFlagBitmapForLocale(self.model.getTranslation().getLocale().toString())
        if bitmap is None:
            bitmap = getEmptyFlagBitmap()
        self.translationFlag = ZStaticBitmap(self, bitmap)
        self.translationLabel = wx.StaticText(self, wx.ID_ANY, self.translationDisplayName)
        self.englishText = wx.TextCtrl(self, wx.ID_ANY, style = wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_BESTWRAP)
        self.translationText = wx.TextCtrl(self, wx.ID_ANY, style = wx.TE_MULTILINE | wx.TE_BESTWRAP | wx.TE_PROCESS_ENTER)

        self.translationText.Enable(False)

        self.staticLine = wx.StaticLine(self, wx.HORIZONTAL)
    # end _createNonHeaderWidgets()

    def _populateNonHeaderWidgets(self):
        self.showOnlyCB.SetValue(False)
    # end _populateNonHeaderWidgets()

    def _layoutNonHeaderWidgets(self):
        englishSizer = wx.BoxSizer(wx.HORIZONTAL)
        englishSizer.Add(self.englishFlag, 0, wx.ALL | wx.EXPAND, 2)
        englishSizer.Add(self.englishLabel, 1, wx.ALL | wx.EXPAND, 2)
        translationSizer = wx.BoxSizer(wx.HORIZONTAL)
        translationSizer.Add(self.translationFlag, 0, wx.ALL | wx.EXPAND, 2)
        translationSizer.Add(self.translationLabel, 1, wx.ALL | wx.EXPAND, 2)
        labelSizer = wx.BoxSizer(wx.HORIZONTAL)
        labelSizer.AddSizer(englishSizer, 1, wx.EXPAND)
        labelSizer.AddSizer(translationSizer, 1, wx.EXPAND)

        valueSizer = wx.BoxSizer(wx.HORIZONTAL)
        valueSizer.Add(self.englishText, 1, wx.ALL | wx.EXPAND, 2)
        valueSizer.Add(self.translationText, 1, wx.ALL | wx.EXPAND, 2)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.showOnlyCB, 0, wx.ALL | wx.EXPAND, 3)
        sizer.Add(self.listBox, 2, wx.ALL | wx.EXPAND, 3)
        sizer.AddSizer(labelSizer, 0, wx.ALL | wx.EXPAND, 1)
        sizer.AddSizer(valueSizer, 1, wx.ALL | wx.EXPAND, 1)
        sizer.Add(self.staticLine, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 2)
        return sizer
    # end _layoutNonHeaderWidgets()

    def _getHeaderTitle(self):
        return _extstr(u"translationeditor.TranslationEditor") #$NON-NLS-1$
    # end _getHeaderTitle()

    def _getHeaderMessage(self):
        return _extstr(u"translationeditor.UseThisDialogMsg") #$NON-NLS-1$
    # end _getHeaderMessage()

    def _getHeaderImagePath(self):
        return u"images/dialogs/translation/editor/header.png" #$NON-NLS-1$
    # end _getHeaderImagePath()

    def _getHeaderHelpURL(self):
        return u"http://www.zoundry.com" #$NON-NLS-1$
    # end _getHeaderHelpUrl()

    def _bindWidgetEvents(self):
        self._bindOkButton(self.onSave)
        self._bindCancelButton(self.onCancel)
        self.Bind(wx.EVT_CHECKBOX, self.onShowOnly, self.showOnlyCB)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onListSelection, self.listBox)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onListActivation, self.listBox)
        self.Bind(wx.EVT_TEXT_ENTER, self.onTranslationActivation, self.translationText)

        wx.EVT_KILL_FOCUS(self.translationText, self.onTranslationUnfocus)
    # end _bindWidgetEvents()

    def _setInitialFocus(self):
        self.listBox.SetFocus()
    # end _setInitialFocus()

    def _getOKButtonLabel(self):
        return _extstr(u"translationeditor.Save") #$NON-NLS-1$
    # end _getOKButtonLabel()

    def onSave(self, event):
        wx.BusyCursor()
        self.model.save()
        event.Skip()
    # end onSave()

    def onCancel(self, event):
        if self.model.isDirty() and ZShowYesNoMessage(self, _extstr(u"translationeditor.CancelTranslationMessage"), _extstr(u"translationeditor.CancelTranslationTitle")): #$NON-NLS-2$ #$NON-NLS-1$
            self.model.getTranslation().clear()
            event.Skip()
        elif not self.model.isDirty():
            event.Skip()
    # end onCancel()

    def onListSelection(self, event):
        self._doListSelection()
        event.Skip()
    # end onListSelection()

    def onShowOnly(self, event):
        self.model.setShowOnlyUntranslated(event.IsChecked())
        self.listBox.refresh()
        event.Skip()
    # end onShowOnly()

    def onTranslationUnfocus(self, event):
        value = self.translationText.GetValue()
        # if there is a selection, and the value has changed
        if self.selectedKey is not None and value != self.selectedValue:
            value = getSafeString(value).strip()
            self.model.setTranslationValue(self.selectedKey, value)
            self.listBox.refresh()
        self.translationText.Enable(False)
        event.Skip()
    # end onTranslationUnfocus()

    def onListActivation(self, event):
        self._doListSelection()
        self.translationText.Enable(True)
        self.translationText.SetFocus()
        event.Skip()
    # end onListActivation()

    def onTranslationActivation(self, event):
        self.listBox.SetFocus()
        selectionIdx = self.listBox.getSelection()[0]
        if not self.showOnlyCB.IsChecked():
            selectionIdx = selectionIdx + 1
        self.listBox.Select(selectionIdx, True)
        self._doListSelection()
        event.Skip()
    # end onTranslationActivation()

    def _doListSelection(self):
        selectionIdx = self.listBox.getSelection()[0]
        self.selectedKey = self.model.getKeys()[selectionIdx]
        defValue = self.model.getDefaultValue(self.selectedKey)
        transValue = self.model.getTranslationValue(self.selectedKey)
        self.selectedValue = getSafeString(transValue).strip()

        self.englishText.SetValue(defValue)
        self.translationText.SetValue(self.selectedValue)
    # end _doListSelection()

# end ZTranslationEditor
