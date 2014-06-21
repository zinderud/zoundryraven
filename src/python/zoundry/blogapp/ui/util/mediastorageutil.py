from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.ui.widgets.dialogs.standarddialogs import ZShowYesNoMessage
from zoundry.blogapp.constants import IZBlogAppServiceIDs
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.ui.wizards.mediastoragewizard import ZNewMediaStorageWizard
import wx


# ------------------------------------------------------------------------------------
# Utility class for Media Storage stuff.
# ------------------------------------------------------------------------------------
class ZMediaStorageUtil:

    def createNewMediaStorage(self, parent):
        u"""Shows the create medais tore wizard. Returns store id if store was created - else returns None.""" #$NON-NLS-1$
        storeId = None
        wizard = ZNewMediaStorageWizard(parent)
        wizard.CenterOnParent()
        rval = wizard.showWizard()
        if rval == wx.ID_OK:
            mediaStoreService = getApplicationModel().getService(IZBlogAppServiceIDs.MEDIA_STORAGE_SERVICE_ID)
            name = wizard.getMediaStorageName()
            mediaSiteId = wizard.getMediaSiteId()
            properties = wizard.getMediaStorageProperties()
            store = mediaStoreService.createMediaStorage(name, mediaSiteId, properties)
            storeId = store.getId()
            wizard.Destroy()
            # Now find any accounts that don't have a storage already
            # configured - then ask the user if she wants to associate
            # this storage with those accounts.
            self._associateStorageWithAccounts(parent, storeId)
        else:
            wizard.Destroy()

        return storeId
    # end createNewMediaStorage()

    def _associateStorageWithAccounts(self, parent, storeId):
        nakedAccounts = []
        accountStore = getApplicationModel().getService(IZBlogAppServiceIDs.ACCOUNT_STORE_SERVICE_ID)
        accounts = accountStore.getAccounts()
        for account in accounts:
            storageId = account.getMediaUploadStorageId()
            if storageId is None:
                nakedAccounts.append(account)

        if nakedAccounts:
            msg = _extstr(u"mediastorageutil.AssociateStorageWithAccountsMsg") % len(nakedAccounts) #$NON-NLS-1$
            if ZShowYesNoMessage(parent, msg, _extstr(u"mediastorageutil.AssociateStorageWithAccounts")): #$NON-NLS-1$
                for account in nakedAccounts:
                    account.setMediaUploadStorageId(storeId)
                    accountStore.saveAccount(account)
    # end _associateStorageWithAccounts()

# end ZMediaStorageUtil
