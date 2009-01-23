from zoundry.blogapp.constants import IZBlogAppServiceIDs
from zoundry.appframework.global_services import getApplicationModel
from zoundry.base.xhtml.xhtmlanalyzers import ZXhtmlRemovePrefixVisitor
from zoundry.appframework.global_services import getLoggerService
from zoundry.appframework.util import crypt
from zoundry.base.util.command import ZCommandBase
from zoundry.base.util.text.textutil import getSafeString
from zoundry.base.util.types.capabilities import ZCapabilities
from zoundry.base.util.types.parameters import ZParameters
from zoundry.blogapp.constants import PASSWORD_ENCRYPTION_KEY
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.services.docindex.indeximpl import ZDocumentSearchFilter
from zoundry.blogapp.services.pubsystems.blog.blogpubprocessor import ZBlogDocumentPublishProcessor
from zoundry.blogpub.blogserverapi import IZBlogApiCapabilityConstants
from zoundry.blogpub.blogserverapi import IZBlogApiParamConstants
from zoundry.blogpub.blogserverapi import ZBlogServerException

#----------------------------------------------------
# media storage type for blog publisher
#----------------------------------------------------
BLOGPUBLISHER_MEDIA_STORE_TYPE_ID = u"zoundry.blogapp.mediastorage.type.blog" #$NON-NLS-1$
BLOGPUBLISHER_METAWEBLOG_MEDIA_SITE_ID = u"zoundry.blogapp.mediastorage.site.blog.metaweblog" #$NON-NLS-1$


# --------------------------------------------------------------------------
# Creates publisher for the given account
# --------------------------------------------------------------------------
def createBlogPublisherFromAccount(zaccount, zpublishingsvc, factoryClassname = None):
    username = zaccount.getAttribute(u"username")#$NON-NLS-1$
    cyppass = zaccount.getAttribute(u"password")#$NON-NLS-1$
    password = crypt.decryptCipherText(cyppass, PASSWORD_ENCRYPTION_KEY)
    apiInfo = zaccount.getAPIInfo()
    url = apiInfo.getUrl()
    siteId = apiInfo.getType()
    publisher = createBlogPublisher(username,password,url,siteId,zpublishingsvc,factoryClassname)
    publisher.setAccount( zaccount )
    return publisher
# end createBlogPublisherFromAccount()


def createBlogPublisher(username, password, url, siteId, zpublishingsvc, factoryClassname = None):
        map = {}
        map[IZBlogApiParamConstants.API_USERNAME] = username
        map[IZBlogApiParamConstants.API_PASSWORD] = password
        if url:
            map[IZBlogApiParamConstants.API_ENDPOINT_URL] = url
        map[IZBlogApiParamConstants.API_CLIENT_VERSION] = u"Zoundry Raven (www.zoundry.com)" #$NON-NLS-1$ #$NON-NLS-2$

        # override factory class property
        if factoryClassname and len(factoryClassname) > 0:
            map[u"zoundry.raven.param.blogpub.blogserver.factory.classname"] = factoryClassname #$NON-NLS-1$
        # FIXME (PJ) merge params and capabilities from zaccount (instead of using explict factory classname)
        params = ZParameters(map)
        capabilites = ZCapabilities()
        publisher = zpublishingsvc.createPublisher( siteId, capabilites, params )
        # FIXME (PJ) assert publisher is not None and isinstanceof IZBlogPublisher
        return publisher
# end createBlogPublisher()


