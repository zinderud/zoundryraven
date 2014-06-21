from zoundry.appframework.constants import IZAppServiceIDs
from zoundry.base.util.zthread import IZRunnable
from zoundry.base.util.zthread import ZThread
from zoundry.blogapp.services.singleton.rpcserver import ZRavenRPCServer
from zoundry.blogapp.services.singleton.singleton import IZSingletonService
from zoundry.blogapp.services.singleton.singleton import IZSingletonServiceListener
import SimpleXMLRPCServer

# ------------------------------------------------------------------------------
# Implementation of the mime type service.
# ------------------------------------------------------------------------------
class ZSingletonService(IZSingletonService, IZSingletonServiceListener, IZRunnable):

    def __init__(self):
        self.listeners = []
        self.running = False
    # end __init__()

    def start(self, applicationModel):
        self.applicationModel = applicationModel
        self.logger = self.applicationModel.getEngine().getService(IZAppServiceIDs.LOGGER_SERVICE_ID)

        try:
            self._startListening()
            self.logger.debug(u"Singleton Service started.") #$NON-NLS-1$
        except Exception, e:
            self.logger.exception(e)
            self.logger.error(u"Singleton Service failed to start.") #$NON-NLS-1$
    # end start()

    def stop(self):
        self.listeners = []
        self._stopListening()
    # end stop()

    def addListener(self, listener):
        self.listeners.append(listener)
    # end addListener()

    def removeListener(self, listener):
        self.listeners.remove(listener)
    # end removeListener()

    def _startListening(self):
        sysProfile = self.applicationModel.getSystemProfile()

        port = sysProfile.getProperties().getPropertyInt(u"/system-properties/singleton/port", 84113) #$NON-NLS-1$
        self.server = SimpleXMLRPCServer.SimpleXMLRPCServer( (u"localhost", port), logRequests = False ) #$NON-NLS-1$
        self.server.register_instance(ZRavenRPCServer(self))
        
        self.logger.debug(u"Singleton server created on port %d." % port) #$NON-NLS-1$

        thread = ZThread(self, u"ZSingletonService", True) #$NON-NLS-1$
        thread.start()
    # end _startListening()

    def run(self):
        try:
            self.running = True
            # FIXME (EPW) extend the xmlrpc server so that it can be gracefully shut down.
            self.server.serve_forever()
        except:
            print u'Error' #$NON-NLS-1$
        self.running = False
    # end run()

    def _stopListening(self):
        self.server.server_close()
    # end _stopListening()

    def onBlogThis(self, blogThisData):
        for listener in self.listeners:
            listener.onBlogThis(blogThisData)
    # end onBlogThis()

# end ZSingletonService
