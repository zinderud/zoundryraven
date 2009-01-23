from zoundry.appframework.constants import IZAppExtensionPoints
from zoundry.appframework.exceptions import ZAppFrameworkException
from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.ui.actions.toolbaraction import ZToolBarActionContext
from zoundry.appframework.ui.widgets.controls.common.toolbar.toolbar import ZPersistentToolBar
from zoundry.appframework.ui.widgets.controls.common.toolbar.toolbar import ZToolBar
from zoundry.appframework.ui.widgets.controls.common.toolbar.toolbardef import ZToolBarItemDef
from zoundry.appframework.ui.widgets.controls.common.toolbar.toolbarimpl import ZActiveCallbackToolBarNode
from zoundry.appframework.ui.widgets.controls.common.toolbar.toolbarimpl import ZActiveNodeBasedToolBarContentProvider
from zoundry.appframework.ui.widgets.controls.common.toolbar.toolbarimpl import ZActiveNodeBasedToolBarEventHandler
from zoundry.appframework.ui.widgets.controls.common.toolbar.toolbarimpl import ZActiveToolBarNode
from zoundry.appframework.ui.widgets.controls.common.toolbar.toolbarimpl import ZToolBarSeparatorNode
from zoundry.base.util.types.list import ZDefaultListComparator
from zoundry.base.util.types.list import ZSortedList
from zoundry.base.util.types.list import ZSortedSet

# ------------------------------------------------------------------------------
# Compares two toolbar nodes (based on gravity).
# ------------------------------------------------------------------------------
class ZToolBarNodeComparator(ZDefaultListComparator):

    def compare(self, object1, object2):
        gravity1 = object1.getGravity()
        gravity2 = object2.getGravity()
        if gravity1 == gravity2:
            return 0
        elif gravity1 < gravity2:
            return -1
        else:
            return 1
    # end compare()

# end ZToolBarNodeComparator