# --------------------------------------------------------------------------
# Publishing Related Tasks.
# --------------------------------------------------------------------------
class ZBlogPublisherCommandBase(ZCommandBase):

    def __init__(self, name, zblogpublisher):
        ZCommandBase.__init__(self, name)
        self.publisher = zblogpublisher

    def _getPublisher(self):
        return self.publisher

    def doCommand(self):
        pass

    def _debug(self, message):
        self._logActivity(message)
        if getLoggerService():
            getLoggerService().debug(message)
        else:
            print message.encode(u'iso-8859-1', u'replace') #$NON-NLS-1$ #$NON-NLS-2$

    def _warning(self, message):
        self._logActivity(message)
        if getLoggerService():
            getLoggerService().warning(message)
        else:
            print message.encode(u'iso-8859-1', u'replace') #$NON-NLS-1$ #$NON-NLS-2$

    def _error(self, message):
        self._logActivity(message)
        if getLoggerService():
            getLoggerService().error(message)
        else:
            print message.encode(u'iso-8859-1', u'replace') #$NON-NLS-1$ #$NON-NLS-2$

    def _exception(self, exception):
        if getLoggerService():
            getLoggerService().exception(exception)

    def _getBlogInfo(self, zblog, zDocEntry):
        # Convinience method to return blog for blog.
        blogInfo = zDocEntry.getBlogInfo( zblog.getId() )
        if not blogInfo:
            self._debug(u"BlogInfo not found for blog ID % in document ID %s" % (zblog.getId(), zDocEntry.getId()) ) #$NON-NLS-1$
        return blogInfo

    def _getPublishInfo(self, zblog, zDocEntry):
        # Convinience method to return pub info for blog.
        blogInfo = self._getBlogInfo(zblog, zDocEntry)
        pubInfo = None
        if blogInfo:
            pubInfo = blogInfo.getPublishInfo()
        return pubInfo


