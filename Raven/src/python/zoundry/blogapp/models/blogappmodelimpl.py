from zoundry.appframework.models.appmodelimpl import ZApplicationModel
from zoundry.blogapp.models.blogappmodel import IZBlogApplicationModel
from zoundry.blogapp.version import ZVersion
from zoundry.blogapp.ui.views.viewreg import ZViewRegistry

# ------------------------------------------------------------------------------------
# An implementation of the Blog App model.  This model extends the basic app
# framework's App Model and adds the additional stuff introduced by the above
# IZBlogApplicationModel interface.
# ------------------------------------------------------------------------------------
class ZBlogApplicationModel(ZApplicationModel, IZBlogApplicationModel):

    def __init__(self):
        ZApplicationModel.__init__(self)

        self.version = ZVersion()
        self.viewRegistry = ZViewRegistry()
    # end __init__()

    def getVersion(self):
        return self.version
    # end getVersion()

    def getViewRegistry(self):
        return self.viewRegistry
    # end getViewRegistry()

# end ZBlogApplicationModel
