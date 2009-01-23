from zoundry.appframework.constants import IZAppServiceIDs
from zoundry.appframework.engine.service import IZService
from zoundry.appframework.global_services import getLoggerService
from zoundry.appframework.services.backgroundtask.backgroundtaskimpl import ZBackgroundTask
from zoundry.base.util.collections import ZListenerSet
from zoundry.base.util.zthread import IZRunnable
from zoundry.blogapp.constants import IZBlogAppServiceIDs
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.services.datastore.datastore import IZDataStoreListener
from zoundry.blogapp.services.docindex.providers.pysqlite.sqlprovider import ZPySQLIndexProvider

PROVIDER_TYPE_SQL = u"SQL" #$NON-NLS-1$


# ------------------------------------------------------------------------------
# The public interface implemented by the Document Index service.
# ------------------------------------------------------------------------------
class IZDocumentIndex:

    def findDocuments(self, filter):
        u"Returns a list of IZDocumentIDO objects that match the given filter." #$NON-NLS-1$
    # end findDocuments()

    def findTags(self, filter):
        u"Returns a list of IZTagIDO objects that match the given filter." #$NON-NLS-1$
    # end findTags()

    def findLinks(self, filter):
        u"Returns a list of IZLinkIDO objects that match the given filter." #$NON-NLS-1$
    # end findLinks()

    def findImages(self, filter):
        u"Returns a list of IZImageIDO objects that match the given filter." #$NON-NLS-1$
    # end findImages()

    def getDocumentCount(self, filter):
        u"Returns a count of the number of documents that match the given filter." #$NON-NLS-1$
    # end getDocumentCount()

    def getTagCount(self, filter):
        u"Returns a count of the number of tags that match the given filter." #$NON-NLS-1$
    # end getTagCount()

    def getLinkCount(self, filter):
        u"Returns a count of the number of links that match the given filter." #$NON-NLS-1$
    # end getLinkCount()

    def getImageCount(self, filter):
        u"Returns a count of the number of images that match the given filter." #$NON-NLS-1$
    # end getImageCount()

# end IZDocumentIndex


# ------------------------------------------------------------------------------
# This is the provider factory that the document index uses to create an index
# provider of the proper type.
# ------------------------------------------------------------------------------
class ZIndexProviderFactory:

    def __init__(self):
        self.type = PROVIDER_TYPE_SQL
        self.providers = {
              PROVIDER_TYPE_SQL : ZPySQLIndexProvider
        }
    # end __init__()

    def createIndexProvider(self):
        providerClass = self.providers[self.type]
        provider = providerClass()
        return provider
    # end createIndexProvider()

# end ZIndexProviderFactory
PROVIDER_FACTORY = ZIndexProviderFactory()


# ------------------------------------------------------------------------------
# A simple runnable class that will reindex all documents in the data store.
# ------------------------------------------------------------------------------
class ZReindexer(IZRunnable):

    def __init__(self, dataStore, docIndex):
        self.dataStore = dataStore
        self.docIndex = docIndex
    # end __init__()

    def run(self):
        docIDs = self.dataStore.getDocumentIDs()
        for docID in docIDs:
            getLoggerService().debug(u"Loading document %s." % docID) #$NON-NLS-1$
            document = self.dataStore.getDocument(docID)
            getLoggerService().debug(u"Indexing document %s." % docID) #$NON-NLS-1$
            self.docIndex.onDocumentAdded(document)
    # end run()

# end ZReindexer


