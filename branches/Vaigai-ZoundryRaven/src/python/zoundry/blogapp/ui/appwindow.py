from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.global_services import getResourceRegistry
from zoundry.appframework.ui.actions.menuaction import ZMenuActionContext
from zoundry.appframework.ui.actions.shutdownaction import ZShutdownActionContext
from zoundry.appframework.ui.actions.startupaction import ZStartupActionContext
from zoundry.appframework.ui.util.uiutil import fireUIExecEvent
from zoundry.appframework.ui.widgets.controls.common.acceleratortable import ZAcceleratorEntry
from zoundry.appframework.ui.widgets.controls.common.acceleratortable import ZAcceleratorTable
from zoundry.appframework.ui.widgets.controls.common.menu.menu import ZMenuBar
from zoundry.appframework.ui.widgets.controls.common.menu.menumodel import ZModelBasedMenuContentProvider
from zoundry.appframework.ui.widgets.controls.common.menu.menumodel import ZModelBasedMenuEventHandler
from zoundry.appframework.ui.widgets.dialogs.standarddialogs import ZShowExceptionMessage
from zoundry.appframework.ui.widgets.window import ZBaseWindow
from zoundry.appframework.zplugin.extpointdef import ZExtensionPointBaseDef
from zoundry.base.util.zthread import IZRunnable
from zoundry.blogapp.blogthis import checkCmdLineForBlogThis
from zoundry.blogapp.constants import IZBlogAppAcceleratorIds
from zoundry.blogapp.constants import IZBlogAppExtensionPoints
from zoundry.blogapp.constants import IZBlogAppServiceIDs
from zoundry.blogapp.constants import IZBlogAppUserPrefsKeys
from zoundry.blogapp.exceptions import ZBlogAppException
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.services.singleton.singleton import IZSingletonServiceListener
#from zoundry.blogapp.ui.appstatusbar import ZRavenApplicationStatusBar
from zoundry.blogapp.ui.blogthishandler import ZBlogThisHandler
from zoundry.blogapp.ui.editors.editorwin import getEditorWindow
from zoundry.blogapp.ui.mainmenu import ZBlogAppMainMenuBarModel
from zoundry.blogapp.ui.menus.main.file_new import ZNewBlogPostMenuAction
from zoundry.blogapp.ui.menus.main.tools import ZSettingsMenuAction
from zoundry.blogapp.ui.perspectives.perspective import ZPerspectiveDef
from zoundry.blogapp.ui.trayicon import ZRavenTrayIcon
from zoundry.blogapp.ui.trayicon import ZRavenTrayIconPrefsAccessor
from zoundry.blogapp.ui.menus.main.tools import ZBackgroundTasksMenuAction
from zoundry.blogapp.ui.menus.main.tools import ZManageTemplatesMenuAction
from zoundry.blogapp.ui.menus.main.tools import ZAccountManagerMenuAction
import wx

# The default perspective to fall back on.
PERSPECTIVE_DEFAULT = u"zoundry.blogapp.ui.perspectives.standard" #$NON-NLS-1$


# FIXME (EPW) should have a multi-part .ico for this instead
ICON_IMAGES = [
    u"images/mainapp/icon/icon16x16.png", #$NON-NLS-1$
    u"images/mainapp/icon/icon24x24.png", #$NON-NLS-1$
    u"images/mainapp/icon/icon32x32.png", #$NON-NLS-1$
    u"images/mainapp/icon/icon48x48.png" #$NON-NLS-1$
]


# ------------------------------------------------------------------------------
# A simple runnable that will execute all of the startup actions.
# ------------------------------------------------------------------------------
class ZStartupActionRunner(IZRunnable):

    def __init__(self, ravenAppWindow):
        self.ravenAppWindow = ravenAppWindow
    # end __init__()

    def run(self):
        self.ravenAppWindow._runStartupActions()
    # end run()

# end ZStartupActionRunner


