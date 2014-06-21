from zoundry.appframework.global_services import getLoggerService
from zoundry.appframework.constants import IZAppExtensionPoints
from zoundry.appframework.engine.engine import IZEngine
from zoundry.appframework.engine.engine import IZEngineStartupListener
from zoundry.appframework.engine.exceptions import ZEngineException
from zoundry.appframework.engine.service import IZService
from zoundry.appframework.exceptions import ZAppFrameworkException
from zoundry.appframework.messages import _extstr
from zoundry.base.exceptions import ZException


# --------------------------------------------------------------------------------------
# A null engine startup listener - this listener can be used if the caller doesn't care
# about the events.
# --------------------------------------------------------------------------------------
class ZNullEngineStartupListener(IZEngineStartupListener):
    u"A null engine startup listener." #$NON-NLS-1$
# end ZNullEngineStartupListener

_NULL_STARTUP_LISTENER = ZNullEngineStartupListener()

# --------------------------------------------------------------------------------------
# The Raven Application's backend 'Engine'.  This class is essentially a set of services
# that are made available to the application.  The Engine controls the life cycle of
# these services (create, start, stop, destroy).
#
# FIXME (EPW) Need to sort the list of services for proper lifecycle (also, iterate backwards when stopping the services)
# --------------------------------------------------------------------------------------
class ZEngine(IZEngine):

    def __init__(self, applicationModel):
        self.applicationModel = applicationModel
        self.services = {}
    # end __init__()

    def start(self, listener = _NULL_STARTUP_LISTENER):
        listener.engineStarting()

        # Get the list of service extension points.
        extensionPoints = self._getServiceExtensionPoints()
        listener.engineCreatingServices(len(extensionPoints))

        # Create all of the IZService objects.
        createdServices = []
        numFailed = 0
        for extensionPoint in extensionPoints:
            extPointId = extensionPoint.getId()
            try:
                theClass = extensionPoint.loadClass()
                if not issubclass(theClass, IZService):
                    raise ZEngineException(_extstr(u"engine.ErrorCreatingService") % extensionPoint.getClass()) #$NON-NLS-1$
                theService = theClass()
                if not isinstance(theService, IZService):
                    raise ZEngineException(_extstr(u"engine.ErrorCreatingService") % extensionPoint.getClass()) #$NON-NLS-1$
                listener.engineServiceCreated(extPointId)
                createdServices.append( (extPointId, theService) )
            except ZException, ze:
                listener.engineServiceCreationFailed(extPointId, ze.getStackTrace())
                numFailed += 1
            except Exception, e:
                listener.engineServiceCreationFailed(extPointId, ZException(rootCause = e).getStackTrace())
                numFailed += 1

        listener.engineServicesCreated(len(createdServices), numFailed)

        # Start all of the services.
        listener.engineStartingServices(len(createdServices))
        startedServices = []
        numFailed = 0
        self.services = {}
        for (key, service) in createdServices:
            listener.engineStartingService(key)
            try:
                service.start(self.applicationModel)
                listener.engineServiceStarted(key)
                startedServices.append( (key, service) )
                self.services[key] = service
            except ZException, ze:
                listener.engineServiceStartFailed(key, ze.getStackTrace())
                numFailed += 1
            except Exception, e:
                listener.engineServiceStartFailed(key, ZException(rootCause = e).getStackTrace())
                numFailed += 1
        listener.engineServicesStarted(len(startedServices), numFailed)

        listener.engineStarted()
    # end start()

    def stop(self):
        for key in self.services:
            service = self.services[key]
            try:
                service.stop()
            except Exception, e:
                getLoggerService().exception(e)
    # end stop()

    def getService(self, serviceId):
        if self.services.has_key(serviceId):
            return self.services[serviceId]
        else:
            raise ZAppFrameworkException(_extstr(u"engine.NoServiceFoundError") % serviceId) #$NON-NLS-1$
    # end getService()

    def _getServiceExtensionPoints(self):
        return self.applicationModel.getPluginRegistry().getExtensions(IZAppExtensionPoints.ZEP_ZOUNDRY_SERVICE)
    # end _getServiceExtensionPoints()

# end ZEngine
