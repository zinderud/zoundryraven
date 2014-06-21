from zoundry.appframework.services.dnd.handlers.filehandler import ZMultiFileDnDHandler
from zoundry.appframework.services.dnd.handlers.filehandler import ZFileDnDHandler
from zoundry.appframework.constants import IZAppExtensionPoints
from zoundry.appframework.constants import IZAppServiceIDs
from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.services.dnd.dnd import IZDnDContext
from zoundry.appframework.services.dnd.dnd import IZDnDService
from zoundry.appframework.services.dnd.dnddef import ZDnDHandlerDef
from zoundry.appframework.services.dnd.handlers.imagehandler import ZImageFileDnDHandler
from zoundry.appframework.services.dnd.handlers.imagehandler import ZMultiImageFileDnDHandler
from zoundry.appframework.services.dnd.handlers.linkhandlers.ifilm import ZiFilmLinkDnDHandler
from zoundry.appframework.services.dnd.handlers.linkhandlers.photobucket import ZPhotoBucketLinkDnDHandler
from zoundry.appframework.services.dnd.handlers.linkhandlers.piratr import ZPiratrLinkDnDHandler
from zoundry.appframework.services.dnd.handlers.linkhandlers.slide import ZSlideLinkDnDHandler
from zoundry.appframework.services.dnd.handlers.linkhandlers.veoh import ZVeohLinkDnDHandler
from zoundry.appframework.services.dnd.handlers.linkhandlers.vsocial import ZVSocialLinkDnDHandler
from zoundry.appframework.services.dnd.handlers.linkhandlers.youtube import ZYouTubeLinkDnDHandler


# ------------------------------------------------------------------------------
# A base implementation of a DnD context.
# ------------------------------------------------------------------------------
class ZDnDContext(IZDnDContext):

    def __init__(self, window):
        self.window = window
    # end __init__()

    def getWindow(self):
        return self.window
    # end getWindow()

# end ZDnDContext


# ------------------------------------------------------------------------------
# Implementation of the Drag & Drop service.
# ------------------------------------------------------------------------------
class ZDnDService(IZDnDService):

    def __init__(self):
        self.handlers = []
    # end __init__()

    def start(self, applicationModel):
        self.logger = applicationModel.getEngine().getService(IZAppServiceIDs.LOGGER_SERVICE_ID)
        self.handlers = self._loadHandlers()
        self.logger.debug(u"DnD Service started [%d handlers loaded]." % len(self.handlers)) #$NON-NLS-1$
    # end start()

    def stop(self):
        self.handlers = []
    # end stop()

    def _loadHandlers(self):
        handlers = []

        contributedHandlers = getApplicationModel().getPluginRegistry().getExtensions(IZAppExtensionPoints.ZEP_DRAG_AND_DROP_HANDLER)
        dndHandlerDefs = map(ZDnDHandlerDef, contributedHandlers)
        for handlerDef in dndHandlerDefs:
            handlers.append(handlerDef.createHandler())

        handlers.append(ZYouTubeLinkDnDHandler())
#        handlers.append(ZGoogleVideoLinkDnDHandler())
        handlers.append(ZVeohLinkDnDHandler())
        handlers.append(ZiFilmLinkDnDHandler())
        handlers.append(ZVSocialLinkDnDHandler())
        handlers.append(ZPhotoBucketLinkDnDHandler())
        handlers.append(ZSlideLinkDnDHandler())
        handlers.append(ZPiratrLinkDnDHandler())
        handlers.append(ZImageFileDnDHandler())
        handlers.append(ZMultiImageFileDnDHandler())
        handlers.append(ZFileDnDHandler())
        handlers.append(ZMultiFileDnDHandler())
        return handlers
    # end _loadHandlers()

    def getHandlers(self):
        return self.handlers
    # end getHandlers()

    def getMatchingHandlers(self, dndSource):
        handlers = []
        for handler in self.handlers:
            if handler.canHandle(dndSource):
                handlers.append(handler)
        return handlers
    # end getMatchingHandlers()

    def registerHandler(self, dndHandler):
        self.handlers.append(dndHandler)
    # end registerHandler()

# end ZDnDService
