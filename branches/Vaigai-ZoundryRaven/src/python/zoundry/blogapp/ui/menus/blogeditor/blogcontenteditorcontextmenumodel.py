from zoundry.appframework.global_services import getResourceRegistry
from zoundry.appframework.ui.widgets.controls.common.menu.menumodel import ZPluginMenuModel
from zoundry.blogapp.constants import IZBlogAppMenuIds
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZBlogPostCopyAction
from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZBlogPostCutAction
from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZBlogPostPasteAction
from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZBlogPostPasteXhtmlAction
from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZBlogPostRedoAction
from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZBlogPostRemoveExtEntryMarkerContextMenuAction
from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZBlogPostSelectAllAction
from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZBlogPostUndoAction
from zoundry.blogapp.ui.menus.blogeditor.imagemenumodel import ZImageMenuModelBuilder
from zoundry.blogapp.ui.menus.blogeditor.linkmenumodel import ZLinkMenuModelBuilder
from zoundry.blogapp.ui.menus.blogeditor.tablemenumodel import ZTableModelBuilder

#-----------------------------------------------------
# Blog post content editor right click context menu
#-----------------------------------------------------
class ZBlogContentEditorContextMenuModel(ZPluginMenuModel):

    def __init__(self):
        ZPluginMenuModel.__init__(self, IZBlogAppMenuIds.ZID_BLOG_EDITOR_DESIGNER_CONTEXT_MENU)
        self.zXHTMLEditControlLinkContext = None
        self.zXHTMLEditControlImageContext = None
        self.zXHTMLEditControlTableContext = None
        self.removeExtEntryMarker = False
        self.buildAllDone = False
    # end __init__()

    def initialize(self, linkCtx, imgCtx, tableCtx, removeExtEntryMarker):
        self.zXHTMLEditControlLinkContext = linkCtx
        self.zXHTMLEditControlImageContext = imgCtx
        self.zXHTMLEditControlTableContext = tableCtx
        self.removeExtEntryMarker = removeExtEntryMarker
        self._buildAll()
    # end initialize

    def _buildAll(self):
        if not self.buildAllDone:
            self._buildStaticModel()
            self._buildDynamicModel()
            self.buildAllDone = True
    # end _buildAll()

    def _buildStaticModel(self):
        resourceReg = getResourceRegistry()

        undoMID = self.addMenuItemWithAction(_extstr(u"blogcontenteditorcontextmenumodel._Undo"),  90, ZBlogPostUndoAction() ) #$NON-NLS-1$
        redoMID = self.addMenuItemWithAction(_extstr(u"blogcontenteditorcontextmenumodel._Redo"),  91, ZBlogPostRedoAction() ) #$NON-NLS-1$
        self.addSeparator(92)
        cutMID = self.addMenuItemWithAction(_extstr(u"blogcontenteditorcontextmenumodel.Cu_t"),  100, ZBlogPostCutAction() ) #$NON-NLS-1$
        copyMID = self.addMenuItemWithAction(_extstr(u"blogcontenteditorcontextmenumodel._Copy"), 105, ZBlogPostCopyAction()) #$NON-NLS-1$
        # img and link url copy
        self.buildCopyUrlLocationMenuItems(self.zXHTMLEditControlLinkContext, self.zXHTMLEditControlImageContext, 106, None, False)
        pasteMID = self.addMenuItemWithAction(_extstr(u"blogcontenteditorcontextmenumodel._Paste"), 110,ZBlogPostPasteAction() ) #$NON-NLS-1$
        pasteXhtmlMID = self.addMenuItemWithAction(_extstr(u"blogcontenteditorcontextmenumodel.Paste_as__Html"), 112,ZBlogPostPasteXhtmlAction()) #@UnusedVariable #$NON-NLS-1$
        self.addSeparator(115)
        selectAllMID = self.addMenuItemWithAction(_extstr(u"blogcontenteditorcontextmenumodel.Select__All"), 116, ZBlogPostSelectAllAction()) #@UnusedVariable #$NON-NLS-1$

        self.setMenuItemBitmap(cutMID, resourceReg.getBitmap(u"images/editors/blogeditor/menu/cut.png")) #$NON-NLS-1$
        self.setMenuItemBitmap(copyMID, resourceReg.getBitmap(u"images/editors/blogeditor/menu/copy.png")) #$NON-NLS-1$
        self.setMenuItemBitmap(pasteMID, resourceReg.getBitmap(u"images/editors/blogeditor/menu/paste.png")) #$NON-NLS-1$
        self.setMenuItemBitmap(undoMID, resourceReg.getBitmap(u"images/editors/blogeditor/menu/undo.png")) #$NON-NLS-1$
        self.setMenuItemBitmap(redoMID, resourceReg.getBitmap(u"images/editors/blogeditor/menu/redo.png")) #$NON-NLS-1$
    # end _buildStaticModel()

    def _buildDynamicModel(self):
        if self.zXHTMLEditControlLinkContext or self.zXHTMLEditControlImageContext or self.zXHTMLEditControlTableContext:
            self.addSeparator(199)
        if self.zXHTMLEditControlLinkContext:
            self._buildLinkMenu(200)
        if self.zXHTMLEditControlImageContext:
            self._buildImageMenu(210)
        if self.zXHTMLEditControlTableContext:
            self.buildTableMenu(220)
        self._buildRemoveElemMenuItem(240)
    # end _buildDynamicModel()

    def buildTableMenu(self, gravity):
        parentId = self.addMenu(_extstr(u"blogcontenteditortablemenumodel.Table"), gravity) #$NON-NLS-1$
        resourceReg = getResourceRegistry()
        self.setMenuItemBitmap(parentId, resourceReg.getBitmap(u"images/editors/blogeditor/designer/toolbar/16x16/table.png")) #$NON-NLS-1$
        ZTableModelBuilder().buildTableMenu(self, parentId)
    # end buildTableMenu()

    def _buildLinkMenu(self, gravity):
        parentId = self.addMenu(_extstr(u"blogcontenteditorlinkmenumodel.Link"), gravity) #$NON-NLS-1$
        url = None
        linkMenuBuilder = ZLinkMenuModelBuilder()
        if self.zXHTMLEditControlLinkContext:
            url = linkMenuBuilder.getLinkLocation(self.zXHTMLEditControlLinkContext)            
        linkMenuBuilder.buildLinkMenu(self, parentId, url)
    # end _buildLinkMenu

    def _buildImageMenu(self, gravity):
        parentId = self.addMenu(_extstr(u"blogcontenteditorimagemenumodel.Image"), gravity) #$NON-NLS-1$
        ZImageMenuModelBuilder().buildImageMenu(self, parentId)
    # end _buildImageMenu

    def buildCopyUrlLocationMenuItems(self, linkContext, imageContext, gravity, parentId, addSeparater):
        linkMenuBuilder = ZLinkMenuModelBuilder()
        imageMenuBuilder = ZImageMenuModelBuilder()
        linkLocation = linkMenuBuilder.getLinkLocation(linkContext)
        imageLocation = imageMenuBuilder.getImageLocation(imageContext)
        if not linkLocation and not imageLocation:
            return
        if addSeparater:
            self.addSeparator(gravity)
            gravity = gravity + 1
        if linkLocation:
            linkMenuBuilder.buildCopyLinkLocationMenuItem(self, gravity, parentId)
        if imageLocation:
            imageMenuBuilder.buildCopyImageLocationMenuItem(self, gravity, parentId)
    # end buildCopyUrlLocationMenuItems()

    def _buildRemoveElemMenuItem(self, gravity):  
        if self.zXHTMLEditControlLinkContext:      
            linkMenuBuilder = ZLinkMenuModelBuilder()
            linkLocation = linkMenuBuilder.getLinkLocation(self.zXHTMLEditControlLinkContext)
            if linkLocation:
                linkMenuBuilder.buildRemoveLinkMenuItem(self, gravity, None)
    # end _buildRemoveElemMenuItem()

    def _buildRemoveExtEntryMarker(self):
        self.addSeparator(150)
        resourceReg = getResourceRegistry()
        mid = self.addMenuItemWithAction(_extstr(u"blogcontenteditorcontextmenumodel.Remove_Extended_Entry_Marker"),  152, ZBlogPostRemoveExtEntryMarkerContextMenuAction() ) #$NON-NLS-1$
        self.setMenuItemBitmap(mid, resourceReg.getBitmap(u"images/editors/blogeditor/designer/toolbar/16x16/remove_extentry.png")) #$NON-NLS-1$
    # end _buildRemoveExtEntryMarker()

# end ZBlogContentEditorContextMenuModel
