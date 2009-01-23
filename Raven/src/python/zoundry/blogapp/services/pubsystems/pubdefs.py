from zoundry.blogpub.blogserverapi import IZBlogApiCapabilityConstants
from zoundry.base.util.types.capabilities import ZCapabilities
from zoundry.blogapp.services.extpointdef import ZBlogAppBaseDef


# ---------------------------------------------------------------------------------------
# Publisher specific impl of capabilities.
# ---------------------------------------------------------------------------------------

class ZPublisherCapabilities(ZCapabilities):

    def __init__(self, capabilityMap):
        ZCapabilities.__init__(self, capabilityMap)

    def clone(self):
        return ZPublisherCapabilities(self.capabilityMap.copy())    
    # end clone()
    
    def supportsUploadMedia(self):
        return self.hasCapability(IZBlogApiCapabilityConstants.MEDIA_UPLOAD) 
    
    def supportsCategories(self):
        return self.hasCapability(IZBlogApiCapabilityConstants.CATEGORIES) 
    
    def supportsMultipleCategories(self):
        return self.hasCapability(IZBlogApiCapabilityConstants.MULTISELECT_CATEGORIES)
    
    def supportsUserGeneratedCategories(self):
        return self.hasCapability(IZBlogApiCapabilityConstants.USERGENERATED_CATEGORIES)
    

# ---------------------------------------------------------------------------------------
# base def for all publishing system defs
# ---------------------------------------------------------------------------------------
class ZPublishingBaseDef(ZBlogAppBaseDef):

    def __init__(self, extensionPoint):
        ZBlogAppBaseDef.__init__(self, extensionPoint)
    # end __init__()


    def _createCapabilities(self, capabilityMap):
        u"""_createCapabilities(dictionary) -> IZCapabilities
        Creates and returns the ZPublisherCapabilities impl. given the capabilities.""" #$NON-NLS-1$
        rval = ZPublisherCapabilities(capabilityMap)
        return rval
    # end _createCapabilities()

# ---------------------------------------------------------------------------------------
# ZPublisherTypeDef:
# Encapsulates a publisher definition with default capabilites and configuration.
# A publisher is composed of the publisher implementation and the server-side api
# delegate. For example, a Publisher for WordPress would use the Raven's xml-rpc publisher
# impl. with xml-rpc metaweblog impl for the server-side api.
#
#    <zoundry-extension point="zoundry.blogapp.pubsystems.publisher.type">
#        <id>zoundry.blogapp.pubsystems.publisher.type.xmlrpc.movabletype</id>
#        <class>zoundry.blogapp.pubsystems.publishers.xmlrpc.ZXmlRpcMovableTypePublisher</class>
#        <extension-data>
#            <publisher-type>
#                <name>MovableType</name>
#                <icon>path/to/icon.png</icon>
#                <capabilities>
#                    <capability enabled="true" id="zoundry.blogapp.pubsystems.publisher.sample-cap"/>
#                </capabilities>
#                <parameters>
#                    <parameter name="astring">a string val</parameter>
#                </parameters>
#            <publisher-type>
#        </extension-data>
#    </zoundry-extension>
#
# ---------------------------------------------------------------------------------------

class ZPublisherTypeDef(ZPublishingBaseDef):

    def __init__(self, extensionPoint):
        ZPublishingBaseDef.__init__(self, extensionPoint)

    def getClassName(self):
        u"Returns the publisher impl. class name." #$NON-NLS-1$
        return self.extensionPoint.getClass()
    # end getClassName()

    def _getExtensionDefNodeName(self):
        return u"plg:publisher-type"  #$NON-NLS-1$

