from zoundry.blogapp.services.datastore.blogdocumentimpl import ZTagwordsSet
from pysqlite2 import dbapi2 as sqlite
from zoundry.appframework.global_services import getLoggerService
from zoundry.base.util.text.textutil import getNoneString
from zoundry.blogapp.services.docindex.indexeventsimpl import ZDocIndexDocumentAddEvent
from zoundry.blogapp.services.docindex.indexeventsimpl import ZDocIndexDocumentRemoveEvent
from zoundry.blogapp.services.docindex.indexeventsimpl import ZDocIndexImageAddEvent
from zoundry.blogapp.services.docindex.indexeventsimpl import ZDocIndexImageRemoveEvent
from zoundry.blogapp.services.docindex.indexeventsimpl import ZDocIndexLinkAddEvent
from zoundry.blogapp.services.docindex.indexeventsimpl import ZDocIndexLinkRemoveEvent
from zoundry.blogapp.services.docindex.indexeventsimpl import ZDocIndexTagAddEvent
from zoundry.blogapp.services.docindex.indexeventsimpl import ZDocIndexTagRemoveEvent
from zoundry.blogapp.services.docindex.indeximpl import ZDocumentIDO
from zoundry.blogapp.services.docindex.indeximpl import ZImageIDO
from zoundry.blogapp.services.docindex.indeximpl import ZLinkIDO
from zoundry.blogapp.services.docindex.indeximpl import ZPubDataIDO
from zoundry.blogapp.services.docindex.indeximpl import ZTagIDO
from zoundry.blogapp.services.docindex.indexprovider import IZIndexProvider
from zoundry.blogapp.services.docindex.providers.pysqlite.pysqlddl import PYSQL_DOCINDEX_DDL
from zoundry.blogapp.services.docindex.providers.pysqlite.pysqlddl import PYSQL_INDEX_VERSION
from zoundry.blogapp.services.docindex.providers.pysqlite.queryhandlers import ZDocumentIDOListQueryHandler
from zoundry.blogapp.services.docindex.providers.pysqlite.queryhandlers import ZImageIDOListQueryHandler
from zoundry.blogapp.services.docindex.providers.pysqlite.queryhandlers import ZLinkIDOListQueryHandler
from zoundry.blogapp.services.docindex.providers.pysqlite.queryhandlers import ZSingleItemQueryHandler
from zoundry.blogapp.services.docindex.providers.pysqlite.queryhandlers import ZTagIDOListQueryHandler
from zoundry.blogapp.services.docindex.providers.pysqlite.querysql import ZDocumentQueryBuilder
from zoundry.blogapp.services.docindex.providers.pysqlite.querysql import ZImageQueryBuilder
from zoundry.blogapp.services.docindex.providers.pysqlite.querysql import ZLinkQueryBuilder
from zoundry.blogapp.services.docindex.providers.pysqlite.querysql import ZTagQueryBuilder
from zoundry.base.util.text.unicodeutil import convertToUtf8
from zoundry.base.util.locking import ZMutex
import os
import time


# ------------------------------------------------------------------------------
# A connection pool for handling connecting to a PySQL database from multiple
# threads.
# ------------------------------------------------------------------------------
class ZPySQLConnectionFactory:

    def __init__(self, pathToDBFile):
        self.pathToDBFile = pathToDBFile
    # end __init__()

    def createConnection(self):
        return sqlite.connect(convertToUtf8(self.pathToDBFile))
    # end getConnection()

# end ZPySQLConnectionFactory


