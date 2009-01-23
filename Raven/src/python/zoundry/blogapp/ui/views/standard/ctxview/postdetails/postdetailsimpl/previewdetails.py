from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.profile.userprefs import IZUserPreferencesListener
from zoundry.appframework.ui.events.commonevents import ZEVT_REFRESH
from zoundry.appframework.ui.util.uiutil import fireRefreshEvent
from zoundry.appframework.ui.widgets.controls.advanced.htmlview import ZHTMLViewControl
from zoundry.base.xhtml.xhtmlio import loadXhtmlDocumentFromString
from zoundry.blogapp.constants import IZBlogAppServiceIDs
from zoundry.blogapp.constants import IZBlogAppUserPrefsKeys
from zoundry.blogapp.services.datastore.datastore import IZDataStoreListener
from zoundry.blogapp.services.template.templateutil import APPLY_TEMPLATE_MODE_TITLE_AND_BODY
from zoundry.blogapp.services.template.templateutil import applyTemplateToDocument
from zoundry.blogapp.services.template.templateutil import getTemplateFromBlog
from zoundry.blogapp.ui.templates.templateuiutil import disableTemplatePreviewJavaScript
from zoundry.blogapp.ui.util.blogutil import getBlogFromDocument
from zoundry.blogapp.ui.views.standard.ctxview.details.commondetails import IZDetailsPanelFactory
from zoundry.blogapp.ui.views.standard.ctxview.details.commondetails import ZAbstractDetailsPanel
import wx

# ----------------------------------------------------------------------------------------
# A concrete impl of a blog post details panel.  This one shows 'preview' information
# about the blog post.
# ----------------------------------------------------------------------------------------
class ZPreviewBlogPostDetailsPanel(ZAbstractDetailsPanel, IZDataStoreListener, IZUserPreferencesListener):

    def __init__(self, parent):
        self.document = None

        # Get the "use template" param from the user prefs
        appModel = getApplicationModel()
        userProfile = appModel.getUserProfile()
        userPrefs = userProfile.getPreferences()
        self.useTemplateInPreview = userPrefs.getUserPreferenceBool(IZBlogAppUserPrefsKeys.POST_PREVIEW_VIEW_USE_TEMPLATE, True)

        ZAbstractDetailsPanel.__init__(self, parent)

        self._registerAsListener()
    # end __init__()

    def _createWidgets(self):
        self.htmlViewer = ZHTMLViewControl(self, wx.ID_ANY)
        self._clearHtmlContent()
    # end _createWidgets()

    def _bindWidgetEvents(self):
        self.Bind(ZEVT_REFRESH, self.onZoundryRefresh, self)
    # end _bindWidgetEvents()

    def _layoutWidgets(self):
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.htmlViewer, 1, wx.EXPAND)
        self.SetAutoLayout(True)
        self.SetSizer(box)
        self.Layout()
    # end _layoutWidgets()

    def onUserPreferenceChange(self, key, newValue):
        if key == IZBlogAppUserPrefsKeys.POST_PREVIEW_VIEW_USE_TEMPLATE:
            self.useTemplateInPreview = newValue
            self._refreshContent()
    # end onUserPreferenceChange()

    # FIXME (EPW) need additional context info - what blog are we looking at?
    def onSelectionChanged(self, document):
        oldDoc = self.document
        self.document = document

        if oldDoc is not None and oldDoc.getId() == document.getId():
            return

        self._refreshContent()
    # end onSelectionChanged()

    def _refreshContent(self):
        document = self.document

        # Clear content if no document is set.
        if document is None:
            self._clearHtmlContent()
            return

        content = document.getContent()
        if content is not None:
            xhtmlDoc = content.getXhtmlDocument()
            blog = getBlogFromDocument(document)
            if blog is not None and self.useTemplateInPreview:
                template = getTemplateFromBlog(blog)
                if template is not None:
                    templatedDoc = applyTemplateToDocument(template, document, APPLY_TEMPLATE_MODE_TITLE_AND_BODY)
                    if templatedDoc is not None:
                        xhtmlDoc = templatedDoc
                    disableTemplatePreviewJavaScript(xhtmlDoc)
                    self.htmlViewer.setXhtmlDocument(xhtmlDoc, False)
                    return

            self.htmlViewer.setXhtmlDocument( xhtmlDoc, True )
    # end _refreshContent()

    def _clearHtmlContent(self):
        self.document = None
        xhtmlDoc = loadXhtmlDocumentFromString(u"") #$NON-NLS-1$
        self.htmlViewer.setXhtmlDocument(xhtmlDoc, False)
    # end _clearHtmlContent()

    def destroy(self):
        self._unregisterAsListener()
    # end destroy()

    # Document changed event from IZDataStoreListener
    def onDocumentChanged(self, document, metaDataOnly):
        if not metaDataOnly and self.document is not None and self.document.getId() == document.getId():
            self.document = document
            fireRefreshEvent(self, None)
    # end onDocumentChange()

    def onDocumentDeleted(self, document):
        if self.document is not None and self.document.getId() == document.getId():
            self.document = None
            fireRefreshEvent(self, None)
    # end onDocumentDeleted()

    def onZoundryRefresh(self, event):
        self._refreshContent()
        event.Skip()
    # end onZoundryRefresh()

    def _registerAsListener(self):
        # Register as a data store listener
        service = getApplicationModel().getService(IZBlogAppServiceIDs.DATA_STORE_SERVICE_ID)
        service.addListener(self)

        # Register as a user prefs listener
        appModel = getApplicationModel()
        userProfile = appModel.getUserProfile()
        userPrefs = userProfile.getPreferences()
        userPrefs.addListener(self)
    # end _registerAsListener()

    def _unregisterAsListener(self):
        # Unregister from the data store
        service = getApplicationModel().getService(IZBlogAppServiceIDs.DATA_STORE_SERVICE_ID)
        service.removeListener(self)
        
        # Unregister from the user prefs object
        # Register as a user prefs listener
        appModel = getApplicationModel()
        userProfile = appModel.getUserProfile()
        userPrefs = userProfile.getPreferences()
        userPrefs.removeListener(self)
    # end _unregisterAsListener()

# end ZPreviewBlogPostDetailsPanel


# ----------------------------------------------------------------------------------------
# An impl of a blog post details panel factory that creates a panel for "General"
# information about the post.
# ----------------------------------------------------------------------------------------
class ZPreviewBlogPostDetailsPanelFactory(IZDetailsPanelFactory):

    def createDetailsPanel(self, parent):
        return ZPreviewBlogPostDetailsPanel(parent)
    # end createDetailsPanel()

# end ZPreviewBlogPostDetailsPanelFactory
