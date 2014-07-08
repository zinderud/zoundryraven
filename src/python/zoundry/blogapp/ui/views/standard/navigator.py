from Queue import Queue
from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.global_services import getLoggerService
from zoundry.appframework.global_services import getResourceRegistry
from zoundry.appframework.models.ui.widgets.treemodel import ZTreeNodeBasedContentProvider
from zoundry.appframework.resources.resourceutils import ZMappedImageList
from zoundry.appframework.ui.events.commonevents import ZEVT_REFRESH
from zoundry.appframework.ui.util.uiutil import fireRefreshEvent
from zoundry.appframework.ui.widgets.controls.common.imgbutton import ZImageButton
from zoundry.appframework.ui.widgets.controls.common.menu.menu import ZMenu
from zoundry.appframework.ui.widgets.controls.common.menu.menumodel import ZModelBasedMenuContentProvider
from zoundry.appframework.ui.widgets.controls.common.menu.menumodel import ZModelBasedMenuEventHandler
from zoundry.appframework.ui.widgets.controls.tree import IZTreeViewVisitor
from zoundry.appframework.ui.widgets.controls.tree import ZTreeView
from zoundry.appframework.ui.widgets.dialogs.standarddialogs import ZShowNotYetImplementedMessage
from zoundry.blogapp.constants import IZBlogAppServiceIDs
from zoundry.blogapp.constants import IZBlogAppUserPrefsKeys
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.models.views.standard.navmodel import NODE_TYPE_ACCOUNT
from zoundry.blogapp.models.views.standard.navmodel import NODE_TYPE_BLOG
from zoundry.blogapp.models.views.standard.navmodel import NODE_TYPE_IMAGES
from zoundry.blogapp.models.views.standard.navmodel import NODE_TYPE_LINKS
from zoundry.blogapp.models.views.standard.navmodel import NODE_TYPE_POSTS
from zoundry.blogapp.models.views.standard.navmodel import NODE_TYPE_TAGS
from zoundry.blogapp.models.views.standard.navmodel import NODE_TYPE_UNPUBLISHED
from zoundry.blogapp.models.views.standard.navmodel import NODE_TYPE_DRAFTED #Vaigai-Zoundry-Raven
from zoundry.blogapp.models.views.standard.navmodel import ZNavigatorModel
from zoundry.blogapp.models.views.standard.navmodel import ZNavigatorTreeBlogNode
from zoundry.blogapp.models.views.standard.navmodel import ZNavigatorTreeNode
from zoundry.blogapp.services.accountstore.accountstore import IZAccountStoreListener
from zoundry.blogapp.services.docindex.indexevents import IZDocIndexEvent
from zoundry.blogapp.services.docindex.indexevents import IZDocumentIndexListener
from zoundry.blogapp.ui.actions.blog.blogactions import ZBlogMenuActionContext
from zoundry.blogapp.ui.dnd.blogpostdnd import ZBlogPostDataObjectInternal
from zoundry.blogapp.ui.menus.account.accountmenu import ZAccountMenuActionContext
from zoundry.blogapp.ui.menus.account.accountmenu import ZBlogAccountMenuModel
from zoundry.blogapp.ui.menus.blog.blogmenu import ZBlogMenuModel
from zoundry.blogapp.ui.util.viewutil import fireViewSelectionEvent
from zoundry.blogapp.ui.util.viewutil import fireViewUnselectionEvent
from zoundry.blogapp.ui.views.boxedview import ZBoxedView
from zoundry.blogapp.ui.views.view import IZViewIds
from zoundry.blogapp.ui.views.viewsel import IZViewSelectionTypes
from zoundry.blogapp.ui.views.viewselimpl import ZViewSelection
from zoundry.base.util.zthread import IZRunnable
from zoundry.appframework.ui.util.uiutil import fireUIExecEvent
import wx

ACCOUNT_EVENT_ADD = 0
ACCOUNT_EVENT_UPDATE = 1
ACCOUNT_EVENT_DELETE = 2

# ------------------------------------------------------------------------------
# Visitor that is called when the tree layout needs to be saved.
# ------------------------------------------------------------------------------
class ZTreeLayoutSaveVisitor(IZTreeViewVisitor):

    def visit(self, node, metaData):
        if isinstance(node, ZNavigatorTreeNode):
            node.saveLayout(metaData)
    # end visit()

