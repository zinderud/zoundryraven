# --------------------------------------------------------------------------
# Prepublish handler responsible for uploading media.
# --------------------------------------------------------------------------
from zoundry.base.util.fileutil import getFileExtension
from zoundry.base.util.fileutil import getFileMetaData
from zoundry.appframework.constants import IZAppServiceIDs
from zoundry.base.util.text.textutil import getSafeString
import os.path
from zoundry.base.util.text.textutil import getNoneString
from zoundry.blogapp.constants import IZBlogAppServiceIDs
from zoundry.appframework.global_services import getApplicationModel
from zoundry.base.util.urlutil import getFilePathFromUri
from zoundry.base.util.urlutil import isLocalFile
from zoundry.blogapp.services.mediastorage.mediastorage import IZMediaStorageUploadListener
from zoundry.blogapp.services.pubsystems.blog.handlers.pubprocesshandlers import ZBlogPostContentAnalyserBase
from zoundry.blogapp.services.pubsystems.blog.handlers.pubprocesshandlers import ZBlogPublishHandlerBase


#------------------------------------------------------------
# Uploads media content,
#------------------------------------------------------------
class ZUploadContentPrePublishHandler(ZBlogPublishHandlerBase):

    def __init__(self, zblog):
        ZBlogPublishHandlerBase.__init__(self, u"ZUploadContentPrePublishHandler") #$NON-NLS-1$
        self.zblog = zblog
        self.mediaStoreId = getNoneString( self.zblog.getMediaUploadStorageId() )
        self.uploadContentList = None
        self._getLogger().debug(u"ZUploadContentPrePublishHandler-init: BlogId: %s" % zblog.getId()) #$NON-NLS-1$
        self._getLogger().debug(u"ZUploadContentPrePublishHandler-init: BlogName: %s" % zblog.getName()) #$NON-NLS-1$
    # end __init__()

    def _getMediaStoreId(self):
        return self.mediaStoreId
    # end _getMediaStoreId()

    def _getMediaStorage(self):
        mediaStoreId = self._getMediaStoreId()
        mediastorage = None
        if mediaStoreId:
            mediaStoreService = getApplicationModel().getService(IZBlogAppServiceIDs.MEDIA_STORAGE_SERVICE_ID)
            mediastorage = mediaStoreService.getMediaStorageById(mediaStoreId)
        return mediastorage
    # end _getMediaStorage()

    def _supportsFile(self, fileName):
        izMediaStorage = self._getMediaStorage()
        if izMediaStorage:
            return izMediaStorage.supportsFile(fileName)
        return False
    #  end _supportsFile

    def _validateConfiguration(self,validationReporter): #@UnusedVariable
        blogName = self.zblog.getName()

        xhtmlDocument = self._getContext().getXhtmlDocument()
        analyser = ZUploadContentAnalyser()
        xhtmlDocument.analyse(analyser)
        uploadList = analyser.getContentList()
        s = u"validate: Files upload: %d" % len(uploadList) #$NON-NLS-1$
        self._getContext().logInfo(self, s)
        if len(uploadList) == 0:
            return

        s = u"validate: Media store id: %s" % self._getMediaStoreId() #$NON-NLS-1$
        self._getContext().logInfo(self, s)
        s = u"validate: Has Mediastore: %s" % (self._getMediaStorage() is not None) #$NON-NLS-1$
        self._getContext().logInfo(self, s)

        if not self._getMediaStoreId():
            validationReporter.addWarning(u"Media Upload", u"A media store is required. Files will not be uploaded for blog %s." % blogName) #$NON-NLS-1$ #$NON-NLS-2$
            s = u"A media store ID is required. Files will not be uploaded for blog %s." % blogName #$NON-NLS-1$
            self._getContext().logWarning(self, s)
            return

        elif not self._getMediaStorage():
            validationReporter.addWarning(u"Media Upload", u"A media store not found. Files will not be uploaded for blog %s." % blogName) #$NON-NLS-1$ #$NON-NLS-2$
            s = u"A media store instance is required. Files will not be uploaded for blog %s." % blogName #$NON-NLS-1$
            self._getContext().logWarning(self, s)
            return

        storeName = self._getMediaStorage().getName()
        for upload in uploadList:
            if not os.path.exists( upload.getFile() ):
                validationReporter.addWarning(u"Media Upload", u"Media upload file not found: %s ." % os.path.abspath(upload.getFile()) ) #$NON-NLS-1$ #$NON-NLS-2$
                s = u"Media upload file not found: %s ." % os.path.abspath(upload.getFile())  #$NON-NLS-1$
                self._getContext().logWarning(self, s)

            elif not self._supportsFile( upload.getFile() ):
                validationReporter.addWarning(u"Media Upload", u"Media type is not support by '%s' media store: %s ." % (storeName, os.path.abspath(upload.getFile()) ) ) #$NON-NLS-1$ #$NON-NLS-2$
                s = u"Media type is not support by this media store: %s ." % os.path.abspath(upload.getFile())  #$NON-NLS-1$
                self._getContext().logWarning(self, s)

    # end validateConfiguration()


    def _prepare(self):
        s = u"prepare: Has Mediastore: %s" % (self._getMediaStorage() is not None) #$NON-NLS-1$
        self._getContext().logInfo(self, s)
        if self._getMediaStorage() is not None:
            self._buildMediaUploadList()
            self._setTotalWorkUnits( len(self._getUploadContentList()) )
    # end _prepare()

    def _process(self):
        s = u"process: Has Mediastore: %s" % (self._getMediaStorage() is not None) #$NON-NLS-1$
        self._getContext().logInfo(self, s)
        if self._getMediaStorage() is not None:
            self._uploadContent()
    # end process()

    def _uploadContent(self):
        pubMetaData = self._getContext().getPubMetaData()
        mediastorage = self._getMediaStorage()
        label = u"%s[%s]" % (mediastorage.getName(), mediastorage.getId() ) #$NON-NLS-1$
        s = u"uploadContent: store: %s" % label #$NON-NLS-1$
        self._getContext().logInfo(self, s)

        filenum = 0
        for upload in self._getUploadContentList():
            if  self.isCancelled():
                break
            filenum = filenum + 1
            s = u"About to upload file %d of %d" % (filenum, self.getTotalWorkUnits()) #$NON-NLS-1$
            self._getContext().logInfo(self, s)

            self._getContext().logInfo(self, u"Bypass registry - %s" % pubMetaData.isForceReUploadImages() ) #$NON-NLS-1$
            s = u"Uploading file %d of %d" % (filenum, self.getTotalWorkUnits()) #$NON-NLS-1$
            self._getContext().notifyProgress(self, s, 1, False)

            if not self._supportsFile( upload.getFile() ):
                s = u"Unsupported media type. Skipping upload: %s" % upload.getFile() #$NON-NLS-1$
                self._getContext().logWarning(self, s)
                continue

            listener = ZPrePublishHandlerMediaStorageUploadListener(self, self.getTotalWorkUnits(), filenum, label)
            uploadResponse = mediastorage.upload(upload.getFile(), listener, bypassRegistry = pubMetaData.isForceReUploadImages() )
            self._getContext().logInfo(self, u"Remote url is %s" % uploadResponse.getUrl() ) #$NON-NLS-1$
            if uploadResponse.hasEmbedFragment():
                self._getContext().logInfo(self, u"Embed fragment is %s" % uploadResponse.getEmbedFragment().serialize() ) #$NON-NLS-1$
            upload.setUploadResponse( uploadResponse )

            listener = None
            # apply uploaded url to the <img> src or <a> href value
            upload.applyUploadResponse(mediastorage)

    # end _uploadContent()

    def _getUploadContentList(self):
        u"""getUploadContentList -> list of ZBlogDocumentUploadContent
        """#$NON-NLS-1$
        return self.uploadContentList
    # end _getUploadContentList()

    def _buildMediaUploadList(self):
        # if upload list it not none, return
        if self.uploadContentList is not None:
            return
        xhtmlDocument = self._getContext().getXhtmlDocument()
        analyser = ZUploadContentAnalyser()
        xhtmlDocument.analyse(analyser)
        uploadList = analyser.getContentList()
        self.uploadContentList = []
        for upload in uploadList:
            if os.path.exists( upload.getFile() ):
                self.uploadContentList.append(upload)
            else:
                s = u"Will not upload file (not found): %s" % upload.getFile() #$NON-NLS-1$
                self._getContext().logWarning(self, s)
    # end _buildMediaUploadList()

