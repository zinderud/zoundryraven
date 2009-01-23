from zoundry.appframework.constants import IZAppNamespaces
from zoundry.base.util.classloader import ZClassLoader
from zoundry.base.util.schematypes import ZSchemaDateTime
import string

# -----------------------------------------------------------------------------------------
# The interface that all background task deserializer implementations must implement.
# -----------------------------------------------------------------------------------------
class IZBackgroundTaskDeserializer:

    def deserialize(self, backgroundTaskDom):
        u"Called to deserialize a background task." #$NON-NLS-1$
    # end deserialize()

# end IZBackgroundTaskDeserializer


# -----------------------------------------------------------------------------------------
# An implementation of a background task deserializer for version 1.0 (or 2006/06) of the
# Zoundry Raven background task format.
# -----------------------------------------------------------------------------------------
class ZVer1BackgroundTaskDeserializer(IZBackgroundTaskDeserializer):

    def __init__(self):
        self.nssMap = { u"zns" : IZAppNamespaces.RAVEN_TASK_NAMESPACE_2006_05 } #$NON-NLS-1$
    # end __init__()

    def deserialize(self, backgroundTaskDom):
        backgroundTaskDom.setNamespaceMap(self.nssMap)
        backgroundTaskElem = backgroundTaskDom.documentElement

        backgroundTask = self._createTask(backgroundTaskDom.documentElement)
        backgroundTask.setId(backgroundTaskElem.getAttribute(u"task-id")) #$NON-NLS-1$

        self._deserializeStandardAttributes(backgroundTask, backgroundTaskElem)
        self._deserializeError(backgroundTask, backgroundTaskElem)
        self._deserializeCustomAttributes(backgroundTask, backgroundTaskElem)

        return backgroundTask
    # end deserialize()

    def _createTask(self, backgroundTaskElem):
        taskClassname = backgroundTaskElem.getAttribute(u"class") #$NON-NLS-1$
        taskClass = ZClassLoader().loadClass(taskClassname)
        task = taskClass()
        return task
    # end _createTask()

    def _deserializeStandardAttributes(self, backgroundTask, backgroundTaskElem):
        standardAttrs = {}
        nodes = backgroundTaskElem.selectNodes(u"zns:task-attributes/zns:attribute") #$NON-NLS-1$
        for node in nodes:
            standardAttrs[node.getAttribute(u"name")] = node.getText() #$NON-NLS-1$

        name = standardAttrs[u"name"] #$NON-NLS-1$
        startTime = ZSchemaDateTime(standardAttrs[u"start-time"]) #$NON-NLS-1$
        endTime = None
        if u"end-time" in standardAttrs: #$NON-NLS-1$
            endTime = ZSchemaDateTime(standardAttrs[u"end-time"]) #$NON-NLS-1$
        numWorkUnits = string.atoi(standardAttrs[u"total-work-units"]) #$NON-NLS-1$
        numCompletedWorkUnits = string.atoi(standardAttrs[u"completed-work-units"]) #$NON-NLS-1$
        cancelled = standardAttrs[u"cancelled"] == u"true" #$NON-NLS-2$ #$NON-NLS-1$

        backgroundTask.setName(name)
        backgroundTask.setStartTime(startTime)
        backgroundTask.setEndTime(endTime)
        backgroundTask.setNumWorkUnits(numWorkUnits)
        backgroundTask.setNumCompletedWorkUnits(numCompletedWorkUnits)
        backgroundTask.setCancelled(cancelled)
    # end _deserializeStandardAttributes()

    def _deserializeError(self, backgroundTask, backgroundTaskElem):
        errorElem = backgroundTaskElem.selectSingleNode(u"zns:error") #$NON-NLS-1$
        if errorElem is not None:
            messageElem = errorElem.selectSingleNode(u"zns:message") #$NON-NLS-1$
            detailsElem = errorElem.selectSingleNode(u"zns:details") #$NON-NLS-1$
            backgroundTask.setError(messageElem.getText(), detailsElem.getText())
    # end _deserializeError()

    def _deserializeCustomAttributes(self, backgroundTask, backgroundTaskElem):
        customAttrs = {}
        nodes = backgroundTaskElem.selectNodes(u"zns:custom-attributes/zns:attribute") #$NON-NLS-1$
        for node in nodes:
            key = node.getAttribute(u"name") #$NON-NLS-1$
            value = node.getText()
            customAttrs[key] = value

        backgroundTask.setCustomAttributes(customAttrs)
    # end _deserializeCustomAttributes()

# end ZVer1BackgroundTaskDeserializer
