from zoundry.base.util.text.textutil import getNoneString
from zoundry.appframework.global_services import getLoggerService
from zoundry.base.util.text.textutil import getSafeString
from zoundry.blogpub.atom.picasa import ZPicasaPhotoEntry
from zoundry.blogpub.atom.picasa import ZPicasaServer
from zoundry.base.exceptions import ZException
from zoundry.blogapp.services.mediastorage.mediastorageupload import ZUploadResponse
from zoundry.blogapp.services.mediastorage.mediastorageprovider import ZStreamBasedMediaStorageProvider



# ------------------------------------------------------------------------------
# Simple cache for web albums
# ------------------------------------------------------------------------------
class ZPicasaAlbumCache:

    def __init__(self):
        self.albumList = []
    # end __init__()

    def hasAlbums(self):
        return len(self.albumList) > 0
    # end hasAlbums()

    def getAlbumByName(self, albumName):
        # return ZPicasaAlbumEntry if found or None otherwise
        # first search by title, case sensitive
        for album in self.albumList:
            name = album.getTitle()
            if name == albumName:
                return album
        # case-insensitive title search
        albumName2 = albumName.lower()
        for album in self.albumList:
            name = album.getTitle()
            name = name.lower()
            if name == albumName2:
                return album
        # search by album name
        for album in self.albumList:
            name = album.getAlbumName()
            if name == albumName:
                return album
        # case-insensitive search
        albumName2 = albumName.lower()
        for album in self.albumList:
            name = album.getAlbumName()
            name = name.lower()
            if name == albumName2:
                return album
        return None
    # end getAlbumByName

    def addAlbum(self, album):
        self.albumList.append(album)
    # end addAlbum

    def addAlbumList(self, albumList):
        self.albumList.extend(albumList)
    # end addAlbumList
# end ZPicasaAlbumCache

G_PICASA_ALBUM_CACHE = ZPicasaAlbumCache()


# ------------------------------------------------------------------------------
# An Google Picasa implementation of a media storage provider.
# ------------------------------------------------------------------------------
class ZPicasaMediaStorageProvider(ZStreamBasedMediaStorageProvider):

    def __init__(self, properties):
        ZStreamBasedMediaStorageProvider.__init__(self, properties)
        self.picasaServer = None
    # end __init__()

    def _getAlbumName(self):
        if u"albumName" in self.properties: #$NON-NLS-1$
            return getSafeString(self.properties[u"albumName"]) #$NON-NLS-1$
        return None
    # end _getAlbumName()

    def _getPicasaServer(self):
        if not self.picasaServer:
            username = None
            password = None
            if u"username" in self.properties: #$NON-NLS-1$
                username = getNoneString(self.properties[u"username"]) #$NON-NLS-1$
            if not username:
                raise ZException(u"Picasa web album account username is required.") #$NON-NLS-1$
            if u"password" in self.properties: #$NON-NLS-1$
                password = getNoneString(self.properties[u"password"]) #$NON-NLS-1$
            if not password:
                raise ZException(u"Picasa web album account password is required.") #$NON-NLS-1$
            self.picasaServer = ZPicasaServer(username, password)
            self.picasaServer.setLogger(getLoggerService())
        return self.picasaServer
    # end _getPicasaServer()

    def _getPicasaAlbumEntry(self, albumName):
        global G_PICASA_ALBUM_CACHE
        # if first time, then list albums online and add to cache.
        if not G_PICASA_ALBUM_CACHE.hasAlbums():
            albumList = self._getPicasaServer().listAlbums()
            G_PICASA_ALBUM_CACHE.addAlbumList(albumList)

        album = G_PICASA_ALBUM_CACHE.getAlbumByName( albumName )
        if not album:
            # album did not exist. Add new album.
            album = self._getPicasaServer().addAlbum(albumName)
            if album:
                G_PICASA_ALBUM_CACHE.addAlbum(album)
        return album
    # end _getPicasaAlbumEntry()

    def _getPicasaPhotoEntry(self, metaDataElement):
        entry = ZPicasaPhotoEntry(metaDataElement)
        return entry
    # end _getPicasaPhotoEntry

    def _getEditMediaLinkFromMetaData(self, metaDataElement):
        photoEditMediaLink = None
        if metaDataElement:
            # Create photo entry.
            regPhoto = self._getPicasaPhotoEntry(metaDataElement)
            if regPhoto and regPhoto.getEditMediaLink():
                photoEditMediaLink = regPhoto.getEditMediaLink()
        return photoEditMediaLink
    # end _getEditMediaLinkFromMetaData()

    def _uploadStream(self, fileName, fileStream, metaData): #@UnusedVariable
        u"""_uploadStream(string, stream, ZElement) -> IZUploadResponse
        Called to upload a file stream to the remote media storage.
        Returns the URL of the uploaded file.""" #$NON-NLS-1$

        photoEditMediaLink = self._getEditMediaLinkFromMetaData(metaData)
        self._logDebug(u"upload file %s" % fileName) #$NON-NLS-1$
        self._logDebug(u"photoEditMediaLink is %s" % photoEditMediaLink) #$NON-NLS-1$
        photoEntry = None
        if photoEditMediaLink:
            # update existing file.
            photoEntry = self._getPicasaServer().updatePhotoFile(photoEditMediaLink, fileStream)
        else:
            # add new photo
            albumName = self._getAlbumName()
            self._logDebug(u"upload albumName %s" % albumName) #$NON-NLS-1$
            if not getNoneString(albumName):
                self._logError(u"Picasa web album name is required.") #$NON-NLS-1$
                raise ZException(u"Picasa web album name is required.") #$NON-NLS-1$
            albumEntry = self._getPicasaAlbumEntry(albumName)
            if not albumEntry:
                self._logError(u"Picasa web album '%s' does not exist." % albumName) #$NON-NLS-1$
                raise ZException(u"Picasa web album '%s' does not exist." % albumName) #$NON-NLS-1$
            photoEntry = self._getPicasaServer().addPhotoFile(albumEntry.getAlbumName(), fileStream)
        if not photoEntry:
            self._logError(u"Picasa web album upload failed for file %s" % fileName) #$NON-NLS-1$
            raise ZException(u"Picasa web album upload failed for file %s" % fileName) #$NON-NLS-1$

        return ZUploadResponse(photoEntry.getUrl(), metaData=photoEntry.getNode())
    # end _uploadStream()

    def deleteFile(self, fileName, metaData): #@UnusedVariable
        photoEditMediaLink = self._getEditMediaLinkFromMetaData(metaData)
        if not photoEditMediaLink:
            raise ZException(u"Cannot delete Picasa resource. Edit-Media link metadata not found.") #$NON-NLS-1$
        self._getPicasaServer().deleteResource(photoEditMediaLink)
    # end deleteFile()

    def listFiles(self, relativePath = None): #@UnusedVariable
        albumName = self._getAlbumName()
        if not albumName:
            raise ZException(u"Picasa web album name is required to list photos.") #$NON-NLS-1$
        albumEntry = self._getPicasaAlbumEntry(albumName)
        if not albumEntry:
            raise ZException(u"Can not list photos. Picasa web album '%s' does not exist." % albumName) #$NON-NLS-1$
        rval = []
        photoEntries = self._getPicasaServer().listPhotosByAlbumName(albumEntry.getAlbumName())
        for entry in photoEntries:
            rval.append( entry.getTitle() )
        return rval
    # end listFiles()

    def _getFileList(self, ftp):
        raise ZException(u"Method _getFileList not supported") #$NON-NLS-1$
    # end getFileList()
# end ZPicasaMediaStorageProvider
