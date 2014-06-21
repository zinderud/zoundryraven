from zoundry.base.net.authhandlers import ZAuthenticationManager
from StringIO import StringIO
from zoundry.appframework.constants import IZAppServiceIDs
from zoundry.appframework.engine.engine import IZEngineStartupListener
from zoundry.appframework.engine.engineimpl import ZEngine
from zoundry.appframework.ui.actions.registry import ZActionRegistry
from zoundry.appframework.zplugin.registry import IZPluginRegistryListener
from zoundry.appframework.zplugin.registryimpl import ZPluginRegistry
from zoundry.base.exceptions import ZException
from zoundry.base.util.zthread import ZThread
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.ui.regactions import registerBlogAppActions
import os

NUM_STARTUP_TASKS = 4

# -----------------------------------------------------------------------------------
# This listener interface defines callbacks that will get invoked during the startup
# of the application.
# -----------------------------------------------------------------------------------
class IRavenApplicationStartupListener:

    def rasStart(self, totalTasks):
        u"This event is called when the Raven Application starts." #$NON-NLS-1$
    # end rasStart()

    def rasTaskStart(self, taskName, totalSubTasks):
        u"This event is called when a specific task begins." #$NON-NLS-1$
    # end rasTaskStart()

    def rasSubTaskStart(self, subTaskName):
        u"This event is called when a specific subtask begins." #$NON-NLS-1$
    # end rasSubTaskStart()

    def rasSubTaskEnd(self):
        u"This event is called when a specific subtask completes." #$NON-NLS-1$
    # end rasSubTaskEnd()

    def rasTaskEnd(self):
        u"This event is called when a specific task completes." #$NON-NLS-1$
    # end rasTaskEnd()

    def rasEnd(self):
        u"This event is called when the Raven Application startup is complete." #$NON-NLS-1$
    # end rasEnd()

# end IRavenApplicationStartupListener


