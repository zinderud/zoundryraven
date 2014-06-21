from zoundry.appframework.global_services import getApplicationModel
from zoundry.blogapp.constants import IZBlogAppServiceIDs


# ------------------------------------------------------------------------------------
# Model used by the media storage editor dialog.
# ------------------------------------------------------------------------------------
class ZEditMediaStorageModel:

    def __init__(self, store):
        self.store = store
        self.mediaStoreService = getApplicationModel().getService(IZBlogAppServiceIDs.MEDIA_STORAGE_SERVICE_ID)
    # end __init__()
    
    def getMediaStorage(self):
        return self.store
    # end getMediaStorage()
    
    def getMediaSite(self):
        return self.mediaStoreService.getMediaSite(self.store.getMediaSiteId())
    # end getMediaSite()

    def getService(self):
        return self.mediaStoreService
    # end getService()

    def updateStore(self, properties):
        for key in properties:
            value = properties[key]
            self.store.getProperties()[key] = value
        self.mediaStoreService.saveMediaStorage(self.store)
    # end updateStore()

# end ZMediaStorageManagerModel