# --------------------------------------------------------------------------
# Command that create and removes blog-publisher type media storages
# --------------------------------------------------------------------------
class ZCreateOrUpdateBlogMediaStoragesCommand(ZBlogPublisherCommandBase):

    def __init__(self, zblogpublisher, mediaStoreService,  zaccount):
        ZBlogPublisherCommandBase.__init__(self,  u"createmediastorages", zblogpublisher) #$NON-NLS-1$
        self.account = zaccount
        self.mediaStoreService = mediaStoreService
    # end __init__()

    def doCommand(self):
        self.removeOrphanedStores(self.account)
        self.createMediaStorages(self.account)

    def _isBlogPublisherTypeStore(self, mediaStore):
        if not mediaStore:
            return False
        siteId = mediaStore.getMediaSiteId()
        mediaSite = self.mediaStoreService.getMediaSite(siteId)
        storeTypeId = mediaSite.getMediaStorageTypeId()
        return BLOGPUBLISHER_MEDIA_STORE_TYPE_ID == storeTypeId

    def getBlogPublisherMediaStoragesByAccount(self, accountId):
        # Returns list of stores for the given account that of type 'blog publisher'
        rval = []
        for store in self.mediaStoreService.getMediaStorages():
            if not self._isBlogPublisherTypeStore(store):
                continue
            # store is of type BLOGPUBLISHER_MEDIA_STORE_TYPE_ID
            props = store.getProperties()
            if props.has_key(u"account-id") and getSafeString(props[u"account-id"]) == accountId: #$NON-NLS-1$ #$NON-NLS-2$
                rval.append(store)
        return rval

    def removeOrphanedStores(self, account):
        u"""Deletes the 'blog-publisher' type media storages for account blogs that not long exists. Eg. when a blog has been removed from the server.
        """ #$NON-NLS-1$
        # build list of IDs for current/active blogs
        currBlogIdList = []
        for blog in account.getBlogs():
            currBlogIdList.append( blog.getId() )
        # get list of 'blog publisher' type media storages associated with this account
        accountMediaStorages = self.getBlogPublisherMediaStoragesByAccount( account.getId() )
        removedStoreIdList = []
        for store in accountMediaStorages:
            props = store.getProperties()
            if props.has_key(u"blog-id") and getSafeString(props[u"blog-id"]) not in currBlogIdList: #$NON-NLS-1$ #$NON-NLS-2$
                removedStoreIdList.append(store.getId())
                self._debug(u"Removing orphaned media store %s[%s]" % (store.getName(), store.getId()) ) #$NON-NLS-1$
                self.mediaStoreService.deleteMediaStorage(store)
            # if
        # for
        return removedStoreIdList

    def createMediaStorages(self, account):
        u"""Creates blogpublisher type media storages for each blog in the account that
        currently do not have a storeId assigned as well as the upload method is set to 'publisher'.
        """ #$NON-NLS-1$        
        accBlogs = account.getBlogs()
        for blog in accBlogs:
            mediaStoreId = blog.getMediaUploadStorageId()
            if mediaStoreId:
                # a store exists.
                continue
            self.createMediaStorageForBlog(account, blog)
    # end createNewStores()
    
    def _createImageShackMediaStorageForBlog(self, zblog):
        mediaSiteId = u"zoundry.blogapp.mediastorage.site.image-shack" #$NON-NLS-1$
        properties = {}
        mediaStoreService = getApplicationModel().getService(IZBlogAppServiceIDs.MEDIA_STORAGE_SERVICE_ID)
        storeName = u"ImageShack %s" % zblog.getName() #$NON-NLS-1$
        storeName = mediaStoreService.createStorageName(storeName)        
        store = mediaStoreService.createMediaStorage(storeName, mediaSiteId, properties)
        zblog.setMediaUploadStorageId( store.getId() )
        zblog.setMediaUploadMethod(u"mediastorage") #$NON-NLS-1$
        return True
    # end _createImageShackMediaStorageForBlog()       
    
    def _createXmlRpcMediaStorageForBlog(self, zblog):
        account = zblog.getAccount()
        accountId = account.getId()
        blogId = zblog.getId()
        apiInfo = account.getAPIInfo()
        apiSiteId = apiInfo.getType()
        mediaSiteId = u"zoundry.blogapp.mediastorage.site.blog.metaweblog" #$NON-NLS-1$
        properties = {}
        properties[u"account-id"] = accountId #$NON-NLS-1$
        properties[u"blog-id"] = blogId #$NON-NLS-1$
        properties[u"blog-url"] = zblog.getUrl() #$NON-NLS-1$
        properties[u"api-site-id"] = apiSiteId #$NON-NLS-1$
        mediaStoreService = getApplicationModel().getService(IZBlogAppServiceIDs.MEDIA_STORAGE_SERVICE_ID)
        storeName = u"Blog %s" % zblog.getName() #$NON-NLS-1$
        storeName = mediaStoreService.createStorageName(storeName)
        store = mediaStoreService.createMediaStorage(storeName, mediaSiteId, properties)
        zblog.setMediaUploadStorageId( store.getId() )
        zblog.setMediaUploadMethod(u"publisher") #$NON-NLS-1$
        return True
    # end _createXmlRpcMediaStorageForBlog()    

    def createMediaStorageForBlog(self, account, zblog):
        u"""Creates blogpublisher type media storage for blog.
        """ #$NON-NLS-1$
        apiInfo = account.getAPIInfo()
        apiSiteId = apiInfo.getType()        
        supportsUpload = False
        try:
            publisherService = getApplicationModel().getService(IZBlogAppServiceIDs.PUBLISHING_SERVICE_ID)
            zpublisherSiteDef = publisherService.getPublisherSite(apiSiteId)
            supportsUpload = zpublisherSiteDef.getCapabilities().supportsUploadMedia()
        except:
            pass
        
        if supportsUpload:
            self._createXmlRpcMediaStorageForBlog(zblog)
        else:
            self._createImageShackMediaStorageForBlog(zblog)
    # end _createStore()

