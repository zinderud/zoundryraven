from zoundry.appframework.messages import _extstr
from zoundry.appframework.services.dnd.handlers.linkhandlers.commonvideo import ZBaseVideoLinkDnDHandler

PATTERN1 = r"http://ww..youtube.com/watch.v=(.*)&mode=related&search=$" #$NON-NLS-1$
PATTERN2 = r"http://ww..youtube.com/watch.v=(.*)&feature=dir$" #$NON-NLS-1$
PATTERN3 = r"http://ww..youtube.com/watch.v=(.*)$" #$NON-NLS-1$
PATTERN4 = r"http://youtube.com/watch.v=(.*)$" #$NON-NLS-1$

TEMPLATE = u"""<object width="425" height="350"><param name="movie" value="http://www.youtube.com/v/%(video-id)s"></param><param name="wmode" value="transparent"></param><embed src="http://www.youtube.com/v/%(video-id)s" type="application/x-shockwave-flash" wmode="transparent" width="425" height="350"></embed></object>""" #$NON-NLS-1$

# ------------------------------------------------------------------------------
# Handles YouTube links for Drag and Drop.
# ------------------------------------------------------------------------------
class ZYouTubeLinkDnDHandler(ZBaseVideoLinkDnDHandler):

    def __init__(self):
        patterns = [ PATTERN1, PATTERN2, PATTERN3, PATTERN4 ]
        ZBaseVideoLinkDnDHandler.__init__(self, patterns, TEMPLATE)
    # end __init__()

    def getName(self):
        return _extstr(u"youtube.YouTubeVideo") #$NON-NLS-1$
    # end getName()

    def getDescription(self):
        return _extstr(u"youtube.YouTubeVideoDesc") #$NON-NLS-1$
    # end getDescription()

# end ZYouTubeLinkDnDHandler
