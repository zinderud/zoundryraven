from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZBlogPostCreateLinkNoUiAction
from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZConvertLinkToEmbedAction
from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.global_services import getResourceRegistry
from zoundry.appframework.ui.widgets.controls.common.menu.menumodel import ZPluginMenuModel
from zoundry.blogapp.constants import IZBlogAppMenuIds
from zoundry.blogapp.constants import IZBlogAppServiceIDs
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZBlogPostCopyLinkLocationAction
from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZBlogPostCreateLinkFromFormatterAction
from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZBlogPostEditLinkAction
from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZBlogPostInsertLinkAction
from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZBlogPostRemoveLinkContextMenuAction
from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZConvertProductLinkAction

#-------------------------------------------
# Menu model used for links
#-------------------------------------------
class ZLinkMenuModelBuilder:

    def createToolbarLinkMenuModel(self):
        menuModel = ZPluginMenuModel(IZBlogAppMenuIds.ZID_INSERT_LINK_MENU)
        self.buildLinkMenu(menuModel, None, None)
        return menuModel
    # end createToolbarLinkMenuModel()

    def buildLinkMenu(self, menuModel, parentId, url): #@UnusedVariable
        self.buildInsertLinkMenuItem(menuModel, 10, parentId)
        self.buildLinkToFormattersMenu(menuModel, 12, parentId)
        self.buildConvertLinkToEmdedMenuItem(menuModel, 15, parentId, url)
        self.buildCopyLinkLocationMenuItem(menuModel, 20, parentId)
        self.buildEditObjectsMenuItems(menuModel, 30, parentId)
        self.buildRemoveLinkMenuItem(menuModel, 50, parentId)
    # end buildLinkMenu

    def buildInsertLinkMenuItem(self, menuModel, gravity, parentId):        #@UnusedVariable
        resourceReg = getResourceRegistry()
        linkto = _extstr(u"blogcontenteditorlinkmenumodel.LinkTo") #@UnusedVariable #$NON-NLS-1$
        mid = menuModel.addMenuItemWithAction(_extstr(u"blogcontenteditorlinkmenumodel.CreateLink"),  gravity, ZBlogPostInsertLinkAction(), parentId ) #$NON-NLS-1$
        menuModel.setMenuItemBitmap(mid, resourceReg.getBitmap(u"images/editors/blogeditor/designer/toolbar/16x16/insert_link.png")) #$NON-NLS-1$
    # end buildInsertLinkMenuItem()

    def buildCopyLinkLocationMenuItem(self, menuModel, gravity, parentId):
        resourceReg = getResourceRegistry()
        mid = menuModel.addMenuItemWithAction(_extstr(u"blogcontenteditorlinkmenumodel.CopyLinkLocation"),  gravity, ZBlogPostCopyLinkLocationAction(), parentId ) #$NON-NLS-1$
        menuModel.setMenuItemBitmap(mid, resourceReg.getBitmap(u"images/common/menu/link/copylinklocation.png")) #$NON-NLS-1$
    # end buildCopyLinkLocationMenuItem()

    def buildEditObjectsMenuItems(self, menuModel, gravity, parentId):
        resourceReg = getResourceRegistry()
        label = _extstr(u"blogcontenteditorlinkmenumodel.EditLink") #$NON-NLS-1$
        mid = menuModel.addMenuItemWithAction(u"%s\tCtrl+L" % label, gravity, ZBlogPostEditLinkAction(), parentId ) #$NON-NLS-1$
        menuModel.setMenuItemBitmap(mid, resourceReg.getBitmap(u"images/editors/blogeditor/designer/toolbar/16x16/insert_link.png")) #$NON-NLS-1$

        label = _extstr(u"blogcontenteditorlinkmenumodel.ConvertLink") #$NON-NLS-1$
        mid = menuModel.addMenuItemWithAction(u"%s" % label, gravity+1, ZConvertProductLinkAction(), parentId ) #$NON-NLS-1$
        menuModel.setMenuItemBitmap(mid, resourceReg.getBitmap(u"images/editors/blogeditor/menu/convert_link.png")) #$NON-NLS-1$
    # end buildEditObjectsMenuItems()

    def buildRemoveLinkMenuItem(self, menuModel, gravity, parentId):
        menuModel.addSeparator(gravity)
        resourceReg = getResourceRegistry()
        mid = menuModel.addMenuItemWithAction(_extstr(u"blogcontenteditorlinkmenumodel.RemoveLink"),  gravity+1, ZBlogPostRemoveLinkContextMenuAction(), parentId ) #$NON-NLS-1$
        menuModel.setMenuItemBitmap(mid, resourceReg.getBitmap(u"images/common/menu/link/link_delete.png")) #$NON-NLS-1$
    # end buildRemoveLinkMenuItem()

    def buildLinkToFormattersMenu(self, menuModel, gravity, parentId):
        linkService = getApplicationModel().getService(IZBlogAppServiceIDs.LINKS_SERVICE_ID)
        formatterTypes = linkService.listFormatterTypes()
        if not formatterTypes:
            return
        linkToParentId = menuModel.addMenu(_extstr(u"blogcontenteditorlinkmenumodel.LinkTo"), gravity, parentId) #$NON-NLS-1$
        for formatterType in formatterTypes:
            formattersMenuId = menuModel.addMenu(formatterType, gravity, linkToParentId) #$NON-NLS-1$
            for linkFormatter in linkService.listFormattersByType(formatterType):
                mid = menuModel.addMenuItemWithAction(linkFormatter.getName(),  gravity+1, ZBlogPostCreateLinkFromFormatterAction(linkFormatter), formattersMenuId ) #$NON-NLS-1$
                icon = linkFormatter.getIconAsBitmap()
                if icon:
                    menuModel.setMenuItemBitmap(mid, icon)
        # add simple links
        for link in linkService.listLinks(10):
            mid = menuModel.addMenuItemWithAction(link.getName(),  gravity+1, ZBlogPostCreateLinkNoUiAction(link.getUrl(), link.getRel()), linkToParentId ) #$NON-NLS-1$
            icon = link.getIconAsBitmap()
            if icon:
                menuModel.setMenuItemBitmap(mid, icon)

    # end buildLinkToFormattersMenu()

    def getLinkLocation(self, linkContext):
        linkLocation = None
        if linkContext is not None and linkContext.canEditLink():
            attrs = linkContext.getLinkAttributes()
            if attrs.has_key(u"href"): #$NON-NLS-1$
                linkLocation = attrs[u"href"]    #$NON-NLS-1$
        return linkLocation
    # end getLinkLocation()
    
    def buildConvertLinkToEmdedMenuItem(self, menuModel, gravity, parentId, url):
        resourceReg = getResourceRegistry()
        label = _extstr(u"blogcontenteditorlinkmenumodel.CreateEmbedContent") #$NON-NLS-1$
        action = ZConvertLinkToEmbedAction()
        if url:
            name = action.getDnDHandlerName(url)
            if name:
                label = label + u" - %s" % name #$NON-NLS-1$
        mid = menuModel.addMenuItemWithAction(label, gravity+1, action, parentId ) #$NON-NLS-1$
        menuModel.setMenuItemBitmap(mid, resourceReg.getBitmap(u"images/editors/blogeditor/menu/create_embed.png")) #$NON-NLS-1$
    # end buildConvertLinkMenuItem()
    
# end ZLinkMenuModelBuilder