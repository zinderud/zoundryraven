from zoundry.base.net.http import ZSimpleTextHTTPRequest
from zoundry.base.util.text.textutil import getNoneString
from zoundry.base.util.text.textutil import getSafeString
from zoundry.base.util.text.unicodeutil import convertToUtf8
from zoundry.base.util.types.attrmodel import ZModelWithAttributes
from zoundry.base.xhtml.xhtmlutil import extractTitle
import re

#===================================================
# Module for sending trackbacks
#===================================================
RDF_NS = u"http://www.w3.org/1999/02/22-rdf-syntax-ns#" #$NON-NLS-1$
DC_ELEMENTS_NS = u"http://purl.org/dc/elements/1.1/" #$NON-NLS-1$

# Begin RDF regular expressions
RDF_PATTERN = r'<rdf:RDF[^<>]*?>(.*?)</rdf:RDF[^<>]*?>' #$NON-NLS-1$
RDF_RE = re.compile(RDF_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
RDF_ABOUT_PATTERN = r'.*rdf:about\s*=\s*\"(.*?)\"' #$NON-NLS-1$
RDF_ABOUT_RE = re.compile(RDF_ABOUT_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
DC_ID_PATTERN = r'.*dc:identifier\s*=\s*\"(.*?)\"' #$NON-NLS-1$
DC_ID_RE = re.compile(DC_ID_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
DC_TITLE_PATTERN = r'.*dc:title\s*=\s*\"(.*?)\"' #$NON-NLS-1$
DC_TITLE_RE = re.compile(DC_TITLE_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
TB_PING_PATTERN = r'.*trackback:ping\s*=\s*\"(.*?)\"' #$NON-NLS-1$
TB_PING_RE = re.compile(TB_PING_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
DC_DESC_PATTERN = r'.*dc:description\s*=\s*\"(.*?)\"' #$NON-NLS-1$
DC_DESC_RE = re.compile(DC_DESC_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
DC_DATE_PATTERN = r'.*dc:date\s*=\s*\"(.*?)\"' #$NON-NLS-1$
DC_DATE_RE = re.compile(DC_DATE_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
DC_CREATOR_PATTERN = r'.*dc:creator\s*=\s*\"(.*?)\"' #$NON-NLS-1$
DC_CREATOR_RE = re.compile(DC_CREATOR_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
# End RDF regular expressions

# RSS Item regular expressions
ITEM_PATTERN = r'<item[^<>]*?>(.*?)</item[^<>]*?>' #$NON-NLS-1$
ITEM_RE = re.compile(ITEM_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)

ITEM_LINK_PATTERN = r'<link[^<>]*?>(.*?)</link[^<>]*?>' #$NON-NLS-1$
ITEM_LINK_RE = re.compile(ITEM_LINK_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
ITEM_DESC_PATTERN = r'<description[^<>]*?>(.*?)</description[^<>]*?>' #$NON-NLS-1$
ITEM_DESC_RE = re.compile(ITEM_DESC_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
# RSS 1.0
ITEM_TB_1_PATTERN = r'<trackback:ping.*rdf:resource\s*=\s*\"(.*?)\"' #$NON-NLS-1$
ITEM_TB_1_RE = re.compile(ITEM_TB_1_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
# RSS 2.0
ITEM_TB_2_PATTERN = r'<trackback:ping[^<>]*?>(.*?)</trackback:ping[^<>]*?>' #$NON-NLS-1$
ITEM_TB_2_RE = re.compile(ITEM_TB_2_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
# End RSS Item regular expressions

# Trackback ping response
TB_RESP_ERROR_PATTERN = r'<error[^<>]*?>(.*?)</error[^<>]*?>' #$NON-NLS-1$
TB_RESP_ERROR_RE = re.compile(TB_RESP_ERROR_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
TB_RESP_MSG_PATTERN = r'<message[^<>]*?>(.*?)</message[^<>]*?>' #$NON-NLS-1$
TB_RESP_MSG_RE = re.compile(TB_RESP_MSG_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
TB_RESP_TITLE_PATTERN = r'<title[^<>]*?>(.*?)</title[^<>]*?>' #$NON-NLS-1$
TB_RESP_TITLE_RE = re.compile(TB_RESP_TITLE_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)

# ping back
PB_LINK_TAG_PATTERN = u'(<link.*rel\s*=\s*"pingback".*>)' #$NON-NLS-1$
PB_LINK_TAG_RE = re.compile(PB_LINK_TAG_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE)
PB_HREF_PATTERN = u'(.*href\s*=\s*"?)([^"^\s]*)(["\s].*>)(.*)' #$NON-NLS-1$
PB_HREF_RE = re.compile(PB_HREF_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE)

#----------------------------------------------
# Blog post entry trackback meta data
#--------------------------------------------------------------
class ZTrackbackEntry(ZModelWithAttributes):

    def __init__(self, pingUrl, entryUrl, title, summary):
        ZModelWithAttributes.__init__(self)
        self.setAttribute(u"ping", pingUrl) #$NON-NLS-1$
        self.setAttribute(u"url", entryUrl) #$NON-NLS-1$
        self.setAttribute(u"title", title) #$NON-NLS-1$
        self.setAttribute(u"summary", summary) #$NON-NLS-1$
    # end __init__

    def getPingUrl(self):
        u"""
        getPingUrl() -> string
        Returns trackback ping URL.
        """ #$NON-NLS-1$
        return self.getAttribute(u"ping") #$NON-NLS-1$
    # end getPingUrl()

    def getEntryUrl(self):
        u"""
        getEntryUrl() -> string
        Returns blog post entry URL.
        """ #$NON-NLS-1$
        return self.getAttribute(u"url") #$NON-NLS-1$
    # end getEntryUrl()

    def getTitle(self):
        u"""
        getTitle() -> string
        Returns title of post.
        """ #$NON-NLS-1$
        return getSafeString(self.getAttribute(u"title")) #$NON-NLS-1$
    # end  getTitle()

    def getSummary(self):
        u"""
        getSummary() -> string
        Returns the optional summary or description.
        """ #$NON-NLS-1$
        return getSafeString(self.getAttribute(u"summary")) #$NON-NLS-1$
    # end  getSummary()

# end  ZTrackbackEntry

#----------------------------------------------
# Auto discover result
#--------------------------------------------------------------
class ZTrackbackDiscoverResult:

    def __init__(self, title, entries):
        self. title = title
        self.entries = entries
    # end __init__()

    def getTitle(self):
        u"""
        getTitle() -> string
        Returns html page title.
        """ #$NON-NLS-1$
        return self.title
    # end getTitle()

    def getTrackbackEntries(self):
        u"""
        getTrackbackEntries() -> list
        Returns list of ZTrackbackEntry items.
        """ #$NON-NLS-1$
        return self.entries
    # end getTrackbackEntries

# end ZTrackbackDiscoverResult


#---------------------------------------------
# Class to auto discover trackback information
#----------------------------------------------
class ZTrackbackDiscovery:
    u"""ZTrackbackDiscovery discovers trackback information given a site URL.
    The discovery is based on either RDF or RSS content in a page.""" #$NON-NLS-1$

    def discover(self, url):
        u"""discover(string) -> list of IZTrackbackEntry
        Retrieves the contents of the given url and discovers (extracts) the trackback
        information from either the RDF of RSS Item constructs. This method returns a list
        of IZTrackbackEntry objects for each trackback discovered.""" #$NON-NLS-1$

        trackbackEntryList = []
        htmlContent = self._downloadHtmlContent(url)
        title = u"" #$NON-NLS-1$
        if htmlContent:
            title = extractTitle(htmlContent)
            trackbackEntryList = self._parseContent(url, title, htmlContent)
        rval = ZTrackbackDiscoverResult(title, trackbackEntryList)
        return rval
    # end discover()

    def _parseContent(self, url, title, htmlContent):
        trackbackEntryList = []
        trackbackEntryList.extend( self._extractRdf(url, title, htmlContent) )
        trackbackEntryList.extend( self._extractRssItems(url, title, htmlContent) )
        trackbackEntryList.extend( self._extractMsnContent(url, title, htmlContent) )
        return trackbackEntryList
    # end _parseContent()

    def _extractRdf(self, url, title, htmlContent): #@UnusedVariable
        rdfTbList = []
        rdfEleList = RDF_RE.findall(htmlContent)
        for rdf in rdfEleList:
            #rdfAbout = self._extract(RDF_ABOUT_RE,rdf)
            rdfId = self._extract(DC_ID_RE,rdf)
            rdfTitle = self._extract(DC_TITLE_RE,rdf)
            pingUrl = self._extract(TB_PING_RE,rdf)
            rdfDesc = self._extract(DC_DESC_RE,rdf)
            rdfDate = self._extract(DC_DATE_RE,rdf)
            rdfCreator = self._extract(DC_CREATOR_RE,rdf)
            if rdfDesc:
                temp = rdfDesc.lower()
                if temp.startswith(u"<![cdata[") and temp.endswith(u"]]"): #$NON-NLS-1$ #$NON-NLS-2$
                    rdfDesc = rdfDesc[9:len(rdfDesc)-2]
            if pingUrl:
                tb = ZTrackbackEntry(pingUrl, entryUrl=rdfId, title=rdfTitle, summary=rdfDesc)
                tb.setAttribute(u"date",rdfDate, DC_ELEMENTS_NS) #$NON-NLS-1$
                tb.setAttribute(u"creator",rdfCreator, DC_ELEMENTS_NS) #$NON-NLS-1$
                rdfTbList.append(tb)
        return rdfTbList
    # 3ne _extractRdf()

    def _extractRssItems(self, url, title, htmlContent): #@UnusedVariable
        u"""Extracts the RSS Item data from the given content string and returns a list of Trackback objects.""" #$NON-NLS-1$
        ## NOTE: Needs more testing.
        rssTbList = []
        itemEleList = ITEM_RE.findall(htmlContent)
        for item in itemEleList:
            link = self._extract(ITEM_LINK_RE,item)
            desc = self._extract(ITEM_DESC_RE,item)
            pingUrl = self._extract(ITEM_TB_1_RE,item)
            if getNoneString(pingUrl) is None:
                pingUrl = self._extract(ITEM_TB_2_RE,item)
            if getNoneString(pingUrl) is not None:
                tb = ZTrackbackEntry(pingUrl, entryUrl=link, title=desc, summary=u"") #$NON-NLS-1$
                rssTbList.append(tb)
        return rssTbList
    # end __extractRssItems()

    def _extractMsnContent(self, url, title, htmlContent):
        tbList = []
        if url and ( url.lower().find(u".msn.com") != -1 or url.lower().find(u".live.com") != -1) and htmlContent: #$NON-NLS-1$ #$NON-NLS-2$
            msnPattern = url.rstrip(u"/").rstrip(u".entry") + u".trak" #$NON-NLS-3$ #$NON-NLS-2$ #$NON-NLS-1$
            msnRe = re.compile(msnPattern, re.IGNORECASE | re.MULTILINE | re.UNICODE)
            findList = msnRe.findall(htmlContent)
            if findList and findList[0]:
                tb = ZTrackbackEntry(findList[0], entryUrl=url, title=title, summary=u"") #$NON-NLS-1$
                tbList.append(tb)
        return tbList
    # end _extractMsnContent()

    def _extract(self, regExpr, content):
        u"""Matches and extracts the string from group 1.""" #$NON-NLS-1$
        findList = regExpr.findall(content)
        retVal = u"" #$NON-NLS-1$
        if findList:
            retVal = findList[0]
        retVal = retVal.replace(u"&apos;", u"'") #$NON-NLS-1$ #$NON-NLS-2$
        retVal = retVal.replace(u"&amp;", u"&") #$NON-NLS-1$ #$NON-NLS-2$
        retVal = retVal.replace(u"&quot;", u'"') #$NON-NLS-1$ #$NON-NLS-2$
        return retVal
    # end _extract()

    def _downloadHtmlContent(self, url):
        html = None
        request = ZSimpleTextHTTPRequest(url)
        if request.send():
            html = request.getResponse()
        return html
    # end _downloadHtmlContent()
# end   ZTrackbackDiscovery


#---------------------------------------------
# Ping response wrapper
#----------------------------------------------
class ZTrackbackPingResponse:

    def __init__(self, success, message):
        self.success = success
        self.message = message
    # end __inti__()

    def isSuccessful(self):
        return self.success
    # end isSuccessful

    def getMessage(self):
        return self.message
    # end getMessage()

# end ZTrackbackPingResponse

#---------------------------------------------
# Class to send a trackback ping
#----------------------------------------------
class ZTrackbackPinger:
    u"""Pings a trackback ping URL.""" #$NON-NLS-1$

    def ping(self, pingUrl, id, url, title, blogName, excerpt):
        u"""ping(string, string, string, string, string, string) -> ZTrackbackPingResponse
        Pings the track back and returns ZTrackbackPingResponse""" #$NON-NLS-1$
        if getNoneString(pingUrl) is None:
            return ZTrackbackPingResponse(False, u"Trackback ping url is required.") #$NON-NLS-1$

        if getNoneString(id) is None:
            return ZTrackbackPingResponse(False, u"Trackback Originating Resource ID is required.") #$NON-NLS-1$

        if getNoneString(url) is None:
            return ZTrackbackPingResponse(False, u"Trackback post url is required.") #$NON-NLS-1$

        title = convertToUtf8( getSafeString(title) )
        blogName = convertToUtf8( getSafeString(blogName))
        excerpt = convertToUtf8( getSafeString(excerpt))

        postData = {
            u'id': id, #$NON-NLS-1$
            u'url': url, #$NON-NLS-1$
            u'title': title, #$NON-NLS-1$
            u'blog_name': blogName, #$NON-NLS-1$
            u'excerpt': excerpt #$NON-NLS-1$
        }

        htmlResult = self._sendHttpPostData(pingUrl, postData)
        resp = self._parseResponse(htmlResult)
        return resp
    # end ping

    def _sendHttpPostData(self, pingUrl, postDataMap):
        try:
            request = ZSimpleTextHTTPRequest(pingUrl)
            if request.send(postDataMap):
                return request.getResponse()
        except:
            pass
        return None
    # end _sendHttpPostData()


    def _parseResponse(self, htmlResult):
        u"""Parses the trackback response data and returns ZTrackbackPingResponse.""" #$NON-NLS-1$
        if not htmlResult:
            return ZTrackbackPingResponse(False, u"Trackback HTTP POST empty response error.") #$NON-NLS-1$
        bOk = False
        msg = u"OK" #$NON-NLS-1$
        fList = TB_RESP_ERROR_RE.findall(htmlResult)
        if fList and len(fList) > 0 and fList[0] and fList[0].strip() == u"0": #$NON-NLS-1$
            bOk = True
        elif fList and len(fList) > 0 and fList[0] and fList[0].strip() == u"1": #$NON-NLS-1$
            bOk = False
        else:
            msg = u"Trackback <error/> element not found in response" #$NON-NLS-1$
            fList = TB_RESP_TITLE_RE.findall(htmlResult)
            if fList and len(fList) > 0 and fList[0]:
                msg = u"Trackback HTTP response error: %s" % fList[0].strip() #$NON-NLS-1$
            return ZTrackbackPingResponse (False, msg)

        fList = TB_RESP_MSG_RE.findall(htmlResult)
        if fList and len(fList) > 0 and fList[0]:
            msg = fList[0].strip()
        elif not bOk:
            msg = u"Trackback response message not available" #$NON-NLS-1$

        return ZTrackbackPingResponse(bOk, msg)
    # end _parseResponse()

# end ZTrackbackPinger()

# FIXME PJ Support following trackback formats:
# http://www.lifewiki.net/attachments/view/101/2.2
#
#   Example HTML TrackBack Link
#
#     <link rel="trackback"
#           type="application/x-www-form-urlencoded"
#           href="http://example.org/trackback-url" />

#     <link rel="trackback-rdf" type="application/rdf+xml" href="foo-tb.rdf" />
#
#   Example Atom TrackBack Link
#
#     <entry xmlns="http://www.w3.org/2005/Atom">
#       ...
#       <link rel="trackback"
#             type="application/x-www-form-urlencoded"
#             href="http://example.org/trackback-url" />
#       ...
#     </entry>
