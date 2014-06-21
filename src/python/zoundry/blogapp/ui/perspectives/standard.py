from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.global_services import getResourceRegistry
from zoundry.appframework.ui.actions.toolbaraction import ZToolBarActionContext
from zoundry.appframework.ui.events.toolbarevents import ZEVT_TOOLBAR_RESIZE
from zoundry.appframework.ui.widgets.controls.advanced.splitter import ZSplitterWindow
from zoundry.appframework.ui.widgets.controls.common.panel import ZTransparentPanel
from zoundry.appframework.ui.widgets.controls.common.toolbar.toolbar import ZPersistentToolBar
from zoundry.appframework.ui.widgets.controls.common.toolbar.toolbar import ZToolBar
from zoundry.appframework.ui.widgets.controls.common.toolbar.toolbarmodel import ZModelBasedToolBarContentProvider
from zoundry.appframework.ui.widgets.controls.common.toolbar.toolbarmodel import ZModelBasedToolBarEventHandler
from zoundry.appframework.ui.widgets.controls.common.toolbar.toolbarmodel import ZPluginToolBarModel
from zoundry.blogapp.constants import IZBlogAppToolBarIds
from zoundry.blogapp.constants import IZBlogAppUserPrefsKeys
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.ui.events.viewevents import ZEVT_VIEW_SELECTION_CHANGED
from zoundry.blogapp.ui.perspectives.perspective import IZPerspective
from zoundry.blogapp.ui.util.blogutil import getBlogFromIds
from zoundry.blogapp.ui.views.standard.contextinfo import ZContextInfoView
from zoundry.blogapp.ui.views.standard.navigator import ZNavigatorView
from zoundry.blogapp.ui.views.standard.toolbaractions import ZDeleteToolBarAction
from zoundry.blogapp.ui.views.standard.toolbaractions import ZDownloadToolBarAction
from zoundry.blogapp.ui.views.standard.toolbaractions import ZNewAccountToolBarAction
from zoundry.blogapp.ui.views.standard.toolbaractions import ZNewMediaStorageToolBarAction
from zoundry.blogapp.ui.views.standard.toolbaractions import ZPublishToolBarAction
from zoundry.blogapp.ui.views.standard.toolbaractions import ZViewOnlineToolBarAction
from zoundry.blogapp.ui.views.standard.toolbaractions import ZWriteToolBarAction
from zoundry.blogapp.ui.views.viewsel import IZViewSelectionTypes
import wx

# ------------------------------------------------------------------------------
# Gets a toolbar bitmap with a given name.
# ------------------------------------------------------------------------------
def getToolbarBitmap(size, toolbarName, imageName):
    return getResourceRegistry().getBitmap(u"images/perspectives/standard/toolbar/%s/%dx%d/%s.png" % (toolbarName, size, size, imageName)) #$NON-NLS-1$
# end getToolbarBitmap()


# ------------------------------------------------------------------------------
# An implementaiton of a toolbar action context that also provides access to
# the Standard Perspective's specific information, such as the current View
# Selection (IZViewSelection).
# ------------------------------------------------------------------------------
class ZStandardPerspectiveToolBarActionContext(ZToolBarActionContext):

    def __init__(self, window, viewSelection):
        self.window = window
        self.viewSelection = viewSelection
        ZToolBarActionContext.__init__(self, window)
    # end __init__()

    def getViewSelection(self):
        return self.viewSelection
    # end getViewSelection()

    def setViewSelection(self, viewSelection):
        self.viewSelection = viewSelection
    # end setViewSelection()

    def getBlog(self):
        blog = None
        if self.viewSelection is not None and self.viewSelection.getType() == IZViewSelectionTypes.BLOG_SELECTION:
            (accId, blogId) = self.viewSelection.getData()
            blog = getBlogFromIds(accId, blogId)
        elif self.viewSelection is not None and self.viewSelection.getType() == IZViewSelectionTypes.DOCUMENT_SELECTION:
            (blog, document) = self.viewSelection.getData() #@UnusedVariable
        return blog
    # end getBlog()

