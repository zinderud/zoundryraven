from zoundry.appframework.ui.actions.menuaction import ZMenuAction
from zoundry.blogapp.messages import _extstr

# -------------------------------------------------------------------------------------
# This is the action implementation for the File->Exit main menu item.
# -------------------------------------------------------------------------------------
class ZExitMenuAction(ZMenuAction):

    def getDisplayName(self):
        return _extstr(u"file.Exit") #$NON-NLS-1$
    # end getDisplayName()
    
    def getDescription(self):
        return _extstr(u"file.ExitDescription") #$NON-NLS-1$
    # end getDescription()

    def runAction(self, actionContext):
        actionContext.getParentWindow().Close()
    # end runAction()

# end ZExitMenuAction
