from zoundry.blogapp.services.mediastorage.mediastorageupload import ZUploadResponse
from zoundry.base.util.text.textutil import getSafeString
from zoundry.blogpub.fotobilder import ZFotoBilderServer
from zoundry.base.exceptions import ZException
from zoundry.blogapp.services.mediastorage.mediastorageprovider import ZStreamBasedMediaStorageProvider

# ------------------------------------------------------------------------------
# An LiveJournal photo bilder implementation of a media storage provider.
# ------------------------------------------------------------------------------
class ZLJFotoBilderStorageProvider(ZStreamBasedMediaStorageProvider):

    def __init__(self, properties):
        ZStreamBasedMediaStorageProvider.__init__(self, properties)
        self.fotobilderServer = None
    # end __init__()

    def _getPhotoBilderServer(self):
        if not self.fotobilderServer:
            url = None
            username = None
            password = None
            if u"url" in self.properties: #$NON-NLS-1$
                url = self.properties[u"url"] #$NON-NLS-1$

            if u"username" in self.properties: #$NON-NLS-1$
                username = self.properties[u"username"] #$NON-NLS-1$
            else:
                raise ZException(u"LJ FotoBilder account username is required.") #$NON-NLS-1$
            if u"password" in self.properties: #$NON-NLS-1$
                password = self.properties[u"password"] #$NON-NLS-1$
            else:
                raise ZException(u"LJ FotoBilder account password is required.") #$NON-NLS-1$
            self.fotobilderServer = ZFotoBilderServer(username, password, url)
        return self.fotobilderServer
    # end _getPhotoBilderServer()

    def _uploadStream(self, fileName, fileStream, metaData): #@UnusedVariable
        albumName = self._getAlbumName()
        if not albumName:
            raise ZException(u"LJ Fotobilder web album name is required.") #$NON-NLS-1$
        fotoBilderUploadResult = self._getPhotoBilderServer().uploadFile(fileStream, gallery=albumName)
        if fotoBilderUploadResult:
            if fotoBilderUploadResult.getUploadPicResponseNode():
                return ZUploadResponse(fotoBilderUploadResult.getUrl(), metaData=fotoBilderUploadResult.getUploadPicResponseNode())
            else:
                return ZUploadResponse(fotoBilderUploadResult.getUrl())
        else:
            raise ZException(u"LJ FotoBilder upload failed.") #$NON-NLS-1$
    # end _uploadStream

    def _getAlbumName(self):
        if u"albumName" in self.properties: #$NON-NLS-1$
            return getSafeString(self.properties[u"albumName"]) #$NON-NLS-1$
        return None
    # end _getAlbumName()

# end ZLJFotoBilderStorageProvider