from zoundry.appframework.constants import IZAppServiceIDs
from zoundry.appframework.engine.service import IZService
from zoundry.base.util import guid
from zoundry.base.util.collections import ZListenerSet
from zoundry.base.util.fileutil import getDirectoryListing
from zoundry.base.util.schematypes import ZSchemaDateTime
from zoundry.blogapp.services.datastore.dataio import loadDocument
from zoundry.blogapp.services.datastore.dataio import saveDocument
import os


# ------------------------------------------------------------------------------
# A filter function for use in the getDirectoryListing() method.  This will
# return true only for *.rbe.xml files.
# ------------------------------------------------------------------------------
def documentXmlFilter(path):
    return os.path.isfile(path) and path.endswith(u".rbe.xml") #$NON-NLS-1$
# end documentXmlFilter()


# ------------------------------------------------------------------------------
# The data store listener.  This interface defines the callbacks that the
# datastore will make to any listener of it.
# ------------------------------------------------------------------------------
class IZDataStoreListener:

    def onDocumentAdded(self, document):
        u"Called when a document is added to the store." #$NON-NLS-1$
    # end onDocumentAdded()

    def onDocumentChanged(self, document, metaDataOnly):
        u"Called when a specific document has changed." #$NON-NLS-1$
    # end onDocumentChanged()

    def onDocumentDeleted(self, document):
        u"Called when a specific document has been deleted." #$NON-NLS-1$
    # end onDocumentDeleted()

# end IZDataStoreListener


# ------------------------------------------------------------------------------
# The data store's public interface.
# ------------------------------------------------------------------------------
class IZDataStore(IZService):

    def addListener(self, listener):
        u"Adds the given listener." #$NON-NLS-1$
    # end addListener()

    def removeListener(self, listener):
        u"Removes the listener." #$NON-NLS-1$
    # end removeListener()

    def addDocument(self, document):
        u"Adds the given document to the store." #$NON-NLS-1$
    # end addDocument()

    def getDocument(self, docId):
        u"Gets the document with the given document id." #$NON-NLS-1$
    # end getDocument()

    def exists(self, docId):
        u"Returns True if document (given id) exists." #$NON-NLS-1$
    # end exists()

    def getDocumentIDs(self):
        u"Gets a list of all document IDs." #$NON-NLS-1$
    # end getDocumentIDs()

    def saveDocument(self, document, metaDataOnly = False):
        u"Saves the given document to disk." #$NON-NLS-1$
    # end saveDocument()

    def removeDocument(self, docId):
        u"Removes the given document from the store." #$NON-NLS-1$
    # end removeDocument

    def getNumDocuments(self):
        u"Gets the total number of documents in the store." #$NON-NLS-1$
    # end getNumDocuments()

# end ZDataStore


