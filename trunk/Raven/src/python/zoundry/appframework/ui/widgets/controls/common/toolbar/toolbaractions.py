from zoundry.appframework.ui.actions.menuaction import IZMenuAction
from zoundry.appframework.ui.actions.menuaction import ZMenuActionContext

# ------------------------------------------------------------------------------
# The toolbar's context menu's action context.
# ------------------------------------------------------------------------------
class ZToolBarMenuContext(ZMenuActionContext):

    def __init__(self, window):
        ZMenuActionContext.__init__(self, window)
    # end __init__()

    def getToolBar(self):
        return self.window
    # end getToolBar()

# end ZToolBarMenuContext


# ------------------------------------------------------------------------------
# The Show Text check-box menu item action.
# ------------------------------------------------------------------------------
class ZShowTextMenuAction(IZMenuAction):

    def __init__(self):
        pass
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

    def isChecked(self, context):
        return context.getToolBar().isShowText()
    # end isChecked()

    def runAction(self, actionContext): #@UnusedVariable
        pass
    # end runAction()

    def runCheckAction(self, actionContext, checked):
        actionContext.getToolBar().showText(checked)
    # end runCheckAction()

# end ZShowTextMenuAction


# ------------------------------------------------------------------------------
# The Show Text check-box menu item action.
# ------------------------------------------------------------------------------
class ZResizeToolbarAction(IZMenuAction):

    def __init__(self, size):
        self.size = size
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

    def isChecked(self, context):
        return context.getToolBar().getToolSize() == self.size
    # end isChecked()

    def runAction(self, actionContext): #@UnusedVariable
        pass
    # end runAction()

    def runCheckAction(self, actionContext, checked): #@UnusedVariable
        actionContext.getToolBar().setToolSize(self.size)
    # end runCheckAction()

# end ZShowTextMenuAction
