from zoundry.blogapp.ui.util.tagsiteutil import serializeTagSiteList
from zoundry.blogapp.ui.util.tagsiteutil import deserializeTagSiteList
from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.ui.dialogs.prefpage import IZUserPreferencePageSession
from zoundry.appframework.ui.dialogs.prefpage import ZUserPreferencePage
from zoundry.appframework.ui.widgets.controls.advanced.toolbook import ZToolBook
from zoundry.base.exceptions import ZAbstractMethodCalledException
from zoundry.blogapp.constants import IZBlogAppServiceIDs
from zoundry.blogapp.constants import IZBlogAppUserPrefsKeys
from zoundry.blogapp.ui.util.pingsiteutil import deserializePingSiteList
from zoundry.blogapp.ui.util.pingsiteutil import serializePingSiteList
import wx

KEY_OVERRIDE_PUB_SETTINGS = u"override-pub-settings" #$NON-NLS-1$
KEY_STORE_ID = u"store-id" #$NON-NLS-1$
KEY_TEMPLATE_ID = u"template-id" #$NON-NLS-1$
KEY_ADD_POWERED_BY = u"add-powered-by" #$NON-NLS-1$
KEY_UPLOAD_TNS_ONLY = u"upload-tns-only" #$NON-NLS-1$
KEY_FORCE_REUPLOAD = u"force-reupload" #$NON-NLS-1$
KEY_ADD_LIGHTBOX = u"add-lightbox" #$NON-NLS-1$
KEY_OVERRIDE_PING_SITES = u"override-ping-sites" #$NON-NLS-1$
KEY_PING_SITES = u"ping-sites" #$NON-NLS-1$
KEY_OVERRIDE_TAG_SITES = u"override-tag-sites" #$NON-NLS-1$
KEY_TAG_SITES = u"tag-sites" #$NON-NLS-1$
KEY_REMOVE_NEWLINES = u"remove-newlines" #$NON-NLS-1$

