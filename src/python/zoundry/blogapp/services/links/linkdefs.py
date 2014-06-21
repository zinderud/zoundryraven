from zoundry.base.util.text.textutil import getNoneString
from zoundry.blogapp.services.extpointdef import ZBlogAppBaseDef

# ---------------------------------------------------------------------------------------
# Definition representing the Link Provider Type plug-in config.
# Example:
#    <zoundry-extension point="zoundry.blogapp.links.provider.type">
#        <id>zoundry.blogapp.links.provider.type.simplelinkprovider</id>
#        <class>zoundry.blogapp.services.links.providers.simplelinkprovider.ZSimpleLinkProvider</class>
#        <extension-data>
#            <link-provider-type>
#                <name>Simple Quick Links</name>
#                <description>Provides quick links and formatters configured via plug-in xml.</description>
#                <locations>
#                    <location>zoundry.raven.links.uicontrib.location.contextmenu</location>
#                </locations>
#                <category>zoundry.raven.links.uicontrib.category.local</category>
#                <capabilities>
#                    <capability enabled="true" id="zoundry.raven.capability.links.linkprovider.listlinks"/>
#                    <capability enabled="true" id="zoundry.raven.capability.links.linkprovider.formatters"/>
#                </capabilities>
#            </link-provider-type>
#        </extension-data>
#    </zoundry-extension>
# ---------------------------------------------------------------------------------------
class ZLinkProviderDef(ZBlogAppBaseDef):

    def __init__(self, extensionPoint):
        # See base class for getName(), getIcon(), getCapabilities() etc.
        ZBlogAppBaseDef.__init__(self, extensionPoint)
    # end __init__()

    def getClassName(self):
        u"Returns the publisher impl. class name." #$NON-NLS-1$
        return self.extensionPoint.getClass()
    # end getClassName()

    def _getExtensionDefNodeName(self):
        return u"plg:link-provider-type"  #$NON-NLS-1$
    # end _getExtensionDefNodeName()

    def getDescription(self):
        u"""getDescription() -> string or None if not found.
        Returns the  provider description.""" #$NON-NLS-1$
        return self._getExtensionDefChildNodeText(u"plg:description") #$NON-NLS-1$
    # end getDescription()
# end ZLinkProviderDef

#-----------------------------------------------------------------
# Link definition
# Example:
#    <link>
#      <name>Zoundry</name>
#      <url>http://www.zoundry.com</url>
#      <rel/>
#      <icon>icons/zoundry.gif</icon>#      
#    </link>
#-----------------------------------------------------------------
class ZLinkDef:

    def __init__(self, linkElement, resourceRegistry): #@UnusedVariable
        self.element = linkElement
        self.resourceRegistry = resourceRegistry
    # end __init__()

    def getElement(self):
        return self.element
    # end getElement()
    
    def _getResourceRegistry(self):
        return self.resourceRegistry
    # end _getResourceRegistry()

    def _getText(self, xpath):
        if self.getElement():
            node = self.getElement().selectSingleNode(xpath)
            if node:
                return getNoneString(node.getText())
        return None
    # end _getText

    def getName(self):
        u"""getName() -> string
        Returns link name""" #$NON-NLS-1$
        return self._getText(u"plg:name") #$NON-NLS-1$
    # end getName()

    def getUrl(self):
        u"""getUrl() -> string
        Returns link url""" #$NON-NLS-1$
        return self._getText(u"plg:url") #$NON-NLS-1$
    # end getUrl()

    def getRel(self):
        u"""getRel() -> string
        Returns link rel attribute or None if not specified""" #$NON-NLS-1$
        return self._getText(u"plg:rel") #$NON-NLS-1$
    # end getRel()

    def getIcon(self):
        u"""getIcon() -> string
        Returns link icon text or None if not specified""" #$NON-NLS-1$
        return self._getText(u"plg:icon") #$NON-NLS-1$
    # end getIconPath()

    def getIconPath(self):
        u"""getIconPath() -> string or None if not found
        Returns path to icon in resources folder or None if not found."""  #$NON-NLS-1$
        icon = self.getIcon()
        if icon:
            return self._getResourceRegistry().getImagePath(icon)
        else:
            return None
    # end getIconPath()

    def getIconAsBitmap(self):
        u"""getIconAsBitmap() -> wxBitmap or None if not found.
        Returns icon bitmap or None if not found."""  #$NON-NLS-1$
        iconPath = self.getIcon()
        bitmap = None
        if iconPath:
            bitmap = self._getResourceRegistry().getBitmap(iconPath)
        return bitmap
    # end getIconAsBitmap()
# end ZLinkDef

#-----------------------------------------------------------------
# Link Formatter definition
# Exaample:
#    <link-formatter>
#      <name>Technorati</name>
#      <url>http://www.technorati.com</url>
#      <rel/>
#      <icon>icons/simplelinkprovider/technorati.gif</icon>
#      <type>tag</type>
#      <enc>+</enc>
#      <format>http://www.technorati.com/tag/{0}</format>
#    </link-formatter>
#-----------------------------------------------------------------
class ZLinkFormatterDef(ZLinkDef):

    def __init__(self, linkFormatterElement, resourceRegistry): #@UnusedVariable
        ZLinkDef.__init__(self, linkFormatterElement, resourceRegistry)
        pass
    # end __init__()

    def getType(self):
        u"""getType() -> string
        Returns link formatter type""" #$NON-NLS-1$
        return self._getText(u"plg:type") #$NON-NLS-1$
    # end getType()

    def getEncoding(self):
        u"""getEncoding() -> string
        Returns link formatter encoding""" #$NON-NLS-1$
        return self._getText(u"plg:enc") #$NON-NLS-1$
    # end getEncoding()

    def getFormat(self):
        u"""getFormat() -> string
        Returns link formatter format""" #$NON-NLS-1$
        return self._getText(u"plg:format") #$NON-NLS-1$
    # end getFormat()
# end ZLinkFormatterDef
