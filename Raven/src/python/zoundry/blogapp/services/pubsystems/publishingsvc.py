from zoundry.blogapp.services.datastore.blogdocumentimpl import ZWeblogPingSite
from zoundry.blogapp.services.pubsystems.pubdefs import ZWeblogPingSiteDef
from zoundry.appframework.constants import IZAppServiceIDs
from zoundry.appframework.engine.service import IZService
from zoundry.base.util.text.textutil import getNoneString
from zoundry.blogapp.constants import IZBlogAppExtensionPoints
from zoundry.blogapp.exceptions import ZBlogAppException
from zoundry.blogapp.services.pubsystems.pubdefs import ZPublisherSiteDef
from zoundry.blogapp.services.pubsystems.pubdefs import ZPublisherTypeDef
from zoundry.blogapp.services.pubsystems.autodiscovery import ZBlogDiscovery

# --------------------------------------------------------------------------
# Publishing service related exceptions
# --------------------------------------------------------------------------
class ZPublishingServiceException(ZBlogAppException):

    def __init__(self, message, rootCause = None):
        ZBlogAppException.__init__(self, message, rootCause)

# --------------------------------------------------------------------------
#
# --------------------------------------------------------------------------
class IZPublishingService(IZService):

    def listPublisherTypes(self):
        u"""listPublisherTypes() -> list of ZPublisherTypeDef
        Returns list of ZPublisherTypeDef objects.""" #$NON-NLS-1$
    # end listPublisherTypes()

    def getPublisherType(self, typeId):
        u"""getPublisherType(string) -> ZPublisherTypeDef
        Returns ZPublisherTypeDef given id.""" #$NON-NLS-1$
    # end getPublisherType()

    def listPublisherSites(self):
        u"""listPublisherSites() -> list of ZPublisherSiteDef
        Returns list of ZPublisherSiteDef objects.""" #$NON-NLS-1$
    # end listPublisherSites()

    def getPublisherSite(self, siteId):
        u"""getPublisherSite(string) -> ZPublisherSiteDef
        Returns ZPublisherSiteDef given id.""" #$NON-NLS-1$
    # end getPublisherSite()

    def createPublisherByPublisherId(self, publisherId):
        u"Returns IZPublisher given  publisher id string." #$NON-NLS-1$
    # end createPublisherByPublisherId()

    def createPublisherBySiteId(self, siteId):
        u"Returns IZPublisher given site id string." #$NON-NLS-1$
    # end createPublisherBySiteId()

    def createPublisher(self, siteOrTypeId, izcapabilities, izparameters):
        u"""createPublisher(string, izcapabilities, izparameters) -> IZPublisher
        Returns IZPublisher given site or a typeid string and optional (override) capabilities and parameters.
        This method first tries to create a publisher assuming a site id else reverts to a type id.
        """ #$NON-NLS-1$
    # end createPublisher()

    def autodiscover(self, url):
        u"""autodiscover(string) -> ZDiscoveryInfo
        Attempts to auto discover endpoint settings. """ #$NON-NLS-1$
    # end autodiscover()

    def listWeblogPingSites(self):
        u"""listWeblogPingSites() -> list of IZWeblogPingSite
        Returns list of weblog ping sites. """ #$NON-NLS-1$
    # end listWeblogPingSites()

    def findWeblogPingSiteById(self, pingSiteId):
        u"""findWeblogPingSiteById(id) -> IZWeblogPingSite
        Returns the ping site instance with the given ID or
        None if not found.""" #$NON-NLS-1$
    # end findWeblogPingSiteById()

# end class IZPublishingService

