from zoundry.appframework.global_services import getResourceRegistry
from zoundry.appframework.ui.widgets.controls.common.menu.menumodel import ZPluginMenuBarModel
from zoundry.blogapp.constants import IZBlogAppActionIDs
from zoundry.blogapp.constants import IZBlogAppMenuIds
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.ui.menus.main.view.perspective import ZChangePerspectiveMenuAction

# ------------------------------------------------------------------------------
# The menu bar model used by the main application window.
# ------------------------------------------------------------------------------
class ZBlogAppMainMenuBarModel(ZPluginMenuBarModel):

    def __init__(self, perspectives):
        self.perspectives = perspectives

        ZPluginMenuBarModel.__init__(self, IZBlogAppMenuIds.ZID_MAINMENU)

        self._buildMenuModel()
    # end __init__()

    def _buildMenuModel(self):
        fileMenuId = self.addMenu(_extstr(u"mainmenu.File"), 0) #$NON-NLS-1$
        self.setMenuItemPluginId(fileMenuId, IZBlogAppMenuIds.ZID_MAINMENU_FILE)
        viewMenuId = self.addMenu(_extstr(u"mainmenu.View"), 5) #$NON-NLS-1$
        self.setMenuItemPluginId(viewMenuId, IZBlogAppMenuIds.ZID_MAINMENU_VIEW)
        perspectiveMenuId = self.addMenu(_extstr(u"mainmenu.Perspective"), 10, viewMenuId) #$NON-NLS-1$
        self.setMenuItemPluginId(viewMenuId, IZBlogAppMenuIds.ZID_MAINMENU_VIEW_PERSPECTIVE)
        toolsMenuId = self.addMenu(_extstr(u"mainmenu.Tools"), 10) #$NON-NLS-1$
        self.setMenuItemPluginId(toolsMenuId, IZBlogAppMenuIds.ZID_MAINMENU_TOOLS)
        helpMenuId = self.addMenu(_extstr(u"mainmenu.Help"), 100) #$NON-NLS-1$
        self.setMenuItemPluginId(helpMenuId, IZBlogAppMenuIds.ZID_MAINMENU_HELP)

        fileNewMenuId = self.addMenu(_extstr(u"mainmenu.New"), 5, fileMenuId) #$NON-NLS-1$
        self.setMenuItemPluginId(fileNewMenuId, IZBlogAppMenuIds.ZID_MAINMENU_FILE_NEW)
        menuId = self.addMenuItemWithActionId(500, IZBlogAppActionIDs.EXIT_ACTION, fileMenuId) #$NON-NLS-1$
        self.setMenuItemBitmap(menuId, getResourceRegistry().getBitmap(u"images/common/menu/exit.png")) #$NON-NLS-1$

        menuId = self.addMenuItemWithActionId(15, IZBlogAppActionIDs.ACCOUNT_MANAGER_ACTION, toolsMenuId)
        self.setMenuItemBitmap(menuId, getResourceRegistry().getBitmap(u"images/dialogs/account/manager/menuIcon.png")) #$NON-NLS-1$

        self.addSeparator(40, helpMenuId)

        # Help->Check for Updates...
        check4UpdatesId = self.addMenuItemWithActionId(41, IZBlogAppActionIDs.CHECK_FOR_UPDATES_ACTION, helpMenuId)
        self.setMenuItemBitmap(check4UpdatesId, getResourceRegistry().getBitmap(u"images/common/menu/help/check4updates.png")) #$NON-NLS-1$
        # Help->Get Support...
        getSupportId = self.addMenuItemWithActionId(42, IZBlogAppActionIDs.GET_SUPPORT_ACTION, helpMenuId)
        self.setMenuItemBitmap(getSupportId, getResourceRegistry().getBitmap(u"images/common/menu/help/getSupport.png")) #$NON-NLS-1$

        self.addSeparator(45, helpMenuId)

        # Help->Send Feedback...
        feedbackId = self.addMenuItemWithActionId(5, IZBlogAppActionIDs.FEEDBACK_ACTION, helpMenuId)
        self.setMenuItemBitmap(feedbackId, getResourceRegistry().getBitmap(u"images/dialogs/feedback/send.png")) #$NON-NLS-1$

        self._createPerspectiveMenuItems(perspectiveMenuId)
    # end _buildMenuModel()

    def _createPerspectiveMenuItems(self, parentMenuId):
        for perspectiveDef in self.perspectives:
            perspectiveId = perspectiveDef.getId()
            name = perspectiveDef.getName()
            description = perspectiveDef.getDescription()
            action = ZChangePerspectiveMenuAction(perspectiveId)
            menuId = self.addMenuItemWithAction(name, 5, action, parentMenuId)
            self.setMenuItemCheckbox(menuId, True)
            self.setMenuItemDescription(menuId, description)
            # FIXME (EPW) add an icon to the perspective extension point for use here
#            self.setMenuItemBitmap(menuId, bitmap)
    # end _createPerspectiveMenuItems()

# end ZBlogAppMainMenuBarModel
