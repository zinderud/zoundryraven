import sys
import threading
import traceback

# --------------------------------------------------------------------------
# This is the base exception for all Zoundry errors.  Other more specific
# exceptions should extend this one.
# --------------------------------------------------------------------------
class ZException(Exception):

    # Construct the exception with a message and an optional root cause.
    def __init__(self, message = None, rootCause = None, rootTraceback = None): #$NON-NLS-1$
        self.threadName = threading.currentThread().getName()
        self.message = message
        self.rootCause = rootCause
        self.rootStackTrace = None
        self.cachedPrintedStackTrace = None
        self.rootTraceback = rootTraceback

        if isinstance(self.rootCause, ZException):
            self.rootStackTrace = self.rootCause.getStackTrace()
            if self.message is None:
                self.message = self.rootCause.getMessage()
        elif isinstance(self.rootCause, Exception):
            self.rootStackTrace = self._createRootStackTrace()
            if self.message is None:
                self.message = unicode(self.rootCause)
            sys.exc_clear()
        if self.rootTraceback:
            (type, value, tb) = self.rootTraceback
            self.rootStackTrace = self._formatTraceBack(type, value, tb)

        # Crappy 'None" stack trace doesn't count.
        if self.rootStackTrace is not None and self.rootStackTrace.strip() == u"None: {None}": #$NON-NLS-1$
            self.rootStackTrace = None

        if self.rootStackTrace is None:
            if rootCause is not None or rootTraceback is not None:
                currentStack = self._getStackInfoAsString()
                self.rootStackTrace = u"[Cause: %s  TB: %s]\n%s" % (unicode(rootCause), unicode(rootTraceback), currentStack) #$NON-NLS-1$
    # end __init__()

    def _getStackInfoAsString(self):
        stack = traceback.extract_stack()
        stack = stack[0:len(stack)-3]
        return self._formatStack(u"", stack) #$NON-NLS-1$
    # end _getStackInfoAsString()

    def getRootException(self):
        return self.rootCause
    # end getRootException()

    def getRootStackTrace(self):
        return self.rootStackTrace
    # end getRootStackTrace()

    def getMessage(self):
        return self.message
    # end getMessage()

    def printStackTrace(self):
        print self.getStackTrace()
    # end printStackTrace()

    # Should only be called when the exception is caught.
    def getStackTrace(self):
        if self.cachedPrintedStackTrace is None:
            rval = self._getCurrentStackTrace()
            if self.rootStackTrace:
                rval = rval + u"Caused By:" + self.rootStackTrace #$NON-NLS-1$
            self.cachedPrintedStackTrace = rval + u"\nThread: [%s]" % self.threadName #$NON-NLS-1$
        return self.cachedPrintedStackTrace
    # end getStackTrace()

    def _createRootStackTrace(self):
        return self._getCurrentStackTrace()
    # end _createRootStackTrace()

    # Gets a string representing the current stack trace.
    def _getCurrentStackTrace(self):
        (type, value, tb) = sys.exc_info()
        return self._formatTraceBack(type, value, tb)
    # end _getCurrentStackTrace()

    def _formatTraceBack(self, type, value, tb):
        tbitems = traceback.extract_tb(tb)
        
        message = u"\n%s: {%s}" % (type, value) #$NON-NLS-1$
        return self._formatStack(message, tbitems)
    # end _formatTraceBack()

    def _formatStack(self, message, tbitems):
        tbitems.reverse()
        for (filename, lineno, method, code) in tbitems:
            message = message + (u"\n    at %s:%d [%s()]  ->  %s" % (filename, lineno, method, code)) #$NON-NLS-1$

        return message + u"\n" #$NON-NLS-1$
    # end _formatTraceBack()

    def __str__(self):
        return u"%s [%s]." % (self.__class__.__name__, self.message) #$NON-NLS-1$
    # end __str__()

# end ZException


# --------------------------------------------------------------------------
# This is the exception thrown when a classloader cannot find a class.
# --------------------------------------------------------------------------
class ZClassNotFoundException(ZException):

    def __init__(self, className, rootCause = None):
        ZException.__init__(self, u"Class not found: %s" % className, rootCause) #$NON-NLS-1$
    # end __init__()

# end ZClassNotFoundException


# --------------------------------------------------------------------------
# This is the exception thrown when a method is called on a class that is
# supposed to be abstract.  This would only happen due to 'bad programming'.
# --------------------------------------------------------------------------
class ZAbstractMethodCalledException(ZException):

    def __init__(self, className, methodName):
        ZException.__init__(self, u"Error: method '%s' called on abstract base class '%s'." % (methodName, className)) #$NON-NLS-1$
    # end __init__()

# end ZAbstractMethodCalledException


# --------------------------------------------------------------------------
# This is the exception thrown when an unimplemented method is called.  No
# application should be shipped with this exception being thrown (unless it
# is in an alpha or beta state).
# --------------------------------------------------------------------------
class ZNotYetImplementedException(ZException):

    def __init__(self, className, methodName):
        ZException.__init__(self, u"Error: method '%s' for class '%s' is not yet implemented." % (methodName, className)) #$NON-NLS-1$
    # end __init__()

# end ZNotYetImplementedException