# ------------------------------------------------------------------------------
# This is an implementation of a document index.  This service listens to the
# data store for changes and updates its internal index accordingly.  This
# service provides a way to quickly search through the data in the data store.
# ------------------------------------------------------------------------------
class ZDocumentIndex(IZService, IZDocumentIndex, IZDataStoreListener):

    def __init__(self):
        self.logger = None
        self.listeners = ZListenerSet()
        self.provider = None
    # end __init__()

    def start(self, applicationModel):
        self.logger = applicationModel.getEngine().getService(IZAppServiceIDs.LOGGER_SERVICE_ID)
        self.dataStore = applicationModel.getEngine().getService(IZBlogAppServiceIDs.DATA_STORE_SERVICE_ID)
        self.bgTaskService = applicationModel.getEngine().getService(IZBlogAppServiceIDs.BACKGROUND_TASK_SERVICE_ID)
        self.provider = PROVIDER_FACTORY.createIndexProvider()
        self.provider.create(applicationModel)

        needsReindex = False
        if self.provider.requiresReindex():
            self.logger.warning(u"Re-indexing documents because the provider requires it.") #$NON-NLS-1$
            needsReindex = True
        elif self.dataStore.getNumDocuments() != self.provider.getNumDocuments():
            self.logger.warning(u"Re-indexing documents because the number of documents in the data store does not match the number of documents in the provider.") #$NON-NLS-1$
            needsReindex = True

        # If a reindex is needed, then go ahead and create the reindex
        # background task and start it.  (dependency on the bg task service)
        if needsReindex:
            self.provider.clear()
            task = ZReindexTask()
            task.initializeTaskParams(self.dataStore, self)
            self.bgTaskService.addTask(task)
        else:
            self.provider.optimize()

        # Register as a listener of the data store
        self.dataStore.addListener(self)
        self.logger.debug(u"Document Index started.") #$NON-NLS-1$
    # end start()

    def stop(self):
        # Unregister as a listener of the data store
        self.dataStore.removeListener(self)

        self.provider.destroy()
        self.dataStore = None
        self.provider = None
    # end stop()

    def onReindexComplete(self):
        self.provider.optimize()
    # end onReindexComplete()

    def findDocuments(self, filter):
        return self.provider.findDocuments(filter)
    # end findDocuments()

    def findTags(self, filter):
        return self.provider.findTags(filter)
    # end findTags()

    def findLinks(self, filter):
        return self.provider.findLinks(filter)
    # end findLinks()

    def findImages(self, filter):
        return self.provider.findImages(filter)
    # end findImages()

    def getDocumentCount(self, filter):
        return self.provider.getDocumentCount(filter)
    # end getDocumentCount()

    def getTagCount(self, filter):
        return self.provider.getTagCount(filter)
    # end getTagCount()

    def getLinkCount(self, filter):
        return self.provider.getLinkCount(filter)
    # end getLinkCount()

    def getImageCount(self, filter):
        return self.provider.getImageCount(filter)
    # end getImageCount()

    def addListener(self, listener):
        self.listeners.append(listener)
    # end addListener()

    def removeListener(self, listener):
        self.listeners.remove(listener)
    # end removeListener()

    def onDocumentAdded(self, document):
        self.provider.addDocument(document, self.listeners)
    # end onDocumentAdded()

    def onDocumentChanged(self, document, metaDataOnly): #@UnusedVariable
        self.provider.updateDocument(document, self.listeners)
    # end onDocumentChange()

    def onDocumentDeleted(self, document):
        self.provider.removeDocument(document.getId(), self.listeners)
    # end onDocumentDeleted()

# end ZDocumentIndex


# --------------------------------------------------------------------------------------
# An impl of a background task for reindexing the documents in the doc store.
# --------------------------------------------------------------------------------------
class ZReindexTask(ZBackgroundTask):

    def __init__(self):
        ZBackgroundTask.__init__(self)

        self.customAttributes = {}
    # end __init__()

    def initializeTaskParams(self, dataStore, docIndex):
        self.dataStore = dataStore
        self.docIndex = docIndex

        self.docIDs = self.dataStore.getDocumentIDs()
        self.setName(_extstr(u"docindex.ReindexTask")) #$NON-NLS-1$
        self.setNumWorkUnits(len(self.docIDs) * 2)
    # end _initializeTaskParams()

    def getCustomAttributes(self):
        return self.customAttributes
    # end getCustomAttributes()

    def setCustomAttributes(self, attributeMap):
        self.customAttributes = attributeMap
    # end setCustomAttributes()

    def isResumable(self):
        return False
    # end isResumable()

    def _run(self):
        index = 0
        done = False
        while not self.stopped and not done:
            docID = self.docIDs[index]
            index = index + 1

            document = self.dataStore.getDocument(docID)
            self._incrementWork(_extstr(u"docindex.LoadedDocument") % unicode(docID)) #$NON-NLS-1$
            self.docIndex.onDocumentAdded(document)
            self._incrementWork(_extstr(u"docindex.ReindexedDocument") % unicode(docID)) #$NON-NLS-1$

            if index >= len(self.docIDs):
                done = True

        # Let the doc index know that the reindex is finished.
        self.docIndex.onReindexComplete()
    # end _run()

# end ZReindexTask
