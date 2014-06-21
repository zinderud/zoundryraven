from zoundry.base.css.cssdepends import ZCSSDependencyFinder
from zoundry.base.exceptions import ZException
from zoundry.base.net.http import IZHttpBinaryFileDownloadListener
from zoundry.base.net.http import ZCookieReg
from zoundry.base.net.http import ZHttpBinaryFileDownload
from zoundry.base.net.http import ZSimpleTextHTTPRequest
from zoundry.base.resdepends import IZResourceDependencyTypes
from zoundry.base.util.fileutil import getFileContents
from zoundry.base.util.fileutil import makeRelativePath
from zoundry.base.util.guid import generate
from zoundry.base.util.types.list import ZDefaultListComparator
from zoundry.base.util.types.list import ZSortedSet
from zoundry.base.xhtml.xhtmldepends import ZXhtmlDependencyFinder
from zoundry.base.xhtml.xhtmltelements import ZUrl
import codecs
import os
import urlparse

# ------------------------------------------------------------------------------
# Compares based on the lengths of two hrefs.
# ------------------------------------------------------------------------------
class ZHrefLengthComparator(ZDefaultListComparator):

    def compare(self, object1, object2):
        return ZDefaultListComparator.compare(self, len(object2), len(object1))
    # end compare()

# end ZHrefLengthComparator


# ------------------------------------------------------------------------------
# Interface for listening to the download of a web page.  Downloading a web
# page consists of downloading the root page, and then downloading all of the
# pages that the root depends on (images, CSS, javascript).
# ------------------------------------------------------------------------------
class IZHttpWebpageGetterListener:

    def onWebpageGetterStart(self):
        u"""onWebpageGetterStart() -> None
        Initial start callback - at the start of the
        entire website get.""" #$NON-NLS-1$
    # end onWebpageGetterStart()

    def onWebpageGetterResourceStarted(self, url, type):
        u"""onWebpageGetterResourceStarted() -> None
        Called when a resource is about to be downloaded.""" #$NON-NLS-1$
    # end onWebpageGetterResourceStarted()

    def onWebpageGetterResourceConnected(self, url, contentType, contentLength):
        u"""onWebpageGetterResourceConnected() -> None
        Called when a connection is made to get a resource.  Note
        that this method may not be called for all resources.""" #$NON-NLS-1$
    # end onWebpageGetterResourceConnected()

    def onWebpageGetterResourceChunk(self, url, bytesDownloaded):
        u"""onWebpageGetterResourceChunk() -> None
        Called each time a block/chunk of binary data is
        downloaded while getting a particular resource.  note
        that this method may not be called for all resources.""" #$NON-NLS-1$
    # end onWebpageGetterResource()

    def onWebpageGetterResourceComplete(self, url):
        u"""onWebpageGetterResourceComplete() -> None
        Called when a resource has been downloaded
        successfully.""" #$NON-NLS-1$
    # end onWebpageGetterResourceComplete()
    
    def onWebpageGetterFoundDependencies(self, parentUrl, dependencies):
        u"""onWebpageGetterFoundDependencies() -> None
        Called when a CSS or HTML resource has been downloaded
        and analyzed for its dependencies.""" #$NON-NLS-1$
    # end onWebpageGetterFoundDependencies()

    def onWebpageGetterComplete(self):
        u"""onWebpageGetterComplete() -> None
        Called when the entire webpage has been downloaded.""" #$NON-NLS-1$
    # end onWebpageGetterComplete()

    def onWebpageGetterError(self, error):
        u"""onWebpageGetterError() -> None
        Called if a fatal error is encountered.""" #$NON-NLS-1$
    # end onWebpageGetterError()

# end IZHttpWebpageGetterListener


# ------------------------------------------------------------------------------
# Adapts a binary download listener to a webpage getter listener.
# ------------------------------------------------------------------------------
class ZBinaryToWebpageGetterAdapterListener(IZHttpBinaryFileDownloadListener):

    def __init__(self, url, listener):
        self.url = url
        self.listener = listener
        if self.listener is None:
            self.listener = IZHttpWebpageGetterListener()
    # end __init__()

    def transferStarted(self, contentType, contentLength):
        self.listener.onWebpageGetterResourceConnected(self.url, contentType, contentLength)
    # end transferStarted()

    def transferBlock(self, blockLength):
        self.listener.onWebpageGetterResourceChunk(self.url, blockLength)
    # end transferBlock()

    def transferComplete(self):
        self.listener.onWebpageGetterResourceComplete(self.url)
    # end transferComplete()

# end ZBinaryToWebpageGetterAdapterListener


