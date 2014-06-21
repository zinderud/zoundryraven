from zoundry.appframework.messages import _extstr
from zoundry.appframework.services.dnd.dndsource import IZDnDSource
from zoundry.appframework.services.dnd.handlers.handler import ZBaseFileDnDHandler
from zoundry.base.util.urlutil import getUrlFromShortcut
from zoundry.base.xhtml.xhtmldocutil import createHtmlElement
from zoundry.base.xhtml.xhtmlio import loadXhtmlDocumentFromDOM

# ------------------------------------------------------------------------------
# Generic file DnD Handler.
# ------------------------------------------------------------------------------
class ZFileDnDHandler(ZBaseFileDnDHandler):

    def __init__(self):
        ZBaseFileDnDHandler.__init__(self)
    # end __init__()

    def getName(self):
        return _extstr(u"filehandler.File") #$NON-NLS-1$
    # end getName()

    def getDescription(self):
        return _extstr(u"filehandler.FileDesc") #$NON-NLS-1$
    # end getDescription()

    def canHandle(self, dndSource):
        return dndSource.hasType(IZDnDSource.TYPE_FILE)
    # end canHandle()

    def handle(self, dndSource, dndContext): #@UnusedVariable
        fileList = self._getFileList(dndSource)
        xhtml = self._handleFileList(fileList)
        return xhtml
    # end handle()

    def _getFileList(self, dndSource):
        fileSource = dndSource.getSource(IZDnDSource.TYPE_FILE)
        srcFile = fileSource.getData()
        return [srcFile]
    # end _getFileList()

    def _handleFileList(self, fileList):
        if not fileList:
            return None
        rootEle = None
        if len(fileList) == 1:
            rootEle = self._createFileAnchorElement(fileList[0], None)
        else:
            rootEle = createHtmlElement(None, u"p") #$NON-NLS-1$
            for fileName in fileList:
                self._createFileAnchorElement(fileName, rootEle)
                createHtmlElement(rootEle, u"br") #$NON-NLS-1$
        xhtmlDom = loadXhtmlDocumentFromDOM(rootEle)
        return xhtmlDom
    # end _handleFileList()

    def _createFileAnchorElement(self, fileName, parentElement):
        # check if this is a url shortcut
        size = 0
        rel = None
        (url, shortName) = getUrlFromShortcut(fileName)
        if not url:
            #  local file
            (url, shortName, absPath, size, schemaDate) = self._getFileMetaData(fileName) #@UnusedVariable
        if not shortName:
            shortName = url
        linkText = shortName
        linkTitle = shortName

        if size > 0:
            rel = u"enclosure" #$NON-NLS-1$
            linkTitle = linkTitle + u" (%s)" % self._getFileSizeString(size) #$NON-NLS-1$
        attrs = {}
        attrs[u"title"] = linkTitle #$NON-NLS-1$
        attrs[u"href"] = url #$NON-NLS-1$
        if rel:
            attrs[u"rel"] = rel #$NON-NLS-1$
        elem = createHtmlElement(parentElement, u"a", attrs, linkText) #$NON-NLS-1$
        return elem
    # end _handleFileList()

    def _getFileSizeString(self, nbytes):
        if nbytes and nbytes > 1024*1024:
            rval = u"%6.2F MB" % (float(nbytes) / (1024.0*1024.0)) #$NON-NLS-1$
        elif nbytes and nbytes > 1024:
            rval = u"%6.2F kB" % (float(nbytes) / 1024.0) #$NON-NLS-1$
        else:
            rval = u"%d bytes" % nbytes  #$NON-NLS-1$
        return rval
    # end _getFileSizeString()

# end ZFileDnDHandler


# ------------------------------------------------------------------------------
# Generic multifile DnD Handler.
# ------------------------------------------------------------------------------
class ZMultiFileDnDHandler(ZFileDnDHandler):

    def __init__(self):
        ZFileDnDHandler.__init__(self)
    # end __init__()

    def getName(self):
        return _extstr(u"filehandler.MultipleFiles") #$NON-NLS-1$
    # end getName()

    def getDescription(self):
        return _extstr(u"filehandler.MultipleFilesDesc") #$NON-NLS-1$
    # end getDescription()

    def canHandle(self, dndSource):
        return dndSource.hasType(IZDnDSource.TYPE_MULTI_FILE)
    # end canHandle()

    def _getFileList(self, dndSource):
        multiFileSource = dndSource.getSource(IZDnDSource.TYPE_MULTI_FILE)
        fileNames = multiFileSource.getData()
        return fileNames
    # end _getFileList()
