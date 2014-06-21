from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.global_services import getLoggerService
from zoundry.appframework.services.backgroundtask.backgroundtaskimpl import ZBackgroundTask
from zoundry.base.exceptions import ZException
from zoundry.base.net.httpdownload import IZHttpWebpageGetterListener
from zoundry.base.net.httpdownload import ZHttpWebpageGetter
from zoundry.base.util.fileutil import deleteDirectory
from zoundry.base.util.fileutil import makeRelativePath
from zoundry.base.util.text.textutil import getSafeString
from zoundry.base.xhtml.xhtmlio import loadXhtmlDocumentFromFile
from zoundry.base.xhtml.xhtmlnet import ZSimpleXHtmlHTTPRequest
from zoundry.base.zdom.domvisitor import ZDomVisitor
from zoundry.blogapp.constants import IZBlogAppServiceIDs
from zoundry.blogapp.constants import IZBlogAppUserPrefsKeys
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.services.pubsystems.blog.blogcommands import createBlogPublisherFromAccount
from zoundry.blogapp.services.template.template import IZTemplateConstants
import os
import string

# ------------------------------------------------------------------------------
# Thrown when the fetch is cancelled.
# ------------------------------------------------------------------------------
class ZTemplateFetchCancelledException(ZException):
    
    def __init__(self):
        ZException.__init__(self)
    # end __init__()
    
# end ZTemplateFetchCancelledException


# ------------------------------------------------------------------------------
# Visitor that finds an element.  Returns true if it exists.
# ------------------------------------------------------------------------------
class ZElementFindingVisitor(ZDomVisitor):

    def __init__(self, element):
        self.element = element
        self.found = False
    # end __init__()

    def isFound(self):
        return self.found
    # end isFound()

    def visitElement(self, element):
        if element.element == self.element.element:
            self.found = True
            return False
    # end visitElement()

# end ZElementFindingVisitor


# ------------------------------------------------------------------------------
# This visitor looks for an element that matches the criteria.
# ------------------------------------------------------------------------------
class ZFindElementsByCriteriaVisitor(ZDomVisitor):

    def __init__(self, criteriaStr, numChars):
        self.criteriaStr = criteriaStr
        self.numChars = numChars
        self.trimmedCriteriaStr = self._trim(self.criteriaStr)
        self.isInBody = False

        self.elements = []
    # end __init__()

    def getElements(self):
        return self.elements
    # end getElements()

    def _trim(self, text):
        trimmedText = text
        if self.numChars != -1 and len(text) > self.numChars:
            trimmedText = text[0:self.numChars]
        return trimmedText
    # end _trim()

    def visitElement(self, element):
        elementStr = getSafeString(element.selectRaw(u"string(.)")) #$NON-NLS-1$
        elementStr = string.strip(elementStr)
        elementStr = self._trim(elementStr)
        if elementStr == self.trimmedCriteriaStr and self.isInBody:
            self.elements.append(element)

        if element.nodeName.lower() == u"body": #$NON-NLS-1$
            self.isInBody = True
    # end visitElement()

# end ZFindElementsByCriteriaVisitor


# ------------------------------------------------------------------------------
# Listener interface for the blog template grab process.
# ------------------------------------------------------------------------------
class IZBlogTemplateGrabListener:

    def grabStarted(self):
        u"""grabStarted() -> None
        Called when the grab process starts.""" #$NON-NLS-1$
    # end grabStarted()

    def grabBlogPostAnalysisStarted(self):
        u"""grabBlogPostAnalysisStarted() -> None
        Called when the grab has started analysing the
        blog's published content.""" #$NON-NLS-1$
    # end grabBlogPostAnalysisStarted()

    def grabBlogPostAnalysisComplete(self):
        u"""grabBlogPostAnalysisComplete() -> None
        Called when the blog posts have been analysed.""" #$NON-NLS-1$
    # end grabBlogPostAnalysisComplete()

    def grabFeedback(self, message):
        u"""grabFeedback(string) -> None
        Provides some feedback to the listener as the grab is
        being performed.""" #$NON-NLS-1$
    # end grabFeedback()

    def grabError(self, error):
        u"""grabError(error | exception) -> None
        Called when an error occurs during grabbing.""" #$NON-NLS-1$
    # end grabError()

    def grabComplete(self):
        u"""grabComplete() -> None
        Called when the grab process has completed.""" #$NON-NLS-1$
    # end grabComplete()