# ------------------------------------------------------------------------------
# An accelerator table for the main Raven window (create accelerators for the
# main menu items).
# ------------------------------------------------------------------------------
class ZRavenAppWindowAcceleratorTable(ZAcceleratorTable):

    def __init__(self):
        ZAcceleratorTable.__init__(self, IZBlogAppAcceleratorIds.ZID_MAIN_WINDOW_ACCEL)
    # end __init__()

    def _loadAdditionalEntries(self):
        return [
            ZAcceleratorEntry(wx.ACCEL_CTRL, ord(u'N'), ZNewBlogPostMenuAction()), #$NON-NLS-1$
            ZAcceleratorEntry(wx.ACCEL_ALT, ord(u'P'), ZSettingsMenuAction()), #$NON-NLS-1$
            ZAcceleratorEntry(wx.ACCEL_CTRL, ord(u'J'), ZBackgroundTasksMenuAction()), #$NON-NLS-1$
            ZAcceleratorEntry(wx.ACCEL_CTRL, ord(u'T'), ZManageTemplatesMenuAction()), #$NON-NLS-1$
            ZAcceleratorEntry(wx.ACCEL_ALT, ord(u'A'), ZAccountManagerMenuAction()), #$NON-NLS-1$
        ]
    # end _loadAdditionalEntries()

# end ZRavenAppWindowAcceleratorTable