# ------------------------------------------------------------------------------
# Model that can be used when creating a ZToolBar.
# ------------------------------------------------------------------------------
class ZToolBarModel:

    def __init__(self):
        comparator = ZToolBarNodeComparator()
        self.toolBarNodes = ZSortedList(comparator)
        self.toolIdToNodeMap = {}
        self.nextToolId = 0
        self.supportedSizes = ZSortedSet()
        self.defaultSize = -1
    # end __init__()

    def _getNextToolId(self):
        self.nextToolId = self.nextToolId + 1
        return self.nextToolId
    # end _getNextToolId()

    def _getToolBarNode(self, toolId):
        if toolId in self.toolIdToNodeMap:
            return self.toolIdToNodeMap[toolId]
        raise ZAppFrameworkException(u"No tool found with id '%s'." % unicode(toolId)) #$NON-NLS-1$
    # end _getToolBarNode()

    def _addToolBarNode(self, node):
        self.toolBarNodes.add(node)
        toolId = self._getNextToolId()
        self.toolIdToNodeMap[toolId] = node
        return toolId
    # end _addToolBarNode()

    def getToolBarNodes(self):
        return self.toolBarNodes
    # end getToolBarNodes()

    def getSupportedSizes(self):
        return self.supportedSizes
    # end getSupportedSizes()

    def getDefaultToolSize(self):
        return self.defaultSize
    # end getDefaultToolSize()

    def setDefaultToolSize(self, defaultSize):
        self.defaultSize = defaultSize
    # end setDefaultToolSize()

    def addSeparator(self, gravity):
        u"""addSeparator(int) -> toolId
        Adds a toolbar separator item.""" #$NON-NLS-1$
        toolBarNode = ZToolBarSeparatorNode(gravity)
        return self._addToolBarNode(toolBarNode)
    # end addSeparator()

    def addItemWithAction(self, name, gravity, action):
        u"""addItemWithAction(string, int, IZToolBarAction) -> toolId
        Adds an action-based toolbar item to the model.""" #$NON-NLS-1$
        toolBarNode = ZActiveToolBarNode(name, u"", gravity, action = action) #$NON-NLS-1$
        return self._addToolBarNode(toolBarNode)
    # end addItemWithAction()

    def addItemWithCallback(self, name, gravity, callback):
        u"""addItemWithCallback(string, int, method) -> toolId
        Adds an callback-based toolbar item to the model.""" #$NON-NLS-1$
        toolBarNode = ZActiveCallbackToolBarNode(name, u"", gravity, callback = callback) #$NON-NLS-1$
        return self._addToolBarNode(toolBarNode)
    # end addItemWithCallback()

    def addToggleItemWithAction(self, name, gravity, action):
        u"""addToggleItemWithAction(string, int, IZToolBarAction) -> toolId
        Adds a toggle-style, action-based toolbar item to
        the model.""" #$NON-NLS-1$
        toolBarNode = ZActiveToolBarNode(name, u"", gravity, isToggle = True, action = action) #$NON-NLS-1$
        return self._addToolBarNode(toolBarNode)
    # end addToggleItemWithAction()

    def addDropDownItemWithAction(self, name, gravity, action):
        u"""addToggleItemWithAction(string, int, IZToolBarAction) -> toolId
        Adds a toggle-style, action-based toolbar item to
        the model.""" #$NON-NLS-1$
        toolBarNode = ZActiveToolBarNode(name, u"", gravity, isDropDown = True, action = action) #$NON-NLS-1$
        return self._addToolBarNode(toolBarNode)
    # end addDropDownItemWithAction()

    def setToolText(self, toolId, text):
        node = self._getToolBarNode(toolId)
        node.setText(text)
    # end setToolText()

    def setToolDescription(self, toolId, description):
        node = self._getToolBarNode(toolId)
        node.setDescription(description)
    # end setToolDescription()

    def addToolBitmap(self, toolId, size, bitmap):
        node = self._getToolBarNode(toolId)
        node.addBitmap(size, bitmap)
        self.supportedSizes.add(size)
    # end addToolBitmap()

    def addToolDisabledBitmap(self, toolId, size, disabledBitmap):
        node = self._getToolBarNode(toolId)
        node.addDisabledBitmap(size, disabledBitmap)
    # end addToolDisabledBitmap()

    def addToolHoverBitmap(self, toolId, size, hoverBitmap):
        node = self._getToolBarNode(toolId)
        node.addHoverBitmap(size, hoverBitmap)
    # end addToolHoverBitmap()

    def setToolDropDownMenuModel(self, toolId, menuModel):
        node = self._getToolBarNode(toolId)
        node.setDropDownMenuModel(menuModel)
    # end setToolDropDownMenuModel()

# end ZToolBarModel


# ------------------------------------------------------------------------------
# A content provider that uses a ZToolBarModel.
# ------------------------------------------------------------------------------
class ZModelBasedToolBarContentProvider(ZActiveNodeBasedToolBarContentProvider):

    def __init__(self, model, toolBarContext):
        self.model = model

        ZActiveNodeBasedToolBarContentProvider.__init__(self, self.model.getToolBarNodes(), self.model.getDefaultToolSize(), self.model.getSupportedSizes(), toolBarContext)
    # end __init__()

# end ZModelBasedToolBarContentProvider


# ------------------------------------------------------------------------------
# An event handler that uses a ZToolBarModel.
# ------------------------------------------------------------------------------
class ZModelBasedToolBarEventHandler(ZActiveNodeBasedToolBarEventHandler):

    def __init__(self, model, toolBarContext):
        self.model = model

        ZActiveNodeBasedToolBarEventHandler.__init__(self, toolBarContext)
    # end __init__()

# end ZModelBasedToolBarEventHandler


