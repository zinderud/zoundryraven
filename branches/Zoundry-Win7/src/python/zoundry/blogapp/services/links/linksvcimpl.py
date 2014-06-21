from zoundry.blogapp.services.links.linkprovider import IZLinkProviderCapabilityConstants
from zoundry.appframework.constants import IZAppServiceIDs
from zoundry.base.util.text.textutil import getNoneString
from zoundry.blogapp.constants import IZBlogAppExtensionPoints
from zoundry.blogapp.services.links.linkdefs import ZLinkProviderDef
from zoundry.blogapp.services.links.linksvc import IZLinkProviderService


# --------------------------------------------------------------------------
# IZLinkProviderService provides listing various quick links
# such as for tagging, bookmarks, search etc.
# --------------------------------------------------------------------------
class ZLinkProviderService(IZLinkProviderService):

    def __init__(self):
        self.providers = []
    # end __init__()

    def start(self, applicationModel):
        self.logger = applicationModel.getEngine().getService(IZAppServiceIDs.LOGGER_SERVICE_ID)
        self.applicationModel = applicationModel
        self.cachedFormatterList = None
        self.cachedFormatterTypes = None
        self.cachedFormatterByType = {}
        self.cachedAllSimpleLinks = None
        self.logger.debug(u"Starting Link Provider Service") #$NON-NLS-1$
        self._loadProviders()
        self.logger.debug(u"Link Provider Service started.") #$NON-NLS-1$
    # end start

    def listLinkProviders(self):
        return self.providers
    # end listLinkProviders()

    def getLinkProviderById(self, providerId):
        rval = None
        for provider in self.listLinkProviders():
            if provider.getId() == providerId:
                rval = provider
                break
        return rval
    # end getLinkProviderById()

    def listFormatterTypes(self):
        if self.cachedFormatterTypes is None:
            self.cachedFormatterTypes = []
            for linkProvider in self.listLinkProviders():
                for formatType in linkProvider.listFormatterTypes():
                    if formatType not in self.cachedFormatterTypes:
                        self.cachedFormatterTypes.append(formatType)
        return self.cachedFormatterTypes
    # end listFormatterTypes()

    def listFormattersByType(self, formatterType):
        formatters = None
        if self.cachedFormatterByType.has_key(formatterType):
            formatters = self.cachedFormatterByType[formatterType]
        else:
            formatters = []
            self.cachedFormatterByType[formatterType] = formatters
            for linkProvider in self.listLinkProviders():
                formatters.extend( linkProvider.listFormattersByType(formatterType) )
        return formatters
    # end listFormattersByType()
    
    def listLinks(self, maxNumLinks):
        if self.cachedAllSimpleLinks is None:
            self.cachedAllSimpleLinks = []
            for pvd in self.listLinkProviders():
                if pvd.hasCapability(IZLinkProviderCapabilityConstants.LIST_LINKS):
                    self.cachedAllSimpleLinks.extend( pvd.listLinks(50) )         
        n = maxNumLinks
        if n > len(self.cachedAllSimpleLinks):
            n = len(self.cachedAllSimpleLinks)
        return self.cachedAllSimpleLinks[0:n]
    # end listLinks()    

    def _loadProviders(self):
        self.providers = []
        typeDefs = self._loadProviderTypeDefs()
        for typedef in typeDefs:
            providerClazz = typedef.getClass()
            providerInstance = providerClazz()
            providerInstance.initialize(self.applicationModel, typedef)
            self.providers.append( providerInstance )
    # end _loadProviders()

    def _loadProviderTypeDefs(self):
        pluginRegistry = self.applicationModel.getPluginRegistry()
        extensions = pluginRegistry.getExtensions(IZBlogAppExtensionPoints.ZEP_ZOUNDRY_LINK_PROVIDER_TYPE)
        typeDefs = map(ZLinkProviderDef, extensions)
        rval = []
        idList = []
        for typedef in typeDefs:
            typeId = typedef.getId()
            if getNoneString(typeId) is None:
                self.logger.error(u"Link provider typedef id is None.") #$NON-NLS-1$
                continue
            if typeId in idList:
                self.logger.warning(u"Ignoring - duplicate link provider type id %s" % typeId) #$NON-NLS-1$
                continue
            if getNoneString(typedef.getClassName()) is None:
                self.logger.warning(u"Ignoring - empty classname for link provider type id %s" % typeId) #$NON-NLS-1$
                continue
            idList.append(typeId)
            rval.append(typedef)
        return rval
    # end _loadProviderTypeDefs()

# end ZLinkProviderService