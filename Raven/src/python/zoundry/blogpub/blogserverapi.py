from zoundry.blogpub.namespaces import IZBlogPubTagwordNamespaces
from zoundry.base.exceptions import ZException
from zoundry.base.net import http
from zoundry.base.util.text.texttransform import ZXhtmlRemoveNewLinesTransformer
from zoundry.base.util.text.textutil import getNoneString
from zoundry.base.util.text.textutil import getSafeString
from zoundry.base.util.types.attrmodel import ZModelWithAttributes
from zoundry.base.util.types.capabilities import ZCapabilities
from zoundry.base.util.types.parameters import ZParameters
from zoundry.base.util.zdatetime import getCurrentUtcDateTime

#===================================================
# Base class definitions used by the blog pub layer
#===================================================

#===================================================
# <parameter> names
#===================================================
class IZBlogApiParamConstants:

    FACTORY_CLASSNAME        = u"zoundry.raven.param.blogpub.blogserver.factory.classname" #$NON-NLS-1$
    SERVER_CLASSNAME         = u"zoundry.raven.param.blogpub.blogserver.classname" #$NON-NLS-1$
    API_ENDPOINT_URL         = u"zoundry.raven.param.blogpub.blogserver.api.url" #$NON-NLS-1$
    API_USERNAME             = u"zoundry.raven.param.blogpub.blogserver.api.username" #$NON-NLS-1$
    API_PASSWORD             = u"zoundry.raven.param.blogpub.blogserver.api.password" #$NON-NLS-1$
    API_AUTH_SCHEME          = u"zoundry.raven.param.blogpub.blogserver.api.authscheme" #$NON-NLS-1$
    API_CLIENT_VERSION       = u"zoundry.raven.param.blogpub.blogserver.api.client.version" #$NON-NLS-1$
    DATEFORMAT_IN            = u"zoundry.raven.param.blogpub.blogserver.dateformat.in" #$NON-NLS-1$
    DATEFORMAT_OUT           = u"zoundry.raven.param.blogpub.blogserver.dateformat.out" #$NON-NLS-1$
    SUMMARY_FIELDNAME        = u"zoundry.raven.param.blogpub.blogserver.summary.fieldname" #$NON-NLS-1$
    EXTENDED_ENTRY_MARKER    = u"zoundry.raven.param.blogpub.blogserver.extendedentry.marker" #$NON-NLS-1$
    MAX_POSTS                = u"zoundry.raven.param.blogpub.blogserver.maxposts" #$NON-NLS-1$
    REMOVE_NEWLINES          = u"zoundry.raven.param.blogpub.blogserver.removenewlines" #$NON-NLS-1$


#===================================================
# <capability> constants
#===================================================
class IZBlogApiCapabilityConstants:

    MEDIA_UPLOAD             = u"zoundry.raven.capability.blogpub.blogserver.mediaupload" #$NON-NLS-1$
    DRAFT_POSTS              = u"zoundry.raven.capability.blogpub.blogserver.draft" #$NON-NLS-1$
    EXTENDED_ENTRY           = u"zoundry.raven.capability.blogpub.blogserver.extendedentry" #$NON-NLS-1$
    POST_SUMMARY             = u"zoundry.raven.capability.blogpub.blogserver.summary" #$NON-NLS-1$
    CATEGORIES               = u"zoundry.raven.capability.blogpub.blogserver.categories" #$NON-NLS-1$
    MULTISELECT_CATEGORIES   = u"zoundry.raven.capability.blogpub.blogserver.categories.multiselect" #$NON-NLS-1$
#    EDITABLE_CATEGORIES      = u"zoundry.raven.capability.blogpub.blogserver.categories.editable" #$NON-NLS-1$
    USERGENERATED_CATEGORIES = u"zoundry.raven.capability.blogpub.blogserver.categories.usergenerated" #$NON-NLS-1$
    TEMPLATE                 = u"zoundry.raven.capability.blogpub.blogserver.template" #$NON-NLS-1$
    PAGES                    = u"zoundry.raven.capability.blogpub.blogserver.pages" #$NON-NLS-1$
    HIERARCHICAL_PAGES       = u"zoundry.raven.capability.blogpub.blogserver.hierarchical.pages" #$NON-NLS-1$
    TAGGING                  = u"zoundry.raven.capability.blogpub.blogserver.tagging" #$NON-NLS-1$    

#===================================================
# Server factory
#===================================================
class IZBlogServerFactory:

    def createServer(self, properties): #@UnusedVariable
        u"""createServer(dict) ->  ZBlogServer
        Creates and returns a blogserver. See IZBlogApiParamConstants for property names."""#$NON-NLS-1$
        return None

