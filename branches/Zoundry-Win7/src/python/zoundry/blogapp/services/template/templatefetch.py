from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.services.backgroundtask.backgroundtaskimpl import ZBackgroundTask
from zoundry.base.net.httpdownload import IZHttpWebpageGetterListener
from zoundry.base.net.httpdownload import ZHttpWebpageGetter
from zoundry.base.util.fileutil import makeRelativePath
from zoundry.base.util.schematypes import ZSchemaDateTime
from zoundry.base.util.zthread import IZRunnable
from zoundry.base.xhtml.xhtmlio import loadXhtmlDocumentFromString
from zoundry.blogapp.constants import IZBlogAppServiceIDs
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.services.datastore.blogdocumentimpl import ZBlogDocument
from zoundry.blogapp.services.datastore.documentimpl import ZXhtmlContent
from zoundry.blogapp.services.pubsystems.blog.blogcommands import createBlogPublisherFromAccount
from zoundry.blogapp.services.template.templateimpl import ZTemplate
from zoundry.blogapp.services.template.templatetrim import ZTemplateTrimmer

# ------------------------------------------------------------------------------
# Listener interface for listeners of the template fetcher.
# ------------------------------------------------------------------------------
class IZTemplateFetchListener:

    def onFetchStart(self):
        u"""onFetchStart() -> None
        Called when the fetch process starts.""" #$NON-NLS-1$
    # end onFetchStart()

    def onFetchTemplatePublished(self, permaLink):
        u"""onFetchTemplatePublished(string) -> None
        Called after the template post has been
        successfully published.""" #$NON-NLS-1$
    # end onFetchTemplatePublished()

    def onFetchTemplateDownloaded(self):
        u"""onFetchTemplateDownloaded() -> None
        Called after the template has been downloaded.""" #$NON-NLS-1$
    # end onFetchTemplateDownloaded()

    def onFetchTemplateTrimmed(self):
        u"""onFetchTemplateTrimmed() -> None
        Called after the template has been trimmed.""" #$NON-NLS-1$
    # end onFetchTemplateTrimmed()

    def onFetchTemplateSaved(self):
        u"""onFetchTemplateSaved() -> None
        Called after the template has been saved.""" #$NON-NLS-1$
    # end onFetchTemplateSaved()

    def onFetchProgressInfo(self, text):
        u"""onFetchProgressInfo(string) -> None
        Called at various points during the fetch to
        provide textual feedback.""" #$NON-NLS-1$
    # end onFetchProgressInfo()

    def onFetchComplete(self, templateId):
        u"""onFetchComplete(id) -> None
        Called when the fetch process completes.""" #$NON-NLS-1$
    # end onFetchComplete()

    def onFetchCancelled(self):
        u"""onFetchCancelled() -> None
        Called if the fetch is cancelled by the user.""" #$NON-NLS-1$
    # end onFetchCancelled()

    def onFetchError(self, error):
        u"""onFetchError(exception) -> None
        Called if an error occurs.""" #$NON-NLS-1$
    # end onFetchError()

# end IZTemplateFetchListener


# ------------------------------------------------------------------------------
# Takes multiple listeners and makes them appear to be a single listener.
# ------------------------------------------------------------------------------
class ZAggregateTemplateFetchListener(IZTemplateFetchListener):

    def __init__(self):
        self.delegates = []
    # end __init__()

    def addDelegate(self, listener):
        self.delegates.append(listener)
    # end addDelegate()

    def onFetchStart(self):
        for listener in self.delegates:
            listener.onFetchStart()
    # end onFetchStart()

    def onFetchComplete(self, templateId):
        for listener in self.delegates:
            listener.onFetchComplete(templateId)
    # end onFetchComplete()

# end ZAggregateTemplateFetchListener

