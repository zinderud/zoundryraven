from zoundry.blogapp.messages import _extstr
from zoundry.appframework.global_services import getResourceRegistry
from zoundry.appframework.ui.widgets.controls.common.menu.menumodel import ZMenuBarModel
from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZBlogPostCopyAction
from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZBlogPostCutAction
from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZBlogPostFindReplaceAction
from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZBlogPostPasteAction
from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZBlogPostPasteXhtmlAction
from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZBlogPostRedoAction
from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZBlogPostSaveAction
from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZBlogPostSelectAllAction
from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZBlogPostUndoAction

# ------------------------------------------------------------------------------
# The menu bar model used by the blog post editor.
# ------------------------------------------------------------------------------
class ZBlogPostEditorMenuBarModel(ZMenuBarModel):
    
    def __init__(self, editor):
        self.editor = editor
        ZMenuBarModel.__init__(self)

        fileMID = self.addMenu(_extstr(u"blogpostmenubar._File"), 0) #$NON-NLS-1$
        editMID = self.addMenu(_extstr(u"blogpostmenubar._Edit"), 0) #$NON-NLS-1$
        saveMID = self.addMenuItemWithAction(_extstr(u"blogpostmenubar._Save"), 10, ZBlogPostSaveAction(), fileMID) #$NON-NLS-1$
        self.addMenuItemWithCallback(_extstr(u"blogpostmenubar._Close"), 100, self.editor.onMenuClose, fileMID) #$NON-NLS-1$

        undoMID = self.addMenuItemWithAction(_extstr(u"blogpostmenubar._Undo"),  90, ZBlogPostUndoAction(), editMID) #$NON-NLS-1$
        redoMID = self.addMenuItemWithAction(_extstr(u"blogpostmenubar._Redo"),  91, ZBlogPostRedoAction(), editMID) #$NON-NLS-1$
        self.addSeparator(92, editMID)

        cutMID = self.addMenuItemWithAction(_extstr(u"blogpostmenubar.Cu_t"),  100, ZBlogPostCutAction(), editMID) #$NON-NLS-1$
        copyMID = self.addMenuItemWithAction(_extstr(u"blogpostmenubar._Copy"), 105, ZBlogPostCopyAction(), editMID) #$NON-NLS-1$
        pasteMID = self.addMenuItemWithAction(_extstr(u"blogpostmenubar._Paste"), 110,ZBlogPostPasteAction(), editMID) #$NON-NLS-1$
        pasteXhtmlMID = self.addMenuItemWithAction(_extstr(u"blogpostmenubar.PasteAs_Html"), 112, ZBlogPostPasteXhtmlAction(), editMID) #@UnusedVariable #$NON-NLS-1$
        self.addSeparator(115, editMID)
        selectAllMID = self.addMenuItemWithAction(_extstr(u"blogpostmenubar.Select_All"), 120, ZBlogPostSelectAllAction(), editMID) #@UnusedVariable #$NON-NLS-1$
        self.addSeparator(122, editMID)
        findMID = self.addMenuItemWithAction(_extstr(u"blogpostmenubar._Find"), 125, ZBlogPostFindReplaceAction(), editMID) #@UnusedVariable #$NON-NLS-1$

        resourceReg = getResourceRegistry()
        self.setMenuItemBitmap(saveMID, resourceReg.getBitmap(u"images/editors/blogeditor/menu/save.png")) #$NON-NLS-1$
        self.setMenuItemBitmap(undoMID, resourceReg.getBitmap(u"images/editors/blogeditor/menu/undo.png")) #$NON-NLS-1$
        self.setMenuItemBitmap(redoMID, resourceReg.getBitmap(u"images/editors/blogeditor/menu/redo.png")) #$NON-NLS-1$
        self.setMenuItemBitmap(cutMID, resourceReg.getBitmap(u"images/editors/blogeditor/menu/cut.png")) #$NON-NLS-1$
        self.setMenuItemBitmap(copyMID, resourceReg.getBitmap(u"images/editors/blogeditor/menu/copy.png")) #$NON-NLS-1$
        self.setMenuItemBitmap(pasteMID, resourceReg.getBitmap(u"images/editors/blogeditor/menu/paste.png")) #$NON-NLS-1$

    # end __init__()

# end ZBlogPostEditorMenuBarModel
