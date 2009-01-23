from zoundry.blogapp.exceptions import ZBlogAppException
from zoundry.blogapp.services.mediastorage.io.deserializers import ZVer1MediaStorageDeserializer
from zoundry.blogapp.services.mediastorage.io.serializers import ZVer1MediaStorageSerializer

RAVEN_MEDIASTORE_NAMESPACE_VER1 = u"http://www.zoundry.com/schemas/2006/07/zmediastorage.rng" #$NON-NLS-1$

# -----------------------------------------------------------------------------------------
# A deserializer factory for creating media storage deserializers.  A media storage deserializer
# takes a media storage DOM and deserializes that into a ZMediaStorage instance.
# -----------------------------------------------------------------------------------------
class ZMediaStorageDeserializer:

    def __init__(self):
        self.deserializerMap = self._loadDeserializerMap()
    # end __init__()

    def _loadDeserializerMap(self):
        return {
            RAVEN_MEDIASTORE_NAMESPACE_VER1 : ZVer1MediaStorageDeserializer(RAVEN_MEDIASTORE_NAMESPACE_VER1)
        }
    # end _loadDeserializerMap()

    def getDeserializer(self, namespace):
        if namespace in self.deserializerMap:
            return self.deserializerMap[namespace]
        else:
            raise ZBlogAppException(u"No deserializer found for '%s'." % namespace) #$NON-NLS-1$
    # end getDeserializer()

# end ZMediaStorageDeserializer


# -----------------------------------------------------------------------------------------
# A serializer factory for creating media storage serializers.  A media storage serializer
# takes a ZMediaStorage and serializes that into a DOM.
# -----------------------------------------------------------------------------------------
class ZMediaStorageSerializerFactory:

    def __init__(self):
        self.serializerMap = self._loadSerializerMap()
    # end __init__()

    def _loadSerializerMap(self):
        return {
            RAVEN_MEDIASTORE_NAMESPACE_VER1: ZVer1MediaStorageSerializer(RAVEN_MEDIASTORE_NAMESPACE_VER1)
        }
    # end _loadSerializerMap()

    def getSerializer(self, namespace = RAVEN_MEDIASTORE_NAMESPACE_VER1):
        if namespace in self.serializerMap:
            return self.serializerMap[namespace]
        else:
            raise ZBlogAppException(u"No serializer found for '%s'." % namespace) #$NON-NLS-1$
    # end getSerializer()

# end ZMediaStorageSerializerFactory


DESERIALIZER_FACTORY = ZMediaStorageDeserializer()
SERIALIZER_FACTORY = ZMediaStorageSerializerFactory()


def getMediaStorageDeserializerFactory():
    return DESERIALIZER_FACTORY
# end getMediaStorageDeserializerFactory()
def getMediaStorageSerializerFactory():
    return SERIALIZER_FACTORY
# end getMediaStorageSerializerFactory()
