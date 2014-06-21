from zoundry.blogapp.ui.dialogs.accountmanpages.acctsubpages.tagsubpage import ZTagSitesPrefSubPage
from zoundry.appframework.global_services import getResourceRegistry
from zoundry.blogapp.constants import IZBlogAppUserPrefsKeys
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.services.accountstore.accountimpl import ZAccountAPIInfo
from zoundry.blogapp.ui.dialogs.accountmanpages.acctsubpages.pingsubpage import ZPingSitesPrefSubPage
from zoundry.blogapp.ui.dialogs.accountmanpages.acctsubpages.pubsubpage import ZPublishingPrefSubPage
from zoundry.blogapp.ui.dialogs.accountmanpages.acctsubpages.settingssubpage import ZAccountSettingsPrefSubPage
from zoundry.blogapp.ui.dialogs.accountmanpages.acctsubpages.storesubpage import ZMediaStoragePrefSubPage
from zoundry.blogapp.ui.dialogs.accountmanpages.acctsubpages.templatesubpage import ZTemplatePrefSubPage
from zoundry.blogapp.ui.dialogs.accountmanpages.commonpage import ZBasePrefsPage
from zoundry.blogapp.ui.dialogs.accountmanpages.commonpage import ZBasePrefsSession

KEY_ACCOUNT_USERNAME = u"account-username" #$NON-NLS-1$
KEY_ACCOUNT_PASSWORD = u"account-password" #$NON-NLS-1$
KEY_ACCOUNT_API_URL = u"account-api-url" #$NON-NLS-1$

# ------------------------------------------------------------------------------
# Session used by the account prefs page and its subpages.
# ------------------------------------------------------------------------------
class ZAccountPrefsSession(ZBasePrefsSession):

    def __init__(self, accountPrefPage, account):
        self.account = account

        ZBasePrefsSession.__init__(self, accountPrefPage)

        self.newSettings = {}
    # end __init__()

    def _createUserPrefs(self):
        return self.account.getPreferences()
    # end _createUserPrefs()

    def _getOverridePublishingSettingsKey(self):
        return IZBlogAppUserPrefsKeys.BLOG_ACCOUNT_OVERRIDE_PUB_SETTINGS
    # end _getOverridePublishingSettingsKey()

    def _getOverridePingSitesKey(self):
        return IZBlogAppUserPrefsKeys.BLOG_ACCOUNT_OVERRIDE_PING_SITE
    # end _getOverridePingSitesKey()
    
    def _getOverrideTagSitesKey(self):
        return IZBlogAppUserPrefsKeys.BLOG_ACCOUNT_OVERRIDE_TAG_SITE
    # end _getOverrideTagSitesKey()
    
    def _getStoreId(self):
        return self.account.getMediaUploadStorageId()
    # end _getStoreId()

    def _setStoreId(self, storeId):
        self.account.setMediaUploadStorageId(storeId)
    # end _setStoreId()

    def _getTemplateId(self):
        return self.account.getTemplateId()
    # end _getTemplateId()

    def _setTemplateId(self, templateId):
        self.account.setTemplateId(templateId)
    # end _setTemplateId()

    def getAccountUsername(self):
        if KEY_ACCOUNT_USERNAME in self.newSettings:
            return self.newSettings[KEY_ACCOUNT_USERNAME]
        else:
            return self._getAccountUsername()
    # end getAccountUsername()

    def _getAccountUsername(self):
        return self.account.getUsername()
    # end _getAccountUsername()

    def setAccountUsername(self, username):
        self.newSettings[KEY_ACCOUNT_USERNAME] = username
        if self._getAccountUsername() == username:
            del self.newSettings[KEY_ACCOUNT_USERNAME]
        self.prefPage.onSessionChange()
    # end setAccountUsername()

    def getAccountPassword(self):
        if KEY_ACCOUNT_PASSWORD in self.newSettings:
            return self.newSettings[KEY_ACCOUNT_PASSWORD]
        else:
            return self._getAccountPassword()
    # end getAccountPassword()

    def _getAccountPassword(self):
        return self.account.getPassword()
    # end _getAccountPassword()

    def setAccountPassword(self, password):
        self.newSettings[KEY_ACCOUNT_PASSWORD] = password
        if self._getAccountPassword() == password:
            del self.newSettings[KEY_ACCOUNT_PASSWORD]
        self.prefPage.onSessionChange()
    # end setAccountPassword()

    def getAccountAPIUrl(self):
        if KEY_ACCOUNT_API_URL in self.newSettings:
            return self.newSettings[KEY_ACCOUNT_API_URL]
        else:
            return self._getAccountAPIUrl()
    # end getAccountAPIUrl()

    def _getAccountAPIUrl(self):
        return self.account.getAPIInfo().getUrl()
    # end _getAccountAPIUrl()

    def setAccountAPIUrl(self, url):
        self.newSettings[KEY_ACCOUNT_API_URL] = url
        if self._getAccountAPIUrl() == url:
            del self.newSettings[KEY_ACCOUNT_API_URL]
        self.prefPage.onSessionChange()
    # end setAccountAPIUrl()

    def isDirty(self):
        return len(self.newSettings) > 0
    # end isDirty()

    def apply(self):
        ZBasePrefsSession.apply(self)

        if KEY_ACCOUNT_USERNAME in self.newSettings:
            self.account.setUsername(self.newSettings[KEY_ACCOUNT_USERNAME])
        if KEY_ACCOUNT_PASSWORD in self.newSettings:
            self.account.setPassword(self.newSettings[KEY_ACCOUNT_PASSWORD])
        if KEY_ACCOUNT_API_URL in self.newSettings:
            apiinfo = ZAccountAPIInfo()
            apiinfo.setType(self.account.getAPIInfo().getType())
            apiinfo.setUrl(self.newSettings[KEY_ACCOUNT_API_URL])
            self.account.setAPIInfo(apiinfo)

        self._getAccountStore().saveAccount(self.account)

        self.newSettings = {}
    # end apply()

    def rollback(self):
        self.newSettings = {}
    # end rollback()

