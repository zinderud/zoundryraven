from zoundry.blogapp.services.common import IZAttributeModel


# -----------------------------------------------------------------------------------------
# The interface for the document's content.
# -----------------------------------------------------------------------------------------
class IZDocumentContent:

    def getMode(self):
        u"Gets the mode (xml, escaped, etc)." #$NON-NLS-1$
    # end getMode()

    def setMode(self, mode):
        u"Sets the mode." #$NON-NLS-1$
    # end setMode()

    def getType(self):
        u"Gets the content type." #$NON-NLS-1$
    # end getType()

    def setType(self, type):
        u"Sets the content type." #$NON-NLS-1$
    # end setType()

# end IZDocumentContent


# -----------------------------------------------------------------------------------------
# The interface for the document's content when the content type of xhtml.
# -----------------------------------------------------------------------------------------
class IZXHTMLContent(IZDocumentContent):

    def getXhtmlDocument(self):
        u"Gets the content as a ZXhtmlDocument." #$NON-NLS-1$
    # end getXhtmlDocument()

    def setXhtmlDocument(self, xhtmlDocument):
        u"Sets the content." #$NON-NLS-1$
    # end setXhtmlDocument()

    def toDocument(self):
        u"Converts the Document Content to a DOM and returns it." #$NON-NLS-1$
    # end toDocument()

# end IZDocumentContent


# -----------------------------------------------------------------------------------------
# The Zoundry Raven document interface.  All implementations of documents (basically
# blog entries) must implement this interface.
# -----------------------------------------------------------------------------------------
class IZDocument(IZAttributeModel):

    def getId(self):
        u"Gets the document id." #$NON-NLS-1$
    # end getId()

    def setId(self, id):
        u"Sets the document id." #$NON-NLS-1$
    # end setId()

    def getCreationTime(self):
        u"Gets the document's creation-time." #$NON-NLS-1$
    # end getCreationTime()

    def setCreationTime(self, creationTime):
        u"Sets the document's creation-time." #$NON-NLS-1$
    # end setCreationTime()

    def getLastModifiedTime(self):
        u"Gets the document's last-modified-time." #$NON-NLS-1$
    # end getLastModifiedTime()

    def setLastModifiedTime(self, lastModifiedTime):
        u"Sets the document's last-modified-time." #$NON-NLS-1$
    # end setLastModifiedTime()

    def getContent(self):
        u"Gets the content of this document.  Returns a ZDocumentContent object." #$NON-NLS-1$
    # end getContent()

    def setContent(self, content):
        u"Sets the content of this document." #$NON-NLS-1$
    # end setContent()

# end IZDocument