# --------------------------------------------------------------------------
# Command that updates the account with the list of blogs
# --------------------------------------------------------------------------
class ZListBlogsCommand(ZBlogPublisherCommandBase):

    def __init__(self, zblogpublisher, zaccount, filterBlogList = []):
        ZBlogPublisherCommandBase.__init__(self,  u"listblogs", zblogpublisher) #$NON-NLS-1$
        self.account = zaccount
        self.listChanged = False
        self.filterBlogList = filterBlogList

    def isListChanged(self):
        return self.listChanged

    def doCommand(self):
        self.listBlogs()

    def listBlogs(self):
        self._debug(u"Begin listBlogs") #$NON-NLS-1$
        self.listChanged = False
        onlineBlogs = self._getPublisher().listBlogs()
        self._debug(u"Found %d blogs" % len (onlineBlogs) ) #$NON-NLS-1$
        # First, remove any blogs that not longer exist online.
        for localBlog in self.account.getBlogs():
            if not self._containsBlog(onlineBlogs, localBlog):
                self._debug(u"Removing blog %s[%s]" % (localBlog.getName(), localBlog.getId()) ) #$NON-NLS-1$
                self.listChanged = True
                self.account.removeBlog(localBlog)

        # Now, add any new blogs. (if filter list is given, then only add those.)
        if self.filterBlogList and len(self.filterBlogList) > 0:
            onlineBlogs = self._getFilteredBlogList(onlineBlogs, self.filterBlogList)

        for onlineBlog in onlineBlogs:
            if self._containsBlog(self.account.getBlogs() , onlineBlog):
                # already exists - just update for now
                if self._updateBlog(onlineBlog, self.account.getBlogById(onlineBlog.getId()) ):
                    self._debug(u"Updating blog %s[%s]" % (onlineBlog.getName(), onlineBlog.getId()) ) #$NON-NLS-1$
                    self.listChanged = True
            else:
                self._debug(u"Adding blog %s[%s]" % (onlineBlog.getName(), onlineBlog.getId()) ) #$NON-NLS-1$
                self.listChanged = True
                self.account.addBlog(onlineBlog)
        # end for
        self._debug(u"End listBlogs") #$NON-NLS-1$
        return self.listChanged

    def _updateBlog(self, fromBlog, toBlog):
        dirty = False
        if toBlog:
            if fromBlog.getName() != toBlog.getName():
                toBlog.setName( fromBlog.getName() )
                dirty = True
            if fromBlog.getUrl() != toBlog.getUrl():
                toBlog.setUrl( fromBlog.getUrl() )
                dirty = True
        return dirty

    def _getFilteredBlogList(self, srcBlogList, filterBlogList):
        rval = []
        for blog in srcBlogList:
            for tmp in filterBlogList:
                if (blog.getId() == tmp.getId()) \
                    or (blog.getName() == tmp.getName() and blog.getUrl() == tmp.getUrl()):
                    rval.append(blog)
        return rval

    def _containsBlog(self, blogList, blog):
        for b in blogList:
            if b.getId() == blog.getId():
                return True
        return False
    # end _containsBlog()

# --------------------------------------------------------------------------
# Command that updates the account blogs with the list of categoriss
# --------------------------------------------------------------------------
class ZListCategoriesCommand(ZBlogPublisherCommandBase):

    def __init__(self, zblogpublisher, zaccount, zbloglist):
        ZBlogPublisherCommandBase.__init__(self,  u"listcategories", zblogpublisher) #$NON-NLS-1$
        self.account = zaccount
        self.blogList = zbloglist
        self.listChanged = False

    def isListChanged(self):
        return self.listChanged

    def doCommand(self):
        self.listCategories()

    def listCategories(self):
        self.listChanged = False
        for blog in self.blogList:
            if not self.isCancelled() and self.listCategoriesForBlog(blog):
                self.listChanged = True
        return self.listChanged

    def listCategoriesForBlog(self, zblog):
        dirty = False
        self._debug(u"Begin listCategories for blog %s[%s]" % (zblog.getName(), zblog.getId()) ) #$NON-NLS-1$
        onlineCategories = self._getPublisher().listCategories(zblog)
        blogCategories = zblog.getCategories()
        self._debug(u"Number of categores local:%d, online:%d" % (len(blogCategories), len(onlineCategories)) ) #$NON-NLS-1$
        # get list of new categories
        addList = self._getDiffList(blogCategories, onlineCategories)
        self._debug(u"Number of categores to add: %d" % len(addList) ) #$NON-NLS-1$
        # get list of categories to be removed
        delList = self._getDiffList(onlineCategories, blogCategories)
        self._debug(u"Number of categores to remove: %d" % len(delList) ) #$NON-NLS-1$
        # remove categories only if the categories are not user generated
        if len(delList) > 0 and not self._getPublisher().getCapabilities().hasCapability(IZBlogApiCapabilityConstants.USERGENERATED_CATEGORIES):
            dirty = True
            for delCat in delList:
                self._debug(u"Removing category %s[%s]" % (delCat.getName(), delCat.getId()) ) #$NON-NLS-1$
                zblog.removeCategory(delCat)
        # add the new categories
        for addCat in addList:
            self._debug(u"Adding category %s[%s]" % (addCat.getName(), addCat.getId()) ) #$NON-NLS-1$
            dirty = True
            zblog.addCategory(addCat)
        self._debug(u"End listCategories") #$NON-NLS-1$
        return dirty

    def _getDiffList(self, oldList, newList):
        # compares the two lists of categories and returns the items
        # thay are new.
        diffList = []
        for newCat in newList:
            found = False
            for oldCat in oldList:
                if newCat.getId() == oldCat.getId():
                    found = True
                    break
                # end for
            if not found:
                diffList.append(newCat)
        # end for
        return diffList


