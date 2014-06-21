from zoundry.appframework.util.portableutil import isPortableEnabled
from zoundry.base.util.fileutil import makeRelativePath
from zoundry.base.util.fileutil import resolveRelativePath
from zoundry.base.util.schematypes import ZSchemaDateTime
from zoundry.base.zdom.dom import ZDom
from zoundry.blogapp.services.mediastorage.mediastorageupload import ZUploadResponse
import os

# -----------------------------------------------------------------------------------
# Interface that must be implemented by the media storage's file registry.  The file
# registry is responsible for keeping track of the files that the store has already
# uploaded.
# -----------------------------------------------------------------------------------
class IZMediaStorageRegistry:

    def addFileEntry(self, filePath, size, timestamp, url, embedFragment, metaData):
        u"Adds the given file (meta data) to the registry." #$NON-NLS-1$
    # end addFileEntry()

    def removeFile(self, filePath):
        u"Removes the file from the media storage registry." #$NON-NLS-1$
    # end removeFile()

    def hasFile(self, filePath, size, timestamp):
        u"Returns True if the file with the given meta data exists in the registry." #$NON-NLS-1$
    # end hasFile()

    def getUploadResponse(self, filePath):
        u"Returns the upload response associated with the given filePath." #$NON-NLS-1$
    # end getUploadResponse()

    def getMetaData(self, filePath):
        u"""getMetaData(string) -> ZElement
        Returns the meta data for the given file path, or None.""" #$NON-NLS-1$
    # end getMetaData()

    def load(self, registryFile):
        u"Called to load the registry from a file." #$NON-NLS-1$
    # end load()

# end IZMediaStorageRegistry


# ----------------------------------------------------------------------------------------------
# The media storage registry is a class that is responsible for keeping track
# ----------------------------------------------------------------------------------------------
class ZMediaStorageRegistry(IZMediaStorageRegistry):

    def __init__(self, registryFile):
        self.registryFile = registryFile
        self.fileMap = {}

        self._load()
    # end __init__()

    # Adds the file at the given path to the registry.  Size should be an int, timestamp should
    # be a ZSchemaDateTime instance, url is a string.
    def addFile(self, filePath, size, timestamp, url):
        self.addFileEntry(filePath, size, timestamp, ZUploadResponse(url))
    # end addFile()

    def addFileEntry(self, filePath, size, timestamp, uploadResponse):
        self.fileMap[filePath] = (size, timestamp, uploadResponse)
        self._save()
    # end addFileEntry()

    def removeFile(self, filePath):
        del self.fileMap[filePath]
        self._save()
    # end removeFile()

    def getUploadResponse(self, filePath):
        if filePath in self.fileMap:
            (size, timestamp, uploadResponse) = self.fileMap[filePath] #@UnusedVariable
            return uploadResponse
        return None
    # end getUploadResponse()

    def getMetaData(self, filePath):
        uploadResponse = self.getUploadResponse(filePath)
        if uploadResponse is not None:
            return uploadResponse.getMetaData()
        return None
    # end getMetaData()

    def hasFile(self, filePath, size, timestamp):
        if filePath in self.fileMap:
            (recordedSize, recordedTimestamp, uploadResponse) = self.fileMap[filePath] #@UnusedVariable
            return recordedSize == size and timestamp == recordedTimestamp
        return False
    # end contains()

    def _save(self):
        if not self.registryFile:
            return

        mediaStorageDir = os.path.basename(self.registryFile)

        dom = ZDom()
        dom.loadXML(u"<registry/>") #$NON-NLS-1$
        registryElem = dom.documentElement
        for fileName in self.fileMap:
            (size, timestamp, uploadResponse) = self.fileMap[fileName]
            relativeFileName = makeRelativePath(mediaStorageDir, fileName)
            url = uploadResponse.getUrl()
            embedFragment = uploadResponse.getEmbedFragment()
            metaData = uploadResponse.getMetaData()

            entryElem = dom.createElement(u"entry") #$NON-NLS-1$
            entryElem.setAttribute(u"size", unicode(size)) #$NON-NLS-1$
            entryElem.setAttribute(u"timestamp", unicode(timestamp)) #$NON-NLS-1$

            fileElem = dom.createElement(u"file") #$NON-NLS-1$
            urlElem = dom.createElement(u"url") #$NON-NLS-1$
            embedElem = dom.createElement(u"embed") #$NON-NLS-1$
            metaDataElem = dom.createElement(u"metaData") #$NON-NLS-1$

            # When in portable mode, save the file paths as relative (which will
            # only happen when the image is on the same drive as the app).
            if isPortableEnabled():
                fileElem.setText(relativeFileName)
            else:
                fileElem.setText(fileName)

            entryElem.appendChild(fileElem)
            if url:
                urlElem.setText(unicode(url))
            entryElem.appendChild(urlElem)
            if embedFragment is not None:
                embedElem.appendChild(dom.importNode(embedFragment, True))
            entryElem.appendChild(embedElem)
            if metaData is not None:
                metaDataElem.appendChild(dom.importNode(metaData, True))
            entryElem.appendChild(metaDataElem)

            registryElem.appendChild(entryElem)

        dom.save(self.registryFile, True)
    # end save()

    def _load(self):
        if not self.registryFile or not os.path.exists(self.registryFile):
            return

        mediaStorageDir = os.path.basename(self.registryFile)

        dom = ZDom()
        dom.load(self.registryFile)
        # Legacy handling - old registry file format
        for fileElem in dom.selectNodes(u"/registry/file"): #$NON-NLS-1$
            fileName = fileElem.getText()
            size = int(fileElem.getAttribute(u"size")) #$NON-NLS-1$
            timestamp = ZSchemaDateTime(fileElem.getAttribute(u"timestamp")) #$NON-NLS-1$
            url = fileElem.getAttribute(u"url") #$NON-NLS-1$
            self.addFile(fileName, size, timestamp, url)
        # New registry file format
        for entryElem in dom.selectNodes(u"/registry/entry"): #$NON-NLS-1$
            size = int(entryElem.getAttribute(u"size")) #$NON-NLS-1$
            timestamp = ZSchemaDateTime(entryElem.getAttribute(u"timestamp")) #$NON-NLS-1$
            relativeFileName = entryElem.selectSingleNodeText(u"file") #$NON-NLS-1$
            fileName = resolveRelativePath(mediaStorageDir, relativeFileName)
            url = entryElem.selectSingleNodeText(u"url") #$NON-NLS-1$
            embedFragment = entryElem.selectSingleNode(u"embed/*") #$NON-NLS-1$
            metaData = entryElem.selectSingleNode(u"metaData/*") #$NON-NLS-1$
            uploadResponse = ZUploadResponse(url, embedFragment, metaData)
            self.addFileEntry(fileName, size, timestamp, uploadResponse)
    # end load()

# end ZMediaStorageRegistry
