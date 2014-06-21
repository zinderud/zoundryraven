from zoundry.blogapp.exceptions import ZBlogAppException
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.services.mediastorage.mediasite import IZMediaSite
from zoundry.blogapp.services.mediastorage.mediastoragetypeimpl import ZMediaStorageCapabilities
from zoundry.blogapp.services.mediastorage.mediastoragetypeimpl import ZMediaStorageProperty

# ------------------------------------------------------------------------------------------
# A concrete implementation of a media site.  This impl uses a media site def which wraps
# an extension point found in a plugin, as well as a media storage type.
# ------------------------------------------------------------------------------------------
class ZMediaSite(IZMediaSite):

    def __init__(self, mediaSiteDef):
        self.mediaSiteDef = mediaSiteDef
        self.mediaStoreType = None
        self.properties = None
        self.capabilities = None
    # end __init__()

    def setMediaStorageType(self, mediaStoreType):
        self.mediaStoreType = mediaStoreType
    # end setMediaStorageType()

    def getId(self):
        return self.mediaSiteDef.getId()
    # end getId()

    def getDisplayName(self):
        return self.mediaSiteDef.getDisplayName()
    # end getDisplayName()

    def getIconPath(self):
        iconPath = self.mediaSiteDef.getIconPath()
        if iconPath is None:
            iconPath = self.mediaStoreType.getIconPath()
        return iconPath
    # end getIconPath()

    def getProperties(self):
        if self.properties is None:
            # 1) Get the properties from the store type
            self.properties = self._cloneStoreTypeProperties()
            # 2) Override those properties with properties from the site def.
            siteProps = self.mediaSiteDef.getProperties()
            for subMap in siteProps:
                prop = ZMediaStorageProperty(subMap)
                self._overrideProperty(prop)
        return self.properties
    # end getProperties()

    def getCapabilities(self):
        if self.capabilities is None:
            # 1) Get the capabilities from the store type
            self.capabilities = self.mediaStoreType.getCapabilities().clone()
            # 2) Override those with the capabilities set in the site
            self.capabilities.override(ZMediaStorageCapabilities(self.mediaSiteDef.getCapabilities()))
        return self.capabilities
    # end getCapabilities()

    def createContributedWizardPages(self):
        return self.mediaStoreType.createContributedWizardPages()
    # end createContributedWizardPages()

    def getMediaStorageTypeId(self):
        return self.mediaSiteDef.getMediaStorageTypeId()
    # end getMediaStorageTypeId()
    
    def isInternal(self):
        return self.mediaSiteDef.isInternal()
    # end isInternal()
    
    def _cloneStoreTypeProperties(self):
        rval = []
        for prop in self.mediaStoreType.getProperties():
            rval.append(prop.clone())
        return rval
    # end _cloneStoreTypeProperties()
    
    def _overrideProperty(self, property):
        for prop in self.properties:
            if prop.getName() == property.getName():
                prop.override(property)
                return
        raise ZBlogAppException(_extstr(u"mediasiteimpl.InvalidPropertyOverride") % property.getName()) #$NON-NLS-1$
    # end _overrideProperty()

# end ZMediaSite