# --------------------------------------------------------------------------
# Command that lists recent posts
# --------------------------------------------------------------------------
class ZListEntriesCommand(ZBlogPublisherCommandBase):

    def __init__(self, zblogpublisher, zaccount, zbloglist, numPosts = 20):
        ZBlogPublisherCommandBase.__init__(self,  u"downloadEntries", zblogpublisher) #$NON-NLS-1$
        self.account = zaccount
        self.blogList = zbloglist
        self.numPosts = numPosts
        self.entriesMap = {}

    def doCommand(self):
        for blog in self.blogList:
            if not self.isCancelled():
                self.downloadEntriesForBlog(blog, self.numPosts)

    def downloadEntriesForBlog(self, zblog, numPosts):
        self._debug(u"Begin downloadEntries for blog %s[%s]" % (zblog.getName(), zblog.getId()) ) #$NON-NLS-1$
        entries = self._getPublisher().listEntries(zblog, numPosts)
        self.entriesMap[zblog.getId() ] = entries
        self._debug(u"Downloaded %d entries." % len(entries))  #$NON-NLS-1$
        self._debug(u"End downloadEntries") #$NON-NLS-1$
        return entries

    def getEntries(self, zblog):
        rval = None
        if self.entriesMap.has_key(zblog.getId()):
            rval = self.entriesMap[ zblog.getId()]
        return rval

