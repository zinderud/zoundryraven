from zoundry.blogapp.services.mediastorage.mediastorageprovider import ZStreamBasedMediaStorageProvider
from string import atoi
from string import split
from zoundry.blogapp.services.mediastorage.mediastorageupload import ZUploadResponse
import ftplib
import os

# ------------------------------------------------------------------------------
# An FTP implementation of a media storage provider.
#
# FIXME (proxy) need to support proxies here
# ------------------------------------------------------------------------------
class ZFTPMediaStorageProvider(ZStreamBasedMediaStorageProvider):

    def __init__(self, properties):
        ZStreamBasedMediaStorageProvider.__init__(self, properties)
    # end __init__()

    def _uploadStream(self, fileName, fileStream, metaData): #@UnusedVariable
        (host, path, username, password, port, urlBase, pasv) = self._getFTPSettings()

        ftp = ftplib.FTP()
        try:
            self._connect(ftp, host, port, username, password, path, pasv)
            ftp.storbinary(u"STOR " + fileName, fileStream, 4096) #$NON-NLS-1$
        finally:
            self._disconnect(ftp)

        url = urlBase.rstrip(u"/") + u"/" + fileName #$NON-NLS-1$ #$NON-NLS-2$
        return ZUploadResponse(url)
    # end upload()

    def deleteFile(self, fileName, metaData): #@UnusedVariable
        (host, path, username, password, port, urlBase, pasv) = self._getFTPSettings() #@UnusedVariable

        ftp = ftplib.FTP()
        try:
            self._connect(ftp, host, port, username, password, path, pasv)
            ftp.delete(fileName)
        finally:
            self._disconnect(ftp)
    # end deleteFile()

    def listFiles(self, relativePath = None):
        (host, path, username, password, port, urlBase, pasv) = self._getFTPSettings() #@UnusedVariable
        if relativePath:
            path = os.path.join(path, relativePath)

        ftp = ftplib.FTP()
        try:
            self._connect(ftp, host, port, username, password, path, pasv)
            return self._getFileList(ftp)
        finally:
            self._disconnect(ftp)
    # end listFiles()

    def _connect(self, ftp, host, port, username, password, path, pasv):
        # FIXME (EPW) raise some better exceptions for failures, and close the ftp connection in a finally!
        # FIXME (EPW) test - make sure each command succeeds (or alternatively make sure that each call throws if it fails)
        ftp.connect(host, port)
        ftp.sendcmd(u"USER %s" % username) #$NON-NLS-1$
        ftp.sendcmd(u"PASS %s" % password) #$NON-NLS-1$
        if not path == u"/": #$NON-NLS-1$
            ftp.cwd(path)
        ftp.set_pasv(pasv)
    # end _connect()

    def _disconnect(self, ftp):
        # Note - some FTP sites will cause quit() to throw.  But we should try it anyway just
        # to be nice.  If it fails, then call close() [quit calls close when it works]
        try:
            ftp.quit()
        except:
            ftp.close()
    # end _disconnect()

    def _getFTPSettings(self):
        host = self.properties[u"host"] #$NON-NLS-1$
        path = self.properties[u"path"] #$NON-NLS-1$
        username = self.properties[u"username"] #$NON-NLS-1$
        password = self.properties[u"password"] #$NON-NLS-1$
        port = atoi(self.properties[u"port"]) #$NON-NLS-1$
        if not port:
            port = 21
        urlBase = self.properties[u"url"] #$NON-NLS-1$
        pasv = self.properties[u"passive"] #$NON-NLS-1$
        return (host, path, username, password, port, urlBase, pasv)
    # end _getFTPSettings()

    def _getFileList(self, ftp):
        fileList = []
        rvalList = []
        ftp.retrlines(u'LIST', fileList.append) #$NON-NLS-1$
        for rfile in fileList:
            rfileSplit = split(rfile)
            if len(rfileSplit) == 9:
                rfileName = rfileSplit[8]
                if (not rfileName == u".") and (not rfileName == u"..") and (not rfile[0] == u'd'): #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$
#                    rfileSize = rfileSplit[4]
#                    rvalList.append( (rfileName, atoi(rfileSize)) )
                    rvalList.append(rfileName)
            elif len(rfileSplit) == 4:
                rfileName = rfileSplit[3]
                if (not rfileName == u".") and (not rfileName == u"..") and (not rfileSplit[2] == u'<DIR>'): #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$
#                    rfileSize = rfileSplit[2]
#                    rvalList.append( (rfileName, atoi(rfileSize)) )
                    rvalList.append(rfileName)
            elif len(rfileSplit) == 5:
                rfileName = rfileSplit[4]
                if (not rfileName == u".") and (not rfileName == u"..") and (not rfileSplit[3] == u'<DIR>'): #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$
#                    rfileSize = rfileSplit[3]
#                    rvalList.append( (rfileName, atoi(rfileSize)) )
                    rvalList.append(rfileName)
        return rvalList
    # end getFileList()

# end ZFTPMediaStorageProvider
