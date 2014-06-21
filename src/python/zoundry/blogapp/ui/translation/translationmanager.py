from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.global_services import getResourceRegistry
from zoundry.appframework.resources.resourceutils import ZMappedImageList
from zoundry.appframework.ui.actions.menuaction import ZMenuActionContext
from zoundry.appframework.ui.dialogs.mixins import ZPersistentDialogMixin
from zoundry.appframework.ui.events.commonevents import ZEVT_REFRESH
from zoundry.appframework.ui.util.fontutil import getDefaultFontBold
from zoundry.appframework.ui.widgets.controls.common.bitmap import ZStaticBitmap
from zoundry.appframework.ui.widgets.controls.listex import IZListViewExContentProvider
from zoundry.appframework.ui.widgets.controls.listex import ZListViewEx
from zoundry.appframework.ui.widgets.dialogs.standarddialogs import ZShowExceptionMessage
from zoundry.appframework.ui.widgets.dialogs.standarddialogs import ZShowWarnMessage
from zoundry.appframework.ui.widgets.window import ZBaseWindow
from zoundry.base.exceptions import ZException
from zoundry.base.util import fileutil
from zoundry.blogapp.constants import IZBlogAppUserPrefsKeys
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.ui.translation.newtranslationdl import ZNewTranslationDialog
from zoundry.blogapp.ui.translation.translationeditor import ZTranslationEditor
from zoundry.blogapp.ui.translation.translationmodel import ZTranslationManagerModel
from zoundry.appframework.ui.util.resourceutil import getFlagBitmapForLocale
import wx

# FIXME (EPW) should have a multi-part .ico for this instead
ICON_IMAGES = [
    u"images/mainapp/icon/icon16x16.png", #$NON-NLS-1$
    u"images/mainapp/icon/icon24x24.png", #$NON-NLS-1$
    u"images/mainapp/icon/icon32x32.png", #$NON-NLS-1$
    u"images/mainapp/icon/icon48x48.png" #$NON-NLS-1$
]

TRANSLATION_MANAGER_WINDOW = None

# ------------------------------------------------------------------------------------
# Use this function to show the translation window.  It will enforce a
# singleton window instance.
# ------------------------------------------------------------------------------------
def ZShowTranslationManager():
    global TRANSLATION_MANAGER_WINDOW
    try:
        # Check if the bundle dir is writeable - if not, don't allow
        # the user to open the translation manager.
        systemProfile = getApplicationModel().getSystemProfile()
        bundleDirectory = systemProfile.getBundleDirectory()
        if not fileutil.isDirectoryWritable(bundleDirectory):
            title = _extstr(u"translationmanager.TranslationEditingNotAllowed") #$NON-NLS-1$
            message = _extstr(u"translationmanager.MustHaveWriteAccessError") #$NON-NLS-1$
            ZShowWarnMessage(None, message, title)
            return

        if TRANSLATION_MANAGER_WINDOW is None:
            TRANSLATION_MANAGER_WINDOW = ZTranslationManagerWindow(None)
        TRANSLATION_MANAGER_WINDOW.Show()
        TRANSLATION_MANAGER_WINDOW.Raise()
        return TRANSLATION_MANAGER_WINDOW
    except Exception, e:
        ZShowExceptionMessage(None, ZException(u"Error opening Translation Manager", e)) #$NON-NLS-1$
# end ZShowTranslationManager()


# ------------------------------------------------------------------------------------
# Getter for the background task manager window.
# ------------------------------------------------------------------------------------
def getTranslationManager():
    global TRANSLATION_MANAGER_WINDOW
    return TRANSLATION_MANAGER_WINDOW
# end getTranslationManager()


