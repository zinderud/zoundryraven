from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.global_services import getLoggerService
from zoundry.base.xhtml.xhtmlanalyzers import IZXhtmlAnalyser
from zoundry.base.xhtml.xhtmltelements import ZXhtmlElement
from zoundry.base.xhtml.xhtmltelements import ZXhtmlImage
from zoundry.base.xhtml.xhtmltelements import ZXhtmlLink
from zoundry.blogapp.constants import IZBlogAppServiceIDs
from zoundry.blogapp.ui.util.blogutil import getBlogFromPubMetaData

# --------------------------------------------------------------------------
# Publishing handler context
# --------------------------------------------------------------------------
class IZPublishingHandlerContext:

    def saveMetaData(self):
        u"""saveMetaData() -> void
        Saves document meta data."""  #$NON-NLS-1$
        pass

    def getBlog(self):
        u"""getBlog() -> IZBlog
        Returns blog being published to."""  #$NON-NLS-1$
        pass

    def getTitle(self):
        u"""getTitle() -> string
        Returns document"""  #$NON-NLS-1$
        pass

    def getUrl(self):
        u"""getUrl() -> string
        Returns entry URL if published otherwise returns None"""  #$NON-NLS-1$
        pass

    def getXhtmlDocument(self):
        u"""getXhtmlDocument() -> ZXhtmlDocument
        Xhtml document to publish."""  #$NON-NLS-1$
        pass

    def getPubMetaData(self):
        u"""getPubMetaData() -> IZPubMetaData
        """  #$NON-NLS-1$
        pass

    def getTagwordList(self):
        u"""getTagwordList() -> list
        Returns list of IZTagwords objects.
        """  #$NON-NLS-1$
        pass

    def getTrackbackList(self):
        u"""getTrackbackList() -> list
        Returns list of IZTrackback objects in the document.
        """  #$NON-NLS-1$
        pass

    def getBlogInfo(self):
        u"""getBlogInfo() -> IZBlogInfo or None""" #$NON-NLS-1$
        pass

    def notifyBegin(self, izBlogPublishHandler):#@UnusedVariable
        u"""notifyBegin() -> void
        """  #$NON-NLS-1$
        pass

    def notifyProgress(self, izBlogPublishHandler, message, workamount, logMessage) :#@UnusedVariable
        u"""notifyProgress() -> void
        """  #$NON-NLS-1$
        pass

    def notifyEnd(self, izBlogPublishHandler):#@UnusedVariable
        u"""notifyEnd() -> void
        """  #$NON-NLS-1$
        pass

    def logInfo(self, izBlogPublishHandler, message):#@UnusedVariable
        u"""notifyEnd() -> void
        """  #$NON-NLS-1$
        pass

    def logWarning(self, izBlogPublishHandler, message):#@UnusedVariable
        u"""logWarning() -> void
        """  #$NON-NLS-1$
        pass

    def logError(self, izBlogPublishHandler, message): #@UnusedVariable
        u"""logError() -> void
        """  #$NON-NLS-1$
        pass

    def logException(self, izBlogPublishHandler, exception):#@UnusedVariable
        u"""logException() -> void
        """  #$NON-NLS-1$
        pass


