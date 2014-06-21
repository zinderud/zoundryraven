from zoundry.appframework.global_services import getResourceRegistry
from zoundry.appframework.ui.dialogs.mixins import ZPersistentDialogMixin
from zoundry.appframework.ui.events.toolbarevents import ZEVT_TOOLBAR_RESIZE
from zoundry.appframework.ui.widgets.controls.advanced.tabs import IZTabContainerListener
from zoundry.appframework.ui.widgets.controls.advanced.tabs import ZTabContainer
from zoundry.appframework.ui.widgets.controls.advanced.tabs import ZTabInfo
from zoundry.appframework.ui.widgets.controls.common.menu.menu import ZMenuBar
from zoundry.appframework.ui.widgets.controls.common.menu.menumodel import ZModelBasedMenuContentProvider
from zoundry.appframework.ui.widgets.controls.common.menu.menumodel import ZModelBasedMenuEventHandler
from zoundry.appframework.ui.widgets.controls.common.statusbar import ZStatusBar
from zoundry.appframework.ui.widgets.controls.common.statusbar import ZStatusBarModelBasedContentProvider
from zoundry.appframework.ui.widgets.controls.common.toolbar.toolbar import ZPersistentToolBar
from zoundry.appframework.ui.widgets.controls.common.toolbar.toolbar import ZToolBar
from zoundry.appframework.ui.widgets.controls.common.toolbar.toolbarmodel import ZModelBasedToolBarContentProvider
from zoundry.appframework.ui.widgets.controls.common.toolbar.toolbarmodel import ZModelBasedToolBarEventHandler
from zoundry.appframework.ui.widgets.dialogs.standarddialogs import ZShowYesNoCancelMessage
from zoundry.appframework.ui.widgets.window import ZBaseWindow
from zoundry.blogapp.constants import IZBlogAppUserPrefsKeys
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.ui.editors.blogeditor import ZBlogPostEditor
from zoundry.blogapp.ui.events.editors.editorevents import ZEVT_EDITOR_CLOSE
from zoundry.blogapp.ui.events.editors.editorevents import ZEVT_EDITOR_DIRTY
from zoundry.blogapp.ui.events.editors.editorevents import ZEVT_EDITOR_MENU_BAR_CHANGED
from zoundry.blogapp.ui.events.editors.editorevents import ZEVT_EDITOR_STATUS_BAR_CHANGED
from zoundry.blogapp.ui.events.editors.editorevents import ZEVT_EDITOR_TITLE_CHANGED
from zoundry.blogapp.ui.events.editors.editorevents import ZEVT_EDITOR_TOOL_BAR_CHANGED
import wx

# FIXME (EPW) should have a multi-part .ico for this instead
ICON_IMAGES = [
    u"images/mainapp/icon/icon16x16.png", #$NON-NLS-1$
    u"images/mainapp/icon/icon24x24.png", #$NON-NLS-1$
    u"images/mainapp/icon/icon32x32.png", #$NON-NLS-1$
    u"images/mainapp/icon/icon48x48.png" #$NON-NLS-1$
]


# ---------------------------------------------------------------------------------------
# The editor factory.
# ---------------------------------------------------------------------------------------
class ZEditorFactory:

    def __init__(self):
        pass
    # end __init__()

    def createEditor(self, parent, document):
        # FIXME (EPW) need to make this type-based, so that we can support other content (wiki, etc)
        return ZBlogPostEditor(parent, document)
    # end createEditor()

# end ZEditorFactory


# ---------------------------------------------------------------------------------------
# The editor window interface.
# ---------------------------------------------------------------------------------------
class IZEditorWindow:

    def openDocument(self, document):
        u"Opens the given document in the editor window." #$NON-NLS-1$
    # end openDocument()

    def getEditors(self):
        u"Returns a list of currently active editors." #$NON-NLS-1$
    # end getEditors()

# end IZEditorWindow


# ------------------------------------------------------------------------------
# Convenience method used to get the editor window.
# ------------------------------------------------------------------------------
EDITOR_WINDOW = None
def getEditorWindow():
    global EDITOR_WINDOW
    if EDITOR_WINDOW is None:
        EDITOR_WINDOW = _ZEditorWindow()

    return EDITOR_WINDOW
# end getEditorWindow()


