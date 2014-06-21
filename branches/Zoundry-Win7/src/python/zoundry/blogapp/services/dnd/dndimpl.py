from zoundry.appframework.services.dnd.dndsource import ZDnDSource
from zoundry.blogapp.services.dnd.dnd import IZBlogAppDnDSource

# ------------------------------------------------------------------------------
# A base class for all concrete blog app DnD source implementations.
# ------------------------------------------------------------------------------
class ZBlogAppDnDSource(ZDnDSource, IZBlogAppDnDSource):

    def __init__(self, type):
        ZDnDSource.__init__(self, type, None)
    # end __init__()

# end ZBlogAppDnDSource


# ------------------------------------------------------------------------------
# An implementation of a Drag & Drop source for CF_HDROP (file) data.
# ------------------------------------------------------------------------------
class ZBlogPostDnDSource(ZBlogAppDnDSource):

    def __init__(self, documentId):
        self.documentId = documentId

        ZBlogAppDnDSource.__init__(self, IZBlogAppDnDSource.TYPE_BLOG_POST)
    # end __init__()

    def getData(self):
        return self.documentId
    # end getData()

# end ZBlogPostDnDSource
