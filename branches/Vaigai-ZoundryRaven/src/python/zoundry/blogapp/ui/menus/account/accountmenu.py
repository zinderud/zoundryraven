from zoundry.appframework.global_services import getResourceRegistry
from zoundry.appframework.ui.actions.menuaction import ZMenuAction
from zoundry.appframework.ui.actions.menuaction import ZMenuActionContext
from zoundry.appframework.ui.widgets.controls.common.menu.menumodel import ZPluginMenuModel
from zoundry.blogapp.constants import IZBlogAppActionIDs
from zoundry.blogapp.constants import IZBlogAppMenuIds
from zoundry.blogapp.ui.dialogs.accountprefsdialog import ZAccountManagerDialog
from zoundry.blogapp.ui.util.publisherutil import ZPublisherSiteSynchUiUtil

# ----------------------------------------------------------------------------------------
# An implementation of a menu action context for menu items in the ZAccount context
# menu (the menu that is displayed when a ZAccount is right-clicked).
# ----------------------------------------------------------------------------------------
class ZAccountMenuActionContext(ZMenuActionContext):

    def __init__(self, window, account):
        self.account = account
        ZMenuActionContext.__init__(self, window)
    # end __init__()

    def getAccount(self):
        return self.account
    # end getAccount()

# end ZAccountMenuActionContext


# ----------------------------------------------------------------------------------------
# The action that gets run when the user clicks on the "Settings..." menu option in the
# Blog Account context menu.
# ----------------------------------------------------------------------------------------
class ZAccountSettingsMenuAction(ZMenuAction):
    # FIXME (PJ) extern these
    def getDisplayName(self):
        return u"&Settings..." #$NON-NLS-1$
    # end getDisplayName()

    def getDescription(self):
        return u"Open the Account Settings dialog." #$NON-NLS-1$
    # end getDescription()

    def runAction(self, actionContext):
        dialog = ZAccountManagerDialog(actionContext.getParentWindow(), actionContext.getAccount())
        dialog.ShowModal()
        dialog.Destroy()
    # end runAction()

# end ZAccountSettingsMenuAction


# ----------------------------------------------------------------------------------------
# The action that gets run when the user clicks on the "Synchronize..." menu
# option in the Blog Account context menu.
# ----------------------------------------------------------------------------------------
class ZAccountSynchronizeMenuAction(ZMenuAction):

    def getDisplayName(self):
        return u"S&ynchronize..." #$NON-NLS-1$
    # end getDisplayName()

    def getDescription(self):
        return u"Synchronize the account online." #$NON-NLS-1$
    # end getDescription()

    def __init__(self):
        pass
    # end __init__()

    def runAction(self, actionContext):
        ZPublisherSiteSynchUiUtil().synchronizeAccount(actionContext.getParentWindow(), actionContext.getAccount())
    # end runAction()

# end ZAccountSynchronizeMenuAction


# ------------------------------------------------------------------------------
# Menu model used for the Blog Account context menu.
# ------------------------------------------------------------------------------
class ZBlogAccountMenuModel(ZPluginMenuModel):

    def __init__(self):
        ZPluginMenuModel.__init__(self, IZBlogAppMenuIds.ZID_BLOG_ACCOUNT_MENU)

        self._buildModel()
    # end __init__()

    def _buildModel(self):
        menuId = self.addMenuItemWithActionId(5, IZBlogAppActionIDs.ACCOUNT_SYNCHRONIZE_ACTION)
        self.setMenuItemBitmap(menuId, getResourceRegistry().getBitmap(u"images/common/menu/blog-account/synchronize.png")) #$NON-NLS-1$
        self.addSeparator(50)
        menuId = self.addMenuItemWithActionId(55, IZBlogAppActionIDs.ACCOUNT_SETTINGS_ACTION)
        self.setMenuItemBitmap(menuId, getResourceRegistry().getBitmap(u"images/common/menu/blog-account/settings.png")) #$NON-NLS-1$
    # end _buildModel()

# end ZBlogAccountMenuModel
