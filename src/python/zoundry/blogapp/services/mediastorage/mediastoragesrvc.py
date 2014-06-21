import time
from zoundry.appframework.constants import IZAppServiceIDs
from zoundry.appframework.engine.service import IZService
from zoundry.base.util.collections import ZListenerSet
from zoundry.base.util.fileutil import deleteFile
from zoundry.base.util.fileutil import getDirectoryListing
from zoundry.base.util.guid import generate
from zoundry.blogapp.constants import IZBlogAppExtensionPoints
from zoundry.blogapp.exceptions import ZBlogAppException
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.services.mediastorage.mediasiteimpl import ZMediaSite
from zoundry.blogapp.services.mediastorage.mediastoragedefs import ZMediaSiteDef
from zoundry.blogapp.services.mediastorage.mediastoragedefs import ZMediaStorageTypeDef
from zoundry.blogapp.services.mediastorage.mediastorageimpl import ZMediaStorage
from zoundry.blogapp.services.mediastorage.mediastorageio import loadMediaStorage
from zoundry.blogapp.services.mediastorage.mediastorageio import saveMediaStorage
from zoundry.blogapp.services.mediastorage.mediastoragetypeimpl import ZMediaStorageType
import os


# ---------------------------------------------------------------------------------------
# A getDirectoryListing filter that will return only *.store files.
# ---------------------------------------------------------------------------------------
def STORE_FILE_FILTER(path):
    return path.endswith(u".store") #$NON-NLS-1$
# end STORE_FILE_FILTER()


# ---------------------------------------------------------------------------------------
# Interface implemented by Media Storage Service listeners.
# ---------------------------------------------------------------------------------------
class IZMediaStorageServiceListener:

    def onMediaStorageAdded(self, mediaStore):
        u"Called when a media storage is added." #$NON-NLS-1$
    # end onMediaStorageAdded()

    def onMediaStorageRemoved(self, mediaStore):
        u"Called when a media storage is removed." #$NON-NLS-1$
    # end onMediaStorageRemoved() #$NON-NLS-1$

# end IZMediaStorageServiceListener


# -------------------------------------------------------------------------------------
# The interface that the media uploader service implements.
# -------------------------------------------------------------------------------------
class IZMediaStorageService(IZService):

    def addListener(self, listener):
        u"Adds a listener to the service." #$NON-NLS-1$
    # end addListener()

    def removeListener(self, listener):
        u"Removes the listener from the service." #$NON-NLS-1$
    # end removeListener()

    def getMediaSite(self, mediaSiteId):
        u"Returns a single IZMediaSite by ID." #$NON-NLS-1$
    # end getMediaSite()

    def getMediaSites(self):
        u"Returns a list of all IZMediaSites." #$NON-NLS-1$
    # end getMediaSites()

    def getMediaStorageById(self, mediaStoreId):
        u"Returns a single IZMediaStorage by its ID." #$NON-NLS-1$
    # end getMediaStorageById()

    def getMediaStorageByName(self, name):
        u"Returns a single IZMediaStorage by its name." #$NON-NLS-1$
    # end getMediaStorageByName()

    def getMediaStorages(self):
        u"Returns a list of all IZMediaStorages." #$NON-NLS-1$
    # end getMediaStorages()

    def hasMediaStorage(self, name):
        u"Returns true if there is already a media storage with the given name." #$NON-NLS-1$
    # end hasMediaStorage()
    
    def createStorageName(self, name):
        u"""Returns name if name does not exist otherwise creates a new uniqu
        store name by appending a number """ #$NON-NLS-1$
    # end createStorageName()
    
    def createMediaStorage(self, name, mediaSiteId, properties, persist = True):
        u"Creates a new media storage and adds it to the service." #$NON-NLS-1$
    # end createMediaStorage()

    def saveMediaStorage(self, mediaStore):
        u"Called when a change is made to a media storage - this saves it to disk." #$NON-NLS-1$
    # end saveMediaStorage()

    def deleteMediaStorage(self, mediaStore):
        u"Deletes the given media storage." #$NON-NLS-1$
    # end deleteMediaStorage()

    def deleteMediaStorageById(self, mediaStoreId):
        u"Deletes the given media uploader by its ID." #$NON-NLS-1$
    # end deleteMediaStorageById()

    def deleteMediaStorageByName(self, name):
        u"Deletes the given media uploader by its name." #$NON-NLS-1$
    # end deleteMediaStorageByName()

