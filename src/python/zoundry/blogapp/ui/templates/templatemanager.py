from zoundry.blogapp.ui.templates.templateuiutil import disableTemplatePreviewJavaScript
from zoundry.appframework.global_services import getResourceRegistry
from zoundry.appframework.ui.actions.menuaction import ZMenuActionContext
from zoundry.appframework.ui.dialogs.mixins import ZPersistentDialogMixin
from zoundry.appframework.ui.events.commonevents import ZEVT_REFRESH
from zoundry.appframework.ui.util.fontutil import getDefaultFontBold
from zoundry.appframework.ui.util.uiutil import ZMethodRunnable
from zoundry.appframework.ui.util.uiutil import fireUIExecEvent
from zoundry.appframework.ui.widgets.controls.advanced.htmlview import ZHTMLViewControl
from zoundry.appframework.ui.widgets.controls.advanced.splitter import ZSplitterWindow
from zoundry.appframework.ui.widgets.controls.common.bitmap import ZStaticBitmap
from zoundry.appframework.ui.widgets.controls.common.panel import ZTransparentPanel
from zoundry.appframework.ui.widgets.controls.common.statusbar import ZStatusBar
from zoundry.appframework.ui.widgets.controls.common.statusbar import ZStatusBarModel
from zoundry.appframework.ui.widgets.controls.common.statusbar import ZStatusBarModelBasedContentProvider
from zoundry.appframework.ui.widgets.controls.listex import ZListViewEx
from zoundry.appframework.ui.widgets.dialogs.standarddialogs import ZShowExceptionMessage
from zoundry.appframework.ui.widgets.window import ZBaseWindow
from zoundry.base.exceptions import ZException
from zoundry.base.xhtml.xhtmlio import loadXhtmlDocumentFromString
from zoundry.blogapp.constants import IZBlogAppUserPrefsKeys
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.models.ui.templates.templatemanagermodel import ZTemplateManagerModel
from zoundry.blogapp.services.template.templatesvc import IZTemplateServiceListener
from zoundry.blogapp.services.template.templateutil import APPLY_TEMPLATE_MODE_FULL
from zoundry.blogapp.services.template.templateutil import applyTemplateToDocument
from zoundry.blogapp.ui.templates.templateactions import ZAddTemplateFromBlogAction
from zoundry.blogapp.ui.templates.templateactions import ZRemoveTemplateAction
from zoundry.blogapp.ui.templates.templatemanagerui import ZTemplateListProvider
import wx

# FIXME (EPW) should have a multi-part .ico for this instead
ICON_IMAGES = [
    u"images/mainapp/icon/icon16x16.png", #$NON-NLS-1$
    u"images/mainapp/icon/icon24x24.png", #$NON-NLS-1$
    u"images/mainapp/icon/icon32x32.png", #$NON-NLS-1$
    u"images/mainapp/icon/icon48x48.png" #$NON-NLS-1$
]

TEMPLATE_MANAGER_WINDOW = None

# ------------------------------------------------------------------------------------
# Use this function to show the background task manager window.  It will enforce a
# singleton window instance.
# ------------------------------------------------------------------------------------
def ZShowTemplateManager():
    global TEMPLATE_MANAGER_WINDOW
    try:
        if TEMPLATE_MANAGER_WINDOW is None:
            TEMPLATE_MANAGER_WINDOW = ZTemplateManagerWindow(None)
        TEMPLATE_MANAGER_WINDOW.Show()
        TEMPLATE_MANAGER_WINDOW.Raise()
        return TEMPLATE_MANAGER_WINDOW
    except Exception, e:
        ZShowExceptionMessage(None, ZException(u"Error opening Background Task Manager", e)) #$NON-NLS-1$
# end ZShowTemplateManager


# ------------------------------------------------------------------------------------
# Getter for the background task manager window.
# ------------------------------------------------------------------------------------
def getTemplateManager():
    global TEMPLATE_MANAGER_WINDOW
    return TEMPLATE_MANAGER_WINDOW
# end getTemplateManager()


# ------------------------------------------------------------------------------
# Action context for the template manager.
# ------------------------------------------------------------------------------
class ZTemplateManagerActionContext(ZMenuActionContext):

    def __init__(self, window, template):
        self.template = template

        ZMenuActionContext.__init__(self, window)
    # end __init__()

    def getTemplate(self):
        return self.template
    # end getTemplate()

    def setTemplate(self, template):
        self.template = template
    # end setTemplate()

# end ZTemplateManagerActionContext


