from zoundry.appframework.ui.actions.action import IZAction
from zoundry.appframework.ui.actions.action import IZActionContext
from zoundry.appframework.ui.actions.action import ZActionContext

# ------------------------------------------------------------------------------------
# The interface that all accelerator actions must implement.
# ------------------------------------------------------------------------------------
class IZAcceleratorActionContext(IZActionContext):

    def getParentWindow(self):
        u"Returns the wx Window that is a parent to the accelerator." #$NON-NLS-1$
    # end getParentWindow()

# end IZAcceleratorAction


# ------------------------------------------------------------------------------------
# An implementation of a accelerator action context.
# ------------------------------------------------------------------------------------
class ZAcceleratorActionContext(ZActionContext, IZAcceleratorActionContext):

    def __init__(self, window):
        self.window = window
        
        ZActionContext.__init__(self)
    # end __init__()

    def getParentWindow(self):
        return self.window
    # end getParentWindow()

# end ZAcceleratorActionContext()


# ------------------------------------------------------------------------------------
# The interface that all accelerator actions must implement.
# ------------------------------------------------------------------------------------
class IZAcceleratorAction(IZAction):

    def getParameters(self):
        u"""getParameters() -> IZParameters
        Returns the IZParameters.""" #$NON-NLS-1$
    # end getParameters()

    def setParameters(self, izParameters):
        u"""setParameters(IZParameters) -> void
        Sets the IZParameters - normally during creation of accelerator items.""" #$NON-NLS-1$
    # end setParameters()

# end IZAcceleratorAction


# ------------------------------------------------------------------------------------
# Simple base class for accelerator action impls.
# ------------------------------------------------------------------------------------
class ZAcceleratorAction(IZAcceleratorAction):

    def __init__(self):
        self.parameters = None
    # end __init__()

    def setParameters(self, izParameters):
        self.parameters = izParameters
    # end getParameters()

    def getParameters(self):
        return self.parameters
    # end getParameters()

# end ZAcceleratorAction
        