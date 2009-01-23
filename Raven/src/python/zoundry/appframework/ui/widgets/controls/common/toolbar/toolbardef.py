from zoundry.appframework.zplugin.extpointdef import ZExtensionPointBaseDef
from zoundry.base.util.text.textutil import getSafeString
import string

# ----------------------------------------------------------------------------------
# A wrapper around a ZExtensionPoint, this class provides convenient access to
# the specific data of interest for this type of extension point (ToolBar Item).
# ----------------------------------------------------------------------------------
class ZToolBarItemDef(ZExtensionPointBaseDef):

    TYPE_SEPARATOR = u"separator" #$NON-NLS-1$
    TYPE_STANDARD = u"standard" #$NON-NLS-1$
    TYPE_TOGGLE = u"toggle" #$NON-NLS-1$
    TYPE_DROPDOWN = u"dropdown" #$NON-NLS-1$
    
    BMP_TYPE_STANDARD = u"standard" #$NON-NLS-1$
    BMP_TYPE_HOVER = u"hover" #$NON-NLS-1$
    BMP_TYPE_DISABLED = u"disabled" #$NON-NLS-1$

    def __init__(self, extensionPoint):
        ZExtensionPointBaseDef.__init__(self, extensionPoint)
        self.parameters = None
    # end __init__()

    def createAction(self):
        actionClass = self.getClass()
        return actionClass()
    # end createAction()

    def getToolBar(self):
        group = self._getExtensionText(u"plg:toolbar-item/plg:toolbar") #$NON-NLS-1$
        if not group:
            return None
        return group
    # end getToolBar()

    def getText(self):
        name = self._getExtensionText(u"plg:toolbar-item/plg:text") #$NON-NLS-1$
        return getSafeString(name)
    # end getText()

    def getDescription(self):
        desc = self._getExtensionText(u"plg:toolbar-item/plg:description") #$NON-NLS-1$
        return getSafeString(desc)
    # end getName()

    def getGravity(self):
        gravity = self._getExtensionText(u"plg:toolbar-item/plg:gravity") #$NON-NLS-1$
        if not gravity:
            return 50
        return string.atoi(gravity)
    # end getGravity()

    def getType(self):
        type = self._getExtensionText(u"plg:toolbar-item/plg:type") #$NON-NLS-1$
        if not type:
            return ZToolBarItemDef.TYPE_STANDARD
        return type
    # end getType()

    def getBitmaps(self):
        u"""getBitmaps() -> (wx.Bitmap, int, bmp_type)[]
        Returns a list of bitmaps (bitmap, size, type).""" #$NON-NLS-1$
        rval = []

        bitmapList = self._getExtensionNodes(u"plg:toolbar-item/plg:bitmaps/plg:bitmap") #$NON-NLS-1$
        for bitmapNode in bitmapList:
            bitmap = self._loadBitmap(bitmapNode.getText())
            size = string.atoi(bitmapNode.getAttribute(u"size")) #$NON-NLS-1$
            type = bitmapNode.getAttribute(u"type") #$NON-NLS-1$
            rval.append( (bitmap, size, type) )
        return rval    
    # end getBitmaps()

    def _loadBitmap(self, imagePath):
        return self.getPlugin().getResourceRegistry().getBitmap(imagePath)
    # end _loadBitmap()

# end ZToolBarItemDef

