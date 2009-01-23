# --------------------------------------------------------------------------
# Basic handlers that are run after publishing a document.
# --------------------------------------------------------------------------
from zoundry.base.util.schematypes import ZSchemaDateTime
from zoundry.base.util.text.textutil import getNoneString
from zoundry.base.util.text.textutil import getSafeString
from zoundry.blogapp.services.datastore.blogdocumentimpl import ZTrackback
from zoundry.blogapp.services.pubsystems.blog.handlers.pubprocesshandlers import ZBlogPublishHandlerBase
from zoundry.blogpub.trackback import ZTrackbackPinger
from zoundry.blogpub.weblogping import ZWeblogPingServer

#------------------------------------------------------------
# Pings weblog services.
#------------------------------------------------------------
class ZWeblogPingPublishHandler(ZBlogPublishHandlerBase):

    def __init__(self):
        ZBlogPublishHandlerBase.__init__(self, u"ZWeblogPingPublishHandler") #$NON-NLS-1$
        self.pingSites = None
    # end __init__()

    def _prepare(self):
        pubmetaData = self._getContext().getPubMetaData()
        self.pingSites = pubmetaData.getPingServices()
        workunits = 0
        if self.pingSites is not None:
            workunits = len(self.pingSites)
        self._setTotalWorkUnits( workunits )
    # end _prepare()

    def _process(self):
        if self.pingSites is None:
            return
        blog = self._getContext().getBlog()
        blogName = getNoneString( blog.getName() )
        if blogName is None:
            # get the post entry title
            blogName = self._getContext().getTitle()

        blogUrl = blog.getUrl()
        if blogUrl is None:
            # get the post entry url.
            blogUrl = self._getContext().getUrl()

        pingServer = ZWeblogPingServer()
        for weblogPingSite in self.pingSites:
            if self.isCancelled():
                return
            s = u"Pinging %s at %s" % ( weblogPingSite.getName(), weblogPingSite.getUrl() ) #$NON-NLS-1$
            self._getContext().logInfo(self, s)
            self._getContext().notifyProgress(self, s, 1, False)

            weblogPingResponse = pingServer.ping(weblogPingSite.getUrl(), blogName, blogUrl)
            if weblogPingResponse.isSuccessful():
                s = u"Pinged %s successfully: %s" % ( weblogPingSite.getName(),weblogPingResponse.getMessage() ) #$NON-NLS-1$
                self._getContext().logInfo(self, s)
                self._getContext().notifyProgress(self, s, 0, False)

            else:
                s = u"Pinging %s failed: %s" % ( weblogPingSite.getName(),weblogPingResponse.getMessage() ) #$NON-NLS-1$
                self._getContext().logError(self, s)
                self._getContext().notifyProgress(self, s, 0, False)

    # end _process()
# end ZWeblogPingPublishHandler()

#------------------------------------------------------------
# Send Trackbacks services.
#------------------------------------------------------------
class ZSendTrackbackPublishHandler(ZBlogPublishHandlerBase):

    def __init__(self):
        ZBlogPublishHandlerBase.__init__(self, u"ZSendTrackbackPublishHandler") #$NON-NLS-1$
        self.pingSites = None
    # end __init__()

    def _getPubInfo(self):
        pubInfo = None
        blogInfo = self._getContext().getBlogInfo()
        if blogInfo:
            pubInfo = blogInfo.getPublishInfo()
        return pubInfo
    # end _getPubInfo

    def _getTrackbacks(self):
        # return tuple (sendUrlList, doNotSendUrlList)
        pubmetaData = self._getContext().getPubMetaData()
        toBeSentList = pubmetaData.getTrackbacks()
        sentTrackbackList = []
        pubInfo = self._getPubInfo()
        if pubInfo:
            sentTrackbackList = pubInfo.getTrackbacks()
        sendUrlList = []
        doNotSendUrlList = []
        # create list not to be sent
        for tb in toBeSentList:
            for sentTb in sentTrackbackList:
                if tb.getUrl() == sentTb.getUrl():
                    doNotSendUrlList.append(sentTb.getUrl())
                    break
        # create list to be sent
        for tb in toBeSentList:
            if tb.getUrl() not in doNotSendUrlList:
                sendUrlList.append( tb.getUrl() )
        return (sendUrlList, doNotSendUrlList)
    # end _getTrackbacks()

    def _prepare(self):
        (sendUrlList, doNotSendUrlList) = self._getTrackbacks() #@UnusedVariable
        workunits = len(sendUrlList)
        self._setTotalWorkUnits( workunits )
    # end _prepare()

    def _validateConfiguration(self, validationReporter): #@UnusedVariable
        (sendUrlList, doNotSendUrlList) = self._getTrackbacks() #@UnusedVariable
    # end _validateConfiguration()

    def _process(self):
        (sendUrlList, doNotSendUrlList) = self._getTrackbacks() #@UnusedVariable
        for url in doNotSendUrlList:
            s = u"Will not send previously sent trackback : %s" % url #$NON-NLS-1$
            self._getContext().logInfo(self, s)
            self._getContext().notifyProgress(self, s, 0, False)

        if len(sendUrlList) == 0:
            return
        self._sendTrackbacks(sendUrlList)
        # do pubInfo.addTrackback(tb)
    # end _process

    def _sendTrackbacks(self, trackbackUrlList):
        blog = self._getContext().getBlog()
        blogName = getNoneString( blog.getName() )
        id = blog.getUrl()
        title = self._getContext().getTitle()
        if blogName is None:
            blogName = title
        # get the post entry url.
        postUrl = getNoneString( self._getContext().getUrl() )
        if not postUrl:
            pass
            #log error and return
        if not id:
            id = postUrl
        # post summary
        excerpt = self._getContext().getXhtmlDocument().getSummary(500)
        pinger = ZTrackbackPinger()
        sentCount = 0
        for pingUrl in trackbackUrlList:
            if self.isCancelled():
                return
            s = u"Sending trackback to %s" % pingUrl #$NON-NLS-1$
            self._getContext().logInfo(self, s)
            self._getContext().notifyProgress(self, s, 1, False)
            ok = False
            msg = u"" #$NON-NLS-1$
            try:
                response = pinger.ping(pingUrl, id, postUrl, title, blogName, excerpt)
                ok = response.isSuccessful()
                msg = getSafeString(response.getMessage())
            except Exception, e:
                ok = False
                msg = unicode(e)
            if ok:
                trackback = ZTrackback()
                trackback.setUrl(pingUrl) #$NON-NLS-1$
                trackback.setSentDate(ZSchemaDateTime())
                pubInfo = self._getPubInfo()
                if pubInfo:
                    pubInfo.addTrackback(trackback)
                sentCount = sentCount + 1
                s = u"Trackback sent successfully: %s" % msg #$NON-NLS-1$
                self._getContext().logInfo(self, s)
                self._getContext().notifyProgress(self, s, 0, False)
            else:
                s = u"Trackback failed: %s" % msg #$NON-NLS-1$
                self._getContext().logError(self, s)
                self._getContext().notifyProgress(self, s, 0, False)
        # end for
        #  Save sent trackback to document
        if sentCount > 0:
            self._getContext().saveMetaData()

    # end _sendTrackbacks()

# end ZSendTrackbackPublishHandler
