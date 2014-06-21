from zoundry.base.util.schematypes import ZSchemaDateTime
from zoundry.blogapp.services.commonimpl import ZModelWithAttributes
from zoundry.blogapp.services.datastore.document import IZDocument
from zoundry.blogapp.services.datastore.document import IZDocumentContent
from zoundry.blogapp.services.datastore.document import IZXHTMLContent


# -----------------------------------------------------------------------------------------
# Base class for the document's content.
# -----------------------------------------------------------------------------------------
class ZDocumentContent(IZDocumentContent):

    def __init__(self):
        self.mode = None
        self.type = None
    # end __init__()

    def getMode(self):
        return self.mode
    # end getMode()

    def setMode(self, mode):
        self.mode = mode
    # end setMode()

    def getType(self):
        return self.type
    # end getType()

    def setType(self, type):
        self.type = type
    # end setType()

# end ZDocumentContent


# -----------------------------------------------------------------------------------------
# The document's content.  The document content is a wrapper object around a ZXhtmlDocument
# instance.  This class contains a single instance of a ZXhtmlDocument that represents the
# actual content of the document.
# -----------------------------------------------------------------------------------------
class ZXhtmlContent(ZDocumentContent, IZXHTMLContent):

    def __init__(self):
        ZDocumentContent.__init__(self)

        self.xhtmlDocument = None
    # end __init__()

    def getXhtmlDocument(self):
        return self.xhtmlDocument
    # end getXhtmlDocument()

    def setXhtmlDocument(self, xhtmlDocument):
        self.xhtmlDocument = xhtmlDocument
    # end setXhtmlDocument()

    def toDocument(self):
        if self.getXhtmlDocument():
            return self.getXhtmlDocument().getDom()
        else:
            raise Exception(u"xhtmlDocument is None") #$NON-NLS-1$
    # end toDocument()

# end ZDocumentContent


# -----------------------------------------------------------------------------------------
# The Zoundry Raven document impl.  Base class for all implementations of documents.
# -----------------------------------------------------------------------------------------
class ZDocument(ZModelWithAttributes, IZDocument):

    def __init__(self):
        ZModelWithAttributes.__init__(self)

        self.id = None
        self.content = None
    # end __init__()

    def getId(self):
        return self.id
    # end getId()

    def setId(self, id):
        self.id = id
    # end setId()

    def getCreationTime(self):
        ct = self.getAttribute(u"creation-time") #$NON-NLS-1$
        if ct:
            ct = ZSchemaDateTime(ct)
        return ct
    # end getCreationTime()

    def setCreationTime(self, creationTime):
        self.setAttribute(u"creation-time", unicode(creationTime)) #$NON-NLS-1$
    # end setCreationTime()

    def getLastModifiedTime(self):
        lmt = self.getAttribute(u"modified-time") #$NON-NLS-1$
        if lmt:
            lmt = ZSchemaDateTime(lmt)
        return lmt
    # end getLastModifiedTime()

    def setLastModifiedTime(self, lastModifiedTime):
        self.setAttribute(u"modified-time", unicode(lastModifiedTime)) #$NON-NLS-1$
    # end setLastModifiedTime()

    def getContent(self):
        return self.content
    # end getContent()

    def setContent(self, content):
        self.content = content
    # end setContent()

# end ZDocument