# ------------------------------------------------------------------------------
# This is an implementation of the Zoundry DataStore Service.  The data store
# is responsible for handling all Blog Post related I/O.  Each blog post is a
# document in the data store.  The data store can be listened to for changes
# to the documents.  The data store can also be queried for specific document
# and for an iterator over all documents.  Note that iterating over all
# documents is frowned upon - you should instead use the ZDataStoreIndex service
# to find multiple documents.
# ------------------------------------------------------------------------------
class ZDataStore(IZDataStore):

    def __init__(self):
        self.listeners = ZListenerSet()
    # end __init__()

    def start(self, applicationModel):
        self.logger = applicationModel.getEngine().getService(IZAppServiceIDs.LOGGER_SERVICE_ID)
        self.dataStoreDirectory = applicationModel.getUserProfile().getDirectory(u"datastore") #$NON-NLS-1$
        self.logger.debug(u"Data Store started.") #$NON-NLS-1$
    # end start()

    def stop(self):
        pass
    # end stop()

    def addListener(self, listener):
        self.listeners.append(listener)
    # end addListener()

    def removeListener(self, listener):
        self.listeners.remove(listener)
    # end removeListener()

    def addDocument(self, document):
        if document.getId():
            self.saveDocument(document)
            return

        document.setId(guid.generate())
        if document.getCreationTime() is None:
            document.setCreationTime(ZSchemaDateTime())
        if document.getLastModifiedTime() is None:
            document.setLastModifiedTime(ZSchemaDateTime())

        documentXmlPath = self._getDocumentPath( document.getId() )
        saveDocument(document, documentXmlPath)
        self._fireDocumentAddedEvent(document)
    # end addDocument()

    def getDocument(self, docId):
        documentXmlPath = self._getDocumentPath( docId )
        return loadDocument(documentXmlPath)
    # end getDocument()

    def exists(self, docId):
        documentXmlPath = self._getDocumentPath( docId )
        return os.path.exists(documentXmlPath)
    # end exists()

    def getDocumentIDs(self):
        docXmlFilePaths = getDirectoryListing(self.dataStoreDirectory, documentXmlFilter)
        return map(self._getDocumentIDFromPath, docXmlFilePaths)
    # end getDocumentIDs()

    def saveDocument(self, document, metaDataOnly = False):
        if not document.getId():
            self.addDocument(document)
            return

        if not metaDataOnly:
            document.setLastModifiedTime(ZSchemaDateTime())

        documentXmlPath = self._getDocumentPath( document.getId() )
        saveDocument(document, documentXmlPath)
        self.logger.debug(u"Saved document id=%s" % document.getId()) #$NON-NLS-1$
        self._fireDocumentChangedEvent(document, metaDataOnly)
    # end saveDocument()

    def removeDocument(self, docId):
        documentXmlPath = self._getDocumentPath( docId )
        document = loadDocument(documentXmlPath)
        os.remove(documentXmlPath)
        self._fireDocumentDeletedEvent(document)
    # end removeDocument

    def getNumDocuments(self):
        return len(getDirectoryListing(self.dataStoreDirectory, documentXmlFilter))
    # end getNumDocuments()

    # Given a path to the document xml file, returns the ID of the document.
    def _getDocumentIDFromPath(self, path):
        return os.path.basename(path).split(u".")[0] #$NON-NLS-1$
    # end _getDocumentIDFromPath()

    def _getDocumentPath(self, docId):
        u"""_getDocumentPath(string) -> string
        Returns file path given document id."""  #$NON-NLS-1$
        documentXmlPath = os.path.join(self.dataStoreDirectory, docId + u".rbe.xml") #$NON-NLS-1$
        return documentXmlPath
    # end _getDocumentPath

    def _fireDocumentAddedEvent(self, document):
        for listener in self.listeners:
            try:
                self.logger.debug(u"Firing doc added event to handler: %s" % unicode(listener)) #$NON-NLS-1$
                listener.onDocumentAdded(document)
            except Exception, e:
                self.logger.exception(e)
        self.logger.debug(u"Done firing doc added event.") #$NON-NLS-1$
    # end  _fireDocumentAddedEvent

    def _fireDocumentChangedEvent(self, document, metaDataOnly):
        for listener in self.listeners:
            try:
                self.logger.debug(u"Firing doc change event to handler: %s" % unicode(listener)) #$NON-NLS-1$
                listener.onDocumentChanged(document, metaDataOnly)
            except Exception, e:
                self.logger.exception(e)
        self.logger.debug(u"Done firing doc change event.") #$NON-NLS-1$
    # end _fireDocumentChangedEvent

    def _fireDocumentDeletedEvent(self, document):
        for listener in self.listeners:
            try:
                self.logger.debug(u"Firing doc deleted event to handler: %s" % unicode(listener)) #$NON-NLS-1$
                listener.onDocumentDeleted(document)
            except Exception, e:
                self.logger.exception(e)
        self.logger.debug(u"Done firing doc deleted event.") #$NON-NLS-1$
    # end _fireDocumenttDeletedEvent

# end ZDataStore