# end IZBlogTemplateGrabListener


# ------------------------------------------------------------------------------
# Routes grab event information to a delegate listener after logging debug
# information.
# ------------------------------------------------------------------------------
class ZDebugTemplateGrabListener(IZBlogTemplateGrabListener):

    def __init__(self, delegate, logger):
        self.delegate = delegate
        self.logger = logger
    # end __init__()

    def grabStarted(self):
        self.logger.debug(u"grabStarted") #$NON-NLS-1$
        self.delegate.grabStarted()
    # end grabStarted()

    def grabBlogPostAnalysisStarted(self):
        self.logger.debug(u"grabBlogPostAnalysisStarted") #$NON-NLS-1$
        self.delegate.grabBlogPostAnalysisStarted()
    # end grabBlogPostAnalysisStarted()

    def grabBlogPostAnalysisComplete(self):
        self.logger.debug(u"grabBlogPostAnalysisComplete") #$NON-NLS-1$
        self.delegate.grabBlogPostAnalysisComplete()
    # end grabBlogPostAnalysisComplete()

    def grabFeedback(self, message):
        self.logger.debug(u"grabFeedback: %s" % getSafeString(message)) #$NON-NLS-1$
        self.delegate.grabFeedback(message)
    # end grabFeedback()

    def grabError(self, error):
        ZException(rootCause = error).printStackTrace()
        self.logger.debug(u"grabError") #$NON-NLS-1$
        self.logger.exception(error)
        self.delegate.grabError(error)
    # end grabError()

    def grabComplete(self):
        self.logger.debug(u"grabComplete") #$NON-NLS-1$
        self.delegate.grabComplete()
    # end grabComplete()

# end ZDebugTemplateGrabListener


