from zoundry.appframework.messages import _extstr
from zoundry.appframework.services.dnd.handlers.linkhandlers.commonvideo import ZBaseRemoteVideoLinkDnDHandler

PATTERN = r"http://www.vsocial.com/video/.d=(.*)$" #$NON-NLS-1$

XPATH = r"//xhtml:textarea[@class = 'embedblocktext']" #$NON-NLS-1$

# ------------------------------------------------------------------------------
# Handles VSocial links for Drag and Drop.
# ------------------------------------------------------------------------------
class ZVSocialLinkDnDHandler(ZBaseRemoteVideoLinkDnDHandler):

    def getName(self):
        return _extstr(u"vsocial.VSocialVideo") #$NON-NLS-1$
    # end getName()

    def getDescription(self):
        return _extstr(u"vsocial.VSocialVideoDesc") #$NON-NLS-1$
    # end getDescription()

    def __init__(self):
        patterns = [ PATTERN ]
        ZBaseRemoteVideoLinkDnDHandler.__init__(self, patterns, XPATH)
    # end __init__()

# end ZVSocialLinkDnDHandler
