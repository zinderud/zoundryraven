
# ------------------------------------------------------------------------------
# View selection types.
# ------------------------------------------------------------------------------
class IZViewSelectionTypes:

    EMPTY_SELECTION = u"zoundry.blogapp.core.view-selection.type.empty" #$NON-NLS-1$
    ACCOUNT_SELECTION = u"zoundry.blogapp.core.view-selection.type.account" #$NON-NLS-1$
    UNPUBLISHED_ACCOUNT_SELECTION = u"zoundry.blogapp.core.view-selection.type.account.unpublished" #$NON-NLS-1$
    BLOG_SELECTION = u"zoundry.blogapp.core.view-selection.type.blog" #$NON-NLS-1$
    BLOG_POSTS_SELECTION = u"zoundry.blogapp.core.view-selection.type.blog-posts" #$NON-NLS-1$
    BLOG_LINKS_SELECTION = u"zoundry.blogapp.core.view-selection.type.blog-links" #$NON-NLS-1$
    BLOG_IMAGES_SELECTION = u"zoundry.blogapp.core.view-selection.type.blog-images" #$NON-NLS-1$
    BLOG_TAGS_SELECTION = u"zoundry.blogapp.core.view-selection.type.blog-tags" #$NON-NLS-1$
    BLOG_EDITED_SELECTION = u"zoundry.blogapp.core.view-selection.type.tag" #pitchaimuthu
    DOCUMENT_SELECTION = u"zoundry.blogapp.core.view-selection.type.document" #$NON-NLS-1$
    IMAGE_SELECTION = u"zoundry.blogapp.core.view-selection.type.image" #$NON-NLS-1$
    LINK_SELECTION = u"zoundry.blogapp.core.view-selection.type.link" #$NON-NLS-1$
    TAG_SELECTION = u"zoundry.blogapp.core.view-selection.type.tag" #$NON-NLS-1$


# end IZViewSelectionTypes


# ------------------------------------------------------------------------------
# View selection interface.
# ------------------------------------------------------------------------------
class IZViewSelection:

    def getType(self):
        u"""getType() -> type
        Returns the selection type.""" #$NON-NLS-1$
    # end getType()

    def getData(self):
        u"""getData() -> data
        Returns the selection data.""" #$NON-NLS-1$
    # end getData()

# end IZViewSelection

