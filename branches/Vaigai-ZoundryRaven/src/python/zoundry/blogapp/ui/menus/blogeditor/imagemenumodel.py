from zoundry.blogapp.ui.menus.blogeditor.menulabels import ZImageBorderMenuLabels
from zoundry.blogapp.ui.menus.blogeditor.menulabels import ZImageAlignMenuLabels
from zoundry.blogapp.ui.actions.blogeditor.blogcontexttoolbaractions import ZBlogPostCreateThumbnailImageAction
from zoundry.blogapp.ui.actions.blogeditor.blogcontexttoolbaractions import ZBlogPostImageBorderAction
from zoundry.appframework.global_services import getResourceRegistry
from zoundry.appframework.ui.widgets.controls.common.menu.menumodel import ZPluginMenuModel
from zoundry.blogapp.constants import IZBlogAppMenuIds
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.ui.actions.blogeditor.blogcontexttoolbaractions import ZBlogPostImageAlignAction
from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZBlogPostCopyImageLocationAction
from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZBlogPostEditImageAction
from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZBlogPostInsertImageAction
from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZBlogPostInsertImgTagAction

#-------------------------------------------
# Menu model used for images
#-------------------------------------------
class ZImageMenuModelBuilder:

    def createImageMenuModel(self):
        menuModel = ZPluginMenuModel(IZBlogAppMenuIds.ZID_INSERT_IMAGE_MENU)
        self.buildImageMenu(menuModel, None)
        return menuModel
    # end createImageMenuModel

    def buildImageMenu(self, menuModel, parentId): #@UnusedVariable
        self.buildInsertImageMenuItems(menuModel, 10, parentId)
        self.buildCopyImageLocationMenuItem(menuModel, 20, parentId)
        self.buildEditObjectsMenuItems(menuModel, 30, parentId)
        self.buildImageAlignMenu(menuModel, 40, parentId)
        self.buildImageBorderMenu(menuModel, 50, parentId)
        self.buildImageThumbnailMenu(menuModel, 60, parentId) 
    # end buildImageMenu

    def buildInsertImageMenuItems(self, menuModel, gravity, parentId): #@UnusedVariable
        resourceReg = getResourceRegistry()
        mid = menuModel.addMenuItemWithAction(_extstr(u"blogcontenteditorimagemenumodel.InsertImageFile"),  gravity+1, ZBlogPostInsertImageAction(), parentId ) #$NON-NLS-1$
        menuModel.setMenuItemBitmap(mid, resourceReg.getBitmap(u"images/editors/blogeditor/designer/toolbar/16x16/insert_link.png")) #$NON-NLS-1$

        mid = menuModel.addMenuItemWithAction(_extstr(u"blogcontenteditorimagemenumodel.InsertImageTag"),  gravity+2, ZBlogPostInsertImgTagAction(), parentId ) #$NON-NLS-1$
        menuModel.setMenuItemBitmap(mid, resourceReg.getBitmap(u"images/editors/blogeditor/designer/toolbar/16x16/insert_link.png")) #$NON-NLS-1$
    # end buildInsertImageMenuItems

    def buildCopyImageLocationMenuItem(self, menuModel, gravity, parentId):
        resourceReg = getResourceRegistry()
        mid = menuModel.addMenuItemWithAction(_extstr(u"blogcontenteditorimagemenumodel.CopyImageLocation"),  gravity+1, ZBlogPostCopyImageLocationAction(), parentId ) #$NON-NLS-1$
        menuModel.setMenuItemBitmap(mid, resourceReg.getBitmap(u"images/common/menu/image/copyimagelocation.png")) #$NON-NLS-1$
    # end buildCopyImageLocationMenuItem()

    def buildEditObjectsMenuItems(self, menuModel, gravity, parentId):
        resourceReg = getResourceRegistry()
        label = _extstr(u"blogcontenteditorimagemenumodel.EditImage") #$NON-NLS-1$
        mid = menuModel.addMenuItemWithAction(u"%s\tCtrl+M" % label, gravity, ZBlogPostEditImageAction(), parentId ) #$NON-NLS-1$
        menuModel.setMenuItemBitmap(mid, resourceReg.getBitmap(u"images/editors/blogeditor/designer/toolbar/16x16/insert_image.png")) #$NON-NLS-1$
    # end buildEditObjectsMenuItems()

    def buildImageAlignMenu(self, menuModel, gravity, parentId):
        alignParentId = menuModel.addMenu(_extstr(u"blogcontenteditorimagealignmenumodel.Align"), gravity, parentId) #$NON-NLS-1$
        ZImageAlignMenuModelBuilder().buildAlignImageMenu(menuModel, alignParentId)
    # end buildImageAlignMenu

    def buildImageThumbnailMenu(self, menuModel, gravity, parentId):
        alignParentId = menuModel.addMenu(_extstr(u"blogcontenteditorimagethumbnailmenumodel.Thumbnail"), gravity, parentId) #$NON-NLS-1$
        ZImageThumbnailMenuModelBuilder().buildImageThumbnailMenu(menuModel, alignParentId)
    # end buildImageThumbnailMenu

    def buildImageBorderMenu(self, menuModel, gravity, parentId):
        borderParentId = menuModel.addMenu(_extstr(u"blogcontenteditorimagebordermenumodel.Border"), gravity, parentId) #$NON-NLS-1$
        ZImageBorderMenuModelBuilder().buildImageBorderMenu(menuModel, borderParentId)
    # end buildImageBorderMenu

    def getImageLocation(self, imageContext):
        imageLocation = None
        if imageContext is not None and imageContext.canEditImage():
            attrs = imageContext.getImageAttributes()
            if attrs.has_key(u"src"): #$NON-NLS-1$
                imageLocation = attrs[u"src"]    #$NON-NLS-1$
        return imageLocation
    # end getImageLocation()
