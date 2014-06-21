from zoundry.appframework.engine.service import IZService

# --------------------------------------------------------------------------
# IZLinkProviderService provides listing various quick links
# such as for tagging, bookmarks, search etc.
# --------------------------------------------------------------------------
class IZLinkProviderService(IZService):
    
    def listLinkProviders(self):
        u"""listLinkProviders() -> list of IZLinkProvider
        Returns list of link providers""" #$NON-NLS-1$
    # end listLinkProviders()
    
    def getLinkProviderById(self, providerId):
        u"""getLinkProviderById() -> IZLinkProvider
        Returns provider""" #$NON-NLS-1$
    # end getLinkProviderById()
        
#    def listLinkProvidersByContribLocation(self, location, category = None):
#        u"""listLinkProvidersByContribLocation(string, string) -> IZLinkProvider[]
#        Returns list of link providers that contrib to the given location""" #$NON-NLS-1$
#    # end listLinkProvidersByContribLocation() 
#    
#    def listLinkProvidersByContribCategory(self, catagory, location = None):
#        u"""listLinkProvidersByContribCategory(string, string) -> IZLinkProvider[]
#        Returns list of link providers that contrib to the given category""" #$NON-NLS-1$
#    # end listLinkProvidersByContribCategory()       
    
    def listFormatterTypes(self):
        u"""listFormatterTypes() -> string[]
        Returns list of available formatter types (constants defined in IZLinkFormatType).""" #$NON-NLS-1$
    # end listFormatterTypes()
    
    def listFormattersByType(self, formatterType):
        u"""listFormattersByType(string) - IZLinkFormatter[]
        Returns list of all link formatters. """ #$NON-NLS-1$
    # end listFormattersByType()
    
    def listLinks(self, maxNumLinks):
        u"""listLinks(int) - IZLink[]
        Returns list of links. Providers must support LIST_LINKS capability """ #$NON-NLS-1$
    # end listLinks()
        
# end IZLinkProviderService