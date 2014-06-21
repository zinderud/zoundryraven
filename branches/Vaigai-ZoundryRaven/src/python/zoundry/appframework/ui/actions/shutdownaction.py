from zoundry.appframework.ui.actions.action import IZAction
from zoundry.appframework.ui.actions.action import IZActionContext
from zoundry.appframework.ui.actions.action import ZActionContext


# -----------------------------------------------------------------------------------
# The context that is passed to an instance of IZAction that is registered as a 
# shutdown action.
# -----------------------------------------------------------------------------------
class IZShutdownActionContext(IZActionContext):

    def getWindow(self):
        u"Returns the main application's window." #$NON-NLS-1$
    # end getWindow()

# end IZShutdownActionContext


# ------------------------------------------------------------------------------------
# An implementation of a shutdown action context.
# ------------------------------------------------------------------------------------
class ZShutdownActionContext(ZActionContext, IZShutdownActionContext):

    def __init__(self, window):
        self.window = window
        ZActionContext.__init__(self)
    # end __init__()

    def getWindow(self):
        return self.window
    # end getWindow()

# end ZShutdownActionContext()


# ------------------------------------------------------------------------------------
# The interface that all shutdown actions must implement.
# ------------------------------------------------------------------------------------
class IZShutdownAction(IZAction):

    def shouldShutdown(self, actionContext):
        u"Called during shutdown to give the shutdown action an opportunity to cancel the shutdown process." #$NON-NLS-1$
    # end shouldShutdown()

# end IZShutdownAction
