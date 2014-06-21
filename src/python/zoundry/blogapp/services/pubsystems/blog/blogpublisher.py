from zoundry.base.util.text.textutil import getSafeString
from zoundry.base.exceptions import ZNotYetImplementedException
from zoundry.base.util.classloader import ZClassLoader
from zoundry.base.util.schematypes import ZSchemaDateTime
from zoundry.base.util.text.texttransform import ZXhtmlRemoveNewLinesTransformer
from zoundry.base.util.text.textutil import getNoneString
from zoundry.base.util.zdatetime import getCurrentUtcDateTime
from zoundry.base.xhtml.xhtmlio import loadXhtmlDocumentFromString
from zoundry.base.xhtml.xhtmlutil import extractBody
from zoundry.blogapp.constants import IZBlogAppNamespaces
from zoundry.blogapp.constants import IZBlogAppUserPrefsKeys
from zoundry.blogapp.services.accountstore.accountimpl import ZBlogFromAccount
from zoundry.blogapp.services.commonimpl import ZCategory
from zoundry.blogapp.services.datastore.blogdocumentimpl import ZBlogDocument
from zoundry.blogapp.services.datastore.blogdocumentimpl import ZBlogInfo
from zoundry.blogapp.services.datastore.blogdocumentimpl import ZPubMetaData
from zoundry.blogapp.services.datastore.blogdocumentimpl import ZPublishInfo
from zoundry.blogapp.services.datastore.blogdocumentimpl import ZTagwords
from zoundry.blogapp.services.datastore.documentimpl import ZXhtmlContent
from zoundry.blogapp.services.pubsystems.publisher import IZPublisher
from zoundry.blogapp.services.pubsystems.publisher import IZPublisherRequest
from zoundry.blogapp.services.pubsystems.publisher import IZPublisherResponse
from zoundry.blogapp.services.pubsystems.publisher import ZPublisherBase
from zoundry.blogapp.services.pubsystems.publisher import ZPublisherRequest
from zoundry.blogapp.services.pubsystems.publisher import ZPublisherResponse
from zoundry.blogapp.services.pubsystems.publisher import ZQualifiedPublisherId
from zoundry.blogapp.ui.util.blogutil import getCustomWPMetaDataAttribute
from zoundry.blogapp.ui.util.tagsiteutil import getWordListFromZTagwords
from zoundry.blogpub.blogserverapi import IZBlogApiParamConstants
from zoundry.blogpub.blogserverapi import IZBlogServerLogger
from zoundry.blogpub.blogserverapi import IZBlogServerMediaUploadListener
from zoundry.blogpub.blogserverapi import ZServerBlogCategory
from zoundry.blogpub.blogserverapi import ZServerBlogEntry
from zoundry.blogpub.namespaces import IZBlogPubAttrNamespaces
from zoundry.blogpub.namespaces import IZBlogPubTagwordNamespaces
#
# To ensure we get "<iframe></iframe>" instead of "<iframe/>" tags, we employ the help of "tidy HTML".
#    ChuahTC Date:2013-Sept-3
from zoundry.base.zdom import tidyutil

#
#

# -----------------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------------
class IZBlogPublisherRequest(IZPublisherRequest):

    def getBlog(self):
        u"""getBlog() -> IZBlog
        Returns blog.""" #$NON-NLS-1$
# -----------------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------------
class IZBlogEntryPublisherRequest(IZBlogPublisherRequest):

    def getEntry(self):
        u"""getEntry() -> IZDocument
        Returns entry document.""" #$NON-NLS-1$
# -----------------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------------
class IZBlogEntryPublisherResponse(IZPublisherResponse):

    def getBlog(self):
        u"""getBlog() -> IZBlog
        Returns blog.""" #$NON-NLS-1$

    def getUrl(self):
        u"""getUrl() -> string
        Returns post url.""" #$NON-NLS-1$

    def getEntry(self):
        u"""getEntry() -> IZDocument
        Returns entry document.""" #$NON-NLS-1$

# -----------------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------------
class IZBlogPublisher(IZPublisher):