# ------------------------------------------------------------------------------
# This is the main application window.
# ------------------------------------------------------------------------------
class ZRavenApplicationWindow(ZBaseWindow, IZSingletonServiceListener):

    def __init__(self):
        self.perspectives = self._loadPerspectives()
        self.perspectiveId = self._getStartupPerspective()
        self.perspective = self._createPerspective(self.perspectiveId)
        self.startupActions = self._loadStartupActions()
        self.shutdownActions = self._loadShutdownActions()
        self.iconBundle = getResourceRegistry().getIconBundle(ICON_IMAGES)
        self.trayIconPrefs = ZRavenTrayIconPrefsAccessor()
        self.trayIcon = None

        size = self._getWindowSize()
        pos = self._getWindowPos()
        ZBaseWindow.__init__(self, None, u"Zoundry Raven", size = size, pos = pos) #$NON-NLS-1$

        userPrefs = getApplicationModel().getUserProfile().getPreferences()
        isMax = userPrefs.getUserPreferenceBool(IZBlogAppUserPrefsKeys.APPWIN_MAXIMIZED, False)
        if isMax:
            self.Maximize()

        self.SetIcons(self.iconBundle)
        self.Show(True)

        self._createTrayIcon()
        if self.trayIconPrefs.isAlwaysShowTrayIcon():
            self._showTrayIcon()

        self._registerAsSingletonListener()
        self._doCmdLineBlogThis()

        fireUIExecEvent(ZStartupActionRunner(self), self)
    # end __init__()

    def _registerAsSingletonListener(self):
        service = getApplicationModel().getService(IZBlogAppServiceIDs.SINGLETON_SERVICE_ID)
        service.addListener(self)
    # end _registerAsSingletonListener()

    def _doCmdLineBlogThis(self):
        blogThisInfo = checkCmdLineForBlogThis()
        if blogThisInfo is not None:
            self.onBlogThis(blogThisInfo)
    # end _doCmdLineBlogThis()

    def _loadStartupActions(self):
        pluginReg = getApplicationModel().getPluginRegistry()
        extensions = pluginReg.getExtensions(IZBlogAppExtensionPoints.ZEP_STARTUP_ACTION)
        return map(ZExtensionPointBaseDef, extensions)
    # end _loadStartupActions()

    def _loadShutdownActions(self):
        pluginReg = getApplicationModel().getPluginRegistry()
        extensions = pluginReg.getExtensions(IZBlogAppExtensionPoints.ZEP_SHUTDOWN_ACTION)
        return map(ZExtensionPointBaseDef, extensions)
    # end _loadShutdownActions()

    def _loadPerspectives(self):
        pluginReg = getApplicationModel().getPluginRegistry()
        extensions = pluginReg.getExtensions(IZBlogAppExtensionPoints.ZEP_ZOUNDRY_PERSPECTIVE)
        return map(ZPerspectiveDef, extensions)
    # end _loadPerspectives()

    def _createTrayIcon(self):
        self.trayIcon = ZRavenTrayIcon(self)
    # end _createTrayIcon()

    def _showTrayIcon(self):
        if not self.trayIcon.IsIconInstalled():
            self.trayIcon.SetIcon(self.iconBundle.GetIcon(wx.Size(16, 16)), _extstr(u"ZoundryRaven")) #$NON-NLS-1$
    # end _showTrayIcon()

    def _hideTrayIcon(self):
        if self.trayIcon.IsIconInstalled():
            self.trayIcon.RemoveIcon()
    # end _hideTrayIcon()

    def _destroyTrayIcon(self):
        self.trayIcon.Destroy()
        del self.trayIcon
    # end _destroyTrayIcon()

    # Gets the perspective def for the given ID.
    def _getPerspectiveDef(self, perspectiveId):
        for pdef in self.perspectives:
            if pdef.getId() == perspectiveId:
                return pdef
        return None
    # end _getPerspectiveDef()

    def _getStartupPerspective(self):
        userPrefs = getApplicationModel().getUserProfile().getPreferences()
        return userPrefs.getUserPreference(IZBlogAppUserPrefsKeys.APPWIN_DEFAULT_PERSPECTIVE, PERSPECTIVE_DEFAULT)
    # end _getStartupPerspective()

    def _createPerspective(self, perspectiveId):
        pdef = self._getPerspectiveDef(perspectiveId)
        if not pdef:
            pdef = self._getPerspectiveDef(PERSPECTIVE_DEFAULT)
        if not pdef:
            raise ZBlogAppException(_extstr(u"appwindow.FailedToLoadDefaultPerspective")) #$NON-NLS-1$
        pclass = pdef.getClass()
        perspective = pclass()
        return perspective
    # end _createPerspective()

    def _getWindowSize(self):
        userPrefs = getApplicationModel().getUserProfile().getPreferences()
        width = userPrefs.getUserPreferenceInt(IZBlogAppUserPrefsKeys.APPWIN_WIDTH, 800)
        height = userPrefs.getUserPreferenceInt(IZBlogAppUserPrefsKeys.APPWIN_HEIGHT, 600)

        if width < 100:
            width = 800
        if height < 100:
            width = 600

        return wx.Size(width, height)
    # end _getWindowSize()

    def _getWindowPos(self):
        userPrefs = getApplicationModel().getUserProfile().getPreferences()
        posX = userPrefs.getUserPreferenceInt(IZBlogAppUserPrefsKeys.APPWIN_X, -1)
        posY = userPrefs.getUserPreferenceInt(IZBlogAppUserPrefsKeys.APPWIN_Y, -1)

        if posX < 0:
            posX = -1
        if posY < 0:
            posY = -1
        displaySize = wx.GetDisplaySize()
        if posX >= displaySize.GetWidth() - 50:
            posX = -1
        if posY >= displaySize.GetHeight() - 50:
            posY = -1

        if posX != -1 and posY != -1:
            return wx.Point(posX, posY)
        return wx.DefaultPosition
    # end _getWindowPos()

    def _createWidgets(self):
        self._createMenuBar()
        self._createStatusBar()
        self._createPerspectiveUI()
        self._createAcceleratorTable()
    # end _createWidgets()

    def _createMenuBar(self):
        # FIXME (EPW) this should be supplied by the perspective
        menuContext = ZMenuActionContext(self)
        menuBarModel = ZBlogAppMainMenuBarModel(self.perspectives)
        provider = ZModelBasedMenuContentProvider(menuBarModel, menuContext)
        eventHandler = ZModelBasedMenuEventHandler(menuBarModel, menuContext)
        self.menuBar = ZMenuBar(self, provider, eventHandler)
        self.SetMenuBar(self.menuBar)
    # end _createMenuBar()

    def _createStatusBar(self):
        # FIXME (EPW) this should be supplied by the perspective
        self.statusBar = self.CreateStatusBar()