# end IZMediaStorageService


# -------------------------------------------------------------------------------------
# The implementation of the media upload service.
# -------------------------------------------------------------------------------------
class ZMediaStorageService(IZMediaStorageService):

    def __init__(self):
        self.mediaStoreTypes = []
        self.mediaSites = []
        self.mediaStores = []
        self.mediaStoresDirectory = None
        self.listeners = ZListenerSet()
    # end __init__()

    def _getMediaStoragesDirectory(self):
        return self.applicationModel.getUserProfile().getDirectory(u"mediastorages") #$NON-NLS-1$
    # end _getMediaStoragesDirectory()

    def start(self, applicationModel):
        self.applicationModel = applicationModel
        self.logger = applicationModel.getEngine().getService(IZAppServiceIDs.LOGGER_SERVICE_ID)
        self.mediaStoresDirectory = self._getMediaStoragesDirectory()
        self.mediaStoreTypes = self._loadMediaStorageTypes()
        self.mediaSites = self._loadMediaSites()
        self.mediaStores = self._loadMediaStorages()

        for site in self.mediaSites:
            mediaStoreTypeId = site.getMediaStorageTypeId()
            mediaStoreType = self._getMediaStorageType(mediaStoreTypeId)
            if mediaStoreType is None:
                raise ZBlogAppException(_extstr(u"mediastoragesrvc.StoreTypeNotFoundError") % (site.getId(), mediaStoreTypeId)) #$NON-NLS-1$
            site.setMediaStorageType(mediaStoreType)

        self.logger.debug(u"Media Storage Service started [%d types, %d sites, %d storages loaded]." % (len(self.mediaStoreTypes), len(self.mediaSites), len(self.mediaStores))) #$NON-NLS-1$
    # end start()

    def stop(self):
        self.mediaStoreTypes = []
        self.mediaSites = []
        self.mediaStores = []
    # end stop()

    def addListener(self, listener):
        self.listeners.append(listener)
        self.logger.debug(u"Added Media Storage Service Listener: '%s'" % unicode(listener.__class__)) #$NON-NLS-1$
    # end addListener()

    def removeListener(self, listener):
        self.listeners.remove(listener)
        self.logger.debug(u"Removed Media Storage Service Listener: '%s'" % unicode(listener.__class__)) #$NON-NLS-1$
    # end removeListener()

    def getMediaSite(self, mediaSiteId):
        for site in self.mediaSites:
            if site.getId() == mediaSiteId:
                return site
        return None
    # end getMediaSite()

    def getMediaSites(self):
        rval = []
        for site in self.mediaSites:
            if not site.isInternal():
                rval.append(site)
        return rval
    # end getMediaSites()

    def getMediaStorageById(self, mediaStoreId):
        for uploader in self.mediaStores:
            if uploader.getId() == mediaStoreId:
                return uploader
        return None
    # end getMediaStorageById()

    def getMediaStorageByName(self, name):
        for uploader in self.mediaStores:
            if uploader.getName() == name:
                return uploader
        return None
    # end getMediaStorageByName()

    def getMediaStorages(self):
        return self.mediaStores
    # end getMediaStorages()

    def hasMediaStorage(self, name):
        return self.getMediaStorageByName(name) is not None
    # end hasMediaStorage()
    
    def createStorageName(self, name):
        if not self.hasMediaStorage(name):
            return name
        count = 1
        while count < 1000:
            newname = u"%s (%03d)" % (name, count) #$NON-NLS-1$
            if not self.hasMediaStorage(newname):
                return newname
            count = count + 1       
        newname = u"%s (%d)" % (name, int(time.time())) #$NON-NLS-1$
        return newname     
    # end createStorageName()
    

    def createMediaStorage(self, name, mediaSiteId, properties, persist = True):
        if self.hasMediaStorage(name):
            raise ZBlogAppException(_extstr(u"mediastoragesrvc.FailedToAddMediaStorageError") % name) #$NON-NLS-1$
        storage = self._createMediaStorage(name, mediaSiteId, properties)
        if persist:
            self.mediaStores.append(storage)
            self.saveMediaStorage(storage)
            self.logger.debug(u"Created a media storage named '%s' using site '%s'." % (name, mediaSiteId)) #$NON-NLS-1$
            for listener in self.listeners:
                listener.onMediaStorageAdded(storage)
        return storage
    # end createMediaStorage()

    def _createMediaStorage(self, name, mediaSiteId, properties):
        site = self.getMediaSite(mediaSiteId)
        if site is None:
            raise ZBlogAppException(_extstr(u"mediastoragesrvc.NoMediaSiteFound") % mediaSiteId) #$NON-NLS-1$
        id = generate()
        storageTypeId = site.getMediaStorageTypeId()
        storageType = self._getMediaStorageType(storageTypeId)
        storage = ZMediaStorage(id, name, mediaSiteId, properties)
        registryFile = os.path.join(self.mediaStoresDirectory, id + u".store.registry") #$NON-NLS-1$
        storage.init(site, storageType, registryFile)
        return storage
    # end _createMediaStorage()

    def saveMediaStorage(self, mediaStore):
        path = os.path.join(self.mediaStoresDirectory, mediaStore.getId() + u".store") #$NON-NLS-1$
        saveMediaStorage(mediaStore, path)
        self.logger.debug(u"Saved Media Storage: '%s'" % unicode(mediaStore.getName())) #$NON-NLS-1$
    # end saveMediaStorage()

    def deleteMediaStorageById(self, mediaStoreId):
        storage = self.getMediaStorageById(mediaStoreId)
        if storage is not None:
            self.deleteMediaStorage(storage)
    # end deleteMediaStorageById()

    def deleteMediaStorageByName(self, name):
        storage = self.getMediaStorageByName(name)
        if storage is not None:
            self.deleteMediaStorage(storage)
    # end deleteMediaStorageByName()

    def deleteMediaStorage(self, mediaStore):
        self.mediaStores.remove(mediaStore)
        path = os.path.join(self.mediaStoresDirectory, mediaStore.getId() + u".store") #$NON-NLS-1$
        deleteFile(path)
        registryPath = path + u".registry" #$NON-NLS-1$
        deleteFile(registryPath)
        self.logger.debug(u"Deleted a media storage named '%s'." % mediaStore.getName()) #$NON-NLS-1$
        for listener in self.listeners:
            listener.onMediaStorageRemoved(mediaStore)
    # end deleteMediaStorage()

    def _loadMediaStorageTypes(self):
        pluginRegistry = self.applicationModel.getPluginRegistry()
        extensions = pluginRegistry.getExtensions(IZBlogAppExtensionPoints.ZEP_ZOUNDRY_MEDIASTORE_TYPE)
        mediaTypeDefs = map(ZMediaStorageTypeDef, extensions)
        return map(ZMediaStorageType, mediaTypeDefs)
    # end _loadMediaStorageTypes()

    def _loadMediaSites(self):
        pluginRegistry = self.applicationModel.getPluginRegistry()
        extensions = pluginRegistry.getExtensions(IZBlogAppExtensionPoints.ZEP_ZOUNDRY_MEDIASTORE_SITE)
        mediaSiteDefs = map(ZMediaSiteDef, extensions)
        return map(ZMediaSite, mediaSiteDefs)
    # end _loadMediaSites()

    def _loadMediaStorages(self):
        storages = []

        storageFiles = getDirectoryListing(self.mediaStoresDirectory, STORE_FILE_FILTER)
        for storageFile in storageFiles:
            registryFile = storageFile + u".registry" #$NON-NLS-1$
            storage = self._loadMediaStorage(storageFile)
            mediaSiteId = storage.getMediaSiteId()
            site = self.getMediaSite(mediaSiteId)
            if site is None:
                raise ZBlogAppException(_extstr(u"mediastoragesrvc.NoMediaSiteFound") % mediaSiteId) #$NON-NLS-1$
            storageTypeId = site.getMediaStorageTypeId()
            storageType = self._getMediaStorageType(storageTypeId)
            storage.init(site, storageType, registryFile)
            storages.append(storage)

        return storages
    # end _loadMediaStorages()

    def _loadMediaStorage(self, storageFile):
        return loadMediaStorage(storageFile)
    # end _loadMediaStorage()

    def _getMediaStorageType(self, mediaStoreTypeId):
        for msType in self.mediaStoreTypes:
            if msType.getId() == mediaStoreTypeId:
                return msType
        return None
    # end _getMediaStorageType()

# end ZMediaStorageService
