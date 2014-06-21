from zoundry.appframework.constants import IZAppNamespaces
from zoundry.base.zdom.dom import ZDom

# -----------------------------------------------------------------------------------------
# The interface that all background task serializer implementations must implement.
# -----------------------------------------------------------------------------------------
class IZBackgroundTaskSerializer:

    def serialize(self, task):
        u"Called to serialize a background task (returns a dom)." #$NON-NLS-1$
    # end serialize()

# end IZBackgroundTaskSerializer


# -----------------------------------------------------------------------------------------
# An implementation of a background task serializer for version 1.0 (or 2006/06) of the 
# Zoundry Raven background task format.
# -----------------------------------------------------------------------------------------
class ZVer1BackgroundTaskSerializer(IZBackgroundTaskSerializer):

    def __init__(self):
        pass
    # end __init__()

    def serialize(self, task):
        taskDom = ZDom()
        taskDom.loadXML(u"<task xmlns='%s' />" % IZAppNamespaces.RAVEN_TASK_NAMESPACE_2006_05) #$NON-NLS-1$
        taskElem = taskDom.documentElement
        taskElem.setAttribute(u"task-id", task.getId()) #$NON-NLS-1$
        taskElem.setAttribute(u"class", unicode(task.__class__)) #$NON-NLS-1$
        
        self._serializeStandardAttributes(task, taskElem)
        self._serializeError(task, taskElem)
        self._serializeCustomAttributes(task, taskElem)

        return taskDom
    # end serialize()
    
    def _serializeStandardAttributes(self, task, parentElem):
        taskAttrsElem = parentElem.ownerDocument.createElement(u"task-attributes", IZAppNamespaces.RAVEN_TASK_NAMESPACE_2006_05) #$NON-NLS-1$
        parentElem.appendChild(taskAttrsElem)
        
        # Name
        attributeElem = taskAttrsElem.ownerDocument.createElement(u"attribute", IZAppNamespaces.RAVEN_TASK_NAMESPACE_2006_05) #$NON-NLS-1$
        attributeElem.setAttribute(u"name", u"name") #$NON-NLS-2$ #$NON-NLS-1$
        attributeElem.setText(task.getName())
        taskAttrsElem.appendChild(attributeElem)
        
        # Start Time
        attributeElem = taskAttrsElem.ownerDocument.createElement(u"attribute", IZAppNamespaces.RAVEN_TASK_NAMESPACE_2006_05) #$NON-NLS-1$
        attributeElem.setAttribute(u"name", u"start-time") #$NON-NLS-2$ #$NON-NLS-1$
        attributeElem.setText(str(task.getStartTime()))
        taskAttrsElem.appendChild(attributeElem)
        
        # End Time
        if task.getEndTime() is not None:
            attributeElem = taskAttrsElem.ownerDocument.createElement(u"attribute", IZAppNamespaces.RAVEN_TASK_NAMESPACE_2006_05) #$NON-NLS-1$
            attributeElem.setAttribute(u"name", u"end-time") #$NON-NLS-2$ #$NON-NLS-1$
            attributeElem.setText(str(task.getEndTime()))
            taskAttrsElem.appendChild(attributeElem)
        
        # Total Work Units
        attributeElem = taskAttrsElem.ownerDocument.createElement(u"attribute", IZAppNamespaces.RAVEN_TASK_NAMESPACE_2006_05) #$NON-NLS-1$
        attributeElem.setAttribute(u"name", u"total-work-units") #$NON-NLS-2$ #$NON-NLS-1$
        attributeElem.setText(str(task.getNumWorkUnits()))
        taskAttrsElem.appendChild(attributeElem)

        # Completed Work Units
        attributeElem = taskAttrsElem.ownerDocument.createElement(u"attribute", IZAppNamespaces.RAVEN_TASK_NAMESPACE_2006_05) #$NON-NLS-1$
        attributeElem.setAttribute(u"name", u"completed-work-units") #$NON-NLS-2$ #$NON-NLS-1$
        attributeElem.setText(str(task.getNumCompletedWorkUnits()))
        taskAttrsElem.appendChild(attributeElem)

        # Cancelled Flag
        attributeElem = taskAttrsElem.ownerDocument.createElement(u"attribute", IZAppNamespaces.RAVEN_TASK_NAMESPACE_2006_05) #$NON-NLS-1$
        attributeElem.setAttribute(u"name", u"cancelled") #$NON-NLS-2$ #$NON-NLS-1$
        if task.isCancelled():
            attributeElem.setText(u"true") #$NON-NLS-1$s
        else:
            attributeElem.setText(u"false") #$NON-NLS-1$
        taskAttrsElem.appendChild(attributeElem)
    # end _serializeStandardAttributes

    def _serializeError(self, task, parentElem):
        if not task.hasError():
            return
    
        (errorMessage, errorDetails) = task.getError()
        errorElem = parentElem.ownerDocument.createElement(u"error", IZAppNamespaces.RAVEN_TASK_NAMESPACE_2006_05) #$NON-NLS-1$
        parentElem.appendChild(errorElem)
        
        messageElem = parentElem.ownerDocument.createElement(u"message", IZAppNamespaces.RAVEN_TASK_NAMESPACE_2006_05) #$NON-NLS-1$
        detailsElem = parentElem.ownerDocument.createElement(u"details", IZAppNamespaces.RAVEN_TASK_NAMESPACE_2006_05) #$NON-NLS-1$
        errorElem.appendChild(messageElem)
        errorElem.appendChild(detailsElem)
        messageElem.setText(errorMessage)
        detailsElem.setText(errorDetails)
    # end _serializeError()

    def _serializeCustomAttributes(self, task, parentElem):
        customAttributes = task.getCustomAttributes()
        if customAttributes is None or len(customAttributes) == 0:
            return
        
        customAttrsElem = parentElem.ownerDocument.createElement(u"custom-attributes", IZAppNamespaces.RAVEN_TASK_NAMESPACE_2006_05) #$NON-NLS-1$
        parentElem.appendChild(customAttrsElem)
        
        for key in customAttributes:
            value = customAttributes[key]
            attributeElem = parentElem.ownerDocument.createElement(u"attribute", IZAppNamespaces.RAVEN_TASK_NAMESPACE_2006_05) #$NON-NLS-1$
            attributeElem.setAttribute(u"name", key) #$NON-NLS-1$
            attributeElem.setText(value)
            customAttrsElem.appendChild(attributeElem)
    # end _serializeCustomAttributes

# end ZVer1BackgroundTaskSerializer
