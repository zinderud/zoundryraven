from zoundry.blogapp.exceptions import ZBlogAppException
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.services.template.io.deserializers import ZBlogTemplateDeserializer
from zoundry.blogapp.services.template.io.serializers import ZBlogTemplateSerializer

LEGACY_RAVEN_BLOG_TEMPLATE_NAMESPACE = u"http://www.zoundry.com/schemas/2007/06/ztemplate.rng" #$NON-NLS-1$
RAVEN_BLOG_TEMPLATE_NAMESPACE = u"http://www.zoundry.com/schemas/2007/11/ztemplate.rng" #$NON-NLS-1$

# -----------------------------------------------------------------------------------------
# A deserializer factory for creating template deserializers.  An template deserializer
# takes an template directory and an template DOM and deserializes that into a ZTemplate
# instance.
# -----------------------------------------------------------------------------------------
class ZTemplateDeserializerFactory:

    def __init__(self):
        self.deserializerMap = self._loadDeserializerMap()
    # end __init__()

    def _loadDeserializerMap(self):
        return {
            RAVEN_BLOG_TEMPLATE_NAMESPACE : ZBlogTemplateDeserializer(RAVEN_BLOG_TEMPLATE_NAMESPACE)
        }
    # end _loadDeserializerMap()

    def getDeserializer(self, namespace):
        if namespace in self.deserializerMap:
            return self.deserializerMap[namespace]
        else:
            raise ZBlogAppException(_extstr(u"factory.TemplateDeserializerNotFound") % namespace) #$NON-NLS-1$
    # end getDeserializer()

# end ZTemplateDeserializerFactory


# -----------------------------------------------------------------------------------------
# A serializer factory for creating template serializers.  An template serializer takes an
# template instance and an template directory, and serializes/saves the template to that
# directory.
# -----------------------------------------------------------------------------------------
class ZTemplateSerializerFactory:

    def __init__(self):
        self.serializerMap = self._loadSerializerMap()
    # end __init__()

    def _loadSerializerMap(self):
        return {
            RAVEN_BLOG_TEMPLATE_NAMESPACE : ZBlogTemplateSerializer(RAVEN_BLOG_TEMPLATE_NAMESPACE)
        }
    # end _loadSerializerMap()

    def getSerializer(self, namespace = RAVEN_BLOG_TEMPLATE_NAMESPACE):
        if namespace in self.serializerMap:
            return self.serializerMap[namespace]
        else:
            raise ZBlogAppException(_extstr(u"factory.TemplateSerializerNotFound") % namespace) #$NON-NLS-1$
    # end getSerializer()

# end ZTemplateSerializerFactory


DESERIALIZER_FACTORY = ZTemplateDeserializerFactory()
SERIALIZER_FACTORY = ZTemplateSerializerFactory()

def getTemplateDeserializerFactory():
    return DESERIALIZER_FACTORY
# end getTemplateDeserializerFactory()

def getTemplateSerializerFactory():
    return SERIALIZER_FACTORY
# end getTemplateSerializerFactory()
