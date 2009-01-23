from logfilters import ZLogFilterFactory
from new import instance
from string import atoi
from zoundry.base.messages import _extstr
from zoundry.base.util.classloader import ZClassLoader
from zoundry.base.util.text.textutil import getSafeString
import cgi
import codecs
import os
import socket


# ------------------------------------------------------------------------------------
# This class creates ZLogOutput objects given a log output type
# ------------------------------------------------------------------------------------
class ZLogOutputFactory:
    u"""Creates a ZLogOutput object given a type and XML 'data' node.

    This class is the factory that the Logger uses to create
    ZLogOutput objects from entries in the logger's XML configuration.
    The Logger calls createLogOutput(), passing the type and the
    XML data node and the factory returns the new ZLogOutput object.
    """ #$NON-NLS-1$

    # Constructor - make a mapping of ZLogOutput names to
    # ZLogOutput classes.
    def __init__(self):
        self.outputMap = {
            u"console" : ZLogConsoleOutput, #$NON-NLS-1$
            u"file" : ZLogFileOutput, #$NON-NLS-1$
            u"simple-tcp" : ZLogSimpleTCPOutput, #$NON-NLS-1$
            u"simple-udp" : ZLogSimpleUDPOutput, #$NON-NLS-1$
            u"custom" : ZLogCustomOutput #$NON-NLS-1$
        }
    # end __init__()

    def createLogOutput(self, type, data, outputDirectory):
        inst = instance(self.outputMap[type])
        inst.__init__(data, outputDirectory)

        return inst
    # end createLogOutput

# end ZLogOutputFactory


# ------------------------------------------------------------------------------------
# Base class for all Log Output classes.
# ------------------------------------------------------------------------------------
class ZLogOutput:

    def __init__(self, data, outputDirectory):
        self.outputDirectory = outputDirectory

        # Map the severity to an int value
        self.severityMap = {
            u"all"       : 0x0FFFFFFF, #$NON-NLS-1$
            u"none"      : 0x00000000, #$NON-NLS-1$
            u"exception" : 0x00000001, #$NON-NLS-1$
            u"error"     : 0x00000002, #$NON-NLS-1$
            u"warning"   : 0x00000004, #$NON-NLS-1$
            u"debug"     : 0x00000008 #$NON-NLS-1$
        }
        self.severity = 0
        self.format = u"log" #$NON-NLS-1$
        self.filters = []

        # Get this ZLogOutput's severity setting
        sevNodes = data.selectNodes(u'severity') #$NON-NLS-1$
        for sev in sevNodes:
            try:
                self.severity += self.severityMap[sev.getText()]
            except:
                self.severity = self.severityMap[u'all'] #$NON-NLS-1$

        # Get the ZLogOutput's format
        try:
            self.format = data.selectSingleNode(u'format').getText(u"log") #$NON-NLS-1$ #$NON-NLS-2$
        except:
            self.format = u"log" #$NON-NLS-1$

        # Now get the filter list
        factory = ZLogFilterFactory()
        filterNodes = data.selectNodes(u'filter') #$NON-NLS-1$
        for filterNode in filterNodes:
            filter = factory.createLogFilter(filterNode)
            self.filters.append(filter)
    # end __init__()

    # This method is called by the Logger class when it wants to log
    # a message.  The individual ZLogOutput instance then checks to see
    # if it SHOULD log the message before actually logging it.  Note
    # that subclasses do not override the log() method but instead
    # override the _log() method.
    def log(self, logMessage):
        if self.shouldLog(logMessage):
            fmtStr = self.formatLogMessage(logMessage)
            if fmtStr:
                self._log(fmtStr)
    # end log()
    
    # This method is called by the Logger to write  large 
    # unicode content directly to the given file.
    def clob(self, fileName, clob): #@UnusedVariable
        pass
    # end clob()

    # This method determines if this ZLogOutput object will log the
    # message.  The criteria involves the severity level of the
    # message and the filter list for the ZLogOutput object.
    def shouldLog(self, logMessage):
        # First, should we nix it based on severity?
        if (self.severityMap[logMessage.severity] & self.severity) == 0:
            return 0

        # Next, check the filter list.  If there are no filters, then
        # we let it through, otherwise it must match one of the filters
        if len(self.filters) == 0:
            return 1
        for filter in self.filters:
            if filter.filterMessage(logMessage):
                return 1

        return 0
    # end shouldLog()

    # This method formats the log message depending on this ZLogOutput's
    # format type (currently only XML or LOG).  Returns None if the
    # self.format variable is not valid
    def formatLogMessage(self, logMessage):
        if self.format == u"xml": #$NON-NLS-1$
            return u'<log-entry time="%s" thread="%s" severity="%s" source-file-name="%s" source-line-number="%d">%s</log-entry>' % (logMessage.theTime, logMessage.threadName, logMessage.severity, logMessage.fileName, logMessage.lineNumber, cgi.escape(getSafeString(logMessage.message))) #$NON-NLS-1$
        elif self.format == u"log": #$NON-NLS-1$
            return u"[%s] - [%s] - [%s] - [%s] - [%d] - [%s]" % (logMessage.theTime, logMessage.threadName, logMessage.severity, logMessage.fileName, logMessage.lineNumber, cgi.escape(logMessage.message)) #$NON-NLS-1$
        elif self.format == u"short": #$NON-NLS-1$
            return u"[%s:%d (%s)] %s" % (os.path.basename(logMessage.fileName), logMessage.lineNumber, logMessage.severity, cgi.escape(logMessage.message)) #$NON-NLS-1$
        else:
            return None
    # end formatLogMessage()

    # This method must be overridden by subclasses of ZLogOutput, since
    # it takes a formatted message string and logs it to whereever it
    # is supposed to go.
    def _log(self, message):
        u"Should be overridden by subclasses." #$NON-NLS-1$
    # end _log()

    def close(self):
        pass
    # end close()
    
    def _writeUTF8Clob(self, fileName, clob): 
        clobFile = None                
        if clob and not isinstance(clob, unicode):
            try:
                clob = clob.decode(u"utf-8") #$NON-NLS-1$
            except:
                pass
        try:
            fullPath = os.path.join(self.outputDirectory, fileName)
            clobFile = codecs.open(fullPath, u"w", u"utf-8", u"replace") #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$
            clobFile.write(clob) #$NON-NLS-1$
            clobFile.flush()            
        except:
            print u"Could not open clob file '%s', logger will not log." % unicode(fileName) #$NON-NLS-1$ #$NON-NLS-2$
        if clobFile:
            try:
                clobFile.close()
            except:
                pass
    # clob()    