# end ZTreeLayoutSaveVisitor


# ------------------------------------------------------------------------------
# Visitor that restores the navigator's selection.
# ------------------------------------------------------------------------------
class ZTreeSelectionRestoreVisitor(IZTreeViewVisitor):

    def __init__(self, navView, hashValue):
        self.navView = navView
        self.hashValue = hashValue
    # end __init__()

    def visit(self, node, metaData):
        if node.hashCode() == self.hashValue:
            treeItemId = metaData[u"id"] #$NON-NLS-1$
            self.navView.treeView.SelectItem(treeItemId, True)
            self.navView.treeView.SetFocus()
            selection = self.navView._getCurrentSelection()
            if selection:
                class ZFireViewSelectionDelayed(IZRunnable):
                    def __init__(self, navView, selection):
                        self.navView = navView
                        self.selection = selection
                    def run(self):
                        fireViewSelectionEvent(selection, self.navView)
                runnable = ZFireViewSelectionDelayed(self.navView, selection)
                fireUIExecEvent(runnable, self.navView)
    # end visit()

# end ZTreeSelectionRestoreVisitor


# ------------------------------------------------------------------------------
# Creates a view selection from the given Navigator node.
# ------------------------------------------------------------------------------
def createViewSelection(node):
    if node is None:
        return None

    if node.getType() == NODE_TYPE_ACCOUNT:
        return ZViewSelection(IZViewSelectionTypes.ACCOUNT_SELECTION, node.getAccount().getId())
    elif node.getType() == NODE_TYPE_BLOG:
        blogId = node.getBlog().getId()
        accountId = node.getBlog().getAccount().getId()
        return ZViewSelection(IZViewSelectionTypes.BLOG_SELECTION, (accountId, blogId))
    elif node.getType() == NODE_TYPE_IMAGES:
        accountId = None
        blogId = None
        if node.getParentBlog() is not None:
            blogId = node.getParentBlog().getId()
            accountId = node.getParentBlog().getAccount().getId()
        return ZViewSelection(IZViewSelectionTypes.BLOG_IMAGES_SELECTION, (accountId, blogId))
    elif node.getType() == NODE_TYPE_LINKS:
        accountId = None
        blogId = None
        if node.getParentBlog() is not None:
            blogId = node.getParentBlog().getId()
            accountId = node.getParentBlog().getAccount().getId()
        return ZViewSelection(IZViewSelectionTypes.BLOG_LINKS_SELECTION, (accountId, blogId))
    elif node.getType() == NODE_TYPE_TAGS:
        accountId = None
        blogId = None
        if node.getParentBlog() is not None:
            blogId = node.getParentBlog().getId()
            accountId = node.getParentBlog().getAccount().getId()
        return ZViewSelection(IZViewSelectionTypes.BLOG_TAGS_SELECTION, (accountId, blogId))
    elif node.getType() == NODE_TYPE_DRAFTED:#Vaigai-Zoundry-Raven pitchaimuthu
        accountId = None
        blogId = None
        if node.getParentBlog() is not None:
            blogId = node.getParentBlog().getId()
            accountId = node.getParentBlog().getAccount().getId()
        return ZViewSelection(IZViewSelectionTypes.BLOG_EDITED_SELECTION, (accountId, blogId))
    elif node.getType() == NODE_TYPE_POSTS:
        accountId = None
        blogId = None
        if node.getParentBlog() is not None:
            blogId = node.getParentBlog().getId()
            accountId = node.getParentBlog().getAccount().getId()
        return ZViewSelection(IZViewSelectionTypes.BLOG_POSTS_SELECTION, (accountId, blogId))
    elif node.getType() == NODE_TYPE_UNPUBLISHED:
        accountId = None
        blogId = None
        return ZViewSelection(IZViewSelectionTypes.BLOG_POSTS_SELECTION, (accountId, blogId))

    return None
# end createViewEvent()


