from zoundry.appframework.messages import _extstr
from zoundry.appframework.ui.actions.menuaction import ZMenuActionContext
from zoundry.appframework.ui.widgets.controls.common.menu.menu import ZMenu
from zoundry.appframework.ui.widgets.controls.common.menu.menuimpl import ZActiveCallbackMenuNode
from zoundry.appframework.ui.widgets.controls.common.menu.menuimpl import ZActiveModelBasedMenuContentProvider
from zoundry.appframework.ui.widgets.controls.common.menu.menuimpl import ZActiveModelBasedMenuEventHandler
from zoundry.appframework.ui.widgets.controls.common.menu.menuimpl import ZHiddenRootMenuNode

# ------------------------------------------------------------------------------
# Context menu that gets displayed when the user right-clicks on a tab in a
# tab container.
# ------------------------------------------------------------------------------
class ZTabContextMenu(ZMenu):

    def __init__(self, tab):
        self.tab = tab

        menuContext = self._createMenuContext()
        menuNode = self._createMenuNode()
        contentProvider = ZActiveModelBasedMenuContentProvider(menuNode, menuContext)
        eventHandler = ZActiveModelBasedMenuEventHandler(menuContext)
        ZMenu.__init__(self, tab, menuNode, contentProvider, eventHandler)
    # end __init__()
    
    def _createMenuContext(self):
        return ZMenuActionContext(self.tab)
    # end _createMenuContext()
    
    def _createMenuNode(self):
        rootNode = ZHiddenRootMenuNode()
        rootNode.addChild(ZActiveCallbackMenuNode(_extstr(u"tabctxmenu.Close"), _extstr(u"tabctxmenu.CloseMsg"), None, False, False, True, 0, True, True, self.onClose)) #$NON-NLS-2$ #$NON-NLS-1$
        rootNode.addChild(ZActiveCallbackMenuNode(_extstr(u"tabctxmenu.CloseOthers"), _extstr(u"tabctxmenu.CloseOthersMsg"), None, False, False, False, 1, True, True, self.onCloseOthers)) #$NON-NLS-2$ #$NON-NLS-1$
        rootNode.addChild(ZActiveCallbackMenuNode(_extstr(u"tabctxmenu.CloseAll"), _extstr(u"tabctxmenu.CloseAllMsg"), None, False, False, False, 2, True, True, self.onCloseAll)) #$NON-NLS-2$ #$NON-NLS-1$
        return rootNode
    # end _createMenuNode()
    
    def onClose(self, context): #@UnusedVariable
        self.tab._fireClosedEvent()
    # end onClose()

    def onCloseOthers(self, context): #@UnusedVariable
        tabBar = self.tab.getTabBar()
        for tab in tabBar._getTabs():
            if tab is not self.tab:
                tabBar._fireClosedEvent(tab)
    # end onCloseOthers()

    def onCloseAll(self, context): #@UnusedVariable
        tabBar = self.tab.getTabBar()
        for tab in tabBar._getTabs():
            tabBar._fireClosedEvent(tab)
    # end onCloseAll()
    
# end ZTabContextMenu
