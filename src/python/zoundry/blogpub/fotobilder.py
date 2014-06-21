import stat
from zoundry.base.net.http import ZSimpleXmlHTTPRequest
from zoundry.base.exceptions import ZException
from zoundry.base.util.text.textutil import getNoneString
import md5
import os.path

#-------------------------------------------------------------------
# Implements LiveJournal.com's photostorage api named FotoBilder
# See http://pics.livejournal.com/doc/protocol/
#-------------------------------------------------------------------


FOTOBILDER_HOST = u"pics.livejournal.com" #$NON-NLS-1$
FOTOBILDER_URL = u"http://" + FOTOBILDER_HOST + u"/interface/simple" #$NON-NLS-1$ #$NON-NLS-2$
FB_GALLERY_NAME =  u"Zoundry Raven" #$NON-NLS-1$
UPLOAD_BUFFER_SIZE = 1024 * 10

#===================================================
# FotoBilder exception
#===================================================
class ZFotoBilderException(ZException):
    def __init__(self, message = None, rootCause = None):  #$NON-NLS-1$  #$NON-NLS-2$
        ZException.__init__(self, message, rootCause)
    # end __init__()
# end ZFotoBilderException

#---------------------------------------------
# Request meta data
#---------------------------------------------
class ZFotoBilderRequest:

    def __init__(self, mode, fileName = None, fileDescriptor = None, zBlogServerMediaUploadListener = None):
        self.requestParams = {}
        self.addRequestParam(u"X-FB-Mode", mode) #$NON-NLS-1$
        self.fileName = fileName
        self.fileDescriptor = fileDescriptor
        self.clientVersion = None
        self.zBlogServerMediaUploadListener = zBlogServerMediaUploadListener
    #end __init__()

    def addRequestParam(self, name, value):
        value = getNoneString(value)
        name = getNoneString(name)
        if name and value:
            self.requestParams[name] = value
    # end addRequestParam

    def getRequestParams(self):
        return self.requestParams
    # end getRequestParams()

    def getFileName(self):
        return self.fileName
    # end getFile()
    
    def getFileDescriptor(self):
        return self.fileDescriptor
    # end getFileDescriptor()    

    def hasFile(self):
        return self.fileName != None and os.path.exists(self.fileName)
    # end hasFile

    def getUploadListener(self):
        return self.zBlogServerMediaUploadListener
    # end getUploadListener()
# end ZFotoBilderRequest

#---------------------------------------------
# Response data
#---------------------------------------------
class ZFotoBilderResponse:
    def __init__(self, httpCode, httpMessage, document):
        self.httpCode = httpCode
        self.httpMessage = httpMessage
        #zdom
        self.document = document
    # end __init__()

    def getStatusCode(self):
        return self.httpCode
    # end getStatusCode()

    def getStatusMessage(self):
        return self.httpMessage
    # end getStatusMessage()

    def getDocument(self):
        return self.document
    # end getDocument()
# end ZFotoBilderResponse

#---------------------------------------------
# image upload result
#---------------------------------------------
class ZFotoBilderUploadResult:
    def __init__(self, uploadPicResponseNode):
        self.uploadPicResponseNode = uploadPicResponseNode
    # end __init__()

    def getUploadPicResponseNode(self):
        return self.uploadPicResponseNode
    # end getUploadPicResponseNode()

    def getUrl(self):
        if self.uploadPicResponseNode:
            node = self.uploadPicResponseNode.selectSingleNode(u"URL") #$NON-NLS-1$
            if node:
                return node.getText()
        return None
    # end getUrl()
# ZFotoBilderUploadResult

