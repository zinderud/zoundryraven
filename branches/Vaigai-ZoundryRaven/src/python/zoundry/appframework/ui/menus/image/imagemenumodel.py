from zoundry.appframework.constants import IZAppActionIDs
from zoundry.appframework.constants import IZAppMenuIds
from zoundry.appframework.global_services import getResourceRegistry
from zoundry.appframework.ui.widgets.controls.common.menu.menumodel import ZPluginMenuModel

MENU_ITEMS = [
       # gravity, actionId, boldFlag, iconPath
        (10, IZAppActionIDs.OPEN_IMAGE_ACTION, True, u"images/common/menu/image/open.png"), #$NON-NLS-1$
        (12, IZAppActionIDs.COPY_IMAGE_LOCATION_ACTION, False, u"images/common/menu/image/copyimagelocation.png"), #$NON-NLS-1$
]

# ------------------------------------------------------------------------------
# Menu model to use for image context menu.
# ------------------------------------------------------------------------------
class ZImageMenuModel(ZPluginMenuModel):

    def __init__(self):
        ZPluginMenuModel.__init__(self, IZAppMenuIds.ZID_IMAGE_MENU)

        self.buildModel()
    # end __init__()

    # FIXME (EPW) lots of menu models with this pattern - need base class
    def buildModel(self):
        registry = getResourceRegistry()

        for (gravity, actionId, boldFlag, iconPath) in MENU_ITEMS:
            menuId = self.addMenuItemWithActionId(gravity, actionId, None)
            self.setMenuItemBold(menuId, boldFlag)
            if iconPath is not None:
                bitmap = registry.getBitmap(iconPath)
                self.setMenuItemBitmap(menuId, bitmap)
    # end buildModel()

# end ZImageMenuModel
