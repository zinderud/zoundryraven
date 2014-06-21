from zoundry.appframework.ui.actions.menuaction import ZMenuAction
from zoundry.appframework.ui.widgets.controls.common.menu.menu import IZMenuContentProvider
from zoundry.appframework.ui.widgets.controls.common.menu.menu import IZMenuEventHandler
from zoundry.base.util.types.list import ZDefaultListComparator
from zoundry.base.util.types.list import ZSortedList

# ------------------------------------------------------------------------------
# Compares two menu nodes (based on gravity).
# ------------------------------------------------------------------------------
class ZMenuNodeComparator(ZDefaultListComparator):

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

# end ZMenuNodeComparator


# -----------------------------------------------------------------------------------
# Interface for a generic menu node.  When using the ZNodeBasedMenuContentProvider
# class, the nodes that are used to create the Menu must implement this interface.
# -----------------------------------------------------------------------------------
class IZMenuNode:

    def getChildren(self):
        u"Returns the children of this node." #$NON-NLS-1$
    # end getChildren()

    def getName(self):
        u"Returns the name of this node." #$NON-NLS-1$
    # end getName()

    def getDescription(self):
        u"Returns the description of this node." #$NON-NLS-1$
    # end getDescription()

    def getBitmap(self):
        u"Returns the node bitmap." #$NON-NLS-1$
    # end getBitmap()

    def isSeparator(self):
        u"Returns True if this node is a separator." #$NON-NLS-1$
    # end isSeparator()

    def isCheckboxItem(self):
        u"Returns True if this node is a checkbox item." #$NON-NLS-1$
    # end isCheckboxItem()

    def isBold(self):
        u"Returns True if this node is bold." #$NON-NLS-1$
    # end isBold()

# end IZMenuNode


# -----------------------------------------------------------------------------------
# Interface for a generic menu node.  When using the ZModelBasedMenuEventHandler
# class, the nodes that are used to create the Menu must implement this interface.
# Typically, an implementation of this interface will own an instance of an
# IZMenuAction, which will supply the implementation of its methods.
# -----------------------------------------------------------------------------------
class IZActiveMenuNode(IZMenuNode):

    def isEnabled(self, menuContext):
        u"Returns True if this node is enabled (if not, the menu item will be visible but greyed out)." #$NON-NLS-1$
    # end isEnabled()

    def isVisible(self, menuContext):
        u"Returns True if this ndoe is visible." #$NON-NLS-1$
    # end isVisible()

    def isBoldWithContext(self, menuContext):
        u"Returns True if this node is bold." #$NON-NLS-1$
    # end isBoldWithContext()

    def isChecked(self):
        u"Returns True if this node is checked." #$NON-NLS-1$
    # end isChecked()

    def runAction(self, menuActionContext):
        u"Runs the action associated with this node." #$NON-NLS-1$
    # end runAction()

    def runCheckAction(self, menuActionContext, checked):
        u"Runs the action associated with this node." #$NON-NLS-1$
    # end runCheckAction()

# end IZActiveMenuNode


# ------------------------------------------------------------------------------
# A generic implementation of IZMenuNode.
# ------------------------------------------------------------------------------
class ZMenuNode(IZMenuNode):

    def __init__(self, name = None, description = None, bitmap = None, isSep = False, isCB = False, boldFlag = False, gravity = 0):
        self.name = name
        self.description = description
        self.bitmap = bitmap
        self.isSep = isSep
        self.isCB = isCB
        self.boldFlag = boldFlag
        self.gravity = gravity
        self.children = ZSortedList(ZMenuNodeComparator())
    # end __init__()

    def addChild(self, node):
        self.children.append(node)
    # end addChild()

    def getChildren(self):
        return self.children
    # end getChildren()

    def getName(self):
        return self.name
    # end getName()
    
    def setName(self, name):
        self.name = name
    # end setName()

    def getDescription(self):
        return self.description
    # end getDescription()
    
    def setDescription(self, description):
        self.description = description
    # end setDescription()

    def getBitmap(self):
        return self.bitmap
    # end getBitmap()
    
    def setBitmap(self, bitmap):
        self.bitmap = bitmap
    # end setBitmap()

    def isSeparator(self):
        return self.isSep
    # end isSeparator()

    def isCheckboxItem(self):
        return self.isCB
    # end isCheckboxItem()
    
    def setCheckboxItem(self, checkboxFlag):
        self.isCB = checkboxFlag
    # end setCheckboxItem()

    def isBold(self):
        return self.boldFlag
    # end isBold()
    
    def setBold(self, boldFlag):
        self.boldFlag = boldFlag
    # end setBold()
    
    def getGravity(self):
        return self.gravity
    # end getGravity()
    
    def setGravity(self, gravity):
        self.gravity = gravity
    # end setGravity()

