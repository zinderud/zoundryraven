import os
import wx

IMAGE_TYPE_MAP = {
    u"png" : wx.BITMAP_TYPE_PNG, #$NON-NLS-1$
    u"gif" : wx.BITMAP_TYPE_GIF, #$NON-NLS-1$
    u"jpg" : wx.BITMAP_TYPE_JPEG, #$NON-NLS-1$
    u"jpeg" : wx.BITMAP_TYPE_JPEG, #$NON-NLS-1$
    u"bmp" : wx.BITMAP_TYPE_BMP, #$NON-NLS-1$
    u"ico" : wx.BITMAP_TYPE_ICO #$NON-NLS-1$
}

# Gets the image type of a given image from its path.
def getImageType(path):
    l = path.split(u".") #$NON-NLS-1$
    l.reverse()
    ext = l[0].lower()
    return IMAGE_TYPE_MAP[ext]
# end getImageType()

# -------------------------------------------------------------------------------
# An interface that all resource registries must implement.  Note that there is
# one main resource registry, but other objects may want to implement the
# resource registry interface (such as the plugin object).
# -------------------------------------------------------------------------------
class IZResourceRegistry:

    def getResourcePath(self, path, dirOk = False):
        u"Resolves and returns the resource path (returns None if the path does not exist)." #$NON-NLS-1$
    # end getResourcePath()

    def getImage(self, path):
        u"Returns the wx.Image at the given path." #$NON-NLS-1$
    # end getImage()

    def getIconBundle(self, pathList):
        u"Returns a wx.IconBundle from the list of paths." #$NON-NLS-1$
    # end getIconBundle()

    def getIcon(self, path):
        u"Gets the icon found at the given path." #$NON-NLS-1$
    # end getIcon()

    def getBitmap(self, path):
        u"Gets the bitmap found at the given path." #$NON-NLS-1$
    # end getBitmap()

    def getImagePath(self, path):
        u"Resolves and returns the image path (returns None if the path does not exist)." #$NON-NLS-1$
    # end getImagePath()

# end IZResourceRegistry


# -------------------------------------------------------------------------------
# The resource registry provides a consistent view of all resources found in
# the application (images, html files, etc...).  All access to application
# resources should go through the resource registry.
# -------------------------------------------------------------------------------
class ZResourceRegistry(IZResourceRegistry):

    def __init__(self, resourceDirectory):
        self.resourceDirectory = resourceDirectory
    # end __init__()

    def getResourcePath(self, path, dirOk = False):
        resPath = os.path.join(self.resourceDirectory, path) 
        if os.path.exists(resPath) and (dirOk or os.path.isfile(resPath)):
            return resPath
        return None
    # end getResourcePath()

    def getImage(self, path):
        # if path is already resolved, then no need resolve.
        if os.path.isfile(path):
            pathToImage = path
        else:
            pathToImage = self.getImagePath(path)
        if pathToImage is not None:
            return wx.Image(pathToImage, getImageType(path))
        return None
    # end getImage()

    # FIXME (EPW) impl a version of getIconBundle that takes a single multi-part .ico file
    def getIconBundle(self, pathList):
        bundle = wx.IconBundle()
        for path in pathList:
            icon = self.getIcon(path)
            bundle.AddIcon(icon)
        return bundle
    # end getIconBundle()

    def getIcon(self, path):
        if path.endswith(u".ico"): #$NON-NLS-1$
            pathToImage = self.getImagePath(path)
            if pathToImage is not None:
                return wx.Icon(pathToImage, wx.BITMAP_TYPE_ICO)
        else:
            bmp = self.getBitmap(path)
            if bmp is not None:
                icon = wx.EmptyIcon()
                icon.CopyFromBitmap(bmp)
                return icon
        return None
    # end getIcon()

    def getBitmap(self, path):
        tempImg = self.getImage(path)
        if tempImg is not None:
            return tempImg.ConvertToBitmap()
        return None
    # end getImage()

    # Note: this is just an alias to getResourcePath()
    def getImagePath(self, path):
        return self.getResourcePath(path)
    # end getImagePath()

# end ZResourceRegistry


# -------------------------------------------------------------------------------
# The aggregate resource registry implementation.  This takes a list of resource
# registries and combines them so that they appear to be a single registry.  The
# registries will be searched in order for the requested resource.
# -------------------------------------------------------------------------------
class ZAggregateResourceRegistry(ZResourceRegistry):

    def __init__(self, registryList):
        self.registryList = registryList

        # Init the base class with no path - then we need to override getResourcePath() to
        # avoid the NPE.
        ZResourceRegistry.__init__(self, None)
    # end __init__()

    # Overrides the base method in order to look for the resource path in all of the
    # available registries.
    def getResourcePath(self, path, dirOk = False):
        for registry in self.registryList:
            resPath = registry.getResourcePath(path, dirOk)
            if resPath is not None:
                return resPath
        return None
    # end getResourcePath()

# end ZAggregateResourceRegistry


# -------------------------------------------------------------------------------
# The resource registry provides a consistent view of all resources found in
# the system profile.
# -------------------------------------------------------------------------------
class ZSystemResourceRegistry(ZResourceRegistry):

    def __init__(self, systemProfile):
        self.systemProfile = systemProfile

        ZResourceRegistry.__init__(self, self.systemProfile.getResourceDirectory())
    # end __init__()

# end ZSystemResourceRegistry

