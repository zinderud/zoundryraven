from zoundry.appframework.global_services import getApplicationModel
from zoundry.blogapp.constants import IZBlogAppServiceIDs


# ------------------------------------------------------------------------------------
# Model used by the account manager dialog.
# ------------------------------------------------------------------------------------
class ZAccountManagerModel:

    def __init__(self):
        self.accountStore = getApplicationModel().getService(IZBlogAppServiceIDs.ACCOUNT_STORE_SERVICE_ID)
        self.refresh()
    # end __init__()

    def refresh(self):
        self.accounts = self.accountStore.getAccounts()
    # end refresh()

    def getService(self):
        return self.accountStore
    # end getService()
    
    def getAccounts(self):
        return self.accounts
    # end getAccounts

    def deleteAccount(self, account):
        self.accountStore.removeAccount(account)
    # end deleteAccount()

# end ZAccountManagerModel