# end ZStandardPerspectiveToolBarActionContext


# ------------------------------------------------------------------------------
# The standard email-like perspective.  This view of the data will have a tree
# on the left side which contains the list of accounts and a section for
# unpublished posts.  When the user clicks on something in that tree, the
# right-hand side
#
# ::Notes on Events::
#   In order for the toolbar to update based on the selection that the user
#   makes, it is the responsibility of the various views to fire events that
#   the perspective can listen to.
#
#   ZEVT_VIEW_SELECTION_CHANGED:  fired when the user selects something in a
#      view.  The perspective will update/maintain its "current selection"
#      information based on this event.  If the user "un-selects" something,
#      this event will be fired, possibly with "None" as the selection.
# ------------------------------------------------------------------------------
class ZStandardPerspective(IZPerspective):

    def __init__(self):
        self.currentViewSelection = None
        self.panel = None
        self.splitterWindow = None
        self.navView = None
        self.ctxView = None
        self.sizer = None
    # end __init__()

    def destroy(self):
        self._saveLayout()

        self.navView.destroy()
        self.ctxView.destroy()
    # end destroy()

    def createUIPanel(self, parent):
        self.panel = ZTransparentPanel(parent, wx.ID_ANY)
        self.splitterWindow = ZSplitterWindow(self.panel)

        self._createToolBar(self.panel)
        self._createNavigatorView(self.splitterWindow)
        self._createContextInfoView(self.splitterWindow)

        self._doSplit()

        self._bindViewEvents()

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.toolBar, 0, wx.EXPAND)
        self.sizer.Add(self.toolBarStaticLine, 0, wx.EXPAND)
        self.sizer.Add(self.splitterWindow, 1, wx.EXPAND | wx.ALL, 5)

        self.panel.SetAutoLayout(True)
        self.panel.SetSizer(self.sizer)

        self.panel.Layout()
        self._restoreLayout()
        return self.panel
    # end createUI()

    def _doSplit(self):
        self.splitterWindow.SplitVertically(self.navView, self.ctxView)
        self.splitterWindow.SetMinimumPaneSize(100)
        self.splitterWindow.SetSashSize(8)
        self.splitterWindow.SetSashGravity(0.0)
    # end _doSplit()

    def _createToolBar(self, parent):
        self.toolBarModel = self._createToolBarModel()
        self.toolBarContext = ZStandardPerspectiveToolBarActionContext(parent, self.currentViewSelection)
        contentProvider = ZModelBasedToolBarContentProvider(self.toolBarModel, self.toolBarContext)
        eventHandler = ZModelBasedToolBarEventHandler(self.toolBarModel, self.toolBarContext)
        self.toolBar = ZPersistentToolBar(self._getUserPrefsKey() + u".toolbar", contentProvider, eventHandler, parent, ZToolBar.STYLE_SHOW_TEXT) #$NON-NLS-1$
        self.toolBarStaticLine = wx.StaticLine(parent, wx.ID_ANY)
    # end _createToolBar()

    def _createToolBarModel(self):
        model = ZPluginToolBarModel(IZBlogAppToolBarIds.ZID_STANDARD_PERSPECTIVE_TOOLBAR)
        model.setDefaultToolSize(24)

        # 'Write' Tool
        toolId = model.addItemWithAction(_extstr(u"standard.Write"), 1, ZWriteToolBarAction()) #$NON-NLS-1$
        model.addToolBitmap(toolId, 24, getToolbarBitmap(24, u"file", u"write"))  #$NON-NLS-2$ #$NON-NLS-1$
        model.addToolBitmap(toolId, 32, getToolbarBitmap(32, u"file", u"write"))  #$NON-NLS-2$ #$NON-NLS-1$
        model.addToolDisabledBitmap(toolId, 24, getToolbarBitmap(24, u"file", u"write_disabled")) #$NON-NLS-1$ #$NON-NLS-2$
        model.addToolDisabledBitmap(toolId, 32, getToolbarBitmap(32, u"file", u"write_disabled")) #$NON-NLS-1$ #$NON-NLS-2$
        model.setToolDescription(toolId, _extstr(u"standard.Author_some_new_content_")) #$NON-NLS-1$

        # 'New Account' Tool
        toolId = model.addItemWithAction(_extstr(u"standard.AddAccount"), 3, ZNewAccountToolBarAction()) #$NON-NLS-1$
        model.addToolBitmap(toolId, 24, getToolbarBitmap(24, u"file", u"addAccount"))  #$NON-NLS-2$ #$NON-NLS-1$
        model.addToolBitmap(toolId, 32, getToolbarBitmap(32, u"file", u"addAccount"))  #$NON-NLS-2$ #$NON-NLS-1$
        model.setToolDescription(toolId, _extstr(u"standard.AddAccountDescriton")) #$NON-NLS-1$

        # 'New Storage' Tool
        toolId = model.addItemWithAction(_extstr(u"standard.AddStorage"), 3, ZNewMediaStorageToolBarAction()) #$NON-NLS-1$
        model.addToolBitmap(toolId, 24, getToolbarBitmap(24, u"file", u"addStorage"))  #$NON-NLS-2$ #$NON-NLS-1$
        model.addToolBitmap(toolId, 32, getToolbarBitmap(32, u"file", u"addStorage"))  #$NON-NLS-2$ #$NON-NLS-1$
        model.setToolDescription(toolId, _extstr(u"standard.AddStorageDescription")) #$NON-NLS-1$

        model.addSeparator(10)

        # 'Publish' Tool
        toolId = model.addItemWithAction(_extstr(u"standard.Publish"), 15, ZPublishToolBarAction()) #$NON-NLS-2$ #$NON-NLS-3$ #$NON-NLS-1$
        model.addToolBitmap(toolId, 24, getToolbarBitmap(24, u"api", u"publish"))  #$NON-NLS-2$ #$NON-NLS-1$
        model.addToolBitmap(toolId, 32, getToolbarBitmap(32, u"api", u"publish"))  #$NON-NLS-2$ #$NON-NLS-1$
        model.addToolDisabledBitmap(toolId, 24, getToolbarBitmap(24, u"api", u"publish_disabled")) #$NON-NLS-1$ #$NON-NLS-2$
        model.addToolDisabledBitmap(toolId, 32, getToolbarBitmap(32, u"api", u"publish_disabled")) #$NON-NLS-1$ #$NON-NLS-2$
        model.setToolDescription(toolId, _extstr(u"standard.Publish_some_content_")) #$NON-NLS-1$

        # 'Download' Tool
        toolId = model.addDropDownItemWithAction(_extstr(u"standard.Download"), 20, ZDownloadToolBarAction()) #$NON-NLS-2$ #$NON-NLS-3$ #$NON-NLS-1$
        model.addToolBitmap(toolId, 24, getToolbarBitmap(24, u"api", u"download"))  #$NON-NLS-2$ #$NON-NLS-1$
        model.addToolBitmap(toolId, 32, getToolbarBitmap(32, u"api", u"download"))  #$NON-NLS-2$ #$NON-NLS-1$
        model.addToolDisabledBitmap(toolId, 24, getToolbarBitmap(24, u"api", u"download_disabled")) #$NON-NLS-1$ #$NON-NLS-2$
        model.addToolDisabledBitmap(toolId, 32, getToolbarBitmap(32, u"api", u"download_disabled")) #$NON-NLS-1$ #$NON-NLS-2$
        model.setToolDescription(toolId, _extstr(u"standard.Download_content_")) #$NON-NLS-1$

        # 'View (online)' Tool
        toolId = model.addItemWithAction(_extstr(u"standard.ViewOnline"), 25, ZViewOnlineToolBarAction()) #$NON-NLS-1$
        model.addToolBitmap(toolId, 24, getToolbarBitmap(24, u"api", u"viewOnline"))  #$NON-NLS-2$ #$NON-NLS-1$
        model.addToolBitmap(toolId, 32, getToolbarBitmap(32, u"api", u"viewOnline"))  #$NON-NLS-2$ #$NON-NLS-1$
        model.addToolDisabledBitmap(toolId, 24, getToolbarBitmap(24, u"api", u"viewOnline_disabled")) #$NON-NLS-1$ #$NON-NLS-2$
        model.addToolDisabledBitmap(toolId, 32, getToolbarBitmap(32, u"api", u"viewOnline_disabled")) #$NON-NLS-1$ #$NON-NLS-2$
        model.setToolDescription(toolId, _extstr(u"standard.ViewOnlineDescription")) #$NON-NLS-1$

        model.addSeparator(50)

        # 'Delete' Tool
        toolId = model.addItemWithAction(_extstr(u"standard.Delete"), 55, ZDeleteToolBarAction()) #$NON-NLS-2$ #$NON-NLS-3$ #$NON-NLS-1$
        model.addToolBitmap(toolId, 24, getToolbarBitmap(24, u"file", u"delete"))  #$NON-NLS-2$ #$NON-NLS-1$
        model.addToolBitmap(toolId, 32, getToolbarBitmap(32, u"file", u"delete"))  #$NON-NLS-2$ #$NON-NLS-1$
        model.addToolDisabledBitmap(toolId, 24, getToolbarBitmap(24, u"file", u"delete_disabled")) #$NON-NLS-1$ #$NON-NLS-2$
        model.addToolDisabledBitmap(toolId, 32, getToolbarBitmap(32, u"file", u"delete_disabled")) #$NON-NLS-1$ #$NON-NLS-2$
        model.setToolDescription(toolId, _extstr(u"standard.DeleteDescription")) #$NON-NLS-1$

        return model
    # end _createToolBarModel()

    def _createContextInfoView(self, parent):
        self.ctxView = ZContextInfoView(parent)
    # end _createContextInfoView()

    def _createNavigatorView(self, parent):
        self.navView = ZNavigatorView(parent)
    # end _createNavigatorView()

    def _bindViewEvents(self):
        self.toolBar.Bind(ZEVT_TOOLBAR_RESIZE, self.onToolBarResize, self.toolBar)
        ZEVT_VIEW_SELECTION_CHANGED(self.navView, self.onViewSelectionChanged)
    # end _bindViewEvents()

    def onToolBarResize(self, event):
        self.panel.Layout()
        self.panel.Refresh()
        event.Skip()
    # end onToolBarResize()

    def onViewSelectionChanged(self, event):
        self.toolBarContext.setViewSelection(event.getSelection())
        self.toolBar.refresh()
        event.Skip()
    # end onViewSelectionChanged()

    def _saveLayout(self):
        if self.panel.IsShown():
            key = self._getUserPrefsKey() + u".sash-width" #$NON-NLS-1$
            userPrefs = getApplicationModel().getUserProfile().getPreferences()
            userPrefs.setUserPreference(key, self.splitterWindow.GetSashPosition())
    # end _saveLayout()

    def _restoreLayout(self):
        key = self._getUserPrefsKey() + u".sash-width" #$NON-NLS-1$
        userPrefs = getApplicationModel().getUserProfile().getPreferences()
        sashPos = userPrefs.getUserPreferenceInt(key, 200)
        self.splitterWindow.SetSashPosition(sashPos)
    # end _restoreLayout()

    def _getUserPrefsKey(self):
        return IZBlogAppUserPrefsKeys.STANDARD_PERSPECTIVE_LAYOUT
    # end _getUserPrefsKey()

# end ZStandardPerspective