#        self.statusBar = ZRavenApplicationStatusBar(self)
        self.SetStatusBar(self.statusBar)
    # end _createStatusBar()

    def _createPerspectiveUI(self):
        self.panel = self.perspective.createUIPanel(self)
    # end _createPerspectiveUI()

    def _createAcceleratorTable(self):
        self.acceleratorTable = ZRavenAppWindowAcceleratorTable()
        self.SetAcceleratorTable(self.acceleratorTable)
    # end _createAcceleratorTable()

    def _bindWidgetEvents(self):
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.Bind(wx.EVT_ICONIZE, self.onIconize)
        self.acceleratorTable.bindTo(self)
    # end _bindWidgetEvents()

    def getCurrentPerspectiveId(self):
        return self.perspectiveId
    # end getCurrentPerspectiveId()

    def onPerspectiveSwitch(self, perspectiveId):
        self.perspective.destroy()
        self.DestroyChildren()
        self.perspective = self._createPerspective(perspectiveId)
        self._createPerspectiveUI()
        self.perspectiveId = perspectiveId

        self._layoutWidgets()

        userPrefs = getApplicationModel().getUserProfile().getPreferences()
        userPrefs.setUserPreference(IZBlogAppUserPrefsKeys.APPWIN_DEFAULT_PERSPECTIVE, perspectiveId)

        self.menuBar.refresh()
    # end onPerspectiveSwitch()

    def onIconize(self, event):
        if event.Iconized():
            if self.trayIconPrefs.isHideWhenMinimized():
                self._showTrayIcon()
                self.Show(False)
        else:
            self.Show(True)
        event.Skip()
    # end onIconize()

    def restoreFromMinimize(self):
        self.Show(True)
        self.Iconize(False)
        if not self.trayIconPrefs.isAlwaysShowTrayIcon():
            self._hideTrayIcon()
    # end restoreFromMinimize()

    def onClose(self, event):
        # Run all of the shutdown actions - if they all succeed, then exit.
        try:
            if self._runShutdownActions():
                self.perspective.destroy()
                self._destroyTrayIcon()
                event.Skip()
            else:
                event.Veto()
        except Exception, e:
            ZShowExceptionMessage(self, e)
            event.Skip()
    # end onClose()

    def onBlogThis(self, blogThisData):
        class ZBlogThisRunner(IZRunnable):
            def __init__(self, blogThisInfo):
                self.blogThisInfo = blogThisInfo
            def run(self):
                blogThisContentHandler= ZBlogThisHandler( blogThisData )
                doc = blogThisContentHandler.createBlogDocument()
                editorWindow = getEditorWindow()
                editorWindow.openDocument(doc)
                editorWindow.Show(True)
                editorWindow.Raise()
        runner = ZBlogThisRunner(blogThisData)
        fireUIExecEvent(runner, self)
    # end onBlogThis()

    def _populateWidgets(self):
        pass
    # end _populateWidgets()

    def _layoutWidgets(self):
        if self.panel is not None:
            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(self.panel, 1, wx.EXPAND)
            self.SetSizer(sizer)
            self.SetAutoLayout(True)
            self.Layout()
    # end _layoutWidgets()

    def _runStartupActions(self):
        for actionDef in self.startupActions:
            classs = actionDef.getClass()
            action = classs()
            context = ZStartupActionContext(self)
            action.runAction(context)
    # end _runStartupActions()

    def _runShutdownActions(self):
        # First, check to make sure all shutdown actions think it's ok to shutdown.
        for actionDef in self.shutdownActions:
            classs = actionDef.getClass()
            action = classs()
            context = ZShutdownActionContext(self)
            rval = action.shouldShutdown(context)
            if rval == False:
                return False
        # If they all say 'ok', then run them all.
        for actionDef in self.shutdownActions:
            classs = actionDef.getClass()
            action = classs()
            context = ZShutdownActionContext(self)
            action.runAction(context)
        return True
    # end _runShutdownActions()

# end ZRavenApplicationWindow
