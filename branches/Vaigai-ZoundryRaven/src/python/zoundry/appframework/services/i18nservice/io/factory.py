from zoundry.appframework.messages import _extstr
from zoundry.appframework.constants import IZAppNamespaces
from zoundry.appframework.exceptions import ZAppFrameworkException
from zoundry.appframework.services.i18nservice.io.deserializers import ZCountryCodes200611Deserializer
from zoundry.appframework.services.i18nservice.io.deserializers import ZLanguageCodes200611Deserializer


# -----------------------------------------------------------------------------------------
# A deserializer factory for loading country code and language code files.
# -----------------------------------------------------------------------------------------
class ZI18NDeserializerFactory:

    def __init__(self):
        self.deserializerMap = self._loadDeserializerMap()
    # end __init__()

    def _loadDeserializerMap(self):
        return {
            IZAppNamespaces.RAVEN_COUNTRY_CODES_NAMESPACE_2006_11 : ZCountryCodes200611Deserializer(),
            IZAppNamespaces.RAVEN_LANGUAGE_CODES_NAMESPACE_2006_11 : ZLanguageCodes200611Deserializer()
        }
    # end _loadDeserializerMap()

    def getDeserializer(self, namespace):
        if namespace in self.deserializerMap:
            return self.deserializerMap[namespace]
        else:
            raise ZAppFrameworkException(_extstr(u"factory.NoI18NDeserializerFound") % namespace) #$NON-NLS-1$
    # end getDeserializer()

# end ZI18NDeserializerFactory


DESERIALIZER_FACTORY = ZI18NDeserializerFactory()

def getI18NDeserializerFactory():
    return DESERIALIZER_FACTORY
# end getI18NDeserializerFactory()

