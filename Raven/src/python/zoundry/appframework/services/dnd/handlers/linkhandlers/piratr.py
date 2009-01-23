from zoundry.appframework.messages import _extstr
from zoundry.appframework.services.dnd.handlers.linkhandlers.commonvideo import ZBaseVideoLinkDnDHandler

PATTERN1 = r"http://w?w?w?.?piratr.com/action/viewvideo/([^/]+)/.*$" #$NON-NLS-1$
PATTERN2 = u"http://w?w?w?.?piratr.com/members/action/viewvideo/([^/]+)/.*$" #$NON-NLS-1$

TEMPLATE = u"""<embed src="http://piratr.com/flvplayer.swf" FlashVars="config=http://piratr.com/videoConfigXmlCode.php?pg=video_%(video-id)s_no_0" quality="high" bgcolor="#000000" width="450" height="370" name="flvplayer" align="middle" allowScriptAccess="always" type="application/x-shockwave-flash" pluginspage="http://www.macromedia.com/go/getflashplayer" allowFullScreen="true" />""" #$NON-NLS-1$


# ------------------------------------------------------------------------------
# Handles Piratr links for Drag and Drop.
# ------------------------------------------------------------------------------
class ZPiratrLinkDnDHandler(ZBaseVideoLinkDnDHandler):

    def __init__(self):
        patterns = [ PATTERN1, PATTERN2 ]
        ZBaseVideoLinkDnDHandler.__init__(self, patterns, TEMPLATE)
    # end __init__()

    def getName(self):
        return _extstr(u"piratr.PiratrVideo") #$NON-NLS-1$
    # end getName()

    def getDescription(self):
        return _extstr(u"piratr.PiratrVideoDesc") #$NON-NLS-1$
    # end getDescription()

# end ZPiratrLinkDnDHandler
