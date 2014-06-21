from zoundry.appframework.ui.actions.action import IZAction
from zoundry.appframework.ui.actions.action import IZActionContext
from zoundry.appframework.ui.actions.action import ZActionContext

# ------------------------------------------------------------------------------------
# The interface that all menu actions must implement.
# ------------------------------------------------------------------------------------
class IZMenuActionContext(IZActionContext):

    def getParentWindow(self):
        u"Returns the wx Window that is a parent to the menu." #$NON-NLS-1$
    # end getParentWindow()

# end IZMenuAction


# ------------------------------------------------------------------------------------
# An implementation of a menu action context.
# ------------------------------------------------------------------------------------
class ZMenuActionContext(ZActionContext, IZMenuActionContext):

    def __init__(self, window):
        self.window = window
        
        ZActionContext.__init__(self)
    # end __init__()

    def getParentWindow(self):
        return self.window
    # end getParentWindow()

# end ZMenuActionContext()


# ------------------------------------------------------------------------------------
# The interface that all menu actions must implement.
# ------------------------------------------------------------------------------------
class IZMenuAction(IZAction):

    def isVisible(self, context):
        u"Returns True if the menu item should be visible when displaying the menu." #$NON-NLS-1$
    # end isVisible()

    def isEnabled(self, context):
        u"Returns True if the menu item should be enabled when displaying the menu." #$NON-NLS-1$
    # end isEnabled()

    def isBold(self, context):
        u"Returns True if the menu item should be bold when displaying the menu." #$NON-NLS-1$
    # end isBold()

    def isChecked(self, context):
        u"Returns True if the menu item is currently checked (return None to indicate 'don't care')." #$NON-NLS-1$
    # end isBold()

    def getParameters(self):
        u"""getParameters() -> IZParameters
        Returns the IZParameters.""" #$NON-NLS-1$
    # end getParameters()

    def setParameters(self, izParameters):
        u"""setParameters(IZParameters) -> void
        Sets the IZParameters - normally during creation of menu items.""" #$NON-NLS-1$
    # end setParameters()

    def runCheckAction(self, actionContext, checked):
        u"Called to execute the action when the user clicks on a checkable menu item." #$NON-NLS-1$
    # end runCheckAction()

# end IZMenuAction


# ------------------------------------------------------------------------------------
# Simple base class for menu action impls.
# ------------------------------------------------------------------------------------
class ZMenuAction(IZMenuAction):

    def __init__(self):
        self.parameters = None
    # end __init__()

    def isVisible(self, context): #@UnusedVariable
        return True
    # end isVisible()

    def isEnabled(self, context): #@UnusedVariable
        return True
    # end isEnabled()

    def isBold(self, context): #@UnusedVariable
        return False
    # end isBold()
    
    def isChecked(self, context): #@UnusedVariable
        # Return None to let the menu framework handle it.
        return None
    # end isChecked()

    def setParameters(self, izParameters):
        self.parameters = izParameters
    # end getParameters()

    def getParameters(self):
        return self.parameters
    # end getParameters()

    def runCheckAction(self, actionContext, checked): #@UnusedVariable
        self.runAction(actionContext)
    # end runCheckAction()

# end ZMenuAction
        