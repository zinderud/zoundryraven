from zoundry.blogapp.ui.util.dateformatutil import formatLocalDateAndTime
from zoundry.blogapp.ui.templates.templateuiutil import disableTemplatePreviewJavaScript
from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.global_services import getLoggerService
from zoundry.appframework.global_services import getResourceRegistry
from zoundry.appframework.ui.util.uiutil import ZMethodRunnable
from zoundry.appframework.ui.util.uiutil import fireUIExecEvent
from zoundry.appframework.ui.widgets.controls.advanced.htmlview import ZHTMLViewControl
from zoundry.appframework.ui.widgets.controls.common.panel import ZTransparentPanel
from zoundry.appframework.ui.widgets.controls.common.statusbar import ZStatusBarModel
from zoundry.blogapp.constants import IZBlogAppServiceIDs
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.models.ui.editors.blogeditormodel import ZBlogPostEditorModel
from zoundry.blogapp.services.datastore.datastore import IZDataStoreListener
from zoundry.blogapp.services.template.templatesvc import IZTemplateServiceListener
from zoundry.blogapp.services.template.templateutil import APPLY_TEMPLATE_MODE_FULL
from zoundry.blogapp.services.template.templateutil import applyTemplateToDocument
from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZBlogPostEditorMenuActionContext
from zoundry.blogapp.ui.actions.blogeditor.blogeditoractions import ZBlogPostEditorToolBarActionContext
from zoundry.blogapp.ui.editors.blogeditorctrls.wysiwygcontenteditor import ZBlogPostWysiwygContentEditor
from zoundry.blogapp.ui.editors.blogeditorctrls.xhtmlcontenteditor import ZBlogPostXhtmlContentEditor
from zoundry.blogapp.ui.editors.blogeditorsupport.blogeditordocument import ZBlogPostEditorPreviewDocument
from zoundry.blogapp.ui.editors.blogeditorsupport.blogpostaccel import ZBlogPostEditorAcceleratorTable
from zoundry.blogapp.ui.editors.blogeditorsupport.blogpostmenubar import ZBlogPostEditorMenuBarModel
from zoundry.blogapp.ui.editors.blogeditorsupport.blogposttoolbar import ZBlogPostEditorToolBarModel
from zoundry.blogapp.ui.editors.editor import ZEditor
from zoundry.blogapp.ui.events.editors.blogeditorctrls.metadataevents import ZEVT_META_DATA_TITLE_CHANGED
from zoundry.blogapp.ui.events.editors.blogeditorevents import ZEVT_PUBLISHING_CHANGE
from zoundry.blogapp.ui.util.blogutil import getBlogFromPubMetaData
from zoundry.blogapp.ui.util.portableuiutil import copyNonPortableFiles
import wx #@UnusedImport
import wx.combo #@Reimport
import wx.lib.flatnotebook as fnb

# ------------------------------------------------------------------------------
# Factory creating the control that display the content
# ------------------------------------------------------------------------------
class ZBlogPostContentEditorFactory:

    def createContentWysiwygEditor(self, parentWindow, zblogPostEditor, model): #@UnusedVariable
        u"""createContentWysiwygEditor(wxWindow, ZBlogPostEditor, ZBlogPostEditorModel) -> IZBlogContentEditorControl
        Returns the content designer""" #$NON-NLS-1$
        return ZBlogPostWysiwygContentEditor(parentWindow, zblogPostEditor, model)
    # end createContentWysiwygEditor()

    def createContentXhtmlEditor(self, parentWindow, zblogPostEditor, model): #@UnusedVariable
        u"""createContentXhtmlEditor(wxWindow, ZBlogPostEditor, ZBlogPostEditorModel) -> IZBlogContentEditorControl
        Returns xhtml source text content editor""" #$NON-NLS-1$
        return ZBlogPostXhtmlContentEditor(parentWindow, zblogPostEditor, model)
    # end createContentXhtmlEditor()

    def createContentPreviewer(self, parentWindow, zblogPostEditor, model): #@UnusedVariable
        u"""createContentPreviewer(wxWindow, ZBlogPostEditor, ZBlogPostEditorModel) -> IZHTMLViewControl
        """ #$NON-NLS-1$
        htmlview = ZHTMLViewControl(parentWindow, wx.ID_ANY)
        return htmlview
    # end createContentPreviewer()

