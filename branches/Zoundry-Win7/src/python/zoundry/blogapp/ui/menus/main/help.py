from zoundry.appframework.constants import IZAppServiceIDs
from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.ui.actions.menuaction import ZMenuAction
from zoundry.appframework.util.osutilfactory import getOSUtil
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.ui.dialogs.aboutdialog import ZAboutDialog
from zoundry.blogapp.ui.translation.translationmanager import ZShowTranslationManager

# -------------------------------------------------------------------------------------
# This is the action implementation for the Help->About main menu item.
# -------------------------------------------------------------------------------------
class ZAboutMenuAction(ZMenuAction):

    def getDisplayName(self):
        return _extstr(u"help._About") #$NON-NLS-1$
    # end getDisplayName()

    def getDescription(self):
        return _extstr(u"help.AboutDescription") #$NON-NLS-1$
    # end getDescription()

    def runAction(self, actionContext):
        dialog = ZAboutDialog(actionContext.getParentWindow())
        dialog.CentreOnParent()
        dialog.ShowModal()
        dialog.Destroy()
    # end runAction()

# end ZAboutMenuAction


# -------------------------------------------------------------------------------------
# This is the action implementation for the Help->Translation... main menu item.
# -------------------------------------------------------------------------------------
class ZManageTranslationsMenuAction(ZMenuAction):

    def getDisplayName(self):
        return _extstr(u"help.ManageTranslations") #$NON-NLS-1$
    # end getDisplayName()

    def getDescription(self):
        return _extstr(u"help.ManageTranslationsDesc") #$NON-NLS-1$
    # end getDescription()

    def runAction(self, actionContext): #@UnusedVariable
        ZShowTranslationManager()
    # end runAction()

# end ZManageTranslationsMenuAction


# -------------------------------------------------------------------------------------
# This is the action implementation for the Help->Check for Updates main menu item.
# -------------------------------------------------------------------------------------
class ZCheck4UpdatesMenuAction(ZMenuAction):

    def getDisplayName(self):
        return _extstr(u"help.CheckForUpdates") #$NON-NLS-1$
    # end getDisplayName()

    def getDescription(self):
        return _extstr(u"help.CheckForUpdatesDesc") #$NON-NLS-1$
    # end getDescription()

    def runAction(self, actionContext): #@UnusedVariable
        service = getApplicationModel().getService(IZAppServiceIDs.AUTO_UPDATE_SERVICE_ID)
        service.checkForUpdate(onlyPromptWhenNewVersionIsAvailable = False)
    # end runAction()

# end ZCheck4UpdatesMenuAction


# ------------------------------------------------------------------------------
# This is the action implementation for the Help->Get Support main menu item.
# ------------------------------------------------------------------------------
class ZGetSupportMenuAction(ZMenuAction):

    def getDisplayName(self):
        return _extstr(u"help.GetSupport") #$NON-NLS-1$
    # end getDisplayName()

    def getDescription(self):
        return _extstr(u"help.GetSupportDesc") #$NON-NLS-1$
    # end getDescription()

    def runAction(self, actionContext): #@UnusedVariable
        url = u"http://forums.zoundry.com/viewforum.php?f=12" #$NON-NLS-1$
        getOSUtil().openUrlInBrowser(url)
    # end runAction()

# end ZGetSupportMenuAction

