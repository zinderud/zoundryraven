from zoundry.base.util.types.capabilities import ZCapabilities
from zoundry.blogapp.services.mediastorage.mediastoragetype import IZMediaStorageCapabilities
from zoundry.blogapp.services.mediastorage.mediastoragetype import IZMediaStorageProperty
from zoundry.blogapp.services.mediastorage.mediastoragetype import IZMediaStorageType

# --------------------------------------------------------------------------------------------
# Concrete implementation of a media storage property.
# --------------------------------------------------------------------------------------------
class ZMediaStorageProperty(IZMediaStorageProperty):

    def __init__(self, propertyMap):
        self.propertyMap = propertyMap
    # end __init__()

    def getName(self):
        return self._getProperty(u"name") #$NON-NLS-1$
    # end getName()

    def getType(self):
        return self._getProperty(u"type") #$NON-NLS-1$
    # end getType()

    def getDisplayName(self):
        return self._getProperty(u"display-name") #$NON-NLS-1$
    # end getDisplayName()

    def getTooltip(self):
        return self._getProperty(u"tooltip") #$NON-NLS-1$
    # end getTooltip()

    def getValidationRegexp(self):
        return self._getProperty(u"validation-regexp") #$NON-NLS-1$
    # end getValidationRegexp()

    def getValidationErrorMessage(self):
        return self._getProperty(u"validation-error-message") #$NON-NLS-1$
    # end getValidationErrorMessage()

    def getDefaultValue(self):
        return self._getProperty(u"default-value") #$NON-NLS-1$
    # end getDefaultValue()

    def isHidden(self):
        return u"true" == self._getHidden() #$NON-NLS-1$
    # end isHidden()

    def _getHidden(self):
        return self._getProperty(u"hidden") #$NON-NLS-1$
    # end _getHidden()

    def clone(self):
        return ZMediaStorageProperty(self.propertyMap.copy())
    # end clone()

    def override(self, property):
        type = property.getType()
        displayName = property.getDisplayName()
        tooltip = property.getTooltip()
        regexp = property.getValidationRegexp()
        errorMsg = property.getValidationErrorMessage()
        defaultValue = property.getDefaultValue()
        hidden = property._getHidden()

        self._setProperty(u"type", type) #$NON-NLS-1$
        self._setProperty(u"display-name", displayName) #$NON-NLS-1$
        self._setProperty(u"tooltip", tooltip) #$NON-NLS-1$
        self._setProperty(u"validation-regexp", regexp) #$NON-NLS-1$
        self._setProperty(u"validation-error-message", errorMsg) #$NON-NLS-1$
        self._setProperty(u"default-value", defaultValue) #$NON-NLS-1$
        self._setProperty(u"hidden", hidden) #$NON-NLS-1$
    # end override()

    def _getProperty(self, propertyKey):
        if propertyKey in self.propertyMap:
            rval = self.propertyMap[propertyKey]
            if rval:
                return rval
        return None
    # end _getProperty()

    def _setProperty(self, propName, value):
        if value is not None:
            self.propertyMap[propName] = value
    # end _setProperty()

# end ZMediaStorageProperty


# --------------------------------------------------------------------------------------------
# A concrete implementation of media storage capabilities.
# --------------------------------------------------------------------------------------------
class ZMediaStorageCapabilities(ZCapabilities, IZMediaStorageCapabilities):

    def __init__(self, capabilityMap):
        ZCapabilities.__init__(self)

        self.capabilityMap = capabilityMap
    # end __init__()

    def supportsDelete(self):
        return self.hasCapability(IZMediaStorageCapabilities.KEY_SUPPORTS_DELETE)
    # end supportsDelete()

    def supportsFileList(self):
        return self.hasCapability(IZMediaStorageCapabilities.KEY_SUPPORTS_FILE_LIST)
    # end supportsFileList()

    def supportsVideoFiles(self):
        return self.supportsAnyFile() or self.hasCapability(IZMediaStorageCapabilities.KEY_SUPPORTS_VIDEO_FILES)
    # end supportsVideoFiles()

    def supportsImageFiles(self):
        return self.supportsAnyFile() or self.hasCapability(IZMediaStorageCapabilities.KEY_SUPPORTS_IMAGE_FILES)
    # end supportsImageFiles()

    def supportsAnyFile(self):
        return self.hasCapability(IZMediaStorageCapabilities.KEY_SUPPORTS_ANYTYPE_FILES)
    # end supportsAnyFile()

    def clone(self):
        return ZMediaStorageCapabilities(self.capabilityMap)
    # end clone()

# end ZMediaStorageCapabilities


# --------------------------------------------------------------------------------------------
# A concrete implementation of a media storage type.  Instances of this class are created using
# meta data found in plugins.
# --------------------------------------------------------------------------------------------
class ZMediaStorageType(IZMediaStorageType):

    def __init__(self, mediaStoreTypeDef):
        self.mediaStoreTypeDef = mediaStoreTypeDef
        self.properties = None
        self.capabilities = None
    # end __init__()

    def getId(self):
        return self.mediaStoreTypeDef.getId()
    # end getId()

    def getClass(self):
        return self.mediaStoreTypeDef.getClass()
    # end getClass()

    def getProperties(self):
        if self.properties is None:
            self.properties = []
            typeProps = self.mediaStoreTypeDef.getProperties()
            for subMap in typeProps:
                self.properties.append(ZMediaStorageProperty(subMap))
        return self.properties
    # end getProperties()

    def getCapabilities(self):
        if self.capabilities is None:
            self.capabilities = ZMediaStorageCapabilities(self.mediaStoreTypeDef.getCapabilities())
        return self.capabilities
    # end getCapabilities()

    def createContributedWizardPages(self):
        return self.mediaStoreTypeDef.createContributedWizardPages()
    # end createContributedWizardPages()

    def getIconPath(self):
        return self.mediaStoreTypeDef.getIconPath()
    # end getIconPath()

# end ZMediaStorageType