# end ZImageMenuModelBuilder

#-------------------------------------------
# Menu model used for align image menu options
#-------------------------------------------
class ZImageAlignMenuModelBuilder:

    def createImageAlignMenuModel(self):
        menuModel = ZPluginMenuModel(IZBlogAppMenuIds.ZID_INSERT_IMAGE_MENU)
        self.buildAlignImageMenu(menuModel, None)
        return menuModel
    # end createImageAlignMenuModel

    def buildAlignImageMenu(self, menuModel, parentId): #@UnusedVariable
        resourceReg = getResourceRegistry()
        gravity = 10
        mid = menuModel.addMenuItemWithAction(ZImageAlignMenuLabels.ALIGN_LABELS[ZImageAlignMenuLabels.NONE], gravity, ZBlogPostImageAlignAction(), parentId ) #$NON-NLS-1$ @UnusedVariable
        #menuModel.setMenuItemBitmap(mid, resourceReg.getBitmap(u"images/editors/blogeditor/designer/toolbar/16x16/image_align_left.png")) #$NON-NLS-1$

        mid = menuModel.addMenuItemWithAction(ZImageAlignMenuLabels.ALIGN_LABELS[ZImageAlignMenuLabels.LEFT], gravity+1, ZBlogPostImageAlignAction(u"left"), parentId ) #$NON-NLS-1$ #$NON-NLS-2$
        menuModel.setMenuItemBitmap(mid, resourceReg.getBitmap(u"images/editors/blogeditor/designer/toolbar/16x16/image_align_left.png")) #$NON-NLS-1$

        mid = menuModel.addMenuItemWithAction(ZImageAlignMenuLabels.ALIGN_LABELS[ZImageAlignMenuLabels.CENTER], gravity+2, ZBlogPostImageAlignAction(u"center"), parentId ) #$NON-NLS-1$ #$NON-NLS-2$
        menuModel.setMenuItemBitmap(mid, resourceReg.getBitmap(u"images/editors/blogeditor/designer/toolbar/16x16/image_align_center.png")) #$NON-NLS-1$

        mid = menuModel.addMenuItemWithAction(ZImageAlignMenuLabels.ALIGN_LABELS[ZImageAlignMenuLabels.RIGHT], gravity+3, ZBlogPostImageAlignAction(u"right"), parentId ) #$NON-NLS-1$ #$NON-NLS-2$
        menuModel.setMenuItemBitmap(mid, resourceReg.getBitmap(u"images/editors/blogeditor/designer/toolbar/16x16/image_align_right.png")) #$NON-NLS-1$
    # end buildAlignImageMenu
# end ZImageAlignMenuModelBuilder

#-------------------------------------------
# Menu model used for image border menu options
#-------------------------------------------
class ZImageBorderMenuModelBuilder:

    def createImageBorderMenuModel(self):
        menuModel = ZPluginMenuModel(IZBlogAppMenuIds.ZID_IMAGE_BORDER_MENU)
        self.buildImageBorderMenu(menuModel, None)
        return menuModel
    # end createImageBorderMenuModel

    def buildImageBorderMenu(self, menuModel, parentId): #@UnusedVariable
        for style in ZImageBorderMenuLabels.BORDER_KEYWORDS:
            label = ZImageBorderMenuLabels.BORDER_LABELS[style]
            menuModel.addMenuItemWithAction(label, 5, ZBlogPostImageBorderAction(style.lower()), parentId)        
    # end buildImageBorderMenu()
# end ZImageBorderMenuModelBuilder

#-------------------------------------------
# Menu model used for image tn menu options
#-------------------------------------------
class ZImageThumbnailMenuModelBuilder:

    def createImageThumbnailMenuModel(self):
        menuModel = ZPluginMenuModel(IZBlogAppMenuIds.ZID_IMAGE_THUMBNAIL_MENU)
        self.buildImageThumbnailMenu(menuModel, None)
        return menuModel
    # end createImageThumbnailMenuModel

    def buildImageThumbnailMenu(self, menuModel, parentId): #@UnusedVariable
        self.menuModel = ZPluginMenuModel(IZBlogAppMenuIds.ZID_IMAGE_THUMBNAIL_MENU)
        tnSizes = [75, 100, 250, 400, 500, 600, 800]
        for width in tnSizes:
            menuModel.addMenuItemWithAction(u"%spx X %spx" % (width, width), 5, ZBlogPostCreateThumbnailImageAction(width, width), parentId ) #$NON-NLS-1$
    # end buildImageThumbnailMenu()
# end ZImageThumbnailMenuModelBuilder