#===================================================
# Interface for logging features
#===================================================
class IZBlogServerLogger:
    def debug(self, message):
        u"Logs a debug message to the log." #$NON-NLS-1$
    # end debug()

    def warning(self, message):
        u"Logs a warning to the log." #$NON-NLS-1$
    # end warning()

    def error(self, message):
        u"Logs an error to the log." #$NON-NLS-1$
    # end error()

    def logData(self, filename, data):
        u"Logs data (such as http xml response) to file." #$NON-NLS-1$
    # end logData


#===================================================
# Base Blog class
#===================================================
class ZServerBase(ZModelWithAttributes):

    def __init__(self, id = None, systemId = None):
        # server side attributes such as atom feed etc. are maintained in the base class.
        ZModelWithAttributes.__init__(self)
        self._setId(id)

        # system id is an optional id that can be used to track
        # blogs, posts, categories across multiple accounts.
        # (equivalent to a "guid" with a single raven repository)
        # This id is normally assigned by the application/api user
        self.systemId = systemId
        self.debugMode = False
        self.logger = None

    def setLogger(self, logger):
        self.logger = logger

    def getLogger(self):
        return self.logger

    def getId(self):
        u"Gets the ID." #$NON-NLS-1$
        return self.getAttribute(u"id") #$NON-NLS-1$

    def _setId(self, id):
        self.setAttribute(u"id", getNoneString(id) ) #$NON-NLS-1$

    def setSystemId(self, systemId):
        self.systemId = systemId

    def getSystemId(self):
        return self.systemId

    def isDebug(self):
        return self.debugMode

    def setDebug(self, bDebug):
        self.debugMode = bDebug

    def _debug(self, message):
        if self.getLogger():
            self.getLogger().debug(message)

    def _error(self, message):
        if self.getLogger():
            self.getLogger().error(message)

    def _warning(self, message):
        if self.getLogger():
            self.getLogger().warning(message)

    def _log(self, message):
        self._debug(message)

#===================================================
# Base classes for object with id and name
#===================================================

class ZNamedServerBase(ZServerBase):

    def __init__(self, id, name):
        ZServerBase.__init__(self, id)
        name = getSafeString(name)
        self._setName(name)

    def getName(self):
        u"Gets the  name." #$NON-NLS-1$
        return self.getAttribute(u"name") #$NON-NLS-1$
    # end getName()

    def _setName(self, name):
        self.setAttribute(u"name", name) #$NON-NLS-1$

#===================================================
# Blog class
#===================================================
class ZServerBlogInfo(ZNamedServerBase):

    def __init__(self, id, name, url):
        name = getNoneString(name)
        id = getSafeString(id)
        if not name: #$NON-NLS-1$
            name = u"untitled blog" #$NON-NLS-1$
            if id != u"": #$NON-NLS-1$
                name = name + u" (" + id + u")" #$NON-NLS-2$ #$NON-NLS-1$
        ZNamedServerBase.__init__(self, id, name)
        self._setUrl(url)
    # end __init__()

    def getUrl(self):
        u"""getUrl() -> string
        Gets the blog url.""" #$NON-NLS-1$
        return self.url

    def _setUrl(self, url):
        self.url = url

    def __str__(self):
        return u"ZServerBlogInfo[id=%s; name=%s; url=%s]" % (self.getId(), self.getName(), self.getUrl())  #$NON-NLS-1$
# end ZServerBlogInfo


#===================================================
# Blog Username or author
#===================================================
class ZServerBlogUser(ZNamedServerBase):

    def __init__(self, id, name, email = u""):  #$NON-NLS-1$
        ZNamedServerBase.__init__(self, id, name)
        self.email = email

    def getEmail(self):
        return self.email

    def __str__(self):
        return u"ZServerBlogUser[id=%s; name=%s]" % (self.getId(), self.getName())  #$NON-NLS-1$

# end  ZServerBlogUser