# --------------------------------------------------------------------------
# Media store upload listener.
# --------------------------------------------------------------------------

class ZPrePublishHandlerMediaStorageUploadListener(IZMediaStorageUploadListener):

    def __init__(self, uploadContentPrePublishHandler, totalfiles, filenum, label):
        self.uploadContentPrePublishHandler = uploadContentPrePublishHandler
        self.totalfiles = totalfiles
        self.filenum = filenum
        self.totalBytes = 0
        self.currBytes = 0
        self.fileName = None
        self.mediaStoreLabel = label
    # end __init__()

    def onUploadStarted(self, fileName, totalBytes): #@UnusedVariable
        self.totalBytes = totalBytes
        self.currBytes = 0
        self.fileName = fileName
        fname = os.path.basename(self.fileName)
        s = u"Uploading to media store %s file %d of %d (%s),  %d bytes" % (self.mediaStoreLabel, self.filenum, self.totalfiles, fname, self.totalBytes)  #$NON-NLS-1$
        self.uploadContentPrePublishHandler._getContext().logInfo(self.uploadContentPrePublishHandler, s)
        s = u"Uploading file %d of %d (%s)" % (self.filenum, self.totalfiles, self.fileName)  #$NON-NLS-1$
        self.uploadContentPrePublishHandler._getContext().notifyProgress(self.uploadContentPrePublishHandler, s, 0, False)

    # end onUploadStarted()

    def onUploadChunk(self, fileName, chunkBytes): #@UnusedVariable
        fname = os.path.basename(self.fileName)
        self.currBytes = self.currBytes + chunkBytes
        per = 0
        if self.totalBytes > 0:
            per = int( 100 * float(self.currBytes) / float(self.totalBytes) )
        s = u"Uploading file %d of %d (%d%%, %s)" % (self.filenum, self.totalfiles, per, fname)  #$NON-NLS-1$
        self.uploadContentPrePublishHandler._getContext().notifyProgress(self.uploadContentPrePublishHandler, s, 0, False)
    # end onUploadChunk()

    def onUploadFailed(self, fileName, exception): #@UnusedVariable
        s = u"Failed to upload file %d of %d (%s)" % (self.filenum, self.totalfiles, self.fileName)  #$NON-NLS-1$
        self.uploadContentPrePublishHandler._getContext().notifyProgress(self.uploadContentPrePublishHandler, s, 0, False)
        self.uploadContentPrePublishHandler._getContext().logInfo(self.uploadContentPrePublishHandler, s)
        self.uploadContentPrePublishHandler._getContext().logException(self.uploadContentPrePublishHandler, exception)
    # end onUploadFailed()

    def onUploadComplete(self, fileName): #@UnusedVariable
        s = u"Done uploading file %d of %d (%s), %d bytes" % (self.filenum, self.totalfiles, self.fileName, self.totalBytes)  #$NON-NLS-1$
        self.uploadContentPrePublishHandler._getContext().logInfo(self.uploadContentPrePublishHandler, s)
        s = u"Done uploading file %d of %d (%s)" % (self.filenum, self.totalfiles, self.fileName)  #$NON-NLS-1$
        self.uploadContentPrePublishHandler._getContext().notifyProgress(self.uploadContentPrePublishHandler, s, 0, False)

