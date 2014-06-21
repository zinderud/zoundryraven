from zoundry.appframework.global_services import getApplicationModel
from zoundry.blogapp.constants import IZBlogAppServiceIDs

# ------------------------------------------------------------------------------------
# Compares two media storages by their name.
# ------------------------------------------------------------------------------------
def _cmpMediaStorages(store1, store2):
    return cmp(store1.getName().lower(), store2.getName().lower())
# end _cmpMediaStorages()


# ------------------------------------------------------------------------------------
# Content provider used to populate the list of media storages.
# ------------------------------------------------------------------------------------
class ZMediaStorageManagerModel:

    def __init__(self):
        self.mediaStorageService = getApplicationModel().getService(IZBlogAppServiceIDs.MEDIA_STORAGE_SERVICE_ID)
        self.mediaStorages = None
        self.refresh()
    # end __init__()

    def refresh(self):
        self.mediaStorages = []
        for storage in self.mediaStorageService.getMediaStorages():
            if self._shouldIncludeStorage(storage):
                self.mediaStorages.append(storage)
        self.mediaStorages.sort(_cmpMediaStorages)
    # end refresh()
    
    # Only include storages that are not internal.
    def _shouldIncludeStorage(self, storage):
        siteId = storage.getMediaSiteId()
        site = self.getService().getMediaSite(siteId)
        return site is not None and not site.isInternal()
    # end _shouldIncludeStorage()

    def getService(self):
        return self.mediaStorageService
    # end getService()
    
    def getMediaSites(self):
        return self.mediaStorageService.getMediaSites()
    # end getMediaSites()

    def getMediaStorages(self):
        return self.mediaStorages
    # end getMediaStorages()

    def getMediaSite(self, mediaStore):
        siteId = mediaStore.getMediaSiteId()
        return self.mediaStorageService.getMediaSite(siteId)
    # end getMediaSite()

    def getImageKey(self, mediaStore):
        return self.getMediaSite(mediaStore).getId()
    # end getImageKey()

    def getIconPath(self, mediaStore):
        return self.getMediaSite(mediaStore).getIconPath()
    # end getIconPath()

    def deleteStore(self, mediaStore):
        self.mediaStorageService.deleteMediaStorage(mediaStore)
    # end deleteStore()

# end ZMediaStorageManagerModel