# end ZMenuNode


# ------------------------------------------------------------------------------
# Class that can be used as the root node of a context menu.
# ------------------------------------------------------------------------------
class ZHiddenRootMenuNode(ZMenuNode):

    def __init__(self):
        ZMenuNode.__init__(self, u"", u"", None, False, False, False, 0) #$NON-NLS-1$ #$NON-NLS-2$
    # end __init__()

# end ZHiddenRootMenuNode


# --------------------------------------------------------------------------------
# A generic implementation of IZActiveMenuNode.
# --------------------------------------------------------------------------------
class ZActiveMenuNode(ZMenuNode, IZActiveMenuNode):

    def __init__(self, name = None, description = None, bitmap = None, isSep = False, isCB = False, boldFlag = False, gravity = 0, action = None):
        ZMenuNode.__init__(self, name, description, bitmap, isSep, isCB, boldFlag, gravity)
        self.action = action
    # end __init__()

    def isEnabled(self, menuContext):
        if self.action is not None:
            return self.action.isEnabled(menuContext)
        else:
            return True
    # end isEnabled()

    def isVisible(self, menuContext):
        if self.action is not None:
            return self.action.isVisible(menuContext)
        else:
            return True
    # end isVisible()

    def isBoldWithContext(self, menuContext):
        if self.action is not None:
            return self.action.isBold(menuContext)
        else:
            return False
    # end isBoldWithContext()

    def isChecked(self, menuContext):
        if self.action is not None:
            return self.action.isChecked(menuContext)
        else:
            return None
    # end isChecked()

    def runAction(self, menuContext):
        self.action.runAction(menuContext)
    # end runAction()

    def runCheckAction(self, menuContext, checked):
        self.action.runCheckAction(menuContext, checked)
    # end runCheckAction()

# end ZActiveMenuNode


# --------------------------------------------------------------------------------
# Extends the active menu node in order to implement a method callback version of
# an active menu node.
# --------------------------------------------------------------------------------
class ZActiveCallbackMenuNode(ZActiveMenuNode):

    # --------------------------------------------------------------------------
    # Inner class used to adapt the callback to an action.
    # --------------------------------------------------------------------------
    class ZCallbackRunner(ZMenuAction):

        def __init__(self, callback, visible, enabled, bold):
            self.callback = callback
            self.visible = visible
            self.enabled = enabled
            self.bold = bold
            
            ZMenuAction.__init__(self)
        # end __init__()

        def isVisible(self, context): #@UnusedVariable
            return self.visible
        # end isVisible()

        def isEnabled(self, context): #@UnusedVariable
            return self.enabled
        # end isEnabled()

        def isBold(self, context): #@UnusedVariable
            return self.bold
        # end isBold()

        def runAction(self, actionContext):
            if self.callback is not None:
                self.callback(actionContext)
        # end runAction()

    # end ZCallbackRunner

    def __init__(self, name = None, description = None, bitmap = None, isSep = False, isCB = False, boldFlag = False, gravity = 0, enabledFlag = True, visibleFlag = True, callback = None):
        ZActiveMenuNode.__init__(self, name, description, bitmap, isSep, isCB, boldFlag, gravity, ZActiveCallbackMenuNode.ZCallbackRunner(callback, visibleFlag, enabledFlag, boldFlag))
    # end __init__()

