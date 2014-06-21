from zoundry.appframework.ui.actions.menuaction import ZMenuAction
from zoundry.appframework.ui.actions.menuaction import ZMenuActionContext
from zoundry.appframework.ui.widgets.dialogs.standarddialogs import ZShowYesNoMessage
from zoundry.appframework.ui.widgets.dialogs.tdialog import ZTestProgressDialog
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.services.mediastorage.mediastorageztest import ZMediaStorageSettingsZTest
from zoundry.blogapp.ui.dialogs.editstoredialog import ZEditMediaStorageSettingsDialog
from zoundry.blogapp.services.mediastorage.mediastoragetype import IZMediaStorageCapabilities
import wx


# -------------------------------------------------------------------------------------
# This is the menu action context that is passed to menu actions for the right-click
# context menu in the media storage manager dialog (when the user right-clicks on a media
# storage manager).
# -------------------------------------------------------------------------------------
class ZMediaStorageMenuActionContext(ZMenuActionContext):
    
    def __init__(self, window, mediaStore, model):
        self.window = window
        self.mediaStore = mediaStore
        self.model = model
        ZMenuActionContext.__init__(self, window)
    # end __init__()
    
    def getMediaStorage(self):
        return self.mediaStore
    # end getMediaStorage()
    
    def getModel(self):
        return self.model
    # end getModel()

# end ZMediaStorageMenuActionContext


# -------------------------------------------------------------------------------------
# This is the action implementation the "Edit" option in the media storage manager
# right-click menu (when the user right-clicks on a media storage manager).
# -------------------------------------------------------------------------------------
class ZEditMediaStorageMenuAction(ZMenuAction):

    def getDisplayName(self):
        return _extstr(u"mediastoragemanager._Edit") #$NON-NLS-1$
    # end getDisplayName()
    
    def getDescription(self):
        return _extstr(u"mediastoragemanager.EditDescription") #$NON-NLS-1$
    # end getDescription()

    def runAction(self, actionContext):
        store = actionContext.getMediaStorage()
        dialog = ZEditMediaStorageSettingsDialog(store, actionContext.getParentWindow())
        dialog.CentreOnParent()
        dialog.ShowModal()
        dialog.Destroy()
    # end runAction()

# end ZEditMediaStorageMenuAction


# -------------------------------------------------------------------------------------
# This is the action implementation the "Test" option in the media storage manager
# right-click menu (when the user right-clicks on a media storage manager).
# -------------------------------------------------------------------------------------
class ZTestMediaStorageMenuAction(ZMenuAction):

    def getDisplayName(self):
        return _extstr(u"mediastoragemanager._Test") #$NON-NLS-1$
    # end getDisplayName()
    
    def getDescription(self):
        return _extstr(u"mediastoragemanager.TestDescription") #$NON-NLS-1$
    # end getDescription()

    def isVisible(self, context): #@UnusedVariable
        storage = context.getMediaStorage()
        return storage.getCapabilities().hasCapability(IZMediaStorageCapabilities.KEY_SUPPORTS_DELETE)
    # end isVisible()

    def runAction(self, actionContext):
        storage = actionContext.getMediaStorage()
        ztest = ZMediaStorageSettingsZTest(storage)
        dlg = ZTestProgressDialog(ztest, actionContext.getParentWindow(), _extstr(u"mediastoragemanager.MediaStorageTestDialogTitle"), size = wx.Size(-1, 350)) #$NON-NLS-1$
        dlg.CenterOnParent()
        dlg.ShowModal()
        dlg.Destroy()
    # end runAction()

# end ZTestMediaStorageMenuAction


# -------------------------------------------------------------------------------------
# This is the action implementation the "Delete" option in the media storage manager
# right-click menu (when the user right-clicks on a media storage manager).
# -------------------------------------------------------------------------------------
class ZDeleteMediaStorageMenuAction(ZMenuAction):

    def getDisplayName(self):
        return _extstr(u"mediastoragemanager._Delete") #$NON-NLS-1$
    # end getDisplayName()
    
    def getDescription(self):
        return _extstr(u"mediastoragemanager.DeleteDescription") #$NON-NLS-1$
    # end getDescription()

    def runAction(self, actionContext):
        store = actionContext.getMediaStorage()
        if ZShowYesNoMessage(actionContext.getParentWindow(), _extstr(u"mediastoragemanager.DeleteMediaStorage") % store.getName(), _extstr(u"mediastoragemanager.ConfirmDelete")): #$NON-NLS-2$ #$NON-NLS-1$
            actionContext.getModel().deleteStore(store)
    # end runAction()

# end ZDeleteMediaStorageMenuAction