# FIXME (PJ) use IZBlogEntryPublisherRequest and IZBlogEntryPublisherResponse objects
    def setAccountId(self, accountId):
        u"""setAccountId(string) -> void
        Sets the account id associated with this publisher.""" #$NON-NLS-1$

    def listBlogs(self):
        u"""listBlogs() -> list of IZBlog objects
        Returns list of blogs.""" #$NON-NLS-1$

    def listCategories(self, izblog):
        u"""listCategories(IZBlog) -> list of category objects
        Returns list of categories for given blog.""" #$NON-NLS-1$

    def listEntries(self, izblog, maxEntries):
        u"""listEntries(IZBlog, int) -> list of entry docs
        Returns list of entries for given blog.""" #$NON-NLS-1$

    def postEntry(self, zblog, zblogDocument, zxhtmlDocument):
        u"""postEntry(IZBlog, IZBlogDocument, ZXhtmlDocument) -> ZBlogInfo
        Posts a new entry.""" #$NON-NLS-1$

    def updateEntry(self, zblog, zblogDocument, zxhtmlDocument):
        u"""listEntries(IZBlog, IZBlogDocument, ZXhtmlDocument) -> ZBlogInfo
        Updates the given entry.""" #$NON-NLS-1$

    def deleteEntry(self, izblog, zblogDocument):
        u"""deleteEntry(IZBlog, IZBlogDocument) -> bool
        Deletes the given entry.""" #$NON-NLS-1$

    def uploadFile(self, izblog, srcFilename, destFilename, serverMediaUploadListener):
        u"""uploadFile(IZBlog, string, string, int,  IZBlogServerMediaUploadListener) -> string
        Uploads the given file and return the url to the uploaded file.""" #$NON-NLS-1$

# -----------------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------------
class ZBlogPublisherRequest(ZPublisherRequest, IZBlogPublisherRequest):

    def __init__(self, blog):
        ZPublisherRequest.__init__(self)
        self.blog = blog

    def getBlog(self):
        return self.blog

# -----------------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------------
class ZBlogEntryPublisherRequest(ZBlogPublisherRequest, IZBlogEntryPublisherRequest):

    def __init__(self, blog):
        ZBlogPublisherRequest.__init__(self, blog)
        self.entry = None

    def getEntry(self):
        return self.entry

# -----------------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------------
class ZBlogEntryPublisherResponse(ZPublisherResponse, IZBlogEntryPublisherResponse):

    def __init__(self, ok = False, message = None):
        ZPublisherResponse.__init__(self, ok, message)

    def getBlog(self):
        return None

    def getUrl(self):
        return None

    def getEntry(self):
        return None

# -----------------------------------------------------------------------------------
# Adapts the blogpub api logger to rave logger service
# -----------------------------------------------------------------------------------
class ZBlogServerLoggerAdapter(IZBlogServerLogger):

    def __init__(self, ravenLoggerService):
        self.loggerService = ravenLoggerService

    def debug(self, message):
        self.loggerService.debug(message)
    # end debug()

    def warning(self, message):
        self.loggerService.warning(message)
    # end warning()

    def error(self, message):
        self.loggerService.error(message)
    # end error()

    def logData(self, filename, data):
        self.loggerService.logClob(filename, data)

# -----------------------------------------------------------------------------------
# blog publisher related util
# -----------------------------------------------------------------------------------

class ZBlogPublisherUtil:

    def createRavenCategoryByName(self, zblogId, categoryName):
        category = ZCategory()
        bogQID = ZQualifiedPublisherId( zblogId)
        urn = u"%s,zoundry:blog:%s" % (bogQID.getLocalId(), bogQID.getServerId())  #$NON-NLS-1$
        qid = ZQualifiedPublisherId(localId=urn, serverId=categoryName)
        category.setId( qid.getId() )
        category.setName(categoryName)
        return category
    # end  createRavenCategoryByName

