from zoundry.appframework.ui.actions.menuaction import ZMenuAction

# -------------------------------------------------------------------------------------
# This is the action implementation for the View->Perspective->Standard main menu item.
# -------------------------------------------------------------------------------------
class ZChangePerspectiveMenuAction(ZMenuAction):

    def __init__(self, perspectiveId):
        self.perspectiveId = perspectiveId
    # end __init__()

    def isEnabled(self, context): #@UnusedVariable
        mainWindow = context.getParentWindow()
        return not mainWindow.getCurrentPerspectiveId() == self.perspectiveId
    # end isEnabled()

    def isChecked(self, context): #@UnusedVariable
        return not self.isEnabled(context)
    # end isChecked()

    def runAction(self, actionContext):
        actionContext.getParentWindow().onPerspectiveSwitch(self.perspectiveId)
    # end runAction()

# end ZChangePerspectiveMenuAction