# --------------------------------------------------------------------------
# Basic imple of handler context
# --------------------------------------------------------------------------
class ZPublishingHandlerContextBase(IZPublishingHandlerContext):

    def __init__(self, zblogDocument, xhtmlDocument, pubMetaData,):
        self.zblogDocument = zblogDocument
        self.xhtmlDocument = xhtmlDocument
        self.pubMetaDta = pubMetaData
        self.blog = getBlogFromPubMetaData( pubMetaData )

    def saveMetaData(self):
        dataStoreService = getApplicationModel().getService(IZBlogAppServiceIDs.DATA_STORE_SERVICE_ID)
        dataStoreService.saveDocument(self.zblogDocument, True)
    # end saveMetaData()

    def getBlog(self):
        return self.blog

    def getTitle(self):
        return self.zblogDocument.getTitle()

    def getUrl(self):
        return self.zblogDocument.getPublishedUrl( self.getBlog().getId() )

    def getXhtmlDocument(self):
        return self.xhtmlDocument

    def getPubMetaData(self):
        return self.pubMetaDta

    def getTagwordList(self):
        return self.zblogDocument.getTagwordsList()

    def getTrackbackList(self):
        return self.zblogDocument.getTrackbacks()
    # end getTrackbackList

    def getBlogInfo(self):
        return self.zblogDocument.getBlogInfo( self.blog.getId() )
    # end getBlogInfo

    def notifyBegin(self, izBlogPublishHandler):#@UnusedVariable
        pass

    def notifyProgress(self, izBlogPublishHandler, message, workamount):#@UnusedVariable
        pass

    def notifyEnd(self, izBlogPublishHandler):#@UnusedVariable
        pass

    def _debug(self, izBlogPublishHandler, message): #@UnusedVariable
        pass
    # end
    def logInfo(self, izBlogPublishHandler, message):#@UnusedVariable
        s = u"[%s] %s" % (izBlogPublishHandler.getName(), message) #$NON-NLS-1$
        self._debug(izBlogPublishHandler, s)
        if getLoggerService():
            getLoggerService().debug(message)
        else:
            print message.encode(u'iso-8859-1', u'replace') #$NON-NLS-1$ #$NON-NLS-2$

    def logWarning(self, izBlogPublishHandler, message):#@UnusedVariable
        s = u"[WARN][%s] %s" % (izBlogPublishHandler.getName(), message) #$NON-NLS-1$
        self._debug(izBlogPublishHandler, s)
        if getLoggerService():
            getLoggerService().warning(message)
        else:
            print message.encode(u'iso-8859-1', u'replace') #$NON-NLS-1$ #$NON-NLS-2$

    def logError(self, izBlogPublishHandler, message): #@UnusedVariable
        s = u"[ERROR][%s] %s" % (izBlogPublishHandler.getName(), message) #$NON-NLS-1$
        self._debug(izBlogPublishHandler, s)
        if getLoggerService():
            getLoggerService().error(message)
        else:
            print message.encode(u'iso-8859-1', u'replace') #$NON-NLS-1$ #$NON-NLS-2$

    def logException(self, izBlogPublishHandler, exception):#@UnusedVariable
        s = u"[EXCEPTION][%s] %s" % (izBlogPublishHandler.getName(), unicode(exception)) #$NON-NLS-1$
        self._debug(izBlogPublishHandler, s)
        if getLoggerService():
            getLoggerService().exception(exception)


# --------------------------------------------------------------------------
# Interface that is invoked during to publising the document.
# --------------------------------------------------------------------------
class IZBlogPublishHandler:

    def getName(self):
        u"""getName() -> string
        Returns name of handler
        """  #$NON-NLS-1$
        pass

    def cancel(self):
        u"""cancel() -> void
        Cancels/stops current work.
        """  #$NON-NLS-1$
        pass

    def hasError(self):
        u"""hasError() -> bool
        Returns true if there were any errors.
        """  #$NON-NLS-1$
        pass

    def getError(self):
        u"""getError() -> string
        Returns error message.
        """  #$NON-NLS-1$
        pass

    def isAbortOnError(self):
        u"""isAbortOnError() -> bool
        Returns true if the publishing process should be aborted on errors.
        """  #$NON-NLS-1$
        pass

    def getTotalWorkUnits(self):
        u"""getTotalWorkUnits() -> int
        Calculate and return estimated work units (steps).
        """  #$NON-NLS-1$
        pass

    def prepare(self, izPublishingHandlerContext): #@UnusedVariable
        u"""prepare(IZPublishingHandlerContext) -> void
        Pre-process including estimating the number of work units.
        """  #$NON-NLS-1$
        pass

    def process(self, izPublishingHandlerContext): #@UnusedVariable
        u"""process(IZPublishingHandlerContext) -> void
        Handle the publising work
        """  #$NON-NLS-1$
        pass

    def validateConfiguration(self, izPublishingHandlerContext, validationReporter): #@UnusedVariable
        u"""validateConfiguration(IZPublishingHandlerContext, IZConfigValidationReporter) -> void
        Implementation of IZConfigValidatable.
        """  #$NON-NLS-1$
        pass
    # end validateConfiguration()