# end ZAccountPrefsSession


# ------------------------------------------------------------------------------
# Implements the prefs page that is shown in the account manager when the user
# clicks on an account.
# ------------------------------------------------------------------------------
class ZAccountPrefsPage(ZBasePrefsPage):

    def __init__(self, parent, account):
        self.account = account

        ZBasePrefsPage.__init__(self, parent)
    # end __init__()

    def _createSession(self):
        return ZAccountPrefsSession(self, self.account)
    # end _createSession()

    def _createPrefsSubPages(self, parent):
        bmp = getResourceRegistry().getBitmap(u"images/dialogs/account/manager/account_pages/settings.png") #$NON-NLS-1$
        self.settingsPage = ZAccountSettingsPrefSubPage(parent, self.session)
        self.toolBook.addPage(self.settingsPage, _extstr(u"accountpage.Settings"), _extstr(u"accountpage.Settings_Description"), bmp) #$NON-NLS-2$ #$NON-NLS-1$

        bmp = getResourceRegistry().getBitmap(u"images/dialogs/account/manager/account_pages/publishing.png") #$NON-NLS-1$
        self.pubPage = ZPublishingPrefSubPage(parent, self.session)
        self.toolBook.addPage(self.pubPage, _extstr(u"accountpage.Publishing"), _extstr(u"accountpage.Publishing_Description"), bmp) #$NON-NLS-2$ #$NON-NLS-1$

        bmp = getResourceRegistry().getBitmap(u"images/dialogs/account/manager/account_pages/media_store.png") #$NON-NLS-1$
        self.storePage = ZMediaStoragePrefSubPage(parent, self.session)
        self.toolBook.addPage(self.storePage, _extstr(u"accountpage.Media_Store"), _extstr(u"accountpage.Media_Store_Description"), bmp) #$NON-NLS-2$ #$NON-NLS-1$

        bmp = getResourceRegistry().getBitmap(u"images/dialogs/account/manager/account_pages/template.png") #$NON-NLS-1$
        self.templatePage = ZTemplatePrefSubPage(parent, self.session)
        self.toolBook.addPage(self.templatePage, _extstr(u"accountpage.Template"), _extstr(u"accountpage.Template_Description"), bmp) #$NON-NLS-2$ #$NON-NLS-1$

        bmp = getResourceRegistry().getBitmap(u"images/dialogs/account/manager/account_pages/ping_sites.png") #$NON-NLS-1$
        self.sitesPage = ZPingSitesPrefSubPage(parent, self.session)
        self.toolBook.addPage(self.sitesPage, _extstr(u"accountpage.Ping_Sites"), _extstr(u"accountpage.Ping_Sites_Description"), bmp) #$NON-NLS-2$ #$NON-NLS-1$
        
        bmp = getResourceRegistry().getBitmap(u"images/dialogs/account/manager/account_pages/tag_sites.png") #$NON-NLS-1$
        self.tagsPage = ZTagSitesPrefSubPage(parent, self.session)
        self.toolBook.addPage(self.tagsPage, _extstr(u"accountpage.Tag_Sites"), _extstr(u"accountpage.Tag_Sites_Description"), bmp) #$NON-NLS-2$ #$NON-NLS-1$
        
    # end _createPrefsSubPages()

    def populateWidgets(self):
        self.settingsPage._populateWidgets()
        self.pubPage._populateWidgets()
        self.storePage._populateWidgets()
        self.sitesPage._populateWidgets()
        self.tagsPage._populateWidgets()
    # end populateWidgets()

    def bindWidgetEvents(self):
        self._bindValidatingWidget(self.settingsPage)
        self._bindValidatingWidget(self.pubPage)
        self._bindValidatingWidget(self.storePage)
        self._bindValidatingWidget(self.sitesPage)
        self._bindValidatingWidget(self.tagsPage)
    # end bindWidgetEvents()

# end ZAccountPrefsPage