#------------------------------------------------------------------------
# Http request to support IZBlogServerMediaUploadListener call back when uploading file.
#-----------------------------------------------------------------------
class ZFotoBilderHTTPRequest(ZSimpleXmlHTTPRequest):

    def __init__(self, url, customHeaders, zBlogServerMediaUploadListener = None):
        self.listener = zBlogServerMediaUploadListener
        ZSimpleXmlHTTPRequest.__init__(self, url, customHeaders)
    # end __init__()

    def _sendRawFile(self, fileDescriptor, connection):
        file_size = os.fstat( fileDescriptor.fileno() )[stat.ST_SIZE]
        CHUNK_SIZE = 10 * 1024
        if hasattr(fileDescriptor, u'seek'): #$NON-NLS-1$
            fileDescriptor.seek(0)
        if self.listener:
            self.listener.onStartTransfer(file_size)
        while True:
            chunk = fileDescriptor.read(CHUNK_SIZE)
            if not chunk:
                break
            connection.send(chunk)
            if self.listener:
                self.listener.onTransferChunk( len(chunk) )
        if self.listener:
            self.listener.onEndTransfer()

    # end _sendRawFile()
# end ZFotoBilderHTTPRequest
#------------------------------------------------------------------------
# FotoBilder API server proxy
#-----------------------------------------------------------------------
class ZFotoBilderServer:
    def __init__(self, username, password, url = None):
        self.username = username
        self.password = password
        self.url = getNoneString(url)
        if not self.url:
            self.url = FOTOBILDER_URL
        self.transferListener = None
        self.hpassword = self._md5digest(password)
        self.challenge = None
        self.challengeResponse = None
        self.clientVersion = None
    #end __init__()

    def getUrl(self):
        return self.url
    # end getUrl()

    def setUrl(self, url):
        self.url = url
    # end setUrl()

    def getUsername(self):
        return self.username
    #end getUsername()

    def getPassword(self):
        return self.password
    # end getPassword()

    def setClientVersion(self, version):
        self.clientVersion = getNoneString(version)
    # end setClientVersion()

    def getClientVersion(self):
        return self.clientVersion
    # end getClientVersion()

    def _getClientVersionParam(self):
        s = u"0.5" #$NON-NLS-1$
        if self.getClientVersion():
            s = self.getClientVersion()
        return u"Win32-ZoundryRaven/%s"  % s#$NON-NLS-1$
    # end _getClientVersionParam()

    def _getAuth(self, challenge, challengeResponse):
        auth = u"crp:%s:%s" % (challenge, challengeResponse) #$NON-NLS-1$
        return auth
    # end _getAuth()

    def _getFbStatus(self, fbResponse, xpath = u"/FBResponse/Error"): #$NON-NLS-1$
        u"""Returns tuple(bOk, message)""" #$NON-NLS-1$
        if not fbResponse:
            return (False, u"FotoBilderError: Empty Response") #$NON-NLS-1$
        msg = unicode(fbResponse.getStatusCode()) + u" - " + fbResponse.getStatusMessage() #$NON-NLS-1$
        if fbResponse.getStatusCode() != 200:
            return (False, msg)
        if not fbResponse.getDocument():
            return (False, u"FotoBilderError: XML Response not available") #$NON-NLS-1$
        errNode = fbResponse.getDocument().selectSingleNode(xpath)
        if not errNode and xpath != u"/FBResponse/Error": #$NON-NLS-1$
            xpath = u"/FBResponse/Error" #$NON-NLS-1$
            errNode = fbResponse.getDocument().selectSingleNode(xpath)
        if errNode:
            msg = u"FotoBilderError: [%s] %s" % (errNode.getAttribute(u"code"), errNode.getText()) #$NON-NLS-2$ #$NON-NLS-1$
            return (False, msg)
        return (True, u"ok") #$NON-NLS-1$
    # end _getFbStatus()

    def _setNextChallenge(self, fbResponse):
        if fbResponse.getDocument():
            node = fbResponse.getDocument().selectSingleNode(u"//GetChallengeResponse/Challenge") #$NON-NLS-1$
            if node:
                self.challenge = node.getText()
                s = str(self.challenge) + str(self.hpassword)
                self.challengeResponse = self._md5digest(s)
    # end _setNextChallenge()

    def _sendLogin(self):
        fbRequest = ZFotoBilderRequest(u"Login") #$NON-NLS-1$
        fbRequest.addRequestParam(u"X-FB-Login.ClientVersion", self._getClientVersionParam()) #$NON-NLS-1$
        fbResponse = self._sendRequest(fbRequest)
        return fbResponse
    # end _sendLogin()

    def _sendInitChallenge(self):
        self.challenge = None
        self.challengeResponse = None
        fbRequest = ZFotoBilderRequest(u"GetChallenge") #$NON-NLS-1$
        fbRequest.addRequestParam(u"X-FB-User", self.getUsername()) #$NON-NLS-1$
        fbResponse = self._internalSendRequest(fbRequest)
        (bOk, msg) = self._getFbStatus(fbResponse, u"//GetChallengeResponse/Error") #$NON-NLS-1$ @UnusedVariable
        if bOk:
            self._setNextChallenge(fbResponse)
        else:
            raise ZFotoBilderException(u"Initial Challenge failed: %s" % msg) #$NON-NLS-1$
    # end _sendInitChallenge()

    def _sendGetPics(self):
        fbRequest = ZFotoBilderRequest(u"GetPics") #$NON-NLS-1$
        fbResponse = self._sendRequest(fbRequest)
        return fbResponse
    # end _sendLogin()

    def _sendUploadPrepare(self, fileName):
        (picMd5, picMagic, picSize) = self._getPicFingerprint(fileName)
        fbRequest = ZFotoBilderRequest(u"UploadPrepare") #$NON-NLS-1$
        fbRequest.addRequestParam(u"X-FB-UploadPrepare.Pic._size", u"1") #$NON-NLS-1$ #$NON-NLS-2$
        fbRequest.addRequestParam(u"X-FB-UploadPrepare.Pic.0.MD5", picMd5) #$NON-NLS-1$
        fbRequest.addRequestParam(u"X-FB-UploadPrepare.Pic.0.Magic",  picMagic) #$NON-NLS-1$
        fbRequest.addRequestParam(u"X-FB-UploadPrepare.Pic.0.Size", str(picSize)) #$NON-NLS-1$
        fbResponse = self._sendRequest(fbRequest)
        return fbResponse
    # end _sendUploadPrepare()

    def _sendUploadFile(self, fileName, metaTitle = None, metaDesc = None, zBlogServerMediaUploadListener = None, gallery=None):
        fileDescriptor = None
        if hasattr(fileName, u'read'): #$NON-NLS-1$
            # file name is a file descriptor. get name from descriptor.
            fileDescriptor = fileName     
            fileName = fileDescriptor.name.split(u'/')[-1] #$NON-NLS-1$   
        metaFilename = os.path.basename(fileName)
        if not metaTitle:
            metaTitle =  metaFilename
        if not metaDesc:
            metaDesc  =  metaFilename

        if not getNoneString(gallery):
            gallery = FB_GALLERY_NAME
        picMd5 = self._getFileMD5(fileName)
        picSize = os.path.getsize(fileName)
        fbRequest = ZFotoBilderRequest(u"UploadPic", fileName, fileDescriptor, zBlogServerMediaUploadListener) #$NON-NLS-1$
        fbRequest.addRequestParam(u"X-FB-UploadPic.MD5", picMd5) #$NON-NLS-1$
        #fbRequest.addRequestParam("X-FB-UploadPic.PicSec", "1")
        fbRequest.addRequestParam(u"X-FB-UploadPic.ImageLength", str(picSize) ) #$NON-NLS-1$
        fbRequest.addRequestParam(u"X-FB-UploadPic.Meta.Filename", metaFilename ) #$NON-NLS-1$
        fbRequest.addRequestParam(u"X-FB-UploadPic.Meta.Title", metaTitle )#$NON-NLS-1$
        fbRequest.addRequestParam(u"X-FB-UploadPic.Meta.Description", metaDesc ) #$NON-NLS-1$
        fbRequest.addRequestParam(u"X-FB-UploadPic.Gallery._size", u"1" ) #$NON-NLS-1$ #$NON-NLS-2$
        fbRequest.addRequestParam(u"X-FB-UploadPic.Gallery.0.GalName", gallery ) #$NON-NLS-1$
        #fbRequest.addRequestParam("X-FB-UploadPic.Gallery.0.GalSec", "")
        fbResponse = self._sendRequest(fbRequest)
        return fbResponse
    # end _sendUploadFile()

    def uploadFile(self, fileName, metaTitle = None, metaDesc = None, zBlogServerMediaUploadListener = None, gallery=None):
        u"""uploadFile(string, string, string  -> ZFotoBilderUploadResult
        """ #$NON-NLS-1$
        fbResponse = self._sendUploadFile(fileName, metaTitle, metaDesc, zBlogServerMediaUploadListener, gallery)
        (bOk, msg) = self._getFbStatus(fbResponse, u"//UploadPicResponse/Error") #$NON-NLS-1$
        if not bOk:
            raise ZFotoBilderException(u"Upload error: " + msg) #$NON-NLS-1$
        node = fbResponse.getDocument().selectSingleNode(u"//UploadPicResponse") #$NON-NLS-1$
        if node:
            return ZFotoBilderUploadResult(node)
        else:
            raise ZFotoBilderException(u"FotoBilderError: Upload <UploadPicResponse> not available") #$NON-NLS-1$
    # end uploadFile()

    def _sendRequest(self, fbRequest):
        # Sends http request and returns ZFotoBilderResponse.
        if not self.challenge:
            self._sendInitChallenge()
        return self._internalSendRequest(fbRequest)
    # end _sendRequest()

    def _internalSendRequest(self, fbRequest):
        # Sends http request and returns ZFotoBilderResponse.
        endpoint = self.getUrl()
        if not endpoint:
            raise ZFotoBilderException(u"FotoBilderError: API Endpoint URL not available") #$NON-NLS-1$
        headers = fbRequest.getRequestParams().copy()
        headers[u"X-FB-User"] = self.getUsername() #$NON-NLS-1$
        headers[u"X-FB-Auth"] = self._getAuth(self.challenge, self.challengeResponse) #$NON-NLS-1$
        headers[u"X-FB-GetChallenge"] = u"1" #$NON-NLS-1$ #$NON-NLS-2$

        # optional upload listener - IZBlogServerMediaUploadListener.
        listener = fbRequest.getUploadListener()
        xmlHttpRequest = ZFotoBilderHTTPRequest(endpoint, headers, listener)
        fileHandle = None
        if fbRequest.hasFile():
            fileHandle = None
            # create file handle from descriptor or filename
            if fbRequest.getFileDescriptor():
                fileHandle = fbRequest.getFileDescriptor()
            else:
                fileHandle = open(fbRequest.getFileName(), u'rb') #$NON-NLS-1$
            xmlHttpRequest.setMethod(u"PUT") #$NON-NLS-1$
            if listener:
                listener.onStart()
        dom = None
        try:
            if xmlHttpRequest.send(fileHandle):
                dom = xmlHttpRequest.getResponse()
        except Exception, ex:
            if listener:
                listener.onFail(ex)
            raise ex
        if fileHandle:
            fileHandle.close()
            if listener:
                listener.onEnd()

        code = xmlHttpRequest.getHttpStatusCode()
        msg = xmlHttpRequest.getHttpStatusMessage()
        fbResponse = ZFotoBilderResponse(code, msg, dom)
        self._setNextChallenge(fbResponse)
        return fbResponse
    # end _internalSendRequest()

    def _md5digest(self, text):
        rVal = None
        try:
            m = md5.new()
            m.update(text)
            rVal = m.hexdigest()
        except AttributeError:
            pass
        return rVal
    # end _md5digest()

    def _getPicFingerprint(self, fileName):
        picMd5 = None #@UnusedVariable
        picMagic = None #@UnusedVariable
        picSize = 0        #@UnusedVariable
        f = file(fileName, u'rb') #$NON-NLS-1$
        magicData = f.read(10)
        f.close()
        import binascii
        picMagic = binascii.hexlify(magicData)
        picMd5 = self._getFileMD5(fileName)
        picSize = os.path.getsize(fileName)
        return (picMd5, picMagic, picSize)
    # end _getPicFingerprint()

    def _getFileMD5(self, fileName):
        total = 0
        f = file(fileName, u'rb') #$NON-NLS-1$
        m = md5.new()
        while 1:
            data = f.read(UPLOAD_BUFFER_SIZE)
            total = total + len(data)
            if not data:
                break
            m.update(data)
        f.close()
        rVal = m.hexdigest()
        return rVal
    # end _getFileMD5()

# end ZFotoBilderServer