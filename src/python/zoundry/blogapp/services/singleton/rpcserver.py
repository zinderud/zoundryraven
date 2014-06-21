from zoundry.appframework.global_services import getApplicationModel
from zoundry.blogapp.blogthis import ZBlogThisInformation

# ------------------------------------------------------------------------------
# Server implementation of the Blog This feature.
# ------------------------------------------------------------------------------
class ZRavenRPCServer:

    def __init__(self, listener):
        self.listener = listener
    # end __init__()

    def blogThis(self, title, url, text, file, author, format, isAutoDiscover, isQuoted):
        blogThis = ZBlogThisInformation(title, url, text, file, author, format, isAutoDiscover, isQuoted)
        self.listener.onBlogThis(blogThis)
        return True
    # end blogThis()

    def getVersion(self):
        version = getApplicationModel().getVersion()
        return version.getFullVersionString()
    # end getVersion()

    def bringToFront(self):
        window = getApplicationModel().getTopWindow()
        window.Raise()
        window.SetFocus()
    # end bringToFront()

# end ZRavenRPCServer
