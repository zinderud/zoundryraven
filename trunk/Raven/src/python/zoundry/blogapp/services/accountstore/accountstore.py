from zoundry.appframework.constants import IZAppServiceIDs
from zoundry.appframework.engine.service import IZService
from zoundry.base.util import fileutil
from zoundry.base.util.collections import ZListenerSet
from zoundry.base.util.fileutil import getDirectoryListing
from zoundry.base.util.guid import generate
from zoundry.blogapp.services.accountstore.accountio import loadAccount
from zoundry.blogapp.services.accountstore.accountio import saveAccount
from zoundry.blogapp.services.accountstore.accounttutil import ZAccountUtil
import os


# ------------------------------------------------------------------------------
# A filter function for use in the getDirectoryListing() method.  This will
# return true only for account directories.
# ------------------------------------------------------------------------------
def accountDirectoryFilter(path):
    accountXmlPath = os.path.join(path, u"account.xml") #$NON-NLS-1$
    return os.path.isdir(path) and os.path.isfile(accountXmlPath)
# end accountDirectoryFilter()


# ------------------------------------------------------------------------------
# The account store listener.  This interface defines the callbacks that the
# accountstore will make to any listener of it.
# ------------------------------------------------------------------------------
class IZAccountStoreListener:

    def onAccountAdded(self, account):
        u"Called when a account is added to the store." #$NON-NLS-1$
    # end onAccountAdded()

    def onAccountChanged(self, account):
        u"Called when a specific account has changed." #$NON-NLS-1$
    # end onAccountChange()

    def onAccountDeleted(self, account):
        u"Called when a specific account has been deleted." #$NON-NLS-1$
    # end onAccountDeleted()

# end IZAccountStoreListener


# ------------------------------------------------------------------------------
# The Account Store service interface.  This is the public facing interface for
# the account store.
# ------------------------------------------------------------------------------
class IZAccountStore(IZService):

    def addAccount(self, account):
        u"""addAccount(IZAccount) -> None
        Adds the account to the store.""" #$NON-NLS-1$
    # end addAccount()

    # Returns True if an account with the given name exists.
    def hasAccount(self, accountName):
        u"""hasAccount(string) -> boolean
        Returns True if an account with the given name
        exists.""" #$NON-NLS-1$
    # end hasAccount()

    # Removes a single account by name.
    def removeAccountByName(self, accountName):
        u"""removeAccountByName(string) -> None
        Removes the account with the given name from
        the store.""" #$NON-NLS-1$
    # end removeAccountByName()

    # Removes a single account by id.
    def removeAccountById(self, accountId):
        u"""removeAccountById(accountId) -> None
        Removes the account with the given account ID
        from the store.""" #$NON-NLS-1$
    # end removeAccountById()

    # Removes a single account.
    def removeAccount(self, account):
        u"""removeAccount(IZAccount) -> None
        Removes the given account from the store.""" #$NON-NLS-1$
    # end removeAccount()

    # Gets a single account by name.
    def getAccountByName(self, accountName):
        u"""getAccountByName(string) -> IZAccount
        Gets an account by name.""" #$NON-NLS-1$
    # end getAccount()

    # Gets a single account by id.
    def getAccountById(self, accountId):
        u"""getAccountById(accountId) -> IZAccount
        Gets an account by its ID.""" #$NON-NLS-1$
    # end getAccountById()

    # Returns a list of all acounts in the store.
    def getAccounts(self):
        u"""getAccounts() -> IZAccount[]
        Returns all accounts in the store.""" #$NON-NLS-1$
    # end getAccounts()

    # Called to save any changes to the account to disk.
    def saveAccount(self, account):
        u"""saveAccount(IZAccount) -> None
        Saves the given account.""" #$NON-NLS-1$
    # end saveAccount()

    def addListener(self, listener):
        u"""addListener(IZAccountStoreListener) -> None
        Adds a store listener.""" #$NON-NLS-1$
    # end addListener()

    def removeListener(self, listener):
        u"""removeListener(IZAccountStoreListener) -> None
        Removes a store listener.""" #$NON-NLS-1$
    # end removeListener()

# end IZAccountStore


