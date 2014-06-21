from zoundry.appframework.messages import _extstr
from zoundry.appframework.services.dnd.handlers.linkhandlers.commonvideo import ZBaseVideoLinkDnDHandler

PATTERN = r"http://video.google.com/videoplay.docid=(.*)$" #$NON-NLS-1$

# ------------------------------------------------------------------------------
# Handles Google Video links for Drag and Drop.
# ------------------------------------------------------------------------------
class ZGoogleVideoLinkDnDHandler(ZBaseVideoLinkDnDHandler):

    def __init__(self):
        patterns = [ PATTERN ]
        ZBaseVideoLinkDnDHandler.__init__(self, patterns, None)
    # end __init__()

    def getName(self):
        return _extstr(u"googlevideo.GoogleVideo") #$NON-NLS-1$
    # end getName()

    def getDescription(self):
        return _extstr(u"googlevideo.GoogleVideoDesc") #$NON-NLS-1$
    # end getDescription()

    def handle(self, dndSource, dndContext): #@UnusedVariable
#        urlSource = dndSource.getSource(IZDnDSourceTypes.TYPE_URL)
#        url = urlSource.getData()
#        xhtmlReq = ZSimpleXHtmlHTTPRequest(url)
#        if xhtmlReq.send():
#            resp = xhtmlReq.getResponse()
#            print resp
        return u"Not yet implemented!" #$NON-NLS-1$
    # end handle()

# end ZGoogleVideoLinkDnDHandler
