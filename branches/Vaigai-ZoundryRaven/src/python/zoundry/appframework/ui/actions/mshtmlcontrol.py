from zoundry.appframework.ui.actions.acceleratoraction import ZAcceleratorAction
from zoundry.appframework.ui.actions.action import ZActionContext

# ------------------------------------------------------------------------------
# Action context used for mshtml control actions.
# ------------------------------------------------------------------------------
class ZMSHTMLActionContext(ZActionContext):

    def __init__(self, control):
        self.control = control
    # end __init__()

    def getControl(self):
        return self.control
    # end getControl()

# end ZMSHTMLActionContext


# ------------------------------------------------------------------------------
# Implements the DEL key for the MSHTML control.
# ------------------------------------------------------------------------------
class ZMSHTMLControlDelAction(ZAcceleratorAction):

    def runAction(self, actionContext): #@UnusedVariable
        actionContext.getControl().onDeleteKey()
    # end runAction()

# end ZMSHTMLControlDelAction


# ------------------------------------------------------------------------------
# Implements "Select All" for the MSHTML control.
# ------------------------------------------------------------------------------
class ZMSHTMLControlSelectAllAction(ZAcceleratorAction):

    def runAction(self, actionContext): #@UnusedVariable
        actionContext.getControl().selectAll()
    # end runAction()

# end ZMSHTMLControlSelectAllAction
