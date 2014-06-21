from zoundry.appframework.global_services import getApplicationModel
from zoundry.base.util.zthread import IZRunnable

# ------------------------------------------------------------------------------------
# When an action is run, an action context is supplied as well.  The action context
# provides access to data that the action will need in order to run properly.
# Specific types of actions will likely have specific contexts that extend this one.
# ------------------------------------------------------------------------------------
class IZActionContext:

    def getApplicationModel(self):
        u"Returns the current application model." #$NON-NLS-1$
    # end getApplicationModel()

# end IZActionContext


# ------------------------------------------------------------------------------------
# The interface that all actions must implement.
# ------------------------------------------------------------------------------------
class IZAction:

    def getDisplayName(self):
        u"""getDisplayName() -> string
        Gets the action's display name.""" #$NON-NLS-1$
    # end getDisplayName()

    def getDescription(self):
        u"""getDescription() -> string
        Gets the action's description.""" #$NON-NLS-1$
    # end getDescription()

    def runAction(self, actionContext):
        u"Called to execute the action." #$NON-NLS-1$
    # end runAction()

# end IZAction


# ------------------------------------------------------------------------------------
# An implementation of an action context.
# ------------------------------------------------------------------------------------
class ZActionContext:

    def __init__(self):
        pass
    # end __init__()

    def getApplicationModel(self):
        return getApplicationModel()
    # end getApplicationModel()

# end ZActionContext


# ------------------------------------------------------------------------------------
# Convenience class for running an action in a thread or a UI-exec event.
# ------------------------------------------------------------------------------------
class ZActionRunner(IZRunnable):

    def __init__(self, action, context):
        self.action = action
        self.context = context
    # end __init__()

    def run(self):
        self.action.runAction(self.context)
    # end run()

# end ZActionRunner

