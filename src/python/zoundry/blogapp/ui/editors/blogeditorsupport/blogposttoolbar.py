from zoundry.appframework.global_services import getResourceRegistry
from zoundry.appframework.ui.widgets.controls.common.toolbar.toolbarmodel import ZPluginToolBarModel
from zoundry.blogapp.constants import IZBlogAppToolBarIds
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZBlogPostCopyAction
from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZBlogPostCutAction
from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZBlogPostPasteAction
from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZBlogPostPublishAction
from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZBlogPostRedoAction
from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZBlogPostSaveAction
from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZBlogPostUndoAction
from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZBlogPostViewOnlineAction

# ------------------------------------------------------------------------------
# An implementation of a tool bar for use in the blog post editor.
# ------------------------------------------------------------------------------
class ZBlogPostEditorToolBarModel(ZPluginToolBarModel):

    def __init__(self):
        ZPluginToolBarModel.__init__(self, IZBlogAppToolBarIds.ZID_BLOG_EDITOR_TOOLBAR)

        self.setDefaultToolSize(32)

        resourceReg = getResourceRegistry()
        toolId = self.addItemWithAction(_extstr(u"blogeditor.Save"), 10, ZBlogPostSaveAction() ) #$NON-NLS-1$
        self.setToolDescription(toolId, _extstr(u"blogeditor.SaveDesc")) #$NON-NLS-1$
        self.addToolBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/toolbar/16x16/save.png")) #$NON-NLS-1$
        self.addToolDisabledBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/toolbar/16x16/save_disabled.png")) #$NON-NLS-1$
        self.addToolBitmap(toolId, 24, resourceReg.getBitmap(u"images/editors/blogeditor/toolbar/24x24/save.png")) #$NON-NLS-1$
        self.addToolDisabledBitmap(toolId, 24, resourceReg.getBitmap(u"images/editors/blogeditor/toolbar/24x24/save_disabled.png")) #$NON-NLS-1$
        self.addToolBitmap(toolId, 32, resourceReg.getBitmap(u"images/editors/blogeditor/toolbar/32x32/save.png")) #$NON-NLS-1$
        self.addToolDisabledBitmap(toolId, 32, resourceReg.getBitmap(u"images/editors/blogeditor/toolbar/32x32/save_disabled.png")) #$NON-NLS-1$

        self.addSeparator(50)

        toolId = self.addItemWithAction(_extstr(u"blogeditor.Cut"), 100, ZBlogPostCutAction() ) #$NON-NLS-1$
        self.setToolDescription(toolId, _extstr(u"blogeditor.CutDesc")) #$NON-NLS-1$
        self.addToolBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/toolbar/16x16/cut.png")) #$NON-NLS-1$
        self.addToolDisabledBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/toolbar/16x16/cut_disabled.png")) #$NON-NLS-1$
        self.addToolBitmap(toolId, 24, resourceReg.getBitmap(u"images/editors/blogeditor/toolbar/24x24/cut.png")) #$NON-NLS-1$
        self.addToolDisabledBitmap(toolId, 24, resourceReg.getBitmap(u"images/editors/blogeditor/toolbar/24x24/cut_disabled.png")) #$NON-NLS-1$
        self.addToolBitmap(toolId, 32, resourceReg.getBitmap(u"images/editors/blogeditor/toolbar/32x32/cut.png")) #$NON-NLS-1$
        self.addToolDisabledBitmap(toolId, 32, resourceReg.getBitmap(u"images/editors/blogeditor/toolbar/32x32/cut_disabled.png")) #$NON-NLS-1$

        toolId = self.addItemWithAction(_extstr(u"blogeditor.Copy"), 101, ZBlogPostCopyAction() ) #$NON-NLS-1$
        self.setToolDescription(toolId, _extstr(u"blogeditor.CopyDesc")) #$NON-NLS-1$
        self.addToolBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/toolbar/16x16/copy.png")) #$NON-NLS-1$
        self.addToolDisabledBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/toolbar/16x16/copy_disabled.png")) #$NON-NLS-1$
        self.addToolBitmap(toolId, 24, resourceReg.getBitmap(u"images/editors/blogeditor/toolbar/24x24/copy.png")) #$NON-NLS-1$
        self.addToolDisabledBitmap(toolId, 24, resourceReg.getBitmap(u"images/editors/blogeditor/toolbar/24x24/copy_disabled.png")) #$NON-NLS-1$
        self.addToolBitmap(toolId, 32, resourceReg.getBitmap(u"images/editors/blogeditor/toolbar/32x32/copy.png")) #$NON-NLS-1$
        self.addToolDisabledBitmap(toolId, 32, resourceReg.getBitmap(u"images/editors/blogeditor/toolbar/32x32/copy_disabled.png")) #$NON-NLS-1$

        toolId = self.addItemWithAction(_extstr(u"blogeditor.Paste"), 102,  ZBlogPostPasteAction() ) #$NON-NLS-1$
        self.setToolDescription(toolId, _extstr(u"blogeditor.PasteDesc")) #$NON-NLS-1$
        self.addToolBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/toolbar/16x16/paste.png")) #$NON-NLS-1$
        self.addToolDisabledBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/toolbar/16x16/paste_disabled.png")) #$NON-NLS-1$
        self.addToolBitmap(toolId, 24, resourceReg.getBitmap(u"images/editors/blogeditor/toolbar/24x24/paste.png")) #$NON-NLS-1$
        self.addToolDisabledBitmap(toolId, 24, resourceReg.getBitmap(u"images/editors/blogeditor/toolbar/24x24/paste_disabled.png")) #$NON-NLS-1$
        self.addToolBitmap(toolId, 32, resourceReg.getBitmap(u"images/editors/blogeditor/toolbar/32x32/paste.png")) #$NON-NLS-1$
        self.addToolDisabledBitmap(toolId, 32, resourceReg.getBitmap(u"images/editors/blogeditor/toolbar/32x32/paste_disabled.png")) #$NON-NLS-1$

        self.addSeparator(110)

        toolId = self.addItemWithAction(_extstr(u"blogeditor.Undo"), 111,  ZBlogPostUndoAction() ) #$NON-NLS-1$
        self.setToolDescription(toolId, _extstr(u"blogeditor.UndoDesc")) #$NON-NLS-1$
        self.addToolBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/toolbar/16x16/undo.png")) #$NON-NLS-1$
        self.addToolDisabledBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/toolbar/16x16/undo_disabled.png")) #$NON-NLS-1$
        self.addToolBitmap(toolId, 24, resourceReg.getBitmap(u"images/editors/blogeditor/toolbar/24x24/undo.png")) #$NON-NLS-1$
        self.addToolDisabledBitmap(toolId, 24, resourceReg.getBitmap(u"images/editors/blogeditor/toolbar/24x24/undo_disabled.png")) #$NON-NLS-1$
        self.addToolBitmap(toolId, 32, resourceReg.getBitmap(u"images/editors/blogeditor/toolbar/32x32/undo.png")) #$NON-NLS-1$
        self.addToolDisabledBitmap(toolId, 32, resourceReg.getBitmap(u"images/editors/blogeditor/toolbar/32x32/undo_disabled.png")) #$NON-NLS-1$

        toolId = self.addItemWithAction(_extstr(u"blogeditor.Redo"), 112,  ZBlogPostRedoAction() ) #$NON-NLS-1$
        self.setToolDescription(toolId, _extstr(u"blogeditor.RedoDesc")) #$NON-NLS-1$
        self.addToolBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/toolbar/16x16/redo.png")) #$NON-NLS-1$
        self.addToolDisabledBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/toolbar/16x16/redo_disabled.png")) #$NON-NLS-1$
        self.addToolBitmap(toolId, 24, resourceReg.getBitmap(u"images/editors/blogeditor/toolbar/24x24/redo.png")) #$NON-NLS-1$
        self.addToolDisabledBitmap(toolId, 24, resourceReg.getBitmap(u"images/editors/blogeditor/toolbar/24x24/redo_disabled.png")) #$NON-NLS-1$
        self.addToolBitmap(toolId, 32, resourceReg.getBitmap(u"images/editors/blogeditor/toolbar/32x32/redo.png")) #$NON-NLS-1$
        self.addToolDisabledBitmap(toolId, 32, resourceReg.getBitmap(u"images/editors/blogeditor/toolbar/32x32/redo_disabled.png")) #$NON-NLS-1$

        self.addSeparator(150)

        toolId = self.addItemWithAction(_extstr(u"blogposttoolbar.Publish"), 200,  ZBlogPostPublishAction() ) #$NON-NLS-1$
        self.setToolDescription(toolId, _extstr(u"blogeditor.PublishContentToYourBlog")) #$NON-NLS-1$
        self.addToolBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/toolbar/16x16/publish.png")) #$NON-NLS-1$
        self.addToolDisabledBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/toolbar/16x16/publish_disabled.png")) #$NON-NLS-1$
        self.addToolBitmap(toolId, 24, resourceReg.getBitmap(u"images/editors/blogeditor/toolbar/24x24/publish.png")) #$NON-NLS-1$
        self.addToolDisabledBitmap(toolId, 24, resourceReg.getBitmap(u"images/editors/blogeditor/toolbar/24x24/publish_disabled.png")) #$NON-NLS-1$
        self.addToolBitmap(toolId, 32, resourceReg.getBitmap(u"images/editors/blogeditor/toolbar/32x32/publish.png")) #$NON-NLS-1$
        self.addToolDisabledBitmap(toolId, 32, resourceReg.getBitmap(u"images/editors/blogeditor/toolbar/32x32/publish_disabled.png")) #$NON-NLS-1$

        toolId = self.addDropDownItemWithAction(_extstr(u"blogposttoolbar.ViewOnline"), 205,  ZBlogPostViewOnlineAction() ) #$NON-NLS-1$
        self.setToolDescription(toolId, _extstr(u"blogposttoolbar.ViewPostOnline")) #$NON-NLS-1$
        self.addToolBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/toolbar/16x16/viewOnline.png")) #$NON-NLS-1$
        self.addToolDisabledBitmap(toolId, 16, resourceReg.getBitmap(u"images/editors/blogeditor/toolbar/16x16/viewOnline_disabled.png")) #$NON-NLS-1$
        self.addToolBitmap(toolId, 24, resourceReg.getBitmap(u"images/editors/blogeditor/toolbar/24x24/viewOnline.png")) #$NON-NLS-1$
        self.addToolDisabledBitmap(toolId, 24, resourceReg.getBitmap(u"images/editors/blogeditor/toolbar/24x24/viewOnline_disabled.png")) #$NON-NLS-1$
        self.addToolBitmap(toolId, 32, resourceReg.getBitmap(u"images/editors/blogeditor/toolbar/32x32/viewOnline.png")) #$NON-NLS-1$
        self.addToolDisabledBitmap(toolId, 32, resourceReg.getBitmap(u"images/editors/blogeditor/toolbar/32x32/viewOnline_disabled.png")) #$NON-NLS-1$
    # end __init__()

# end ZBlogPostEditorToolBarModel