# --------------------------------------------------------------------------
# Command that download recent posts direcly to the store
# --------------------------------------------------------------------------
class ZDownloadEntriesCommand(ZListEntriesCommand):

    def __init__(self, zdocstore, zindexService, zblogpublisher, zaccount, zbloglist, numPosts = 20):
        ZListEntriesCommand.__init__(self, zblogpublisher, zaccount, zbloglist, numPosts)
        self.docStore = zdocstore
        self.docIndexService = zindexService
    # end __init__()

    def downloadEntriesForBlog(self, zblog, numPosts):
        zDocEntries = ZListEntriesCommand.downloadEntriesForBlog(self, zblog, numPosts)
        for zDocEntry in zDocEntries:
            if self._checkIfCanceled():
                break
            # if previously published (i.e. already in datastore), then get IZDocumentIDO for that.
            docIDO = self._getExistingDocumentIdo(zblog, zDocEntry)
            # add document if not update document
            if not self._addDocument(zblog, zDocEntry, docIDO):
                self._updateDocument(zblog, zDocEntry, docIDO)         
        return zDocEntries
    # end downloadEntriesForBlog()
    
    def _addDocument(self, zblog, zDocEntry, docIDO): #@UnusedVariable
        # add document and return true otherwise false
        if self._checkIfAdd(zblog, zDocEntry, docIDO):
            self.docStore.addDocument(zDocEntry)
            return True
        else:
            return False
    # end _addDocument

    def _checkIfAdd(self, zblog, zDocEntry, docIDO): #@UnusedVariable
        # FIXME (PJ) Check for conflicts/changes: timestamp, title, draft and categories. (Note: xml-rpc only supports a single 'creationDate'. Does not supporte lastModified etc.)
        # E.g. in the simplest case, if the server has the new version, then replace the current docstore blog info with the downloaded zDocEntry bloginfo.
        return docIDO is None
    # end _checkIfAdd()
    
    def _updateDocument(self, zblog, zDocEntry, docIDO): #@UnusedVariable
        izPubDataIDO =  docIDO.getPubDataIDO(  zblog.getId() )
        if not izPubDataIDO:
            return False
        # update published URL if need (e.g blogger.com does not return URL for scheduled posts - so, that means
        # we will have to get the post URL next time the user downloads the document.
        # first, check to see if local document has URL
        if izPubDataIDO and izPubDataIDO.getUrl() is not None:
            return False
        
        document = self.docStore.getDocument( docIDO.getId() )
        if not document:
            return False
        docBlogInfo = document.getBlogInfo( zblog.getId() )
        if not docBlogInfo:
            return False
        docPubInfo = docBlogInfo.getPublishInfo()
        if not docPubInfo:
            return False
        # pub info for the remote doc        
        remoteDocPubInfo = self._getPublishInfo(zblog, zDocEntry)
        docPubInfo.setUrl(remoteDocPubInfo.getUrl() )
        # save document meta data
        self.docStore.saveDocument(document, True)
    # end _updateDocument()
            
    def _getExistingDocumentIdo(self,zblog, zDocEntry):
       rval = None
       if self.docIndexService:
            # Use the index service to see if the document (by published entry id) already exists locally. If so, do not add.
            pubInfo = self._getPublishInfo(zblog, zDocEntry)
            if pubInfo:
                rval = self._getDocumentIdoFromEntryId( pubInfo.getBlogEntryId() )
       return rval
   # end _getExistingDocumentIdo
    

    def _getDocumentIdoListFromEntryId(self, blogEntryId):
        # Convenience method to return the document ido list (in case of duplicates) given blogEntryId.
        if not self.docIndexService:
            self._error(u"_getDocumentIdoFromEntryId() -> Document Indexer service must be enabled.")  #$NON-NLS-1$
            return None
        filter = ZDocumentSearchFilter()
        filter.setBlogEntryIdCriteria(blogEntryId)
        izdocumentIdoList = self.docIndexService.findDocuments(filter)
        return izdocumentIdoList
    # end _getDocumentIdoListFromEntryId()

    def _getDocumentIdoFromEntryId(self, blogEntryId):
        # Convenience method to return the document ido (in case of duplicates) given blogEntryId.
        # Returns first entry if multiple matches are found.
        izdocumentIdoList = self._getDocumentIdoListFromEntryId(blogEntryId)
        ido = None
        if len(izdocumentIdoList) > 0:
            ido = izdocumentIdoList[0]
        return ido
    # end _getDocumentIdoFromEntryId()

# end ZDownloadEntriesCommand


# --------------------------------------------------------------------------
# base command to publish, update and delete a document.
# --------------------------------------------------------------------------
class ZCreateUpdateDeleteEntryCommandBase(ZBlogPublisherCommandBase):

    def __init__(self, name, zblogpublisher, zdocstore, zaccount, zblog, zblogDocument):
        ZBlogPublisherCommandBase.__init__(self, name, zblogpublisher)
        self.docStore = zdocstore
        self.account = zaccount
        self.zblog = zblog
        self.zblogDocument = zblogDocument
    # end __init__()

    def _getAccount(self):
        return self.account
    # end _getAccount()

    def _getBlog(self):
        return self.zblog
    # end _getBlog()

    def _getDocument(self):
        return self.zblogDocument
    # end _getDocument()

# end ZCreateUpdateDeleteEntryCommandBase


