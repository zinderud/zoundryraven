from zoundry.base.exceptions import ZAbstractMethodCalledException
from zoundry.appframework.models.appmodel import IZApplicationModel
from zoundry.appframework.services.logger import IZLoggerService

# -----------------------------------------------------------------------------------
# This class is a wrapper around various objects, including the system profile, user
# profile, plugin registry, engine, etc.  It also provides access to application
# resources such as images.
# -----------------------------------------------------------------------------------
class ZApplicationModel(IZApplicationModel):

    def __init__(self):
        self.systemProfile = None
        self.resourceRegistry = None
        self.actionRegistry = None
        self.logger = None
        self.userProfile = None
        self.pluginRegistry = None
        self.engine = None
        self.logger = None
        self.topWindow = None
    # end __init__()

    def getVersion(self):
        raise ZAbstractMethodCalledException(self.__class__, u"getVersion") #$NON-NLS-1$
    # end getVersion()

    def getSystemProfile(self):
        return self.systemProfile
    # end getSystemProfile()

    def setSystemProfile(self, systemProfile):
        self.systemProfile = systemProfile
    # end getSystemProfile()

    def getResourceRegistry(self):
        return self.resourceRegistry
    # end getResourceRegistry()

    def setResourceRegistry(self, resourceRegistry):
        self.resourceRegistry = resourceRegistry
    # end setResourceRegistry()

    def getLogger(self):
        if self.logger is None:
            return IZLoggerService()
        else:
            return self.logger
    # end getLogger()

    def setLogger(self, logger):
        self.logger = logger
    # end setLogger()

    def getUserProfile(self):
        return self.userProfile
    # end getUserProfile()

    def setUserProfile(self, userProfile):
        self.userProfile = userProfile
    # end getUserProfile()

    def getPluginRegistry(self):
        return self.pluginRegistry
    # end getPluginRegistry()

    def setPluginRegistry(self, pluginRegistry):
        self.pluginRegistry = pluginRegistry
    # end setPluginRegistry()

    def getActionRegistry(self):
        return self.actionRegistry
    # end getActionRegistry()

    def setActionRegistry(self, actionRegistry):
        self.actionRegistry = actionRegistry
    # end setActionRegistry()

    def getEngine(self):
        return self.engine
    # end getEngine()

    def setEngine(self, engine):
        self.engine = engine
    # end setEngine()

    def getService(self, serviceId):
        return self.getEngine().getService(serviceId)
    # end getService()

    def getPlugin(self, pluginId):
        return self.getPluginRegistry().getPlugin(pluginId)
    # end getPlugin()

    def getTopWindow(self):
        return self.topWindow
    # end getTopWindow()

    def setTopWindow(self, window):
        self.topWindow = window
    # end setTopWindow()

# end ZApplicationModel
