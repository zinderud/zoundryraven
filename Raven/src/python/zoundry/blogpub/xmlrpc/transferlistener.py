#------------------------------------------------
#  XML-RPX Server Proxy  transport level listener
#------------------------------------------------
from zoundry.base.util.fileutil import getFileMetaData
from zoundry.base.util.streamutil import IZStreamWrapperListener

class IZXmlRpcTransportListener:

    def onStartSend(self, total): #@UnusedVariable
        pass

    def onSend(self, chunkBytes): #@UnusedVariable
        pass

    def onEndSend(self):
        pass

    def onStartReceive(self, total):#@UnusedVariable
        pass

    def onReceive(self, chunkBytes):#@UnusedVariable
        pass

    def onEndReceive(self):
        pass


#------------------------------------------------
#  Listener adapter  to adapt  IZBlogServerMediaUploadListener
#  with IZXmlRpcTransportListener and base64 encoding of
#  of data.
#  Implements IZStreamWrapperListener to listen to base64 encoding
#  Implmentes IZXmlRpcTransportListener to listen to the tranport layer.
#------------------------------------------------
class ZMetawblogMediaUploadListenerAdapter(IZStreamWrapperListener, IZXmlRpcTransportListener):

    def __init__(self, mediaFile, izMediaUploadListener):
        self.mediaUploadListener  = izMediaUploadListener
        (shortName, filePath, size, timestamp) = getFileMetaData(mediaFile) #@UnusedVariable
        self.encTotal = size
        self.encStarted = False
        self.currTotalEnc = 0
        self.transferTotal = 0
        self.currTotalTranfered = 0
        self.sessionStarted = False

    def _notifyStarted(self):
        if not self.sessionStarted:
            self.sessionStarted = True
            if self.mediaUploadListener:
                self.mediaUploadListener.onStart()

    def _notifyEnded(self):
        if self.sessionStarted:
            self.sessionStarted = False
            if self.mediaUploadListener:
                self.mediaUploadListener.onEnd()

    def streamRead(self, blockSize, data): #@UnusedVariable
        # called when file is read -> during base64 enc.
        self._notifyStarted()
        if not self.mediaUploadListener:
            return
        if not self.encStarted:
            self.encStarted = True
            self.mediaUploadListener.onStartEncode(self.encTotal)
            self.currTotalEnc = 0
        self.mediaUploadListener.onEncodeChunk(blockSize)
        self.currTotalEnc  = self.currTotalEnc + blockSize
        if self.currTotalEnc >= self.encTotal:
            self.mediaUploadListener.onEndEncode()

    def onStartSend(self, total): #@UnusedVariable
        self._notifyStarted()
        self.transferTotal = total
        self.currTotalTranfered = 0
        if self.mediaUploadListener:
            self.mediaUploadListener.onStartTransfer(total)

    def onSend(self,chunkBytes): #@UnusedVariable
        if self.mediaUploadListener:
            self.currTotalTranfered = self.currTotalTranfered + chunkBytes
            self.mediaUploadListener.onTransferChunk(chunkBytes)

    def onEndSend(self):
        if self.mediaUploadListener:
            self.mediaUploadListener.onEndTransfer()
        self._notifyEnded()

    def onStartReceive(self, total):#@UnusedVariable
        pass

    def onReceive(self, chunkBytes):#@UnusedVariable
        pass

    def onEndReceive(self):
        self._notifyEnded()

    def notifyFailure(self, exception):
        if self.mediaUploadListener:
            self.mediaUploadListener.onFail(exception)
        self._notifyEnded()



