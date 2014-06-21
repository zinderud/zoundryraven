from zoundry.appframework.models.appmodel import IZApplicationModel

# ------------------------------------------------------------------------------------
# The Blog Application model interface.
# ------------------------------------------------------------------------------------
class IZBlogApplicationModel(IZApplicationModel):
    
    def getViewRegistry(self):
        u"""getViewRegistry() -> IZViewRegistry
        Returns the global View Registry.""" #$NON-NLS-1$
    # end getViewRegistry()
    
# end IZBlogApplicationModel