# ------------------------------------------------------------------------------
# The http webpage getter is a class that is used to download a complete web
# page.  It does this by downloading the HTML file at the given root URL, then
# downloading all of the resources that web page is dependent upon (javascript,
# CSS, images).
# ------------------------------------------------------------------------------
class ZHttpWebpageGetter:

    def __init__(self, url, outputDir, listener):
        self.url = url
        self.outputDir = os.path.abspath(outputDir)
        self.listener = listener
        self.resourceMap = {}
        self.downloadedHrefs = ZSortedSet()
        self.resourcesToFixup = ZSortedSet()
        self.basePathToken = None
        self.baseHref = None

        self.imagesDir = os.path.join(self.outputDir, u"images") #$NON-NLS-1$
        if not os.path.exists(self.imagesDir):
            os.makedirs(self.imagesDir)
        self.cssDir = os.path.join(self.outputDir, u"css") #$NON-NLS-1$
        if not os.path.exists(self.cssDir):
            os.makedirs(self.cssDir)
        self.otherDir = os.path.join(self.outputDir, u"other") #$NON-NLS-1$
        if not os.path.exists(self.otherDir):
            os.makedirs(self.otherDir)
            
        self.cookieReg = ZCookieReg()
        
        if self.listener is None:
            self.listener = IZHttpWebpageGetterListener()
    # end __init__()
    
    def setBasePathToken(self, token):
        self.basePathToken = token
    # end setBasePathToken()

    def saveAsWebpage(self):
        self.listener.onWebpageGetterStart()
        
        rootFile = None
        try:
            rootFile = self._saveAsWebpage()
        except ZException, ze:
            self.listener.onWebpageGetterError(ze)
            raise ze
        except Exception, e:
            ze = ZException(rootCause = e)
            self.listener.onWebpageGetterError(ze)
            raise ze

        self.listener.onWebpageGetterComplete()
        return rootFile
    # end saveAsWebpage()

    def _saveAsWebpage(self):
        rootFile = self._generateResourceName(self.outputDir, self.url) #$NON-NLS-1$

        self.resourceMap[self.url] = rootFile
        self.resourcesToFixup.add(rootFile)

        # Download the root URL
        download = ZSimpleTextHTTPRequest(self.url, cookieReg = self.cookieReg)
        self.listener.onWebpageGetterResourceStarted(self.url, u"text/xhtml") #$NON-NLS-1$
        if download.send(None):
            # Now find all dependencies, and download those too.
            content = download.getResponse()
            self._saveFileContent(rootFile, content)
            self.listener.onWebpageGetterResourceComplete(self.url)
            finder = ZXhtmlDependencyFinder(content)
            dependencies = finder.findDependencies()
            baseHref = finder.getBaseHref()
            if baseHref is None:
                baseHref = self.url
            self.listener.onWebpageGetterFoundDependencies(self.url, dependencies)
            for dependency in dependencies:
                href = urlparse.urljoin(baseHref, dependency.getHref())
                
                # Skip this dependency if it is not an http or https guy.
                if href is None or not href.lower().startswith(u"http"): #$NON-NLS-1$
                    continue

                resourceFile = None
                if dependency.getType() == IZResourceDependencyTypes.IMAGE:
                    resourceFile = self._saveImage(href)
                elif dependency.getType() == IZResourceDependencyTypes.SCRIPT:
                    resourceFile = self._saveScript(href)
                    self._addResourceToFixup(resourceFile)
                elif dependency.getType() == IZResourceDependencyTypes.CSS:
                    resourceFile = self._saveCSS(href)
                    self._addResourceToFixup(resourceFile)
                if resourceFile:
                    self.downloadedHrefs.add(href)
                    self.resourceMap[dependency.getHref()] = resourceFile

        # Now fix up all of the downloaded resources by replacing the hrefs in
        # them with the new local hrefs found in the resourceMap.
        self._fixupAllHrefs()
        
        return rootFile
    # end _saveAsWebpage()

    def _saveCSS(self, cssHref):
        # Try to do css files only once.
        if cssHref in self.downloadedHrefs:
            return

        fileName = self._generateResourceName(self.cssDir, cssHref, IZResourceDependencyTypes.CSS)
        download = ZSimpleTextHTTPRequest(cssHref, cookieReg = self.cookieReg)
        self.listener.onWebpageGetterResourceStarted(cssHref, IZResourceDependencyTypes.CSS)
        if download.send(None):
            cssContent = download.getResponse()
            self._saveFileContent(fileName, cssContent)
            self.listener.onWebpageGetterResourceComplete(cssHref)
            finder = ZCSSDependencyFinder(cssContent)
            dependencies = finder.findDependencies()
            self.listener.onWebpageGetterFoundDependencies(cssHref, dependencies)
            for dependency in dependencies:
                href = urlparse.urljoin(cssHref, dependency.getHref())
                resourceFile = None
                if dependency.getType() == IZResourceDependencyTypes.IMAGE:
                    resourceFile = self._saveImage(href)
                elif dependency.getType == IZResourceDependencyTypes.CSS:
                    resourceFile = self._saveCSS(href)
                    self._addResourceToFixup(resourceFile)
                if resourceFile:
                    self.downloadedHrefs.add(href)
                    self.resourceMap[dependency.getHref()] = resourceFile
        else:
            return None