# end ZActiveCallbackMenuNode


# --------------------------------------------------------------------------------
# A menu content provider that simply uses the data in instances of IZMenuNode to
# provide the content.  Note that the root node is assumed to be hidden (a virtual
# root of the tree - useful for both menu bars and popup menus).
# --------------------------------------------------------------------------------
class ZNodeBasedMenuContentProvider(IZMenuContentProvider):

    def __init__(self, rootNode):
        self.rootNode = rootNode
    # end __init__()

    def getMenuNodes(self, parent):
        if parent is None:
            return self.rootNode.getChildren()
        return parent.getChildren()
    # end getMenuNodes()

    def getMenuNodeName(self, menuNode):
        return menuNode.getName()
    # end getMenuNodeName()

    def getMenuNodeDescription(self, menuNode):
        return menuNode.getDescription()
    # end getMenuNodeDescription()

    def getMenuNodeBitmap(self, menuNode):
        return menuNode.getBitmap()
    # end getMenuNodeBitmap()

    def isSeparator(self, menuNode):
        return menuNode.isSeparator()
    # end isSeparator()

    def isMenuGroup(self, menuNode):
        children = menuNode.getChildren()
        return children is not None and len(children) > 0
    # end isMenuGroup()

    def isMenuItem(self, menuNode):
        return not self.isMenuGroup(menuNode) and not self.isSeparator(menuNode)
    # end isMenuItem()

    def isCheckboxMenuItem(self, menuNode):
        return menuNode.isCheckboxItem()
    # end isCheckboxMenuItem()

    def isEnabled(self, menuNode): #@UnusedVariable
        return True
    # end isEnabled()

    def isVisible(self, menuNode): #@UnusedVariable
        if self.isMenuGroup(menuNode):
            for child in menuNode.getChildren():
                if self.isVisible(child):
                    return True
            return False
        else:
            return True
    # end isVisible()

    def isBold(self, menuNode):
        return menuNode.isBold()
    # end isBold()
    
    def isChecked(self, menuNode): #@UnusedVariable
        return None
    # end isChecked()

# end ZNodeBasedMenuContentProvider


# --------------------------------------------------------------------------------
# A menu content provider that simply uses the data in instances of
# IZActiveMenuNode to provide the content.
# --------------------------------------------------------------------------------
class ZActiveModelBasedMenuContentProvider(ZNodeBasedMenuContentProvider):

    def __init__(self, rootNode, menuContext):
        self.menuContext = menuContext
        ZNodeBasedMenuContentProvider.__init__(self, rootNode)
    # end __init__()

    def isEnabled(self, menuNode):
        return menuNode.isEnabled(self.menuContext)
    # end isEnabled()

    def isVisible(self, menuNode):
        if self.isMenuGroup(menuNode):
            ZNodeBasedMenuContentProvider.isVisible(self, menuNode)
        return menuNode.isVisible(self.menuContext)
    # end isVisible()

    def isBold(self, menuNode):
        return ZNodeBasedMenuContentProvider.isBold(self, menuNode) or menuNode.isBoldWithContext(self.menuContext)
    # end isBold()
    
    def isChecked(self, menuNode):
        if self.isCheckboxMenuItem(menuNode):
            return menuNode.isChecked(self.menuContext)
        return None
    # end isChecked()

# end ZActiveModelBasedMenuContentProvider


# --------------------------------------------------------------------------------
# A menu event handler that simply uses the data in instances of IZActiveMenuNode
# to handle the menu events.
# --------------------------------------------------------------------------------
class ZActiveModelBasedMenuEventHandler(IZMenuEventHandler):

    def __init__(self, menuContext):
        self.menuContext = menuContext
    # end __init__()

    def onMenuClick(self, menuNode):
        menuNode.runAction(self.menuContext)
    # end onMenuClick()

    def onCheckMenuClick(self, menuNode, checked):
        menuNode.runCheckAction(self.menuContext, checked)
    # end onCheckMenuClick()

# end ZActiveModelBasedMenuEventHandler
