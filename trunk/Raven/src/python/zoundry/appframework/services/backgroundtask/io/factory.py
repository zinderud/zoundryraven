from zoundry.appframework.constants import IZAppNamespaces
from zoundry.appframework.exceptions import ZAppFrameworkException
from zoundry.appframework.messages import _extstr
from zoundry.appframework.services.backgroundtask.io.deserializers import ZVer1BackgroundTaskDeserializer
from zoundry.appframework.services.backgroundtask.io.serializers import ZVer1BackgroundTaskSerializer

# -----------------------------------------------------------------------------------------
# A deserializer factory for creating background task deserializers.  A background task
# deserializer takes a DOM and returns an instance of IZBackgroundTask.
# -----------------------------------------------------------------------------------------
class ZBackgroundTaskDeserializerFactory:

    def __init__(self):
        self.deserializerMap = self._loadDeserializerMap()
    # end __init__()

    def _loadDeserializerMap(self):
        return {
            IZAppNamespaces.RAVEN_TASK_NAMESPACE_2006_05 : ZVer1BackgroundTaskDeserializer()
        }
    # end _loadDeserializerMap()

    def getDeserializer(self, namespace):
        if namespace in self.deserializerMap:
            return self.deserializerMap[namespace]
        else:
            raise ZAppFrameworkException(_extstr(u"factory.NoTaskDeserializerFound") % namespace) #$NON-NLS-1$
    # end getDeserializer()

# end ZBackgroundTaskDeserializerFactory


# -----------------------------------------------------------------------------------------
# A serializer factory for creating background task serializers.  A background task 
# serializer takes an IZBackgroundTask instance and returns the serialized DOM.
# -----------------------------------------------------------------------------------------
class ZBackgroundTaskSerializerFactory:

    def __init__(self):
        self.serializerMap = self._loadSerializerMap()
    # end __init__()

    def _loadSerializerMap(self):
        return {
            IZAppNamespaces.RAVEN_TASK_NAMESPACE_2006_05 : ZVer1BackgroundTaskSerializer()
        }
    # end _loadSerializerMap()

    def getSerializer(self, namespace = IZAppNamespaces.RAVEN_TASK_NAMESPACE_2006_05):
        if namespace in self.serializerMap:
            return self.serializerMap[namespace]
        else:
            raise ZAppFrameworkException(_extstr(u"factory.NoTaskSerializerFound") % namespace) #$NON-NLS-1$
    # end getSerializer()

# end ZBackgroundTaskSerializerFactory


DESERIALIZER_FACTORY = ZBackgroundTaskDeserializerFactory()
SERIALIZER_FACTORY = ZBackgroundTaskSerializerFactory()

def getBackgroundTaskDeserializerFactory():
    return DESERIALIZER_FACTORY
# end getBackgroundTaskDeserializerFactory()

def getBackgroundTaskSerializerFactory():
    return SERIALIZER_FACTORY
# end getBackgroundTaskSerializerFactory()