# ------------------------------------------------------------------------------
# Base class for the session objects used by the account and blog pages.
# ------------------------------------------------------------------------------
class ZBasePrefsSession(IZUserPreferencePageSession):

    def __init__(self, prefPage):
        self.prefPage = prefPage
        self.userPrefs = self._createUserPrefs()

        self.newSettings = {}
    # end __init__()

    def _getAccountStore(self):
        return getApplicationModel().getService(IZBlogAppServiceIDs.ACCOUNT_STORE_SERVICE_ID)
    # end _getAccountStore()

    def _createUserPrefs(self):
        raise ZAbstractMethodCalledException(self.__class__, u"_createUserPrefs") #$NON-NLS-1$
    # end _createUserPrefs()

    def isOverridePublishingSettings(self):
        if KEY_OVERRIDE_PUB_SETTINGS in self.newSettings:
            return self.newSettings[KEY_OVERRIDE_PUB_SETTINGS]
        else:
            return self._isOverridePublishingSettings()
    # end isOverridePublishingSettings()

    def _isOverridePublishingSettings(self):
        return self.userPrefs.getUserPreferenceBool(self._getOverridePublishingSettingsKey(), False)
    # end isOverridePublishingSettings()

    def _getOverridePublishingSettingsKey(self):
        raise ZAbstractMethodCalledException(self.__class__, u"_getOverridePublishingSettingsKey") #$NON-NLS-1$
    # end _getOverridePublishingSettingsKey()

    def setOverridePublishingSettings(self, bValue):
        self.newSettings[KEY_OVERRIDE_PUB_SETTINGS] = bValue
        if self._isOverridePublishingSettings() == bValue:
            del self.newSettings[KEY_OVERRIDE_PUB_SETTINGS]
        if not bValue:
            if KEY_ADD_POWERED_BY in self.newSettings:
                del self.newSettings[KEY_ADD_POWERED_BY]
            if KEY_REMOVE_NEWLINES in self.newSettings:
                del self.newSettings[KEY_REMOVE_NEWLINES]                
            if KEY_UPLOAD_TNS_ONLY in self.newSettings:
                del self.newSettings[KEY_UPLOAD_TNS_ONLY]
            if KEY_FORCE_REUPLOAD in self.newSettings:
                del self.newSettings[KEY_FORCE_REUPLOAD]
            if KEY_ADD_LIGHTBOX in self.newSettings:
                del self.newSettings[KEY_ADD_LIGHTBOX]

        self.prefPage.onSessionChange()
    # end setOverridePublishingSettings()

    def isAddPoweredByZoundry(self):
        if KEY_ADD_POWERED_BY in self.newSettings:
            return self.newSettings[KEY_ADD_POWERED_BY]
        else:
            return self._isAddPoweredByZoundry()
    # end isAddPoweredByZoundry()

    def _isAddPoweredByZoundry(self):
        return self.userPrefs.getUserPreferenceBool(IZBlogAppUserPrefsKeys.SP_ADD_POWERED_BY, False)
    # end _isAddPoweredByZoundry()

    def setAddPoweredByZoundry(self, bValue):
        self.newSettings[KEY_ADD_POWERED_BY] = bValue
        if self._isAddPoweredByZoundry() == bValue:
            del self.newSettings[KEY_ADD_POWERED_BY]
        self.prefPage.onSessionChange()
    # end setAddPoweredByZoundry()
    
    def isRemoveNewLines(self):
        if KEY_REMOVE_NEWLINES in self.newSettings:
            return self.newSettings[KEY_REMOVE_NEWLINES]
        else:
            return self._isRemoveNewLines()
    # end isRemoveNewLines()

    def _isRemoveNewLines(self):
        return self.userPrefs.getUserPreferenceBool(IZBlogAppUserPrefsKeys.SP_REMOVE_NEWLINES, False)
    # end _isRemoveNewLines()

    def setRemoveNewLines(self, bValue):
        self.newSettings[KEY_REMOVE_NEWLINES] = bValue
        if self._isRemoveNewLines() == bValue:
            del self.newSettings[KEY_REMOVE_NEWLINES]
        self.prefPage.onSessionChange()
    # end setRemoveNewLines()    

    def isUploadThumbnailsOnly(self):
        if KEY_UPLOAD_TNS_ONLY in self.newSettings:
            return self.newSettings[KEY_UPLOAD_TNS_ONLY]
        else:
            return self._isUploadThumbnailsOnly()
    # end isUploadThumbnailsOnly()

    def _isUploadThumbnailsOnly(self):
        return self.userPrefs.getUserPreferenceBool(IZBlogAppUserPrefsKeys.SP_UPLOAD_TNS_ONLY, False)
    # end _isUploadThumbnailsOnly()

    def setUploadThumbnailsOnly(self, bValue):
        self.newSettings[KEY_UPLOAD_TNS_ONLY] = bValue
        if self._isUploadThumbnailsOnly() == bValue:
            del self.newSettings[KEY_UPLOAD_TNS_ONLY]
        self.prefPage.onSessionChange()
    # end setUploadThumbnailsOnly()

    def isForceReupload(self):
        if KEY_FORCE_REUPLOAD in self.newSettings:
            return self.newSettings[KEY_FORCE_REUPLOAD]
        else:
            return self._isForceReupload()
    # end isForceReupload()

    def _isForceReupload(self):
        return self.userPrefs.getUserPreferenceBool(IZBlogAppUserPrefsKeys.SP_FORCE_REUPLOAD, False)
    # end _isForceReupload()

    def setForceReupload(self, bValue):
        self.newSettings[KEY_FORCE_REUPLOAD] = bValue
        if self._isForceReupload() == bValue:
            del self.newSettings[KEY_FORCE_REUPLOAD]
        self.prefPage.onSessionChange()
    # end setForceReupload()

    def isAddLightbox(self):
        if KEY_ADD_LIGHTBOX in self.newSettings:
            return self.newSettings[KEY_ADD_LIGHTBOX]
        else:
            return self._isAddLightbox()
    # end isAddLightbox()

    def _isAddLightbox(self):
        return self.userPrefs.getUserPreferenceBool(IZBlogAppUserPrefsKeys.SP_ADD_LIGHTBOX, False)
    # end _isAddLightbox()

    def setAddLightbox(self, bValue):
        self.newSettings[KEY_ADD_LIGHTBOX] = bValue
        if self._isAddLightbox() == bValue:
            del self.newSettings[KEY_ADD_LIGHTBOX]
        self.prefPage.onSessionChange()
    # end setAddLightbox()

    def getStoreId(self):
        if KEY_STORE_ID in self.newSettings:
            return self.newSettings[KEY_STORE_ID]
        else:
            return self._getStoreId()
    # end getStoreId()

    def _getStoreId(self):
        raise ZAbstractMethodCalledException(self.__class__, u"_getStoreId") #$NON-NLS-1$
    # end _getStoreId()

    def setStoreId(self, storeId):
        self.newSettings[KEY_STORE_ID] = storeId
        if self._getStoreId() == storeId:
            del self.newSettings[KEY_STORE_ID]
        self.prefPage.onSessionChange()
    # end setStoreId()

    def _setStoreId(self, storeId):
        raise ZAbstractMethodCalledException(self.__class__, u"_setStoreId") #$NON-NLS-1$
    # end _setStoreId()

    def getTemplateId(self):
        if KEY_TEMPLATE_ID in self.newSettings:
            return self.newSettings[KEY_TEMPLATE_ID]
        else:
            return self._getTemplateId()
    # end getTemplateId()

    def _getTemplateId(self):
        raise ZAbstractMethodCalledException(self.__class__, u"_getTemplateId") #$NON-NLS-1$
    # end _getTemplateId()

    def setTemplateId(self, templateId):
        self.newSettings[KEY_TEMPLATE_ID] = templateId
        if self._getTemplateId() == templateId:
            del self.newSettings[KEY_TEMPLATE_ID]
        self.prefPage.onSessionChange()
    # end setTemplateId()

    def _setTemplateId(self, templateId):
        raise ZAbstractMethodCalledException(self.__class__, u"_setTemplateId") #$NON-NLS-1$
    # end _setTemplateId()

    def isOverridePingSites(self):
        if KEY_OVERRIDE_PING_SITES in self.newSettings:
            return self.newSettings[KEY_OVERRIDE_PING_SITES]
        else:
            return self._isOverridePingSites()
    # end isOverridePingSites()

    def _isOverridePingSites(self):
        return self.userPrefs.getUserPreferenceBool(self._getOverridePingSitesKey(), False)
    # end isOverridePingSites()

    def _getOverridePingSitesKey(self):
        raise ZAbstractMethodCalledException(self.__class__, u"_getOverridePingSitesKey") #$NON-NLS-1$
    # end _getOverridePingSitesKey()

    def setOverridePingSites(self, bValue):
        self.newSettings[KEY_OVERRIDE_PING_SITES] = bValue
        if self._isOverridePingSites() == bValue:
            del self.newSettings[KEY_OVERRIDE_PING_SITES]
        # Remove ping sites setting if we are no longer overriding.
        if not bValue and KEY_PING_SITES in self.newSettings:
            del self.newSettings[KEY_PING_SITES]
        self.prefPage.onSessionChange()
    # end setOverridePingSites()

    def getSelectedPingSites(self):
        if KEY_PING_SITES in self.newSettings:
            return deserializePingSiteList( self.newSettings[KEY_PING_SITES] )
        else:
            return self._getSelectedPingSites()
    # end getSelectedPingSites()

    def _getSelectedPingSites(self):
        sitesStr = self.userPrefs.getUserPreference(IZBlogAppUserPrefsKeys.SP_PING_SITES, None)
        return deserializePingSiteList(sitesStr)
    # end _getSelectedPingSites()

    def setSelectedPingSites(self, sites):
        sitesStr = serializePingSiteList(sites)
        self.newSettings[KEY_PING_SITES] = sitesStr
        if self.userPrefs.getUserPreference(IZBlogAppUserPrefsKeys.SP_PING_SITES, None) == sitesStr:
            del self.newSettings[KEY_PING_SITES]

        self.prefPage.onSessionChange()
    # end setSelectedPingSites()

    def isOverrideTagSites(self):
        if KEY_OVERRIDE_TAG_SITES in self.newSettings:
            return self.newSettings[KEY_OVERRIDE_TAG_SITES]
        else:
            return self._isOverrideTagSites()
    # end isOverrideTagSites()

    def _isOverrideTagSites(self):
        return self.userPrefs.getUserPreferenceBool(self._getOverrideTagSitesKey(), False)
    # end isOverrideTagSites()

    def _getOverrideTagSitesKey(self):
        raise ZAbstractMethodCalledException(self.__class__, u"_getOverrideTagSitesKey") #$NON-NLS-1$
    # end _getOverrideTagSitesKey()

    def setOverrideTagSites(self, bValue):
        self.newSettings[KEY_OVERRIDE_TAG_SITES] = bValue
        if self._isOverrideTagSites() == bValue:
            del self.newSettings[KEY_OVERRIDE_TAG_SITES]
        # Remove tag sites setting if we are no longer overriding.
        if not bValue and KEY_TAG_SITES in self.newSettings:
            del self.newSettings[KEY_TAG_SITES]
        self.prefPage.onSessionChange()
    # end setOverrideTagSites()

    def getSelectedTagSites(self):
        if KEY_TAG_SITES in self.newSettings:
            return deserializeTagSiteList( self.newSettings[KEY_TAG_SITES] )
        else:
            return self._getSelectedTagSites()
    # end getSelectedTagSites()

    def _getSelectedTagSites(self):
        sitesStr = self.userPrefs.getUserPreference(IZBlogAppUserPrefsKeys.SP_TAG_SITES, None)
        return deserializeTagSiteList(sitesStr)
    # end _getSelectedTagSites()

    def setSelectedTagSites(self, sites):
        sitesStr = serializeTagSiteList(sites)
        self.newSettings[KEY_TAG_SITES] = sitesStr
        if self.userPrefs.getUserPreference(IZBlogAppUserPrefsKeys.SP_TAG_SITES, None) == sitesStr:
            del self.newSettings[KEY_TAG_SITES]

        self.prefPage.onSessionChange()
    # end setSelectedTagSites()

    def isDirty(self):
        return len(self.newSettings) > 0
    # end isDirty()

    def apply(self):
        if KEY_STORE_ID in self.newSettings:
            self._setStoreId(self.newSettings[KEY_STORE_ID])
        if KEY_TEMPLATE_ID in self.newSettings:
            self._setTemplateId(self.newSettings[KEY_TEMPLATE_ID])
        if KEY_ADD_POWERED_BY in self.newSettings:
            self.userPrefs.setUserPreference(IZBlogAppUserPrefsKeys.SP_ADD_POWERED_BY, self.newSettings[KEY_ADD_POWERED_BY])
        if KEY_REMOVE_NEWLINES in self.newSettings:
            self.userPrefs.setUserPreference(IZBlogAppUserPrefsKeys.SP_REMOVE_NEWLINES, self.newSettings[KEY_REMOVE_NEWLINES])            
        if KEY_UPLOAD_TNS_ONLY in self.newSettings:
            self.userPrefs.setUserPreference(IZBlogAppUserPrefsKeys.SP_UPLOAD_TNS_ONLY, self.newSettings[KEY_UPLOAD_TNS_ONLY])
        if KEY_FORCE_REUPLOAD in self.newSettings:
            self.userPrefs.setUserPreference(IZBlogAppUserPrefsKeys.SP_FORCE_REUPLOAD, self.newSettings[KEY_FORCE_REUPLOAD])
        if KEY_ADD_LIGHTBOX in self.newSettings:
            self.userPrefs.setUserPreference(IZBlogAppUserPrefsKeys.SP_ADD_LIGHTBOX, self.newSettings[KEY_ADD_LIGHTBOX])
        if KEY_PING_SITES in self.newSettings:
            self.userPrefs.setUserPreference(IZBlogAppUserPrefsKeys.SP_PING_SITES, self.newSettings[KEY_PING_SITES])
        if KEY_TAG_SITES in self.newSettings:
            self.userPrefs.setUserPreference(IZBlogAppUserPrefsKeys.SP_TAG_SITES, self.newSettings[KEY_TAG_SITES])

        # If the user is turning off the pub settings override, then we need
        # to remove all of the relevant prefs so that the inheritance from
        # the parent prefs works properly.
        if KEY_OVERRIDE_PUB_SETTINGS in self.newSettings:
            self.userPrefs.setUserPreference(self._getOverridePublishingSettingsKey(), self.newSettings[KEY_OVERRIDE_PUB_SETTINGS])
            if not self.newSettings[KEY_OVERRIDE_PUB_SETTINGS]:
                self.userPrefs.removeUserPreference(IZBlogAppUserPrefsKeys.SP_ADD_POWERED_BY)
                self.userPrefs.removeUserPreference(IZBlogAppUserPrefsKeys.SP_REMOVE_NEWLINES)
                self.userPrefs.removeUserPreference(IZBlogAppUserPrefsKeys.SP_UPLOAD_TNS_ONLY)
                self.userPrefs.removeUserPreference(IZBlogAppUserPrefsKeys.SP_FORCE_REUPLOAD)
                self.userPrefs.removeUserPreference(IZBlogAppUserPrefsKeys.SP_ADD_LIGHTBOX)
        # See above comment
        if KEY_OVERRIDE_PING_SITES in self.newSettings:
            self.userPrefs.setUserPreference(self._getOverridePingSitesKey(), self.newSettings[KEY_OVERRIDE_PING_SITES])
            if not self.newSettings[KEY_OVERRIDE_PING_SITES]:
                self.userPrefs.removeUserPreference(IZBlogAppUserPrefsKeys.SP_PING_SITES)
        if KEY_OVERRIDE_TAG_SITES in self.newSettings:
            self.userPrefs.setUserPreference(self._getOverrideTagSitesKey(), self.newSettings[KEY_OVERRIDE_TAG_SITES])
            if not self.newSettings[KEY_OVERRIDE_TAG_SITES]:
                self.userPrefs.removeUserPreference(IZBlogAppUserPrefsKeys.SP_TAG_SITES)

    # end apply()

    def rollback(self):
        self.newSettings = {}
    # end rollback()

# end ZBasePrefsSession


# ------------------------------------------------------------------------------
# Base class for an account prefs dialog's prefs pages.
# ------------------------------------------------------------------------------
class ZBasePrefsPage(ZUserPreferencePage):

    def __init__(self, parent):
        ZUserPreferencePage.__init__(self, parent)
    # end __init__()

    def onSessionChange(self):
        self._firePrefPageChangeEvent()
    # end onSessionChange()

    def createWidgets(self):
        self.toolBook = ZToolBook(self)
        self.verticalLine = wx.StaticLine(self, style = wx.LI_VERTICAL)

        self._createPrefsSubPages(self.toolBook)
    # end createWidgets()

    def layoutWidgets(self):
        boxSizer = wx.BoxSizer(wx.HORIZONTAL)
        boxSizer.Add(self.verticalLine, 0, wx.EXPAND)
        boxSizer.Add(self.toolBook, 1, wx.EXPAND)

        self.SetAutoLayout(True)
        self.SetSizer(boxSizer)
        self.Layout()
    # end layoutWidgets()

# end ZBasePrefsPage