# end ZBlogPostContentEditorFactory


# ------------------------------------------------------------------------------
# Implementation of an IZEditor for editing blog posts.
# ------------------------------------------------------------------------------
class ZBlogPostEditor(ZEditor, IZDataStoreListener, IZTemplateServiceListener):

    def __init__(self, parent, document):
        self.parent = parent
        self.notebook = None
        self.model = ZBlogPostEditorModel()
        self.model.setDocument(document)
        self.wysiwygContentEditor = None
        self.xhtmlContentEditor = None
        self.contentPreviewer = None
        self.activeContentEditor = None
        self.previewMode = False
        self.currentPreviewTemplate = None
        self.dataStoreService = getApplicationModel().getService(IZBlogAppServiceIDs.DATA_STORE_SERVICE_ID)
        self.templateService = getApplicationModel().getService(IZBlogAppServiceIDs.TEMPLATE_SERVICE_ID)

        ZEditor.__init__(self, parent)

        self.bitmap = self._createEditorBitmap()
        self.menuBarModel = self._createMenuBarModel()
        self.toolBarModel = self._createToolBarModel()
        self.statusBarModel = self._createStatusBarModel()

        self._registerAsListener()
        self._startSnapshotTimer()
    # end __init__()

    def getActiveContentEditor(self):
        return self.activeContentEditor
    # end getActiveContentEditor()

    def _setActiveContentEditor(self, editor):
        if not (editor == self.wysiwygContentEditor or editor == self.xhtmlContentEditor):
            return

        # FIXME (PJ) switch only if content is dirty i.e. not to lose current selection info, and cursor/caret position etc.
        # copy current editor ui data (including xhtml content) to the model
        self._updateModel()
        # switch editors
        self.activeContentEditor = editor
        # update ui based on model data
        self._refreshContentEditorUI()
    # end _setActiveContentEditor()

    def _updateModel(self):
        # update model data based on current ui data.
        self.getActiveContentEditor().updateModel()
    # end _updateModel()

    def _refreshContentEditorUI(self):
        # update ui based on current model data
        self.getActiveContentEditor().refreshUI()
    # end _refreshContentEditorUI()

    def _showPreview(self):
        xhtmlDoc = self.getActiveContentEditor()._getContentEditControl().getXhtmlDocument()
        # Get the current blog selection from the UI control.
        if self.currentPreviewTemplate is not None:
            document = ZBlogPostEditorPreviewDocument(self.getTitle(), xhtmlDoc)
            templatedDoc = applyTemplateToDocument(self.currentPreviewTemplate, document, APPLY_TEMPLATE_MODE_FULL)
            if templatedDoc is not None:
                xhtmlDoc = templatedDoc
                disableTemplatePreviewJavaScript(xhtmlDoc)
        self.contentPreviewer.setXhtmlDocument(xhtmlDoc, False)
    # end _showPreview()

    def _isWysiwygActive(self):
        return self.previewMode == False and self.activeContentEditor is not None and self.activeContentEditor == self.wysiwygContentEditor
    # end _isWysiwygActive()

    def _isXhtmlActive(self):
        return self.previewMode == False and self.activeContentEditor is not None and self.activeContentEditor == self.xhtmlContentEditor
    # end _isXhtmlActive()

    def _isPreviewActive(self):
        return self.previewMode
    # end _isPreviewActive()

    def getTitle(self):
        return self.model.getTitle()
    # end getTitle()

    def getBitmap(self):
        return self.bitmap
    # end getBitmap()

    def getMenuBarModel(self):
        return self.menuBarModel
    # end getMenuBarModel()

    def getToolBarModel(self):
        return self.toolBarModel
    # end getToolBarModel()

    def getStatusBarModel(self):
        return self.statusBarModel
    # end getStatusBarModel()

    def getDocumentId(self):
        return self.model.getDocument().getId()
    # end getDocumentId()

    def getDocument(self):
        return self.model.getDocument()
    # end getDocument()

    def getToolBarActionContext(self):
        return ZBlogPostEditorToolBarActionContext(self)
    # end getToolBarActionContext()

    def getMenuActionContext(self):
        return ZBlogPostEditorMenuActionContext(self)
    # end getMenuActionContext

    def getAcceleratorActionContext(self):
        return ZBlogPostEditorMenuActionContext(self)
    # end getAcceleratorActionContext

    def save(self):
        self._clearRecoverySnapshot()
        # Flush data from UI controls to document model
        self._updateModel()
        portableFilesCopies = self._checkForNonPortableFiles()
        # save model documen to data store
        self.model.saveDocument()
        self.getActiveContentEditor().modelSaved()
        self.setDirty(False)
        if portableFilesCopies:
            # refresh editor UI if files were copies to the portable profile resource store
            self.getActiveContentEditor().refreshUI()            
    # end save()

    def _checkForNonPortableFiles(self):
        xhtmlDoc = self.getDocument().getContent().getXhtmlDocument()
        # This method copies non portable files/images to resource store and updates the  img src (href) attribute values.
        # Returns true if files were copies.
        return copyNonPortableFiles(self, xhtmlDoc)
    # end _checkForNonPortableFiles

    def close(self):
        pass
    # end close()

    def destroy(self):
        self._stopSnapshotTimer()
        self._unregisterAsListener()
        self._clearRecoverySnapshot()
    # end destroy()

    def hasCapability(self, capabilityKey): #@UnusedVariable
        if not self._isPreviewActive():
            # delegate to the content editor's edit control
            return self.getActiveContentEditor().hasCapability(capabilityKey)
        else:
            return False
    # end hasCapability()

    def _createMenuBarModel(self):
        return ZBlogPostEditorMenuBarModel(self)
    # end getMenuBarModel()

    def _createToolBarModel(self):
        return ZBlogPostEditorToolBarModel()
    # end _createToolBarModel()

    def _createStatusBarModel(self):
        # FIXME (PJ) need a proper implementation of the status bar model, this is just a sample
        # Instead showing datetime, show word count, current tag name etc.
        sbModel = ZStatusBarModel()
        pane = sbModel.addPane(u"datetime") #$NON-NLS-1$
        pane.text = formatLocalDateAndTime( self.model.getDocument().getCreationTime() )
        
        pane = sbModel.addPane(u"rowcol") #$NON-NLS-1$
        sbModel.setPaneWidth(u"rowcol", 80) #$NON-NLS-1$
        pane.text = u"" #$NON-NLS-1$
        return sbModel
    # end _createStatusBarModel()

    def _createEditorWidgets(self):
        self._createAcceleratorTable()

        self.notebook = fnb.FlatNotebook(self, wx.ID_ANY, style = fnb.FNB_BOTTOM | fnb.FNB_NO_NAV_BUTTONS | fnb.FNB_NO_X_BUTTON | fnb.FNB_NODRAG)
        self.notebook.AddPage(self._createWysiwygPage(), _extstr(u"blogeditor.Design"), True, -1) #$NON-NLS-1$
        self.notebook.AddPage(self._createXHTMLPage(), _extstr(u"blogeditor.XHTML"), False, -1) #$NON-NLS-1$
        self.notebook.AddPage(self._createPreviewPage(), _extstr(u"blogeditor.Preview"), False, -1) #$NON-NLS-1$
    # end _createEditorWidgets()

    def _createWysiwygPage(self):
        self.wysiwygContentEditor = ZBlogPostContentEditorFactory().createContentWysiwygEditor(self.notebook, self, self.model)
        return self.wysiwygContentEditor
    # end _createDesignPage()

    def _createXHTMLPage(self):
        self.xhtmlContentEditor = ZBlogPostContentEditorFactory().createContentXhtmlEditor(self.notebook, self, self.model)
        self.xhtmlContentEditor.SetBackgroundColour(wx.WHITE)
        return self.xhtmlContentEditor
    # end _createXHTMLPage()

    def _createPreviewPage(self):
        self.previewTabPanel = ZTransparentPanel(self.notebook, wx.ID_ANY)
        self._createPreviewTools(self.previewTabPanel)
        self.contentPreviewer = ZBlogPostContentEditorFactory().createContentPreviewer(self.previewTabPanel, self, self.model)
        self.contentPreviewer.SetBackgroundColour(wx.WHITE)
        return self.previewTabPanel
    # end _createPreviewPage()

    def _createPreviewTools(self, parent):
        self.templateChooseLabel = wx.StaticText(parent, wx.ID_ANY, _extstr(u"blogeditor.ViewWithTemplate")) #$NON-NLS-1$
        self.templateChooser = wx.combo.BitmapComboBox(parent, wx.ID_ANY, style = wx.CB_READONLY)
        self.previewStaticLine = wx.StaticLine(parent, wx.ID_ANY)
    # end _createPreviewTools()

    def _createAcceleratorTable(self):
        self.acceleratorTable = ZBlogPostEditorAcceleratorTable(self.getAcceleratorActionContext())
        self.SetAcceleratorTable(self.acceleratorTable)
    # end _createAcceleratorTable()

    def _populateEditorWidgets(self):
        self.activeContentEditor = self.wysiwygContentEditor
        self._refreshContentEditorUI()

        self._updateTemplateUI()
    # end _populateEditorWidgets()

    def _updateTemplateUI(self):
        blog = self._getBlog()
        self.currentPreviewTemplate = None
        currentTemplateId = None
        if blog is not None:
            templateId = blog.getTemplateId()
            if templateId is not None:
                currentTemplateId = templateId
                template = self.templateService.getTemplate(templateId)
                if template:
                    self.currentPreviewTemplate = template
        self._updateTemplateChooser(currentTemplateId)
    # end _updateTemplateUI()

    def _updateTemplateChooser(self, currentTemplateId = None):
        if currentTemplateId is None and self.currentPreviewTemplate is not None:
            currentTemplateId = self.currentPreviewTemplate.getId()
        self.templateChooser.Clear()

        bitmap = getResourceRegistry().getBitmap(u"images/dialogs/template/manager/template.png") #$NON-NLS-1$
        self.templateChooser.Append(_extstr(u"blogeditor.__NoTemplate__"), wx.NullBitmap, u"_no_template_") #$NON-NLS-2$ #$NON-NLS-1$
        idx = 1
        for template in self.templateService.getTemplates():
            self.templateChooser.Append(template.getName(), bitmap, template.getId())
            if template.getId() == currentTemplateId:
                self.templateChooser.Select(idx)
            idx = idx + 1
        (w, h) = self.templateChooser.GetBestSizeTuple()
        self.templateChooser.SetMinSize(wx.Size(w + 18, h))
        if currentTemplateId is None:
            self.templateChooser.Select(0)
    # end _updateTemplateUI()

    def _layoutEditorWidgets(self):
        self._layoutPreviewWidgets()

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.notebook, 1, wx.EXPAND)
        return sizer
    # end _layoutEditorWidgets()

    def _layoutPreviewWidgets(self):
        chooserSizer = wx.BoxSizer(wx.HORIZONTAL)
        chooserSizer.Add(self.templateChooseLabel, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 3)
        chooserSizer.Add(self.templateChooser, 0, wx.ALL, 3)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddSizer(chooserSizer, 0, wx.ALL | wx.EXPAND)
        sizer.Add(self.previewStaticLine, 0, wx.ALL | wx.EXPAND)
        sizer.Add(self.contentPreviewer, 1, wx.ALL | wx.EXPAND)
        self.previewTabPanel.SetSizer(sizer)
        self.previewTabPanel.SetAutoLayout(True)
    # end _layoutPreviewWidgets()

    def _bindWidgetEvents(self):
        self.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CHANGING, self.onTabChanging)
        self.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CHANGED, self.onTabChanged)
        self.Bind(ZEVT_PUBLISHING_CHANGE, self.onPublishingChange)
        self.Bind(ZEVT_META_DATA_TITLE_CHANGED, self.onTitleChanged)
        self.Bind(wx.EVT_COMBOBOX, self.onTemplateChooser, self.templateChooser)
        self.acceleratorTable.bindTo(self)
    # end _bindWidgetEvents()

    def _setInitialFocus(self):
        document = self.getDocument()
        title = document.getTitle()
        if title:
            self.getActiveContentEditor().focusOnContent()
    # end _setInitialFocus()

    def _createEditorBitmap(self):
        # FIXME (EPW) change the icon for blog posts
        return getApplicationModel().getResourceRegistry().getBitmap(u"images/mainapp/icon/icon16x16.png") #$NON-NLS-1$
    # end _createEditorBitmap()

    def onTabChanging(self, event):
        editorTabId = event.GetSelection()
        self.previewMode = False
        # switch to wysiwyg
        if editorTabId == 0 and not self._isWysiwygActive():
            self._setActiveContentEditor(self.wysiwygContentEditor)
        # switch to xthml text editor
        elif editorTabId == 1 and not self._isXhtmlActive():
            self._setActiveContentEditor(self.xhtmlContentEditor)
        elif editorTabId == 2:
            self.previewMode = True
            self._updateModel()
            self._updateTemplateUI()
            self._showPreview()
            # clear (row, col) text in status bar for preview control
            self.statusBarModel.setPaneText(u"rowcol", u"") #$NON-NLS-1$ #$NON-NLS-2$
        # update toolbar (e.g. disable paste, cut actions )
        self._fireToolBarChangedEvent()
        self._fireMenuBarChangedEvent()
        self._fireStatusBarChangedEvent()
    # end onTabChanging()

    def onTabChanged(self, event):
        event.Skip()
    # end onTabChanged()

    def onTitleChanged(self, event):
        self.model.setTitle(event.getTitle())
        self._fireTitleChangedEvent()
        event.Skip()
    # end onTitleChanged()

    def onPublishingChange(self, event):
        self.setDirty(True)
        event.Skip()
    # end onPublishingChange()

    def onMenuClose(self, menuContext): #@UnusedVariable
        self._fireCloseEvent()
    # end onMenuClose()

    # Likely to happen on a separate thread...
    def onDocumentChanged(self, document, metaDataOnly):
        if document.getId() == self.getDocumentId():
            if metaDataOnly:
                modelDoc = self.getDocument()
                modelDoc.setBlogInfoList(document.getBlogInfoList())
                self._fireUpdateMenu()
            elif not self.isDirty():
                self.model.setDocument(document)
                fireUIExecEvent(ZMethodRunnable(self._refreshContentEditorUI), self)
            else:
                # FIXME (EPW) Editor is dirty, but content changes were made by someone else - prompt the user for what to do
                pass
    # end onDocumentChanged()

    def onDocumentDeleted(self, document):
        u"Called when a specific document has been deleted." #$NON-NLS-1$
        # Note: we should probably do something interesting if the document we are currently
        # editing was deleted.
    # end onDocumentDeleted()

    def onTemplateCreated(self, template): #@UnusedVariable
        self._updateTemplateChooser()
    # end onTemplateCreated()

    def onTemplateDeleted(self, template): #@UnusedVariable
        if self.currentPreviewTemplate is not None:
            if template.getId() == self.currentPreviewTemplate.getId():
                self.currentPreviewTemplate = None
                self._updateTemplateUI()
                self._showPreview()
                return
        self._updateTemplateChooser()
    # end onTemplateDeleted()

    def onTemplateModified(self, template): #@UnusedVariable
        self._updateTemplateChooser()
    # end onTemplateModified()

    def _fireDirtyEvent(self):
        ZEditor._fireDirtyEvent(self)
        self._fireUpdateMenu()
    # end _fireDirtyEvent();

    def _fireUpdateMenu(self):
        self._fireMenuBarChangedEvent()
        self._fireToolBarChangedEvent()
    # end _fireUpdateMenu();

    def _registerAsListener(self):
        self.dataStoreService.addListener(self)
        self.templateService.addListener(self)
    # end _registerAsListener()

    def _unregisterAsListener(self):
        self.dataStoreService.removeListener(self)
        self.templateService.removeListener(self)
    # end _unregisterAsListener()

    def _startSnapshotTimer(self):
        self.snapshotTimerId = wx.NewId()
        self.snapshotTimer = wx.Timer(self, self.snapshotTimerId)
        wx.EVT_TIMER(self, self.snapshotTimerId, self.onSnapshotTimer)
        # Timer will fire every 60 seconds
        self.snapshotTimer.Start(60000)
    # end _startSnapshotTimer()

    def _stopSnapshotTimer(self):
        self.snapshotTimer.Stop()
    # end _stopSnapshotTimer()

    def _clearRecoverySnapshot(self):
        document = self.getDocument()
        crashRecoveryService = getApplicationModel().getService(IZBlogAppServiceIDs.CRASH_RECOVERY_SERVICE_ID)
        crashRecoveryService.clearRecoverySnapshot(document)
    # end _clearRecoverySnapshot()

    def _takeRecoverySnapshot(self):
        try:
            self._updateModel()
            document = self.getDocument()
            crashRecoveryService = getApplicationModel().getService(IZBlogAppServiceIDs.CRASH_RECOVERY_SERVICE_ID)
            crashRecoveryService.takeRecoverySnapshot(document)
        except Exception, e:
            getLoggerService().exception(e)
    # end _takeRecoverySnapshot()

    def onSnapshotTimer(self, event):
        if self.isDirty():
            self._takeRecoverySnapshot()
        event.Skip()
    # end onSnapshotTimer()

    def onTemplateChooser(self, event):
        selId = self.templateChooser.GetSelection()
        if selId == wx.NOT_FOUND:
            self.currentPreviewTemplate = None
        else:
            templateId = self.templateChooser.GetClientData(selId)
            if templateId == u"_no_template_": #$NON-NLS-1$
                self.currentPreviewTemplate = None
            elif templateId is None:
                # Bug in the bitmap combo?  The last item's client data always returns None
                templateName = self.templateChooser.GetValue()
                self.currentPreviewTemplate = self.templateService.getTemplateByName(templateName)
            else:
                self.currentPreviewTemplate = self.templateService.getTemplate(templateId)

        self._showPreview()
        event.Skip()
    # end onTemplateChooser()

    def _getBlog(self):
        # FIXME (PJ) hide this code in self.getActiveContentEditor().getBlog()
        blogPostMetaDataModel = self.model.getMetaDataModel()
        pubMetaDataList = blogPostMetaDataModel.getPubMetaDataList()
        if pubMetaDataList and len(pubMetaDataList) > 0:
            pubMetaData = pubMetaDataList[0]
            blog = getBlogFromPubMetaData(pubMetaData)
            return blog
        return None
    # end _getBlog()

# end ZBlogPostEditor
