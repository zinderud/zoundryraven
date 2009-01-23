from zoundry.appframework.messages import _extstr
from zoundry.appframework.services.dnd.handlers.linkhandlers.commonvideo import ZBaseVideoLinkDnDHandler

PATTERN = r"http://.*.photobucket.com/albums/.*action=view.current=(.*).[pf][bl][rv]$" #$NON-NLS-1$

TEMPLATE = u"""<embed width="448" height="361" type="application/x-shockwave-flash" wmode="transparent" src="http://i0006.photobucket.com/remix/player.swf?videoURL=http%%3A%%2F%%2Fvid0006.photobucket.com%%2Falbums%%2F0006%%2Fpbhomepage%%2Fremix%%2F%(video-id)s.pbr&amp;hostname=stream0006.photobucket.com"></embed>""" #$NON-NLS-1$


# ------------------------------------------------------------------------------
# Handles Photobucket links for Drag and Drop.
# ------------------------------------------------------------------------------
class ZPhotoBucketLinkDnDHandler(ZBaseVideoLinkDnDHandler):

    def __init__(self):
        patterns = [ PATTERN ]
        ZBaseVideoLinkDnDHandler.__init__(self, patterns, TEMPLATE)
    # end __init__()

    def getName(self):
        return _extstr(u"photobucket.PhotoBucketVideo") #$NON-NLS-1$
    # end getName()

    def getDescription(self):
        return _extstr(u"photobucket.PhotoBucketVideoDesc") #$NON-NLS-1$
    # end getDescription()

# end ZPhotoBucketLinkDnDHandler
