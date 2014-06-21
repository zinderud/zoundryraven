from zoundry.base.exceptions import ZException

# --------------------------------------------------------------------------
# This is the base exception for all errors found in the Zoundry Blog App.  
# Other more specific exceptions may extend this one.
# --------------------------------------------------------------------------
class ZAppFrameworkException(ZException):

    # Construct the exception with a message and an optional root cause.
    def __init__(self, message, rootCause = None):
        ZException.__init__(self, message, rootCause)
    # end __init__()

# end ZAppFrameworkException


# --------------------------------------------------------------------------
# An exception that is thrown when the app needs to be restarted.
# --------------------------------------------------------------------------
class ZRestartApplicationException(ZAppFrameworkException):
    
    def __init__(self):
        ZAppFrameworkException.__init__(self, u"The application must be restarted.") #$NON-NLS-1$
    # end __init__()

# end ZRestartApplicationException
