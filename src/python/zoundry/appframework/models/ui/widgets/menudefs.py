from zoundry.appframework.exceptions import ZAppFrameworkException
from zoundry.appframework.messages import _extstr
from zoundry.appframework.zplugin.extpointdef import ZExtensionPointBaseDef
from zoundry.base.util.types.parameters import ZParameters
import string

# ------------------------------------------------------------------------------------------
# An extension point def for the zoundry.appframework.ui.core.menu extension point.
# ------------------------------------------------------------------------------------------
class ZMenuExtensionPointDef(ZExtensionPointBaseDef):

    MENUBAR_TYPE = u"menubar" #$NON-NLS-1$
    POPUP_MENU_TYPE = u"popup" #$NON-NLS-1$

    def __init__(self, extPoint):
        ZExtensionPointBaseDef.__init__(self, extPoint)
    # end __init__()

    def getType(self):
        type = self._getExtensionText(u"plg:menu/plg:type") #$NON-NLS-1$
        if not type:
            type = None
        return type
    # end getType()

# end ZMenuExtensionPointDef


# ----------------------------------------------------------------------------------
# A wrapper around a ZExtensionPoint, this class provides convenient access to
# the specific data of interest for this type of extension point (Menu Group).
# ----------------------------------------------------------------------------------
class ZMenuGroupDef(ZExtensionPointBaseDef):

    def __init__(self, extensionPoint):
        ZExtensionPointBaseDef.__init__(self, extensionPoint)
    # end __init__()

    def getParent(self):
        parent = self._getExtensionText(u"plg:menu-group/plg:parent-group") #$NON-NLS-1$
        if not parent:
            return None
        return parent
    # end getParent()

    def getName(self):
        name = self._getExtensionText(u"plg:menu-group/plg:name") #$NON-NLS-1$
        if not name:
            raise ZAppFrameworkException(_extstr(u"menudefs.NameMissingInMenuItemError") % self.extensionPoint.getId()) #$NON-NLS-1$
        return name
    # end getName()

    def getDescription(self):
        desc = self._getExtensionText(u"plg:menu-group/plg:description") #$NON-NLS-1$
        if not desc:
            return u"" #$NON-NLS-1$
        return desc
    # end getName()

    def getGravity(self):
        gravity = self._getExtensionText(u"plg:menu-group/plg:gravity") #$NON-NLS-1$
        if not gravity:
            return 50
        return string.atoi(gravity)
    # end getGravity()

    def getIcon(self):
        icon = self._getExtensionText(u"plg:menu-group/plg:icon") #$NON-NLS-1$
        if not icon:
            return u"" #$NON-NLS-1$
        return icon
    # end getIcon()

    # FIXME share the icon/iconkey/loadicon logic - this is duplicated now
    def getIconKey(self):
        return u"%s:%s" % (self.getId(), self.getIcon()) #$NON-NLS-1$
    # end getIconKey()

    def loadIcon(self):
        return self.getPlugin().getResourceRegistry().getBitmap(self.getIcon())
    # end loadIcon()

# end ZMenuGroupDef


# ----------------------------------------------------------------------------------
# A wrapper around a ZExtensionPoint, this class provides convenient access to
# the specific data of interest for this type of extension point (Menu Item).
# ----------------------------------------------------------------------------------
class ZMenuItemDef(ZExtensionPointBaseDef):

    TYPE_STANDARD = u"standard" #$NON-NLS-1$
    TYPE_CHECKBOX = u"check" #$NON-NLS-1$
    TYPE_SEPARATOR = u"separator" #$NON-NLS-1$

    def __init__(self, extensionPoint):
        ZExtensionPointBaseDef.__init__(self, extensionPoint)
        self.parameters = None
    # end __init__()

    def createMenuItem(self):
        menuItemClass = self.getClass()
        return menuItemClass()
    # end createMenuItem()

    def getGroup(self):
        group = self._getExtensionText(u"plg:menu-item/plg:group") #$NON-NLS-1$
        if not group:
            return None
        return group
    # end getGroup()

    def getName(self):
        name = self._getExtensionText(u"plg:menu-item/plg:name") #$NON-NLS-1$
        if not name:
            raise ZAppFrameworkException(_extstr(u"menudefs.NameMissingInMenuItemError") % self.extensionPoint.getId()) #$NON-NLS-1$
        return name
    # end getName()

    def getDescription(self):
        desc = self._getExtensionText(u"plg:menu-item/plg:description") #$NON-NLS-1$
        if not desc:
            return u"" #$NON-NLS-1$
        return desc
    # end getName()

    def getGravity(self):
        gravity = self._getExtensionText(u"plg:menu-item/plg:gravity") #$NON-NLS-1$
        if not gravity:
            return 50
        return string.atoi(gravity)
    # end getGravity()

    def getType(self):
        type = self._getExtensionText(u"plg:menu-item/plg:type") #$NON-NLS-1$
        if not type:
            return ZMenuItemDef.TYPE_STANDARD
        return type
    # end getType()

    def isBold(self):
        boldFlag = self._getExtensionText(u"plg:menu-item/plg:bold") #$NON-NLS-1$
        if not boldFlag:
            return False
        return boldFlag == u"true" #$NON-NLS-1$
    # end isBold()

    def getIcon(self):
        icon = self._getExtensionText(u"plg:menu-item/plg:icon") #$NON-NLS-1$
        if not icon:
            return u"" #$NON-NLS-1$
        return icon
    # end getIcon()

    def getIconKey(self):
        return self.getId() + u":" + self.getIcon() #$NON-NLS-1$
    # end getIconKey()

    def loadIcon(self):
        return self.getPlugin().getResourceRegistry().getBitmap(self.getIcon())
    # end loadIcon()

    def getParameters(self):
        u"""getParameters() -> IZParameters
        Returns the IZParameters.""" #$NON-NLS-1$
        if self.parameters is None:
            nodes = self._getExtensionNodes(u"plg:menu-item/plg:parameters/plg:parameter") #$NON-NLS-1$
            paramMap = {}
            for node in nodes:
                name = node.getAttribute(u"name") #$NON-NLS-1$
                if name:
                    paramMap[name] = node.getText()
            self.parameters = ZParameters(paramMap)
        return self.parameters
    # end getParameters()

# end ZMenuItemDef
