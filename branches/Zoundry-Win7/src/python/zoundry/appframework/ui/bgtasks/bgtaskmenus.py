from zoundry.appframework.messages import _extstr
from zoundry.appframework.ui.actions.menuaction import ZMenuAction
from zoundry.appframework.ui.widgets.controls.common.menu.menuimpl import ZActiveMenuNode
from zoundry.appframework.ui.widgets.controls.common.menu.menuimpl import ZMenuNode
from zoundry.appframework.ui.widgets.dialogs.standarddialogs import ZShowErrorMessage
from zoundry.appframework.ui.widgets.dialogs.standarddialogs import ZShowExceptionMessage
from zoundry.appframework.util.osutilfactory import getOSUtil
import wx

# -------------------------------------------------------------------------------------
# An action for opening the background task log file.
# -------------------------------------------------------------------------------------
class ZOpenBackgroundTaskLogFileAction(ZMenuAction):
    
    def __init__(self, task):
        self.task = task
        ZMenuAction.__init__(self)
    # end __init__()

    def runAction(self, actionContext):
        busyCursor = wx.BusyCursor()
        try:
            getOSUtil().openFileInDefaultEditor(self.task.getLogLocation())
        except Exception, e:
            ZShowExceptionMessage(actionContext.getParentWindow(), e)
        del busyCursor
    # end runAction()

# end ZOpenBackgroundTaskLogFileAction


# -------------------------------------------------------------------------------------
# An action for opening the background task log file.
# -------------------------------------------------------------------------------------
class ZShowTaskErrorAction(ZMenuAction):
    
    def __init__(self, task):
        self.task = task
        ZMenuAction.__init__(self)
    # end __init__()
    
    def runAction(self, actionContext):
        (errorMessage, errorDetails) = self.task.getError()
        ZShowErrorMessage(actionContext.getParentWindow(), errorMessage, errorDetails)
    # end runAction()

# end ZShowTaskErrorAction


# -------------------------------------------------------------------------------------
# Creates a menu node that will be the root of the menu displayed when the user clicks
# on the info glyph in the background task panel.
# -------------------------------------------------------------------------------------
def createBackgroundTaskInfoMenuNode(task):
    rootNode = ZMenuNode()
    
    openLogAction = ZOpenBackgroundTaskLogFileAction(task)
    openLogFileNode = ZActiveMenuNode(_extstr(u"bgtaskmenus.OpenLogFile"), _extstr(u"bgtaskmenus.OpenLogFileTooltip"), action = openLogAction) #$NON-NLS-2$ #$NON-NLS-1$
    rootNode.addChild(openLogFileNode)
    
    return rootNode
# end createBackgroundTaskInfoMenuNode()


# -------------------------------------------------------------------------------------
# Creates a menu node that will be the root of the menu displayed when the user clicks
# on the error glyph in the background task panel.
# -------------------------------------------------------------------------------------
def createBackgroundTaskErrorMenuNode(task):
    rootNode = ZMenuNode()
    
    openLogAction = ZOpenBackgroundTaskLogFileAction(task)
    openLogFileNode = ZActiveMenuNode(_extstr(u"bgtaskmenus.OpenLogFile"), _extstr(u"bgtaskmenus.OpenLogFileTooltip"), action = openLogAction) #$NON-NLS-2$ #$NON-NLS-1$
    
    showErrorAction = ZShowTaskErrorAction(task)
    showErrorNode = ZActiveMenuNode(_extstr(u"bgtaskmenus.ShowError"), _extstr(u"bgtaskmenus.ShowErrorTooltip"), action = showErrorAction) #$NON-NLS-2$ #$NON-NLS-1$

    rootNode.addChild(showErrorNode)
    rootNode.addChild(openLogFileNode)

    return rootNode
# end createBackgroundTaskErrorMenuNode()