# ------------------------------------------------------------------------------
# This is an implementation of the Zoundry AccountStore Service.  The account
# store is responsible for handling the list of configured accounts in the
# application.  It will notify listeners when accounts are added, deleted, or
# changed.
# ------------------------------------------------------------------------------
class ZAccountStore(IZAccountStore):

    def __init__(self):
        self.logger = None
        self.listeners = ZListenerSet()
    # end __init__()

    def start(self, applicationModel):
        self.logger = applicationModel.getEngine().getService(IZAppServiceIDs.LOGGER_SERVICE_ID)
        self.applicationModel = applicationModel
        self.accounts = self._loadAccounts()
        self.logger.debug(u"Account Store started [%d accounts loaded]" % len(self.accounts)) #$NON-NLS-1$
    # end start()

    def stop(self):
        pass
    # end stop()

    # Adds a new account to the store.
    def addAccount(self, account):
        # Generate a new id for this account
        accountId = generate()
        # Determine the account's directory
        userProfile = self.applicationModel.getUserProfile()
        accountsDirPath = userProfile.getDirectory(u"accounts") #$NON-NLS-1$
        accountDirPath = os.path.join(accountsDirPath, accountId)
        os.makedirs(accountDirPath)

        account.setId(accountId)
        account.setDirectoryPath(accountDirPath)

        # auto assign media stores
        try:
            accUtil = ZAccountUtil()
            accountList = [account]
            blogList = accUtil.getBlogsWithOutMediaStore(accountList)
            for blog in blogList:
                accUtil.autoAssignMediaStoreToBlog(blog)
        except:
            pass

        self.accounts.append(account)
        self._saveAccount(account)
        self._fireAccountAddedEvent(account)
    # end addAccount()

    # Returns True if an account with the given name exists.
    def hasAccount(self, accountName):
        if not accountName:
            return True
        accountName = accountName.strip()
        # local folder name is reserved.
        if accountName.lower() == u"unpublished": #$NON-NLS-1$
            return True
        return self.getAccountByName(accountName) is not None
    # end hasAccount()

    # Removes a single account by name.
    def removeAccountByName(self, accountName):
        account = self.getAccountByName(accountName)
        self.removeAccount(account)
    # end removeAccountByName()

    # Removes a single account by id.
    def removeAccountById(self, accountId):
        account = self.getAccountById(accountId)
        self.removeAccount(account)
    # end removeAccountById()

    # Removes a single account.
    def removeAccount(self, account):
        if account is None:
            return

        self.accounts.remove(account)
        self._deleteAccount(account)
        self._fireAccountDeletedEvent(account)
    # end removeAccount()

    # Gets a single account by name.
    def getAccountByName(self, accountName):
        if accountName and accountName.strip():
            accountName = accountName.strip().lower()
            for account in self.accounts:
                if account.getName().strip().lower() == accountName:
                    return account
        return None
    # end getAccount()

    # Gets a single account by id.
    def getAccountById(self, accountId):
        for account in self.accounts:
            if account.getId() == accountId:
                return account
        return None
    # end getAccountById()

    # Returns a list of all acounts in the store.
    def getAccounts(self):
        return self.accounts
    # end getAccounts()

    # Called to save any changes to the account to disk.
    def saveAccount(self, account):
        self._saveAccount(account)
        self._fireAccountChangedEvent(account)
    # end saveAccount()

    def _saveAccount(self, account):
        saveAccount(account)
    # end _saveAccount()

    def addListener(self, listener):
        self.listeners.append(listener)
    # end addListener()

    def removeListener(self, listener):
        self.listeners.remove(listener)
    # end removeListener()

    def _loadAccounts(self):
        userProfile = self.applicationModel.getUserProfile()
        accountsDirName = userProfile.getDirectory(u"accounts") #$NON-NLS-1$
        accountDirs = getDirectoryListing(accountsDirName, accountDirectoryFilter)
        return map(loadAccount, accountDirs)
    # end _loadAccounts()

    def _deleteAccount(self, account):
        accountDir = account.getDirectoryPath()
        fileutil.deleteDirectory(accountDir, True)
    # end _deleteAccount()

    def _fireAccountAddedEvent(self, account):
        for listener in self.listeners:
            try:
                listener.onAccountAdded(account)
            except Exception, e:
                self.logger.exception(e)

    def _fireAccountChangedEvent(self, account):
        for listener in self.listeners:
            try:
                listener.onAccountChanged(account)
            except Exception, e:
                self.logger.exception(e)

    def _fireAccountDeletedEvent(self, account):
        for listener in self.listeners:
            try:
                listener.onAccountDeleted(account)
            except Exception, e:
                self.logger.exception(e)

# end ZAccountStore