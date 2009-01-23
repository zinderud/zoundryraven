from zoundry.appframework.exceptions import ZAppFrameworkException
from zoundry.appframework.global_services import getResourceRegistry
from zoundry.appframework.messages import _extstr
from zoundry.appframework.ui.util.fontutil import getDefaultFontBold
import wx

# ---------------------------------------------------------------------------------------
# An interface that must be implemented by menu content providers.  This interface
# provides the menu with the data it needs to create the actual menu.
# ---------------------------------------------------------------------------------------
class IZMenuContentProvider:

    def getMenuNodes(self, parent):
        u"Returns a list of menu item nodes that should be displayed for the given parent." #$NON-NLS-1$
    # end getMenuNodes()

    def getMenuNodeName(self, menuNode):
        u"Returns the name of the menu item node." #$NON-NLS-1$
    # end getMenuNodeName()

    def getMenuNodeDescription(self, menuNode):
        u"Returns the description of the menu item node." #$NON-NLS-1$
    # end getMenuNodeDescription()

    def getMenuNodeBitmap(self, menuNode):
        u"Returns the image to use for this menu item node." #$NON-NLS-1$
    # end getMenuNodeBitmap()

    def isSeparator(self, menuNode):
        u"Returns True if the menu item node is, in fact, a simple separator." #$NON-NLS-1$
    # end isSeparator()

    def isMenuGroup(self, menuNode):
        u"Returns True if the menu item node is a group." #$NON-NLS-1$
    # end isMenuGroup()

    def isMenuItem(self, menuNode):
        u"Returns True if the menu item node is an item." #$NON-NLS-1$
    # end isMenuItem()

    def isCheckboxMenuItem(self, menuNode):
        u"Returns True if the item is a checkbox menu item." #$NON-NLS-1$
    # end isCheckboxMenuItem()

    def isEnabled(self, menuNode):
        u"Returns True if the item is enabled." #$NON-NLS-1$
    # end isEnabled()

    def isVisible(self, menuNode):
        u"Returns True if the item is visible." #$NON-NLS-1$
    # end isVisible()

    def isBold(self, menuNode):
        u"Returns True if the item is bold." #$NON-NLS-1$
    # end isBold()
    
    def isChecked(self, menuNode):
        u"""Returns True if the item is checked.  Note that this
        method can also return None to indicate that the
        content provider makes no claim about the checked
        status of the node (the menu should handle it).""" #$NON-NLS-1$
    # end isChecked()

# end IZMenuContentProvider


# ---------------------------------------------------------------------------------------
# An interface that must be implemented by menu event handlers.  A menu event handler is
# used by the menu to run some sort of action when a menu is clicked.
# ---------------------------------------------------------------------------------------
class IZMenuEventHandler:

    def onMenuClick(self, menuNode):
        u"Called on the event handler when a menu item is clicked." #$NON-NLS-1$
    # end onMenuClick()
    
    def onCheckMenuClick(self, menuNode, checked):
        u"Called on the event handler when a checkable menu item is clicked." #$NON-NLS-1$
    # end onCheckMenuClick()

# end IZMenuEventHandler


# ---------------------------------------------------------------------------------------
# The menu bar uses instances of this class internally in order to model the menu
# structure.  It wraps whatever menu item object is returned by the menu bar content
# provider.
# ---------------------------------------------------------------------------------------
class ZMenuItem(wx.MenuItem):

    def __init__(self, parent, menuNode, contentProvider, eventHandler):
        self.menu = parent
        self.menuNode = menuNode
        self.contentProvider = contentProvider
        self.eventHandler = eventHandler
        self.menuId = wx.NewId()

        # Get all of the params for the wx.MenuItem c'tor.
        name = self.contentProvider.getMenuNodeName(menuNode)
        helpStr = self.contentProvider.getMenuNodeDescription(menuNode)
        if not helpStr:
            helpStr = u"" #$NON-NLS-1$
        kind = wx.ITEM_NORMAL
        if self.contentProvider.isCheckboxMenuItem(menuNode):
            kind = wx.ITEM_CHECK

        # Construct the wx menu item.
        wx.MenuItem.__init__(self, parent, self.menuId, name, helpStr, kind)

        if not self.contentProvider.isCheckboxMenuItem(menuNode):
            bitmap = self.contentProvider.getMenuNodeBitmap(menuNode)
            if bitmap is None:
                bitmap = getResourceRegistry().getBitmap(u"images/common/menu/trans.png") #$NON-NLS-1$
            self.SetBitmap(bitmap)
    # end __init__()

    def getMenuNode(self):
        return self.menuNode
    # end getMenuNode()
    
    def isChecked(self):
        return self.menu.IsChecked(self.menuId)
    # end isChecked()
    
    def check(self, checked = True):
        self.menu.Check(self.menuId, checked)
    # end check()

    def onClicked(self, event):
        if self.eventHandler:
            if self.IsCheckable():
                self.eventHandler.onCheckMenuClick(self.getMenuNode(), self.isChecked())
            else:
                self.eventHandler.onMenuClick(self.getMenuNode())
        event.Skip()
    # end onClicked()

    def getParentWindow(self):
        return self._findParentWindow()
    # end getParentWindow()

    def _findParentWindow(self):
        menu = self.GetMenu()
        if menu is None:
            raise ZAppFrameworkException(_extstr(u"menu.MissingParentForMenuItemError")) #$NON-NLS-1$
        return menu.getParentWindow()
    # end _findParentWindow()

    def refresh(self):
        self.Enable(self.contentProvider.isEnabled(self.menuNode))
        checked = self.contentProvider.isChecked(self.menuNode)
        if checked is not None:
            self.check(checked)
    # end refresh()

