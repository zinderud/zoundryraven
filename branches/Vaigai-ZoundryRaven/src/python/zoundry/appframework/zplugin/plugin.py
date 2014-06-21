
# -----------------------------------------------------------------------------------
# The public plugin interface.  This interface will have various things on it that
# a plugin developer might need, such as the ability to get resources, get strings
# from the plugin's bundle, etc.
# -----------------------------------------------------------------------------------
class IZPlugin:

    def getPluginDirectory(self):
        u"Returns the plugin's installation directory." #$NON-NLS-1$
        return self.pluginDirectory
    # end getPluginDirectory()

    def getId(self):
        u"Returns the plugin id." #$NON-NLS-1$
    # end getId()

    def getName(self):
        u"Returns the plugin name." #$NON-NLS-1$
    # end getName()

    # Returns a ZVersion object representing the version of this plugin.
    def getVersion(self):
        u"Returns the plugin version." #$NON-NLS-1$
    # end getVersion()

    def getString(self, key):
        u"Gets a string from the plugin's string bundle." #$NON-NLS-1$
    # end getString()

    def getResourceRegistry(self):
        u"Returns the plugin's resource registry (provides access to plugin resources)." #$NON-NLS-1$
    # end getResourceRegistry()
    
    def getClassloader(self):
        u"Returns a ZClassloader used to load classes for this plugin." #$NON-NLS-1$
    # end getClassloader()

# end IZPlugin
