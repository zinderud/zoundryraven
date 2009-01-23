from zoundry.appframework.engine.service import IZService

# ------------------------------------------------------------------------------
# The context that gets passed to the DnD handler.
# ------------------------------------------------------------------------------
class IZDnDContext:

    def getWindow(self):
        u"""getWindow() -> wx.Widget
        Returns the wx window that should be used as the
        parent of any dialogs that the DnD handler might
        need to create.""" #$NON-NLS-1$
    # end getWindow()

# end IZDnDContext


# ------------------------------------------------------------------------------
# A handler that is responsible for creating XHTML content given some data in a
# IZDnDSource object.
# ------------------------------------------------------------------------------
class IZDnDHandler:

    def getName(self):
        u"""getName() -> string
        Returns the name of the handler.""" #$NON-NLS-1$
    # end getName()

    def getDescription(self):
        u"""getDescription() -> string
        Gets the description of the handler.""" #$NON-NLS-1$
    # end getDescription()

    def canHandle(self, dndSource):
        u"""canHandle(IZDnDSource) -> boolean
        Returns True if this handler can handle DnD content
        found in the given IZDnDSource.""" #$NON-NLS-1$
    # end canHandle()

    def handle(self, dndSource, dndContext):
        u"""handle(IZDnDSource, IZDnDContext) -> ZXhtmlDocument
        Given the IZDnDSource, generates XHTML content and
        returns it.""" #$NON-NLS-1$
    # end handle()

# end IZDnDHandler


# ------------------------------------------------------------------------------
# This interface defines the Drag & Drop service.  The Drag & Drop service is
# responsible for managing contributed and built-in Drag & Drop handlers.  A
# Drag & Drop handler is used when the user is Dropping some content onto an
# editor.  Each handler is responsible for generating XHTML data given an
# IZDnDSource object (typically created by the drop target of a particular
# editor.
# ------------------------------------------------------------------------------
class IZDnDService(IZService):

    def getHandlers(self):
        u"""getHandlers() -> IZDnDHandler[]
        Returns a list of all the DnD handlers registered
        with the service.""" #$NON-NLS-1$
    # end getHandlers()

    def getMatchingHandlers(self, dndSource):
        u"""getMatchingHandlers(IZDnDSource) -> IZDnDHandler[]
        Returns all of the handlers that are capable of
        handling the data found in the given IZDnDSource.
        Returns an empty list if no capable handlers are
        found.""" #$NON-NLS-1$
    # end getMatchingHandlers()

    def registerHandler(self, dndHandler):
        u"""registerHandler(IZDnDHandler) -> None
        Registers the given handler with the service.""" #$NON-NLS-1$
    # end registerHandler()

# end IZDnDService