# ------------------------------------------------------------------------------------
# List provider for the list of translations.
# ------------------------------------------------------------------------------------
class ZTranslationListProvider(IZListViewExContentProvider):

    def __init__(self, model):
        self.model = model

        self.imageMap = self._createImageMap()
        self.columnInfo = self._createColumnInfo()
        
        self.updateImageList()
    # end __init__()

    def _createColumnInfo(self):
        cstyle = wx.LIST_FORMAT_LEFT
        columnInfo = [
            (u"Translation", None, cstyle, ZListViewEx.COLUMN_RELATIVE, 99), #$NON-NLS-1$
#            (u"Modified", None, cstyle, ZListViewEx.COLUMN_RELATIVE, 50), #$NON-NLS-1$
        ]
        return columnInfo
    # end _createColumnInfo()

    def _createImageMap(self):
        imageList = ZMappedImageList(16, 11)
        return imageList
    # end _createImageMap()

    def updateImageList(self):
        for translation in self.model.getTranslations():
            bitmap = getFlagBitmapForLocale(translation.getLocale())
            key = translation.getLocale().toString()
            self.imageMap.addImage(key, bitmap)
    # end updateImageList()

    def getImageList(self):
        return self.imageMap
    # end getImageList()

    def getNumColumns(self):
        return len(self.columnInfo)
    # end getNumColumns()

    def getNumRows(self):
        return len(self.model.getTranslations())
    # end getNumRows()

    def getColumnInfo(self, columnIndex):
        return self.columnInfo[columnIndex]
    # end getColumnInfo()

    def getRowText(self, rowIndex, columnIndex): #@UnusedVariable
        translation = self.model.getTranslations()[rowIndex]
        return self.model.getNameForLocale(translation.getLocale())
    # end getRowText()

    def getRowImage(self, rowIndex, columnIndex): #@UnusedVariable
        translation = self.model.getTranslations()[rowIndex]
        key = translation.getLocale().toString()
        rval = self.imageMap[key]
        return rval
    # end getRowImage()

# end ZTranslationListProvider


# ------------------------------------------------------------------------------
# Action context for the translation manager.
# ------------------------------------------------------------------------------
class ZTranslationManagerActionContext(ZMenuActionContext):

    def __init__(self, window, translation):
        self.translation = translation

        ZMenuActionContext.__init__(self, window)
    # end __init__()

    def getTranslation(self):
        return self.translation
    # end getTranslation()

    def setTranslation(self, translation):
        self.translation = translation
    # end setTranslation()

# end ZTranslationManagerActionContext


