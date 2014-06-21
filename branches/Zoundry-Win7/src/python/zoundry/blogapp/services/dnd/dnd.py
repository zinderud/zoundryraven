from zoundry.appframework.services.dnd.dndsource import IZDnDSource

# ------------------------------------------------------------------------------
# Interface for a Drag & Drop source from Zoundry Raven (blog app).
# ------------------------------------------------------------------------------
class IZBlogAppDnDSource(IZDnDSource):

    TYPE_BLOG_POST = u"zoundry.blogapp.dnd.source.blog-post" #$NON-NLS-1$

# end IZBlogAppDnDSource
