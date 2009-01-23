from zoundry.base.zdom.dom import ZDom
from zoundry.blogapp.exceptions import ZBlogAppException
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.services.datastore.io.factory import ZBlogDocumentSerializationContext
from zoundry.blogapp.services.datastore.io.factory import getDocumentDeserializerFactory
from zoundry.blogapp.services.datastore.io.factory import getDocumentSerializerFactory
import os

# ----------------------------------------------------------------------------------------
# This function takes a path to a Raven Document and loads it into a ZDocument
# instance, using the deserialization framework.
# ----------------------------------------------------------------------------------------
def loadDocument(documentXmlPath):
    try:
        dom = ZDom()
        dom.load(documentXmlPath)

        dataDir = os.path.dirname(documentXmlPath)
        context = ZBlogDocumentSerializationContext(dataDir)
        deserializer = getDocumentDeserializerFactory().getDeserializer(dom.documentElement.getNamespaceUri())
        return deserializer.deserialize(dom, context)
    except Exception, e:
        raise ZBlogAppException(_extstr(u"dataio.DocumentLoadFailedError") % documentXmlPath, e) #$NON-NLS-1$
# end loadDocument()


# ----------------------------------------------------------------------------------------
# This function takes a IZDocument instance and serializes it to disk at the given path.
# ----------------------------------------------------------------------------------------
def saveDocument(document, documentXmlPath):
    try:
        dataDir = os.path.dirname(documentXmlPath)
        context = ZBlogDocumentSerializationContext(dataDir)
        serializer = getDocumentSerializerFactory().getSerializer()
        dom = serializer.serialize(document, context)
        dom.save(documentXmlPath, True)
    except Exception, e:
        raise ZBlogAppException(_extstr(u"dataio.FailedToSaveDocument") % documentXmlPath, e) #$NON-NLS-1$
# end saveDocument()