# --------------------------------------------------------------------------
# IZPublishingService implementation
# --------------------------------------------------------------------------
class ZPublishingService(IZPublishingService):

    def __init__(self):
        self.logger = None
        self.applicationModel = None
        self.pubTypeDefs = []
        self.pubSiteDefs = []
        self.weblogPingSiteDefs = []
    # end __init__()

    def _clearDefs(self):
        self.pubTypeDefs = []
        self.pubSiteDefs = []
        self.weblogPingSiteDefs = []
    # end _clearDefs()

    def start(self, applicationModel):
        self.applicationModel = applicationModel
        self.logger = applicationModel.getEngine().getService(IZAppServiceIDs.LOGGER_SERVICE_ID)
        self.logger.debug(u"Starting Publishing Service") #$NON-NLS-1$
        self._clearDefs()
        self.pubTypeDefs = self._loadPubTypeDefs()
        self.pubSiteDefs = self._loadPubSiteDefs()
        self.weblogPingSiteDefs = self._loadWeblogPingSiteDefs()
        self.weblogPingSites = self._loadWeblogPingSites()
        self.logger.debug(u"Publishing Service started.") #$NON-NLS-1$

        # FIXME (PJ) validate mediaStoreType exists: zoundry.blogapp.mediastorage.type.blog
        # FIXME (PJ) validate mediaSite exists: zoundry.blogapp.mediastorage.site.blog.metaweblog

    def stop(self):
        self.logger.debug(u"PublishingService stopped.") #$NON-NLS-1$
        self._clearDefs()
    # end stop()

    def listPublisherTypes(self):
        return self.pubTypeDefs

    def getPublisherType(self, typeId):
        rval = None
        if typeId is not None:
            for typedef in self.listPublisherTypes():
                if typedef.getId() == typeId:
                    rval = typedef
                    break
        return rval

    def listPublisherSites(self):
        return self.pubSiteDefs

    def getPublisherSite(self, siteId):
        rval = None
        if siteId is not None:
            for sitedef in self.listPublisherSites():
                if sitedef.getId() == siteId:
                    rval = sitedef
                    break
        return rval

    def createPublisherByPublisherId(self, publisherId):
        typedef = self.getPublisherType(publisherId)
        if not typedef:
            raise ZPublishingServiceException(u"Publisher-type not found for id:%s" % publisherId) #$NON-NLS-1$
        pubClazz = typedef.getClass()
        pubInstance = pubClazz()
        pubInstance.setTypeDef(typedef)
        return pubInstance

    def createPublisherBySiteId(self, siteId):
        sitedef = self.getPublisherSite(siteId)
        if not sitedef:
            raise ZPublishingServiceException(u"Publisher-site not found for id:%s" % siteId) #$NON-NLS-1$
        publisherId = sitedef.getPublisherTypeId()
        publisher = self.createPublisherByPublisherId(publisherId)
        # override params and capabilities
        publisher.initialize( sitedef.getCapabilities(), sitedef.getParameters(), self.logger )
        return publisher

    def createPublisher(self, siteOrTypeId, izcapabilities, izparameters):
        # If the site exists for a given id, then create publisher based on the site def,
        # else revert to the type def.
        publisher = None
        sitedef = self.getPublisherSite(siteOrTypeId)
        if sitedef:
            publisher = self.createPublisherBySiteId(siteOrTypeId)
        else:
            publisher = self.createPublisherByPublisherId(siteOrTypeId)
        publisher.initialize(izcapabilities, izparameters, self.logger)
        return publisher

    def listWeblogPingSites(self):
        u"""listWeblogPingSites() -> list of IZWeblogPingSite
        Returns list of weblog ping sites. """ #$NON-NLS-1$
        return self.weblogPingSites
    # end listWeblogPingSites()
    
    def _loadWeblogPingSites(self):
        # Create IZWeblogPingSite from defs
        rval = []
        for siteDef in  self.weblogPingSiteDefs:
            site = ZWeblogPingSite()
            site.setAttribute(u"id", siteDef.getId()) #$NON-NLS-1$
            site.setAttribute(u"name", siteDef.getName()) #$NON-NLS-1$
            site.setAttribute(u"url", siteDef.getUrl()) #$NON-NLS-1$
            rval.append(site)
        # sort list.
        rval.sort( lambda x, y: cmp( x.getName().lower(), y.getName().lower() ) )
        return rval
    # end _loadWeblogPingSites()

    def findWeblogPingSiteById(self, pingSiteId):
        for site in self.listWeblogPingSites():
            if site.getAttribute(u"id") == pingSiteId: #$NON-NLS-1$
                return site
        return None
    # end findWeblogPingSiteById()

    def _loadPubTypeDefs(self):
        pluginRegistry = self.applicationModel.getPluginRegistry()
        extensions = pluginRegistry.getExtensions(IZBlogAppExtensionPoints.ZEP_ZOUNDRY_PUBLISHER_TYPE)
        pubTypeDefs = map(ZPublisherTypeDef, extensions)
        rval = []
        idList = []
        for typedef in pubTypeDefs:
            typeId = typedef.getId()
            if getNoneString(typeId) is None:
                self.logger.error(u"Publisher TypeDef id is None.") #$NON-NLS-1$
                continue
            if typeId in idList:
                self.logger.warning(u"Ignoring - duplicate publisher type id %s" % typeId) #$NON-NLS-1$
                continue
            if getNoneString(typedef.getClassName()) is None:
                self.logger.warning(u"Ignoring - empty classname for publisher type id %s" % typeId) #$NON-NLS-1$
                continue

            idList.append(typeId)
            rval.append(typedef)
        return rval

    def _loadPubSiteDefs(self):
        pluginRegistry = self.applicationModel.getPluginRegistry()
        extensions = pluginRegistry.getExtensions(IZBlogAppExtensionPoints.ZEP_ZOUNDRY_PUBLISHER_SITE)
        pubSiteDefs = map(ZPublisherSiteDef, extensions)
        rval = []
        idList = []
        for sitedef in pubSiteDefs:
            siteId = sitedef.getId()
            pubId = sitedef.getPublisherTypeId()
            if getNoneString(siteId) is None:
                self.logger.error(u"Publisher SiteDef id is None.") #$NON-NLS-1$
                continue
            if siteId in idList:
                self.logger.warning(u"Ignoring - duplicate publisher site id %s" % siteId) #$NON-NLS-1$
                continue
            publisherDef = self.getPublisherType(pubId)
            if publisherDef is None:
                self.logger.warning(u"Ignoring - publisher type (%s) not found for site (%s)" % (pubId, siteId)) #$NON-NLS-1$
                continue
            sitedef.setPublisherTypeDef(publisherDef)
            idList.append(siteId)
            rval.append(sitedef)

        return rval

    def _loadWeblogPingSiteDefs(self):
        pluginRegistry = self.applicationModel.getPluginRegistry()
        extensions = pluginRegistry.getExtensions(IZBlogAppExtensionPoints.ZEP_ZOUNDRY_WEBLOGPING_SITE)
        pingSiteDefs = map(ZWeblogPingSiteDef, extensions)
        rval = []
        idList = []
        for sitedef in pingSiteDefs:
            siteId = sitedef.getId()
            if getNoneString(siteId) is None:
                self.logger.error(u"Weblog ping SiteDef id is None.") #$NON-NLS-1$
                continue
            if siteId in idList:
                self.logger.warning(u"Ignoring - duplicate weblog ping site id %s" % siteId) #$NON-NLS-1$
                continue
            url = getNoneString (sitedef.getUrl() )
            if not url:
                self.logger.error(u"Weblog ping SiteDef name is None for %s" % siteId ) #$NON-NLS-1$
                continue
            idList.append(siteId)
            rval.append(sitedef)
        return rval


    def autodiscover(self, url):
        discoveryInfo = None
        blogDiscovery = ZBlogDiscovery()
        if blogDiscovery.discover(url):
            discoveryInfo = blogDiscovery.getApiInfo()
        return discoveryInfo
