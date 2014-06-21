from zoundry.base.util.types.capabilities import IZCapabilities

# ----------------------------------------------------------------------------------------------
# The set of capabilities that a given media storage supports.
# ----------------------------------------------------------------------------------------------
class IZMediaStorageCapabilities(IZCapabilities):

    KEY_SUPPORTS_DELETE = u"zoundry.raven.capability.mediastorage.supports-delete" #$NON-NLS-1$
    KEY_SUPPORTS_FILE_LIST = u"zoundry.raven.capability.mediastorage.supports-file-list" #$NON-NLS-1$
    KEY_SUPPORTS_IMAGE_FILES = u"zoundry.raven.capability.mediastorage.supports-image-files" #$NON-NLS-1$
    KEY_SUPPORTS_VIDEO_FILES = u"zoundry.raven.capability.mediastorage.supports-video-files" #$NON-NLS-1$
    KEY_SUPPORTS_ANYTYPE_FILES = u"zoundry.raven.capability.mediastorage.supports-anytype-files" #$NON-NLS-1$

    def supportsDelete(self):
        u"Returns True if the site supports deleting previously uploaded files." #$NON-NLS-1$
    # end supportsDelete()

    def supportsFileList(self):
        u"Returns True if the site supports listing the remote files." #$NON-NLS-1$
    # end supportsFileList()

    def supportsVideoFiles(self):
        u"Returns True if the site supports video files files." #$NON-NLS-1$
    # end supportsVideoFiles()

    def supportsImageFiles(self):
        u"Returns True if the site supports image files files." #$NON-NLS-1$
    # end supportsImageFiles()

    def supportsAnyFile(self):
        u"Returns True if the site supports any file type." #$NON-NLS-1$
    # end supportsAnyFile()

# end IZMediaStorageCapabilities


# ----------------------------------------------------------------------------------------------
# A media storage property.
# ----------------------------------------------------------------------------------------------
class IZMediaStorageProperty:

    def getName(self):
        u"Returns the property name." #$NON-NLS-1$
    # end getName()

    def getType(self):
        u"Returns the property's type (text, checkbox, password)." #$NON-NLS-1$
    # end getType()

    def getDisplayName(self):
        u"Returns the media storage property's display name." #$NON-NLS-1$
    # end getDisplayName()

    def getTooltip(self):
        u"Returns the media storage property's tooltip." #$NON-NLS-1$
    # end getTooltip()

    def getValidationRegexp(self):
        u"Returns the media storage property's validation regular expression." #$NON-NLS-1$
    # end getValidationRegexp()

    def getValidationErrorMessage(self):
        u"Returns the media storage property's validation error message." #$NON-NLS-1$
    # end getValidationErrorMessage()

    def getDefaultValue(self):
        u"Returns the media storage property's default value." #$NON-NLS-1$
    # end getDefaultValue()

    def isHidden(self):
        u"Returns the media storage property's hidden flag." #$NON-NLS-1$
    # end isHidden()

    def clone(self):
        u"Called to make a copy of this property." #$NON-NLS-1$
    # end clone()

    def override(self, property):
        u"Called to override the property with data from some other property." #$NON-NLS-1$
    # end override()

# end IZMediaStorageProperty


# ----------------------------------------------------------------------------------------------
# A media storage type is a description of a single type of media storage.  Media store types would
# include FTP, Flickr, etc.  (Basically there will be a single media storage type per supported
# API).  Media Sites will extend the media storage by providing concrete 'templates' for the
# store types.  For example, there might be a Media Site for Ripway.com that extends the FTP
# media storage type (by providing default values for the store type's properties and optionally
# overriding the store type's capabilities).
# ----------------------------------------------------------------------------------------------
class IZMediaStorageType:

    def getId(self):
        u"Returns the store type's id." #$NON-NLS-1$
    # end getId()

    def getClass(self):
        u"Returns the class that implements the IZMediaStorage interface." #$NON-NLS-1$
    # end getClass()

    def getProperties(self):
        u"Returns the list of IZMediaStorageProperty's necessary for proper configuration of a store of this type." #$NON-NLS-1$
    # end getProperties()

    def getCapabilities(self):
        u"Returns the IZMediaStorageCapabilities specified by this store type." #$NON-NLS-1$
    # end getCapabilities()

    def createContributedWizardPages(self):
        u"""createContributedWizardPages() -> class[]
        Creates the wizard pages contributed by the storage type.""" #$NON-NLS-1$
    # end createContributedWizardPages()

    def getIconPath(self):
        u"Returns a file path to the icon associated with this store type." #$NON-NLS-1$
    # end getIconPath()

# end IZMediaStorageType