#end class ZLogOutput


# ------------------------------------------------------------------------------------
# A log output implementation that writes the log messages to a file.
# ------------------------------------------------------------------------------------
class ZLogFileOutput(ZLogOutput):
    
    def __init__(self, data, outputDirectory):
        ZLogOutput.__init__(self, data, outputDirectory)
        self.filename = None

        try:
            fileLocation = data.selectSingleNode(u"file-location").getText() #$NON-NLS-1$
            self.filename = os.path.join(self.outputDirectory, fileLocation)
            self.file = open(self.filename, u"a") #$NON-NLS-1$
        except:
            print u"Could not open file '%s', logger will not log." % unicode(self.filename) #$NON-NLS-1$ #$NON-NLS-2$
            self.file = None
    # end __init__()

    def _log(self, message):
        if self.file:
            self.file.write(message.encode(u'utf8')) #$NON-NLS-1$
            self.file.write(u"\n") #$NON-NLS-1$
            self.file.flush()
    # end _log()

    def close(self):
        if self.file:
            self.file.close()
            self.file = None
    # end close()
    
    # This method is called by the Logger to write  large 
    # unicode content directly to the given file.
    def clob(self, fileName, clob): #@UnusedVariable
        self._writeUTF8Clob(fileName, clob)
    # clob()
    

# end class ZLogFileOutput

# ------------------------------------------------------------------------------------
# An implementation of a log output that prints the messages to the console.
# ------------------------------------------------------------------------------------
class ZLogConsoleOutput(ZLogOutput):
    
    def __init__(self, data, outputDirectory):
        ZLogOutput.__init__(self, data, outputDirectory)

    def _log(self, message):
        print(message.encode(u'utf8')) #$NON-NLS-1$

    def clob(self, fileName, clob): #@UnusedVariable
        if clob:
            print clob.encode(u'utf8', u'replace') #$NON-NLS-1$  #$NON-NLS-2$
    # end clob()

