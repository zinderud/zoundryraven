from zoundry.base.util.validatables import IZConfigValidatable
from zoundry.blogapp.services.pubsystems.blog.handlers.postpubhandlers import ZSendTrackbackPublishHandler
from zoundry.blogapp.services.pubsystems.blog.handlers.postpubhandlers import ZWeblogPingPublishHandler
from zoundry.blogapp.services.pubsystems.blog.handlers.prepubhandlers import ZAddPoweredByPrePublishHandler
from zoundry.blogapp.services.pubsystems.blog.handlers.prepubhandlers import ZAddTagwordsPrePublishHandler
from zoundry.blogapp.services.pubsystems.blog.handlers.prepubhandlers import ZCreateAffiliateLinksPublishHandler
from zoundry.blogapp.services.pubsystems.blog.handlers.prepubhandlers import ZInitContentPrePublishHandler
from zoundry.blogapp.services.pubsystems.blog.handlers.pubprocesshandlers import ZPublishingHandlerContextBase
from zoundry.blogapp.services.pubsystems.blog.handlers.pubuploadhandler import ZUploadContentPrePublishHandler
from zoundry.blogapp.ui.util.blogutil import createDefaultPubMetaDataForBlog


# --------------------------------------------------------------------------
#
# --------------------------------------------------------------------------
class ZPublishingHandlerContext(ZPublishingHandlerContextBase):
    def __init__(self, zblogDocument, xhtmlDocument, pubMetaData, notifyCallback):
        ZPublishingHandlerContextBase.__init__(self, zblogDocument, xhtmlDocument, pubMetaData)
        self.notifyCallback = notifyCallback
        self.workcompleted = 0

    def notifyBegin(self, izBlogPublishHandler):#@UnusedVariable
        #print "**BEGIN %s" % izBlogPublishHandler.getName()
        pass

    def notifyProgress(self, izBlogPublishHandler, message, workamount, logMessage):#@UnusedVariable
        self.workcompleted = self.workcompleted + workamount
        if self.notifyCallback:
            self.notifyCallback.notifyProgress(izBlogPublishHandler, message, workamount, logMessage)
    # end notifyProgress

    def notifyEnd(self, izBlogPublishHandler):#@UnusedVariable
        #print "**END %s" % izBlogPublishHandler.getName()
        pass

    def _debug(self, izBlogPublishHandler, message): #@UnusedVariable
        if self.notifyCallback and message:
            self.notifyCallback.notifyDebug(izBlogPublishHandler, message)
    # end _debug