# ------------------------------------------------------------------------------
# A drop target for the Navigator View.
# ------------------------------------------------------------------------------
class ZNavigatorViewDropTarget(wx.PyDropTarget):

    def __init__(self, treeView, navigator):
        self.treeView = treeView
        self.navigator = navigator
        self.selectedID = None
        self.entered = False

        wx.PyDropTarget.__init__(self)

        self.dataObj = ZBlogPostDataObjectInternal()
        self.SetDataObject(self.dataObj)
    # end __init__()

    def OnData(self, x, y, dragResult): #@UnusedVariable
        if self.GetData():
            blogId = self.dataObj.GetData()
            itemId = self._getTreeItemId(x, y)
            node = self._getTreeNode(itemId)
            self.navigator.onBlogEntryDropped(blogId, node)
        return wx.DragCopy
    # end OnData()

    def OnDrop(self, x, y): #@UnusedVariable
        self.leave()
        return True
    # end OnDrop()

    def OnEnter(self, x, y, dragResult): #@UnusedVariable
        self.enter()
        return wx.DragNone
    # end OnEnter()

    def OnLeave(self):
        self.leave()
    # end OnLeave()

    # FIXME (EPW) need to expand tree onDragOver
    def OnDragOver(self, x, y, dragResult): #@UnusedVariable
        self.enter()

        if dragResult == wx.DragMove:
            dragResult = wx.DragCopy

        itemId = self._getTreeItemId(x, y)
        if itemId is not None:
            self.treeView.SelectItem(itemId)
            node = self._getTreeNode(itemId)
            if isinstance(node, ZNavigatorTreeBlogNode):
                return dragResult
        return wx.DragNone
    # end OnDragOver()

    def enter(self):
        if not self.entered:
            # Save the currently selected tree item.
            self.selectedID = self.treeView.GetSelection()
            self.navigator.Unbind(wx.EVT_TREE_SEL_CHANGED, self.treeView)
            self.entered = True
    # end enter()

    def leave(self):
        if self.entered:
            self.treeView.SelectItem(self.selectedID)
            self.selectedID = -1
            self.navigator.Bind(wx.EVT_TREE_SEL_CHANGED, self.navigator.onSelectionChanged, self.treeView)
            self.entered = False
    # end leave()

    def _getTreeNode(self, treeItem):
        return self.treeView.GetPyData(treeItem)
    # end _getTreeNode()

    def _getTreeItemId(self, x, y):
        (itemId, flags) = self.treeView.HitTest(wx.Point(x, y))
        if flags & wx.TREE_HITTEST_ONITEMLABEL:
            return itemId
        if flags & wx.TREE_HITTEST_ONITEMBUTTON:
            return itemId
        if flags & wx.TREE_HITTEST_ONITEMICON:
            return itemId
        if flags & wx.TREE_HITTEST_ONITEMINDENT:
            return itemId
        if flags & wx.TREE_HITTEST_ONITEMRIGHT:
            return itemId
        if flags & wx.TREE_HITTEST_ONITEMSTATEICON:
            return itemId
        return None
    # end _getTreeItemId()

# end ZNavigatorViewDropTarget