# -----------------------------------------------------------------------------------
# Base implementation of a BLOG (xml-rpc or atom) publisher
# -----------------------------------------------------------------------------------
class ZBlogPublisher(ZPublisherBase, IZBlogPublisher):

    DEFAULT_FACTORY = u"zoundry.blogpub.xmlrpc.xmlrpcapi.ZXmlRpcServerFactory" #$NON-NLS-1$

    def __init__(self):
        ZPublisherBase.__init__(self)
        self.account = None
        self.accountId = u"nil" #$NON-NLS-1$
        self.server = None
    # end __init__()

    def _getServerId(self, qualifiedId):
        # returns the serverId part given qid "{localIdNS}serverId"
        qid = ZQualifiedPublisherId(qualifiedId)
        return qid.getServerId()
    # end _getServerId()

    def _createBlogQId(self, serverBlogId):
        urn = u"urn:zoundry:acc:%s" % self.getAccountId()  #$NON-NLS-1$
        qid = ZQualifiedPublisherId(localId = urn, serverId = serverBlogId)
        return qid.getId()
    # end _createBlogQId()

    def _createEntryQId(self, zblogId, serverEntryId):
        serverBlogId = self._getServerId(zblogId)
        urn = u"urn:zoundry:acc:%s,zoundry:blog:%s" % (self.getAccountId(), serverBlogId)  #$NON-NLS-1$
        qid = ZQualifiedPublisherId(localId = urn, serverId = serverEntryId)
        return qid.getId()
    # end _createEntryQId()

    def _getServerFactoryClassname(self):
        u"""_getServerFactoryClassname() -> string
        Returns the server factory classname parameter value or the default classname if not found.""" #$NON-NLS-1$
        return self.getParameters().getParameter(IZBlogApiParamConstants.FACTORY_CLASSNAME, ZBlogPublisher.DEFAULT_FACTORY)
    # end _getServerFactoryClassname()

    def _createServerFactory(self):
        u"""_createServerFactory() -> IZBlogServerFactory
        Creates and returns a IZBlogServerFactory instance.""" #$NON-NLS-1$
        clazzName = self._getServerFactoryClassname()
        factoryClazz = ZClassLoader().loadClass(clazzName)
        return factoryClazz()
    # end _createServerFactory()

    def _getServerClassname(self):
        u"""_getServerClassname() -> string
        Returns the server impl classname parameter value or None if not found.""" #$NON-NLS-1$
        return self.getParameters().getParameter(IZBlogApiParamConstants.SERVER_CLASSNAME)
    # end _getServerClassname()

    def _getServer(self):
        if self.server is None:
            self.server = self._createServer()
        return self.server
    # end _getServer()

    def _createServer(self):
        factory = self._createServerFactory()
        paramMap = self._getParametersAsMap()
        server = factory.createServer(paramMap)
        # configure logger service
        if self._getLogger():
            blogServerLogger = ZBlogServerLoggerAdapter(self._getLogger())
            server.setLogger(blogServerLogger)
            server.setDebug( self._getLogger().isDebugLoggingEnabled() )
        # intialize server api with params and capabilities.
        server.initialize( self.getParameters(), self.getCapabilities() )
        return server
    # _createServer()

    def setAccount(self, account):
        self.account = account
        if self.account:
            # set acc id
            self.setAccountId( self.account.getId() )
    # end setAccount()

    def getAccount(self):
        return self.account
    # end getAccount()

    def setAccountId(self, accountId):
        # FIXME (PJ) delete this method if not used outside of this class
        self.accountId = accountId
    # end setAccountId()

    def getAccountId(self):
        return self.accountId
    # end getAccountId()

    def _createRavenBlog(self, zserverBlogInfo):
        # qid is a unique id with in the raven repository
        qid = self._createBlogQId( zserverBlogInfo.getId() )
        zserverBlogInfo.setSystemId(qid)

        izblog = ZBlogFromAccount()
        izblog.setId( qid )
        izblog.setAccount( self.getAccount() )
        izblog.setName( zserverBlogInfo.getName() )
        izblog.setUrl( zserverBlogInfo.getUrl() )
        # copy over server side attribute to raven izblog model
        self._copyAttrsFromServerToRaven(zserverBlogInfo, izblog)
        return izblog


    def _copyAttrsFromServerToRaven(self, fromModelWithAttrs, toModelWithAttrs):
        # fromModelWithAttrs = pub layer zserverblog, zservercategory or zserverentry
        # toModelWithAttrs = raven zcategory, izblog, zblogpubinfo
        for (name, value, namespace) in fromModelWithAttrs.getAllAttributes():
            # if ns is none, then copy them to cms namespace since the data came from the cms layer
            if not namespace:
                namespace = IZBlogAppNamespaces.CMS_PUBLISHER_NAMESPACE
            elif namespace == IZBlogAppNamespaces.RAVEN_DOCUMENT_NAMESPACE:
                namespace = None

            toModelWithAttrs.setAttribute(name, value, namespace) #$NON-NLS-1$
    # end _createRavenBlog()

    def _copyAttrsFromRavenToServer(self, fromModelWithAttrs, toModelWithAttrs):
        # fromModelWithAttrs = raven zcategory, izblog, zblogpubinfo
        # toModelWithAttrs = pub layer zserverblog, zservercategory or zserverentry
        for (name, value, namespace) in fromModelWithAttrs.getAllAttributes():
            if not namespace:
                # if ns is none, then copy them to raven zdocument NS
                namespace = IZBlogAppNamespaces.RAVEN_DOCUMENT_NAMESPACE
            elif namespace == IZBlogAppNamespaces.CMS_PUBLISHER_NAMESPACE:
                # if current NS is cms, the set NS to be None
                namespace = None
            toModelWithAttrs.setAttribute(name, value, namespace) #$NON-NLS-1$
    # end _copyAttrsFromRavenToServer()

    def _createRavenCategories(self, zblog, serverCategories):
        # Convert server side categories to Raven ZCategory object list
        rval = []
        for serverCategory in serverCategories:
            zcategory = self._createRavenCategory(zblog, serverCategory)
            if zcategory:
                rval.append(zcategory)
        return rval
    # end _createRavenCategories()

    def _createRavenCategory(self, zblog, serverCategory):
        # Create and return ZCategory object given server side category
        zcategory = ZCategory()
        # copy over server side attribute to raven izblog model
        self._copyAttrsFromServerToRaven(serverCategory, zcategory)
        id = self._createEntryQId( zblog.getId(), serverCategory.getId() )
        zcategory.setId(id)
        zcategory.setName( serverCategory.getName() )
        return zcategory
    # end _createRavenCategory()

    def _createRavenContent(self, serverContent):
        # Created and return xhtml content in IZDocumentContent.
        # content holder.
        zdocContent = ZXhtmlContent()
        zdocContent.setType(u"application/xhtml+xml") #$NON-NLS-1$
        zdocContent.setMode(u"xml") #$NON-NLS-1$
        xhtmlDoc = loadXhtmlDocumentFromString(serverContent)
        zdocContent.setXhtmlDocument(xhtmlDoc)
        return zdocContent
    # end _createRavenContent()

    def _createRavenPubInfo(self, zblog, serverEntry):
        # published info
        zpubinfo = ZPublishInfo()
        # copy attrs
        self._copyAttrsFromServerToRaven(serverEntry, zpubinfo)
        id = self._createEntryQId( zblog.getId(), serverEntry.getId() )
        zpubinfo.setBlogEntryId( id )
        zpubinfo.setDraft( serverEntry.isDraft() ) #
        schemaDt = ZSchemaDateTime( serverEntry.getUtcDateTime() )
        zpubinfo.setPublishedTime( schemaDt )
        zpubinfo.setSynchTime(ZSchemaDateTime())
        # FIXME (PJ) also set  updated-date
        if serverEntry.getUrl():
            zpubinfo.setUrl( serverEntry.getUrl() )
        # TODO (PJ) zpubinfo.addTrackback()
        return zpubinfo
    # end _createRavenPubInfo()

    def _createRavenBlogInfo(self, zblog, serverEntry):
        # blog info
        zbloginfo = ZBlogInfo()
        zbloginfo.setAccountId( self.getAccountId() )
        zbloginfo.setBlogId( zblog.getId() )

        # published info
        zpubinfo =  self._createRavenPubInfo(zblog, serverEntry)
        zbloginfo.setPublishInfo(zpubinfo)
        # build post entry categories
        for serverCategory in serverEntry.getCategories():
            # Convert server side category to Raven ZCategory.
            zcategory = self._createRavenCategory(zblog, serverCategory)
            zbloginfo.addCategory(zcategory)        
        return zbloginfo
    # end _createRavenBlogInfo()

    def _createRavenTagwords(self, zdoc, serverEntry):
        # Set any tagwords returned from the pub layer.
        if serverEntry.getTagwords() and len( serverEntry.getTagwords() ) > 0:
            tagspaceUri = getNoneString( serverEntry.getTagspaceUrl() )
            if tagspaceUri and tagspaceUri != IZBlogPubTagwordNamespaces.DEFAULT_TAGWORDS_URI:
                # preserve original content - tagspace as returned by pub layer. E.g LiveJournal
                ztagwords = ZTagwords()
                ztagwords.setUrl(tagspaceUri)
                ztagwords.setValue( u",".join(serverEntry.getTagwords()) ) #$NON-NLS-1$
                zdoc.addTagwords(ztagwords)
            # also add a copy to default tag NS
            ztagwords = ZTagwords()
            ztagwords.setUrl(IZBlogPubTagwordNamespaces.DEFAULT_TAGWORDS_URI)
            ztagwords.setValue( u",".join(serverEntry.getTagwords()) ) #$NON-NLS-1$
            zdoc.addTagwords(ztagwords)
    # end _createRavenTagwords

    def _createRavenDocument(self, zblog, serverEntry):
        # Create and return IZDocument
        # main document struct.
        zdoc = ZBlogDocument()
        # FIXME (PJ) server api needs separate dt fields for creation-time vs published time vs updated-time.
        schemaDt = ZSchemaDateTime( serverEntry.getUtcDateTime() )
        zdoc.setCreationTime( schemaDt )
        zdoc.setLastModifiedTime( schemaDt )
        # FIXME (PJ) Test test for entries with out a title (else autogen titles)
        zdoc.setTitle( serverEntry.getTitle() )
        # tagwords, if any.
        self._createRavenTagwords(zdoc, serverEntry)
        # blog info (including pubinfo object)
        zbloginfo = self._createRavenBlogInfo(zblog, serverEntry)
        # add blog info to doc
        zdoc.addBlogInfo(zbloginfo)
        # server side content
        content = serverEntry.getContent()
        # convert to Raven IZDocumentContent xhtml model
        zdocContent = self._createRavenContent(content)
        # add content to doc
        zdoc.setContent(zdocContent)
        # TODO: zdoc.setTagwords() and zdoc.add/setTrackback
        return zdoc
    # end _createRavenDocument()

    def _populateServerEntry(self, zserverBlogEntry, zblog, zblogDocument, zxhtmlDocument, zpubinfo):
        # Populate a ZServerBlogEntry given raven pubmeta data and post content.
        # Note: zpubinfo is valid only when updating existing post. It is None when posting new entry.
        pubmetadata = self._getPubMetaData(zblog, zblogDocument)
        title = zblogDocument.getTitle()
        content = self._transformContentForPublishing(zblog, zxhtmlDocument)
        # ----
        # print "DEBUG (blogpublisher:_populateServerEntry): ", content    # DEBUG: ChuahTC 2013-Sep-2
        # ----

        zserverBlogEntry.setTitle(title)
        zserverBlogEntry.setContent(content)
        pubSchemaDT = pubmetadata.getPublishTime()
        
        # set pub time.
        if pubSchemaDT:
            # if user has specified a pub datetime, then use it.
            zserverBlogEntry.setUtcDateTime( pubSchemaDT.getDateTime() ) # getDateTime
        elif zpubinfo:
            # if updating existing post, then use the previouslty published time
            publishedSchemaDt = zpubinfo.getPublishedTime()
            zserverBlogEntry.setUtcDateTime( publishedSchemaDt.getDateTime() )
        else:
            # default to current time.
            nowDT = getCurrentUtcDateTime()
            zserverBlogEntry.setUtcDateTime(nowDT)
        
        zserverBlogEntry.setDraft( pubmetadata.isPublishAsDraft() )
        for ravenCat in pubmetadata.getCategories():
            serverCatId = self._getServerId( ravenCat.getId() )
            serverCat = ZServerBlogCategory(serverCatId, ravenCat.getName())
            self._copyAttrsFromRavenToServer(ravenCat, serverCat)
            zserverBlogEntry.addCategory(serverCat)

        # zblogDocument::getTagwordsList() -> list of ZTagwords (a ZTagwords is a list of words per site e.g. Technorati)
        listOfWords = getWordListFromZTagwords(zblogDocument.getTagwordsList() )
        zserverBlogEntry.setTagwords(listOfWords)

        # custom meta data. (WP slug, password and post status
        slug = getCustomWPMetaDataAttribute(pubmetadata, u"wp_slug") #$NON-NLS-1$
        if slug is not None:
            zserverBlogEntry.setAttribute(u"wp_slug", slug, IZBlogPubAttrNamespaces.WP_ATTR_NAMESPACE) #$NON-NLS-1$
        status = getNoneString( getCustomWPMetaDataAttribute(pubmetadata, u"post_status") ) #$NON-NLS-1$
        if status:
            zserverBlogEntry.setAttribute(u"post_status", status, IZBlogPubAttrNamespaces.WP_ATTR_NAMESPACE) #$NON-NLS-1$
        pw = getSafeString( getCustomWPMetaDataAttribute(pubmetadata, u"wp_password") ) #$NON-NLS-1$
        zserverBlogEntry.setAttribute(u"wp_password", pw, IZBlogPubAttrNamespaces.WP_ATTR_NAMESPACE) #$NON-NLS-1$
            
        return zserverBlogEntry
    # end _populateServerEntry()

    def _getBlogInfo(self, zblog, zblogDocument):
        # returns IZBlogInfo for blog
        return zblogDocument.getBlogInfo( zblog.getId() )
    # end _getBlogInfo()

    def _getPubMetaData(self, zblog, zblogDocument):
        pubMetaData = None
        for metadata in zblogDocument.getPubMetaDataList():
            if metadata.getBlogId() == zblog.getId():
                pubMetaData = metadata
                break
        if not pubMetaData:
            if self._getLogger():
                self._getLogger().warning(u"ZPubMetaData not found for blog %s and document %s" %(zblog.getId(), zblogDocument.getId())) #$NON-NLS-1$
            pubMetaData = ZPubMetaData()
            pubMetaData.setAccountId( self.getAccountId())
            pubMetaData.setBlogId(zblog.getId())
            pubMetaData.setAddPoweredBy(False)
            pubMetaData.setPublishAsDraft(False)
            pubMetaData.setForceReUploadImages(False)
            pubMetaData.setUploadTNsOnly(False)
            pubMetaData.setPublishTime(None)

        return pubMetaData
    # end _getPubMetaData()

    def listBlogs(self):
        rval = []
        serverBlogs = self._listBlogs()
        # assign unique id within each account.
        for serverBlog in serverBlogs:
            # server blog is instance of ZServerBlogInfo
            # convert to raven account blog
            izblog = self._createRavenBlog(serverBlog)
            rval.append(izblog)
        return rval

    def listCategories(self, zblog):
        serverBlogId = self._getServerId( zblog.getId() )
        serverCategories = self._listCategories(zblog, serverBlogId)
        rval = self._createRavenCategories(zblog, serverCategories)
        return rval

    def listEntries(self, zblog, maxEntries):
        if maxEntries < 1:
            maxEntries  = 20
        serverBlogId = self._getServerId( zblog.getId() )
        # get list of blogpub:ZServerBlogEntry object
        serverEntries = self._listEntries(zblog, serverBlogId, maxEntries)
        rval = []
        for serverEntry in serverEntries:
            try:    
                zdoc = self._createRavenDocument(zblog, serverEntry)            
                if zdoc:
                    rval.append(zdoc)
            except Exception,e:
                if self._getLogger():
                    s = u"Error converting post to xhtml: '%s', PostId=%s, PostURL=%s, PostTitle=%s" % (unicode(e), serverEntry.getId(), serverEntry.getUrl(), serverEntry.getTitle()) #$NON-NLS-1$
                    self._getLogger().error(s) 
                    self._getLogger().exception(e)
        return rval
    # end listEntries()

    def postEntry(self, zblog, zblogDocument, zxhtmlDocument):
        serverBlogId = self._getServerId( zblog.getId() )
        zserverBlogEntry = ZServerBlogEntry()
        self._populateServerEntry(zserverBlogEntry, zblog, zblogDocument, zxhtmlDocument, None)
        zserverBlogEntry = self._postEntry(zblog, serverBlogId, zserverBlogEntry)
        zbloginfo = self._createRavenBlogInfo(zblog, zserverBlogEntry)
        return zbloginfo
    # end postEntry()

    def _createServerEntryForUpdateOrDelete(self, zblog, zblogDocument, zxhtmlDocument):
        zblogInfo = self._getBlogInfo(zblog, zblogDocument)
        zpubinfo = zblogInfo.getPublishInfo()
        serverEntryId = self._getServerId( zpubinfo.getBlogEntryId() )
        # create server entry
        zserverBlogEntry = ZServerBlogEntry()
        # copy raven pub data (including atom edit endpoints) to server doc.
        self._copyAttrsFromRavenToServer(zpubinfo, zserverBlogEntry)
        # copy title, date, and content iff content is given (otherwise only meta data such as atom edit link is available - i.e for atom delete op).
        if zxhtmlDocument:
            self._populateServerEntry(zserverBlogEntry, zblog, zblogDocument, zxhtmlDocument, zpubinfo)
        zserverBlogEntry.setId(serverEntryId)
        return zserverBlogEntry
    # end _createServerEntryForUpdateOrDelete()

    def updateEntry(self, zblog, zblogDocument, zxhtmlDocument):
        # save copy of previously sent trackbacks
        trackbacks = []
        oldBlogInfo = zblogDocument.getBlogInfo( zblog.getId() )
        if oldBlogInfo:
            oldPubInfo = oldBlogInfo.getPublishInfo()
            if oldPubInfo:
                trackbacks = oldPubInfo.getTrackbacks() 
        
        serverBlogId = self._getServerId( zblog.getId() )
        # create server entry
        zserverBlogEntry = self._createServerEntryForUpdateOrDelete(zblog, zblogDocument, zxhtmlDocument)
        updatedServerBlogEntry = self._updateEntry(zblog, serverBlogId, zserverBlogEntry)
        zupdatedBloginfo = self._createRavenBlogInfo(zblog, updatedServerBlogEntry) 
        #  copy over previousely sent trackbacks
        if trackbacks and zupdatedBloginfo.getPublishInfo():
            for tb in trackbacks:
                zupdatedBloginfo.getPublishInfo().addTrackback(tb)                       
        return zupdatedBloginfo
    # end updateEntry()

    def deleteEntry(self, zblog, zblogDocument):
        serverBlogId = self._getServerId( zblog.getId() )
        zserverBlogEntry = self._createServerEntryForUpdateOrDelete(zblog, zblogDocument, None)
        return self._deleteEntry(zblog, serverBlogId, zserverBlogEntry)
    # end deleteEntry()

    def uploadFile(self, zblog, srcFilename, destFilename, serverMediaUploadListener):
        serverBlogId = self._getServerId( zblog.getId() )
        if serverMediaUploadListener is None:
            serverMediaUploadListener = IZBlogServerMediaUploadListener()
        return self._uploadFile(zblog, serverBlogId, srcFilename, destFilename, serverMediaUploadListener)
    # end uploadFile()

    def _transformContentForPublishing(self, zblog, zxhtmlDocument): #@UnusedVariable
        u"""_transformContentForPublishing(ZBlog, ZXhtmlDocument) -> string representation of content.
        Subclasses can override to convert the xhtml document to a string prior to publishing.
        """  #$NON-NLS-1$
        # simply serialize the body content (but not including the body element).
        content = extractBody(zxhtmlDocument.getBody().serialize())

        # ---- START ----
        #
        # To avoid getting self-terminating "iframe" tags, we filter the body content through "tidyutil.py".
        #    ChuahTC Date: 2013-Sept-3
        #
        # print "DEBUG (blogpublisher:_transformContentForPublishing) BEFORE: ", content    # DEBUG: ChuahTC 2013-Sep-3

        # Set "output_xml=0" instead of 1 to fix the problem with (occasional) empty content after filtering through
        # "tidyutil.py" when "iframe" tags are present.
        #
        #    ChuahTC Date: 2014-Mar-19
        #
        # tidyOptions = dict(output_xml=1, show_body_only=1, quiet=1, char_encoding="utf8", \
        #                   output_error=0, show_warnings=0, quote_nbsp=0, raw=1)
        tidyOptions = dict(output_xml=0, show_body_only=1, quiet=1, char_encoding="utf8", \
                           output_error=0, show_warnings=0, quote_nbsp=0, raw=1)

        content = tidyutil.tidyHtml(content, tidyOptions)

        # print "DEBUG (blogpublisher:_transformContentForPublishing) AFTER: ", content    # DEBUG: ChuahTC 2013-Sep-3
        # ---- END -----


        removeNewLines = zblog.getPreferences().getUserPreferenceBool(IZBlogAppUserPrefsKeys.SP_REMOVE_NEWLINES, False)
        if removeNewLines:
            transformer = ZXhtmlRemoveNewLinesTransformer()
            content = transformer.transform(content)

            # ---- START ----
            # print "DEBUG (blogpublisher:_transformContentForPublishing)NewLinesRemoved: ", content    # DEBUG: ChuahTC 2013-Sep-3
            # ---- END -----


        return content
    # end _transformContentForPublishing()

    def _listBlogs(self):
        u"""Subclasses must implement this method to return list zserver blogs."""  #$NON-NLS-1$
        raise ZNotYetImplementedException(unicode(self.__class__), u"_listBlogs") #$NON-NLS-1$
    # end _listBlogs()

    def _listCategories(self, zblog, serverBlogId): #@UnusedVariable
        u"""Subclasses must implement this method to return list zserver categories."""  #$NON-NLS-1$
        raise ZNotYetImplementedException(unicode(self.__class__), u"_listCategories") #$NON-NLS-1$
    # end _listCategories()

    def _listEntries(self, zblog, serverBlogId, maxEntries): #@UnusedVariable
        u"""Subclasses must implement this method to return list zserver entries."""  #$NON-NLS-1$
        raise ZNotYetImplementedException(unicode(self.__class__), u"_listEntries") #$NON-NLS-1$
    # end _listEntries()

    def _postEntry(self, zblog, serverBlogId, zserverBlogEntry): #@UnusedVariable
        u"""Subclasses must implement this method to publish an entry and return the
        zserverBlogEntry with the new publish info."""  #$NON-NLS-1$
        raise ZNotYetImplementedException(unicode(self.__class__), u"_postEntry") #$NON-NLS-1$
    # end _postEntry()

    def _updateEntry(self, zblog, serverBlogId, zserverBlogEntry): #@UnusedVariable
        u"""Subclasses must implement this method to update an entry and return
        zserverBlogEntry with the new publish info."""  #$NON-NLS-1$
        raise ZNotYetImplementedException(unicode(self.__class__), u"_updateEntry") #$NON-NLS-1$
    # _updateEntry()

    def _deleteEntry(self, zblog, serverBlogId, zserverBlogEntry): #@UnusedVariable
        u"""Subclasses must implement this method to delete  an entry"""  #$NON-NLS-1$
        raise ZNotYetImplementedException(unicode(self.__class__), u"_deleteEntry") #$NON-NLS-1$
    # end _deleteEntry()

    def _uploadFile(self, zblog, serverBlogId, srcFilename, destFilename, serverMediaUploadListener): #@UnusedVariable
        u"""Subclasses must implement this method to return upload file and return url to file."""  #$NON-NLS-1$
        raise ZNotYetImplementedException(unicode(self.__class__), u"_uploadFile") #$NON-NLS-1$
    # end _uploadFile()
# end ZBlogPublisher
