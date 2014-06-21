from zoundry.base.util.types.list import ZSortedList
from zoundry.appframework.global_services import getApplicationModel
from zoundry.base.util.types.list import ZDefaultListComparator
from zoundry.blogapp.constants import IZBlogAppServiceIDs

# -----------------------------------------------------------------------------------------
# Comparator used for sorting media sites.
# -----------------------------------------------------------------------------------------
class ZMediaSiteComparator(ZDefaultListComparator):

    def compare(self, object1, object2):
        if object1.getDisplayName() < object2.getDisplayName():
            return -1
        if object1.getDisplayName() > object2.getDisplayName():
            return 1
        return 0
    # end compare()

# end ZMediaSiteComparator


# -----------------------------------------------------------------------------------------
# The model behind the New Media Storage Wizard.
# -----------------------------------------------------------------------------------------
class ZNewMediaStorageWizardModel:

    def __init__(self):
        self.mediaStoreService = getApplicationModel().getService(IZBlogAppServiceIDs.MEDIA_STORAGE_SERVICE_ID)
        self.mediaSites = self._getAndSortMediaSites()
    # end __init__()
    
    def _getAndSortMediaSites(self):
        sites = self.mediaStoreService.getMediaSites()
        rval = ZSortedList(ZMediaSiteComparator())
        rval.addAll(sites)
        return rval
    # end _getAndSortMediaSites()

    def getMediaSites(self):
        return self.mediaSites
    # end getMediaSites()

    def mediaStoreExists(self, mediaStoreName):
        return self.mediaStoreService.hasMediaStorage(mediaStoreName)
    # end mediaStoreExists()

# end ZNewMediaStorageWizardModel