# end ZMenuBar()


# ---------------------------------------------------------------------------------------
# A class that implements a WX menu separator.
# ---------------------------------------------------------------------------------------
class ZMenuSeparator(wx.MenuItem):

    def __init__(self, menuNode, parent):
        self.menuNode = menuNode

        wx.MenuItem.__init__(self, parent, wx.ID_SEPARATOR)
    # end __init__()

    # Can't click on a separator... :)  But we'll no-op it just in case.
    def onClicked(self, event):
        event.Skip()
    # end onClicked()
    
    def refresh(self):
        pass
    # end refresh()

# end ZMenuSeparator


# ---------------------------------------------------------------------------------------
# A class that implements a WX menu from a IZMenuContentProvider.
# ---------------------------------------------------------------------------------------
class ZMenu(wx.Menu):

    # Note: the parent param should be the frame or widget that is popping up the menu.
    def __init__(self, parent, menuNode, contentProvider, eventHandler):
        self.parent = parent
        self.menuNode = menuNode
        self.contentProvider = contentProvider
        self.eventHandler = eventHandler
        self.idToMenuItemMap = {}

        wx.Menu.__init__(self)

        self._buildMenu()
    # end __init__()

    def getMenuNode(self):
        return self.menuNode
    # end getMenuNode()

    def _buildMenu(self):
        for menuNode in self._getMenuNodes():
            if self.contentProvider.isSeparator(menuNode):
                menuItem = ZMenuSeparator(menuNode, self)
                menuItemId = self.AppendItem(menuItem).GetId()
                self.idToMenuItemMap[menuItemId] = menuItem
            elif self.contentProvider.isMenuGroup(menuNode):
                if self.contentProvider.isVisible(menuNode):
                    submenu = ZMenu(self.parent, menuNode, self.contentProvider, self.eventHandler)
                    name = self.contentProvider.getMenuNodeName(menuNode)
                    helpStr = self.contentProvider.getMenuNodeDescription(menuNode)
                    menuItem = self.AppendMenu(wx.NewId(), name, submenu, helpStr)
                    menuItemId = menuItem.GetId()
                    self.idToMenuItemMap[menuItemId] = submenu
                    self.Enable(menuItemId, self.contentProvider.isEnabled(menuNode))
            else:
                if self.contentProvider.isVisible(menuNode):
                    menuItem = ZMenuItem(self, menuNode, self.contentProvider, self.eventHandler)
                    if self.contentProvider.isBold(menuNode):
                        menuItem.SetFont(getDefaultFontBold())
                    menuItemId = self.AppendItem(menuItem).GetId()
                    self.idToMenuItemMap[menuItemId] = menuItem
                    self._bindMenuItem(menuItem)
                    self.Enable(menuItemId, self.contentProvider.isEnabled(menuNode))
                    if self.contentProvider.isChecked(menuNode):
                        self.Check(menuItemId, True)
    # end _buildMenu()

    def _bindMenuItem(self, menuItem):
        self.parent.Bind(wx.EVT_MENU, menuItem.onClicked, menuItem)
    # end _bindMenuItem()

    def _getMenuNodes(self):
        nodes = self.contentProvider.getMenuNodes(self.menuNode)
        if nodes is None:
            nodes = []
        return nodes
    # end getMenuNodes()

    def getParentWindow(self):
        return self.parent
    # end getParentWindow()
    
    def refresh(self):
        # FIXME (EPW) refresh should handle new menu items/menus
        for menuItem in self.GetMenuItems():
            self._updateMenuItem(menuItem)
    # end refresh()
    
    def _updateMenuItem(self, menuItem):
        menuItem = self.idToMenuItemMap[menuItem.GetId()]
        menuItem.refresh()
    # end _updateMenuItem()

# end ZMenu


# ---------------------------------------------------------------------------------------
# A class that implements a WX menu bar from a IZMenuContentProvider.
# ---------------------------------------------------------------------------------------
class ZMenuBar(wx.MenuBar):

    def __init__(self, parent, contentProvider, eventHandler):
        self.parent = parent
        self.contentProvider = contentProvider
        self.eventHandler = eventHandler

        wx.MenuBar.__init__(self)

        self._buildMenuBar()
    # end __init__()

    def setContentProvider(self, contentProvider, eventHandler):
        self.contentProvider = contentProvider
        self.eventHandler = eventHandler
        
        numMenus = self.GetMenuCount()
        # Append a dummy menu to avoid the re-layout that happens when the 
        # final menu is removed
        self.Append(ZMenu(self.parent, None, IZMenuContentProvider(), IZMenuEventHandler()), u"") #$NON-NLS-1$
        menuIdxs = range(0, numMenus)
        menuIdxs.reverse()
        for idx in menuIdxs:
            menu = self.Remove(idx)
            menu.Destroy()
            del menu
        
        self._buildMenuBar()

        # Now remove the dummy menu.
        menu = self.Remove(0)
        menu.Destroy()
        del menu
    # end setContentProvider()

    def _buildMenuBar(self):
        for menuNode in self._getMenuNodes():
            menu = ZMenu(self.parent, menuNode, self.contentProvider, self.eventHandler)
            self.Append(menu, self.contentProvider.getMenuNodeName(menuNode))
    # end _buildMenu()

    def _getMenuNodes(self):
        nodes = self.contentProvider.getMenuNodes(None)
        if nodes is None:
            nodes = []
        return nodes
    # end _getMenuNodes()

    def refresh(self):
        # FIXME (EPW) refresh should handle new menus
        for (menu, label) in self.GetMenus(): #@UnusedVariable
            menu.refresh()
    # end refresh()

# end ZMenuBar()
