from zoundry.base.util.text.unicodeutil import convertToUnicode
from zoundry.base.util.text.textutil import getNoneString
from zoundry.base.util.text.textutil import getSafeString
from zoundry.blogpub.xmlrpc.zpatch.xmlrpclib import Server
from zoundry.blogpub.xmlrpc.zpatch.xmlrpclib import Fault

#===================================================
# Module for pinging weblog ping sites.
#===================================================

#---------------------------------------------------
# Ping Response
#---------------------------------------------------
class ZWeblogPingResponse:
    u"""Contains response message from a weblog ping.""" #$NON-NLS-1$

    def __init__(self, success, message):
        self.success = success
        self.message = message
    # end __init()

    def isSuccessful(self):
        u"""isSuccessful()  -> bool
        Returns true if ping was successful.
        """ #$NON-NLS-1$
        return self.success
    # end isSuccessful()

    def getMessage(self):
        u"""getMessage()  -> string
        Returns ping message
        """ #$NON-NLS-1$
        return self.message
    # end getMessage()

#---------------------------------------------------
# Ping Server Proxy
#---------------------------------------------------
class ZWeblogPingServer:

    def __init__(self):
        pass
    # end __init__()

    def ping(self, pingServerUrl, weblogName, weblogUrl):
        u"""ping(string, string, string) -> ZWeblogPingResponse
        Pings given url with weblog name and page url and returns a ZWeblogPingResponse.
        """ #$NON-NLS-1$
        return self._internalPing(False, pingServerUrl, weblogName, weblogUrl, None, None)
    # end ping()

    def extendedPing(self, pingServerUrl, weblogName, weblogUrl, checkUrl = None, rssUrl = None):
        u"""ping(string, string, string, string, string) -> ZWeblogPingResponse
        Pings using ExtendPing method to given url with weblog name and page url and returns a ZWeblogPingResponse.
        """ #$NON-NLS-1$
        return self._internalPing(True, pingServerUrl, weblogName, weblogUrl, checkUrl, rssUrl)
    # end extendedPing()

    def _internalPing(self, extendedPing, pingServerUrl, weblogName, weblogUrl, checkUrl = None, rssUrl = None):
        pingServerUrl = getNoneString(pingServerUrl)
        weblogName = getNoneString(weblogName)
        weblogUrl = getNoneString(weblogUrl)
        checkUrl = getSafeString(checkUrl).strip()
        rssUrl = getSafeString(rssUrl).strip()

        if pingServerUrl is None:
            return ZWeblogPingResponse(False, u"Weblog ping URL is required.") #$NON-NLS-1$

        if weblogName is None:
            return ZWeblogPingResponse(False, u"Weblog name or post title is required.") #$NON-NLS-1$

        if weblogUrl is None:
            return ZWeblogPingResponse(False, u"Weblog URL or post permanent link is required.") #$NON-NLS-1$

        if extendedPing and (checkUrl == u"" or rssUrl == u""): #$NON-NLS-1$ #$NON-NLS-2$
            return ZWeblogPingResponse(False, u"URL to RSS feed or Check URL parameter is required for ExtendedPings.") #$NON-NLS-1$

        success = False
        message = u"" #$NON-NLS-1$
        try:
            remoteServer = Server(pingServerUrl)
            result = None
            if extendedPing:
                result = remoteServer.weblogUpdate.extendedPing(weblogName, weblogUrl, checkUrl, rssUrl)
            else:
                result = remoteServer.weblogUpdates.ping(weblogName, weblogUrl)
            if result is not None and result.has_key(u"flerror"): #$NON-NLS-1$
                success = not result[u"flerror"] #$NON-NLS-1$
            if result is not None and result.has_key(u"message"): #$NON-NLS-1$
                message = result[u"message"] #$NON-NLS-1$
            elif not result or not result.has_key(u"message"): #$NON-NLS-1$
                message = u"Weblog ping response message not available after pinging %s" % pingServerUrl #$NON-NLS-1$
        except Fault, fault:
            fcode = u"" #$NON-NLS-1$
            if fault.faultCode:
                fcode = unicode(fault.faultCode)
            fstr = u"" #$NON-NLS-1$
            if fault.faultString:
                fstr = convertToUnicode(fault.faultString)
            success = False
            message = u"Weblog ping faulted when pinging %s (code: %s, reason: %s)" % (pingServerUrl, fcode, fstr) #$NON-NLS-1$
        except Exception, ex:
            success = False
            fstr = convertToUnicode(ex)
            message = u"Weblog ping error when pinging %s (exception: %s)" % (pingServerUrl, fstr) #$NON-NLS-1$

        return ZWeblogPingResponse(success, message)
    # end _internalPing()
