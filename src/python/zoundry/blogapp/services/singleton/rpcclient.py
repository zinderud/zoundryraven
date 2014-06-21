from zoundry.appframework.global_services import getApplicationModel
import xmlrpclib

# ------------------------------------------------------------------------------
# XML-RPC style client that talks to the Raven singleton service.
# ------------------------------------------------------------------------------
class ZRavenRPCClient:

    def __init__(self):
        sysProfile = getApplicationModel().getSystemProfile()
        port = sysProfile.getProperties().getPropertyInt(u"/system-properties/singleton/port", 84113) #$NON-NLS-1$
        self.server = xmlrpclib.ServerProxy(u"http://localhost:%d" % port, allow_none = True) #$NON-NLS-1$
    # end __init__()

    def blogThis(self, blogThisInfo):
        title = blogThisInfo.getTitle()
        url = blogThisInfo.getUrl()
        text = blogThisInfo.getText()
        file = blogThisInfo.getFile()
        author = blogThisInfo.getAuthor()
        format = blogThisInfo.getFormat()
        isAutoDiscover = blogThisInfo.isAutoDiscover()
        isQuoted = blogThisInfo.isQuoted()

        try:
            return self.server.blogThis(title, url, text, file, author, format, isAutoDiscover, isQuoted)
        except:
            return False
    # end blogThis()

    def getVersion(self):
        try:
            return self.server.getVersion()
        except:
            return None
    # end blogThis()

    def bringToFront(self):
        try:
            return self.server.bringToFront()
        except:
            return None
    # end bringToFront()

# end ZRavenRPCClient

