from zoundry.blogapp.ui.dialogs.accountmanpages.blogsubpages.tagsubpage import ZBlogTagSitesPrefSubPage
from zoundry.appframework.global_services import getResourceRegistry
from zoundry.blogapp.constants import IZBlogAppUserPrefsKeys
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.ui.dialogs.accountmanpages.blogsubpages.pingsubpage import ZBlogPingSitesPrefSubPage
from zoundry.blogapp.ui.dialogs.accountmanpages.blogsubpages.pubsubpage import ZBlogPublishingPrefSubPage
from zoundry.blogapp.ui.dialogs.accountmanpages.blogsubpages.storesubpage import ZBlogMediaStoragePrefSubPage
from zoundry.blogapp.ui.dialogs.accountmanpages.blogsubpages.templatesubpage import ZBlogTemplatePrefSubPage
from zoundry.blogapp.ui.dialogs.accountmanpages.commonpage import ZBasePrefsPage
from zoundry.blogapp.ui.dialogs.accountmanpages.commonpage import ZBasePrefsSession

KEY_OVERRIDE_MEDIA_STORE = u"override-media-storage" #$NON-NLS-1$
KEY_OVERRIDE_TEMPLATE = u"override-template" #$NON-NLS-1$


# ------------------------------------------------------------------------------
# Session used by the account prefs page and its subpages.
# ------------------------------------------------------------------------------
class ZBlogPrefsSession(ZBasePrefsSession):

    def __init__(self, blogPrefPage, blog):
        self.blog = blog

        ZBasePrefsSession.__init__(self, blogPrefPage)

        self.newSettings = {}
    # end __init__()

    def _createUserPrefs(self):
        return self.blog.getPreferences()
    # end _createUserPrefs()

    def _getOverridePublishingSettingsKey(self):
        return IZBlogAppUserPrefsKeys.BLOG_OVERRIDE_PUB_SETTINGS
    # end _getOverridePublishingSettingsKey()

    def _getOverridePingSitesKey(self):
        return IZBlogAppUserPrefsKeys.BLOG_OVERRIDE_PING_SITE_SETTINGS
    # end _getOverridePingSitesKey()
    
    def _getOverrideTagSitesKey(self):
        return IZBlogAppUserPrefsKeys.BLOG_OVERRIDE_TAG_SITE_SETTINGS
    # end _getOverrideTagSitesKey()
    
    def _getStoreId(self):
        return self.blog.getMediaUploadStorageId()
    # end _getStoreId()

    def _setStoreId(self, storeId):
        self.blog.setMediaUploadStorageId(storeId)
    # end _setStoreId()

    def isOverrideMediaStorage(self):
        if KEY_OVERRIDE_MEDIA_STORE in self.newSettings:
            return self.newSettings[KEY_OVERRIDE_MEDIA_STORE]
        else:
            return self._isOverrideMediaStorage()
    # end isOverrideMediaStorage()

    def _isOverrideMediaStorage(self):
        return self.userPrefs.getUserPreferenceBool(IZBlogAppUserPrefsKeys.BLOG_OVERRIDE_MEDIA_STORE, False)
    # end isOverrideMediaStorage()

    def setOverrideMediaStorage(self, bValue):
        self.newSettings[KEY_OVERRIDE_MEDIA_STORE] = bValue
        if self._isOverrideMediaStorage() == bValue:
            del self.newSettings[KEY_OVERRIDE_MEDIA_STORE]
        self.prefPage.onSessionChange()
    # end setOverrideMediaStorage()

    def _getTemplateId(self):
        return self.blog.getTemplateId()
    # end _getTemplateId()

    def _setTemplateId(self, storeId):
        self.blog.setTemplateId(storeId)
    # end _setTemplateId()

    def isOverrideTemplate(self):
        if KEY_OVERRIDE_TEMPLATE in self.newSettings:
            return self.newSettings[KEY_OVERRIDE_TEMPLATE]
        else:
            return self._isOverrideTemplate()
    # end isOverrideTemplate()

    def _isOverrideTemplate(self):
        return self.userPrefs.getUserPreferenceBool(IZBlogAppUserPrefsKeys.BLOG_OVERRIDE_TEMPLATE, False)
    # end isOverrideTemplate()

    def setOverrideTemplate(self, bValue):
        self.newSettings[KEY_OVERRIDE_TEMPLATE] = bValue
        if self._isOverrideTemplate() == bValue:
            del self.newSettings[KEY_OVERRIDE_TEMPLATE]
        self.prefPage.onSessionChange()
    # end setOverrideTemplate()

    def isDirty(self):
        return len(self.newSettings) > 0
    # end isDirty()

    def apply(self):
        ZBasePrefsSession.apply(self)

        # If the user is turning off the override media storage override, then 
        # we need to remove all of the relevant prefs so that the inheritance 
        # from the account prefs works properly.
        if KEY_OVERRIDE_MEDIA_STORE in self.newSettings:
            self.userPrefs.setUserPreference(IZBlogAppUserPrefsKeys.BLOG_OVERRIDE_MEDIA_STORE, self.newSettings[KEY_OVERRIDE_MEDIA_STORE])
            if not self.newSettings[KEY_OVERRIDE_MEDIA_STORE]:
                self.blog.setMediaUploadStorageId(None)
        # If the user is turning off the override template override, then we need
        # to remove all of the relevant prefs so that the inheritance from the 
        # account prefs works properly.
        if KEY_OVERRIDE_TEMPLATE in self.newSettings:
            self.userPrefs.setUserPreference(IZBlogAppUserPrefsKeys.BLOG_OVERRIDE_TEMPLATE, self.newSettings[KEY_OVERRIDE_TEMPLATE])
            if not self.newSettings[KEY_OVERRIDE_TEMPLATE]:
                self.blog.setTemplateId(None)

        self._getAccountStore().saveAccount(self.blog.getAccount())

        self.newSettings = {}
    # end apply()

    def rollback(self):
        self.newSettings = {}
    # end rollback()