# --------------------------------------------------------------------------
# Command to publish document.
# --------------------------------------------------------------------------
class ZPublishEntryCommand(ZCreateUpdateDeleteEntryCommandBase):

    def __init__(self, zblogpublisher, zdocstore, zaccount, zblog, zblogDocument, zpubmetadata):
        ZCreateUpdateDeleteEntryCommandBase.__init__(self,  u"publishEntry", zblogpublisher, zdocstore, zaccount, zblog, zblogDocument) #$NON-NLS-1$
        self.processor = ZBlogDocumentPublishProcessor(self.zblog, self.zblogDocument, zpubmetadata, self)
        self.totalWorkUnits = -1
    # end __init__

    def notifyProgress(self, message, workamount, logMessage):
        # call back via ZBlogDocumentPublishProcessor and its pre/post handlers
        self._notifyActivity(message, workamount, logMessage) #$NON-NLS-1$
    # end notifyProgress

    def notifyDebug(self, message):
        # call back via ZBlogDocumentPublishProcessor and its pre/post handlers
        self._debug(message)
    # end notifyDebug

    def getTotalWorkUnits(self):
        if self.totalWorkUnits == -1:
            self._debug(u"Preparing to publish"); #$NON-NLS-1$
            if self._runPrepare():
                # total work units = total for handlers + 1 for publishing
                self.totalWorkUnits = self.processor.getTotalWorkUnits() + 1
            else:
                self._debug(u"Prepare failed."); #$NON-NLS-1$
            self._debug(u"Total work units is %d" % self.totalWorkUnits); #$NON-NLS-1$
        return self.totalWorkUnits
    # end getTotalWorkUnits()

    def doCommand(self):
        self._debug(u"Begin publish/update to blog %s[%s]" % (self.zblog.getName(), self.zblog.getId()) ) #$NON-NLS-1$
        self._debug(u"Document to publish is %s[%s]" % (self.zblogDocument.getTitle(), self.zblogDocument.getId()) ) #$NON-NLS-1$
        # prepare
        # total work units = total for handlers + 1 for publishing
        total = self.getTotalWorkUnits()
        if total < 1:
            self._debug(u"Aborting... work units < 1"); #$NON-NLS-1$
            self._notifyEnd()
            return

        self._notifyBegin(total)
        # preprocess and upload media
        if not self._runPreprocess():
            self._debug(u"Aborting... preprocess failed."); #$NON-NLS-1$
            self._notifyEnd()
            return

        if self._checkIfCanceled():
            return

        self._notifyActivity(u"Publishing document.", 1, True) #$NON-NLS-1$
        # publish document
        if not self._runPublish():
            self._debug(u"Aborting publish/update failed."); #$NON-NLS-1$
            self._notifyEnd()
            return

        if self._checkIfCanceled():
            return

        # ping, track backs etc.
        self._runPostprocess()
        self._notifyEnd()
        self._debug(u"End publish/update to blog %s[%s]" % (self.zblog.getName(), self.zblog.getId()) ) #$NON-NLS-1$

    def _runPrepare(self):
        return self.processor.runPrepare()

    def _runPreprocess(self):
        self._debug(u"Running prepocess"); #$NON-NLS-1$
        return self.processor.runPreprocess()

    def _runPostprocess(self):
        self._debug(u"Running post process"); #$NON-NLS-1$
        return self.processor.runPostprocess()

    def _handleCancel(self):
        self.processor.runCancel()
    # end _handleCancel()

    def _runPublish(self):
        xhtmldoc = self.processor.getDocumentForPublishing()
        # run visitor to remove xml: and xmlns: prefixes
        visitor = ZXhtmlRemovePrefixVisitor()
        visitor.visit(xhtmldoc.getDom() )
        try:
            blogInfo = self._publishContent(xhtmldoc)
            pubInfo = blogInfo.getPublishInfo()
            self._debug(u"Done publishing/updating. Remote doc id is %s" % pubInfo.getBlogEntryId()); #$NON-NLS-1$
            self._debug(u"Doc url %s" % pubInfo.getUrl()); #$NON-NLS-1$
            self.zblogDocument.addBlogInfo(blogInfo)
            self.docStore.saveDocument(self.zblogDocument, True)
            self._debug(u"Document saved.") #$NON-NLS-1$
            return True
        except Exception, e:
            raise e
    # end _runPublish()

    def _publishContent(self, xhtmldoc):
        self._debug(u"Publishing entry...") #$NON-NLS-1$
        blogInfo = self._getPublisher().postEntry(self.zblog, self.zblogDocument, xhtmldoc)
        return blogInfo
    # end _publishContent()

# end ZPublishEntryCommand


