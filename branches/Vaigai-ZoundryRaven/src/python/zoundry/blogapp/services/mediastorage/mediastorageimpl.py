from zoundry.base.util.fileutil import getFileExtension
from zoundry.base.util.fileutil import getFileMetaData
from zoundry.base.util.text.textutil import getSafeString
from zoundry.base.util.text.textutil import sanitizeFileName
from zoundry.blogapp.services.mediastorage.mediastorage import IZMediaStorage
from zoundry.blogapp.services.mediastorage.mediastorage import IZMediaStorageUploadListener
from zoundry.blogapp.services.mediastorage.mediastoragereg import ZMediaStorageRegistry


# ----------------------------------------------------------------------------------------------
# A concrete implementation of a media storage.  This class encapsulates the meta data found in
# the plugin XML, in addition to managing the store provider.
# ----------------------------------------------------------------------------------------------
class ZMediaStorage(IZMediaStorage):

    def __init__(self, id, name, mediaSiteId, properties):
        self.id = id
        self.name = name
        self.mediaSiteId = mediaSiteId
        self.properties = properties
        self.registry = None
        self.site = None
        self.storeType = None
        self.provider = None
        # FIXME (PJ) extern these file extensions to the plugin xml
        self.imgExtensions = u"bmp,gif,jpeg,jpg,png".split(u",") #$NON-NLS-1$ #$NON-NLS-2$
        self.movExtensions = u"avi,mov,mp4,mpg,wmv,mpeg".split(u",") #$NON-NLS-1$ #$NON-NLS-2$        
    # end __init__()

    def init(self, site, storeType, registryFile):
        self.site = site
        self.storeType = storeType
        self.registry = ZMediaStorageRegistry(registryFile)
        self.provider = self._createProvider()
    # end init()

    def getId(self):
        return self.id
    # end getId()

    def getName(self):
        return self.name
    # end getName()

    def getMediaSiteId(self):
        return self.mediaSiteId
    # end getMediaSiteId()

    def getProperties(self):
        return self.properties
    # end getProperties()

    def getCapabilities(self):
        return self.site.getCapabilities()
    # end getCapabilities()

    def upload(self, fileName, listener = None, bypassRegistry = False):
        if listener is None:
            listener = IZMediaStorageUploadListener()
        uploadResponse = None
        (shortName, filePath, size, timestamp) = getFileMetaData(fileName)
        shortName = sanitizeFileName(shortName)
        listener.onUploadStarted(fileName, size)
        try:
            if not bypassRegistry and self.registry.hasFile(filePath, size, timestamp):
                listener.onUploadChunk(fileName, size)
                uploadResponse = self.registry.getUploadResponse(filePath)
            else:
                metaData = self.registry.getMetaData(filePath)
                uploadResponse = self.provider.uploadFile(shortName, filePath, listener, metaData)
                if uploadResponse is not None:
                    self.registry.addFileEntry(filePath, size, timestamp, uploadResponse)
            listener.onUploadComplete(fileName)
        except Exception, e:
            listener.onUploadFailed(fileName, e)
            listener.onUploadComplete(fileName)
            raise e
        return uploadResponse
    # end upload()
    
    def delete(self, fileName):
        (shortName, filePath, size, timestamp) = getFileMetaData(fileName)
        if not self.registry.hasFile(filePath, size, timestamp):
            return
        self.provider.deleteFile(shortName, self.registry.getMetaData(filePath))
        self.registry.removeFile(filePath)
    # end delete()

    def listFiles(self, relativePath = None):
        return self.provider.listFiles(relativePath)
    # end listFiles()

    def supportsFile(self, fileName): #@UnusedVariable
        ext = getSafeString( getFileExtension(fileName) ).lower()
        # for image upload, store must support image types or all types
        if ext and ext in self.imgExtensions and self.getCapabilities().supportsImageFiles():
            return True
        # for video upload, store must support video file types or all types
        if ext and ext in self.movExtensions and self.getCapabilities().supportsVideoFiles():
            return True        
        #default case - must support anytype
        return self.getCapabilities().supportsAnyFile()
    # end supportsFile()

    def _createProvider(self):
        providerClass = self.storeType.getClass()
        return providerClass(self.properties)
    # end _createProvider()

# end ZMediaStorageBase
