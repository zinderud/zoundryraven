from zoundry.base.util.text.textutil import getSafeString
from zoundry.appframework.zplugin.extpointdef import ZExtensionPointBaseDef
from zoundry.blogapp.exceptions import ZBlogAppException
from zoundry.base.util.classloader import ZClassLoader

# ----------------------------------------------------------------------------------
# A wrapper around a ZExtensionPoint, this class provides convenient access to the
# specific data of interest for this type of extension point (Media Storage Type).
# ----------------------------------------------------------------------------------
class ZMediaStorageTypeDef(ZExtensionPointBaseDef):

    def __init__(self, extensionPoint):
        ZExtensionPointBaseDef.__init__(self, extensionPoint)
        self.wizardPageClasses = None
    # end __init__()

    def getIcon(self):
        u"""getIcon() -> string or None if not found
        Returns <icon> element entry value or None if not found."""  #$NON-NLS-1$
        iconXPath = self._getIconXPath()
        icon = self._getExtensionText(iconXPath)
        if icon:
            return icon
        else:
            return None

    def getIconPath(self):
        u"""getIconPath() -> string or None if not found
        Returns path from resource registry for <icon> entry path or None if not found."""  #$NON-NLS-1$
        icon = self.getIcon()
        if not icon:
            return None
        return self.extensionPoint.getPlugin().getResourceRegistry().getImagePath(icon)
    # end getIconPath()

    def loadIconAsBitmap(self):
        icon = self.getIcon()
        return self.getPlugin().getResourceRegistry().getBitmap(icon)
    # end loadIconAsBitmap()

    # Returns a list of maps.
    def getProperties(self):
        rval = []
        propNodesXpath = self._getPropertyNodesXPath()
        propertyNodes = self._getExtensionNodes(propNodesXpath)
        for propNode in propertyNodes:
            propName = propNode.getAttribute(u"name") #$NON-NLS-1$
            type = self._getTextFromNode(propNode, u"plg:type") #$NON-NLS-1$
            displayName = self._getTextFromNode(propNode, u"plg:display-name") #$NON-NLS-1$
            tooltip = self._getTextFromNode(propNode, u"plg:tooltip") #$NON-NLS-1$
            valRegexp = self._getTextFromNode(propNode, u"plg:validation-regexp") #$NON-NLS-1$
            valErrorMsg = self._getTextFromNode(propNode, u"plg:validation-error-message") #$NON-NLS-1$
            defaultVal = self._getTextFromNode(propNode, u"plg:default-value") #$NON-NLS-1$

            props = {}
            props[u"name"] = propName #$NON-NLS-1$
            props[u"type"] = type #$NON-NLS-1$
            props[u"display-name"] = displayName #$NON-NLS-1$
            props[u"tooltip"] = tooltip #$NON-NLS-1$
            props[u"validation-regexp"] = valRegexp #$NON-NLS-1$
            props[u"validation-error-message"] = valErrorMsg #$NON-NLS-1$
            props[u"default-value"] = defaultVal #$NON-NLS-1$

            rval.append(props)

        return rval
    # end getProperties()

    def getCapabilities(self):
        rval = {}
        capNodesXPath = self._getCapabilityNodesXPath()
        nodes = self._getExtensionNodes(capNodesXPath)
        for node in nodes:
            id = node.getAttribute(u"id") #$NON-NLS-1$
            enabled = node.getAttribute(u"enabled") #$NON-NLS-1$
            rval[id] = enabled == u"True" or enabled == u"true" #$NON-NLS-2$ #$NON-NLS-1$
        return rval
    # end getCapabilities()

    def createContributedWizardPages(self):
        if self.wizardPageClasses is not None:
            return self.wizardPageClasses

        self.wizardPageClasses = []
        pageNodes = self._getExtensionNodes(self._getWizardPagesXPath())
        classloader = ZClassLoader()
        for pageNode in pageNodes:
            className = pageNode.getAttribute(u"class") #$NON-NLS-1$
            clazz = classloader.loadClass(className)
            self.wizardPageClasses.append(clazz)

        return self.wizardPageClasses
    # end createContributedWizardPages()

    def _getTextFromNode(self, parent, xpath):
        return parent.selectSingleNodeText(xpath)
    # end _getTextFromNode()

    def _getPropertyNodesXPath(self):
        return u"plg:media-storage-type/plg:properties/plg:property" #$NON-NLS-1$
    # end _getPropertyNodesXPath()

    def _getCapabilityNodesXPath(self):
        return u"plg:media-storage-type/plg:capabilities/plg:capability" #$NON-NLS-1$
    # end _getCapabilityNodesXPath()

    def _getWizardPagesXPath(self):
        return u"plg:media-storage-type/plg:wizardPages/plg:page" #$NON-NLS-1$
    # end _getWizardPagesXPath()

    def _getIconXPath(self):
        return u"plg:media-storage-type/plg:icon" #$NON-NLS-1$
    # end _getIconXPath()

# end ZMediaStorageTypeDef


# ----------------------------------------------------------------------------------
# A wrapper around a ZExtensionPoint, this class provides convenient access to the
# specific data of interest for this type of extension point (Media Site).
# ----------------------------------------------------------------------------------
class ZMediaSiteDef(ZMediaStorageTypeDef):

    def __init__(self, extensionPoint):
        ZMediaStorageTypeDef.__init__(self, extensionPoint)
    # end __init__()

    def getMediaStorageTypeId(self):
        mstId = self._getExtensionText(u"plg:media-site/plg:media-storage-type-id") #$NON-NLS-1$
        if not mstId:
            raise ZBlogAppException(u"Missing required meta data: 'media-storage-type-id'") #$NON-NLS-1$
        return mstId
    # end getMediaStorageTypeId()

    def getDisplayName(self):
        displayName = self._getExtensionText(u"plg:media-site/plg:display-name") #$NON-NLS-1$
        if not displayName:
            raise ZBlogAppException(u"Missing required meta data: 'display-name'") #$NON-NLS-1$
        return displayName
    # end getDisplayName()

    def isInternal(self):
        s = getSafeString( self._getExtensionText(u"plg:media-site/plg:internal-store")) #$NON-NLS-1$
        return u"true" == s.lower(); #$NON-NLS-1$
    # end isInternal()

    def _getPropertyNodesXPath(self):
        return u"plg:media-site/plg:properties/plg:property" #$NON-NLS-1$
    # end _getPropertyNodesXPath()

    def _getCapabilityNodesXPath(self):
        return u"plg:media-site/plg:capabilities/plg:capability" #$NON-NLS-1$
    # end _getCapabilityNodesXPath()

    def _getIconXPath(self):
        return u"plg:media-site/plg:icon" #$NON-NLS-1$
    # end _getIconXPath()

# end ZMediaSiteDef
