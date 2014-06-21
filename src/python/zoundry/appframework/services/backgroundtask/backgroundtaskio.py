from zoundry.appframework.exceptions import ZAppFrameworkException
from zoundry.appframework.messages import _extstr
from zoundry.appframework.services.backgroundtask.io.factory import getBackgroundTaskDeserializerFactory
from zoundry.appframework.services.backgroundtask.io.factory import getBackgroundTaskSerializerFactory
from zoundry.base.zdom.dom import ZDom

# ----------------------------------------------------------------------------------------
# This function takes a path to a Raven Background Task and loads it into a 
# IZBackgroundTask instance, using the deserialization framework.
# ----------------------------------------------------------------------------------------
def loadBackgroundTask(taskXmlPath):
    try:
        dom = ZDom()
        dom.load(taskXmlPath)

        deserializer = getBackgroundTaskDeserializerFactory().getDeserializer(dom.documentElement.getNamespaceUri())
        return deserializer.deserialize(dom)
    except Exception, e:
        raise ZAppFrameworkException(_extstr(u"backgroundtaskio.FailedToLoadTask") % taskXmlPath, e) #$NON-NLS-1$
# end loadBackgroundTask()


# ----------------------------------------------------------------------------------------
# This function takes a Background Task instance and serializes it to disk at the given 
# path.
# ----------------------------------------------------------------------------------------
def saveBackgroundTask(task, taskXmlPath):
    try:
        serializer = getBackgroundTaskSerializerFactory().getSerializer()
        dom = serializer.serialize(task)
        dom.save(taskXmlPath, True)
    except Exception, e:
        raise ZAppFrameworkException(_extstr(u"backgroundtaskio.FailedToSaveTask") % task.getId(), e) #$NON-NLS-1$
# end saveBackgroundTask()
