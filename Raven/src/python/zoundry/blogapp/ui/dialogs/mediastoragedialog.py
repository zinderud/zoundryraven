from zoundry.appframework.constants import IZAppUserPrefsKeys
from zoundry.appframework.ui.dialogs.mixins import ZPersistentDialogMixin
from zoundry.appframework.ui.widgets.controls.common.menu.menu import ZMenu
from zoundry.appframework.ui.widgets.controls.common.menu.menumodel import ZModelBasedMenuContentProvider
from zoundry.appframework.ui.widgets.controls.common.menu.menumodel import ZModelBasedMenuEventHandler
from zoundry.appframework.ui.widgets.controls.common.menu.menumodel import ZPluginMenuModel
from zoundry.appframework.ui.widgets.controls.listex import ZListViewEx
from zoundry.appframework.ui.widgets.dialog import ZBaseDialog
from zoundry.appframework.ui.widgets.dialogs.header import ZHeaderDialog
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.models.ui.dialogs.mediastoragemodel import ZMediaStorageManagerModel
from zoundry.blogapp.ui.common.mediastoragewidgets import ZMediaStorageListContentProvider
from zoundry.blogapp.ui.menus.mediastoragemanager import ZDeleteMediaStorageMenuAction
from zoundry.blogapp.ui.menus.mediastoragemanager import ZEditMediaStorageMenuAction
from zoundry.blogapp.ui.menus.mediastoragemanager import ZMediaStorageMenuActionContext
from zoundry.blogapp.ui.util.mediastorageutil import ZMediaStorageUtil
import wx


# --------------------------------------------------------------------------------
# The Media Storage Manager dialog.  This dialog allows the user to manage their
# media storages.
# --------------------------------------------------------------------------------
class ZMediaStorageManagerDialog(ZHeaderDialog, ZPersistentDialogMixin):

    def __init__(self, parent):
        self.model = ZMediaStorageManagerModel()
        self.model.getService().addListener(self)
        ZHeaderDialog.__init__(self, parent, wx.ID_ANY, _extstr(u"mediastoragedialog.DialogTitle"), style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER, name = u"ZMediaStorageManagerDialog") #$NON-NLS-2$ #$NON-NLS-1$

        size = self.GetBestSize()
        self.SetSize(size)

        ZPersistentDialogMixin.__init__(self, IZAppUserPrefsKeys.MEDIA_STORE_MANAGER_DIALOG)

        self.Layout()
    # end __init__()

    def _createNonHeaderWidgets(self):
        self.staticBox = wx.StaticBox(self, wx.ID_ANY, _extstr(u"mediastoragedialog.MediaStorages")) #$NON-NLS-1$
        provider = ZMediaStorageListContentProvider(self.model)
        self.storageListBox = ZListViewEx(provider, self)
        self.storageListBox.SetSizeHints(-1, 225)
        self.addButton = wx.Button(self, wx.ID_ANY, _extstr(u"mediastoragedialog.NewStore")) #$NON-NLS-1$
    # end _createNonHeaderWidgets()

    def _populateNonHeaderWidgets(self):
        u"Called to populate the non header related widgets.  (abstract)" #$NON-NLS-1$
    # end _populateNonHeaderWidgets()

    def _layoutNonHeaderWidgets(self):
        sizer = wx.StaticBoxSizer(self.staticBox, wx.VERTICAL)
        sizer.Add(self.storageListBox, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(self.addButton, 0, wx.LEFT | wx.BOTTOM, 5)

        return sizer
    # end _layoutNonHeaderWidgets()

    def _bindWidgetEvents(self):
        self._bindCancelButton(self.onCancel)

        self.Bind(wx.EVT_BUTTON, self.onNewStore, self.addButton)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onEdit, self.storageListBox)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelection, self.storageListBox)
        self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.onItemRightClick, self.storageListBox)
        self.Bind(wx.EVT_LIST_KEY_DOWN, self.onKeyPress, self.storageListBox)
    # end _bindWidgetEvents()

    def _getHeaderTitle(self):
        return _extstr(u"mediastoragedialog.HeaderTitle") #$NON-NLS-1$
    # end _getHeaderTitle()

    def _getHeaderMessage(self):
        return _extstr(u"mediastoragedialog.HeaderMessage") #$NON-NLS-1$
    # end _getHeaderMessage()

    def _getHeaderImagePath(self):
        return u"images/dialogs/mediastorage/manage/header_image.png" #$NON-NLS-1$
    # end _getHeaderImagePath()

    def onEdit(self, event):
        actionContext = self._createMenuActionContext()
        action = ZEditMediaStorageMenuAction()
        action.runAction(actionContext)
        event.Skip()
    # end onEdit()

    def onCancel(self, event):
        self.model.getService().removeListener(self)
        event.Skip()
    # end onCancel()

    def onSelection(self, event):
        self.currentIndex = event.GetIndex()
        event.Skip()
    # end onSelection

    def onKeyPress(self, event):
        if event.GetKeyCode() == wx.WXK_DELETE:
            actionContext = self._createMenuActionContext()
            action = ZDeleteMediaStorageMenuAction()
            action.runAction(actionContext)
        event.Skip()
    # end onKeyPress()

    def onNewStore(self, event):
        ZMediaStorageUtil().createNewMediaStorage(self)
        event.Skip()
    # end onNewStore()

    def onItemRightClick(self, event):
        storage = self._getSelectedStore()
        if storage:
            siteId = storage.getMediaSiteId()
            site = self.model.getService().getMediaSite(siteId)
            if site and site.isInternal():
                event.Skip()
                return
        menu = self._createItemContextMenu()
        self.PopupMenu(menu)
        menu.Destroy()
        event.Skip()
    # end onItemRightClick()

    def onMediaStorageAdded(self, mediaStore): #@UnusedVariable
        self.model.refresh()
        self.storageListBox.refresh()
    # end onMediaStorageAdded()

    def onMediaStorageRemoved(self, mediaStore): #@UnusedVariable
        self.model.refresh()
        self.storageListBox.refresh()
    # end onMediaStorageRemoved() #$NON-NLS-1$

    def _getSelectedStore(self):
        return self.model.getMediaStorages()[self.currentIndex]
    # end _getSelectedStore()

    def _createItemContextMenu(self):
        menuContext = self._createMenuActionContext()
        menuModel = ZPluginMenuModel(u"zoundry.blogapp.ui.core.menu.dialogs.mediastoragemanager.mediastorage") #$NON-NLS-1$
        provider = ZModelBasedMenuContentProvider(menuModel, menuContext)
        eventHandler = ZModelBasedMenuEventHandler(menuModel, menuContext)
        return ZMenu(self, menuModel.getRootNode(), provider, eventHandler)
    # end _createItemContextMenu()

    def _createMenuActionContext(self):
        storage = self._getSelectedStore()
        menuContext = ZMediaStorageMenuActionContext(self, storage, self.model)
        return menuContext
    # end _createMenuActionContext()

    def _getButtonTypes(self):
        return ZBaseDialog.CLOSE_BUTTON
    # end _getButtonTypes()

# end ZMediaStorageManagerDialog