# --------------------------------------------------------------------------
# Command to update document.
# --------------------------------------------------------------------------
class ZUpdateEntryCommand(ZPublishEntryCommand):

    def __init__(self, zblogpublisher, zdocstore, zaccount, zblog, zblogDocument, zpubmetadata):
        ZPublishEntryCommand.__init__(self, zblogpublisher, zdocstore, zaccount, zblog, zblogDocument, zpubmetadata)
        self._setName(u"updateEntry") #$NON-NLS-1$
    # end __init__()

    def _publishContent(self, xhtmldoc):
        self._debug(u"Updating entry...") #$NON-NLS-1$
        blogInfo = self._getPublisher().updateEntry(self.zblog, self.zblogDocument, xhtmldoc)
        return blogInfo
    # end _publishContent()

# end ZUpdateEntryCommand


# --------------------------------------------------------------------------
# Command to delete a document.
# --------------------------------------------------------------------------
class ZDeleteEntryCommand(ZCreateUpdateDeleteEntryCommandBase):

    def __init__(self, zblogpublisher, zdocstore, zaccount, zblog, zblogDocument, bDeleteLocalEntry):
        ZCreateUpdateDeleteEntryCommandBase.__init__(self,  u"deleteEntry", zblogpublisher, zdocstore, zaccount, zblog, zblogDocument) #$NON-NLS-1$
        self.deleteLocalEntry = bDeleteLocalEntry
    # end __init__()

    def setDeleteLocalEntry(self, deleteLocalEntry):
        self.deleteLocalEntry = deleteLocalEntry
    # end setDeleteLocalEntry()

    def _isDeleteLocalEntry(self):
        return self.deleteLocalEntry
    # end _isDeleteLocalEntry()

    def doCommand(self):
        # if published, then delete online doc.
        if self.zblogDocument.isPublished():
            self._notifyBegin(3)
            self._notifyActivity(_extstr(u"blogcommands.DeletingPostFromBlog") % self._getBlog().getName(), 1, True) #$NON-NLS-1$
            if self._deleteOnlineEntry():
                if not self.zblogDocument.isPublished():
                    self._notifyActivity(_extstr(u"blogcommands.DeletingLocalCopy"), 1, True) #$NON-NLS-1$
                    self._deleteLocalEntry()
            else:
                self._notifyActivity(_extstr(u"blogcommands.FailedToDeleteOnlinePost"), 1, True) #$NON-NLS-1$
        else:
            self._notifyBegin(2)
            self._notifyActivity(_extstr(u"blogcommands.DeletingLocalCopy"), 1, True) #$NON-NLS-1$
            self._deleteLocalEntry()
        self._notifyActivity(_extstr(u"blogcommands.PostDeleted"), 1, True) #$NON-NLS-1$
        self._notifyEnd()
    # end doCommand()

    def _deleteOnlineEntry(self):
        if self._getPublisher() is None or self.zblog is None:
            return False

        if self.isCancelled():
            # silent return if canceled
            return True
        deleted = False
        try:
            deleted = self._getPublisher().deleteEntry(self.zblog, self.zblogDocument)
        except ZBlogServerException, bse: #@UnusedVariable
            # ignore server errors for now. (e.g. post aleady deleted from server.
            if u"XMLRPC Fault" == bse.getType(): #$NON-NLS-1$
                deleted = True
                s = u"Delete post from server failed: blog-id:%s, doc-id:%s, error:%s" % (self.zblog.getId(), self.zblogDocument.getId(), bse.getDescription() )  #$NON-NLS-1$
                self._error(s)
            else:
                raise bse
        except Exception, e:
            raise e
        # remove blog and pub info
        if deleted:
            self.zblogDocument.removeBlogInfo(self.zblog.getId())
            self.docStore.saveDocument(self.zblogDocument)
        return deleted
    # end _deleteOnlineEntry()

    def _deleteLocalEntry(self):
        if not self._isDeleteLocalEntry() or self.isCancelled():
            return
        self.docStore.removeDocument(self.zblogDocument.getId())
    # end _deleteLocalEntry()

# end ZDeleteEntryCommand

