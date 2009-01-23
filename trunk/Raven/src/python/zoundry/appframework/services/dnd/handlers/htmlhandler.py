from zoundry.appframework.messages import _extstr
from zoundry.appframework.services.dnd.dnd import IZDnDHandler
from zoundry.appframework.services.dnd.dndsource import IZDnDSourceTypes

# ------------------------------------------------------------------------------
# Base class for the image file DnD Handlers.
# ------------------------------------------------------------------------------
class ZHtmlDnDHandler(IZDnDHandler):

    def getName(self):
        return _extstr(u"htmlhandler.HTML") #$NON-NLS-1$
    # end getName()

    def getDescription(self):
        return _extstr(u"htmlhandler.HTMLDesc") #$NON-NLS-1$
    # end getDescription()

    def canHandle(self, dndSource):
        return dndSource.hasType(IZDnDSourceTypes.TYPE_HTML)
    # end canHandle()

    def handle(self, dndSource, dndContext): #@UnusedVariable
        htmlSource = dndSource.getSource(IZDnDSourceTypes.TYPE_HTML)
        return htmlSource.getData().serialize()
    # end handle()

# end ZHtmlDnDHandler
