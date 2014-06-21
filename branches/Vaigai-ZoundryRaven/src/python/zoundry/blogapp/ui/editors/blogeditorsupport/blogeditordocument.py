from zoundry.base.util.schematypes import ZSchemaDateTime
from zoundry.blogapp.services.datastore.blogdocumentimpl import ZBlogDocument
from zoundry.blogapp.services.datastore.documentimpl import ZXhtmlContent

# ------------------------------------------------------------------------------
# Sample IZBlogDocument used when showing the preview of a template in the
# blog post editor's preview tab.
# ------------------------------------------------------------------------------
class ZBlogPostEditorPreviewDocument(ZBlogDocument):

    def __init__(self, title, xhtmlDoc):
        self.title = title
        self.xhtmlDoc = xhtmlDoc

        ZBlogDocument.__init__(self)

        self.setId(u"_blog_post_editor_preview_document_") #$NON-NLS-1$
        self.setTitle(self.title)
        self.setCreationTime(ZSchemaDateTime())
        self.setLastModifiedTime(ZSchemaDateTime())

        content = ZXhtmlContent()
        content.setMode(u"xml") #$NON-NLS-1$
        content.setType(u"application/xhtml+xml") #$NON-NLS-1$
        content.setXhtmlDocument(self.xhtmlDoc)
        self.setContent(content)
    # end __init__()

# end ZBlogPostEditorPreviewDocument
