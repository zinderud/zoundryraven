from zoundry.appframework.messages import _extstr
from zoundry.appframework.services.dnd.handlers.linkhandlers.commonvideo import ZBaseVideoLinkDnDHandler

PATTERN = r"http://www.ifilm.com/video/(.*)$" #$NON-NLS-1$

TEMPLATE = u"""<embed width="448" height="365" src="http://www.ifilm.com/efp" quality="high" bgcolor="000000" name="efp" align="middle" type="application/x-shockwave-flash" pluginspage="http://www.macromedia.com/go/getflashplayer" flashvars="flvbaseclip=%(video-id)s&"></embed>""" #$NON-NLS-1$


# ------------------------------------------------------------------------------
# Handles iFilm links for Drag and Drop.
# ------------------------------------------------------------------------------
class ZiFilmLinkDnDHandler(ZBaseVideoLinkDnDHandler):

    def __init__(self):
        patterns = [ PATTERN ]
        ZBaseVideoLinkDnDHandler.__init__(self, patterns, TEMPLATE)
    # end __init__()

    def getName(self):
        return _extstr(u"ifilm.iFilmVideo") #$NON-NLS-1$
    # end getName()

    def getDescription(self):
        return _extstr(u"ifilm.iFilmVideoDesc") #$NON-NLS-1$
    # end getDescription()


# end ZiFilmLinkDnDHandler
