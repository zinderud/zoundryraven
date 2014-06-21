from zoundry.blogapp.services.pubsystems.blog.blogcommands import createBlogPublisher
from zoundry.blogpub.blogserverapi import IZBlogApiParamConstants
from zoundry.blogapp.constants import IZBlogAppServiceIDs
from zoundry.appframework.global_services import getApplicationModel

# -----------------------------------------------------------------------------------------
# The model behind the New Publisher Site Wizard.
# -----------------------------------------------------------------------------------------
class ZNewPublisherSiteWizardModel:

    def __init__(self):
        self.publisherService = getApplicationModel().getService(IZBlogAppServiceIDs.PUBLISHING_SERVICE_ID)
        self.accStoreService = getApplicationModel().getService(IZBlogAppServiceIDs.ACCOUNT_STORE_SERVICE_ID)
        self.mediaStoreService = getApplicationModel().getService((IZBlogAppServiceIDs.MEDIA_STORAGE_SERVICE_ID))        
 
    def listPublisherSites(self):
        return self.publisherService.listPublisherSites()
    
    def getPublisherSite(self, siteId):
        siteDef = self.publisherService.getPublisherSite(siteId)
        return siteDef
    
    def getMediaStorages(self):
        return self.mediaStoreService.getMediaStorages()
    # end getMediaStorages()

    def getMediaSite(self, mediaStore):
        siteId = mediaStore.getMediaSiteId()
        return self.mediaStoreService.getMediaSite(siteId)
    
    def accountNameExists(self, accName):
        rval = False
        if accName:
            rval = self.accStoreService.hasAccount(accName)
        return rval
    # end __init__()
    
    def getDefaultApiUrl(self, siteDef):
        url = None
        if siteDef:
            url =  siteDef.getParameters().getParameter(IZBlogApiParamConstants.API_ENDPOINT_URL)
            if not url and siteDef.getPublisherTypeDef():
                url = siteDef.getPublisherTypeDef().getParameters().getParameter(IZBlogApiParamConstants.API_ENDPOINT_URL)
        return url
      
    def autodiscover(self, siteUrl ):  
        discoveryInfo = self.publisherService.autodiscover(siteUrl)
        return discoveryInfo

    def listBlogs(self, siteId, username, password, url):
        publisher = createBlogPublisher(username, password, url, siteId, self.publisherService)
        rval = publisher.listBlogs()
        return rval