# ------------------------------------------------------------------------------
# A PySQL based implementation of an index provider.
# ------------------------------------------------------------------------------
class ZPySQLIndexProvider(IZIndexProvider):

    def __init__(self):
        self.userProfile = None
        self.dbLock = ZMutex(u"ZPySQLIndexProviderMTX") #$NON-NLS-1$
    # end __init__()

    def _lockDatabase(self):
        self.dbLock.acquire()
    # end _lockDatabase()

    def _unlockDatabase(self):
        self.dbLock.release()
    # end _unlockDatabase()

    def create(self, applicationModel):
        self.userProfile = applicationModel.getUserProfile()
        self.dataStoreDirectory = self.userProfile.getDirectory(u"datastore") #$NON-NLS-1$
        self.indexFile = os.path.join(self.dataStoreDirectory, u"index.db") #$NON-NLS-1$
        self.connectionFactory = ZPySQLConnectionFactory(self.indexFile)

        if not os.path.isfile(self.indexFile):
            self._createNewIndex()
    # end create()

    def clear(self):
        self._createNewIndex()
    # end clear()

    def findDocuments(self, documentFilter):
        queryBuilder = ZDocumentQueryBuilder(documentFilter)
        sql = queryBuilder.build()
        return self._select(sql, None, ZDocumentIDOListQueryHandler())
    # end findDocuments()

    def findLinks(self, linkFilter):
        queryBuilder = ZLinkQueryBuilder(linkFilter)
        sql = queryBuilder.build()
        return self._select(sql, None, ZLinkIDOListQueryHandler())
    # end findLinks()

    def findTags(self, tagFilter):
        queryBuilder = ZTagQueryBuilder(tagFilter)
        sql = queryBuilder.build()
        return self._select(sql, None, ZTagIDOListQueryHandler())
    # end findTags()

    def findImages(self, imageFilter):
        queryBuilder = ZImageQueryBuilder(imageFilter)
        sql = queryBuilder.build()
        return self._select(sql, None, ZImageIDOListQueryHandler())
    # end findImages()

    def getDocumentCount(self, filter):
        queryBuilder = ZDocumentQueryBuilder(filter)
        sql = queryBuilder.build(True)
        return self._select(sql, None, ZSingleItemQueryHandler())
    # end getDocumentCount()

    def getTagCount(self, filter):
        queryBuilder = ZTagQueryBuilder(filter)
        sql = queryBuilder.build(True)
        return self._select(sql, None, ZSingleItemQueryHandler())
    # end getTagCount()

    def getLinkCount(self, filter):
        queryBuilder = ZLinkQueryBuilder(filter)
        sql = queryBuilder.build(True)
        return self._select(sql, None, ZSingleItemQueryHandler())
    # end getLinkCount()

    def getImageCount(self, filter):
        queryBuilder = ZImageQueryBuilder(filter)
        sql = queryBuilder.build(True)
        return self._select(sql, None, ZSingleItemQueryHandler())
    # end getImageCount()

    def addDocument(self, document, listeners):
        self._lockDatabase()
        try:
            self._addDocument(document, listeners)
        finally:
            self._unlockDatabase()
    # end addDocument()

    def _addDocument(self, document, listeners):
        documentIDO = None
        pubDataIDOs = []
        linkIDOs = []
        imageIDOs = []
        tagIDOs = []

        connection = self._createConnection()
        try:
            # First, store the document itself.
            self._storeDocument(document, connection)
            documentIDO = self._createDocumentIDO(document)

            # Now write out the pub-info.
            blogInfoList = document.getBlogInfoList()
            for blogInfo in blogInfoList:
                self._storeBlogInfo(document.getId(), blogInfo, connection)
                pubDataIDO = self._createPubDataIDO(blogInfo)
                documentIDO.addPubDataIDO(pubDataIDO)
                pubDataIDOs.append(pubDataIDO)

            # Now write out the links, images and tags
            content = document.getContent()
            if content:
                xhtmlDoc = content.getXhtmlDocument()
                links = xhtmlDoc.getLinks()
                for link in links:
                    self._storeLink(document.getId(), link, connection)
                    linkIDOs.append(self._createLinkIDO(document, link, pubDataIDOs))

                images = xhtmlDoc.getImages()
                for image in images:
                    self._storeImage(document.getId(), image, connection)
                    imageIDOs.append(self._createImageIDO(document, image, pubDataIDOs))
            # end writing out the links and images

            # build a map of tags
            tagMap = self._getTagsMap(document)
            # write out the taxonomy.
            for (tagId, tag) in tagMap.iteritems():
                self._storeTag(document.getId(), tagId, tag, connection)
                tagIDOs.append( self._createTagIDO(document, tagId, tag, pubDataIDOs) )

            connection.commit()
        finally:
            connection.close()

        # Now, fire an "index changed" event for the document and each link and image IDO added to the index.
        self._fireIndexChangeEvent(listeners, ZDocIndexDocumentAddEvent, [documentIDO])
        self._fireIndexChangeEvent(listeners, ZDocIndexLinkAddEvent, linkIDOs)
        self._fireIndexChangeEvent(listeners, ZDocIndexImageAddEvent, imageIDOs)
        self._fireIndexChangeEvent(listeners, ZDocIndexTagAddEvent, tagIDOs)
    # end addDocument()

    def _getTagsMap(self, document):
        # temp list containing tag and category strings
        tags = []
        # Collect list of tags from document meta data
        if document.getTagwordsList and document.getTagwordsList():
            wordSet = ZTagwordsSet()
            wordSet.addZTagwordObjectList( document.getTagwordsList() )
            tags.extend( wordSet.getTagwords() )

        # Get document (blog info) categories for tags/taxanomy.
        if document.getBlogInfoList and document.getBlogInfoList():
            for blogInfo in document.getBlogInfoList():
                for category in blogInfo.getCategories():
                    tags.append( category.getName() )

        # Also use document (pub meta data) categories for tags/taxanomy.
        if document.getPubMetaDataList and document.getPubMetaDataList():
            for metaData in document.getPubMetaDataList(): #@UnusedVariable
                pass # FIXME (PJ) add meta data categories?  Same as blog infor categories?


        # get list of tags found in xhtml content document embedded in links with rel = tag
        if document.getContent() and document.getContent().getXhtmlDocument():
            tagwordsInLinks = document.getContent().getXhtmlDocument().getTagwords()
            if tagwordsInLinks:
                tags.extend(tagwordsInLinks)

        # build a map of tags to eliminate duplicates
        # map key: tagId, value: tag word
        tagMap = {}
        for tag in tags:
            tagId = tag.lower().strip().replace(u" ", u"_") #$NON-NLS-1$ #$NON-NLS-2$
            tagId = tagId.replace(u"'", u"_") #$NON-NLS-1$ #$NON-NLS-2$
            tagId = tagId.replace(u'"', u"_") #$NON-NLS-1$ #$NON-NLS-2$
            if not tagId:
                continue
            if not tagMap.has_key(tagId):
                tagMap[tagId] = tag.strip()
        return tagMap

    def updateDocument(self, document, listeners):
        self._lockDatabase()
        try:
            self._updateDocument(document, listeners)
        finally:
            self._unlockDatabase()
    # end updateDocument()

    def _updateDocument(self, document, listeners):
        docId = document.getId()
        # FIXME (EPW) change to actually update the document, rather than remove/add
        self._removeDocument(docId, listeners)
        self._addDocument(document, listeners)
    # end _updateDocument()

    def removeDocument(self, docId, listeners):
        self._lockDatabase()
        try:
            self._removeDocument(docId, listeners)
        finally:
            self._unlockDatabase()
    # end removeDocument()

    def _removeDocument(self, docId, listeners):
        # Get the IDOs being removed (for event firing purposes)
        connection = self._createConnection()
        # FIXME (EPW) remove these if not needed (since pySQL cascade/trigger is used).
        documentIDOs = self._getDocumentIDO(docId, connection)
        linkIDOs = self._getLinkIDOs(docId, connection)
        imageIDOs = self._getImageIDOs(docId, connection)
        tagIDOs = self._getTagIDOs(docId, connection)

        try:
            self._delete(u"DELETE FROM Document WHERE Document.DocumentId = ?", [ docId ], connection) #$NON-NLS-1$
            connection.commit()
        finally:
            connection.close()

        # Now, fire an "index changed" event for the document and each link and image IDO removed
        self._fireIndexChangeEvent(listeners, ZDocIndexDocumentRemoveEvent, documentIDOs)
        self._fireIndexChangeEvent(listeners, ZDocIndexLinkRemoveEvent, linkIDOs)
        self._fireIndexChangeEvent(listeners, ZDocIndexImageRemoveEvent, imageIDOs)
        self._fireIndexChangeEvent(listeners, ZDocIndexTagRemoveEvent, tagIDOs)
    # end _removeDocument()

    def getNumDocuments(self):
        return self._select(u"SELECT count(DocumentId) FROM Document", None, ZSingleItemQueryHandler()) #$NON-NLS-1$
    # end getNumDocuments()

    def requiresReindex(self):
        providerVersion = self._getProviderVersion()
        dbVersion = self._getDBVersion()
        return providerVersion != dbVersion
    # end requiresReindex()

    def destroy(self):
        pass
    # end destroy()

    def _createConnection(self):
        return self.connectionFactory.createConnection()
    # end _createConnection()

    def _createNewIndex(self):
        self._lockDatabase()
        try:
            if os.path.exists(self.indexFile):
                os.remove(self.indexFile)
            self._createDB()
        finally:
            self._unlockDatabase()
    # end _createNewIndex()

    def _createDB(self):
        connection = self._createConnection()
        try:
            cursor = connection.cursor()
            try:
                cursor.executescript(PYSQL_DOCINDEX_DDL)
                connection.commit()
            finally:
                cursor.close()
            cursor.close()
        finally:
            connection.close()
    # end _createDB()

    def _getProviderVersion(self):
        return PYSQL_INDEX_VERSION
    # end _getProviderVersion()

    def _getDBVersion(self):
        return self._select(u"SELECT Value FROM MetaData WHERE Name = 'Version'", None, ZSingleItemQueryHandler()) #$NON-NLS-1$
    # end _getDBVersion()

    def _storeDocument(self, document, connection):
        params = [
              document.getId(),
              document.getTitle(),
              getNoneString(document.getCreationTime()),
              getNoneString(document.getLastModifiedTime())
        ]
        self._insert(u"INSERT INTO Document (DocumentId, Title, CreationTime, LastModifiedTime) values (?, ?, ?, ?)", params, connection) #$NON-NLS-1$
    # end _storeDocument()

    def _storeBlogInfo(self, documentId, blogInfo, connection):
        pubInfo = blogInfo.getPublishInfo()
        draft = 0
        if pubInfo.isDraft():
            draft = 1
        params = [
              documentId,
              blogInfo.getAccountId(),
              blogInfo.getBlogId(),
              pubInfo.getBlogEntryId(),
              getNoneString(pubInfo.getPublishedTime()),
              getNoneString(pubInfo.getSynchTime()),
              draft,
              pubInfo.getUrl()
        ]
        self._insert(u"INSERT INTO PublishedData (DocumentId, AccountId, BlogId, BlogEntryId, IssuedTime, SynchTime, Draft, Permalink) values (?, ?, ?, ?, ?, ?, ?, ?)", params, connection) #$NON-NLS-1$
    # end _storeBlogInfo()

    def _createPubDataIDO(self, blogInfo):
        pubInfo = blogInfo.getPublishInfo()
        accountId = blogInfo.getAccountId()
        blogId = blogInfo.getBlogId()
        blogEntryId = pubInfo.getBlogEntryId()
        issuedTime = pubInfo.getPublishedTime()
        synchTime = pubInfo.getSynchTime()
        draft = pubInfo.isDraft()
        permaLink = pubInfo.getUrl()

        return ZPubDataIDO(accountId, blogId, blogEntryId, issuedTime, synchTime, draft, permaLink)
    # end _createPubDataIDO()

    # Creates a ZDocumentIDO object from the IZDocument and pub data IDO objects.
    def _createDocumentIDO(self, document):
        id = document.getId()
        title = document.getTitle()
        creationTime = document.getCreationTime()
        lastModifiedTime = document.getLastModifiedTime()

        return ZDocumentIDO(None, id, title, creationTime, lastModifiedTime)
    # end _createDocumentIDO()

    def _storeLink(self, documentId, link, connection):
        url = link.getUrl()
        params = [
              documentId,
              url.toString(),
              url.getHost(),
              url.getPath(),
              link.getRel(),
              link.getTitle(),
              link.getText(),
              link.getHitCount()
        ]
        self._insert(u"INSERT INTO Link (DocumentId, Url, Host, Path, Rel, Title, Content, HitCount) values (?, ?, ?, ?, ?, ?, ?, ?)", params, connection) #$NON-NLS-1$
    # end _storeLink()

    def _createLinkIDO(self, document, link, pubDataIDOs):
        url = link.getUrl()
        return ZLinkIDO(pubDataIDOs, document.getId(), url.toString(), url.getHost(), url.getPath(), link.getRel(), link.getTitle(), link.getText())
    # end _createLinkIDO()

    def _storeImage(self, documentId, image, connection):
        url = image.getUrl()
        params = [
              documentId,
              url.toString(),
              url.getHost(),
              url.getPath(),
              image.getTitle(),
              image.getHitCount()
        ]
        self._insert(u"INSERT INTO Image (DocumentId, Url, Host, Path, Title, HitCount) values (?, ?, ?, ?, ?, ?)", params, connection) #$NON-NLS-1$
    # end _storeImage()

    def _createImageIDO(self, document, image, pubDataIDOs):
        url = image.getUrl()
        return ZImageIDO(pubDataIDOs, document.getId(), url.toString(), url.getHost(), url.getPath(), image.getTitle())
    # end _createImageIDO()

    def _storeTag(self, documentId, tagId, tag, connection):
        params = [
              documentId,
              tagId,
              tag
        ]
        self._insert(u"INSERT INTO Tag (DocumentId, TagId, TagWord) values (?, ?, ?)", params, connection) #$NON-NLS-1$
    # end _storeTag()

    def _createTagIDO(self, document, tagId, tag, pubDataIDOs):
        ido = ZTagIDO(pubDataIDOs, document.getId(), tagId, tag)
        return ido
    # end _createTagIDO()

    def _getDocumentIDO(self, docId, connection):
        return self._select(u"SELECT * FROM Document AS doc LEFT JOIN PublishedData AS pd ON doc.DocumentId = pd.DocumentId WHERE doc.DocumentId = ?", [ docId ], ZDocumentIDOListQueryHandler(), connection) #$NON-NLS-1$
    # end _getDocumentIDO()

    def _getLinkIDOs(self, docId, connection):
        return self._select(u"SELECT * FROM Link AS link LEFT JOIN PublishedData AS pd ON link.DocumentId = pd.DocumentId WHERE link.DocumentId = ?", [ docId ], ZLinkIDOListQueryHandler(), connection) #$NON-NLS-1$
    # end _getLinkIDOs()

    def _getImageIDOs(self, docId, connection):
        return self._select(u"SELECT * FROM Image AS image LEFT JOIN PublishedData AS pd ON image.DocumentId = pd.DocumentId WHERE image.DocumentId = ?", [ docId ], ZImageIDOListQueryHandler(), connection) #$NON-NLS-1$
    # end _getImageIDOs()

    def _getTagIDOs(self, docId, connection):
        return self._select(u"SELECT * FROM Tag AS tag WHERE tag.DocumentId = ?", [ docId ], ZTagIDOListQueryHandler(), connection) #$NON-NLS-1$
    # end _getTagIDOs()

    # Fires an 'onIndexChange' event to all the listeners.
    def _fireIndexChangeEvent(self, listeners, eventClass, IDOs):
        for ido in IDOs:
            for listener in listeners:
                try:
                    listener.onIndexChange(eventClass(ido))
                except Exception, e:
                    getLoggerService().exception(e)
    # end _fireIndexChangeEvent

    # Issues a SQL select statement, handles and then returns the result.  The handler variable
    # should be an instance of IZQueryHandler.
    def _select(self, sql, params, handler, connection = None):
        start = time.time()
        execTime = -1
        fetchTime = -1
        shouldCloseConn = False

        # Create a connection if none was included.  Also lock the DB if we are creating
        # a connection.
        if connection is None:
            connection = self._createConnection()
            self._lockDatabase()
            shouldCloseConn = True

        try:
            cursor = connection.cursor()
            try:
                if params is None:
                    params = []
                cursor.execute(sql, params)
                execTime = time.time()
                rows = cursor.fetchall()
                fetchTime = time.time()
                return handler.handle(rows)
            finally:
                cursor.close()
        finally:
            if shouldCloseConn:
                try:
                    connection.close()
                finally:
                    self._unlockDatabase()
            end = time.time()
            self._logSelectQueryTimings(sql, start, execTime, fetchTime, end)
    # end _select()

    # Locks the DB, but only if a connection was NOT included.
    def _insert(self, sql, params, connection = None):
        start = time.time()
        execTime = -1

        shouldCloseConn = False

        # Create a connection if none was included.  Also lock the DB if we are creating
        # a connection.
        if connection is None:
            connection = self._createConnection()
            shouldCloseConn = True
            self._lockDatabase()

        try:
            cursor = connection.cursor()
            try:
                cursor.execute(sql, params)
                execTime = time.time()
            finally:
                cursor.close()
        finally:
            if shouldCloseConn:
                try:
                    connection.close()
                finally:
                    self._unlockDatabase()
            end = time.time()
        self._logInsertTimings(sql, start, execTime, end)
    # end _insert()

    # Locks the DB, but only if a connection was NOT included.
    def _delete(self, sql, params, connection = None):
        start = time.time()
        execTime = -1

        shouldCloseConn = False

        # Create a connection if none was included.  Also lock the DB if we are creating
        # a connection.
        if connection is None:
            connection = self._createConnection()
            shouldCloseConn = True
            self._lockDatabase()

        try:
            cursor = connection.cursor()
            try:
                cursor.execute(sql, params)
                execTime = time.time()
            finally:
                cursor.close()
        finally:
            if shouldCloseConn:
                try:
                    connection.close()
                finally:
                    self._unlockDatabase()
            end = time.time()
        self._logDeleteTimings(sql, start, execTime, end)
    # end _delete()

    def optimize(self):
        start = time.time()

        self._lockDatabase()
        try:
            connection = self._createConnection()
            try:
                cursor = connection.cursor()
                try:
                    cursor.execute(u"ANALYZE", []) #$NON-NLS-1$
                finally:
                    cursor.close()
            finally:
                connection.close()
        finally:
            self._unlockDatabase()
            end = time.time()
            self._logAnalyzeTimings(start, end)
    # end optimize()

    def _logSelectQueryTimings(self, sql, startTime, execTime, fetchTime, endTime):
        total = unicode(round((endTime - startTime) * 1000))
        execute = unicode(round((execTime - startTime) * 1000))
        fetch = unicode(round((fetchTime - execTime) * 1000))
        handle = unicode(round((endTime - fetchTime) * 1000))
        getLoggerService().debug(u"SQLSELECT (total=%s :: exec=%s, fetch=%s, handle=%s): %s" % (total, execute, fetch, handle, sql)) #$NON-NLS-1$
    # end _logSelectQueryTimings()

    def _logInsertTimings(self, sql, startTime, execTime, endTime):
        total = unicode(round((endTime - startTime) * 1000))
        execute = unicode(round((execTime - startTime) * 1000))
        getLoggerService().debug(u"SQLINSERT (total=%s :: exec=%s): %s" % (total, execute, sql)) #$NON-NLS-1$
    # end _logInsertTimings()

    def _logDeleteTimings(self, sql, startTime, execTime, endTime):
        total = unicode(round((endTime - startTime) * 1000))
        execute = unicode(round((execTime - startTime) * 1000))
        getLoggerService().debug(u"SQLDELETE (total=%s :: exec=%s): %s" % (total, execute, sql)) #$NON-NLS-1$
    # end _logDeleteTimings()

    def _logAnalyzeTimings(self, startTime, endTime):
        total = unicode(round((endTime - startTime) * 1000))
        getLoggerService().debug(u"SQLANALYZE (total=%s)" % total) #$NON-NLS-1$
    # end _logAnalyzeTimings()

# end ZPySQLIndexProvider
