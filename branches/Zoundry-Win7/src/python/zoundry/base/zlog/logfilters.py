from new import instance
import re

# ------------------------------------------------------------------------------------
# The log filter factory - creates a log filter given a filter node from the config
# file/xml.
# ------------------------------------------------------------------------------------
class ZLogFilterFactory:
    u"""A factory that creates Log Filter objects (given a type).

    The ZLogFilterFactory's createLogFilter() method is called each time
    a ZLogFilter object needs to be created.  It takes a <filter> XML
    node and returns a ZLogFilter object of the appropriate type.
    """ #$NON-NLS-1$
    def __init__(self):
        self.filterMap = {
            u"simple" : ZSimpleLogFilter, #$NON-NLS-1$
            u"regexp" : ZRegexpLogFilter #$NON-NLS-1$
        }
    # end __init__()

    def createLogFilter(self, filterNode):
        type = filterNode.getAttribute(u"type") #$NON-NLS-1$
        on = filterNode.getAttribute(u"on") #$NON-NLS-1$
        pattern = filterNode.getText()

        inst = instance(self.filterMap[type])
        inst.__init__(on, pattern)

        return inst
    # end createLogFilter()

# end ZLogFilterFactory


# ------------------------------------------------------------------------------------
# The base class for all ZLogFilters.
# ------------------------------------------------------------------------------------
class ZLogFilter:
    u"""The base class for all ZLogFilter objects.

    The ZLogFilter class is a base class that simply defines the interface
    for all subclasses.
    """ #$NON-NLS-1$
    def __init__(self, on, pattern):
        self.on = on
        self.pattern = pattern
    # end __init__()

    def filterMessage(self, logMessage):
        u"Subclasses must implement this." #$NON-NLS-1$
    # end filterMessage()

# end ZLogFilter


# ------------------------------------------------------------------------------------
# A simple log filter that uses string.find() to do its filtering.
# ------------------------------------------------------------------------------------
class ZSimpleLogFilter(ZLogFilter):
    u"""Implements a ZLogFilter that uses the string.find() method.

    This class extends the ZLogFilter class.  It implements a simple filter
    which uses the string module's find() method to determine if a log
    message matches the filter's criteria.
    """ #$NON-NLS-1$
    def __init__(self, on, pattern):
        ZLogFilter.__init__(self, on, pattern)
    # end __init__()

    def filterMessage(self, logMessage):
        if self.on == u"package": #$NON-NLS-1$
            if logMessage.packageName.find(self.pattern) >= 0:
                return 1
        elif self.on == u"class": #$NON-NLS-1$
            if logMessage.className.find(self.pattern) >= 0:
                return 1
        elif self.on == u"message": #$NON-NLS-1$
            if logMessage.message.find(self.pattern) >= 0:
                return 1
        elif self.on == u"thread": #$NON-NLS-1$
            if logMessage.threadName.find(self.pattern) >= 0:
                return 1
        else:
            pass
        return 0
    # end filterMessage()

# end ZSimpleLogFilter


# ------------------------------------------------------------------------------------
# A log filter that uses regular expressions to filter the messages.
# ------------------------------------------------------------------------------------
class ZRegexpLogFilter(ZLogFilter):
    def __init__(self, on, pattern):
        ZLogFilter.__init__(self, on, pattern)

        self.regexpPattern = re.compile(self.pattern)
    # end __init__()

    def filterMessage(self, logMessage):
        match = None
        if self.on == u"package": #$NON-NLS-1$
            match = self.regexpPattern.search(logMessage.packageName)
        elif self.on == u"class": #$NON-NLS-1$
            match = self.regexpPattern.search(logMessage.className)
        elif self.on == u"message": #$NON-NLS-1$
            match = self.regexpPattern.search(logMessage.message)
        elif self.on == u"threadName": #$NON-NLS-1$
            match = self.regexpPattern.search(logMessage.threadName)
        else:
            pass
        return match != None
    # end filterMessage()

# end ZRegexpLogFilter
