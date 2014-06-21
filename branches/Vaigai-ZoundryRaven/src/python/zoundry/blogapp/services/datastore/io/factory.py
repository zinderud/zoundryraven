from zoundry.blogapp.exceptions import ZBlogAppException
from zoundry.blogapp.services.datastore.io.constants import IZDocumentSerializationConstants
from zoundry.blogapp.services.datastore.io.deserializers import ZBlogDocumentDeserializer
from zoundry.blogapp.services.datastore.io.serializers import ZBlogDocumentSerializer


# -----------------------------------------------------------------------------------------
# Serialization context impl.
# -----------------------------------------------------------------------------------------
class ZBlogDocumentSerializationContext:
    
    def __init__(self, dataDir):
        self.dataDir = dataDir
    # end __init__()
    
    def getDataDir(self):
        return self.dataDir
    # end getDataDir()

# ZBlogDocumentSerializationContext


# -----------------------------------------------------------------------------------------
# A deserializer factory for creating document deserializers.  A document deserializer
# takes a document DOM and deserializes that into a IZDocument instance.
# -----------------------------------------------------------------------------------------
class ZDocumentDeserializerFactory:

    def __init__(self):
        self.deserializerMap = self._loadDeserializerMap()
    # end __init__()

    def _loadDeserializerMap(self):
        return {
            IZDocumentSerializationConstants.RAVEN_BLOG_DOCUMENT_NAMESPACE : ZBlogDocumentDeserializer(IZDocumentSerializationConstants.RAVEN_BLOG_DOCUMENT_NAMESPACE)
        }
    # end _loadDeserializerMap()

    def getDeserializer(self, namespace):
        if namespace in self.deserializerMap:
            return self.deserializerMap[namespace]
        else:
            raise ZBlogAppException(u"No deserializer found for '%s'." % namespace) #$NON-NLS-1$
    # end getDeserializer()

# end ZDocumentDeserializerFactory


# -----------------------------------------------------------------------------------------
# A serializer factory for creating document serializers.  A document serializer
# takes a ZDocument and serializes that into a DOM.
# -----------------------------------------------------------------------------------------
class ZDocumentSerializerFactory:

    def __init__(self):
        self.serializerMap = self._loadSerializerMap()
    # end __init__()

    def _loadSerializerMap(self):
        return {
            IZDocumentSerializationConstants.RAVEN_BLOG_DOCUMENT_NAMESPACE : ZBlogDocumentSerializer(IZDocumentSerializationConstants.RAVEN_BLOG_DOCUMENT_NAMESPACE)
        }
    # end _loadSerializerMap()

    def getSerializer(self, namespace = IZDocumentSerializationConstants.RAVEN_BLOG_DOCUMENT_NAMESPACE):
        if namespace in self.serializerMap:
            return self.serializerMap[namespace]
        else:
            raise ZBlogAppException(u"No serializer found for '%s'." % namespace) #$NON-NLS-1$
    # end getSerializer()

# end ZDocumentSerializerFactory


DESERIALIZER_FACTORY = ZDocumentDeserializerFactory()
SERIALIZER_FACTORY = ZDocumentSerializerFactory()


def getDocumentDeserializerFactory():
    return DESERIALIZER_FACTORY
# end getDocumentDeserializerFactory()
def getDocumentSerializerFactory():
    return SERIALIZER_FACTORY
# end getDocumentSerializerFactory()
