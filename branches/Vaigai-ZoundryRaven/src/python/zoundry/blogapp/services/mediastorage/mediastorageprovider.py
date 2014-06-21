from zoundry.appframework.constants import IZAppServiceIDs
from zoundry.appframework.global_services import getApplicationModel
from zoundry.base.util.streamutil import IZStreamWrapperListener
from zoundry.base.util.streamutil import ZStreamWrapper
from zoundry.blogapp.exceptions import ZBlogAppException
from zoundry.blogapp.messages import _extstr

# -----------------------------------------------------------------------------------
# The interface that must be implemented by media storage providers.  A media storage
# provider is a concrete implementation of a media storage API such as FTP or Flickr.
# -----------------------------------------------------------------------------------
class IZMediaStorageProvider:

    def uploadFile(self, fileName, fullPath, listener, metaData):
        u"""uploadFile(string, string, IZMediaStorageUploadListener, ZElement) -> IZUploadResponse
        Called to upload a file to the remote media storage.  Returns the
        result of the upload as an IZUploadResponse.""" #$NON-NLS-1$
    # end upload()

    def deleteFile(self, fileName, metaData):
        u"Called to delete a file from the remote store." #$NON-NLS-1$
    # end deleteFile()

    def listFiles(self, relativePath = None):
        u"Called to get a listing of files at the remote location.  For the root listing, pass None." #$NON-NLS-1$
    # end listFiles()

# end IZMediaStorageProvider


# ------------------------------------------------------------------------------------------
# Simple base class for all media storage provider impls.
# ------------------------------------------------------------------------------------------
class ZBaseMediaStorageProvider(IZMediaStorageProvider):

    def __init__(self, properties):
        self.properties = properties
        self.logger = getApplicationModel().getEngine().getService(IZAppServiceIDs.LOGGER_SERVICE_ID)
    # end __init__()

    def _logDebug(self, s):
        if self.logger:
            self.logger.debug(s)
    # end _logDebug(()

    def _logWarning(self, s):
        if self.logger:
            self.logger.warning(s)
    # end _logWarning()

    def _logError(self, s):
        if self.logger:
            self.logger.error(s)
    # end _logError()

# end ZBaseMediaStorageProvider


# ------------------------------------------------------------------------------------------
# Base implementation of the provider for providers that need to work at the stream level.
# This class implements the uploadFile method
# to allow sub classes to work with streams via uploadStream adapter method.
# ------------------------------------------------------------------------------------------
class ZStreamBasedMediaStorageProvider(ZBaseMediaStorageProvider):

    def __init__(self, properties):
        ZBaseMediaStorageProvider.__init__(self, properties)
    # end __init__()

    def uploadFile(self, fileName, fullPath, listener, metaData):
        u"""Implements the method to adapt the file to a stream and delegate to
        _uploadStream(filename, fileStream) method.
        """  #$NON-NLS-1$
        try:
            file = open(fullPath, u"rb") #$NON-NLS-1$
            stream = ZStreamWrapper(file, ZStreamToUploadListenerAdapter(listener, fileName))
            try:
                return self._uploadStream(fileName, stream, metaData)
            finally:
                stream.close()
        except Exception, e:
            # FIXME (PJ) used key prefix mediastorageprovider
            raise ZBlogAppException(_extstr(u"mediastorageimpl.FailedToUploadFile") % fileName, e) #$NON-NLS-1$
    # end _uploadFile()

    def _uploadStream(self, fileName, fileStream, metaData): #@UnusedVariable
        u"""_uploadStream(string, stream, ZElement) -> IZUploadResponse
        Called to upload a file stream to the remote media storage.
        Returns the URL of the uploaded file.""" #$NON-NLS-1$
    # end _uploadStream()

# end ZStreamBasedMediaStorageProvider


# ----------------------------------------------------------------------------------------------
# Adapts a stream wrapper listener to a IZMediaStorageUploadListener.
# ----------------------------------------------------------------------------------------------
class ZStreamToUploadListenerAdapter(IZStreamWrapperListener):

    def __init__(self, uploadListener, fileName):
        self.uploadListener = uploadListener
        self.fileName = fileName
    # end __init__()

    def streamRead(self, blockSize, data): #@UnusedVariable
        self.uploadListener.onUploadChunk(self.fileName, blockSize)
    # end streamRead()

# end ZStreamToUploadListenerAdapter
