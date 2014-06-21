from zoundry.appframework.ui.widgets.controls.common.acceleratortable import ZAcceleratorEntry
from zoundry.appframework.ui.widgets.controls.common.acceleratortable import ZAcceleratorTable
from zoundry.blogapp.constants import IZBlogAppAcceleratorIds
from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZBlogPostCopyAction
from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZBlogPostCutAction
from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZBlogPostFindReplaceAction
from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZBlogPostPasteAction
from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZBlogPostPasteXhtmlAction
from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZBlogPostRedoAction
from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZBlogPostSaveAction
from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZBlogPostUndoAction
import wx

# ------------------------------------------------------------------------------
# Accelerator table for the blog post editor.
# ------------------------------------------------------------------------------
class ZBlogPostEditorAcceleratorTable(ZAcceleratorTable):

    def __init__(self, context):
        self.context = context
        ZAcceleratorTable.__init__(self, IZBlogAppAcceleratorIds.ZID_BLOG_POST_EDITOR_ACCEL)
    # end __init__()

    def _createActionContext(self):
        return self.context
    # end _createActionContext()

    def _loadAdditionalEntries(self):
        # FIXME (PJ) add short cut for Ctrl+N (new document)
        return [
            ZAcceleratorEntry(wx.ACCEL_CTRL, ord(u'S'), ZBlogPostSaveAction() ), #$NON-NLS-1$
            ZAcceleratorEntry(wx.ACCEL_CTRL, ord(u'X'), ZBlogPostCutAction() ), #$NON-NLS-1$
            ZAcceleratorEntry(wx.ACCEL_CTRL, ord(u'C'), ZBlogPostCopyAction() ), #$NON-NLS-1$
            ZAcceleratorEntry(wx.ACCEL_CTRL, ord(u'V'), ZBlogPostPasteAction() ), #$NON-NLS-1$

#            ZAcceleratorEntry(wx.ACCEL_CTRL, wx.WXK_INSERT, ZBlogPostCopyAction() ), #$NON-NLS-1$
#            ZAcceleratorEntry(wx.ACCEL_SHIFT, wx.WXK_INSERT, ZBlogPostPasteAction() ), #$NON-NLS-1$
#            ZAcceleratorEntry(wx.ACCEL_SHIFT, wx.WXK_DELETE, ZBlogPostCutAction() ), #$NON-NLS-1$

            ZAcceleratorEntry(wx.ACCEL_CTRL + wx.ACCEL_SHIFT, ord(u'V'), ZBlogPostPasteXhtmlAction() ), #$NON-NLS-1$
            ZAcceleratorEntry(wx.ACCEL_CTRL, ord(u'Z'), ZBlogPostUndoAction()), #$NON-NLS-1$
            ZAcceleratorEntry(wx.ACCEL_CTRL, ord(u'Y'), ZBlogPostRedoAction()), #$NON-NLS-1$
            # Find/Replace
            ZAcceleratorEntry(wx.ACCEL_CTRL, ord(u'F'), ZBlogPostFindReplaceAction()), #$NON-NLS-1$
            ZAcceleratorEntry(wx.ACCEL_NORMAL, wx.WXK_F3, ZBlogPostFindReplaceAction()),
        ]
    # end _loadAdditionalEntries()

# end ZBlogPostEditorAcceleratorTable
