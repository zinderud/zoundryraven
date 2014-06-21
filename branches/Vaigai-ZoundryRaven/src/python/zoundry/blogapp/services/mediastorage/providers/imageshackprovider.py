from zoundry.base.net.http import ZSimpleTextHTTPRequest
from zoundry.base.exceptions import ZException
from zoundry.base.net.contrib import urllib2_file #@UnusedImport
from zoundry.base.zdom.dom import ZDom
from zoundry.blogapp.services.mediastorage.mediastorageprovider import ZStreamBasedMediaStorageProvider
from zoundry.blogapp.services.mediastorage.mediastorageupload import ZUploadResponse

# ------------------------------------------------------------------------------
# An ImageShack implementation of a media storage provider.
#
# ------------------------------------------------------------------------------
class ZImageShackMediaStorageProvider(ZStreamBasedMediaStorageProvider):

    def __init__(self, properties):
        ZStreamBasedMediaStorageProvider.__init__(self, properties)
    # end __init__()

    def _uploadStream(self, fileName, fileStream, metaData): #@UnusedVariable
        data = {
            u"xml" : u"yes", #$NON-NLS-1$ #$NON-NLS-2$
            u"fileupload" : fileStream #$NON-NLS-1$
            }
        code = self._getRegistrationCode()
        if code:
            data[u"cookie"] = code #$NON-NLS-1$
        imageShackUrl = u"http://www.imageshack.us/index.php" #$NON-NLS-1$
        request = ZSimpleTextHTTPRequest(imageShackUrl)
        ok = request.send( data )
        if ok:
            respData = request.getResponse()
            dom = ZDom()
            dom.loadXML( respData )
            url = dom.selectSingleNodeText(u"/links/image_link") #$NON-NLS-1$
            return ZUploadResponse(url)
        else:
            code = unicode( request.getHttpStatusCode() )
            msg = unicode( request.getHttpStatusMessage() )
            raise ZException(u"ImageShackMedia upload failed. HTTP response: %s %s" % (code, msg)) #$NON-NLS-1$
    # end upload()

    def deleteFile(self, fileName, metaData): #@UnusedVariable
        raise ZException(u"Method deleteFile not supported") #$NON-NLS-1$
    # end deleteFile()

    def listFiles(self, relativePath = None):
        raise ZException(u"Method listFiles not supported") #$NON-NLS-1$
    # end listFiles()

    def _getFileList(self, ftp):
        raise ZException(u"Method _getFileList not supported") #$NON-NLS-1$
    # end getFileList()
    
    def _getRegistrationCode(self):
        if u"registrationCode" in self.properties: #$NON-NLS-1$
            return self.properties[u"registrationCode"] #$NON-NLS-1$
        return None
    # end _getRegistrationCode()

# end ZImageShackMediaStorageProvider
