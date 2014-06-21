from zoundry.appframework.exceptions import ZAppFrameworkException

# ------------------------------------------------------------------------
# This is the base exception for all errors that may occur in the
# Application Engine.  Other more specific exceptions may extend this
# one.
# ------------------------------------------------------------------------
class ZEngineException(ZAppFrameworkException):

    # Construct the exception with a message and an optional root cause.
    def __init__(self, message, rootCause = None):
        ZAppFrameworkException.__init__(self, message, rootCause)
    # end __init__()

# end ZEngineException
