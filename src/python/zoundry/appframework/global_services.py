
# Global references.
COMMAND_LINE_PARAM_REGISTRY = None
APPLICATION_MODEL = None


# ---------------------------------------------------------------------------------
# Getter and setter for the command line param list.  Once the main application
# calls setCommandLineParameters (happens only once), then the application's
# command line params are easily accessible via getCommandLineParameters.
# ---------------------------------------------------------------------------------
def getCommandLineParameters():
    global COMMAND_LINE_PARAM_REGISTRY
    return COMMAND_LINE_PARAM_REGISTRY
# end getCommandLineParameters()
def setCommandLineParameters(registry):
    global COMMAND_LINE_PARAM_REGISTRY
    COMMAND_LINE_PARAM_REGISTRY = registry
# end setCommandLineParameters()


# ---------------------------------------------------------------------------------
# Getter and setter for the application model.  The application model is an object
# that wraps many other objects that the application as a whole needs access to.
# This includes things like the system and user profiles, the resource registry,
# the engine, etc...  See ZApplicationModel for more details.
# ---------------------------------------------------------------------------------
def getApplicationModel():
    global APPLICATION_MODEL
    return APPLICATION_MODEL
# end getApplicationModel()
def setApplicationModel(appData):
    global APPLICATION_MODEL
    APPLICATION_MODEL = appData
# end setApplicationModel()


# ---------------------------------------------------------------------------------
# Getter for the resource registry.  The resource registry provides access to the 
# system resources such as images.
# ---------------------------------------------------------------------------------
def getResourceRegistry():
    return getApplicationModel().getResourceRegistry()
# end getResourceRegistry()


# ---------------------------------------------------------------------------------
# Getter for the logger.
# ---------------------------------------------------------------------------------
def getLoggerService():
    return getApplicationModel().getLogger()
# end getLoggerService()