# ------------------------------------------------------------------------------
# This class is responsible for fetching the current template for a blog.  It
# will use the template service to create a new template.  The final callback
# will include the new template's templateId.
#
# The steps to fetch a blog template are as follows:
#
#  1) publish a special 'template' blog post
#  2) get the permalink for the new post
#  3) scrape the HTML found at the permalink
#  4) removing excess HTML from the resulting xhtml document
#  5) add the xhtml content to the template
#  6) download all dependent resources, adding them to the template
#  7) done
# ------------------------------------------------------------------------------
class ZTemplateFetcher(IZRunnable, IZHttpWebpageGetterListener):

    def __init__(self, blog, listener):
        self.blog = blog
        self.listener = listener
        if self.listener is None:
            self.listener = IZTemplateFetchListener()
        self.cancelled = False
        self.error = None
    # end __init__()

    def setListener(self, listener):
        self.listener = listener
    # end setListener()

    def cancel(self):
        self.cancelled = True
    # end cancel()

    def run(self):
        self.listener.onFetchStart()
        try:
            permaLink = self._publishTemplatePost()
            self.listener.onFetchTemplatePublished(permaLink)
            if self.cancelled:
                return

            template = self._createTemplate()
            self._downloadTemplate(permaLink, template)
            if self.error is not None:
                raise self.error
            self.listener.onFetchTemplateDownloaded()
            if self.cancelled:
                return

            self._trimTemplate(template)
            self.listener.onFetchTemplateTrimmed()
            if self.cancelled:
                return

            self._saveTemplate(template)
            templateId = template.getId()
            self.blog.setTemplateId(templateId)
            self._saveBlog()
            self.listener.onFetchTemplateSaved()
            if self.cancelled:
                return

            self._deleteTemplatePost()
            self.listener.onFetchComplete(template.getId())
        except Exception, ze:
            self.listener.onFetchError(ze)
    # end run()

    def _publishTemplatePost(self):
        publisher = self._getPublisher()
        blog = self._getBlog()
        self.document = self._createDocument()
        xhtmlDoc = self.document.getContent().getXhtmlDocument()
        self.blogInfo = publisher.postEntry(blog, self.document, xhtmlDoc)
        self.document.addBlogInfo(self.blogInfo)
        return self.blogInfo.getPublishInfo().getUrl()
    # end _publishTemplatePost()

    def _createTemplate(self):
        templateSvc = getApplicationModel().getService(IZBlogAppServiceIDs.TEMPLATE_SERVICE_ID)
        # FIXME (EPW) add createTemplate() variant that takes a bool - add/noadd.  then 'add' the template to the service at the end
        template = templateSvc.createTemplate()
        if template is None:
            template = ZTemplate()
        return template
    # end _createTemplate()

    def _downloadTemplate(self, permaLink, template):
        templateDir = template.getTemplateDirectory()
        webPageGetter = ZHttpWebpageGetter(permaLink, templateDir, self)
        rootFilePath = webPageGetter.saveAsWebpage()
        rootFile = makeRelativePath(templateDir, rootFilePath)
        template.setRootFileName(rootFile)
    # end _downloadTemplate()

    def _trimTemplate(self, template):
        trimmer = ZTemplateTrimmer(template)
        trimmer.trim()
    # end _trimTemplate()

    def _saveTemplate(self, template):
        templateSvc = getApplicationModel().getService(IZBlogAppServiceIDs.TEMPLATE_SERVICE_ID)
        templateSvc.saveTemplate(template)
    # end _saveTemplate()

    def _saveBlog(self):
        accountStore = getApplicationModel().getService(IZBlogAppServiceIDs.ACCOUNT_STORE_SERVICE_ID)
        accountStore.saveAccount(self.blog.getAccount())
    # end _saveBlog()

    def _deleteTemplatePost(self):
        publisher = self._getPublisher()
        publisher.deleteEntry(self.blog, self.document)
    # end _deleteTemplatePost()

    def _getPublisher(self):
        publisherService = getApplicationModel().getService(IZBlogAppServiceIDs.PUBLISHING_SERVICE_ID)
        return createBlogPublisherFromAccount(self._getAccount(), publisherService)
    # end _getPublisher()

    def _getAccount(self):
        return self.blog.getAccount()
    # end _getAccount()

    def _getBlog(self):
        return self.blog
    # end _getBlog()

    def _createDocument(self):
        document = ZBlogDocument()
        document.setTitle(u"RAVEN_TEMPLATE_FETCH_TITLE") #$NON-NLS-1$
        document.setCreationTime(ZSchemaDateTime())
        document.setLastModifiedTime(ZSchemaDateTime())

        xhtmlDoc = loadXhtmlDocumentFromString(u"<p id='_raven_template_body'>RAVEN_TEMPLATE_FETCH_BODY</p>") #$NON-NLS-1$
        content = ZXhtmlContent()
        content.setMode(u"xml") #$NON-NLS-1$
        content.setType(u"application/xhtml+xml") #$NON-NLS-1$
        content.setXhtmlDocument(xhtmlDoc)
        document.setContent(content)

        return document
    # end _createDocument()

    def onWebpageGetterResourceStarted(self, url, type):
        self.listener.onFetchProgressInfo(_extstr(u"templatefetch.DownloadingResource") % url) #$NON-NLS-1$
    # end onWebpageGetterResourceStarted()

    def onWebpageGetterResourceComplete(self, url):
        self.listener.onFetchProgressInfo(_extstr(u"templatefetch.Resource_Downloaded") % url) #$NON-NLS-1$
    # end onWebpageGetterResourceComplete()

    def onWebpageGetterError(self, error):
        self.error = error
    # end onWebpageGetterError()
    
    def _getUrlFilename(self, url):
        pass
    # end _getUrlFilename()

# end ZTemplateFetcher


# ------------------------------------------------------------------------------
# Class that runs the template fetcher as a background task.
# ------------------------------------------------------------------------------
class ZTemplateFetcherTask(ZBackgroundTask):

    def __init__(self):
        ZBackgroundTask.__init__(self)

        self.customAttributes = {}
    # end __init__()

    def isResumable(self):
        return False
    # end isResumable()

    def getCustomAttributes(self):
        return self.customAttributes
    # end getCustomAttributes()

    def setCustomAttributes(self, attributeMap):
        self.customAttributes = attributeMap
    # end setCustomAttributes()

# end ZTemplateFetcherTask
