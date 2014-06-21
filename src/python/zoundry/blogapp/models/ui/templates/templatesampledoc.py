from zoundry.base.util.schematypes import ZSchemaDateTime
from zoundry.base.xhtml.xhtmlio import loadXhtmlDocumentFromString
from zoundry.blogapp.services.datastore.blogdocumentimpl import ZBlogDocument
from zoundry.blogapp.services.datastore.documentimpl import ZXhtmlContent

# ------------------------------------------------------------------------------
# Sample IZBlogDocument used when showing the preview of a template in the
# template manager.
# ------------------------------------------------------------------------------
class ZTemplatePreviewDocument(ZBlogDocument):

    def __init__(self):
        ZBlogDocument.__init__(self)
        
        self.setId(u"_template_preview_document_") #$NON-NLS-1$
        self.setTitle(u"Proin tincidunt. Sed sapien libero, feugiat eu, tristique.") #$NON-NLS-1$
        self.setCreationTime(ZSchemaDateTime())
        self.setLastModifiedTime(ZSchemaDateTime())
        
        content = ZXhtmlContent()
        content.setMode(u"xml") #$NON-NLS-1$
        content.setType(u"application/xhtml+xml") #$NON-NLS-1$
        content.setXhtmlDocument(self._createXHtmlDocument())
        self.setContent(content)
    # end __init__()

    def _createXHtmlDocument(self):
        xhtml = u"""<p>Lorem ipsum dolor sit amet, consectetuer adipiscing elit. 
            Fusce non mauris non purus ultrices tincidunt. Nunc id neque. Curabitur 
            auctor, risus quis semper tincidunt, magna felis egestas orci, ut 
            elementum elit ipsum eget orci. Vivamus non sapien. Nullam a urna. 
            Sed viverra. Aliquam a neque a eros accumsan dapibus. Pellentesque 
            vitae augue vitae est congue convallis. Maecenas dui felis, dictum 
            bibendum, pharetra in, pulvinar eget, diam. Sed consectetuer cursus 
            sapien. Aenean molestie, justo vitae imperdiet tempor, felis dolor 
            pretium massa, eu adipiscing ante purus vitae risus. Etiam ornare 
            erat. Ut bibendum adipiscing nisl. Cras vitae mauris. Suspendisse 
            diam ipsum, sagittis in, dapibus ut, iaculis at, elit. Donec auctor 
            libero volutpat nisl. Proin ornare turpis et odio.</p>

            <p>In non metus a massa malesuada rutrum. Mauris consequat venenatis 
            dolor. Nullam commodo luctus sapien. Integer quis tortor sit amet 
            tellus scelerisque cursus. Class aptent taciti sociosqu ad litora 
            torquent per conubia nostra, per inceptos hymenaeos. Nam at nunc a 
            mi auctor aliquam. Nulla suscipit varius orci. Vestibulum suscipit 
            magna et nisl. Curabitur sem lectus, ullamcorper et, porttitor non, 
            dignissim in, diam. Fusce aliquet. Aenean elit nulla, vulputate eget, 
            interdum id, rhoncus eget, pede. Ut interdum vehicula leo.</p>
        """ #$NON-NLS-1$
        return loadXhtmlDocumentFromString(xhtml)
    # end _createXHtmlDocument()

# end ZTemplatePreviewDocument
