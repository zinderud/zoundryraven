from zoundry.appframework.ui.actions.menuaction import ZMenuAction
from zoundry.appframework.ui.bgtasks.bgtaskmanager import ZShowBackgroundTaskManager
from zoundry.appframework.ui.widgets.dialogs.standarddialogs import ZShowExceptionMessage
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.ui.dialogs.accountprefsdialog import ZAccountManagerDialog
from zoundry.blogapp.ui.dialogs.mediastoragedialog import ZMediaStorageManagerDialog
from zoundry.blogapp.ui.templates.templatemanager import ZShowTemplateManager
from zoundry.blogapp.ui.util.settingsutil import showRavenSettingsDialog


# -------------------------------------------------------------------------------------
# This is the action implementation for the Tools->Media Storages main menu item.
# -------------------------------------------------------------------------------------
class ZAccountManagerMenuAction(ZMenuAction):

    def getDisplayName(self):
        return _extstr(u"tools._AccountManager") #$NON-NLS-1$
    # end getDisplayName()

    def getDescription(self):
        return _extstr(u"tools.AccountManagerDescription") #$NON-NLS-1$
    # end getDescription()

    def runAction(self, actionContext):
        dlg = ZAccountManagerDialog(actionContext.getParentWindow())
        dlg.CentreOnParent()
        dlg.ShowModal()
        dlg.Destroy()
    # end runAction()

# end ZAccountManagerMenuAction


# -------------------------------------------------------------------------------------
# This is the action implementation for the Tools->Settings main menu item.
# -------------------------------------------------------------------------------------
class ZSettingsMenuAction(ZMenuAction):

    def getDisplayName(self):
        return _extstr(u"tools._Preferences") #$NON-NLS-1$
    # end getDisplayName()

    def runAction(self, actionContext):
        try:
            parentWindow = actionContext.getParentWindow()
            showRavenSettingsDialog(parentWindow)
        except Exception, e:
            ZShowExceptionMessage(None, e)
    # end runAction()

# end ZSettingsMenuAction


# -------------------------------------------------------------------------------------
# This is the action implementation for the Tools->Background Tasks main menu item.
# -------------------------------------------------------------------------------------
class ZBackgroundTasksMenuAction(ZMenuAction):

    def getDisplayName(self):
        return _extstr(u"tools.BackgroundTasks") #$NON-NLS-1$
    # end getDisplayName()

    def getDescription(self):
        return _extstr(u"tools.BackgroundTasksDescription") #$NON-NLS-1$
    # end getDescription()

    def runAction(self, actionContext): #@UnusedVariable
        ZShowBackgroundTaskManager()
    # end runAction()

# end ZBackgroundTasksMenuAction


# -------------------------------------------------------------------------------------
# This is the action implementation for the Tools->Background Tasks main menu item.
# -------------------------------------------------------------------------------------
class ZManageTemplatesMenuAction(ZMenuAction):

    def getDisplayName(self):
        return _extstr(u"tools.ManageTemplates") #$NON-NLS-1$
    # end getDisplayName()

    def getDescription(self):
        return _extstr(u"tools.OpenTheTemplateManager") #$NON-NLS-1$
    # end getDescription()

    def runAction(self, actionContext): #@UnusedVariable
        ZShowTemplateManager()
    # end runAction()

# end ZManageTemplatesMenuAction


# -------------------------------------------------------------------------------------
# This is the action implementation for the Tools->Media Storages main menu item.
# -------------------------------------------------------------------------------------
class ZMediaStoragesMenuAction(ZMenuAction):

    def getDisplayName(self):
        return _extstr(u"tools._MediaStorageSettings") #$NON-NLS-1$
    # end getDisplayName()

    def getDescription(self):
        return _extstr(u"tools.MediaStorageSettingsDescription") #$NON-NLS-1$
    # end getDescription()

    def runAction(self, actionContext):
        dlg = ZMediaStorageManagerDialog(actionContext.getParentWindow())
        dlg.CentreOnParent()
        dlg.ShowModal()
        dlg.Destroy()
    # end runAction()

# end ZMediaStoragesMenuAction
