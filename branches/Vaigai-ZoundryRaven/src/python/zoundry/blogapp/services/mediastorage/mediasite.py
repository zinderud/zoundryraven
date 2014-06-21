
# -------------------------------------------------------------------------------------
# Interface that describes a media site.
# -------------------------------------------------------------------------------------
class IZMediaSite:

    def getId(self):
        u"Returns the media site's mediaSiteId." #$NON-NLS-1$
    # end getId()

    def getDisplayName(self):
        u"Returns the display name of the media site." #$NON-NLS-1$
    # end getDisplayName()

    def getIconPath(self):
        u"Returns the path to the icon associated with this media site." #$NON-NLS-1$
    # end getIconPath()

    def getProperties(self):
        u"Returns all of the media site's properties (these will be type-specific, e.g. 'passive' property for FTP sites)." #$NON-NLS-1$
    # end getProperties()

    def getCapabilities(self):
        u"Returns all of the media site's IZMediaStorageCapabilities." #$NON-NLS-1$
    # end getCapabilities()

    def createContributedWizardPages(self):
        u"""createContributedWizardPages() -> class[]
        Creates the wizard pages contributed by the site.""" #$NON-NLS-1$
    # end createContributedWizardPages()

    def getMediaStorageTypeId(self):
        u"Returns the id of the media storage that this site extends." #$NON-NLS-1$
    # end getMediaStorageTypeId()

    def isInternal(self):
        u"Returns true if the site is for internal use." #$NON-NLS-1$
    # end getMediaStorageTypeId()


# end IZMediaSite