# ------------------------------------------------------------------------------
# Extends the toolbar model in order to add plugin awareness.  This model will
# automatically add nodes in the model based on plugin contributions.
# ------------------------------------------------------------------------------
class ZPluginToolBarModel(ZToolBarModel):

    def __init__(self, toolbarPluginId):
        self.toolbarPluginId = toolbarPluginId
        self.pluginsLoaded = False

        ZToolBarModel.__init__(self)
    # end __init__()

    # Override the getter - if the information from the plugins has not yet
    # been loaded, load that information here.
    def getToolBarNodes(self):
        if not self.pluginsLoaded:
            self._createNodesFromPlugins()

        return self.toolBarNodes
    # end getToolBarNodes()

    def _createNodesFromPlugins(self):
        registry = getApplicationModel().getPluginRegistry()
        extensions = registry.getExtensions(IZAppExtensionPoints.ZEP_ZOUNDRY_CORE_TOOLBARITEM)
        extensionDefs = map(ZToolBarItemDef, extensions)
        for extensionDef in extensionDefs:
            if extensionDef.getToolBar() == self.toolbarPluginId:
                self._createNodeFromPlugin(extensionDef)

        self.pluginsLoaded = True
    # end _createNodesFromPlugins()

    def _createNodeFromPlugin(self, extensionDef):
        action = None
        text = extensionDef.getText()
        description = extensionDef.getDescription()
        gravity = extensionDef.getGravity()
        type = extensionDef.getType()
        bitmaps = extensionDef.getBitmaps()

        if type == ZToolBarItemDef.TYPE_SEPARATOR:
            self.addSeparator(gravity)
            return
        else:
            action = extensionDef.createAction()

        toolId = None
        if type == ZToolBarItemDef.TYPE_STANDARD:
            toolId = self.addItemWithAction(text, gravity, action)
        elif type == ZToolBarItemDef.TYPE_TOGGLE:
            toolId = self.addToggleItemWithAction(text, gravity, action)
        elif type == ZToolBarItemDef.TYPE_DROPDOWN:
            toolId = self.addDropDownItemWithAction(text, gravity, action)

        self.setToolDescription(toolId, description)

        for (bitmap, size, type) in bitmaps:
            if type == ZToolBarItemDef.BMP_TYPE_STANDARD:
                self.addToolBitmap(toolId, size, bitmap)
            elif type == ZToolBarItemDef.BMP_TYPE_HOVER:
                self.addToolHoverBitmap(toolId, size, bitmap)
            elif type == ZToolBarItemDef.BMP_TYPE_DISABLED:
                self.addToolDisabledBitmap(toolId, size, bitmap)
    # end _createNodeFromPlugin()

# end ZPluginToolBarModel


# ------------------------------------------------------------------------------
# Convenience class for creating a model-based toolbar.
# ------------------------------------------------------------------------------
class ZModelBasedToolBar(ZToolBar):

    def __init__(self, model, parent, style = 0):
        toolBarContext = ZToolBarActionContext(self)
        self.contentProvider = ZModelBasedToolBarContentProvider(model, toolBarContext)
        self.eventHandler = ZModelBasedToolBarEventHandler(model, toolBarContext)

        ZToolBar.__init__(self, self.contentProvider, self.eventHandler, parent, style)
    # end __init__()

# end ZModelBasedToolBar


# ------------------------------------------------------------------------------
# Convenience class for creating a model-based toolbar with persistence.
# ------------------------------------------------------------------------------
class ZPersistentModelBasedToolBar(ZPersistentToolBar):

    def __init__(self, prefsId, model, parent, style = 0, context = None):
        toolBarContext = None
        if context is not None:
            toolBarContext = context
        else:
            toolBarContext = ZToolBarActionContext(self)
        self.contentProvider = ZModelBasedToolBarContentProvider(model, toolBarContext)
        self.eventHandler = ZModelBasedToolBarEventHandler(model, toolBarContext)

        ZPersistentToolBar.__init__(self, prefsId, self.contentProvider, self.eventHandler, parent, style)
    # end __init__()

# end ZPersistentModelBasedToolBar