# -----------------------------------------------------------------------------------
# This class is responsible for creating the plugin registry and loading all of the
# plugin specs.  It also creates the application Engine and starts it.  A listener
# must be provided that implements the IRavenApplicationStartupListener interface.
# This listener will get called back at various points so that startup status can
# be displayed to the user.
#
# FIXME (EPW) should NOT open the application if plugins fail to load
# -----------------------------------------------------------------------------------
class RavenApplicationStartup(ZThread, IZPluginRegistryListener, IZEngineStartupListener):

    def __init__(self, applicationModel, listener):
        self.startupErrors = []
        self.logBuff = StringIO()

        self.applicationModel = applicationModel
        self.listener = listener
        ZThread.__init__(self, name = u"RavenApplicationStartup") #$NON-NLS-1$
    # end __init__()

    def _run(self):
        try:
            # First, load the plugins
            self.listener.rasStart(NUM_STARTUP_TASKS)
            pluginRegistry = ZPluginRegistry(self.applicationModel.getSystemProfile(), self.applicationModel.getUserProfile())
            pluginRegistry.loadPlugins(self)
            self.applicationModel.setPluginRegistry(pluginRegistry)
            self.applicationModel.setActionRegistry(ZActionRegistry())
            registerBlogAppActions(self.applicationModel.getActionRegistry())

            # Next, create and start the engine
            engine = ZEngine(self.applicationModel)
            self.applicationModel.setEngine(engine)
            engine.start(self)
            self.applicationModel.setLogger(engine.getService(IZAppServiceIDs.LOGGER_SERVICE_ID))
            # hook up logger with auth manager
            ZAuthenticationManager().setLogger( engine.getService(IZAppServiceIDs.LOGGER_SERVICE_ID)  )
        except ZException, ze:
            ze.printStackTrace()
            self.startupErrors.append(_extstr(u"startup.ErrorDuringStartupMsg") % ze.getMessage()) #$NON-NLS-1$
            self.logBuff.write(_extstr(u"startup.ErrorDuringStartupMsg") % ze.getStackTrace()) #$NON-NLS-1$
        except Exception, e:
            ze = ZException(rootCause = e)
            ze.printStackTrace()
            self.startupErrors.append(_extstr(u"startup.ErrorDuringStartupMsg") % unicode(e)) #$NON-NLS-1$
            self.logBuff.write(_extstr(u"startup.ErrorDuringStartupMsg") % ze.getStackTrace()) #$NON-NLS-1$

        self.listener.rasEnd()

        self._outputStartupLog()
        self.logBuff.close()
    # end _run()

    def hasStartupErrors(self):
        return len(self.startupErrors) > 0
    # end hasStartupErrors()

    def _outputStartupLog(self):
        logPath = self.applicationModel.getUserProfile().getLogDirectory()
        logPath = os.path.join(logPath, u"startup.log") #$NON-NLS-1$
        f = open(logPath, u"w") #$NON-NLS-1$
        f.write(self.logBuff.getvalue())
        f.close()
    # end _outputStartupLog()

    def pluginsLoading(self, numPlugins):
        self.logBuff.write(u"PLUGINS_LOADING %d\n" % numPlugins) #$NON-NLS-1$
        self.listener.rasTaskStart(_extstr(u"startup.LoadingPlugins") % numPlugins, numPlugins) #$NON-NLS-1$
    # end pluginsLoading()

    def pluginLoading(self, pluginId):
        self.logBuff.write(u"PLUGIN_LOADING %s\n" % pluginId) #$NON-NLS-1$
        self.listener.rasSubTaskStart(_extstr(u"startup.LoadingPlugin") % pluginId) #$NON-NLS-1$
    # end pluginLoading()

    def pluginLoaded(self, pluginId):
        self.logBuff.write(u"PLUGIN_LOADED %s\n" % pluginId) #$NON-NLS-1$
        self.listener.rasSubTaskEnd()
    # end pluginLoaded()

    def pluginFailed(self, pluginId, failureMessage):
        self.startupErrors.append(_extstr(u"startup.PluginFailedToLoadMsg") % (pluginId, failureMessage)) #$NON-NLS-1$
        self.logBuff.write(u"PLUGIN_FAILED %s, '%s'\n" % (pluginId, failureMessage)) #$NON-NLS-1$
        self.listener.rasSubTaskEnd()
    # end pluginFailed()

    def pluginsLoaded(self, numLoaded, numFailed):
        self.logBuff.write(u"PLUGINS_LOADED %d, %d\n" % (numLoaded, numFailed)) #$NON-NLS-1$
        self.listener.rasTaskEnd()
    # end pluginsLoaded()

    # Called when plugin validation starts.
    def pluginsValidating(self, numPlugins):
        self.logBuff.write(u"PLUGINS_VALIDATING %d\n" % numPlugins) #$NON-NLS-1$
        self.listener.rasTaskStart(_extstr(u"startup.ValidatingPlugins") % numPlugins, numPlugins) #$NON-NLS-1$
    # end pluginsValidating()

    # Called when a plugin being validating.
    def pluginValidating(self, pluginId):
        self.logBuff.write(u"PLUGIN_VALIDATING %s\n" % pluginId) #$NON-NLS-1$
        self.listener.rasSubTaskStart(_extstr(u"startup.ValidatingPlugin") % pluginId) #$NON-NLS-1$
    # end pluginValidating()

    # Called when a plugin successfully validates.
    def pluginValidated(self, pluginId):
        self.logBuff.write(u"PLUGIN_VALIDATED %s\n" % pluginId) #$NON-NLS-1$
        self.listener.rasSubTaskEnd()
    # end pluginValidate()

    # Called if validation of a plugin fails.
    def pluginValidationFailed(self, pluginId, failureMessage):
        self.startupErrors.append(_extstr(u"startup.PluginFailedToValidateMsg") % (pluginId, failureMessage)) #$NON-NLS-1$
        self.logBuff.write(u"PLUGIN_VALIDATION_FAILED %s, '%s'\n" % (pluginId, failureMessage)) #$NON-NLS-1$
        self.listener.rasSubTaskEnd()
    # end pluginValidationFailed()

    # Called at the end of the plugin validation process.
    def pluginsValidated(self, numValidPlugins, numInvalidPlugins):
        self.logBuff.write(u"PLUGINS_VALIDATED %d, %d\n" % (numValidPlugins, numInvalidPlugins)) #$NON-NLS-1$
        self.listener.rasTaskEnd()
    # end pluginsValidated()

    def engineStarting(self):
        self.logBuff.write(u"ENGINE_STARTING\n") #$NON-NLS-1$
    # end engineStarting()

    def engineCreatingServices(self, numServices):
        self.logBuff.write(u"ENGINE_CREATING_SERVICES %d\n" % (numServices)) #$NON-NLS-1$
        self.listener.rasTaskStart(_extstr(u"startup.CreatingEngineServices"), numServices) #$NON-NLS-1$
    # end engineCreatingServices()

    def engineCreatingService(self, serviceName):
        self.logBuff.write(u"ENGINE_CREATING_SERVICE %s\n" % serviceName) #$NON-NLS-1$
        self.listener.rasSubTaskStart(_extstr(u"startup.CreatingService") % serviceName) #$NON-NLS-1$
    # end engineCreatingService()

    def engineServiceCreated(self, serviceName):
        self.logBuff.write(u"ENGINE_SERVICE_CREATED %s\n" % serviceName) #$NON-NLS-1$
        self.listener.rasSubTaskEnd()
    # end engineServiceCreated()

    def engineServiceCreationFailed(self, serviceName, failureMessage):
        self.startupErrors.append(_extstr(u"startup.ServiceCreationFailedMsg") % (serviceName, failureMessage)) #$NON-NLS-1$
        self.logBuff.write(u"ENGINE_SERVICE_CREATION_FAILED %s: '%s'\n" % (serviceName, failureMessage)) #$NON-NLS-1$
        self.listener.rasSubTaskEnd()
    # end engineServiceCreationFailed()

    def engineServicesCreated(self, numCreated, numFailed):
        self.logBuff.write(u"ENGINE_SERVICES_CREATED %d, %d\n" % (numCreated, numFailed)) #$NON-NLS-1$
        self.listener.rasTaskEnd()
    # end engineServicesCreated()

    def engineStartingServices(self, numServices):
        self.logBuff.write(u"ENGINE_STARTING_SERVICES %d\n" % numServices) #$NON-NLS-1$
        self.listener.rasTaskStart(_extstr(u"startup.StartingEngineServices"), numServices) #$NON-NLS-1$
    # end engineStartingServices()

    def engineStartingService(self, serviceName):
        self.logBuff.write(u"ENGINE_STARTING_SERVICE %s\n" % serviceName) #$NON-NLS-1$
        self.listener.rasSubTaskStart(_extstr(u"startup.StartingService") % serviceName) #$NON-NLS-1$
    # end engineStartingService()

    def engineServiceStarted(self, serviceName):
        self.logBuff.write(u"ENGINE_SERVICE_STARTED %s\n" % serviceName) #$NON-NLS-1$
        self.listener.rasSubTaskEnd()
    # end engineServiceStarted()

    def engineServiceStartFailed(self, serviceName, failureMessage):
        self.startupErrors.append(_extstr(u"startup.ServiceFailedToStartMsg") % (serviceName, failureMessage)) #$NON-NLS-1$
        self.logBuff.write(u"ENGINE_SERVICE_START_FAILED %s: '%s'\n" % (serviceName, failureMessage)) #$NON-NLS-1$
        self.listener.rasSubTaskEnd()
    # end engineServiceStartFailed()

    def engineServicesStarted(self, numStarted, numFailed):
        self.logBuff.write(u"ENGINE_SEVICES_STARTED %d, %d\n" % (numStarted, numFailed)) #$NON-NLS-1$
        self.listener.rasTaskEnd()
    # end engineServicesStarted()

    def engineStarted(self):
        self.logBuff.write(u"ENGINE_STARTED\n") #$NON-NLS-1$
    # end engineStarted

# end RavenApplicationStartup