#            raise ZException(_extstr(u"httpdownload.FailedToDownloadCSS") % cssHref) #$NON-NLS-1$
        return fileName
    # end _saveCSS()

    def _saveScript(self, href):
        # Try to do scripts only once.
        if href in self.downloadedHrefs:
            return

        fileName = self._generateResourceName(self.otherDir, href, IZResourceDependencyTypes.SCRIPT)
        download = ZSimpleTextHTTPRequest(href, cookieReg = self.cookieReg)
        self.listener.onWebpageGetterResourceStarted(href, IZResourceDependencyTypes.SCRIPT)
        if download.send(None):
            self._saveFileContent(fileName, download.getResponse())
            self.listener.onWebpageGetterResourceComplete(href)
            return fileName
        else:
            return None
#            raise ZException(_extstr(u"httpdownload.FailedToDownloadScript") % href) #$NON-NLS-1$
    # end _saveScript()

    def _saveImage(self, href):
        # Try to do images only once.
        if href in self.downloadedHrefs:
            return

        fileName = self._generateResourceName(self.imagesDir, href, IZResourceDependencyTypes.IMAGE)
        listener = ZBinaryToWebpageGetterAdapterListener(href, self.listener)
        download = ZHttpBinaryFileDownload(href, fileName, listener)
        self.listener.onWebpageGetterResourceStarted(href, IZResourceDependencyTypes.IMAGE)
        if download.send(None):
            return fileName
        else:
            return None
#            raise ZException(_extstr(u"httpdownload.FailedToDownloadImage") % href) #$NON-NLS-1$
    # end _saveImage()

    def _addResourceToFixup(self, resource):
        if resource:
            self.resourcesToFixup.add(resource)
    # end _addResourceToFixup()

    def _fixupAllHrefs(self):
        hrefs = ZSortedSet(ZHrefLengthComparator())
        for href in self.resourceMap:
            hrefs.add(href)
        for resource in self.resourcesToFixup:
            self._fixupHrefs(resource, hrefs)
    # end _fixupAllHrefs()

    def _fixupHrefs(self, fileName, hrefs):
        content = self._loadFileContent(fileName)
        if content:
            for href in hrefs:
                newHref = None
                filePath = self.resourceMap[href]
                if self.basePathToken is not None:
                    relativeFilePath = makeRelativePath(self.outputDir, filePath)
                    newHref = u"file://" + self.basePathToken + u"/" + relativeFilePath.replace(u"\\", u"/") #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$ #$NON-NLS-4$
                else:
                    newHref = u"file://" + filePath.replace(u"\\", u"/") #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$
                content = content.replace(href, newHref)
        self._saveFileContent(fileName, content)
    # end _fixupHrefs()

    def _getUrlFileExtension(self, href):
        zurl = ZUrl(href)
        fileName = zurl.getFile()
        if fileName:
            return os.path.splitext(fileName)[1]
        else:
            return u".unk" #$NON-NLS-1$
    # end _getUrlFileExtension()

    def _loadFileContent(self, file):
        return getFileContents(file)
    # end _loadFileContent()

    def _saveFileContent(self, file, content):
        file = codecs.open(file, u"w", u"utf-8") #$NON-NLS-1$ #$NON-NLS-2$
        try:
            file.write(content)
        finally:
            file.close()
    # end _saveFileContent()

    # Generate a resource name.  Try to base it off of the URL (for URLs
    # that have a filename component).  If that doesn't work, then simply
    # generate a guid and use that.
    def _generateResourceName(self, outputDir, url, type = u"text/html"): #$NON-NLS-1$
        url = ZUrl(url)
        file = url.getFile()
        if file and u"." in file: #$NON-NLS-1$
            baseName = os.path.basename(file)
            path = os.path.join(outputDir, baseName)
            count = 1
            while os.path.exists(path):
                (fname, ext) = os.path.splitext(baseName)
                path = os.path.join(outputDir, u"%s-%d%s" % (fname, count, ext)) #$NON-NLS-1$
            return path
        else:
            ext = u".html" #$NON-NLS-1$
            if type == IZResourceDependencyTypes.CSS:
                ext = u".css" #$NON-NLS-1$
            elif type == IZResourceDependencyTypes.SCRIPT:
                ext = u".js" #$NON-NLS-1$
            elif type == IZResourceDependencyTypes.IMAGE:
                ext = u".bin" #$NON-NLS-1$
            return os.path.join(outputDir, generate() + ext)
    # end _generateResourceName()

# end ZHttpWebpageGetter