# ------------------------------------------------------------------------------
# Class that attempts to get (grab) a blog's template information.
# ------------------------------------------------------------------------------
class ZBlogTemplateGrabber(IZHttpWebpageGetterListener):

    def __init__(self, blog):
        self.blog = blog
        self.cancelled = False
        self.logger = getLoggerService()
    # end __init__()

    def cancel(self):
        self.cancelled = True
    # end cancel()

    def grab(self, listener = None):
        u"""grab(IZBlogTemplateGrabListener) -> IZTemplate
        Grabs a blog's template.""" #$NON-NLS-1$
        # Steps to grabbing a blog template:
        #  1) Get the blog's 5 most recent posts
        #    1a) If no recent posts, fail
        #  2) For each of the 5 blog posts,
        #    2a) get the string() value of the post's <body>
        #    2b) get the string() value of the post's <title>
        #    2c) download the "ALT" html for the blog post (http or https)
        #    2d) depth-first traverse the ALT html, looking for the deepest
        #        element with a string() value equal to the post's <body>/<title>
        #    2e) if not found, continue
        #    2f) if found, create a new template object
        #  3) If no template object was created, fail
        #  4) Download template supporting files - re-write root template HTML accordingly
        #  5) Trim the template's root HTML file three times:
        #    5a) Trim 1 - All
        #    5b) Trim 2 - Body and Title
        #    5c) Trim 3 - Body only
        #  6) Return template object

        self.listener = listener
        if self.listener is None:
            self.listener = IZBlogTemplateGrabListener()
        self.listener = ZDebugTemplateGrabListener(self.listener, self.logger)

        try:
            self.listener.grabStarted()
            template = self._doGrab()
            if self.cancelled:
                return None
            self.listener.grabComplete()
            return template
        except ZTemplateFetchCancelledException, ce: #@UnusedVariable
            return None
        except Exception, e:
            self.listener.grabError(e)
    # end grab()

    def _doGrab(self):
        account = self.blog.getAccount()
        pubService = getApplicationModel().getService(IZBlogAppServiceIDs.PUBLISHING_SERVICE_ID)
        publisher = createBlogPublisherFromAccount(account, pubService)

        if self.cancelled:
            return None

        self.listener.grabFeedback(_extstr(u"templategrabber.ConnectingToFeed")) #$NON-NLS-1$

        template = None
        documents = publisher.listEntries(self.blog, 5)

        if self.cancelled:
            return None

        self.listener.grabBlogPostAnalysisStarted()
        if len(documents) == 0:
            raise ZException(_extstr(u"templategrabber.BlogHasNoPosts")) #$NON-NLS-1$
        for document in documents:
            if self.cancelled:
                return None
            self.listener.grabFeedback(_extstr(u"templategrabber.AnalysingFrom") % getSafeString(document.getTitle())) #$NON-NLS-1$
            title = document.getTitle()
            content = document.getContent()
            xhtml = content.getXhtmlDocument()
            body = xhtml.getBody()
            bodyStr = getSafeString(body.selectRaw(u"string(.)")) #$NON-NLS-1$
            bodyStr = string.strip(bodyStr)

            if not title or not bodyStr:
                continue

            url = self._getDocumentUrl(document)
            altHtmlDoc = self._downloadAltHtml(url)

            altHtmlDom = altHtmlDoc.getDom()
            if altHtmlDom is None:
                continue

            self.listener.grabFeedback(_extstr(u"templategrabber.FindingBlogPostTitle")) #$NON-NLS-1$
            titleElems = self._findTitleElems(altHtmlDom, title)
            if not titleElems:
                continue

            self.listener.grabFeedback(_extstr(u"templategrabber.FindingBlogPostContent")) #$NON-NLS-1$
            contentElems = self._findContentElems(altHtmlDom, bodyStr)
            if not contentElems:
                continue

            self.listener.grabFeedback(_extstr(u"templategrabber.BlogContentAnalysed")) #$NON-NLS-1$

            if self.cancelled:
                return None

            template = self._fetchTemplate(url, title, bodyStr)
            if template is not None:
                break
        # end foreach

        self.listener.grabBlogPostAnalysisComplete()

        if template is None:
            raise ZException(_extstr(u"templategrabber.UnableToDetectTemplate")) #$NON-NLS-1$

        return template
    # end grab()

    def _getDocumentUrl(self, document):
        blogInfo = document.getBlogInfoList()[0]
        pubInfo = blogInfo.getPublishInfo()
        url = pubInfo.getUrl()
        return url
    # end _getDocumentUrl()

    def _downloadAltHtml(self, url):
        self.listener.grabFeedback(_extstr(u"templategrabber.DownloadingBlogContentForAnalysis")) #$NON-NLS-1$
        request = ZSimpleXHtmlHTTPRequest(url)
        if not request.send():
            return None
        xhtmlDoc = request.getResponse()
        self.listener.grabFeedback(_extstr(u"templategrabber.BlogContentDownloaded_Analysing")) #$NON-NLS-1$
        return xhtmlDoc
    # end _downloadAltHtml()

    def _findTitleElems(self, altHtmlDom, title):
        visitor = ZFindElementsByCriteriaVisitor(title, -1)
        visitor.visit(altHtmlDom)
        return visitor.getElements()
    # end _findTitleElems()

    def _findContentElems(self, altHtmlDom, bodyStr):
        visitor = ZFindElementsByCriteriaVisitor(bodyStr, 256)
        visitor.visit(altHtmlDom)
        return visitor.getElements()
    # end _findContentElems()

    def _fetchTemplate(self, url, title, bodyStr):
        templateService = getApplicationModel().getService(IZBlogAppServiceIDs.TEMPLATE_SERVICE_ID)
        template = templateService.createTemplate()
        templateDir = template.getTemplateDirectory()
        try:
            webPageGetter = ZHttpWebpageGetter(url, templateDir, self)
            webPageGetter.setBasePathToken(IZTemplateConstants.TEMPLATE_BASE_TOKEN)
            rootFilePath = webPageGetter.saveAsWebpage()
            if self.cancelled:
                raise ZTemplateFetchCancelledException()

            rootXHtmlDoc = loadXhtmlDocumentFromFile(rootFilePath)
            rootXHtmlDom = rootXHtmlDoc.getDom()
            titleElems = self._findTitleElems(rootXHtmlDom, title)
            if not titleElems:
                return None
            contentElems = self._findContentElems(rootXHtmlDom, bodyStr)
            if not contentElems:
                return None

            indexAllUTFileName = os.path.join(templateDir, u"index-all-untrimmed.html") #$NON-NLS-1$
            rootXHtmlDom.save(indexAllUTFileName)

            if self.cancelled:
                raise ZTemplateFetchCancelledException()

            for titleElem in titleElems:
                titleElem.removeAllChildren()
                titleMarkerElem = rootXHtmlDom.createElement(u"ravenTitle", titleElem.getNamespaceUri()) #$NON-NLS-1$
                titleElem.appendChild(titleMarkerElem)

            for contentElem in contentElems:
                contentElem.removeAllChildren()
                contentMarkerElem = rootXHtmlDom.createElement(u"ravenBody", contentElem.getNamespaceUri()) #$NON-NLS-1$
                contentElem.appendChild(contentMarkerElem)

            rootFile = makeRelativePath(templateDir, rootFilePath)
            indexAllFileName = u"index-all.html" #$NON-NLS-1$
            indexBodyOnlyFileName = u"index-body.html" #$NON-NLS-1$
            indexTitleAndBodyFileName = u"index-titleBody.html" #$NON-NLS-1$

            template.setRootFileName(rootFile)
            template.setAllFileName(indexAllFileName)
            template.setBodyOnlyFileName(indexBodyOnlyFileName)
            template.setTitleAndBodyFileName(indexTitleAndBodyFileName)

            indexAll = os.path.join(templateDir, indexAllFileName)
            indexTitleAndBody = os.path.join(templateDir, indexTitleAndBodyFileName)
            indexBodyOnly = os.path.join(templateDir, indexBodyOnlyFileName)

            self.listener.grabFeedback(_extstr(u"templategrabber.TemplateDownloaded_Trimming")) #$NON-NLS-1$

            if self.cancelled:
                raise ZTemplateFetchCancelledException()

            # Save the 'all' variant
            rootXHtmlDom.save(indexAll)

            if self.cancelled:
                raise ZTemplateFetchCancelledException()

            # Trim the dom - remove everything except the title and body
            self._trimStageOne(titleElems, contentElems)
            rootXHtmlDom.save(indexTitleAndBody)

            if self.cancelled:
                raise ZTemplateFetchCancelledException()

            # Trim the dom again - remove everything except the body
            self._trimStageTwo(contentElems)
            rootXHtmlDom.save(indexBodyOnly)

            if self.cancelled:
                raise ZTemplateFetchCancelledException()

            self.listener.grabFeedback(_extstr(u"templategrabber.TemplateTrimmedAndSaved")) #$NON-NLS-1$

            return template
        except Exception, e:
            getLoggerService().exception(e)
            deleteDirectory(templateDir, True)
            raise e
    # end _fetchTemplate()

    def _trimStageOne(self, titleElems, contentElems):
        titleElem = titleElems[0]
        contentElem = contentElems[0]
        commonParent = titleElem
        while not self._isAnscestorOf(commonParent, contentElem) and commonParent is not None:
            commonParent = commonParent.parentNode
        self._doTrim(commonParent)
    # end _trimStageOne()

    def _trimStageTwo(self, contentElems):
        contentElem = contentElems[0]
        self._doTrim(contentElem)
    # end _trimStageTwo()

    def _isAnscestorOf(self, someElement, contentElem):
        visitor = ZElementFindingVisitor(contentElem)
        visitor.visit(someElement)
        return visitor.isFound()
    # end _isAnscestorOf()

    def _doTrim(self, elem):
        parent = elem.parentNode
        child = elem
        while not self._isBody(child) and parent is not None:
            self._removeChildrenExcept(parent, child)
            newParent = parent.parentNode
            child = parent
            parent = newParent
    # end _doTrim()

    def _isBody(self, element):
        return element.nodeName.lower() == u"body" #$NON-NLS-1$
    # end _isBody()

    def _removeChildrenExcept(self, parent, childToKeep):
        for child in parent.getChildren():
            if child.node != childToKeep.node:
                parent.removeChild(child)
    # end _removeChildrenExcept()

    def onWebpageGetterStart(self):
        self.listener.grabFeedback(_extstr(u"templategrabber.DownloadingResources")) #$NON-NLS-1$
    # end onWebpageGetterStart()

    def onWebpageGetterResourceStarted(self, url, type):
        self.currentResource = url
        self.listener.grabFeedback(u"%s: %s" % (_extstr(u"templategrabber.Downloading"), unicode(url))) #$NON-NLS-1$ #$NON-NLS-2$
    # end onWebpageGetterResourceStarted()

    def onWebpageGetterResourceConnected(self, url, contentType, contentLength): #@UnusedVariable
        self.currentResourceLength = self._formatKB(contentLength)
        self.currentResourceDownloadedSoFar = 0
        self.listener.grabFeedback(u"%s: %s (%d/%d KB)" % (_extstr(u"templategrabber.Downloading"), unicode(url), 0, self.currentResourceLength)) #$NON-NLS-1$ #$NON-NLS-2$
    # end onWebpageGetterResourceConnected()

    def onWebpageGetterResourceChunk(self, url, bytesDownloaded):
        self.currentResourceDownloadedSoFar = self.currentResourceDownloadedSoFar + bytesDownloaded
        self.listener.grabFeedback(u"%s: %s (%d/%d KB)" % (_extstr(u"templategrabber.Downloading"), unicode(url), self._formatKB(self.currentResourceDownloadedSoFar), self.currentResourceLength)) #$NON-NLS-1$ #$NON-NLS-2$
    # end onWebpageGetterResource()

    def onWebpageGetterError(self, error):
        self.listener.grabError(error)
    # end onWebpageGetterError()

    def _formatKB(self, value):
        if value == 0:
            return 0
        return max(1, (value / 1024))
    # end _formatKB()

