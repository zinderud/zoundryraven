from zoundry.appframework.constants import IZAppExtensionPoints
from zoundry.appframework.exceptions import ZAppFrameworkException
from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.models.ui.widgets.menudefs import ZMenuGroupDef
from zoundry.appframework.models.ui.widgets.menudefs import ZMenuItemDef
from zoundry.appframework.ui.widgets.controls.common.menu.menu import ZMenu
from zoundry.appframework.ui.widgets.controls.common.menu.menuimpl import ZActiveCallbackMenuNode
from zoundry.appframework.ui.widgets.controls.common.menu.menuimpl import ZActiveMenuNode
from zoundry.appframework.ui.widgets.controls.common.menu.menuimpl import ZActiveModelBasedMenuContentProvider
from zoundry.appframework.ui.widgets.controls.common.menu.menuimpl import ZActiveModelBasedMenuEventHandler
from zoundry.appframework.ui.widgets.controls.common.menu.menuimpl import ZHiddenRootMenuNode
from zoundry.base.exceptions import ZException

# ------------------------------------------------------------------------------
# A content provider that uses a ZMenuBarModel.
# ------------------------------------------------------------------------------
class ZModelBasedMenuContentProvider(ZActiveModelBasedMenuContentProvider):

    def __init__(self, model, menuContext):
        self.model = model

        ZActiveModelBasedMenuContentProvider.__init__(self, self.model.getRootNode(), menuContext)
    # end __init__()

# end ZModelBasedMenuContentProvider


# ------------------------------------------------------------------------------
# An event handler that uses a ZMenuBarModel.
# ------------------------------------------------------------------------------
class ZModelBasedMenuEventHandler(ZActiveModelBasedMenuEventHandler):

    def __init__(self, model, menuContext):
        self.model = model

        ZActiveModelBasedMenuEventHandler.__init__(self, menuContext)
    # end __init__()

# end ZModelBasedMenuContentProvider


# ------------------------------------------------------------------------------
# A model that represents a menu bar.
# ------------------------------------------------------------------------------
class ZMenuBarModel:

    def __init__(self):
        self.rootNode = ZHiddenRootMenuNode()
        self.menuIdToNodeMap = {}
        self.nextMenuId = 0
        self.actionRegistry = getApplicationModel().getActionRegistry()
    # end __init__()

    def _getNextMenuId(self):
        self.nextMenuId = self.nextMenuId + 1
        return self.nextMenuId
    # end _getNextMenuId()

    def _getMenuNode(self, menuId):
        if menuId in self.menuIdToNodeMap:
            return self.menuIdToNodeMap[menuId]
        raise ZAppFrameworkException(u"No menu found with id '%s'." % unicode(menuId)) #$NON-NLS-1$
    # end _getMenuNode()

    def _addMenuNode(self, node, parentId):
        parentNode = self.rootNode
        if parentId is not None:
            parentNode = self._getMenuNode(parentId)
        parentNode.addChild(node)
        menuId = self._getNextMenuId()
        self.menuIdToNodeMap[menuId] = node
        return menuId
    # end _addMenuNode()

    def addMenu(self, name, gravity, parentId = None):
        u"""addMenu(string, int, menuId?) -> menuId
        Adds a menu to the model.  This menu can be at the root
        (when parentId is None) or it can be a sub-menu of an
        existing menu.""" #$NON-NLS-1$
        menuNode = ZActiveMenuNode(name, name, None, False, False, False, gravity, None)
        return self._addMenuNode(menuNode, parentId)
    # end addMenu()

    def addMenuItemWithActionId(self, gravity, actionId, parentId = None):
        u"""addMenuItemWithActionId(int, id, menuId?) -> menuId
        Adds a menu item to an existing menu and
        returns the ID of the new menu item.  The
        action to use will be looked up from the
        action registry using the given action id.""" #$NON-NLS-1$
        action = self.actionRegistry.findAction(actionId)
        if action is None:
            raise ZException(u"No action with ID %s is registered." % actionId) #$NON-NLS-1$
        menuId = self.addMenuItemWithAction(action.getDisplayName(), gravity, action, parentId)
        return menuId
    # end addMenuItemWithActionId()

    def addMenuItemWithAction(self, name, gravity, action, parentId = None):
        u"""addMenuItem(string, int, IZMenuAction, menuId) -> menuId
        Adds a menu item to an existing menu and returns
        the ID of the new menu item.""" #$NON-NLS-1$
        menuNode = ZActiveMenuNode(name, name, None, False, False, False, gravity, action)
        menuId = self._addMenuNode(menuNode, parentId)
        self.setMenuItemDescription(menuId, action.getDescription())
        return menuId
    # end addMenuItemWithAction()

    def addMenuItemWithCallback(self, name, gravity, callback, parentId = None):
        u"""addMenuItem(string, int, method, menuId) -> menuId
        Adds a menu item to an existing menu and returns
        the ID of the new menu item.""" #$NON-NLS-1$
        menuNode = ZActiveCallbackMenuNode(name, name, None, False, False, False, gravity, True, True, callback)
        return self._addMenuNode(menuNode, parentId)
    # end addMenuItemWithAction()

    def addSeparator(self, gravity, parentId = None):
        menuNode = ZActiveCallbackMenuNode(u"SEPARATOR", None, None, True, False, False, gravity, True, True, None) #$NON-NLS-1$
        return self._addMenuNode(menuNode, parentId)
    # end addSeparator()

    def setMenuItemName(self, menuId, name):
        node = self._getMenuNode(menuId)
        node.setName(name)
    # end setMenuItemName()

    def setMenuItemDescription(self, menuId, description):
        node = self._getMenuNode(menuId)
        node.setDescription(description)
    # end setMenuItemDescription()

    def setMenuItemBitmap(self, menuId, bitmap):
        node = self._getMenuNode(menuId)
        node.setBitmap(bitmap)
    # end setMenuItemBitmap()

    def setMenuItemBold(self, menuId, boldFlag):
        node = self._getMenuNode(menuId)
        node.setBold(boldFlag)
    # end setMenuItemBold()

    def setMenuItemCheckbox(self, menuId, checkboxFlag):
        node = self._getMenuNode(menuId)
        node.setCheckboxItem(checkboxFlag)
    # end setMenuItemCheckbox()

    def setMenuItemParameters(self, menuId, params):
        node = self._getMenuNode(menuId)
        node.action.setParameters(params)
    # end setMenuItemParameters()

    def getRootNode(self):
        return self.rootNode
    # end getRootNode()

