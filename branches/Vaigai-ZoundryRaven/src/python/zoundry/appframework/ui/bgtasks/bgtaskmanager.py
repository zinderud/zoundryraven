from zoundry.appframework.constants import IZAppUserPrefsKeys
from zoundry.appframework.global_services import getResourceRegistry
from zoundry.appframework.messages import _extstr
from zoundry.appframework.models.ui.bgtasks.bgtaskmodel import ZBackgroundTaskManagerModel
from zoundry.appframework.services.backgroundtask.backgroundtask import IZBackgroundTaskServiceListener
from zoundry.appframework.ui.bgtasks.bgtaskpanel import ZBackgroundTaskPanel
from zoundry.appframework.ui.dialogs.mixins import ZPersistentDialogMixin
from zoundry.appframework.ui.events.commonevents import ZEVT_REFRESH
from zoundry.appframework.ui.util.uiutil import fireRefreshEvent
from zoundry.appframework.ui.widgets.controls.advanced.panellist import IZPanelListProvider
from zoundry.appframework.ui.widgets.controls.advanced.panellist import ZPanelListBox
from zoundry.appframework.ui.widgets.dialogs.standarddialogs import ZShowExceptionMessage
from zoundry.appframework.ui.widgets.window import ZBaseWindow
from zoundry.base.exceptions import ZException
import wx

# FIXME (EPW) should have a multi-part .ico for this instead
ICON_IMAGES = [
    u"images/mainapp/icon/icon16x16.png", #$NON-NLS-1$
    u"images/mainapp/icon/icon24x24.png", #$NON-NLS-1$
    u"images/mainapp/icon/icon32x32.png", #$NON-NLS-1$
    u"images/mainapp/icon/icon48x48.png" #$NON-NLS-1$
]


BGTASK_MANAGER_WINDOW = None

# ------------------------------------------------------------------------------------
# Use this function to show the background task manager window.  It will enforce a
# singleton window instance.
# ------------------------------------------------------------------------------------
def ZShowBackgroundTaskManager():
    global BGTASK_MANAGER_WINDOW
    try:
        if BGTASK_MANAGER_WINDOW is None:
            BGTASK_MANAGER_WINDOW = ZBackgroundTaskManagerWindow(None)
        BGTASK_MANAGER_WINDOW.Show()
        BGTASK_MANAGER_WINDOW.Raise()
    except Exception, e:
        ZShowExceptionMessage(None, ZException(u"Error opening Background Task Manager", e)) #$NON-NLS-1$
# end ZShowBackgroundTaskManager


# ------------------------------------------------------------------------------------
# Getter for the background task manager window.
# ------------------------------------------------------------------------------------
def getBackgroundTaskManager():
    global BGTASK_MANAGER_WINDOW
    return BGTASK_MANAGER_WINDOW
# end getBackgroundTaskManager()


# ------------------------------------------------------------------------------------
# Extends the basic panel list box in order to provide a way to destroy the child
# panels.
# ------------------------------------------------------------------------------------
class ZBackgroundTaskPanelListBox(ZPanelListBox):

    def __init__(self, provider, parent):
        ZPanelListBox.__init__(self, provider, parent)
    # end __init__()

    def destroyPanels(self):
        for (item, panel) in self.internalRepresentation.getPanelData(): #@UnusedVariable
            panel.destroy()
    # end destroyPanels()

# end ZBackgroundTaskPanelListBox


# ------------------------------------------------------------------------------------
# Provider used to populate the list of background tasks.
# ------------------------------------------------------------------------------------
class ZBackgroundTaskListProvider(IZPanelListProvider):

    def __init__(self, model):
        self.model = model
    # end __init__()

    def getNumRows(self):
        return len(self.model.getBackgroundTasks())
    # end getNumRows()

    def getRowItem(self, rowIndex):
        return self.model.getBackgroundTasks()[rowIndex]
    # end getRowItem()

    def createItemPanel(self, parent, rowItem):
        return ZBackgroundTaskPanel(self.model, rowItem, parent)
    # end createItemPanel()

# end ZBackgroundTaskVListContentProvider


# --------------------------------------------------------------------------------
# The Background Task Manager Manager window.  This window allows the user to
# manage their background tasks (cancel, clear, check status, etc).
# --------------------------------------------------------------------------------
class ZBackgroundTaskManagerWindow(ZBaseWindow, IZBackgroundTaskServiceListener, ZPersistentDialogMixin):

    def __init__(self, parent):
        self.model = ZBackgroundTaskManagerModel()

        ZBaseWindow.__init__(self, parent, _extstr(u"bgtaskmanager.BackgroundTaskManager"), name = u"ZBackgroundTaskManager") #$NON-NLS-2$ #$NON-NLS-1$
        ZPersistentDialogMixin.__init__(self, IZAppUserPrefsKeys.BGTASK_WINDOW)
        
        self.Layout()

        self.model.getService().addListener(self)
    # end __init__()

    def _createWindowWidgets(self, parent):
        provider = ZBackgroundTaskListProvider(self.model)
        self.bgTaskList = ZBackgroundTaskPanelListBox(provider, parent)
        self.bgTaskList.SetSizeHints(400, 400)
        self.bgTaskList.SetBackgroundColor(wx.Color(235, 236, 244))
        self.cleanUpButton = wx.Button(parent, wx.ID_ANY, _extstr(u"bgtaskmanager.CleanUp")) #$NON-NLS-1$
    # end _createWindowWidgets()

    def _populateWindowWidgets(self):
        self.SetIcons(getResourceRegistry().getIconBundle(ICON_IMAGES))
    # end _populateWindowWidgets()

    def _layoutWindowWidgets(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.bgTaskList, 1, wx.EXPAND | wx.ALL, 8)
        sizer.Add(self.cleanUpButton, 0, wx.ALIGN_RIGHT | wx.RIGHT | wx.BOTTOM, 5)

        return sizer
    # end _layoutWindowWidgets()

    def _bindWidgetEvents(self):
        self.Bind(wx.EVT_CLOSE, self.onClose, self)
        self.Bind(wx.EVT_BUTTON, self.onCleanUp, self.cleanUpButton)
        self.Bind(ZEVT_REFRESH, self.onRefresh, self)
    # end _bindWidgetEvents()

    def onCleanUp(self, event):
        self.model.cleanUpTasks()
        event.Skip()
    # end onCleanUp()
    
    def onRefresh(self, event):
        self.bgTaskList.Refresh()
        event.Skip()
    # end onRefresh()

    def _setInitialFocus(self):
        pass
    # end _setInitialFocus()

    def onClose(self, event):
        self._destroyPanels()
        self.model.getService().removeListener(self)

        global BGTASK_MANAGER_WINDOW
        BGTASK_MANAGER_WINDOW = None

        event.Skip()
    # end onClose()

    def onTaskAdded(self, task): #@UnusedVariable
        fireRefreshEvent(self)
    # end onTaskAdded()

    def onTaskRemoved(self, task): #@UnusedVariable
        fireRefreshEvent(self)
    # end onTaskRemoved()

    def _destroyPanels(self):
        self.bgTaskList.destroyPanels()
    # end _destroyPanels()

# end ZBackgroundTaskManagerWindow