# ---------------------------------------------------------------------------------------
# ZPublisherSiteDef:
# Encapsulates references to a publisher def and contains meta data such as blog server
# name,  icon, auto-discovery as well as any overrides on capabilites and ext-properties.
#
# There is one ZPublisherSiteDef for each server that needs to be supported. For example,
# TypePad (which uses xml-rpc pub), WordPress, Drupal, TextPatten, Windows Live, Blogger etc.
#
#    <zoundry-extension point="zoundry.blogapp.pubsystems.publisher.site">
#        <id>zoundry.blogapp.pubsystems.publishers.site.drupal</id>
#        <class/>
#        <extension-data>
#            <publisher-site>
#                <publisher-type-id>zoundry.blogapp.pubsystems.publisher.type.xmlrpc.metaweblog</publisher-type-id>
#                <name>Drupal 4.6</name>
#                <icon>path/to/icon.png</icon>
#                <capabilities>
#                </capabilities>
#                <parameters>         
#                    <parameter name="siteparam">site param value 2</parameter>
#                </parameters>
#                <properties>
#                </properties>
#            </publisher-site>
#        </extension-data>
#    </zoundry-extension>  
#
#   Capabilities: { draft, categories,media, extendedentry, can_edit_endpoint, can_add_cats, single_sel_cats}
#   Parameters:   {authscheme, rm_newline_pub, download_template, in_timeformat_str, out_timeformat_str, endpoint_str, endpoint_uri}
#   Auto-discovery: ?
#   Media sites: ?
#
# ---------------------------------------------------------------------------------------

class ZPublisherSiteDef(ZPublishingBaseDef):

    def __init__(self, extensionPoint):
        ZPublishingBaseDef.__init__(self, extensionPoint)
        self.publisherDef = None

    def _getExtensionDefNodeName(self):
        return u"plg:publisher-site"  #$NON-NLS-1$

    def getPublisherTypeId(self):
        u"""getPublisherTypeId() -> string or None if not found.
        Returns the publisher id.""" #$NON-NLS-1$
        return self._getExtensionDefChildNodeText(u"plg:publisher-type-id") #$NON-NLS-1$
    # end getPublisherId()
    
    def setPublisherTypeDef(self, publisherTypeDef):
        u"""setPublisherTypeDef(ZPublisherTypeDef) -> void.
        Sets the parent PublisherTypeDef.""" #$NON-NLS-1$        
        self.publisherTypeDef = publisherTypeDef
        if self.publisherTypeDef:
            # reset capabilites and params such that
            # it uses teh values from the typedef while allowing the site def to override.
            c = self.publisherTypeDef.getCapabilities().clone()
            c.override(self.getCapabilities())
            self.capabilities = c            
            p = self.publisherTypeDef.getParameters().clone()
            p.override(self.getParameters())
            self.parameters = p
    
    def getPublisherTypeDef(self):
        u"""getPublisherTypeDef() -> ZPublisherTypeDef or None if not set
        Returns associated PublisherTypeDef.""" #$NON-NLS-1$        
        return self.publisherTypeDef
        
    def getIconPath(self):
        u"""getIconPath() -> string or None if not found
        Returns path to icon in resources folder. 
        If the site does not define an icon, then the icon path of the parent typedef is returned. """  #$NON-NLS-1$
        iconPath = ZPublishingBaseDef.getIconPath(self)
        if not iconPath and self.getPublisherTypeDef():
            iconPath = self.getPublisherTypeDef().getIconPath()
        return iconPath
    
    def getIconAsBitmap(self):
        u"""getPublisherTypeDef() -> wxBitmap or None if not found
        Returns associated icon. If the site does not define an icon, then the parent typedef's icon is returned.""" #$NON-NLS-1$
        
        bitmap = ZPublishingBaseDef.getIconAsBitmap(self)
        if not bitmap and self.getPublisherTypeDef():
            # if bitmap is not defined, then look in parent def.
            bitmap = self.getPublisherTypeDef().getIconAsBitmap()
        return bitmap
                

    #TODO: (PJ) add getter for icon name and location
    #TODO: (PJ) add getter for autodiscovery
    #TODO: (PJ) add getter for default media site config
    
# --------------------------------------------------    
# Weblog ping site def
# --------------------------------------------------
class ZWeblogPingSiteDef(ZPublishingBaseDef):
    
    EXTENDED_PING_API_CAPABILITY = u"zoundry.blogapp.pubsystems.publisher.weblogping.extended.ping" #$NON-NLS-1$

    def __init__(self, extensionPoint):
        ZPublishingBaseDef.__init__(self, extensionPoint)

    def _getExtensionDefNodeName(self):
        return u"plg:weblog-ping-site"  #$NON-NLS-1$

    def getUrl(self):
        u"""getUrl() -> string or None if not found.
        Returns the site ping url.""" #$NON-NLS-1$
        return self._getExtensionDefChildNodeText(u"plg:url") #$NON-NLS-1$
    # end getUrl()
    
