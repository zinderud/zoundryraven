from zoundry.base.net.http import getAbsoluteUrl
from zoundry.base.net.http import ZSimpleHTTPRequest
from zoundry.base.net.http import joinUrl
from zoundry.base.net.http import splitUrl
from zoundry.base.util.text.unicodeutil import convertToUnicode
from zoundry.blogapp.services.pubsystems.sitenames import DefaultSites
import re


#---------------------------------------------------------------------
# ZRsdBlogApi contains a single entry found in RSD document.
#---------------------------------------------------------------------
class ZRsdBlogApi:

    def __init__(self, name, apiLink, preferred = False, blogId = u""):  #$NON-NLS-1$
        self.name = name
        self.apiLink = apiLink
        self.preferred = preferred
        self.blogId = blogId

    def getName(self):
        return self.name

    def getApiLink(self):
        return self.apiLink

    def isPreferred(self):
        return self.preferred

    def getBlogId(self):
        return self.blogId

    def __str__(self):
        return u"RSDApi[name=%s, pref=%s, url=%s]" % (self.name,self.preferred,self.apiLink) #$NON-NLS-1$  #$NON-NLS-2$  #$NON-NLS-3$


#---------------------------------------------------------------------
# ZRsdBlogService defines one or more RSD entries defined in a site.
#---------------------------------------------------------------------
class ZRsdBlogService:
    u"""Encapsulates the RSD information.
    See http://media-cyber.law.harvard.edu/blogs/gems/tech/rsd.html for more information.
    """  #$NON-NLS-1$
    # list of APIs defined in RSD
    ATOM        = u"Atom"  #$NON-NLS-1$
    BLOGGER     = u"Blogger"  #$NON-NLS-1$
    METAWEBLOG  = u"MetaWeblog"  #$NON-NLS-1$
    MOVABLETYPE = u"MovableType"  #$NON-NLS-1$
    LIVEJOURNAL = u"LiveJournal"  #$NON-NLS-1$
    CONVERSANT  = u"Conversant"  #$NON-NLS-1$
    MANILA      = u"Manila"  #$NON-NLS-1$
    METAWIKI    = u"MetaWiki"  #$NON-NLS-1$
    ANTVILLE    = u"Antville"  #$NON-NLS-1$
    # list of APIs supported by Zoundry
    SUPPORTED_API = [ATOM,BLOGGER,METAWEBLOG,MOVABLETYPE,LIVEJOURNAL]

    def __init__(self, engineName = u"", engineLink = u"", homePageLink = u""):  #$NON-NLS-1$  #$NON-NLS-2$  #$NON-NLS-3$
        self.engineName = engineName
        self.engineLink = engineLink
        self.homePageLink = homePageLink
        self.apiList = []

    def __str__(self):
        return u"RSDService[name=%s, link=%s, url=%s]" % (self.engineName,self.engineLink,self.homePageLink) #$NON-NLS-1$  #$NON-NLS-2$  #$NON-NLS-3$

    def getEngineName(self):
        return self.engineName

    def getEngineLink(self):
        return self.engineLink

    def getHomePageLink(self):
        return self.homePageLink

    def getApiList(self):
        return self.apiList

    def hasDefault(self):
        api = self.getDefaultApi()
        return api != None

    def getDefaultApi(self):
        rVal = None
        if self.getApiList():
            for api in self.getApiList():
                if api.isPreferred():
                    rVal = api
                    break
        return rVal

    def addApi(self, api):
        self.getApiList().append(api)

    def getApiByName(self, apiName):
        for api in self.getApiList():
            if api.getName().lower() == apiName.lower():
                return api
        return None

    def getApiUrlByName(self, apiName):
        api = self.getApiByName(apiName)
        if api:
            return api.getApiLink()
        return None

    def isSupported(self, apiName):
        rVal = False
        if apiName:
            apiName = apiName.strip().lower()
            for n in ZRsdBlogService.SUPPORTED_API:
                if n.strip().lower() == apiName:
                    rVal = True
                    break
        return rVal

#---------------------------------------------------------------------
# Class which defines the preferred api based on the discovery
#---------------------------------------------------------------------
class ZDiscoveryInfo:

    def __init__(self):
        # title of blog page
        self.title = None
        # blog home page url
        self.url = None
        # site def id
        self.siteId = None
        # api url
        self.apiUrl = None
        # fav icon url if available
        self.favIconUrl = None
        # engine (CMS) name
        self.engineName = None
        # username, if available
        self.username = None

    def hasInfo(self):
        return self.siteDefId != None

    def __str__(self):
        return u"ZDiscoveryInfo[siteId=%s; engine=%s; user=%s; apiUrl=%s]" % (self.siteId, self.engineName,self.username, self.apiUrl) #$NON-NLS-1$

#---------------------------------------------------------------------
# Contains information about a <link type="" href="" /> tag
#---------------------------------------------------------------------
class ZLinkTag:
    def __init__(self, rel, href, linkType, title):
        self.rel = rel
        self.href = href
        self.linkType = linkType
        self.title = title

    def __str__(self):
        return u"Link[rel=%s, href=%s, type=%s, title=%s]" % (self.rel, self.href, self.linkType, self.title)#$NON-NLS-1$

