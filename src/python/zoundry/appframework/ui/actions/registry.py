from zoundry.appframework.zplugin.extpointdef import ZExtensionPointBaseDef
from zoundry.base.exceptions import ZException
from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.constants import IZAppExtensionPoints

# ------------------------------------------------------------------------------
# Represents a contributed action.
# ------------------------------------------------------------------------------
class ZActionDef(ZExtensionPointBaseDef):

    def __init__(self, extensionPoint):
        ZExtensionPointBaseDef.__init__(self, extensionPoint)
    # end __init__()

    def createAction(self):
        actionClass = self.getClass()
        return actionClass()
    # end createAction()

# end ZActionDef


# ------------------------------------------------------------------------------
# Interface for the application Action Registry.
# ------------------------------------------------------------------------------
class IZActionRegistry:

    def registerAction(self, actionId, action):
        u"""registerAction(id, IZAction) -> None
        Adds the action to the registry.""" #$NON-NLS-1$
    # end registerAction()

    def findAction(self, actionId):
        u"""findAction(id) -> IZAction
        Finds the action with the given id.""" #$NON-NLS-1$
    # end findAction()

# end IZActionRegistry


# ------------------------------------------------------------------------------
# Implementation of the action registry.
# ------------------------------------------------------------------------------
class ZActionRegistry(IZActionRegistry):

    def __init__(self):
        self.actionMap = {}
        
        self._loadActions()
    # end __init__()

    def _loadActions(self):
        pluginRegistry = getApplicationModel().getPluginRegistry()
        extensions = pluginRegistry.getExtensions(IZAppExtensionPoints.ZEP_ZOUNDRY_CORE_ACTION)
        actionDefs = map(ZActionDef, extensions)
        for actionDef in actionDefs:
            self.registerAction(actionDef.getId(), actionDef.createAction())
    # end _loadActions()

    def registerAction(self, actionId, action):
        if actionId in self.actionMap:
            raise ZException(u"Action with id %s already exists in the registry." % actionId) #$NON-NLS-1$
        self.actionMap[actionId] = action
    # end registerAction()

    def findAction(self, actionId):
        if actionId in self.actionMap:
            return self.actionMap[actionId]
        return None
    # end findAction()

# end ZActionRegistry
