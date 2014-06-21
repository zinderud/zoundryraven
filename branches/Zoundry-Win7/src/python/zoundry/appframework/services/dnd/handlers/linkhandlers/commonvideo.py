from zoundry.appframework.messages import _extstr
from zoundry.appframework.services.dnd.dnd import IZDnDHandler
from zoundry.appframework.services.dnd.dndsource import IZDnDSourceTypes
from zoundry.appframework.ui.widgets.dialogs.standarddialogs import ZShowInfoMessage
from zoundry.base.xhtml.xhtmldoc import XHTML_NAMESPACE
from zoundry.base.xhtml.xhtmlnet import ZSimpleXHtmlHTTPRequest
from zoundry.base.zdom.dom import ZDom
import re
import string
import wx

NSS_MAP = {
    u"xhtml" : XHTML_NAMESPACE #$NON-NLS-1$
}

# ------------------------------------------------------------------------------
# Base class that handles dropping of video links.
# ------------------------------------------------------------------------------
class ZBaseVideoLinkDnDHandler(IZDnDHandler):

    def __init__(self, patternStrs, template):
        self.template = template

        self.patterns = []
        for patternStr in patternStrs:
            self.patterns.append(re.compile(patternStr, re.IGNORECASE | re.UNICODE))
    # end __init__()

    def canHandle(self, dndSource):
        if dndSource.hasType(IZDnDSourceTypes.TYPE_URL):
            urlSource = dndSource.getSource(IZDnDSourceTypes.TYPE_URL)
            url = urlSource.getData()
            for pattern in self.patterns:
                if pattern.match(url) is not None:
                    return True
        return False
    # end canHandle()

    def handle(self, dndSource, dndContext): #@UnusedVariable
        urlSource = dndSource.getSource(IZDnDSourceTypes.TYPE_URL)
        url = urlSource.getData()
        videoId = None
        for pattern in self.patterns:
            match = pattern.match(url)
            if match is not None:
                videoId = match.group(1)
                break

        params = { u"video-id" : videoId } #$NON-NLS-1$
        html = self.template % params
        return html
    # end handle()

# end ZBaseVideoLinkDnDHandler


# ------------------------------------------------------------------------------
# Handles VSocial links for Drag and Drop.
# ------------------------------------------------------------------------------
class ZBaseRemoteVideoLinkDnDHandler(ZBaseVideoLinkDnDHandler):

    def __init__(self, patternStrs, xpath):
        self.xpath = xpath

        ZBaseVideoLinkDnDHandler.__init__(self, patternStrs, None)
    # end __init__()

    def handle(self, dndSource, dndContext): #@UnusedVariable
        bc = wx.BusyCursor()

        try:
            return self._doHandle(dndSource, dndContext)
        finally:
            del bc
    # end handle()

    def _doHandle(self, dndSource, dndContext):
        urlSource = dndSource.getSource(IZDnDSourceTypes.TYPE_URL)
        url = urlSource.getData()
        xhtmlReq = self._createRequest(url)
        if xhtmlReq.send():
            return self._extractEmbedMarkup(xhtmlReq)
        else:
            return self._doHandleError(url, dndContext)
    # end _doHandle()

    def _createRequest(self, url):
        return ZSimpleXHtmlHTTPRequest(url)
    # end _createRequest()
    
    def _extractEmbedMarkup(self, xhtmlReq):
        xhtmlDoc = xhtmlReq.getResponse()
        zdom = xhtmlDoc.getDom()
        embedStr = zdom.selectSingleNodeText(self.xpath, None, NSS_MAP)
        return string.strip(embedStr)
    # end _extractEmbedMarkup()

    def _doHandleError(self, url, dndContext):
        ZShowInfoMessage(dndContext.getWindow(), _extstr(u"commonvideo.ErrorDiscoveringVideoEmbedInfoMsg"), _extstr(u"commonvideo.ErrorDiscoveringVideoEmbedInfoTitle")) #$NON-NLS-2$ #$NON-NLS-1$
        dom = ZDom()
        dom.loadXML(u"<a href='' />") #$NON-NLS-1$
        dom.documentElement.setAttribute(u"href", url) #$NON-NLS-1$
        dom.documentElement.setText(url)
        return dom.serialize()
    # end _doHandleError()

# end ZBaseRemoteVideoLinkDnDHandler
