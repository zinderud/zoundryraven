from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZBlogPostTableCommandsAction
from zoundry.appframework.ui.widgets.controls.advanced.htmleditcontrol import IZXHTMLEditControlTableContext
from zoundry.appframework.global_services import getResourceRegistry
from zoundry.appframework.ui.widgets.controls.common.menu.menumodel import ZPluginMenuModel
from zoundry.blogapp.constants import IZBlogAppMenuIds
from zoundry.blogapp.messages import _extstr

#-------------------------------------------
# Menu model used for table editing/creation
#-------------------------------------------
class ZTableModelBuilder:
    
    def createToolbarTableMenuModel(self):
        menuModel = ZPluginMenuModel(IZBlogAppMenuIds.ZID_INSERT_TABLE_MENU)
        self.buildTableMenu(menuModel, None)
        return menuModel
    # end createToolbarTableMenuModel()

    def buildTableMenu(self, menuModel, parentId): #@UnusedVariable
        resourceReg = getResourceRegistry()
        #parentId = menuModel.addMenu("TableStuff", 1)
        menuId = menuModel.addMenuItemWithAction(_extstr(u"blogcontenteditortablemenumodel.InsertTable"), 4,  ZBlogPostTableCommandsAction(IZXHTMLEditControlTableContext.INSERT_TABLE), parentId) #$NON-NLS-1$
        menuModel.setMenuItemBitmap(menuId, resourceReg.getBitmap(u"images/editors/blogeditor/designer/toolbar/16x16/insert_table.png")) #$NON-NLS-1$
        menuModel.addMenuItemWithAction(u"Edit Table Settings", 5,  ZBlogPostTableCommandsAction(IZXHTMLEditControlTableContext.EDIT_TABLE_ATTRS), parentId) #$NON-NLS-1$
        menuModel.addSeparator(8, parentId)
        
        menuModel.addMenuItemWithAction(u"Insert Header", 10,  ZBlogPostTableCommandsAction(IZXHTMLEditControlTableContext.INSERT_HEADER), parentId) #$NON-NLS-1$
        menuModel.addMenuItemWithAction(u"Insert Footer", 11,  ZBlogPostTableCommandsAction(IZXHTMLEditControlTableContext.INSERT_FOOTER), parentId) #$NON-NLS-1$
        menuModel.addMenuItemWithAction(u"Insert Caption", 12,  ZBlogPostTableCommandsAction(IZXHTMLEditControlTableContext.INSERT_CAPTION), parentId) #$NON-NLS-1$
        menuModel.addSeparator(18, parentId)
        
        menuModel.addMenuItemWithAction(u"Insert Row Above", 20,  ZBlogPostTableCommandsAction(IZXHTMLEditControlTableContext.INSERT_ROW_ABOVE), parentId) #$NON-NLS-1$
        menuModel.addMenuItemWithAction(u"Insert Row Below", 22,  ZBlogPostTableCommandsAction(IZXHTMLEditControlTableContext.INSERT_ROW_BELOW), parentId) #$NON-NLS-1$
        menuModel.addMenuItemWithAction(u"Insert Column Left", 24,  ZBlogPostTableCommandsAction(IZXHTMLEditControlTableContext.INSERT_COL_LEFT), parentId) #$NON-NLS-1$
        menuModel.addMenuItemWithAction(u"Insert Column Right", 26,  ZBlogPostTableCommandsAction(IZXHTMLEditControlTableContext.INSERT_COL_RIGHT),parentId) #$NON-NLS-1$
        menuModel.addSeparator(28, parentId)
    
        menuModel.addMenuItemWithAction(u"Move Row Above", 30,  ZBlogPostTableCommandsAction(IZXHTMLEditControlTableContext.MOVE_ROW_ABOVE), parentId) #$NON-NLS-1$
        menuModel.addMenuItemWithAction(u"Move Row Below", 32,  ZBlogPostTableCommandsAction(IZXHTMLEditControlTableContext.MOVE_ROW_BELOW), parentId) #$NON-NLS-1$
        menuModel.addMenuItemWithAction(u"Move Column Left", 34,  ZBlogPostTableCommandsAction(IZXHTMLEditControlTableContext.MOVE_COL_LEFT), parentId) #$NON-NLS-1$
        menuModel.addMenuItemWithAction(u"Move Column Right", 36,  ZBlogPostTableCommandsAction(IZXHTMLEditControlTableContext.MOVE_COL_RIGHT), parentId) #$NON-NLS-1$
        menuModel.addSeparator(38, parentId)
    
        menuModel.addMenuItemWithAction(u"Clear Cell", 40,  ZBlogPostTableCommandsAction(IZXHTMLEditControlTableContext.CLEAR_CELL), parentId) #$NON-NLS-1$
        menuModel.addMenuItemWithAction(u"Delete Row", 42,  ZBlogPostTableCommandsAction(IZXHTMLEditControlTableContext.DELETE_ROW), parentId) #$NON-NLS-1$
        menuModel.addMenuItemWithAction(u"Delete Column", 42,  ZBlogPostTableCommandsAction(IZXHTMLEditControlTableContext.DELETE_COL),parentId) #$NON-NLS-1$
        return menuModel
    # end buildTableMenu()
#end ZTableModelBuilder