#===================================================
# Blog post entry
#===================================================
class ZServerBlogEntry(ZServerBase):

    def __init__(self, id = None):
        ZServerBase.__init__(self, id)
        self.url = None
        self.title = None
        self.rawContent = None
        self.content = None
        self.summary = None
        self.utcDateTime = getCurrentUtcDateTime() # utc date time.
        self.draft = False
        self.categories = []
        self.tagwords = []
        self.tagspaceUrl = None
        self.author = None
        self.convertNewLines = False

    def __str__(self):
        return u"ZServerBlogEntry[id=%s; title=%s]" % (self.getId(), self.getTitle())  #$NON-NLS-1$

    def setId(self, id):
        ZServerBase._setId(self, id)

    def getUrl(self):
        return self.url

    def setUrl(self, url):
        self.url = url

    def getTitle(self):
        return self.title

    def setTitle(self, title):
        self.title = title

    def getContent(self):
        return self.content

    def setContent(self, content):
        self.content = content
        if not self.rawContent:
            self.rawContent = content

    def getRawContent(self):
        return self.rawContent

    def getSummary(self):
        return self.summary

    def setSummary(self, summary):
        self.summary = summary

    def getUtcDateTime(self):
        return self.utcDateTime

    def setUtcDateTime(self, utcdate):
        self.utcDateTime = utcdate

    def isDraft(self):
        return self.draft

    def setDraft(self, bDraft):
        self.draft = bDraft

    def getCategories(self):
        return self.categories

    def addCategory(self, category):
        self.categories.append(category)

    def getAuthor(self):
        return self.author

    def setAuthor(self, author):
        self.author = author

    def isConvertNewLines(self):
        return self.convertNewLines

    def setConvertNewLines(self, convertNewLines):
        self.convertNewLines = convertNewLines

    def getTagwords(self):
        u"""getTagwords() -> list
        Returns list of tagwords strings""" #$NON-NLS-1$
        return self.tagwords

    def setTagwords(self, tagwords):
        u"""setTagwords(list) -> void
        Sets list of tagwords strings""" #$NON-NLS-1$
        if tagwords is not None:
            self.tagwords = tagwords
        else:
            self.tagwords = []

    def getTagspaceUrl(self):
        u"""getTagspaceUrl() -> string
        Returns url for the tagspace""" #$NON-NLS-1$
        if self.tagspaceUrl:
            return self.tagspaceUrl
        else:
            return IZBlogPubTagwordNamespaces.DEFAULT_TAGWORDS_URI
    # end getTagspaceUrl()

    def setTagspaceUrl(self, tagspaceUrl):
        u"""setTagspaceUrl(string) -> void
        Sets url for the tagspace""" #$NON-NLS-1$
        self.tagspaceUrl = tagspaceUrl

# end  ZServerBlogEntry


#===================================================
# Blog category
#===================================================
class ZServerBlogCategory(ZNamedServerBase):

    def __init__(self, id, name):
        ZNamedServerBase.__init__(self, id, name)

    def __str__(self):
        return u"ZServerBlogCategory[id=%s; name=%s]" % (self.getId(), self.getName())  #$NON-NLS-1$
# end ZServerBlogCategory


#===================================================
# Blog Server
#===================================================
class ZBlogServer (ZServerBase):

    # Default version
    CLIENT_VERSION = u"Zoundry/Raven (www.zoundry.com)" #$NON-NLS-1$


    def __init__(self, apiUrl, username, password, version = None, name = None):
        ZServerBase.__init__(self)
        self.apiUrl = apiUrl
        self.username = username
        self.password = password
        if not version:
            version = ZBlogServer.CLIENT_VERSION
        self.version = version
        self.name = name
        self.debugMode = False
        self.parameters = ZParameters()
        self.capabilities = ZCapabilities()

    def initialize(self, izparameters, izcapabilities):
        self.parameters = izparameters
        self.capabilities = izcapabilities

    def _getParameters(self):
        return self.parameters

    def _getCapabilities(self):
        return self.capabilities

    def getName(self):
        return self.name

    def _setName(self, name):
        self.name = name

    def getVersion(self):
        return self.version

    def setVersion(self, version):
        self.version = version

    def getApiUrl(self):
        return self.apiUrl

    def getBaseUrl(self):
        return http.getBaseUrl(self.getApiUrl())

    def getUsername(self):
        return self.username

    def getPassword(self):
        return self.password

    def _copyEntryAttributesToMap(self, zserverBlogEntry, attrMap, attrNamespace = None):
        # Copies attrs from the blog entry to the given dict.
        for (key, value) in zserverBlogEntry.getAttributes(attrNamespace):
            if key and value:
                attrMap[key] = value

    def _formatContentForPublishing(self, serverEntry):
        # Formats contents for publishing.
        content = serverEntry.getContent()
        if content is not None and isinstance(content,basestring):
            if self._getParameters().getBoolParameter(IZBlogApiParamConstants.REMOVE_NEWLINES) ==  True:
                transformer = ZXhtmlRemoveNewLinesTransformer()
                return transformer.transform(content)

            return content
# end ZBlogServer