#---------------------------------------------------------------------
# Contains information about a <meta name="" content="" /> tag
#---------------------------------------------------------------------
class ZMetaTag:
    def __init__(self, name, content):
        self.name = name
        self.content = content

    def __str__(self):
        return u"Meta[name=%s, data=%s]" % (self.name, self.content) #$NON-NLS-1$


EMPTY_STRING = u"" #$NON-NLS-1$
HTML_TITLE_PATTERN = r'<title[^<>]*?>(.*?)</title[^<>]*?>' #$NON-NLS-1$
HTML_TITLE_RE = re.compile(HTML_TITLE_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
LINK_TAG_PATTERN = u"(<link[^<>]*?>)" #$NON-NLS-1$
LINK_TAG_RE = re.compile(LINK_TAG_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE)
META_TAG_PATTERN = u"(<meta[^<>]*?>)" #$NON-NLS-1$
META_TAG_RE = re.compile(META_TAG_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE)
BASE_TAG_PATTERN = u"(<base[^<>]*?>)" #$NON-NLS-1$
BASE_TAG_RE = re.compile(BASE_TAG_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE)
HREF_PATTERN = r'.*href\s*=\s*\"(.*?)\"' #$NON-NLS-1$
HREF_RE = re.compile(HREF_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
REL_PATTERN = r'.*rel\s*=\s*\"(.*?)\"' #$NON-NLS-1$
REL_RE = re.compile(REL_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
TYPE_PATTERN = r'.*type\s*=\s*\"(.*?)\"' #$NON-NLS-1$
TYPE_RE = re.compile(TYPE_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
TITLE_PATTERN = r'.*title\s*=\s*\"(.*?)\"' #$NON-NLS-1$
TITLE_RE = re.compile(TITLE_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
NAME_PATTERN = r'.*name\s*=\s*\"(.*?)\"' #$NON-NLS-1$
NAME_RE = re.compile(NAME_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
CONTENT_PATTERN = r'.*content\s*=\s*\"(.*?)\"' #$NON-NLS-1$
CONTENT_RE = re.compile(CONTENT_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
HTTPEQUIV_PATTERN = r'.*http-equiv\s*=\s*\"(.*?)\"' #$NON-NLS-1$
HTTPEQUIV_RE = re.compile(HTTPEQUIV_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)

RSD_PATTERN = r'<rsd[^<>]*?>(.*?)</rsd[^<>]*?>' #$NON-NLS-1$
RSD_RE = re.compile(RSD_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
RSD_ENGINE_NAME_PATTERN = r'<engineName[^<>]*?>(.*?)</engineName[^<>]*?>' #$NON-NLS-1$
RSD_ENGINE_NAME_RE = re.compile(RSD_ENGINE_NAME_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
RSD_ENGINE_LINK_PATTERN = r'<engineLink[^<>]*?>(.*?)</engineLink[^<>]*?>' #$NON-NLS-1$
RSD_ENGINE_LINK_RE = re.compile(RSD_ENGINE_LINK_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
RSD_HOMEPAGE_PATTERN = r'<homePageLink[^<>]*?>(.*?)</homePageLink[^<>]*?>' #$NON-NLS-1$
RSD_HOMEPAGE_RE = re.compile(RSD_HOMEPAGE_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
RSD_API_PATTERN = r'(<api\s[^<>]*?>)' #$NON-NLS-1$
RSD_API_RE = re.compile(RSD_API_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
RSD_API_NAME_PATTERN = r'.*name\s*=\s*\"(.*?)\"' #$NON-NLS-1$
RSD_API_NAME_RE = re.compile(RSD_API_NAME_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
RSD_API_PREF_PATTERN = r'.*preferred\s*=\s*\"(.*?)\"' #$NON-NLS-1$
RSD_API_PREF_RE = re.compile(RSD_API_PREF_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
RSD_API_LINK_PATTERN = r'.*apiLink\s*=\s*\"(.*?)\"' #$NON-NLS-1$
RSD_API_LINK_RE = re.compile(RSD_API_LINK_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
RSD_API_BID_PATTERN = r'.*blogId\s*=\s*\"(.*?)\"' #$NON-NLS-1$
RSD_API_BID_RE = re.compile(RSD_API_BID_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)

MSN_URL_PATTERN = r"(http://spaces.msn.com/members/)([\w_-]+)(/.*)*" #$NON-NLS-1$
MSN_URL_RE = re.compile(MSN_URL_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
MSN_URL_PATTERN2 = r"(http://spaces.msn.com/)([\w_-]+)(/.*)*" #$NON-NLS-1$
MSN_URL_RE2 = re.compile(MSN_URL_PATTERN2, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
MSN_URL_PATTERN3 = r"(http://)(.*?)(\.spaces\.msn\.com)(/.*)*" #$NON-NLS-1$
MSN_URL_RE3 = re.compile(MSN_URL_PATTERN3, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
SPACES_LIVE_URL_PATTERN = r"(http://)(.*?)(\.spaces\.live\.com)(/.*)*" #$NON-NLS-1$
SPACES_LIVE_URL_RE = re.compile(SPACES_LIVE_URL_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)

CS_URL_PATTERN = r"(.*/blogs/)(.*)" #$NON-NLS-1$
CS_URL_RE = re.compile(CS_URL_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)

LJ_URL_PATTERN = r"(http://www.livejournal.com/users/)(\w+)(/.*)*" #$NON-NLS-1$
LJ_URL_RE = re.compile(LJ_URL_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
LJ_URL_PATTERN2 = r"(http://)([\w_-]+)(\.livejournal.com.*)" #$NON-NLS-1$
LJ_URL_RE2 = re.compile(LJ_URL_PATTERN2, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)

WP_URL_PATTERN = r"(http://)([\w_-]+)(\.wordpress.com.*)" #$NON-NLS-1$
WP_URL_RE = re.compile(WP_URL_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)

SQUARESPACE_URL_PATTERN = r"(http://)([\w_-]+)(\.squarespace.com.*)" #$NON-NLS-1$
SQUARESPACE_URL_RE = re.compile(SQUARESPACE_URL_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)


DASBLOG_NAME_PATTERN = r"""(\s+newtelligence\s+dasBlog\s+\d+\.\d+)""" #$NON-NLS-1$
DASBLOG_NAME_RE = re.compile(DASBLOG_NAME_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)

DASBLOG_STYLE_PATTERN = r"""(\s+href\s*=\s*"http:\/\/.*)(\/themes\/.*\/\w+\.css")(\s*\/?>)""" #$NON-NLS-1$
DASBLOG_STYLE_RE = re.compile(DASBLOG_STYLE_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)

XOOPS_STYLE_PATTERN = r"""(\s*"http:\/\/.*)(\/xoops\.css")""" #$NON-NLS-1$
XOOPS_STYLE_RE = re.compile(XOOPS_STYLE_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)

TEXTPATTERN_STYLE_PATTERN = r"""(\s*"http:\/\/.*)(\/textpattern\/css\.php.*")""" #$NON-NLS-1$
TEXTPATTERN_STYLE_RE = re.compile(TEXTPATTERN_STYLE_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)

LIFETYPE_POWEREDBY_PATTERN = r"""Power[ed]?\s+by\s+<a\s+href\s*=\s*"http:\/\/www\.lifetype\.net""" #$NON-NLS-1$
LIFETYPE_POWEREDBY_RE = re.compile(LIFETYPE_POWEREDBY_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)

NUCLEUS_POWEREDBY_PATTERN = r"""powered\s+by\s+Nucleus""" #$NON-NLS-1$
NUCLEUS_POWEREDBY_RE = re.compile(NUCLEUS_POWEREDBY_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)


class ZBlogDiscovery:

    def __init__(self):
        self._initialize(None)

    def _debug(self, s): #@UnusedVariable
        pass
        #s = u"ZBlogDiscovery>> %s " % s #$NON-NLS-1$
        #print s.encode(u"utf8") #$NON-NLS-1$  #$NON-NLS-2$

    def _initialize(self, url):
        self.rsdFetched = False
        self.rsdService = None
        self.linkList = []
        self.metaList = []
        self.content = EMPTY_STRING
        self.title = EMPTY_STRING
        self.baseHref = EMPTY_STRING  # base url of site based on <base> html tag
        self.defaultHost = EMPTY_STRING # default host of blog url

        if url:
            (scheme, host, port, path, fname, query, newUrl) = splitUrl(url) #@UnusedVariable
            self.defaultHost = host
            # append trailing / if there is no filename or query string
            if (not fname or fname == u"") and (not query or query == u""): #$NON-NLS-2$ #$NON-NLS-1$
                url = url.rstrip(u"/") + u"/" #$NON-NLS-2$ #$NON-NLS-1$
        self.url = url


    def discover(self, url, enableRsd = False):
        self._initialize(url)
        if not self.url:
            self._debug(u"discover url is empty or None")#$NON-NLS-1$
            return False
        self._debug(u"Blog discover url=%s" % self.url) #$NON-NLS-1$
        # retrieve html content.
        content = self._fetchContent(self.url)
        if not content:
            self._debug(u"Blog content is empty")#$NON-NLS-1$
            return False
        self.content = content
        self.baseHref = self._extractBaseTags(content)
        self._debug(u"Blog discover baseHref=%s" % self.baseHref) #$NON-NLS-1$
        self.title = self._extractTitle(content)
        self._debug(u"Blog discover title=%s" % self.title) #$NON-NLS-1$
        self.linkList = self._extractZLinkTags(content)
        self.metaList = self._extractZMetaTags(content)
        self._debug(u"Blog discover favicon=%s" % self.getFavIconUrl()) #$NON-NLS-1$
        self._debug(u"Blog discover RSDEnabled=%s, RSD=%s" % (enableRsd, self.getRsdUrl())) #$NON-NLS-1$
        if enableRsd:
            self.getRsdService()
        return True

    def fetchRsdService(self, rsdUrl):
        rsdService = None
        self._debug(u"RSD discover downloading content from %s" % rsdUrl) #$NON-NLS-1$
        if rsdUrl:
            rsdContent = self._fetchContent(rsdUrl)
            if rsdContent:
                rsdService = self._extractRsd(rsdContent)
            else:
                self._debug(u"RSD discover content is empty or None")#$NON-NLS-1$
        if not rsdService:
            self._debug(u"RSD not discovered")#$NON-NLS-1$
        return rsdService

    def getApiInfo(self):
        apiInfo = ZDiscoveryInfo()
        if not self.getUrl():
            return apiInfo
        apiInfo.url = self.getUrl()
        apiInfo.title = self.getTitle()
        apiInfo.favIconUrl = self.getFavIconUrl()

        # hard coded test for blogger (test 1 of 2)
        if self.getRsdUrl() and self.getRsdUrl().lower().find(u".blogger.com/rsd") != -1: #$NON-NLS-1$ #$NON-NLS-2$
            apiInfo.siteId = DefaultSites.BLOGGER
            apiInfo.engineName = u"Blogger" #$NON-NLS-1$
            return apiInfo

        # check api pref based on blog home page url
        if self.getUrl().lower().find(u".msn.com/") != -1 or self.getUrl().lower().find(u"spaces.live.com/") != -1: #$NON-NLS-1$ #$NON-NLS-2$
            # msn spaces
            apiInfo.siteId = DefaultSites.MSNSPACES
            apiInfo.engineName = u"MSN Spaces" #$NON-NLS-1$
            # test format http://<membername>.spaces.msn.com/
            partsList = MSN_URL_RE3.findall(self.getUrl())
            if not partsList or len(partsList) == 0:
                partsList = SPACES_LIVE_URL_RE.findall(self.getUrl())
            if partsList and len(partsList) > 0:
                partsTuple = partsList[0]
                if partsTuple and len(partsTuple) > 2:
                    apiInfo.username = partsTuple[1] # username

            else:
                # test format http://spaces.msn.com/members/USERNAME/
                partsList = MSN_URL_RE.findall(self.getUrl())
                if partsList and len(partsList) > 0:
                    partsTuple = partsList[0]
                    # expect tuple = ('http://spaces.msn.com/members/', 'USERNAME', 'extrapath')
                    if partsTuple and len(partsTuple) == 3:
                        apiInfo.username = partsTuple[1] # username
                else:
                    # test format http://spaces.msn.com/USERNAME/  (no members)
                    partsList = MSN_URL_RE2.findall(self.getUrl())
                    if partsList and len(partsList) > 0:
                        partsTuple = partsList[0]
                        # expect tuple = ('http://spaces.msn.com/', 'USERNAME', 'extrapath')
                        if partsTuple and len(partsTuple) == 3:
                            apiInfo.username = partsTuple[1] # username
            return apiInfo
        if self.getUrl().lower().find(u".blogharbor.com") != -1: #$NON-NLS-1$
            # blog harbor
            apiInfo.siteId = DefaultSites.BLOGHARBOR
            apiInfo.engineName = u"Blogware" #$NON-NLS-1$
            return apiInfo
        if self.getUrl().lower().find(u"livejournal.com") != -1: #$NON-NLS-1$
            # live journal
            apiInfo.siteId = DefaultSites.LJ
            apiInfo.engineName = u"LiveJournal" #$NON-NLS-1$
            partsList = LJ_URL_RE.findall(self.getUrl())
            if partsList and len(partsList)== 1 and partsList[0] and len(partsList[0]) == 3 and partsList[0][1]:
                # eg: url = http://www.livejournal.com/users/sandun
                # eg: partsList = [(u'http://www.livejournal.com/users/', u'sandun', u'/')]
                # grab username
                apiInfo.username = partsList[0][1]
            else:
                partsList = LJ_URL_RE2.findall(self.getUrl())
                if partsList and len(partsList)== 1 and partsList[0] and len(partsList[0]) == 3 and partsList[0][1]:
                    # eg: url = http://zoundry.livejournal.com
                    # eg:  partsList = [(u'http://', u'zoundry', u'.livejournal.com/index')]
                    # grab username
                    apiInfo.username = partsList[0][1]
        # get rsd
        rsd = self.getRsdService()
        genList = self.getMetaListByName(u"generator")#$NON-NLS-1$
        genList.extend( self.getMetaListByName(u"powered-by") ) #$NON-NLS-1$)
        genList.extend( self.getMetaListByName(u"poweredby") ) #$NON-NLS-1$)

        # check based on RSD (and content generator)
        if rsd:
            mtUrl = rsd.getApiUrlByName(ZRsdBlogService.MOVABLETYPE)
            mwUrl = rsd.getApiUrlByName(ZRsdBlogService.METAWEBLOG)
            atomUrl = rsd.getApiUrlByName(ZRsdBlogService.ATOM)
            apiInfo.engineName = rsd.getEngineName()
            (siteId, apiUrl) = self._getPreferredApi(rsd)
            eLink = rsd.getEngineLink().lower() # engine link
            if eLink.find(u"typepad.com") != -1 and mtUrl: #$NON-NLS-1$
                siteId = DefaultSites.TYPEPAD_XMLRPC
                apiUrl = mtUrl            
            elif eLink.find(u"typepad.com") != -1 and atomUrl: #$NON-NLS-1$
                siteId = DefaultSites.TYPEPAD_ATOM
                apiUrl = atomUrl
            elif eLink.find(u"blogger.com") != -1: #$NON-NLS-1$
                siteId = DefaultSites.BLOGGER
                apiUrl = None
            elif (eLink.find(u"wordpress.org") != -1  or eLink.find(u"wordpress.com") != -1) and (mtUrl or mwUrl): #$NON-NLS-1$ #$NON-NLS-2$
                siteId = DefaultSites.WORDPRESS
                if mtUrl:
                    apiUrl = mtUrl
                else:
                    apiUrl = mwUrl
                # check for WP 2.3 based on generator
                for gen in genList:
                    if gen:
                        gen = gen.strip()
                    if not gen or not gen.lower().startswith(u"wordpress 2.") or len(gen) < 13: #$NON-NLS-1$
                        continue
                    # e.g. gen = wordpress 2.2 (WordPress 2.5)
                    minorVer = gen.lower()[12:13]
                    if minorVer in [u"2", u"3", u"4", u"5", u"6", u"7", u"8", u"9"]: #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$ #$NON-NLS-4$ #$NON-NLS-5$ #$NON-NLS-6$ #$NON-NLS-7$ #$NON-NLS-8$
                        siteId = DefaultSites.WORDPRESS22
                        break
                # check for wordpress.com specifics
                partsList = WP_URL_RE.findall(self.getUrl())
                if partsList and len(partsList)== 1 and partsList[0] and len(partsList[0]) == 3 and partsList[0][1]:
                    # eg: url = http://sandun.wordpress.com
                    # eg: partsList = [(u'http://', u'sandun', u'.wordpress.com/index')]
                    # grab username
                    apiInfo.username = partsList[0][1]
                    siteId = DefaultSites.WPDOTCOM

            elif (eLink.find(u"movabletype.org") != -1 or eLink.find(u"sixapart.com") != -1)and (mtUrl or mwUrl): #$NON-NLS-1$ #$NON-NLS-2$
                siteId = DefaultSites.SA_MOVABLE_TYPE
                # most six apart mw servers list mw url - but we should check for mt url as well.
                if mtUrl:
                    apiUrl = mtUrl
                else:
                    apiUrl = mwUrl
            elif eLink.find(u"blogware.com") != -1 and mtUrl: #$NON-NLS-1$
                siteId = DefaultSites.BLOGWARE
                apiUrl = mtUrl
            elif eLink.find(u"nucleuscms.org") != -1 and (mtUrl or mwUrl): #$NON-NLS-1$
                siteId = DefaultSites.NUCLEUS
                if mtUrl:
                    apiUrl = mtUrl
                else:
                    apiUrl = mwUrl
            elif eLink.find(u"drupal.org") != -1 and (mtUrl or mwUrl): #$NON-NLS-1$
                siteId = DefaultSites.DRUPAL
                if mtUrl:
                    apiUrl = mtUrl
                else:
                    apiUrl = mwUrl
            elif (eLink.find(u"lifetype.net") != -1 or self._findInList(genList,u"plog")) and mwUrl: #$NON-NLS-1$ #$NON-NLS-2$
                siteId = DefaultSites.LIFETYPE
                apiInfo.engineName = u"LifeType" #$NON-NLS-1$
                apiUrl = mwUrl
            elif (eLink.find(u"communityserver") != -1 or self._findInList(genList,u"CommunityServer")) and mwUrl: #$NON-NLS-1$ #$NON-NLS-2$
                siteId = DefaultSites.COMMUNITY_SERVER
                apiInfo.engineName = u"CommunityServer" #$NON-NLS-1$
                apiUrl = mwUrl
            elif eLink.find(u"rollerweblogger") != -1 and mwUrl: #$NON-NLS-1$
                siteId = DefaultSites.ROLLER
                apiInfo.engineName = u"Roller" #$NON-NLS-1$
                apiUrl = mwUrl
            elif eLink.find(u"dasblog") != -1 and mwUrl: #$NON-NLS-1$
                siteId = DefaultSites.DASBLOG
                apiInfo.engineName = u"dasBlog" #$NON-NLS-1$
                apiUrl = mwUrl
            elif eLink.find(u"squarespace.com") != -1 and mwUrl: #$NON-NLS-1$
                siteId = DefaultSites.SQUARESPACE
                apiInfo.engineName = u"SquareSpace" #$NON-NLS-1$
                apiUrl = mwUrl
                partsList = SQUARESPACE_URL_RE.findall(self.getUrl())
                if partsList and len(partsList)== 1 and partsList[0] and len(partsList[0]) == 3 and partsList[0][1]:
                    apiInfo.username = partsList[0][1]
            elif eLink.find(u"xaraya.com") != -1 and mwUrl: #$NON-NLS-1$
                siteId = DefaultSites.XARAYA
                apiUrl = mwUrl
            elif eLink.find(u"xoops") != -1 and mwUrl: #$NON-NLS-1$
                siteId = DefaultSites.XOOPS
                apiUrl = mwUrl

            apiInfo.siteId = siteId
            apiInfo.apiUrl = apiUrl
        elif genList:
            # rsd not found - figure it out based on meta generator.
            apiUrl = None
            siteId = None
            engineName = None
            if self._findInList(genList,u"plog") or self._findInList(genList,u"lifetype"): #$NON-NLS-1$ #$NON-NLS-2$
                siteId = DefaultSites.LIFETYPE
                engineName = u"LifeType" #$NON-NLS-1$
                apiUrl = self._guessBlogApiUrl(self.getUrl(), u"/xmlrpc.php")#$NON-NLS-1$
            elif self._findInList(genList,u"wordpress"):#$NON-NLS-1$
                if self._findInList(genList,u"wordpress.com"):#$NON-NLS-1$
                    siteId = DefaultSites.WPDOTCOM
                else:
                    siteId = DefaultSites.WORDPRESS
                engineName = u"WordPress" #$NON-NLS-1$
                apiUrl = self._guessBlogApiUrl(self.getUrl(), u"/xmlrpc.php")#$NON-NLS-1$
            elif self._findInList(genList,u"nucleus"):#$NON-NLS-1$
                siteId = DefaultSites.NUCLEUS
                engineName = u"Nucleus" #$NON-NLS-1$
                apiUrl = self._guessBlogApiUrl(self.getUrl(), u"/nucleus/xmlrpc/server.php")#$NON-NLS-1$
            elif self._findInList(genList,u"movable type"):#$NON-NLS-1$
                siteId = DefaultSites.SA_MOVABLE_TYPE
                engineName = u"Movable Type" #$NON-NLS-1$
                apiUrl = self._guessBlogApiUrl(self.getUrl(), u"/mt/mt-xmlrpc.cgi")#$NON-NLS-1$
            elif self._findInList(genList,u"blogger"):#$NON-NLS-1$
                siteId = DefaultSites.BLOGGER
                engineName = u"Blogger" #$NON-NLS-1$
            elif self._findInList(genList,u"textpattern"):#$NON-NLS-1$
                siteId = DefaultSites.TEXTPATTERN
                engineName = u"TextPattern" #$NON-NLS-1$
                apiUrl = self._guessBlogApiUrl(self.getUrl(), u"/textpattern/xmlrpcs.php")#$NON-NLS-1$
            elif self._findInList(genList,u"xoops"):#$NON-NLS-1$
                siteId = DefaultSites.XOOPS
                engineName = u"Xoops" #$NON-NLS-1$
                apiUrl = self._guessBlogApiUrl(self.getUrl(), u"/xmlrpc.php")#$NON-NLS-1$
            elif self._findInList(genList,u"xaraya"):#$NON-NLS-1$
                engineName = u"Xaraya" #$NON-NLS-1$
                siteId = DefaultSites.XARAYA
                apiUrl = self._guessBlogApiUrl(self.getUrl(), u"/ws.php?type=xmlrpc")#$NON-NLS-1$
            elif self._findInList(genList,u"serendipity"):#$NON-NLS-1$
                engineName = u"Serendipity" #$NON-NLS-1$  FIXME (PJ) Serendipity - add site def for Serendipity
                siteId = DefaultSites.CUSTOM_MT
                apiUrl = self._guessBlogApiUrl(self.getUrl(), u"/serendipity_xmlrpc.php")#$NON-NLS-1$
            elif self._findInList(genList,u"drupal"):#$NON-NLS-1$
                engineName = u"Drupal" #$NON-NLS-1$
                siteId = DefaultSites.DRUPAL
                apiUrl = self._guessBlogApiUrl(self.getUrl(), u"/xmlrpc.php")#$NON-NLS-1$$
            elif self._findInList(genList,u"CommunityServer"):#$NON-NLS-1$
                engineName = u"CommunityServer" #$NON-NLS-1$
                siteId = DefaultSites.COMMUNITY_SERVER
                s = CS_URL_RE.findall(self.getUrl())
                # eg: s=> [('http://www.gibixonline.com/blogs/', 'default.aspx')]
                if s and len(s) == 1 and len(s[0]) == 2 and s[0][0] is not None:
                    apiUrl = s[0][0].rstrip(u"/") + u"/metablog.ashx" #$NON-NLS-1$ #$NON-NLS-2$
                else:
                    apiUrl = self._guessBlogApiUrl(self.getUrl(), u"/blogs/metablog.ashx", False)#$NON-NLS-1$
            elif self._findInList(genList,u"dasblog"):#$NON-NLS-1$
                engineName = u"dasBlog" #$NON-NLS-1$
                siteId = DefaultSites.DASBLOG
                if self.baseHref and len(self.baseHref) > 0 and self.baseHref.startswith(u"http"): #$NON-NLS-1$
                    apiUrl = self.baseHref.rstrip(u"/") + u"/blogger.aspx" #$NON-NLS-1$ #$NON-NLS-2$
                else:
                    apiUrl = self._guessBlogApiUrl(self.getUrl(), u"/blogger.aspx")#$NON-NLS-1$$

            apiInfo.siteId = siteId
            apiInfo.apiUrl = apiUrl
            apiInfo.engineName = engineName

        if not apiInfo.siteId and self.getUrl().lower().find(u"typepad.com") != -1: #$NON-NLS-1$
            # typepad
            apiInfo.siteId = DefaultSites.TYPEPAD_ATOM
            apiInfo.engineName = u"Typepad" #$NON-NLS-1$
        elif not apiInfo.siteId and self.baseHref and len(self.baseHref) > 0 and self.baseHref.startswith(u"http"): #$NON-NLS-1$
            if DASBLOG_NAME_RE.findall(self.content) or DASBLOG_STYLE_RE.findall(self.content):
                apiInfo.siteId = DefaultSites.DASBLOG
                apiInfo.apiUrl = self.baseHref.rstrip(u"/") + u"/blogger.aspx" #$NON-NLS-1$ #$NON-NLS-2$
                apiInfo.engineName = u"dasBlog" #$NON-NLS-1$
        if not apiInfo.siteId and TEXTPATTERN_STYLE_RE.findall(self.content):
            apiInfo.siteId = DefaultSites.TEXTPATTERN
            apiInfo.engineName = DefaultSites.TEXTPATTERN
            apiInfo.apiUrl = self._guessBlogApiUrl(self.getUrl(), u"/rpc/")#$NON-NLS-1$$

        if not apiInfo.siteId and self.content and LIFETYPE_POWEREDBY_RE.findall(self.content):
            apiInfo.siteId = DefaultSites.LIFETYPE
            apiInfo.engineName = u"LifeType" #$NON-NLS-1$
            apiInfo.apiUrl = self._guessBlogApiUrl(self.getUrl(), u"/xmlrpc.php")#$NON-NLS-1$

        if not apiInfo.siteId and self.content and NUCLEUS_POWEREDBY_RE.findall(self.content):
            apiInfo.siteId = DefaultSites.NUCLEUS
            apiInfo.engineName = u"Nucleus" #$NON-NLS-1$
            apiInfo.apiUrl= self._guessBlogApiUrl(self.getUrl(), u"/nucleus/xmlrpc/server.php")#$NON-NLS-1$

#        if not apiInfo.siteId:
#            f = XOOPS_STYLE_RE.findall(self.content)
#            print "===XOOPS", f
        return apiInfo

    def _guessBlogApiUrl(self, blogUrl, apiPath, bUseExistingPath=True):
        rVal = None
        if blogUrl and apiPath:
            (scheme, host, port, path, fname, query, newUrl) = splitUrl(blogUrl) #@UnusedVariable
            if bUseExistingPath and path and apiPath:
                path = path.rstrip(u"/") + u"/" + apiPath.lstrip(u"/") #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$
            elif apiPath:
                path = apiPath
            rVal = joinUrl(scheme, host, port, path)
        return rVal

    def _findInList(self, genList, pattern):
        if genList and pattern:
            pattern = pattern.lower()
            for gen in genList:
                if gen and gen.strip().lower().find(pattern) != -1:
                    return True
        return False

    def _getPreferredApi(self, rsd):
        # returns tuple (siteId, apiUrl) if found or (None, None) otherwise
        prefApi = rsd.getDefaultApi()
        # check to see if the default/preferred api is supported
        if not prefApi or not rsd.isSupported(prefApi.getName()):
            prefApi = None
            for api in rsd.getApiList():
                if rsd.isSupported(api.getName()):
                    prefApi = api
                    break
        if not prefApi:
            return (None,None)
        siteId = None
        url = prefApi.getApiLink()
        s = prefApi.getName().strip().lower()
        if s == ZRsdBlogService.ATOM.lower():
            siteId = DefaultSites.CUSTOM_ATOM03
        elif s == ZRsdBlogService.BLOGGER.lower():
            siteId = DefaultSites.CUSTOM_BLOGGERV1
        elif s == ZRsdBlogService.METAWEBLOG.lower():
            siteId = DefaultSites.CUSTOM_METAWEBLOG
        elif s == ZRsdBlogService.MOVABLETYPE.lower():
            siteId = DefaultSites.CUSTOM_MT
        elif s == ZRsdBlogService.LIVEJOURNAL.lower():
            siteId = DefaultSites.CUSTOM_LJ
        return (siteId, url)

    def getTitle(self):
        return self.title

    def getUrl(self):
        return self.url

    def getRsdUrl(self):
        u"""Returns RSD Url if available, else None""" #$NON-NLS-1$
        rVal = None
        for link in self.getLinksList():
            if link.linkType == u"application/rsd+xml":#$NON-NLS-1$
                rVal = self._getAbsoluteUrl(link.href)
                break
        return rVal

    def getFavIconUrl(self):
        u"""Returns FavIcon Url if available, else None""" #$NON-NLS-1$
        rVal = None
        for link in self.getLinksList():
            if link.rel == u"shortcut icon" or link.rel == u"icon" or link.linkType == u"image/x-icon": #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$
                rVal = self._getAbsoluteUrl(link.href)
                break
        return rVal

    def guessFavIconUrl(self):
        if self.getUrl():
            return self._guessBlogApiUrl(self.getUrl(), u"/favicon.ico", False) #$NON-NLS-1$
        else:
            return None

    def getRsdService(self):
        if not self.rsdFetched:
            self.rsdService = self.fetchRsdService(self.getRsdUrl())
            self.rsdFetched = True
        return self.rsdService

    def getLinksList(self):
        return self.linkList

    def getMetaList(self):
        return self.metaList

    def getMetaListByName(self, name):
        u"""returns list of meta attributes give name"""#$NON-NLS-1$
        rVal = []
        for meta in self.getMetaList():
            if meta.name.lower() == name.lower():
                rVal.append(meta.content)
        return rVal

    def _getAbsoluteUrl(self, url):
        # returns absolute url.
        if not url:
            return url
        refUrl = None
        if self.baseHref and len(self.baseHref) > 0 :
            refUrl = self.baseHref
        else:
            refUrl = self.defaultHost
        if not refUrl.lower().startswith(u"http"): #$NON-NLS-1$
            refUrl = u"http://" + refUrl #$NON-NLS-1$
        rval = getAbsoluteUrl(url, refUrl)
        return rval

    def _extractZLinkTags(self, content):
        retList = []
        linkList = LINK_TAG_RE.findall(content)
        for link in linkList:
            linkRel = self._extractAttribute(REL_RE, link).lower()
            linkType = self._extractAttribute(TYPE_RE, link).lower()
            linkTitle = self._extractAttribute(TITLE_RE, link)
            linkHref = self._extractAttribute(HREF_RE, link)
            if len(linkRel) == 0 or len(linkHref) == 0:
                continue
            ld = ZLinkTag(linkRel, linkHref, linkType, linkTitle)
            retList.append(ld)
        return retList

    def _extractZMetaTags(self, content):
        retList = []
        metaList = META_TAG_RE.findall(content)
        for meta in metaList:
            name = self._extractAttribute(NAME_RE, meta)
            if len(name) == 0:
                name = self._extractAttribute(HTTPEQUIV_RE, meta)
            if len(name) == 0:
                continue
            data = self._extractAttribute(CONTENT_RE, meta)
            mt = ZMetaTag(name.lower(), data)
            retList.append(mt)
        return retList

    def _extractBaseTags(self, content):
        baseList = BASE_TAG_RE.findall(content)
        baseHref = EMPTY_STRING
        for base in baseList:
            baseHref = self._extractAttribute(HREF_RE, base)
            break
        if len(baseHref) > 0:
            # if the base href ends with a filename, then restruct with out the filename
            (scheme, host, port, path, fname, query, newUrl) = splitUrl(baseHref) #@UnusedVariable
            if fname and len(fname) > 0:
                idx = baseHref.rfind(u"/")#$NON-NLS-1$
                if idx != -1:
                    baseHref = baseHref[0:idx]
        return baseHref

    def _extractTitle(self, content):
        u"""Extracts html title""" #$NON-NLS-1$
        title = self._extractTagContents(HTML_TITLE_RE, content, EMPTY_STRING)
        if not title:
            title = EMPTY_STRING
        return title

    def _extractRsd(self, content):
        rsdFrag = self._extractTagContents(RSD_RE, content)
        if not rsdFrag:
            return None
        engineName = self._extractTagContents(RSD_ENGINE_NAME_RE,rsdFrag,EMPTY_STRING)
        engineLink = self._extractTagContents(RSD_ENGINE_LINK_RE,rsdFrag,EMPTY_STRING)
        homePageLink = self._extractTagContents(RSD_HOMEPAGE_RE,rsdFrag,EMPTY_STRING)
        if len(engineName) == 0 and len(engineLink) == 0:
            return None
        rsdService = ZRsdBlogService(engineName, engineLink, homePageLink)
        # find API links
        findList = RSD_API_RE.findall(content)
        for apiFrag in findList:
            apiName = self._extractAttribute(RSD_API_NAME_RE, apiFrag)
            s = self._extractAttribute(RSD_API_PREF_RE, apiFrag)
            apiPref = False
            if s and (s.lower() == u"true" or s.lower() == u"yes"): #$NON-NLS-1$ #$NON-NLS-2$
                apiPref = True
            apiLink = self._extractAttribute(RSD_API_LINK_RE, apiFrag)
            apiBid = self._extractAttribute(RSD_API_BID_RE, apiFrag)
            rsdApi = ZRsdBlogApi(apiName, apiLink, apiPref, apiBid)
            rsdService.addApi(rsdApi)
        return rsdService

    def _extractTagContents(self, regExpr, content, defaultValue = None):
        rVal = None
        if regExpr and content:
            findList = regExpr.findall(content)
            if findList and len(findList) > 0 and findList[0]:
                rVal = findList[0].strip()
        if not rVal and defaultValue:
            rVal = defaultValue
        return rVal

    def _extractAttribute(self, regExpr, content):
        u"""Matches and extracts the string from group 1.""" #$NON-NLS-1$
        findList = regExpr.findall(content)
        retVal = EMPTY_STRING
        if findList and len(findList) > 0 and findList[0]:
            retVal = findList[0]
        retVal = retVal.replace(u"&apos;", u"'") #$NON-NLS-1$ #$NON-NLS-2$
        retVal = retVal.replace(u"&amp;", u"&") #$NON-NLS-1$ #$NON-NLS-2$
        retVal = retVal.replace(u"&quot;", u'"') #$NON-NLS-1$ #$NON-NLS-2$
        return retVal.strip()

    def _fetchContent(self, url):
        u"""Retrieves the text content from the url.""" #$NON-NLS-1$
        request = ZSimpleHTTPRequest(url)
        content = None
        if request.send():
            content = request.getResponse()
            content = convertToUnicode(content)
        return content


