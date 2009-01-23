from zoundry.blogapp.ui.menus.blogeditor.blogeditortoolbarmodel import ZBlogContentEditorToolbarModel
from zoundry.blogapp.ui.editors.blogeditorctrls.basecontenteditor import ZBlogPostContentEditorBase
from zoundry.blogapp.ui.editors.blogeditorctrls.styledxhtmlblogposteditcontrol import ZStyledXhtmlBlogPostEditControl

# ------------------------------------------------------------------------------
# Concrete implementations of xhtml source content editor based on the wx
# scintilla control.
# ------------------------------------------------------------------------------
class ZBlogPostXhtmlContentEditor(ZBlogPostContentEditorBase):

    def __init__(self, parentWindow, zblogPostEditor, model):
        ZBlogPostContentEditorBase.__init__(self, parentWindow, zblogPostEditor, model)
    # end __init__()

    def _createContentEditCtrl(self, parent):
        return ZStyledXhtmlBlogPostEditControl(parent)
    # end _createContentEditCtrl()
    
    def _createToolBarModel(self):
        toolbarModel = ZBlogContentEditorToolbarModel(False)
        return toolbarModel
    # end _createToolBarModel()    

# end ZBlogPostXhtmlContentEditor