# end ZBlogPrefsSession


# ------------------------------------------------------------------------------
# Implements the prefs page that is shown in the account manager when the user
# clicks on an blog.
# ------------------------------------------------------------------------------
class ZBlogPrefsPage(ZBasePrefsPage):

    def __init__(self, parent, blog):
        self.blog = blog

        ZBasePrefsPage.__init__(self, parent)
    # end __init__()

    def _createSession(self):
        return ZBlogPrefsSession(self, self.blog)
    # end _createSession()

    def _createPrefsSubPages(self, parent):
        bmp = getResourceRegistry().getBitmap(u"images/dialogs/account/manager/account_pages/publishing.png") #$NON-NLS-1$
        self.pubPage = ZBlogPublishingPrefSubPage(parent, self.session)
        self.toolBook.addPage(self.pubPage, _extstr(u"blogpage.Publishing"), _extstr(u"blogpage.Publishing_Description"), bmp) #$NON-NLS-2$ #$NON-NLS-1$

        bmp = getResourceRegistry().getBitmap(u"images/dialogs/account/manager/account_pages/media_store.png") #$NON-NLS-1$
        self.storePage = ZBlogMediaStoragePrefSubPage(parent, self.session)
        self.toolBook.addPage(self.storePage, _extstr(u"blogpage.Media_Store"), _extstr(u"blogpage.Media_Store_Description"), bmp) #$NON-NLS-2$ #$NON-NLS-1$

        bmp = getResourceRegistry().getBitmap(u"images/dialogs/account/manager/account_pages/template.png") #$NON-NLS-1$
        self.templatePage = ZBlogTemplatePrefSubPage(parent, self.session)
        self.toolBook.addPage(self.templatePage, _extstr(u"blogpage.Template"), _extstr(u"blogpage.Template_Description"), bmp) #$NON-NLS-2$ #$NON-NLS-1$

        bmp = getResourceRegistry().getBitmap(u"images/dialogs/account/manager/account_pages/ping_sites.png") #$NON-NLS-1$
        self.sitesPage = ZBlogPingSitesPrefSubPage(parent, self.session)
        self.toolBook.addPage(self.sitesPage, _extstr(u"blogpage.Ping_Sites"), _extstr(u"blogpage.Ping_Sites_Description"), bmp) #$NON-NLS-2$ #$NON-NLS-1$
        
        bmp = getResourceRegistry().getBitmap(u"images/dialogs/account/manager/account_pages/tag_sites.png") #$NON-NLS-1$
        self.tagsPage = ZBlogTagSitesPrefSubPage(parent, self.session)
        self.toolBook.addPage(self.tagsPage, _extstr(u"blogpage.Tag_Sites"), _extstr(u"blogpage.Tag_Sites_Description"), bmp) #$NON-NLS-2$ #$NON-NLS-1$
        
    # end _createPrefsSubPages()

    def populateWidgets(self):
        self.pubPage._populateWidgets()
        self.storePage._populateWidgets()
        self.sitesPage._populateWidgets()
        self.tagsPage._populateWidgets()
    # end populateWidgets()

    def bindWidgetEvents(self):
        self._bindValidatingWidget(self.pubPage)
        self._bindValidatingWidget(self.storePage)
        self._bindValidatingWidget(self.sitesPage)
        self._bindValidatingWidget(self.tagsPage)
    # end bindWidgetEvents()

# end ZBlogPrefsPage
