#
# This module contains classes that will represent the Application Model.  The Application
# Model is a global model that will contain the data that is of interest to the application
# as a whole.  The application model will likely be extended by any specific application
# instance (such as the blog writer).
#


# -----------------------------------------------------------------------------------
# The application model interface.
# -----------------------------------------------------------------------------------
class IZApplicationModel:

    def getVersion(self):
        u"Gets the application version." #$NON-NLS-1$
    # end getVersion()

    def getSystemProfile(self):
        u"Gets the system profile." #$NON-NLS-1$
    # end getSystemProfile()

    def getResourceRegistry(self):
        u"Gets the resource registry." #$NON-NLS-1$
    # end getResourceRegistry()

    def getLogger(self):
        u"Gets the IZLoggerService instance." #$NON-NLS-1$
    # end getLogger()

    def getUserProfile(self):
        u"Gets the current user profile." #$NON-NLS-1$
    # end getUserProfile()

    def getPluginRegistry(self):
        u"Gets the plugin registry." #$NON-NLS-1$
    # end getPluginRegistry()

    def getActionRegistry(self):
        u"Gets the action registry." #$NON-NLS-1$
    # end getActionRegistry()

    def getEngine(self):
        u"Gets the engine." #$NON-NLS-1$
    # end getEngine()

    def getService(self, serviceId):
        u"Returns the service with the given service ID." #$NON-NLS-1$
    # end getService()

    def getPlugin(self, pluginId):
        u"Returns the plugin with the given ID." #$NON-NLS-1$
    # end getPlugin()

    def getTopWindow(self):
        u"Returns the top wx window for the application." #$NON-NLS-1$
    # end getTopWindow()

# end IZApplicationModel