# end class ZLogConsoleOutput


# ------------------------------------------------------------------------------------
# An implementation of a log output that sends the messages to a TCP port.
# ------------------------------------------------------------------------------------
class ZLogSimpleTCPOutput(ZLogOutput):

    def __init__(self, data, outputDirectory):
        ZLogOutput.__init__(self, data, outputDirectory)
        self.ip = None
        self.port = 0
        self.sock = None

        try:
            self.ip = data.selectSingleNode(u'address').text(u"127.0.0.1") #$NON-NLS-1$ #$NON-NLS-2$
        except:
            self.ip = u"127.0.0.1" #$NON-NLS-1$
        try:
            self.port = atoi(data.selectSingleNode(u'port').getText(u"7707")) #$NON-NLS-1$ #$NON-NLS-2$
        except:
            self.port = 7707
    # end __init__()

    def connect(self):
        if not self.sock:
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect( (self.ip, self.port) )
            except:
                self.sock = None
        # end if
    # end connect()

    def _log(self, message):
        self.connect()
        if self.sock:
            message = message + u"\n" #$NON-NLS-1$
            message = message.encode(u'utf8') #$NON-NLS-1$
            _bytes = self.sock.send(message)
    # end _log()

    def close(self):
        if self.sock:
            self.sock.close()
            self.sock = None
    # end close()

# end ZLogSimpleTCPOutput


# ------------------------------------------------------------------------------------
# An implementation of a log output that sends the log messages to a UDP port.
# ------------------------------------------------------------------------------------
class ZLogSimpleUDPOutput(ZLogOutput):
    def __init__(self, data, outputDirectory):
        ZLogOutput.__init__(self, data, outputDirectory)
        self.ip = None
        self.port = 0
        self.sock = None

        try:
            self.ip = data.selectSingleNode(u'address').text(u"127.0.0.1") #$NON-NLS-1$ #$NON-NLS-2$
        except:
            self.ip = u"127.0.0.1" #$NON-NLS-1$
        try:
            self.port = atoi(data.selectSingleNode(u'port').getText(u"8707")) #$NON-NLS-1$ #$NON-NLS-2$
        except:
            self.port = 8707

        self.connect()
    # end __init__()

    def connect(self):
        if not self.sock:
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.sock.connect( (self.ip, self.port) )
            except:
                self.sock = None
        # end if
    # end connect()

    def _log(self, message):
        if self.sock:
            message = message + u"\n" #$NON-NLS-1$
            message = message.encode(u'utf8') #$NON-NLS-1$
            _bytes = self.sock.send(message)
    # end _log()

    def close(self):
        if self.sock:
            self.sock.close()
            self.sock = None
    # end close()

# end ZLogSimpleUDPOutput


# ------------------------------------------------------------------------------------
# Interface for custom log output classes.
# ------------------------------------------------------------------------------------
class IZCustomLogOutput:
    
    def logMessage(self, message):
        u"Called to log a message to the outoput." #$NON-NLS-1$
    # end logMessage()
    
    def close(self):
        u"Called to close the output." #$NON-NLS-1$
    # end close()

# end IZCustomLogOutput


# ------------------------------------------------------------------------------------
# A custom log output wrapper.  This will use the information found in the data element
# to instantiate a custom log output instance (a custom log output class must extend the
# IZCustomLogOutput interface above).  It will then delegate calls to _log() and call() to
# the custom log output instance.
# ------------------------------------------------------------------------------------
class ZLogCustomOutput(ZLogOutput):

    def __init__(self, data, outputDirectory):
        ZLogOutput.__init__(self, data, outputDirectory)
        className = data.selectSingleNodeText(u"class", None) #$NON-NLS-1$
        classObj = self._importClass(className)
        self.delegate = classObj()
    # end __init__()

    def _log(self, message):
        self.delegate.logMessage(message)
    # end _log()

    def close(self):
        self.delegate.close()
    # end close()

    def _importClass(self, className):
        classloader = ZClassLoader()
        classObj = classloader.loadClass(className)
        if not (issubclass(classObj, IZCustomLogOutput)):
            raise ValueError, _extstr(u"logoutput.ClassMustExtendIZCustomLogOutputError") % className #$NON-NLS-1$
        return classObj
    # end _importClass()

# end ZLogCustomOutput
