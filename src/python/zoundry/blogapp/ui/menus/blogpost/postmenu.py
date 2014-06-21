from zoundry.appframework.ui.actions.menuaction import ZMenuActionContext


# ------------------------------------------------------------------------------
# An implementation of a menu action context for menu items in the blog post
# context menu (the menu that is displayed when a blog post is right-clicked).
# ------------------------------------------------------------------------------
class ZBlogPostActionContext(ZMenuActionContext):

    def __init__(self, window, documentIDO, blogId = None):
        self.documentIDO = documentIDO
        self.blogId = blogId
        ZMenuActionContext.__init__(self, window)
    # end __init__()

    def getDocumentIDO(self):
        return self.documentIDO
    # end getDocumentIDO()

    def getBlogId(self):
        return self.blogId
    # end getBlogId()

# end ZBlogPostActionContext
