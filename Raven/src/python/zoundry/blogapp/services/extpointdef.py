from zoundry.appframework.zplugin.extpointdef import ZExtensionPointBaseDef
from zoundry.base.util.types.capabilities import ZCapabilities
from zoundry.base.util.types.parameters import ZParameters


# ---------------------------------------------------------------------------------------
# common base def used by services assuming the following schema:
#
#    <zoundry-extension point="point_id">
#        <id/>
#        <class/>
#        <extension-data>
#            <the-def-node>  <!-- root def element -->
#                <name>optional name</name> ?
#                <icon>path_to_png</icon>?
#                <capabilities /> ?
#                <parameters /> ?
#                <properties /> ?
#            </the-def-node>
#        </extension-data>
#    </zoundry-extension>
#
# ---------------------------------------------------------------------------------------
class IZBlogAppDef:

    def getId(self):
        u"""getId() -> string
        Returns id of extension def.""" #$NON-NLS-1$

    def getName(self):
        u"""getName() -> string or None if not found
        Returns name of extension def.""" #$NON-NLS-1$

    def getCapabilities(self):
        u"""getCapabilities() -> IZCapabilities
        Returns the IZCapabilities.""" #$NON-NLS-1$

    def getParameters(self):
        u"""getParameters() -> IZParameters
        Returns the IZCapabilities.""" #$NON-NLS-1$

# ---------------------------------------------------------------------------------------
class ZBlogAppBaseDef(ZExtensionPointBaseDef, IZBlogAppDef):


    def __init__(self, extensionPoint):
        ZExtensionPointBaseDef.__init__(self, extensionPoint)
        self.capabilities = None
        self.parameters = None
        self.propertyMapList = None
    # end __init__()

    def getName(self):
        u"""getName() -> string or None if not found
        Returns name of extension def.""" #$NON-NLS-1$
        node = self._getExtensionDefNode()
        if node:
            return node.selectSingleNodeText(u"plg:name") #$NON-NLS-1$
        return None
    # end getName()

    def getIcon(self):
        u"""getIcon() -> string or None if not found
        Returns <icon> element entry value or None if not found."""  #$NON-NLS-1$
        node = self._getExtensionDefNode()
        iconPath = None
        if node:
            iconPath = node.selectSingleNodeText(u"plg:icon") #$NON-NLS-1$
        return iconPath

    def getIconPath(self):
        u"""getIconPath() -> string or None if not found
        Returns path to icon in resources folder or None if not found."""  #$NON-NLS-1$
        icon = self.getIcon()
        if icon:
            return self.extensionPoint.getPlugin().getResourceRegistry().getImagePath(icon)
        else:
            return None

    def getIconAsBitmap(self):
        u"""getIconAsBitmap() -> wxBitmap or None if not found.
        Returns icon bitmap or None if not found."""  #$NON-NLS-1$
        iconPath = self.getIcon()
        bitmap = None
        if iconPath:
            bitmap = self.getPlugin().getResourceRegistry().getBitmap(iconPath)
        return bitmap
    # end getIconAsBitmap()

    def getCapabilities(self):
        u"""getCapabilities() -> IZCapabilities
        Returns the IZCapabilities.""" #$NON-NLS-1$
        if self.capabilities is None:
            capabilityMap = {}
            nodes = self._getExtensionDefChildNodes(u"plg:capabilities/plg:capability") #$NON-NLS-1$
            for node in nodes:
                id = node.getAttribute(u"id") #$NON-NLS-1$
                enabled = node.getAttribute(u"enabled") #$NON-NLS-1$
                capabilityMap[id] = enabled == u"True" or enabled == u"true" #$NON-NLS-2$ #$NON-NLS-1$
            self.capabilities = self._createCapabilities(capabilityMap)
        return self.capabilities
    # end getCapabilities()

    def _createCapabilities(self, capabilityMap):
        u"""_createCapabilities(dictionary) -> IZCapabilities
        Creates and returns the IZCapabilities impl. given the capabilities.""" #$NON-NLS-1$
        rval = ZCapabilities(capabilityMap)
        return rval
    # end _createCapabilities()

    def getParameters(self):
        u"""getParameters() -> IZParameters
        Returns the IZParameters.""" #$NON-NLS-1$
        if self.parameters is None:
            paramMap = {}
            nodes = self._getExtensionDefChildNodes(u"plg:parameters/plg:parameter") #$NON-NLS-1$
            for node in nodes:
                name = node.getAttribute(u"name") #$NON-NLS-1$
                if name:
                    paramMap[name] = node.getText()
            self.parameters = ZParameters(paramMap)
        return self.parameters
    # end getCapabilities()

    def getPropertyMapList(self):
        u"""getPropertyMapList() -> list of property dictionary objects
        Returns list of property maps.""" #$NON-NLS-1$
        if self.propertyMapList is None:
            self.propertyMapList = []
            propertyNodes = self._getExtensionDefChildNodes(u"plg:properties/plg:property") #$NON-NLS-1$
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

                self.propertyMapList.append(props)

        return self.propertyMapList
    # end getPropertyMapList()

    def _getTextFromNode(self, parent, xpath):
        return parent.selectSingleNodeText(xpath)

    def _getExtensionDefNodeName(self):
        u"""_getExtensionDefNodeName() -> string
        Return prefixed element name of root element inside <extension-data> => string"""  #$NON-NLS-1$

    def _getExtensionDefNode(self):
        u"""_getExtensionDefNode() -> Node or None if not found.
        Returns the root element inside <extension-data> => Node or None""" #$NON-NLS-1$
        return self._getExtensionNode( self._getExtensionDefNodeName() )

    def _getExtensionDefChildNodes(self, xpath):
        u"""_getExtensionDefChildNodes() -> list of Nodes or None if not found.
        Returns the list of child nodes inside root element of <extension-data> => Node list or None""" #$NON-NLS-1$
        node = self._getExtensionDefNode()
        if node:
            return node.selectNodes(xpath)
        else:
            return None

    def _getExtensionDefChildNode(self, xpath):
        u"""_getExtensionDefChildNode() -> node or None if not found.
        Returns the child nodes inside root element of <extension-data> => Node list or None""" #$NON-NLS-1$
        node = self._getExtensionDefNode()
        if node:
            return node.selectSingleNode(xpath)
        else:
            return None

    def _getExtensionDefChildNodeText(self, xpath):
        u"""_getExtensionDefChildNodeText(string) -> Node text string or None if not found.
        Returns the text of child node inside root element of <extension-data> => string or None""" #$NON-NLS-1$
        node = self._getExtensionDefChildNode(xpath)
        if node:
            return node.getText()
        else:
            return None
    # end _getExtensionDefChildNodeText()