# ------------------------------------------------------------------------------
# The Background Task Manager Manager window.  This window allows the user to
# manage their background tasks (cancel, clear, check status, etc).
# ------------------------------------------------------------------------------
class ZTemplateManagerWindow(ZBaseWindow, ZPersistentDialogMixin, IZTemplateServiceListener):

    def __init__(self, parent):
        self.model = ZTemplateManagerModel()
        self.selectedTemplate = None

        style = wx.DEFAULT_FRAME_STYLE | wx.FULL_REPAINT_ON_RESIZE | wx.CLIP_CHILDREN
        ZBaseWindow.__init__(self, parent, _extstr(u"templatemanager.BlogTemplateManager"), name = u"ZTemplateManager", style = style) #$NON-NLS-2$ #$NON-NLS-1$
        ZPersistentDialogMixin.__init__(self, IZBlogAppUserPrefsKeys.TEMPLATE_WINDOW)
        self.Layout()

        self._installListener()
    # end __init__()

    def getModel(self):
        return self.model
    # end getModel()

    def _createWindowWidgets(self, parent):
        self.headerPanel = self._createHeaderPanel(parent)
        self.headerStaticLine = wx.StaticLine(parent, wx.ID_ANY)

        self.splitterWindow = ZSplitterWindow(parent)
        self.splitterWindow.SetSizeHints(700, 600)

        self.topPanel = ZTransparentPanel(self.splitterWindow, wx.ID_ANY)
        self.topStaticBox = wx.StaticBox(self.topPanel, wx.ID_ANY, _extstr(u"templatemanager.Templates")) #$NON-NLS-1$

        provider = ZTemplateListProvider(self.model)
        self.templateList = ZListViewEx(provider, self.topPanel)

        self.addButton = wx.Button(self.topPanel, wx.ID_ANY, _extstr(u"templatemanager.Add")) #$NON-NLS-1$
        self.removeButton = wx.Button(self.topPanel, wx.ID_ANY, _extstr(u"templatemanager.Remove")) #$NON-NLS-1$
        self.removeButton.Enable(False)

        self.preview = ZHTMLViewControl(self.splitterWindow, wx.ID_ANY, style = wx.NO_FULL_REPAINT_ON_RESIZE | wx.SIMPLE_BORDER)

        self.splitterWindow.SetSashSize(10)
        self.splitterWindow.SplitHorizontally(self.topPanel, self.preview, 150)
        self.splitterWindow.SetMinimumPaneSize(100)

        self.statusBar = self._createStatusBar()
        self.SetStatusBar(self.statusBar)
    # end _createWindowWidgets()

    def _createHeaderPanel(self, parent):
        panel = wx.Panel(parent, wx.ID_ANY)
        panel.SetBackgroundColour(wx.WHITE)

        self.headerLink = wx.HyperlinkCtrl(panel, wx.ID_ANY, self._getHeaderTitle(), self._getHeaderHelpURL())
        self.headerLink.SetFont(getDefaultFontBold())
        self.headerMessage = wx.StaticText(panel, wx.ID_ANY, self._getHeaderMessage())
        headerImagePath = self._getHeaderImagePath()
        if not headerImagePath:
            headerImagePath = u"images/dialogs/image/header_image.png" #$NON-NLS-1$
        self.headerIcon = ZStaticBitmap(panel, getResourceRegistry().getBitmap(headerImagePath))

        linkAndMsgSizer = wx.BoxSizer(wx.VERTICAL)
        linkAndMsgSizer.Add(self.headerLink, 0, wx.ALL, 2)
        linkAndMsgSizer.Add(self.headerMessage, 1, wx.EXPAND | wx.ALL, 2)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.AddSizer(linkAndMsgSizer, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(self.headerIcon, 0, wx.EXPAND | wx.ALL, 10)

        panel.SetAutoLayout(True)
        panel.SetSizer(sizer)

        return panel
    # end _createHeaderPanel()

    def _createStatusBar(self):
        self.statusBarModel = ZStatusBarModel()
        self.statusBarModel.addPane(u"name") #$NON-NLS-1$
        self.statusBarModel.setPaneWidth(u"name", 1) #$NON-NLS-1$
        self.statusBarModel.setPaneText(u"name", u"") #$NON-NLS-1$ #$NON-NLS-2$
        provider = ZStatusBarModelBasedContentProvider(self.statusBarModel)
        statusBar = ZStatusBar(self, provider)
        return statusBar
    # end _createStatusBar()

    def _populateWindowWidgets(self):
        self.SetIcons(getResourceRegistry().getIconBundle(ICON_IMAGES))
        self.refresh()
    # end _populateWindowWidgets()

    def _layoutWindowWidgets(self):
        staticBoxSizer = wx.StaticBoxSizer(self.topStaticBox, wx.VERTICAL)
        staticBoxSizer.Add(self.templateList, 1, wx.ALL | wx.EXPAND, 3)
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer.Add(self.addButton, 0, wx.ALL | wx.EXPAND, 2)
        buttonSizer.Add(self.removeButton, 0, wx.ALL | wx.EXPAND, 2)
        staticBoxSizer.AddSizer(buttonSizer, 0, wx.ALL | wx.EXPAND, 2)

        self.topPanel.SetSizer(staticBoxSizer)
        self.topPanel.SetAutoLayout(True)

        sizer = wx.BoxSizer(wx.VERTICAL)

        sizer.Add(self.headerPanel, 0, wx.EXPAND | wx.ALL, 0)
        sizer.Add(self.headerStaticLine, 0, wx.EXPAND | wx.ALL, 0)
        sizer.Add(self.splitterWindow, 1, wx.EXPAND | wx.ALL, 5)

        return sizer
    # end _layoutWindowWidgets()

    def _bindWidgetEvents(self):
        self.Bind(wx.EVT_BUTTON, self.onAdd, self.addButton)
        self.Bind(wx.EVT_BUTTON, self.onRemove, self.removeButton)
        self.Bind(wx.EVT_CLOSE, self.onClose, self)
        self.Bind(ZEVT_REFRESH, self.onRefresh, self)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onTemplateSelected, self.templateList)
        self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.onTemplateRightClick, self.templateList)
    # end _bindWidgetEvents()

    def onRefresh(self, event):
        self.templateList.Refresh()
        event.Skip()
    # end onRefresh()

    def onAdd(self, event):
        action = ZAddTemplateFromBlogAction()
        action.runAction(ZTemplateManagerActionContext(self, self.selectedTemplate))
        event.Skip()
    # end onAdd()

    def onRemove(self, event):
        action = ZRemoveTemplateAction()
        action.runAction(ZTemplateManagerActionContext(self, self.selectedTemplate))
        event.Skip()
    # end onRemove()

    def onTemplateSelected(self, event):
        self.selectedTemplate = self.model.getTemplates()[event.GetItem().GetId()]
        self.removeButton.Enable(True)
        self.refresh()
        event.Skip()
    # end onTemplateSelected()

    def onTemplateRightClick(self, event):
        event.Skip()
    # end onTemplateRightClick()

    def _setInitialFocus(self):
        pass
    # end _setInitialFocus()

    def refresh(self):
        self.templateList.refresh()
        self.statusBar.refresh()
        if self.selectedTemplate is not None:
            document = self.model.getSampleDocument()
            xhtmlDoc = applyTemplateToDocument(self.selectedTemplate, document, APPLY_TEMPLATE_MODE_FULL)
            disableTemplatePreviewJavaScript(xhtmlDoc)
        else:
            xhtmlDoc = loadXhtmlDocumentFromString(u"Select a template to view a preview of it.") #$NON-NLS-1$
        self.preview.setXhtmlDocument(xhtmlDoc, False)
    # end refresh()

    def _getHeaderTitle(self):
        return _extstr(u"templatemanager.BlogTemplateManager") #$NON-NLS-1$
    # end _getHeaderTitle()

    def _getHeaderMessage(self):
        return _extstr(u"templatemanager.BlogTemplateManagerDescription") #$NON-NLS-1$
    # end _getHeaderMessage()

    def _getHeaderImagePath(self):
        return u"images/dialogs/template/manager/header_image.png" #$NON-NLS-1$
    # end _getHeaderImagePath()

    def _getHeaderHelpURL(self):
        return u"http://www.zoundry.com" #$NON-NLS-1$
    # end _getHeaderHelpUrl()

    def onClose(self, event):
        global TEMPLATE_MANAGER_WINDOW
        TEMPLATE_MANAGER_WINDOW = None

        self._uninstallListener()

        event.Skip()
    # end onClose()

    def _installListener(self):
        self.model.getService().addListener(self)
    # end _installListener()

    def _uninstallListener(self):
        self.model.getService().removeListener(self)
    # end _uninstallListener()

    def onTemplateCreated(self, template): #@UnusedVariable
        fireUIExecEvent(ZMethodRunnable(self.refresh), self)
    # end onTemplateCreated()

    def onTemplateDeleted(self, template):
        if self.selectedTemplate.getId() == template.getId():
            self.selectedTemplate = None

        self.refresh()
        self.templateList.deselectAll()
        self.removeButton.Enable(False)
    # end onTemplateDeleted()

    def onTemplateModified(self, template): #@UnusedVariable
        fireUIExecEvent(ZMethodRunnable(self.refresh), self)
    # end onTemplateModified()

# end ZTemplateManagerWindow