#===================================================
# Basic Error
#===================================================
class ZBlogServerException(ZException):
    def __init__(self, rootCause = None, stage = u"", message = u"", code = 0):  #$NON-NLS-1$  #$NON-NLS-2$
        self.rootCause = rootCause
        self.code = code
        self.stage = stage
        if not rootCause:
            self.message = message
        else:
            self.message = unicode(rootCause)
        self.type = u"Error" #$NON-NLS-1$
        self._analyze()
        ZException.__init__(self, self.message, self.rootCause)
    # end __init__()

    def _analyze(self):
        pass
    # end _analyze()

    def getType(self):
        return self.type
    # end getType()

    def getErrorCode(self):
        return self.code
    # end getErrorCode()

    def getDescription(self):
        s  = self.type + u" on " + self.stage + u".\n" #$NON-NLS-1$ #$NON-NLS-2$
        s  = s + u"code : " + unicode(self.code) + u".\n" #$NON-NLS-1$ #$NON-NLS-2$
        s  = s + u"error: " + self.message #$NON-NLS-1$
        return s
    # end getDescription()

    def __str__(self):
        return u"ZBlogServerException['%s' type:%s, code:%s msg:%s]" % (self.stage, self.type, unicode(self.code), self.message) #$NON-NLS-1$
    # end __str__()

# end ZBlogServerException

# ------------------------------------------------------------------------------
# The return result of uploading a file to a media storage.
# ------------------------------------------------------------------------------
class IZBlogMediaServerUploadResult:

    def getUrl(self):
        u"""getUrl() -> string
        Returns the URL of the uploaded file.""" #$NON-NLS-1$
    # end getUrl()

    def getEmbedFragment(self):
        u"""getFragment() -> ZElement
        Returns the 'embed' fragment of the uploaded file.  This
        will return None for most file types (images, etc), but
        it might return a valid ZElement for things like Videos.""" #$NON-NLS-1$
    # end getEmbedFragment()

    def hasEmbedFragment(self):
        u"""hasEmbedFragment() -> boolean
        Returns True if the response includes an 'embed' html fragment.""" #$NON-NLS-1$
    # end hasEmbedFragment()

    def getMetaData(self):
        u"""getMetaData() -> ZElement
        Returns any meta data associated with the upload.  This
        meta data might include information that the media storage
        provider requires to perform future operations.""" #$NON-NLS-1$
    # end getMetaData()

# end IZBlogMediaServerUploadResult

#--------------------------------------------------------
# Generic callback listener interface for media uploading.
#--------------------------------------------------------
class IZBlogServerMediaUploadListener:
    u"""Listener for media upoading.
    After onStart, the uploading process may first encode the media
    before transfering (e.g via http) to the server.""" #$NON-NLS-1$

    def onStart(self):
        u"Called when the upload session is started." #$NON-NLS-1$

    def onStartEncode(self, totalBytes):
        u"Called when the encoding is started." #$NON-NLS-1$

    def onEncodeChunk(self, bytes):
        u"Called for each chunk of data that is encoded." #$NON-NLS-1$

    def onEndEncode(self):
        u"Called when the encoding has completed." #$NON-NLS-1$

    def onStartTransfer(self, totalBytes):
        u"Called when the transfer is started." #$NON-NLS-1$

    def onTransferChunk(self, bytes):
        u"Called for each chunk of data that is encoded." #$NON-NLS-1$

    def onEndTransfer(self):
        u"Called when the transfer has completed." #$NON-NLS-1$

    def onEnd(self):
        u"Called when the upload session has finished." #$NON-NLS-1$

    def onFail(self, exception):
        u"Called when the upload session has failed." #$NON-NLS-1$

# end IZBlogServerMediaUploadListener

# ------------------------------------------------------------------------------
# Implementation of a media storage upload response.
# ------------------------------------------------------------------------------
class ZBlogMediaServerUploadResult(IZBlogMediaServerUploadResult):

    def __init__(self, url = None, embedFragment = None, metaData = None):
        self.url = url
        self.embedFragment = embedFragment
        self.metaData = metaData
    # end __init__()

    def getUrl(self):
        return self.url
    # end getUrl()

    def setUrl(self, url):
        self.url = url
    # end setUrl()

    def getEmbedFragment(self):
        return self.embedFragment
    # end getEmbedFragment()

    def setEmbedFragment(self, embedFragment):
        self.embedFragment = embedFragment
    # end setEmbedFragment()

    def hasEmbedFragment(self):
        return self.embedFragment is not None
    # end hasEmbedFragment()

    def getMetaData(self):
        return self.metaData
    # end getMetaData()

    def setMetaData(self, metaData):
        self.metaData = metaData
    # end setMetaData()

# end ZBlogMediaServerUploadResult
