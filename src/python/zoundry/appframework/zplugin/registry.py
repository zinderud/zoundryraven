# -------------------------------------------------------------------------------------
# This is a plugin registry listener 'interface'.  This interface must be implemented
# by any class that wants to listen to the events fired when loading plugins.
# -------------------------------------------------------------------------------------
class IZPluginRegistryListener:

    # The first listener method called when loading plugins.  This is called with the
    # total number of plugin spec files that were found.  Each spec file corresponds to
    # a single plugin (spec file == zplugin.xml).
    def pluginsLoading(self, numPlugins):
        u"This event is called when the registry begins loading the plugins." #$NON-NLS-1$
    # end pluginsLoading()

    # Called when a plugin begins loading.
    def pluginLoading(self, pluginId):
        u"This event is called when the registry begins loading a specific plugin." #$NON-NLS-1$
    # end pluginLoading()

    # Called when a plugin has been successfully loaded.
    def pluginLoaded(self, pluginId):
        u"This event is called when the registry successfully loads a specific plugin." #$NON-NLS-1$
    # end pluginLoaded()

    # Called when a plugin fails to load for some reason.
    def pluginFailed(self, pluginId, failureMessage):
        u"This event is called when the registry fails to load a specific plugin." #$NON-NLS-1$
    # end pluginFailed()

    # Called at the end once all plugins have been loaded.
    #   numLoaded = total number of plugins successfully loaded
    #   numFailed = total number of plugins failed (either during load or validation)
    def pluginsLoaded(self, numLoaded, numFailed):
        u"This event is called when the registry finishes loading the plugins." #$NON-NLS-1$
    # end pluginsLoaded()

    # Called when plugin validation starts.
    def pluginsValidating(self, numPlugins):
        u"This event is called when the registry begins validating the plugins." #$NON-NLS-1$
    # end pluginsValidating()
    
    # Called when a plugin being validating.
    def pluginValidating(self, pluginId):
        u"This event is called when the registry begins validating a specific plugin." #$NON-NLS-1$
    # end pluginValidating()
    
    # Called when a plugin successfully validates.
    def pluginValidated(self, pluginId):
        u"This event is called when the registry successfully validates a plugin." #$NON-NLS-1$
    # end pluginValidate()
    
    # Called if validation of a plugin fails.
    def pluginValidationFailed(self, pluginId, failureMessage):
        u"This event is called when the registry fails to validate a specific plugin." #$NON-NLS-1$
    # end pluginValidationFailed()

    # Called at the end of the plugin validation process.
    def pluginsValidated(self, numValidPlugins, numInvalidPlugins):
        u"This event is called when the registry finishes validating the plugins." #$NON-NLS-1$
    # end pluginsValidated()

# end IZPluginRegistryListener



# -------------------------------------------------------------------------------------
# The plugin registry handles loading all of the plugins found in the system.  The
# registry gets the plugin install location from the given System Profile.  It then
# scans the plugin install location for plugins.  The plugins are loaded (taking into
# account dependencies) and organized.  The registry can then be used by other parts
# of the application.
# -------------------------------------------------------------------------------------
class IZPluginRegistry:

    def getExtensions(self, extensionPointTypeId):
        u"""getExtensions(id) -> ZExtensionPoint[]
        Gets a list of all extensions of a given type.""" #$NON-NLS-1$
    # end getExtensions()
    
    def getExtension(self, extensionPointTypeId, extensionPointId):
        u"""getExtension(id, id) -> ZExtensionPoint
        Gets a single extension by its ID and type.""" #$NON-NLS-1$
    # end getExtension()
    
    def getPlugin(self, pluginId):
        u"""getPlugin(pluginId) -> IZPlugin
        Gets a plugin by its ID.""" #$NON-NLS-1$
    # end getPlugin()

# end ZPluginRegistry

