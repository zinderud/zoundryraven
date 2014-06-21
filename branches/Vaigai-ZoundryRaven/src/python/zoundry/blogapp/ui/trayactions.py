from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.ui.actions.menuaction import ZMenuAction
from zoundry.appframework.ui.util.uiutil import fireUIExecEvent
from zoundry.base.util.zthread import IZRunnable
from zoundry.blogapp.constants import IZBlogAppActionIDs
from zoundry.blogapp.messages import _extstr


# ------------------------------------------------------------------------------
# Action impl for the "Minimize" menu item in the Zoundry Raven tray icon 
# right-click context menu.
# ------------------------------------------------------------------------------
class ZMinimizeAction(ZMenuAction):

    def __init__(self):
        ZMenuAction.__init__(self)
    # end __init__()

    def getDisplayName(self):
        return _extstr(u"trayactions._Minimize") #$NON-NLS-1$
    # end getDisplayName()
    
    def getDescription(self):
        return _extstr(u"trayactions.MinimizeDescription") #$NON-NLS-1$
    # end getDescription()

    def isVisible(self, context): #@UnusedVariable
        return not context.getParentWindow().IsIconized()
    # end isVisible()

    def runAction(self, actionContext):
        actionContext.getParentWindow().Iconize(True)
    # end runAction()

# end ZMinimizeAction


# ------------------------------------------------------------------------------
# Action impl for the "Restore" menu item in the Zoundry Raven tray icon 
# right-click context menu.
# ------------------------------------------------------------------------------
class ZRestoreAction(ZMenuAction):

    def __init__(self):
        ZMenuAction.__init__(self)
    # end __init__()

    def getDisplayName(self):
        return _extstr(u"trayactions._Restore") #$NON-NLS-1$
    # end getDisplayName()
    
    def getDescription(self):
        return _extstr(u"trayactions.RestoreDescription") #$NON-NLS-1$
    # end getDescription()

    def isVisible(self, context): #@UnusedVariable
        return context.getParentWindow().IsIconized()
    # end isVisible()

    def runAction(self, actionContext):
        actionContext.getParentWindow().restoreFromMinimize()
    # end runAction()

# end ZRestoreAction


# ------------------------------------------------------------------------------
# Action impl for the "Exit" menu item in the Zoundry Raven tray icon 
# right-click context menu.
#
# This implementation delegates to the standard main menu Exit action.  However,
# it does this by running the delegate action as a UI event on the main window.
# The reason for this is to avoid calling Close on the main window from the 
# tray icon itself.  This must be avoided because the Close handler for the 
# main menu Destroys the tray icon.  The Tray Icon doesn't like it if someone
# tries to Destroy it while it is in the middle of handling a user action (the
# Exit menu click).
# ------------------------------------------------------------------------------
class ZExitFromTrayAction(ZMenuAction):

    def __init__(self):
        ZMenuAction.__init__(self)
        
        self.delegateAction = getApplicationModel().getActionRegistry().findAction(IZBlogAppActionIDs.EXIT_ACTION)
    # end __init__()

    def getDisplayName(self):
        return self.delegateAction.getDisplayName()
    # end getDisplayName()
    
    def getDescription(self):
        return self.delegateAction.getDescription()
    # end getDescription()

    def runAction(self, actionContext):
        class ZActionRunner(IZRunnable):
            def __init__(self, action, context):
                self.action = action
                self.context = context
            def run(self):
                self.action.runAction(self.context)
        runner = ZActionRunner(self.delegateAction, actionContext)
        fireUIExecEvent(runner, actionContext.getParentWindow())
    # end runAction()
    
# end ZExitFromTrayAction