# end ZMenuBarModel


# ------------------------------------------------------------------------------
# Alias for the menu bar model.
# ------------------------------------------------------------------------------
class ZMenuModel(ZMenuBarModel):

    def __init__(self):
        ZMenuBarModel.__init__(self)
    # end __init__()

# end ZMenuModel


# ------------------------------------------------------------------------------
# Extends the menu model in order to add plugin awareness.  This model will
# automatically add nodes in the model based on plugin contributions.
# ------------------------------------------------------------------------------
class ZPluginMenuBarModel(ZMenuBarModel):

    def __init__(self, menuPluginId):
        self.menuPluginId = menuPluginId
        self.pluginsLoaded = False
        self.groupIdToMenuIdMap = {}

        ZMenuBarModel.__init__(self)
    # end __init__()

    def setMenuItemPluginId(self, menuId, pluginId):
        self.groupIdToMenuIdMap[pluginId] = menuId
    # end setMenuItemPluginId()

    # Override the getter - if the information from the plugins has not yet
    # been loaded, load that information here.
    def getRootNode(self):
        if not self.pluginsLoaded:
            self._createNodesFromPlugins()

        return self.rootNode
    # end getRootNode()

    def _createNodesFromPlugins(self):
        registry = getApplicationModel().getPluginRegistry()
        groupExtensions = registry.getExtensions(IZAppExtensionPoints.ZEP_ZOUNDRY_CORE_MENUGROUP)
        groupExtensionDefs = map(ZMenuGroupDef, groupExtensions)
        for groupExtensionDef in groupExtensionDefs:
            self._createGroupNode(groupExtensionDef)

        menuExtensions = registry.getExtensions(IZAppExtensionPoints.ZEP_ZOUNDRY_CORE_MENUITEM)
        menuExtensionDefs = map(ZMenuItemDef, menuExtensions)
        for menuExtensionDef in menuExtensionDefs:
            self._createMenuNode(menuExtensionDef)

        self.pluginsLoaded = True
    # end _createNodesFromPlugins()

    def _createGroupNode(self, groupExtensionDef):
        groupId = groupExtensionDef.getParent()
        if groupId == self.menuPluginId or groupId in self.groupIdToMenuIdMap:
            groupMenuId = None
            if groupId in self.groupIdToMenuIdMap:
                groupMenuId = self.groupIdToMenuIdMap[groupId]
            menuId = self.addMenu(groupExtensionDef.getName(), groupExtensionDef.getGravity(), groupMenuId)
            self.groupIdToMenuIdMap[groupExtensionDef.getId()] = menuId
            self.setMenuItemDescription(menuId, groupExtensionDef.getDescription())
            self.setMenuItemBitmap(menuId, groupExtensionDef.loadIcon())
    # end _createGroupNode()

    def _createMenuNode(self, menuExtensionDef):
        groupId = menuExtensionDef.getGroup()
        if groupId == self.menuPluginId or groupId in self.groupIdToMenuIdMap:
            groupMenuId = None
            if groupId in self.groupIdToMenuIdMap:
                groupMenuId = self.groupIdToMenuIdMap[groupId]

            gravity = menuExtensionDef.getGravity()
            # Short return for separators
            if menuExtensionDef.getType() == ZMenuItemDef.TYPE_SEPARATOR:
                self.addSeparator(gravity, groupMenuId)
                return

            name = menuExtensionDef.getName()
            action = menuExtensionDef.createMenuItem()
            menuId = self.addMenuItemWithAction(name, gravity, action, groupMenuId)
            bitmap = menuExtensionDef.loadIcon()
            self.setMenuItemBitmap(menuId, bitmap)
            self.setMenuItemBold(menuId, menuExtensionDef.isBold())
            self.setMenuItemDescription(menuId, menuExtensionDef.getDescription())
            if menuExtensionDef.getType() == ZMenuItemDef.TYPE_CHECKBOX:
                self.setMenuItemCheckbox(menuId, True)
            self.setMenuItemParameters(menuId, menuExtensionDef.getParameters())
    # end _createMenuNode()

# end ZPluginMenuBarModel


# ------------------------------------------------------------------------------
# Alias for the menu bar model.
# ------------------------------------------------------------------------------
class ZPluginMenuModel(ZPluginMenuBarModel):

    def __init__(self, *args, **kw):
        ZPluginMenuBarModel.__init__(self, *args, **kw)
    # end __init__()

# end ZPluginMenuModel

# ------------------------------------------------------------------------------
# Convenience class for creating model based menus.
# ------------------------------------------------------------------------------
class ZModelBasedMenu(ZMenu):
    
    def __init__(self, model, context, parent):
        provider = ZModelBasedMenuContentProvider(model, context)
        eventHandler = ZModelBasedMenuEventHandler(model, context)
        ZMenu.__init__(self, parent, model.getRootNode(), provider, eventHandler)
    # end __init__()

# end ZModelBasedMenu