# --------------------------------------------------------------------------
# Class responsible for formatting the document for publishing.
# --------------------------------------------------------------------------
class ZBlogDocumentPublishProcessor(IZConfigValidatable):

    def __init__(self, zblog, zblogDocument, zpubMetaData, notifyCallback):
        self.notifyCallback = notifyCallback
        self.preprocessHandlers = None
        self.postprocessHandlers = None
        self.totalWorkUnits = 0
        self.prepared = False
        self.preprocessed = False
        self.postprocessed =False
        self.zblog = zblog
        self.zblogDocument = zblogDocument
        # get copy of xhtml document.
        self.xhtmlDocument = self.zblogDocument.getContent().getXhtmlDocument().clone()
        # FIXME (PJ) create immutable copy of meta data.
        self.zpubMetaData = zpubMetaData
        # if meta data is not given, the look in blogdocument for pubmeta data.
        if self.zpubMetaData is None:
            for metadata in zblogDocument.getPubMetaDataList():
                if metadata.getBlogId() == zblog.getId():
                    self.zpubMetaData = metadata
                    break
        # default case.
        if self.zpubMetaData is None:
            self.zpubMetaData = createDefaultPubMetaDataForBlog(zblog)
        self.context = ZPublishingHandlerContext(zblogDocument, self.xhtmlDocument, self.zpubMetaData, self)
        self._createPreprocessHandlers()
        self._createPostprocessHandlers()
    # end __inti__()

    def validateConfiguration(self, validationReporter): #@UnusedVariable
        self._validateHandlers(self.preprocessHandlers, validationReporter)
        self._validateHandlers(self.postprocessHandlers, validationReporter)
    # end validateConfiguration()

    def _validateHandlers(self, handlers, validationReporter):
        if handlers:
            for handler in handlers:
                handler.validateConfiguration(self.context, validationReporter)
    # end _validateHandlers

    def notifyProgress(self, izBlogPublishHandler, message, workamount, logMessage):#@UnusedVariable
        if self.notifyCallback:
            self.notifyCallback.notifyProgress(message, workamount, logMessage)
    # end notifyProgress()

    def notifyDebug(self, izBlogPublishHandler, message):#@UnusedVariable
        if self.notifyCallback:
            self.notifyCallback.notifyDebug(message)
    # end notifyDebug()

    def _createPreprocessHandlers(self):
        self.preprocessHandlers = []
        self.preprocessHandlers.append( ZInitContentPrePublishHandler() )
        self.preprocessHandlers.append ( ZCreateAffiliateLinksPublishHandler(self.zblog) )
        # FIXME (PJ) insert user contributed handlers
        self.preprocessHandlers.append( ZAddPoweredByPrePublishHandler() )
        self.preprocessHandlers.append( ZAddTagwordsPrePublishHandler() )
        # media upload
        self.preprocessHandlers.append( ZUploadContentPrePublishHandler(self.zblog) )
    # end _createPreprocessHandlers()

    def _createPostprocessHandlers(self):
        self.postprocessHandlers = []
        self.postprocessHandlers.append( ZWeblogPingPublishHandler() )
        self.postprocessHandlers.append( ZSendTrackbackPublishHandler() )
    # end _createPostprocessHandlers()

    def _calculateWorkUnits(self, handlers):
        total = 0
        for handler in handlers:
            total = total + handler.getTotalWorkUnits()
        return total
    # end _calculateWorkUnits()

    def _runPrepare(self, handlers):
        success = True
        for handler in handlers:
            try:
                handler.prepare(self.context)
            except Exception, e:
                self.context.logException(handler,e)
                if handler.isAbortOnError():
                    success = False
                    break
        return success
    # end _runPrepare()

    def _runProcess(self, handlers):
        success = True
        for handler in handlers:
            try:
                handler.process(self.context)
            except Exception, e:
                self.context.logException(handler,e)
                if handler.isAbortOnError():
                    success = False
                    break
        return success
    # end _runProcess()

    def _runCancel(self, handlers):
        for handler in handlers:
            handler.cancel()
    # end _runCancel()

    def getTotalWorkUnits(self):
        return self.totalWorkUnits
    # end getTotalWorkUnits()

    def runCancel(self):
        self._runCancel(self.preprocessHandlers)
        self._runCancel(self.postprocessHandlers)
    # end runCancel()

    def runPrepare(self):
        u"""runPreprocess() -> void
        Prepares the document for publishing. E.g. add Powered By etc.
        """ #$NON-NLS-1$
        if self.prepared:
            return False
        self.prepared = True
        if not self._runPrepare(self.preprocessHandlers):
            return False
        if not self._runPrepare(self.postprocessHandlers):
            return False
        self.totalWorkUnits = 0
        self.totalWorkUnits = self.totalWorkUnits + self._calculateWorkUnits(self.preprocessHandlers)
        self.totalWorkUnits = self.totalWorkUnits + self._calculateWorkUnits(self.postprocessHandlers)
        return True
    # end runPrepare()

    def runPreprocess(self):
        u"""runPreprocess() -> void
        Prepares the document for publishing. E.g. upload images etc.
        """ #$NON-NLS-1$
        if self.preprocessed:
            return True
        self.preprocessed = True
        return self._runProcess(self.preprocessHandlers)
    # end runPreprocess()

    def runPostprocess(self):
        u"""runPostprocess() -> void
        Run ping, track back etc.
        """ #$NON-NLS-1$
        if self.postprocessed:
            return True
        self.postprocessed = True
        return self._runProcess(self.postprocessHandlers)
    # end runPostprocess()

    def getDocumentForPublishing(self):
        u"""getDocumentForPublishing() -> ZXhtmlDocument()
        Returns the final formatted document for publishing.""" #$NON-NLS-1$
        self.runPreprocess()
        return self.xhtmlDocument
    # end getDocumentForPublishing()

# end ZBlogDocumentPublishProcessor
