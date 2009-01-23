from zoundry.appframework.global_services import getResourceRegistry
from zoundry.appframework.ui.widgets.controls.common.menu.menumodel import ZPluginMenuModel
from zoundry.blogapp.constants import IZBlogAppActionIDs
from zoundry.blogapp.constants import IZBlogAppMenuIds

MENU_ITEMS = [
       # gravity, actionId, boldFlag, iconPath
        (10, IZBlogAppActionIDs.OPEN_BLOG_POST_ACTION, True, u"images/common/menu/blog-post/edit.png"), #$NON-NLS-1$
        (11, IZBlogAppActionIDs.OPEN_BLOG_POST_AS_UNPUBLISHED_ACTION, False, u"images/common/menu/blog-post/edit.png"), #$NON-NLS-1$
        (15, IZBlogAppActionIDs.VIEW_BLOG_POST_ACTION, False, u"images/common/menu/view_online.png"), #$NON-NLS-1$
        (16, IZBlogAppActionIDs.COPY_BLOG_POST_URL_ACTION, False, u"images/common/menu/link/copylinklocation.png"), #$NON-NLS-1$
        (60, IZBlogAppActionIDs.DELETE_BLOG_POST_ACTION, False, u"images/common/menu/blog-post/delete.png"), #$NON-NLS-1$
]

# ------------------------------------------------------------------------------
# Menu model to use for blog post context menu.
# ------------------------------------------------------------------------------
class ZBlogPostMenuModel(ZPluginMenuModel):

    def __init__(self):
        ZPluginMenuModel.__init__(self, IZBlogAppMenuIds.ZID_BLOG_POST_MENU)

        self.buildModel()
    # end __init__()

    def buildModel(self):
        registry = getResourceRegistry()

        for (gravity, actionId, boldFlag, iconPath) in MENU_ITEMS:
            menuId = self.addMenuItemWithActionId(gravity, actionId, None)
            self.setMenuItemBold(menuId, boldFlag)
            if iconPath is not None:
                bitmap = registry.getBitmap(iconPath)
                self.setMenuItemBitmap(menuId, bitmap)
        
        self.addSeparator(50)
    # end buildModel()

# end ZBlogPostMenuModel
