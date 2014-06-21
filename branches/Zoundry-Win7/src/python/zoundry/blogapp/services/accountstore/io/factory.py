from zoundry.blogapp.exceptions import ZBlogAppException
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.services.accountstore.io.deserializers import ZBlogAccountDeserializer
from zoundry.blogapp.services.accountstore.io.serializers import ZBlogAccountSerializer

RAVEN_BLOG_ACCOUNT_NAMESPACE = u"http://www.zoundry.com/schemas/2006/05/zaccount.rng" #$NON-NLS-1$

# -----------------------------------------------------------------------------------------
# A deserializer factory for creating account deserializers.  An account deserializer
# takes an account directory and an account DOM and deserializes that into a ZAccount
# instance.
# -----------------------------------------------------------------------------------------
class ZAccountDeserializerFactory:

    def __init__(self):
        self.deserializerMap = self._loadDeserializerMap()
    # end __init__()

    def _loadDeserializerMap(self):
        return {
            RAVEN_BLOG_ACCOUNT_NAMESPACE : ZBlogAccountDeserializer(RAVEN_BLOG_ACCOUNT_NAMESPACE)
        }
    # end _loadDeserializerMap()

    def getDeserializer(self, namespace):
        if namespace in self.deserializerMap:
            return self.deserializerMap[namespace]
        else:
            raise ZBlogAppException(_extstr(u"factory.NoAccountDeserializer") % namespace) #$NON-NLS-1$
    # end getDeserializer()

# end ZAccountDeserializerFactory


# -----------------------------------------------------------------------------------------
# A serializer factory for creating account serializers.  An account serializer takes an
# account instance and an account directory, and serializes/saves the account to that
# directory.
# -----------------------------------------------------------------------------------------
class ZAccountSerializerFactory:

    def __init__(self):
        self.serializerMap = self._loadSerializerMap()
    # end __init__()

    def _loadSerializerMap(self):
        return {
            RAVEN_BLOG_ACCOUNT_NAMESPACE : ZBlogAccountSerializer(RAVEN_BLOG_ACCOUNT_NAMESPACE)
        }
    # end _loadSerializerMap()

    def getSerializer(self, namespace = RAVEN_BLOG_ACCOUNT_NAMESPACE):
        if namespace in self.serializerMap:
            return self.serializerMap[namespace]
        else:
            raise ZBlogAppException(_extstr(u"factory.NoSerializerForAccountError") % namespace) #$NON-NLS-1$
    # end getSerializer()

# end ZAccountSerializerFactory


DESERIALIZER_FACTORY = ZAccountDeserializerFactory()
SERIALIZER_FACTORY = ZAccountSerializerFactory()

def getAccountDeserializerFactory():
    return DESERIALIZER_FACTORY
# end getAccountDeserializerFactory()

def getAccountSerializerFactory():
    return SERIALIZER_FACTORY
# end getAccountSerializerFactory()
