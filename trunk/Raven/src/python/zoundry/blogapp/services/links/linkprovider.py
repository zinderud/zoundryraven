from zoundry.appframework.constants import IZAppServiceIDs
from zoundry.base.exceptions import ZAbstractMethodCalledException

#===================================================
# <capability> constants
#===================================================
class IZLinkProviderCapabilityConstants:
    SEARCH_LINKS = u"zoundry.raven.capability.links.linkprovider.searchlinks" #$NON-NLS-1$
    LIST_FORMATTERS = u"zoundry.raven.capability.links.linkprovider.formatters" #$NON-NLS-1$
    LIST_LINKS = u"zoundry.raven.capability.links.linkprovider.listlinks" #$NON-NLS-1$
# end IZLinkProviderCapabilityConstants

#===================================================
# UI contrib locations
#===================================================
class IZLinkProviderUIContribLocation:
    EDITOR_CONTEXT_MENU = u"zoundry.raven.links.uicontrib.location.contextmenu" #$NON-NLS-1$
    CREATE_LINK_DIALOG = u"zoundry.raven.links.uicontrib.location.linkdialog" #$NON-NLS-1$
# end IZLinkProviderUIContribLocation

#===================================================
# UI contrib category
#===================================================
class IZLinkProviderUIContribCategory:
    # FIXME subcategory? PHOTO, VIDEO
    LOCAL = u"zoundry.raven.links.uicontrib.category.local" #$NON-NLS-1$
    ONLINE = u"zoundry.raven.links.uicontrib.category.online" #$NON-NLS-1$og" #$NON-NLS-1$
    RECENT = u"zoundry.raven.links.uicontrib.category.recent" #$NON-NLS-1$
    POSTS = u"zoundry.raven.links.uicontrib.category.posts" #$NON-NLS-1$
# end IZLinkProviderUIContribCategory

#-----------------------------------------------
# Link provider interface for extension point zoundry.blogapp.links.provider.type
#-----------------------------------------------
class IZLinkProvider:

    def initialize(self, applicationModel, linkProviderDef):
        u"""initialize(ZApplicationModel, ZLinkProviderDef)
        """ #$NON-NLS-1$
    # end initialize()

    def getId(self):
        u"""getId() - string
        """ #$NON-NLS-1$
    # end getId()

    def getName(self):
        u"""getName() - string
        """ #$NON-NLS-1$
    # end getName()

    def getDescription(self):
        u"""getDescription() - string
        """ #$NON-NLS-1$
    # end getDescription()

    def hasCapability(self, capability):
        u"""hasCapability(string) - bool
        """ #$NON-NLS-1$
    # end hasCapability()

    def getContribLocations(self):
        u"""getContribLocations() - string[]
        """ #$NON-NLS-1$
    # end getContribLocations()

    def contributesToLocation(self, location):
        u"""contributesToLocation(string) -> bool
        """ #$NON-NLS-1$
    # end contributesToLocation()

    def getContribCategory(self):
        u"""getContribCategory() - string
        """ #$NON-NLS-1$
    # end getContribCategory()

    def searchLinks(self, query):
        u"""searchLinks(string ) - IZLink[]
        Returns list of links matching query. Provider must support SEARCH_LINKS capability """ #$NON-NLS-1$
    # end searchLinks()

    def listLinks(self, maxNumLinks):
        u"""listLinks(int) - IZLink[]
        Returns list of links. Provider must support LIST_LINKS capability """ #$NON-NLS-1$
    # end listLinks()

    def listFormatters(self):
        u"""listFormatters() - IZLinkFormatter[]
        Returns list of link formatters for given type. Provider must support LIST_FORMATTERS capability """ #$NON-NLS-1$
    # end listFormatters()

    def listFormattersByType(self, formatterType):
        u"""listFormattersByType(string) - IZLinkFormatter[]
        Returns list of all link formatters. Provider must support LIST_FORMATTERS capability """ #$NON-NLS-1$
    # endli listFormattersByType()

    def listFormatterTypes(self):
        u"""listFormatterTypes() -> string[]
        Returns list of available formatter types (constants defined in IZLinkFormatType).""" #$NON-NLS-1$
    # end listFormatterTypes()    

    #fixme (PJ) add createLink(aWindow, aLogger) -> IZLInk ?
    #fixme (PJ) add createUI(aWindow, ...) -> IZPanel
# end IZLinkProvider

