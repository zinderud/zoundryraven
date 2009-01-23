from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.global_services import getResourceRegistry
from zoundry.appframework.ui.actions.menuaction import ZMenuActionContext
from zoundry.appframework.ui.widgets.controls.common.menu.menu import ZMenu
from zoundry.appframework.ui.widgets.controls.common.menu.menumodel import ZModelBasedMenuContentProvider
from zoundry.appframework.ui.widgets.controls.common.menu.menumodel import ZModelBasedMenuEventHandler
from zoundry.appframework.ui.widgets.controls.common.menu.menumodel import ZPluginMenuModel
from zoundry.blogapp.constants import IZBlogAppActionIDs
from zoundry.blogapp.constants import IZBlogAppMenuIds
from zoundry.blogapp.constants import IZUserPrefsDefaults
from zoundry.blogapp.constants import IZBlogAppUserPrefsKeys
from zoundry.blogapp.messages import _extstr
import wx

# ------------------------------------------------------------------------------
# Accessor class to more easily get at tray icon preferences.
# ------------------------------------------------------------------------------
class ZRavenTrayIconPrefsAccessor:
    
    def __init__(self):
        self.userPrefs = getApplicationModel().getUserProfile().getPreferences()
    # end __init__()
    
    def isAlwaysShowTrayIcon(self):
        return self.userPrefs.getUserPreferenceBool(IZBlogAppUserPrefsKeys.SYSTRAY_ALWAYS_SHOW, IZUserPrefsDefaults.SYSTRAY_ALWAYS_SHOW)
    # end isAlwaysShowTrayIcon()
    
    def isHideWhenMinimized(self):
        return self.userPrefs.getUserPreferenceBool(IZBlogAppUserPrefsKeys.SYSTRAY_HIDE_WHEN_MINIMIZED, IZUserPrefsDefaults.SYSTRAY_HIDE_WHEN_MINIMIZED)
    # end isHideWhenMinimized()

# end ZRavenTrayIconPrefsAccessor


# ------------------------------------------------------------------------------
# Implements the Zoundry Raven application tray icon.
# ------------------------------------------------------------------------------
class ZRavenTrayIcon(wx.TaskBarIcon):

    def __init__(self, mainWindow):
        self.mainWindow = mainWindow
        self.resourceRegistry = getResourceRegistry()
        self.restoreAction = getApplicationModel().getActionRegistry().findAction(IZBlogAppActionIDs.RESTORE_ACTION)

        wx.TaskBarIcon.__init__(self)
        
        self.menuModel = self._createMenuModel()
        self._bindWidgetEvents()
    # end __init__()

    def _bindWidgetEvents(self):
        self.Bind(wx.EVT_TASKBAR_LEFT_DCLICK, self.onDoubleClick)
    # end _bindWidgetEvents()

    def _createMenuModel(self):
        menuModel = ZPluginMenuModel(IZBlogAppMenuIds.ZID_TRAY_MENU)
        
        # New blog post
        newPostId = menuModel.addMenuItemWithActionId(10, IZBlogAppActionIDs.NEW_BLOG_POST_ACTION)
        menuModel.setMenuItemName(newPostId, _extstr(u"trayicon.NewBlogPost")) #$NON-NLS-1$

        menuModel.addSeparator(25)

        # Minimize/restore
        restoreId = menuModel.addMenuItemWithActionId(50, IZBlogAppActionIDs.RESTORE_ACTION)
        menuModel.setMenuItemBold(restoreId, True)
        menuModel.addMenuItemWithActionId(50, IZBlogAppActionIDs.MINIMIZE_ACTION)

        menuModel.addSeparator(990)

        exitId = menuModel.addMenuItemWithActionId(1000, IZBlogAppActionIDs.EXIT_FROM_TRAY_ACTION)
        menuModel.setMenuItemBitmap(exitId, self.resourceRegistry.getBitmap(u"images/common/menu/exit.png")) #$NON-NLS-1$
        return menuModel
    # end _createMenuModel()

    def CreatePopupMenu(self):
        menuContext = ZMenuActionContext(self.mainWindow)
        provider = ZModelBasedMenuContentProvider(self.menuModel, menuContext)
        handler = ZModelBasedMenuEventHandler(self.menuModel, menuContext)
        return ZMenu(self, self.menuModel.getRootNode(), provider, handler)
    # end CreatePopupMenu()
    
    def onDoubleClick(self, event):
        if self.mainWindow.IsIconized():
            menuContext = ZMenuActionContext(self.mainWindow)
            self.restoreAction.runAction(menuContext)
        event.Skip()
    # end onDoubleClick()

# end ZRavenTrayIcon
