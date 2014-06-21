from zoundry.appframework.messages import _extstr
from zoundry.appframework.services.dnd.handlers.linkhandlers.commonvideo import ZBaseRemoteVideoLinkDnDHandler
from zoundry.base.net.http import ZSimpleTextHTTPRequest
from zoundry.base.zdom.dom import ZDom
import re

PATTERN = r"http://www.slide.com/r/(.*)$" #$NON-NLS-1$

EMBED = u"""(<input type="text" name="embedCode" id="embedCode" .* />)""" #$NON-NLS-1$
EMBED_PATTERN = re.compile(EMBED, re.IGNORECASE | re.UNICODE)

# ------------------------------------------------------------------------------
# Handles Slide links for Drag and Drop.
# ------------------------------------------------------------------------------
class ZSlideLinkDnDHandler(ZBaseRemoteVideoLinkDnDHandler):

    def __init__(self):
        patterns = [ PATTERN ]
        ZBaseRemoteVideoLinkDnDHandler.__init__(self, patterns, None)
    # end __init__()

    def getName(self):
        return _extstr(u"slide.SlideSlideshow") #$NON-NLS-1$
    # end getName()

    def getDescription(self):
        return _extstr(u"slide.SlideSlideshowDesc") #$NON-NLS-1$
    # end getDescription()

    def _createRequest(self, url):
        return ZSimpleTextHTTPRequest(url)
    # end _createRequest()

    def _extractEmbedMarkup(self, xhtmlReq):
        resp = xhtmlReq.getResponse()
        match = EMBED_PATTERN.search(resp)
        if match is not None:
            inputMarkup = match.group(1)
            dom = ZDom()
            dom.loadXML(inputMarkup)
            embedStr = dom.documentElement.getAttribute(u"value") #$NON-NLS-1$
            return embedStr
        else:
            return None
    # end _extractEmbedMarkup()

# end ZSlideLinkDnDHandler
