from zoundry.blogapp.ui.util.editorutil import ZLinkUiUtil
from zoundry.blogapp.ui.util.editorutil import ZImageUiUtil
from zoundry.appframework.ui.events.editcontrolevents import IZEditControlEvents
from zoundry.appframework.ui.events.toolbarevents import ZEVT_TOOLBAR_RESIZE
from zoundry.appframework.ui.widgets.controls.common.toolbar.toolbar import ZToolBar
from zoundry.appframework.ui.widgets.controls.common.toolbar.toolbarmodel import ZModelBasedToolBarContentProvider
from zoundry.appframework.ui.widgets.controls.common.toolbar.toolbarmodel import ZModelBasedToolBarEventHandler
from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZBlogPostEditorToolBarActionContext
from zoundry.blogapp.ui.editors.blogeditorctrls.basecontenteditor import ZBlogPostContentEditorBase
from zoundry.blogapp.ui.editors.blogeditorctrls.mshtmlblogposteditcontrol import ZMSHTMLBlogPostEditControl
from zoundry.blogapp.ui.menus.blogeditor.blogeditortoolbarmodel import ZBlogWysiwygEditorContextToolbarModel
import wx

# ------------------------------------------------------------------------------
# Concrete implementations of WsyiWyg content editor based on the mshtml control
# ------------------------------------------------------------------------------
class ZBlogPostWysiwygContentEditor(ZBlogPostContentEditorBase):

    def __init__(self, parentWindow, zblogPostEditor, model):
        ZBlogPostContentEditorBase.__init__(self, parentWindow, zblogPostEditor, model)

        self.metaDataWidget.titleText.SetFocus()
    # end __init__()

    def _createContentEditCtrl(self, parent):
        return ZMSHTMLBlogPostEditControl(parent)
    # end _createContentEditCtrl()

    def _createWidgets(self):
        ZBlogPostContentEditorBase._createWidgets(self)
        self.contextToolBar = self._createContextToolBar()
    # end _createWidgets

    def _layoutWidgets(self):
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.metaDataWidget, 0, wx.EXPAND)
        self.sizer.Add(self.toolBar, 0, wx.EXPAND)
        self.sizer.Add(self.contextToolBar, 0, wx.EXPAND)
        self.sizer.Add(self.tbStaticLine, 0, wx.EXPAND)
        self.sizer.Add(self.contentEditCtrl, 1, wx.EXPAND)
        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)
        self.Layout()
    # end _layoutWidgets()

    def _createContextToolBar(self):
        contextToolBarModel = ZBlogWysiwygEditorContextToolbarModel()
        toolBarContext = ZBlogPostEditorToolBarActionContext(self)
        contentProvider = ZModelBasedToolBarContentProvider(contextToolBarModel, toolBarContext)
        eventHandler = ZModelBasedToolBarEventHandler(contextToolBarModel, toolBarContext)
        return ZToolBar(contentProvider, eventHandler, self)
    # end _createToolBar()

    def _bindWidgetEvents(self):
        ZBlogPostContentEditorBase._bindWidgetEvents(self)
        self.Bind(ZEVT_TOOLBAR_RESIZE, self.onToolBarResize, self.contextToolBar)
    # end _bindWidgetEvents()

    def _bindContentEditCtrlEvents(self):
        ZBlogPostContentEditorBase._bindContentEditCtrlEvents(self)
        self.Bind(IZEditControlEvents.ZEVT_DBL_CLICK, self.onDoubleClick, self._getContentEditControl())


    def onUpdateUI(self, event): #@UnusedVariable
        ZBlogPostContentEditorBase.onUpdateUI(self, event)
        self.contextToolBar.refresh()
    # end onUIUpdate()

    def onDoubleClick(self, event): #@UnusedVariable
        linkContext = self.getLinkContext()
        imageContext = self.getImageContext()
        if imageContext is not None and imageContext.canEditImage():
            ZImageUiUtil().editImage(self, imageContext)
        elif linkContext is not None and linkContext.canEditLink():
            ZLinkUiUtil().editLink(self, linkContext)
    # end onDoubleClick

# end ZBlogPostWysiwygContentEditor