# ------------------------------------------------------------------------------
# The Translation Manager window.  This window allows the user to edit existing
# translations or make new ones.
# ------------------------------------------------------------------------------
class ZTranslationManagerWindow(ZBaseWindow, ZPersistentDialogMixin):

    def __init__(self, parent):
        self.model = ZTranslationManagerModel()
        self.selectedTranslation = None

        style = wx.DEFAULT_FRAME_STYLE | wx.FULL_REPAINT_ON_RESIZE | wx.CLIP_CHILDREN
        ZBaseWindow.__init__(self, parent, _extstr(u"translationmanager.TranslationManager"), style = style) #$NON-NLS-1$
        ZPersistentDialogMixin.__init__(self, IZBlogAppUserPrefsKeys.TRANSLATION_WINDOW)
        self.Layout()
    # end __init__()

    def getModel(self):
        return self.model
    # end getModel()

    def _createWindowWidgets(self, parent):
        self.headerPanel = self._createHeaderPanel(parent)
        self.headerStaticLine = wx.StaticLine(parent, wx.ID_ANY)

        self.bodyPanel = wx.Panel(parent, wx.ID_ANY)

        self.staticBox = wx.StaticBox(self.bodyPanel, wx.ID_ANY, _extstr(u"translationmanager.Translations")) #$NON-NLS-1$

        self.translationProvider = ZTranslationListProvider(self.model)
        self.translationList = ZListViewEx(self.translationProvider, self.bodyPanel)
        self.translationList.SetMinSize(wx.Size(300, 200))

        self.newButton = wx.Button(self.bodyPanel, wx.ID_ANY, _extstr(u"translationmanager.New")) #$NON-NLS-1$
        self.editButton = wx.Button(self.bodyPanel, wx.ID_ANY, _extstr(u"translationmanager.Edit")) #$NON-NLS-1$
        self.editButton.Enable(False)

        self.staticLine = wx.StaticLine(self.bodyPanel, wx.ID_ANY)
    # end _createWindowWidgets()

    def _createHeaderPanel(self, parent):
        panel = wx.Panel(parent, wx.ID_ANY)
        panel.SetBackgroundColour(wx.WHITE)

        self.headerLink = wx.HyperlinkCtrl(panel, wx.ID_ANY, self._getHeaderTitle(), self._getHeaderHelpURL())
        self.headerLink.SetFont(getDefaultFontBold())
        self.headerMessage = wx.StaticText(panel, wx.ID_ANY, self._getHeaderMessage())
        headerImagePath = self._getHeaderImagePath()
        if not headerImagePath:
            headerImagePath = u"images/dialogs/image/header_image.png" #$NON-NLS-1$
        self.headerIcon = ZStaticBitmap(panel, getResourceRegistry().getBitmap(headerImagePath))

        linkAndMsgSizer = wx.BoxSizer(wx.VERTICAL)
        linkAndMsgSizer.Add(self.headerLink, 0, wx.ALL, 2)
        linkAndMsgSizer.Add(self.headerMessage, 1, wx.EXPAND | wx.ALL, 2)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddSizer(linkAndMsgSizer, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(self.headerIcon, 0, wx.EXPAND | wx.ALL, 10)

        panel.SetAutoLayout(True)
        panel.SetSizer(sizer)

        return panel
    # end _createHeaderPanel()

    def _populateWindowWidgets(self):
        self.SetIcons(getResourceRegistry().getIconBundle(ICON_IMAGES))
        self.refresh()
    # end _populateWindowWidgets()

    def _layoutWindowWidgets(self):
        staticBoxSizer = wx.StaticBoxSizer(self.staticBox, wx.VERTICAL)

        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer.Add(self.newButton, 0, wx.ALL | wx.EXPAND, 2)
        buttonSizer.Add(self.editButton, 0, wx.ALL | wx.EXPAND, 2)

        staticBoxSizer.Add(self.translationList, 1, wx.ALL | wx.EXPAND, 3)
        staticBoxSizer.AddSizer(buttonSizer, 0, wx.ALL | wx.EXPAND, 2)

        self.bodyPanel.SetSizer(staticBoxSizer)
        self.bodyPanel.SetAutoLayout(True)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.headerPanel, 0, wx.EXPAND | wx.ALL, 0)
        sizer.Add(self.headerStaticLine, 0, wx.EXPAND | wx.ALL, 0)
        sizer.Add(self.bodyPanel, 1, wx.EXPAND | wx.ALL, 5)

        return sizer
    # end _layoutWindowWidgets()

    def _bindWidgetEvents(self):
        self.Bind(wx.EVT_BUTTON, self.onAdd, self.newButton)
        self.Bind(wx.EVT_BUTTON, self.onEdit, self.editButton)
        self.Bind(wx.EVT_CLOSE, self.onClose, self)
        self.Bind(ZEVT_REFRESH, self.onRefresh, self)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onTranslationSelected, self.translationList)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onEdit, self.translationList)
    # end _bindWidgetEvents()

    def onRefresh(self, event):
        self.translationList.Refresh()
        event.Skip()
    # end onRefresh()

    def onAdd(self, event):
        dialog = ZNewTranslationDialog(self, self.model)
        result = dialog.ShowModal()
        if result == wx.ID_OK:
            busyIndicator = wx.BusyCursor()
            localeStr = dialog.getData()
            translation = self.model.createNewTranslation(localeStr)
            self.translationProvider.updateImageList()
            self.translationList.refresh()
            translationName = self.model.getNameForLocale(translation.getLocale())
            editor = ZTranslationEditor(self, translation, self.model.getDefaultTranslation(), translationName)
            del busyIndicator
            editor.ShowModal()
        self.refresh()
        event.Skip()
    # end onAdd()

    def onEdit(self, event):
        busyIndicator = wx.BusyCursor()
        idx = self.translationList.getSelection()[0]
        translation = self.model.getTranslations()[idx]
        translation.load()
        translationName = self.model.getNameForLocale(translation.getLocale())
        editor = ZTranslationEditor(self, translation, self.model.getDefaultTranslation(), translationName)
        del busyIndicator
        editor.ShowModal()
        event.Skip()
    # end onEdit()

    def onTranslationSelected(self, event):
        self.selectedTranslation = self.model.getTranslations()[event.GetItem().GetId()]
        self.editButton.Enable(True)
        self.refresh()
        event.Skip()
    # end onTranslationSelected()

    def _setInitialFocus(self):
        pass
    # end _setInitialFocus()

    def refresh(self):
        self.translationList.refresh()
    # end refresh()

    def _getHeaderTitle(self):
        return _extstr(u"translationmanager.TranslationManager") #$NON-NLS-1$
    # end _getHeaderTitle()

    def _getHeaderMessage(self):
        return _extstr(u"translationmanager.UseThisWindowMsg") #$NON-NLS-1$
    # end _getHeaderMessage()

    def _getHeaderImagePath(self):
        return u"images/dialogs/translation/manager/header_image.png" #$NON-NLS-1$
    # end _getHeaderImagePath()

    def _getHeaderHelpURL(self):
        return u"http://www.zoundry.com" #$NON-NLS-1$
    # end _getHeaderHelpUrl()

    def onClose(self, event):
        global TRANSLATION_MANAGER_WINDOW
        TRANSLATION_MANAGER_WINDOW = None
        event.Skip()
    # end onClose()

# end ZTranslationManagerWindow
