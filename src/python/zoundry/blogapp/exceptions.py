from zoundry.appframework.exceptions import ZAppFrameworkException

# --------------------------------------------------------------------------
# This is the base exception for all errors found in the Zoundry Blog App.  
# Other more specific exceptions may extend this one.
# --------------------------------------------------------------------------
class ZBlogAppException(ZAppFrameworkException):

    # Construct the exception with a message and an optional root cause.
    def __init__(self, message, rootCause = None):
        ZAppFrameworkException.__init__(self, message, rootCause)
    # end __init__()

# end ZBlogAppException
