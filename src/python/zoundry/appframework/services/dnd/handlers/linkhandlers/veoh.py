from zoundry.appframework.messages import _extstr
from zoundry.appframework.services.dnd.handlers.linkhandlers.commonvideo import ZBaseVideoLinkDnDHandler

PATTERN = r"http://www.veoh.com/videos/(.*)$" #$NON-NLS-1$

TEMPLATE = u"""<embed src="http://www.veoh.com/videodetails2.swf?permalinkId=%(video-id)s&id=anonymous&player=videodetailsembedded&videoAutoPlay=0" allowFullScreen="true" width="540" height="438" bgcolor="#000000" type="application/x-shockwave-flash" pluginspage="http://www.macromedia.com/go/getflashplayer"></embed>""" #$NON-NLS-1$


# ------------------------------------------------------------------------------
# Handles Veoh links for Drag and Drop.
# ------------------------------------------------------------------------------
class ZVeohLinkDnDHandler(ZBaseVideoLinkDnDHandler):

    def __init__(self):
        patterns = [ PATTERN ]
        ZBaseVideoLinkDnDHandler.__init__(self, patterns, TEMPLATE)
    # end __init__()

    def getName(self):
        return _extstr(u"veoh.VeohVideo") #$NON-NLS-1$
    # end getName()

    def getDescription(self):
        return _extstr(u"veoh.VeohVideoDesc") #$NON-NLS-1$
    # end getDescription()

# end ZVeohLinkDnDHandler