# end ZBlogTemplateGrabber


# ------------------------------------------------------------------------------
# Implementation of a background task for grabbing a blog template.
# ------------------------------------------------------------------------------
class ZBlogTemplateGrabberBGTask(ZBackgroundTask, IZBlogTemplateGrabListener):

    def __init__(self):
        self.blog = None
        self.grabber = None
        self.templateName = None
        self.bMakeDefaultTemplate = False
        self.customAttributes = {}

        ZBackgroundTask.__init__(self)
    # end __init__()

    def initialize(self, blog, templateName, bMakeDefaultTemplate):
        self.blog = blog
        self.templateName = templateName
        self.bMakeDefaultTemplate = bMakeDefaultTemplate

        self.grabber = ZBlogTemplateGrabber(self.blog)
        self.setName(_extstr(u"templategrabber.DownloadingBlogTemplate")) #$NON-NLS-1$
        self.setNumWorkUnits(4)
    # end initialize()

    def getCustomAttributes(self):
        return self.customAttributes
    # end getCustomAttributes()

    def setCustomAttributes(self, attributeMap):
        self.customAttributes = attributeMap
    # end setCustomAttributes()

    def isResumable(self):
        return False
    # end isResumable()

    def _doCancel(self):
        self.grabber.cancel()
    # end _doCancel()

    def _run(self):
        template = self.grabber.grab(self)
        if template is not None and not self.cancelled:
            template.setName(self.templateName)
            template.setSource(u"Blog [%s]" % getSafeString(self.blog.getName())) #$NON-NLS-1$
            service = getApplicationModel().getService(IZBlogAppServiceIDs.TEMPLATE_SERVICE_ID)
            service.saveTemplate(template)
            if self.bMakeDefaultTemplate:
                self.blog.setTemplateId(template.getId())
                self.blog.getPreferences().setUserPreference(IZBlogAppUserPrefsKeys.BLOG_OVERRIDE_TEMPLATE, True)
                accountService = getApplicationModel().getService(IZBlogAppServiceIDs.ACCOUNT_STORE_SERVICE_ID)
                accountService.saveAccount(self.blog.getAccount())
    # end _run()

    def grabStarted(self):
        self._incrementWork(_extstr(u"templategrabber.TemplateDownloadStarted"), 1, True) #$NON-NLS-1$
    # end grabStarted()

    def grabBlogPostAnalysisStarted(self):
        self._incrementWork(_extstr(u"templategrabber.AnalysingBlogContent"), 1, True) #$NON-NLS-1$
    # end grabBlogPostAnalysisStarted()

    def grabBlogPostAnalysisComplete(self):
        self._incrementWork(_extstr(u"templategrabber.BlogContentAnalysed"), 1, True) #$NON-NLS-1$
    # end grabBlogPostAnalysisComplete()

    def grabFeedback(self, message):
        self._incrementWork(message, 0, True)
    # end grabFeedback()

    def grabError(self, error):
        self._reportException(error)
    # end grabError()

    def grabComplete(self):
        self._incrementWork(_extstr(u"templategrabber.TemplateDownloaded"), 1, True) #$NON-NLS-1$
    # end grabComplete()

# end ZBlogTemplateGrabberBGTask