# --------------------------------------------------------------------------
# Base class for IZBlogPublishHandler
# --------------------------------------------------------------------------
class ZBlogPublishHandlerBase(IZBlogPublishHandler):

    def __init__(self, name):
        self.name = name
        self.error = None
        self.canceled = False
        self.totalWorkUnits = 0
        self.abortOnError = False
        self.context = None
        self.logger = getLoggerService()
    # end __init__()

    def _getLogger(self):
        return self.logger
    # end _getLogger()

    def _getContext(self):
        return self.context

    def _setContext(self, context):
        self.context = context

    def getName(self):
        return self.name

    def cancel(self):
        self.canceled = True

    def isCancelled(self):
        return self.canceled

    def hasError(self):
        return self.error is not None

    def getError(self):
        return self.error

    def _clearError(self):
        self.error = None

    def isAbortOnError(self):
        return self.abortOnError

    def _setAbortOnError(self, abort):
        self.abortOnError = abort

    def getTotalWorkUnits(self):
        return self.totalWorkUnits

    def _setTotalWorkUnits(self, workunits):
        self.totalWorkUnits = workunits

    def validateConfiguration(self, izPublishingHandlerContext, validationReporter): #@UnusedVariable
        self._setContext(izPublishingHandlerContext)
        self._validateConfiguration(validationReporter)
    # end validateConfiguration()

    def _validateConfiguration(self, validationReporter): #@UnusedVariable
        u"""validateConfiguration(IZConfigValidationReporter) -> void
        Sublcasses must implement to report validation messages
        """  #$NON-NLS-1$
        pass
    # end _validateConfiguration()

    def prepare(self, izPublishingHandlerContext): #@UnusedVariable
        if self.isCancelled():
            return
        self._setContext(izPublishingHandlerContext)
        self._clearError()
        self._prepare()
    # end prepare()

    def _prepare(self): #@UnusedVariable
        u"""_prepare() -> void
        Subclasses must implement this method.
        """  #$NON-NLS-1$
        pass
    # end _prepare()

    def process(self, izPublishingHandlerContext): #@UnusedVariable
        if self.isCancelled():
            return
        self._setContext(izPublishingHandlerContext)
        self._clearError()
        izPublishingHandlerContext.notifyBegin(self)
        self._process()
        izPublishingHandlerContext.notifyEnd(self)

    def _process(self): #@UnusedVariable
        u"""_process() -> void
        Subclasses must implement this method.
        """  #$NON-NLS-1$
        pass


# --------------------------------------------------------------------------
# Base anaylyser for xhtml content in the blog post entry
# --------------------------------------------------------------------------
class ZBlogPostContentAnalyserBase(IZXhtmlAnalyser):

    def analyseElement(self, node):
        if node.localName.lower() == u"a": #$NON-NLS-1$
            elem = ZXhtmlLink(node, 0)
            self._analyseZXhtmlLink(elem)

        elif node.localName.lower() == u"img": #$NON-NLS-1$
            elem = ZXhtmlImage(node, 0)
            self._analyseZXhtmlImage(elem)
        else:
            elem = ZXhtmlElement(node)
            self._analyseZXhtmlElement(elem)

    def _analyseZXhtmlElement(self, iZXhtmlElement): #@UnusedVariable
        pass
    # end _analyseZXhtmlElement

    def _analyseZXhtmlLink(self, iZXhtmlLink): #@UnusedVariable
        pass
    # end _analyseZXhtmlLink

    def _analyseZXhtmlImage(self, iZXhtmlImage): #@UnusedVariable
        pass
    # end _analyseZXhtmlImage