# --------------------------------------------------------------------------
# Analyser to build a list of elements (<a> or <img>) that needs to be uploaded.
# --------------------------------------------------------------------------
class ZUploadContentAnalyser(ZBlogPostContentAnalyserBase):

    def __init__(self):
        self.contentList = []
    # end __init__

    def getContentList(self):
        # erturns list of ZBlogDocumentUploadContent
        return self.contentList
    # end getContentList()

    def _analyseZXhtmlLink(self, iZXhtmlLink): #@UnusedVariable
        if isLocalFile( iZXhtmlLink.getHref() ):
            self.contentList.append( ZBlogDocumentUploadContent(iZXhtmlLink.getNode()) )
    # end _analyseZXhtmlLink()

    def _analyseZXhtmlImage(self, iZXhtmlImage): #@UnusedVariable
        if isLocalFile( iZXhtmlImage.getSrc() ):
            self.contentList.append( ZBlogDocumentUploadContent(iZXhtmlImage.getNode()) )
    # end _analyseZXhtmlImage()

# --------------------------------------------------------------------------
# Encapsulates references to media in a xhtml document which needs to be uploaded.
# --------------------------------------------------------------------------
class ZBlogDocumentUploadContent:

    def __init__(self, element):
        self.element = element
        self.uploadResponse = None
        self.imgExtensions = u"bmp,gif,jpeg,jpg,png".split(u",") #$NON-NLS-1$ #$NON-NLS-2$
    # end __init__()

    def getLocalUri(self):
        u"""getLocalUri() -> stting
        Returns local path of href or src attribute value."""  #$NON-NLS-1$
        if self.element.localName.lower() == u"a": #$NON-NLS-1$
            return self.element.getAttribute(u"href") #$NON-NLS-1$
        elif self.element.localName.lower() == u"img": #$NON-NLS-1$
            return self.element.getAttribute(u"src")  #$NON-NLS-1$
        else:
            return None
    # end getLocalUri()

    def getFile(self):
        u"""getFile() -> string"""  #$NON-NLS-1$
        rval = self.getLocalUri()
        if rval:
            rval = getFilePathFromUri(rval)
        return rval
    # end getFile()

    def setUploadResponse(self, uploadResponse):
        u"""setUploadResponse(IZUploadResponse) -> void""" #$NON-NLS-1$
        self.uploadResponse = uploadResponse
    # end setUploadResponse()

    def applyUploadResponse(self, izMediaStorage):
        u"""applyUploadResponse(IZMediaStorage) -> void""" #$NON-NLS-1$
        if self.uploadResponse and self.uploadResponse.getUrl() is not None:
            url = self._getModifiedUrl( izMediaStorage )
            if self.element.localName.lower() == u"a": #$NON-NLS-1$
                self.element.setAttribute(u"href", url) #$NON-NLS-1$
            elif self.element.localName.lower() == u"img": #$NON-NLS-1$
                self.element.setAttribute(u"src", url)  #$NON-NLS-1$
    # end applyUploadResponse()
    
    def _isImageFile(self):
        (fileName, absFilePath, filePath, dateTime) = getFileMetaData(  self.getFile() ) #@UnusedVariable
        fileExt = getFileExtension(fileName)
        return fileExt and fileExt in self.imgExtensions
    # end _isImageFile()

    def _getModifiedUrl(self, izMediaStorage):
        # temp work around for picasa
        # find best size thumbnail from picasa result given img size
        # and get url that is hotlink compatible with picasa
        url = None
        if self._isPicasaMediaStoreType(izMediaStorage) and self._isImageFile():
            url = self._getPicasaImgUrl()
        else:
            # default case - use img url returned as-is from media store.
            url = self.uploadResponse.getUrl()
        return url
    # end _getModifiedUrl()

    def _getPicasaImgUrl(self):
        # get image size from <img> element attributes
        (width, height) = self._getImageSizeFromElem()
        if width == -1 or height == -1:
            # check file for image size since width/height is not available in <img> element.
            (width, height) = self._getImageSizeFromFile( self.getFile() )
        maxsize = -1
        if width > 1 and width >= height:
            # look for closest landscape size
            maxsize = width
        elif height > 1 and height > width:
            # look for closest landscape size
            maxsize = height
        # FIXME (PJ) check (picasa) embed content for one of thumbnail urls that best matches given size.
        #        url = None
        #        if self.uploadResponse.getMetaData():
        #            if width > 1 and width >= height:
        #                # look for closest landscape size
        #                pass
        #            elif height > 1 and height > width:
        #                # look for closest landscape size
        #                pass
        #            if width > 1:
        #                self.element.setAttribute(u"width", unicode(width)) #$NON-NLS-1$
        #            if height > 1:
        #                self.element.setAttribute(u"height", unicode(width)) #$NON-NLS-1$

        # default url
        url = self.uploadResponse.getUrl()
        # Picasa hotlinking work around => append 'imgmax' query param
        if maxsize != -1:
            imgmax = self._getPicasaImgMax(maxsize)
            url = url + u"?imgmax=%d" % imgmax       #$NON-NLS-1$
        return url
    # end _getPicasaImgUrl

    def _getPicasaImgMax(self, maxSize):
        # these are the max sizes that are compatible with Picasa hot linking.
        sizes = [32, 48, 64, 72, 144, 160, 200, 288, 320, 400, 512, 576, 640, 720, 800]
        for size in sizes:
            if size >= maxSize:
                return size
        # default = 800
        return sizes[-1]
    # end _getPicasaImgMax

    def _isPicasaMediaStoreType(self, izMediaStorage):
        try:
            siteId = izMediaStorage.getMediaSiteId()
            mediaStoreService = getApplicationModel().getService(IZBlogAppServiceIDs.MEDIA_STORAGE_SERVICE_ID)
            mediaSite = mediaStoreService.getMediaSite(siteId)
            storeTypeId = mediaSite.getMediaStorageTypeId()
            return storeTypeId == u"zoundry.blogapp.mediastorage.type.picasa" #$NON-NLS-1$
        except:
            # ignore errors
            return False
    # end _isPicasaMediaStoreType()

    def _getImageSizeFromElem(self):
        width = -1
        try:
            width = int( getSafeString( self.element.getAttribute(u"width")) )#$NON-NLS-1$
        except:
            pass
        height = -1
        try:
            height = int( getSafeString( self.element.getAttribute(u"height")) )#$NON-NLS-1$
        except:
            pass
        return (width, height)
    # end _getImageSizeFromElem

    def _getImageSizeFromFile(self, imgPath):
        imgService = getApplicationModel().getService(IZAppServiceIDs.IMAGING_SERVICE_ID)
        (width, height) = imgService.getImageSize(imgPath)
        return (width, height)
    # end _getImageSize

# end ZBlogDocumentUploadContent