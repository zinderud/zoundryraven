from zoundry.appframework.engine.service import IZService

# ------------------------------------------------------------------------------
# Accessor interface - used by clients wanting to connect and communicate with
# the singleton service on another running instance of the application.
# ------------------------------------------------------------------------------
class IZSingletonServiceAccessor:

    def connect(self):
        u"""connect() -> boolean
        Initiates a connection to the singleton service TCP
        server.  If no connection can be made, returns False.""" #$NON-NLS-1$
    # end connect()

# end IZSingletonServiceAccessor


# ------------------------------------------------------------------------------
# The listener interface for listening to events that are fired by the singleton
# service.
# ------------------------------------------------------------------------------
class IZSingletonServiceListener:
    
    def onBlogThis(self, blogThisData):
        u"""onBlogThis(IZBlogThisInformation) -> None
        Called when the singleton service receives a Blog This
        message from another instance of the application.""" #$NON-NLS-1$
    # end onBlogThis()
    
# end IZSingletonServiceListener


# ------------------------------------------------------------------------------
# This interface defines the singleton service.  The singleton service is
# responsible for providing a way to ensure that only one instance of the
# application is running at a time.  It accomplishes this task by creating a
# TCP server which listens for connections.  When the application starts up,
# it first tries to connect to that TCP server.  If it can connect, then it
# knows another instance of the application is running.
#
# The service is also responsible for receiving commands from other instances
# of the application.  The use case is for the "Blog This" feature.  This
# feature allows users to launch the application with some command line params
# that cause a new Blog Post to be created.
# ------------------------------------------------------------------------------
class IZSingletonService(IZService):

    def addListener(self, listener):
        u"""addListener(IZSingletonServiceListener) -> None""" #$NON-NLS-1$
    # end addListener()

    def removeListener(self, listener):
        u"""removeListener(IZSingletonServiceListener) -> None""" #$NON-NLS-1$
    # end removeListener()

# end IZSingletonService