# ------------------------------------------------------------------------------
# A concrete implementation of the editor window.
# ------------------------------------------------------------------------------
class _ZEditorWindow(IZEditorWindow, ZBaseWindow, IZTabContainerListener, ZPersistentDialogMixin):

    def __init__(self):
        self.editorFactory = ZEditorFactory()
        self.menuBar = None
        self.toolBar = None
        self.statusBar = None
        self.editors = []
        self.tabToEditorMap = {}
        self.parent = None

        ZBaseWindow.__init__(self, self.parent, u"", name = u"ZEditorWindow", size = wx.Size(640, 550)) #$NON-NLS-2$ #$NON-NLS-1$
        ZPersistentDialogMixin.__init__(self, IZBlogAppUserPrefsKeys.EDITOR_WINDOW, False)

        self.Layout()
    # end __init__()

    def _createWindowWidgets(self, parent):
        self.toolBarParent = parent
        self.toolBar = ZPersistentToolBar(IZBlogAppUserPrefsKeys.EDITOR_WINDOW_TOOLBAR, None, None, parent, ZToolBar.STYLE_SHOW_TEXT)
        self.tbStaticLine = wx.StaticLine(parent)
        self.tabContainer = ZTabContainer(parent)
        self.tabContainer.setListener(self)
    # end _createWindowWidgets()

    def _populateWindowWidgets(self):
        self.SetIcons(getResourceRegistry().getIconBundle(ICON_IMAGES))
    # end _populateWindowWidgets()

    def _layoutWindowWidgets(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.toolBar, 0, wx.EXPAND)
        sizer.Add(self.tbStaticLine, 0, wx.EXPAND)
        sizer.Add(self.tabContainer, 1, wx.EXPAND | wx.TOP, 5)
        return sizer
    # end _layoutWindowWidgets()

    def _bindWidgetEvents(self):
        self.Bind(wx.EVT_CLOSE, self.onClose, self)
        self.Bind(ZEVT_TOOLBAR_RESIZE, self.onToolBarResize, self.toolBar)

        self.Bind(ZEVT_EDITOR_CLOSE, self.onEditorClose)
        self.Bind(ZEVT_EDITOR_TITLE_CHANGED, self.onEditorTitleChanged)
        self.Bind(ZEVT_EDITOR_DIRTY, self.onEditorDirty)
        self.Bind(ZEVT_EDITOR_STATUS_BAR_CHANGED, self.onEditorStatusBarChanged)
        self.Bind(ZEVT_EDITOR_MENU_BAR_CHANGED, self.onEditorMenuBarChanged)
        self.Bind(ZEVT_EDITOR_TOOL_BAR_CHANGED, self.onEditorToolBarChanged)
    # end _bindWidgetEvents()

    def openDocument(self, document):
        editor = self.findEditor(document.getId())
        # If not already editing this document, create a new one.
        if editor is None:
            editor = self.editorFactory.createEditor(self.tabContainer, document)
            self._addEditor(editor)
            tabId = self.tabContainer.addTab(ZTabInfo(document.getTitle(), editor.getBitmap()), editor)
            self.tabToEditorMap[tabId] = editor

        # Bring the given editor into focus.
        self._focusOnEditor(editor)
        self.Raise()
        return editor
    # end openDocument()

    def findEditor(self, documentId):
        if documentId is None:
            return None
        for editor in self.editors:
            if editor.getDocumentId() == documentId:
                return editor
        return None
    # end findEditor()

    def closeEditor(self, editor):
        tabId = self._findTabIdForEditor(editor)
        self.tabContainer.removeTab(tabId)
        del self.tabToEditorMap[tabId]
        editor.destroy()
        self.editors.remove(editor)

        if len(self.editors) == 0:
            self.Close()
    # end closeEditor()

    def _addEditor(self, editor):
        self.editors.append(editor)
    # end _addEditor()

    def _focusOnEditor(self, editor):
        tabId = self._findTabIdForEditor(editor)
        if tabId is not None:
            self.tabContainer.selectTab(tabId)
            self.tabContainer.SetFocus()
    # end _focusOnEditor()

    def _findTabIdForEditor(self, editor):
        for (tabId, teditor) in self.tabToEditorMap.items():
            if editor == teditor:
                return tabId
        return None
    # end _findTabIdForEditor()

    def _findEditorByTabId(self, tabId):
        if tabId in self.tabToEditorMap:
            return self.tabToEditorMap[tabId]
        return None
    # end _findEditorByTabId()

    def _getSelectedEditor(self):
        tabId = self.tabContainer.getSelectedTabId()
        return self._findEditorByTabId(tabId)
    # end _getSelectedEditor()

    def getEditors(self):
        return self.editors
    # end getEditors()

    def close(self):
        u"""close() -> boolean
        Called to close the window.  Returns True if the 
        close succeeded, False otherwise.""" #$NON-NLS-1$
        for editor in self.editors:
            if editor.isDirty():
                rval = ZShowYesNoCancelMessage(self, _extstr(u"editorwin.SaveDocumentMessage") % editor.getTitle(), _extstr(u"editorwin.SaveDocument")) #$NON-NLS-2$ #$NON-NLS-1$
                if rval == wx.ID_CANCEL:
                    return False
                elif rval == wx.ID_YES:
                    editor.save()
                elif rval == wx.ID_NO:
                    pass
        for editor in self.editors:
            editor.destroy()
        self.editors = []
        return True
    # end close()

    def onEditorTitleChanged(self, event):
        selEditor = self._getSelectedEditor()
        editor = event.getEditor()
        if selEditor == editor:
            title = self._getEditorTitle(editor)
            self.SetTitle(title)
            tabId = self._findTabIdForEditor(editor)
            self.tabContainer.setTabName(tabId, title)
        event.Skip()
    # end onEditorTitleChanged()

    def onEditorClose(self, event):
        if self.onEditorClosing(event.getEditor()):
            self.closeEditor(event.getEditor())
        event.Skip()
    # end onEditorClose()

    def onEditorDirty(self, event):
        selEditor = self._getSelectedEditor()
        editor = event.getEditor()
        if selEditor == editor:
            title = self._getEditorTitle(editor)
            self.SetTitle(title)
            tabId = self._findTabIdForEditor(editor)
            self.tabContainer.setTabName(tabId, title)
        event.Skip()
    # end onEditorDirty()

    def onEditorStatusBarChanged(self, event):
        selEditor = self._getSelectedEditor()
        editor = event.getEditor()
        if selEditor == editor:
            self.statusBar.refresh()
        event.Skip()
    # end onEditorStatusBarChanged()

    def onEditorMenuBarChanged(self, event):
        selEditor = self._getSelectedEditor()
        editor = event.getEditor()
        if selEditor == editor:
            self.menuBar.refresh()
        event.Skip()
    # end onEditorMenuBarChanged()

    def onEditorToolBarChanged(self, event):
        selEditor = self._getSelectedEditor()
        editor = event.getEditor()
        if selEditor == editor:
            self.toolBar.refresh()
        event.Skip()
    # end onEditorToolBarChanged()

    def onEditorClosing(self, editor):
        u"""Returns True or False based on dirty status of editor
        and user input.  Returns False if the close should be veto'd.""" #$NON-NLS-1$
        if editor.isDirty():
            rval = ZShowYesNoCancelMessage(self, _extstr(u"editorwin.SaveDocumentMessage") % editor.getTitle(), _extstr(u"editorwin.SaveDocument")) #$NON-NLS-2$ #$NON-NLS-1$
            if rval == wx.ID_CANCEL:
                return False
            elif rval == wx.ID_YES:
                editor.save()
            elif rval == wx.ID_NO:
                pass
        return True
    # end onEditorClosing()

    def onToolBarResize(self, event):
        self.toolBarParent.Layout()
        event.Skip()
    # end onToolBarResize()

    def onClose(self, event):
        if self.close():
            global EDITOR_WINDOW
            EDITOR_WINDOW = None
            event.Skip()
        else:
            event.Veto()
    # end onClose()

    def onTabClosing(self, tabId):
        u"""Should return True to prevent the tab from being closed.""" #$NON-NLS-1$
        editor = self._findEditorByTabId(tabId)
        cancelClose = not self.onEditorClosing(editor)
        if not cancelClose:
            editor.destroy()
        return cancelClose
    # end onTabClosing()

    def onTabClosed(self, tabId):
        editor = self._findEditorByTabId(tabId)
        if editor is not None:
            del self.tabToEditorMap[tabId]
            self.editors.remove(editor)

        if len(self.editors) == 0:
            self.Close()
    # end onTabClosed()

    def onTabSelectionChanged(self, fromTabId, toTabId): #@UnusedVariable
        editor = self._findEditorByTabId(toTabId)
        if editor is not None:
            self.SetTitle(self._getEditorTitle(editor))
            self._updateMenuBar(editor)
            self._updateToolBar(editor)
            self._updateStatusBar(editor)
    # end onTabSelectionChanged()

    def _updateMenuBar(self, editor):
        menuBarModel = editor.getMenuBarModel()
        menuContext = editor.getMenuActionContext()
        contentProvider = ZModelBasedMenuContentProvider(menuBarModel, menuContext)
        eventHandler = ZModelBasedMenuEventHandler(menuBarModel, menuContext)
        if self.menuBar is None:
            self.menuBar = ZMenuBar(self, contentProvider, eventHandler)
            self.SetMenuBar(self.menuBar)
            self.Layout()
        else:
            self.menuBar.setContentProvider(contentProvider, eventHandler)
    # end _updateMenuBar()

    def _updateToolBar(self, editor):
        toolBarModel = editor.getToolBarModel()
        toolContext = editor.getToolBarActionContext()
        contentProvider = ZModelBasedToolBarContentProvider(toolBarModel, toolContext)
        eventHandler = ZModelBasedToolBarEventHandler(toolBarModel, toolContext)
        self.toolBar.setContentProvider(contentProvider, eventHandler)
        self.Layout()
    # end _updateToolBar()

    def _updateStatusBar(self, editor):
        statusBarModel = editor.getStatusBarModel()
        provider = ZStatusBarModelBasedContentProvider(statusBarModel)
        if self.statusBar is None:
            self.statusBar = ZStatusBar(self, provider)
            self.SetStatusBar(self.statusBar)
            self.Layout()
        else:
            self.statusBar.setContentProvider(provider)
            self.statusBar.refresh()
    # end _updateStatusBar()
    
    def _getEditorTitle(self, editor):
        title = editor.getTitle()
        if not title:
            title = u"(%s)" % _extstr(u"editorwin.No_Title") #$NON-NLS-1$ #$NON-NLS-2$
        if editor.isDirty():
            title = u"* " + title #$NON-NLS-1$
        return title
    # end _getEditorTitle()

# end _ZEditorWindow
