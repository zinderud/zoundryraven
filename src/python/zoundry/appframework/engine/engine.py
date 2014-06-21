
# --------------------------------------------------------------------------------------
# This is the engine startup listener interface.  This interface must be implemented
# in order to listen to engine startup events.
# --------------------------------------------------------------------------------------
class IZEngineStartupListener:

    def engineStarting(self):
        u"This method is called when the Engine first starts." #$NON-NLS-1$
    # end engineStarting()

    # -----------------------------
    # Methods for service creation.
    # -----------------------------

    def engineCreatingServices(self, numServices):
        u"This method is called when the Engine begins creating its services." #$NON-NLS-1$
    # end engineCreatingServices()

    def engineCreatingService(self, serviceName):
        u"This method is called when the Engine is starting a specific service." #$NON-NLS-1$
    # end engineCreatingService()

    def engineServiceCreated(self, serviceName):
        u"This method is called when the Engine successfully creates a service." #$NON-NLS-1$
    # end engineServiceCreated()

    def engineServiceCreationFailed(self, serviceName, failureMessage):
        u"This method is called when the Engine fails to create a service." #$NON-NLS-1$
    # end engineServiceCreationFailed()

    def engineServicesCreated(self, numCreated, numFailed):
        u"This method is called when the Engine has finished creating its services." #$NON-NLS-1$
    # end engineServicesCreated()

    # -----------------------------
    # Methods for service startup.
    # -----------------------------

    def engineStartingServices(self, numServices):
        u"This method is called when the Engine begins starting up the services." #$NON-NLS-1$
    # end engineStartingServices()

    def engineStartingService(self, serviceName):
        u"This method is called when the Engine tries to start a specific service." #$NON-NLS-1$
    # end engineStartingService()

    def engineServiceStarted(self, serviceName):
        u"This method is called when a service is successfully started." #$NON-NLS-1$
    # end engineServiceStarted()

    def engineServiceStartFailed(self, serviceName, failureMessage):
        u"This method is called when a service fails to start." #$NON-NLS-1$
    # end engineServiceStartFailed()

    def engineServicesStarted(self, numStarted, numFailed):
        u"This method is called after the Engine has finished starting up its services." #$NON-NLS-1$
    # end engineServicesStarted()


    def engineStarted(self):
        u"This is the last method called when the engine starts up.  It is called once the Engine is running." #$NON-NLS-1$
    # end engineStarted

# end IZEngineStartupListener


# --------------------------------------------------------------------------------------
# The public Engine interface.
# --------------------------------------------------------------------------------------
class IZEngine:

    def getService(self, serviceId):
        u"Returns the service with the given id." #$NON-NLS-1$
    # end getService()

# end IZEngine
