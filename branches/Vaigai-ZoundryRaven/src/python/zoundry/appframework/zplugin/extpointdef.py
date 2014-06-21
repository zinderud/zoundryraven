from zoundry.appframework.constants import IZAppNamespaces
import os


# -------------------------------------------------------------------------------------
# This is a base class for wrapping a ZExtensionPoint of any type.  It is primarily
# useful for providing methods to extract data from the <extension-data> child.
# -------------------------------------------------------------------------------------
class ZExtensionPointBaseDef:

    def __init__(self, extensionPoint):
        self.extensionPoint = extensionPoint
        self.extensionClass = None
        nsMap = self._getNamespaceMap()
        if nsMap:
            nsMap[u"plg"] = IZAppNamespaces.RAVEN_PLUGIN_NAMESPACE #$NON-NLS-1$
            self.extensionPoint.epNode.ownerDocument.setNamespaceMap(nsMap)
    # end __init__()

    def getId(self):
        return self.extensionPoint.getId()
    # end getId()

    def getClass(self):
        if self.extensionPoint.getClass() is None:
            return None
        if not self.extensionClass:
            self.extensionClass = self.extensionPoint.loadClass()
        return self.extensionClass
    # end getClass()
    
    def getPlugin(self):
        return self.extensionPoint.getPlugin()
    # end getPlugin()

    def _getExtensionNode(self, xpath):
        node = self.extensionPoint.getExtensionDataNode()
        if node:
            return node.selectSingleNode(xpath)
        return None
    # end _getExtensionNode()

    def _getExtensionNodes(self, xpath):
        node = self.extensionPoint.getExtensionDataNode()
        if node:
            return node.selectNodes(xpath)
        return None
    # end _getExtensionNode()

    def _getExtensionText(self, xpath):
        node = self.extensionPoint.getExtensionDataNode()
        if node:
            return node.selectSingleNodeText(xpath)
        return None
    # end _getExtensionNode()

    def _getNamespaceMap(self):
        return {}
    # end _getNamespaceMap()

# end ZExtensionPointBaseDef()


# -------------------------------------------------------------------------------------
# An interface for the extension def (a def that provides meta information about a 
# contributed extension point, or rather an extension point definition).
# -------------------------------------------------------------------------------------
class IZExtensionDef:

    def getExtensionId(self):
        u"Gets the ID of the contributed extension." #$NON-NLS-1$
    # end getName()

    def getSchemaLocation(self):
        u"Gets the location of the schema." #$NON-NLS-1$
    # end getSchemaLocation()
    
    def getInterface(self):
        u"Returns the interface that must be implemented by contributors to this extension point." #$NON-NLS-1$
    # end getInterface()

# end IZExtensionDef


# -------------------------------------------------------------------------------------
# This class wraps a ZExtensionPoint of the type 'zoundry.extension'.  It provides
# a getter to the (optional) extension info for the extension.
# -------------------------------------------------------------------------------------
class ZExtensionDef(ZExtensionPointBaseDef, IZExtensionDef):

    def __init__(self, extensionPoint, pluginDirectory):
        ZExtensionPointBaseDef.__init__(self, extensionPoint)
        self.pluginDirectory = pluginDirectory
    # end __init__()

    def getExtensionId(self):
        return self._getExtensionText(u"plg:extension-info/plg:id") #$NON-NLS-1$
    # end getName()

    def getSchemaLocation(self):
        schemaLoc = self._getExtensionText(u"plg:extension-info/plg:schema-location") #$NON-NLS-1$
        if not schemaLoc:
            return None
        return os.path.join(self.pluginDirectory, schemaLoc)
    # end getSchemaLocation()

    def getInterface(self):
        iface = self._getExtensionText(u"plg:extension-info/plg:interface") #$NON-NLS-1$
        if not iface:
            return None
        return self.getPlugin().getClassloader().loadClass(iface)
    # end getInterface()

    def isInterfaceOptional(self):
        ifaceNode = self._getExtensionNode(u"plg:extension-info/plg:interface") #$NON-NLS-1$
        if not ifaceNode:
            return None
        return ifaceNode.getAttribute(u"optional") == u"true" #$NON-NLS-2$ #$NON-NLS-1$
    # end isInterfaceOptional()

# end ZExtensionDef
