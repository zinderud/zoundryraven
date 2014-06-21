from zoundry.appframework.global_services import getResourceRegistry
from zoundry.appframework.ui.widgets.controls.common.menu.menumodel import ZPluginMenuModel
from zoundry.blogapp.constants import IZBlogAppActionIDs
from zoundry.blogapp.constants import IZBlogAppMenuIds


MENU_ITEMS = [
       # gravity, actionId, boldFlag, iconPath
        (5, IZBlogAppActionIDs.BLOG_NEW_BLOG_POST_ACTION, False, u"images/common/menu/blog/newpost.png"), #$NON-NLS-1$
        (20, IZBlogAppActionIDs.DOWNLOAD_BLOG_TEMPLATE_ACTION, False, u"images/common/menu/blog/download_template.png"), #$NON-NLS-1$
        (55, IZBlogAppActionIDs.VIEW_BLOG_ACTION, False, u"images/common/menu/view_online.png"), #$NON-NLS-1$
        (65, IZBlogAppActionIDs.CONFIGURE_BLOG_ACTION, False, u"images/common/menu/blog/configure.png"), #$NON-NLS-1$
]


# ------------------------------------------------------------------------------
# Menu model used for the Blog context menu.
# ------------------------------------------------------------------------------
class ZBlogMenuModel(ZPluginMenuModel):

    def __init__(self):
        ZPluginMenuModel.__init__(self, IZBlogAppMenuIds.ZID_BLOG_MENU)

        self._buildModel()
    # end __init__()

    def _buildModel(self):
        registry = getResourceRegistry()

        for (gravity, actionId, boldFlag, iconPath) in MENU_ITEMS:
            menuId = self.addMenuItemWithActionId(gravity, actionId, None)
            self.setMenuItemBold(menuId, boldFlag)
            if iconPath is not None:
                bitmap = registry.getBitmap(iconPath)
                self.setMenuItemBitmap(menuId, bitmap)

        self.addSeparator(50)
    # end _buildModel()

# end ZBlogMenuModel

