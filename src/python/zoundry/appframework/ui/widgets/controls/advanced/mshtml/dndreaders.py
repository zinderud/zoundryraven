from struct import unpack
from zoundry.appframework.services.dnd.dndsource import ZFileDnDSource
from zoundry.appframework.services.dnd.dndsource import ZHtmlDnDSource
from zoundry.appframework.services.dnd.dndsource import ZMultiFileDnDSource
from zoundry.appframework.services.dnd.dndsource import ZUrlDnDSource
from zoundry.base.zdom.dom import ZDom
from zoundry.blogapp.services.dnd.dndimpl import ZBlogPostDnDSource
from zoundry.blogapp.ui.dnd.dnd import IZDnDFormats
from zoundry.base.util.text.unicodeutil import convertToUnicode
import os
import re
import string
import win32api
import win32clipboard
import win32con
from win32com.shell import shell #@UnresolvedImport


MARKER_BLOCK_EX = u"Version:(\S+)\s+StartHTML:(\d+)\s+EndHTML:(\d+)\s+StartFragment:(\d+)\s+EndFragment:(\d+)\s+StartSelection:(\d+)\s+EndSelection:(\d+)\s+SourceURL:(\S+)" #$NON-NLS-1$
MARKER_BLOCK_EX_RE = re.compile(MARKER_BLOCK_EX)
MARKER_BLOCK = u"Version:(\S+)\s+StartHTML:(\d+)\s+EndHTML:(\d+)\s+StartFragment:(\d+)\s+EndFragment:(\d+)\s+SourceURL:(\S+)" #$NON-NLS-1$
MARKER_BLOCK_RE = re.compile(MARKER_BLOCK)


# ------------------------------------------------------------------------------
# Interface that must be implemented by a drag and drop source reader.  The
# DnD source reader is given the windows storage medium STGMEDIUM instance,
# and it will return an instance of IZDnDSource.
# ------------------------------------------------------------------------------
class IZDnDSourceReader:

    def getClipboardFormat(self):
        u"""getClipboardFormat() -> CF_FORMAT""" #$NON-NLS-1$
    # end getClipboardFormat()

    def readDnDSource(self, stgMedium):
        u"""readDnDSource(STGMEDIUM) -> IZDnDSource""" #$NON-NLS-1$
    # end readDnDSource()

# end IZDnDSourceReader


# ------------------------------------------------------------------------------
# Base class for the DnD source readers.  Has some common functionality.
# ------------------------------------------------------------------------------
class ZBaseDnDSourceReader(IZDnDSourceReader):
    
    def _getCFFormatCode(self, cfFormatName):
        try:
            return win32clipboard.RegisterClipboardFormat(cfFormatName)
        except:
            return -1
    # end _getCFFormatCode()

# end ZBaseDnDSourceReader


# ------------------------------------------------------------------------------
# Reads HTML from the storage medium.
# ------------------------------------------------------------------------------
class ZHtmlDnDSourceReader(ZBaseDnDSourceReader):

    def __init__(self):
        self.format = self._getCFFormatCode(u"HTML Format") #$NON-NLS-1$
    # end __init__()

    def getClipboardFormat(self):
        return self.format
    # end getClipboardFormat()

    def readDnDSource(self, stgMedium):
        fmtstring = unicode(len(stgMedium.data)) + u"s" #$NON-NLS-1$
        dataTuple = unpack(fmtstring, stgMedium.data)
        cfhtml = dataTuple[0]
        html = self._decodeCfHtml(cfhtml)
        htmlDom = ZDom()
        rootNode = None
        try:
            htmlDom.loadHTML(html)
            rootNode = htmlDom.selectSingleNode(u"/*") #$NON-NLS-1$
        except:
            # Probably an encoding problem of some sort - just
            # return None (we are going to let IE handle it anyway)
            pass

        return ZHtmlDnDSource(rootNode)
    # end readDnDSource()

    def _decodeCfHtml(self, cfHtml):
        cfHtml = convertToUnicode(cfHtml)

        # Try the extended format first (which has an explicit selection)
        matches = MARKER_BLOCK_EX_RE.match(cfHtml)
        if matches:
            html = cfHtml[int(matches.group(6)):int(matches.group(7))]
            return html
        else:
            # Failing that, try the version without a selection
            matches = MARKER_BLOCK_RE.match(cfHtml)
            if matches:
                html = cfHtml[int(matches.group(4)):int(matches.group(5))]
                return html
        return None
    # end _decodeCfHtml()

# end ZHtmlDnDSourceReader


# ------------------------------------------------------------------------------
# Reads a URL from the storage medium.
# ------------------------------------------------------------------------------
class ZUrlDnDSourceReader(ZBaseDnDSourceReader):

    def __init__(self):
        self.format = self._getCFFormatCode(u"UniformResourceLocator") #$NON-NLS-1$
    # end __init__()

    def getClipboardFormat(self):
        return self.format
    # end getClipboardFormat()

    def readDnDSource(self, stgMedium):
        url = stgMedium.data
        url = string.replace(url, chr(0), u"") #$NON-NLS-1$
        return ZUrlDnDSource(url)
    # end readDnDSource()

# end ZUrlDnDSourceReader


# ------------------------------------------------------------------------------
# Reads a URL from the storage medium.
# ------------------------------------------------------------------------------
class ZHDropDnDSourceReader(ZBaseDnDSourceReader):

    def getClipboardFormat(self):
        return win32con.CF_HDROP
    # end getClipboardFormat()

    def readDnDSource(self, stgMedium):
        filePaths = self._getDropFileList(stgMedium)
        if filePaths:
            if len(filePaths) == 1:
                return ZFileDnDSource(filePaths[0])
            else:
                return ZMultiFileDnDSource(filePaths)
        return None
    # end readDnDSource()

    def _getDropFileList(self, stgMedium):
        rval = []
        hDropInfo = stgMedium.data_handle
        nFiles = win32api.DragQueryFile(hDropInfo)
        try:
            for iFile in range(0, nFiles):
                filepath = shell.DragQueryFileW(hDropInfo, iFile)
                filepath = os.path.abspath(filepath)
                fileExists = os.path.exists(filepath)
                if fileExists:
                    rval.append(filepath)
        finally:
            win32api.DragFinish(hDropInfo);
            return rval
    # end _getDropFileList()

# end ZHDropDnDSourceReader


# ------------------------------------------------------------------------------
# Reads a blog post/document from the storage medium.
# ------------------------------------------------------------------------------
class ZBlogPostDnDSourceReader(ZBaseDnDSourceReader):

    def getClipboardFormat(self):
        return IZDnDFormats.DND_FORMAT_BLOGPOST_INTERNAL.GetType()
    # end getClipboardFormat()

    def readDnDSource(self, stgMedium):
        documentId = stgMedium.data
        # FIXME (EPW) we are using a blogapp object here, in an appframework class - create an extension point for the list of readers...
        return ZBlogPostDnDSource(documentId)
    # end readDnDSource()

# end ZBlogPostDnDSourceReader