#-----------------------------------------------
# Base implementation of a link provider
#-----------------------------------------------
class ZLinkProviderBase(IZLinkProvider):

    def __init__(self):
        self.providerDef = None
        self.applicationModel = None
        self.logger = None
    # end __init__()

    def _getApplicationModel(self):
        return self.applicationModel
    # end _getApplicationModel()

    def _getLogger(self):
        u"""_getLogger() -> IZLoggerService""" #$NON-NLS-1$
        return self.logger
    # end _getLogger()

    def initialize(self, applicationModel, linkProviderDef):
        self.applicationModel = applicationModel
        self.providerDef = linkProviderDef
        self.logger = applicationModel.getEngine().getService(IZAppServiceIDs.LOGGER_SERVICE_ID)
        self.cachedFormatterList = None
        self.cachedFormatterTypes = None
        self._initialize()
    # end initialize()

    def getProviderDef(self):
        u"""getProviderDef() -> ZLinkProviderDef
        Returns link provider type def.""" #$NON-NLS-1$
        return self.providerDef
    # end getProviderDef()

    def getId(self):
        return self.getProviderDef().getId()
    # end getId()

    def getName(self):
        return self.getProviderDef().getName()
    # end getName()

    def getDescription(self):
        return self.getProviderDef().getDescription()
    # end getDescription()

    def hasCapability(self, capability):
        return self.getCapabilities().hasCapability( capability )
    # end hasCapability()

    def getCapabilities(self):
        u"""getCapabilities() - IZCapabilities
        """ #$NON-NLS-1$
        return self.getProviderDef().getCapabilities()
    # end getCapabilities()

    def getContribLocations(self):
        raise ZAbstractMethodCalledException()
        #return self.contribLocations
    # end getContribLocations()

    def contributesToLocation(self, location):
        raise ZAbstractMethodCalledException()
        #location = getSafeString(location)
        #return location in self.getContribLocations()
    # end contributesToLocation()

    def getContribCategory(self):
        raise ZAbstractMethodCalledException()
        #return self.contribCategory
    # end getContribCategory()

    def searchLinks(self, query):
        rval = []
        if self.hasCapability(IZLinkProviderCapabilityConstants.SEARCH_LINKS):
            rval = self._searchLinks(query)
        return rval
    # end searchLinks()

    def listLinks(self, maxNumLinks):
        rval = []
        if self.hasCapability(IZLinkProviderCapabilityConstants.LIST_LINKS):
            rval = self._listLinks(maxNumLinks)
        return rval
    # end listLinks()

    def listFormatters(self):
        if self.cachedFormatterList is None: 
            if self.hasCapability(IZLinkProviderCapabilityConstants.LIST_FORMATTERS):
                self.cachedFormatterList = self._listFormatters()
            else:
                self.cachedFormatterList = []
        return self.cachedFormatterList
    # end listFormatters()

    def listFormattersByType(self, formatterType):
        formatters = self.listFormatters()
        rval = []
        for f in formatters:
            if f.getType() == formatterType:
                rval.append(f)
        return rval
    # end listFormattersByType()
    
    def listFormatterTypes(self):
        if self.cachedFormatterTypes is None:
            self.cachedFormatterTypes = []
            formatters = self.listFormatters()
            for f in formatters:
                if f.getType()  not in self.cachedFormatterTypes:
                    self.cachedFormatterTypes.append( f.getType() )
        return self.cachedFormatterTypes
    # end listFormatterTypes()    
    
    def _initialize(self):
        u"""_initialize() - > void
        A hook for subclasses to initialize data.""" #$NON-NLS-1$
        pass
    # end _initialize()

    def _searchLinks(self, query):
        u"""_searchLinks(string ) - IZLink[]
        Returns list of links matching query. Provider must support SEARCH_LINKS capability """ #$NON-NLS-1$
        raise ZAbstractMethodCalledException(self.__class__, u"_searchLinks") #$NON-NLS-1$
    # end _searchLinks()

    def _listLinks(self, maxNumLinks):
        u"""_listLinks(int) - IZLink[]
        Returns list of links. Provider must support LIST_LINKS capability """ #$NON-NLS-1$
        raise ZAbstractMethodCalledException(self.__class__, u"_listLinks") #$NON-NLS-1$
    # end _listLinks()

    def _listFormatters(self):
        u"""_listFormatters() - IZLinkFormatter[]
        Returns list of link formatters for given type. Provider must support LIST_FORMATTERS capability """ #$NON-NLS-1$
        raise ZAbstractMethodCalledException(self.__class__, u"_listFormatters") #$NON-NLS-1$
    # end _listFormatters()

    #fixme (PJ) add createLink(aWindow, aLogger) -> IZLInk ?
    #fixme (PJ) add createUI(aWindow, ...) -> IZPanel
# end IZLinkProvider