# ------------------------------------------------------------------------------
# This class implements the Standard Perspective's Navigator View.  The
# Navigator View is typically docked on the left side of the Window and displays
# a tree view of the data found in the application.  The data is organized by
# Account.
# ------------------------------------------------------------------------------
class ZNavigatorView(ZBoxedView, IZAccountStoreListener, IZDocumentIndexListener):

    def __init__(self, parent):
        self.indexEventQueue = Queue()
        self.accountEventQueue = Queue()
        self.model = None

        ZBoxedView.__init__(self, parent)

        self.treeView.refresh()
        self._restoreTreeSelection()
    # end __init__()

    def getViewId(self):
        return IZViewIds.NAVIGATOR_VIEW
    # end getViewId()

    def _getHeaderBitmap(self):
        return getResourceRegistry().getBitmap(u"images/perspectives/standard/navigator/navigator.png") #$NON-NLS-1$
    # end _getHeaderBitmap()

    def _getHeaderLabel(self):
        return _extstr(u"navigator.AccountNavigator") #$NON-NLS-1$
    # end _getHeaderLabel()

    def _createHeaderWidgets(self, parent, widgetList):
        # Register for events before creating the model so that we don't miss any.
        # Register for events after init'ing WX!
        self._registerAsListener()
        self.model = ZNavigatorModel()

        # Collapse All button
        bitmap = getResourceRegistry().getBitmap(u"images/perspectives/standard/navigator/collapseAll.png") #$NON-NLS-1$
        self.collapseAllButton = ZImageButton(parent, bitmap, False, None, True)
        self.collapseAllButton.SetToolTipString(_extstr(u"navigator.CollapseAllTooltip")) #$NON-NLS-1$
        # Dashboard button
        bitmap = getResourceRegistry().getBitmap(u"images/perspectives/standard/dashboard.png") #$NON-NLS-1$
        self.dashboardButton = ZImageButton(parent, bitmap, False, None, True)
        self.dashboardButton.SetToolTipString(_extstr(u"navigator.DashboardTooltip")) #$NON-NLS-1$

        widgetList.append(self.collapseAllButton)
        widgetList.append(self.dashboardButton)
    # end _createHeaderWidgets()

    def _createContentWidgets(self, parent):
        self.treeImageList = self._createTreeImageList()
        self.treeProvider = ZTreeNodeBasedContentProvider(self.model.getNavigatorTreeRoot(), self.treeImageList)
        treeStyle = wx.NO_BORDER | wx.TR_HIDE_ROOT | wx.TR_LINES_AT_ROOT | wx.TR_SINGLE | wx.TR_HAS_BUTTONS
        self.treeView = ZTreeView(self.treeProvider, parent, style = treeStyle)
        dropTarget = ZNavigatorViewDropTarget(self.treeView, self)
        self.treeView.SetDropTarget(dropTarget)
    # end _createContentWidgets()

    def _layoutContentWidgets(self):
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.treeView, 1, wx.EXPAND)

        return box
    # end _layoutContentWidgets()

    def _createTreeImageList(self):
        registry = getResourceRegistry()
        imgList = ZMappedImageList()
        for img in [u"unpublished", u"account", u"blog", u"posts", u"links", u"images", u"tags"]: #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$ #$NON-NLS-4$ #$NON-NLS-5$ #$NON-NLS-6$ #$NON-NLS-7$ #$NON-NLS-8$
            imgList.addImage(img, registry.getBitmap(u"images/perspectives/standard/navigator/%s.png" % img)) #$NON-NLS-1$

        return imgList
    # end _createTreeImageList()

    def _bindWidgetEvents(self):
        ZBoxedView._bindWidgetEvents(self)

        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.onSelectionChanged, self.treeView)
        self.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.onItemRightClick, self.treeView)
        self.Bind(wx.EVT_BUTTON, self.onDashboardButton, self.dashboardButton)
        self.Bind(wx.EVT_BUTTON, self.onCollapseAllButton, self.collapseAllButton)
        self.Bind(ZEVT_REFRESH, self.onZoundryRefresh, self)

        wx.EVT_SET_FOCUS(self.treeView, self.onFocus)
        wx.EVT_KILL_FOCUS(self.treeView, self.onUnFocus)
    # end _bindWidgetEvents()

    def onFocus(self, event):
        selection = self._getCurrentSelection()
        if selection:
            fireViewSelectionEvent(selection, self)
        event.Skip()
    # end onFocus()

    def onUnFocus(self, event):
        selection = self._getCurrentSelection()
        if selection:
            fireViewUnselectionEvent()
        event.Skip()
    # end onUnFocus()

    def onDashboardButton(self, event):
        self.treeView.UnselectAll()
        fireViewSelectionEvent(ZViewSelection(IZViewSelectionTypes.UNPUBLISHED_ACCOUNT_SELECTION, None), self)
        event.Skip()
    # end onDashboardButton()

    def onCollapseAllButton(self, event):
        self.treeView.UnselectAll()
        self.treeView.collapseAll()
        fireViewSelectionEvent(ZViewSelection(IZViewSelectionTypes.UNPUBLISHED_ACCOUNT_SELECTION, None), self)
        event.Skip()
    # end onCollapseAllButton()

    def onItemRightClick(self, event):
        itemId = event.GetItem()
        node = self.treeView.GetPyData(itemId)
        nodeType = node.getType()
        if nodeType == NODE_TYPE_ACCOUNT:
            account = node.getAccount()
            menu = self._createAccountCtxMenu(account)
            self.PopupMenu(menu)
            menu.Destroy()
        if nodeType == NODE_TYPE_BLOG:
            blog = node.getBlog()
            menu = self._createBlogCtxMenu(blog)
            self.PopupMenu(menu)
            menu.Destroy()
        event.Skip()
    # end onItemRightClick()

    def _createAccountCtxMenu(self, account):
        menuContext = ZAccountMenuActionContext(self, account)
        menuModel = ZBlogAccountMenuModel()
        provider = ZModelBasedMenuContentProvider(menuModel, menuContext)
        eventHandler = ZModelBasedMenuEventHandler(menuModel, menuContext)
        return ZMenu(self, menuModel.getRootNode(), provider, eventHandler)
    # end _createAccountCtxMenu()

    def _createBlogCtxMenu(self, blog):
        menuContext = ZBlogMenuActionContext(self, blog)
        menuModel = ZBlogMenuModel()
        provider = ZModelBasedMenuContentProvider(menuModel, menuContext)
        eventHandler = ZModelBasedMenuEventHandler(menuModel, menuContext)
        return ZMenu(self, menuModel.getRootNode(), provider, eventHandler)
    # end _createBlogCtxMenu()

    def onSelectionChanged(self, event):
        selection = self._getCurrentSelection()
        if selection:
            fireViewSelectionEvent(selection, self)
        else:
            fireViewUnselectionEvent()
        event.Skip()
    # end _onSelectionChanged()

    def onAccountAdded(self, account):
        self.accountEventQueue.put( (ACCOUNT_EVENT_ADD, account) )
        self.model.addAccount(account)
        fireRefreshEvent(self)
    # end onAccountAdded()

    def onAccountChanged(self, account):
        self.accountEventQueue.put( (ACCOUNT_EVENT_UPDATE, account) )
        self.model.updateAccount(account)
        fireRefreshEvent(self)
    # end onAccountChange()

    def onAccountDeleted(self, account):
        self.accountEventQueue.put( (ACCOUNT_EVENT_DELETE, account) )
        self.model.removeAccount(account)
        fireRefreshEvent(self)
    # end onAccountDeleted()

    def onIndexChange(self, event):
        shouldRefresh = event.getEventType() == IZDocIndexEvent.DOCINDEX_EVENTTYPE_ADD or \
                        event.getEventType() == IZDocIndexEvent.DOCINDEX_EVENTTYPE_REMOVE
        if shouldRefresh:
            self.indexEventQueue.put(event)
            fireRefreshEvent(self)
    # end onIndexChange()

    def onBlogEntryDropped(self, blogId, node):
        getLoggerService().debug(u"Dropped blog entry '%s' onto blog node '%s'." % (blogId, node.getBlog().getId())) #$NON-NLS-1$
        ZShowNotYetImplementedMessage(self)
    # end onBlogEntryDropped()

    def onZoundryRefresh(self, event): #@UnusedVariable
        nodesToRefresh = self._getNodesToRefresh()
        self.treeView.refresh(nodesToRefresh)
    # end onZoundryRefresh()

    # Gets the list of nodes to refresh based on the current queue of index events.
    def _getNodesToRefresh(self):
        nodesToRefresh = []

        # If there are any account events, refresh the whole tree
        if not self.accountEventQueue.empty():
            # Clear out the account event queue
            while not self.accountEventQueue.empty():
                self.accountEventQueue.get()
            return None

        # If there are index events, then we can refresh only parts of the tree
        while not self.indexEventQueue.empty():
            event = self.indexEventQueue.get()
            dirtyNodes = None
            if event.getEventType() == IZDocIndexEvent.DOCINDEX_EVENTTYPE_ADD:
                if event.getDataType() == IZDocIndexEvent.DOCINDEX_DATATYPE_DOCUMENT:
                    dirtyNodes = self.model.addDocumentIDO(event.getDocumentIDO())
                elif event.getDataType() == IZDocIndexEvent.DOCINDEX_DATATYPE_IMAGE:
                    dirtyNodes = self.model.addImageIDO(event.getImageIDO())
                elif event.getDataType() == IZDocIndexEvent.DOCINDEX_DATATYPE_LINK:
                    dirtyNodes = self.model.addLinkIDO(event.getLinkIDO())
                elif event.getDataType() == IZDocIndexEvent.DOCINDEX_DATATYPE_TAG:
                    dirtyNodes = self.model.addTagIDO(event.getTagIDO())

            elif event.getEventType() == IZDocIndexEvent.DOCINDEX_EVENTTYPE_REMOVE:
                if event.getDataType() == IZDocIndexEvent.DOCINDEX_DATATYPE_DOCUMENT:
                    dirtyNodes = self.model.removeDocumentIDO(event.getDocumentIDO())
                elif event.getDataType() == IZDocIndexEvent.DOCINDEX_DATATYPE_IMAGE:
                    dirtyNodes = self.model.removeImageIDO(event.getImageIDO())
                elif event.getDataType() == IZDocIndexEvent.DOCINDEX_DATATYPE_LINK:
                    dirtyNodes = self.model.removeLinkIDO(event.getLinkIDO())
                elif event.getDataType() == IZDocIndexEvent.DOCINDEX_DATATYPE_TAG:
                    dirtyNodes = self.model.removeTagIDO(event.getTagIDO())
            if dirtyNodes is not None:
                nodesToRefresh.extend(dirtyNodes)

        return nodesToRefresh
    # end _getNodesToRefresh()

    def _getCurrentSelection(self):
        treeIDs = self.treeView.GetSelections()
        nodes = map(self.treeView.GetPyData, treeIDs)
        # Just return the 1st node - currently multi-selection is disabled.
        for node in nodes:
            return createViewSelection(node)

        return None
    # end _getCurrentSelection()

    def destroy(self):
        self._saveTreeLayout()

        self._unregisterAsListener()
    # end destroy()

    def _saveTreeLayout(self):
        visitor = ZTreeLayoutSaveVisitor()
        self.treeView.accept(visitor)
        self._saveTreeSelection()

        # Save the properties
        getApplicationModel().getUserProfile().getProperties().save()
    # end _saveTreeLayout()

    def _saveTreeSelection(self):
        nodes = self.treeView.getSelectedNodes()
        hashValue = 0
        if nodes:
            node = nodes[0]
            hashValue = node.hashCode()
        userPrefs = getApplicationModel().getUserProfile().getPreferences()
        userPrefs.setUserPreference(IZBlogAppUserPrefsKeys.NAVIGATOR_VIEW_SELECTION, unicode(hashValue))
    # end _saveTreeSelection()

    def _restoreTreeSelection(self):
        userPrefs = getApplicationModel().getUserProfile().getPreferences()
        hashValue = userPrefs.getUserPreferenceInt(IZBlogAppUserPrefsKeys.NAVIGATOR_VIEW_SELECTION, 0)
        if hashValue != 0:
            visitor = ZTreeSelectionRestoreVisitor(self, hashValue)
            self.treeView.accept(visitor)
    # end _restoreTreeSelection()

    def _registerAsListener(self):
        self._registerAsAccountListener()
        self._registerAsIndexListener()
    # end _registerAsListener()

    def _unregisterAsListener(self):
        self._unregisterAsAccountListener()
        self._unregisterAsIndexListener()
    # end _unregisterAsListener()

    def _registerAsAccountListener(self):
        engine = getApplicationModel().getEngine()
        accountStore = engine.getService(IZBlogAppServiceIDs.ACCOUNT_STORE_SERVICE_ID)
        accountStore.addListener(self)
    # end _registerAsAccountListener()

    def _unregisterAsAccountListener(self):
        engine = getApplicationModel().getEngine()
        accountStore = engine.getService(IZBlogAppServiceIDs.ACCOUNT_STORE_SERVICE_ID)
        accountStore.removeListener(self)
    # end _unregisterAsAccountListener()

    def _registerAsIndexListener(self):
        engine = getApplicationModel().getEngine()
        accountStore = engine.getService(IZBlogAppServiceIDs.DOCUMENT_INDEX_SERVICE_ID)
        accountStore.addListener(self)
    # end _registerAsIndexListener()

    def _unregisterAsIndexListener(self):
        engine = getApplicationModel().getEngine()
        accountStore = engine.getService(IZBlogAppServiceIDs.DOCUMENT_INDEX_SERVICE_ID)
        accountStore.removeListener(self)
    # end _unregisterAsIndexListener()

# end ZNavigatorView
