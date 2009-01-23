from zoundry.appframework.ui.actions.action import IZAction
from zoundry.appframework.ui.actions.action import IZActionContext
from zoundry.appframework.ui.actions.action import ZActionContext


# -----------------------------------------------------------------------------------
# The context that is passed to an instance of IZAction that is registered as a 
# startup action.
# -----------------------------------------------------------------------------------
class IZStartupActionContext(IZActionContext):

    def getWindow(self):
        u"Returns the main application's window." #$NON-NLS-1$
    # end getWindow()

# end IZStartupActionContext


# ------------------------------------------------------------------------------------
# An implementation of a startup action context.
# ------------------------------------------------------------------------------------
class ZStartupActionContext(ZActionContext, IZStartupActionContext):

    def __init__(self, window):
        self.window = window
        ZActionContext.__init__(self)
    # end __init__()

    def getWindow(self):
        return self.window
    # end getWindow()

# end ZStartupActionContext()


# ------------------------------------------------------------------------------------
# The interface that all startup actions must implement.
# ------------------------------------------------------------------------------------
class IZStartupAction(IZAction):
    u"This interface defines a startup action." #$NON-NLS-1$

# end IZStartupAction
