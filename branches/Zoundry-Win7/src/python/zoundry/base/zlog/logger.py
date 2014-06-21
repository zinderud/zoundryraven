from Queue import Queue
from threading import Thread
from threading import currentThread
from time import asctime
from time import localtime
from time import time
from zoundry.base.messages import _extstr
from zoundry.base.zdom.dom import ZDom
from zoundry.base.zlog.logoutput import ZLogOutputFactory

# FIXME rename zlog package to log


CONSOLE_LOGGER_TEMPLATE = u"""
    <output>
      <name>Console</name>
      <type>console</type>
      <init>
        <severity>all</severity>
        <format>log</format>
      </init>
    </output>
""" #$NON-NLS-1$

ECLIPSE_PLUGIN_LOGGER_TEMPLATE = u"""
    <output>
      <name>Eclipse Console</name>
      <type>simple-udp</type>
      <init>
        <address>127.0.0.1</address>
        <port>8707</port>
        <severity>all</severity>
        <format>xml</format>
      </init>
    </output>
""" #$NON-NLS-1$

MASTER_DEBUG_FILE_LOGGER_TEMPLATE = u"""
    <output>
        <name>Master Debug Log File</name>
        <type>file</type>
        <init>
            <severity>all</severity>
            <format>xml</format>
            <file-location>zoundry-debug-log.xml</file-location>
        </init>
    </output>
""" #$NON-NLS-1$

CONSOLE_LOGGER_TEMPLATE = u"""
    <output>
        <name>Console Logger</name>
        <type>console</type>
        <init>
            <severity>all</severity>
            <format>short</format>
        </init>
    </output>
""" #$NON-NLS-1$


# ------------------------------------------------------------------------------------
# A structure that holds all of the information for a single log message.
# ------------------------------------------------------------------------------------
class ZLogMessage:
    u"""Encapsulates a single message that was sent to the Logger.""" #$NON-NLS-1$
    def __init__(self):
        self.isClob = False
        self.clob = None
        self.theTime = asctime(localtime(time()))
    # end __init__()

    def setMessage(self, threadName, fileName, lineNumber, code, message, severity):
        self.threadName = threadName
        self.fileName = fileName
        self.lineNumber = lineNumber
        self.code = code
        self.message = message
        self.severity = severity
    # end setMessage()
    
    def setClob(self, fileName, clob):
        self.isClob = True
        self.clob = clob
        self.clobFileName = fileName
# end ZLogMessage


# ------------------------------------------------------------------------------------
# The logger impl itself.  This class uses the filters and log outputs to actual do
# the business of logging.  Don't worry, it is Spotted Owl-safe.
# ------------------------------------------------------------------------------------
class ZLogger(Thread):

    # Now come the instance variables and methods
    def __init__(self, configNode, masterDebug = False, eclipseDebug = False, consoleDebug = False, outputDirectory = u""): #$NON-NLS-1$
        Thread.__init__(self, None, None, u"LoggerThread") #$NON-NLS-1$

        self.outputDirectory = outputDirectory
        self.done = False
        self.running = False

        # Create the message queue
        self.queue = Queue(0)
        self.outputMap = {}

        # Configure all of the logger outputs (places where we
        # will be logging to).
        if configNode:
            nodes = configNode.selectNodes(u'outputs/output') #$NON-NLS-1$
            for output in nodes:
                self._addLogOutput(output)

        self.enableEclipsePluginLoggerOutput(eclipseDebug)
        self.enableMasterDebugLoggerOutput(masterDebug)
        self.enableConsoleDebugLoggerOutput(consoleDebug)
    # end __init__()

    def _addLogOutput(self, outputNode):
        factory = ZLogOutputFactory()

        # Get the output name (required)
        outputName = outputNode.selectSingleNode(u'name').getText() #$NON-NLS-1$
        # Get the output type (required)
        outputType = outputNode.selectSingleNode(u"type").getText() #$NON-NLS-1$
        # Grab the <init> subtree to pass it to the LogOutput's constructor
        initNode = outputNode.selectSingleNode(u'init') #$NON-NLS-1$

        # Now use the factory to create the LogOutput object and place
        # it in the dictionary/map
        self.outputMap[outputName] = factory.createLogOutput(outputType, initNode, self.outputDirectory)
    # end _addLogOutput()

    def enableEclipsePluginLoggerOutput(self, bEnable):
        exists = self.outputMap.has_key(u"Eclipse Console") #$NON-NLS-1$
        if not exists and bEnable:
            dom = ZDom()
            dom.loadXML(ECLIPSE_PLUGIN_LOGGER_TEMPLATE)
            self._addLogOutput(dom.documentElement)
        elif exists and not bEnable:
            output = self.outputMap.pop(u"Eclipse Console") #$NON-NLS-1$
            if output:
                output.close()
    # end enableEclipsePluginLoggerOutput()

    def enableMasterDebugLoggerOutput(self, bEnable):
        exists = self.outputMap.has_key(u"Master Debug Log File") #$NON-NLS-1$
        if not exists and bEnable:
            dom = ZDom()
            dom.loadXML(MASTER_DEBUG_FILE_LOGGER_TEMPLATE)
            self._addLogOutput(dom.documentElement)
        elif exists and not bEnable:
            output = self.outputMap.pop(u"Master Debug Log File") #$NON-NLS-1$
            if output:
                output.close()
    # end enableMasterDebugLoggerOutput()

    def enableConsoleDebugLoggerOutput(self, bEnable):
        exists = self.outputMap.has_key(u"Console Logger") #$NON-NLS-1$
        if not exists and bEnable:
            dom = ZDom()
            dom.loadXML(CONSOLE_LOGGER_TEMPLATE)
            self._addLogOutput(dom.documentElement)
        elif exists and not bEnable:
            output = self.outputMap.pop(u"Console Logger") #$NON-NLS-1$
            if output:
                output.close()
    # end enableConsoleDebugLoggerOutput()

    def run(self):
        self.running = True
        self.done = False
        while not self.done:
            # This will blog until there is a message waiting (enqueued)
            logMessage = self.queue.get()
            if logMessage.isClob and logMessage.clobFileName:
                for (_outputName, logOutput) in self.outputMap.items():
                    logOutput.clob(logMessage.clobFileName, logMessage.clob)            
            else:
                for (_outputName, logOutput) in self.outputMap.items():
                    logOutput.log(logMessage)
        # end while

        for output in self.outputMap.values():
            output.close()

        self.running = False
    # end run()

    def shutdown(self):
        self.done = True
        self.debug(u"", -1, None, _extstr(u"logger.ShuttingDownLogger")) #$NON-NLS-1$ #$NON-NLS-2$
        while self.running:
            pass
    # end shutdown()

    # The meat and potatoes of _Logger is the log() method.  Most of the
    # actual grit is implemented in the LogOutput class.  This method
    # simply iterates through all of the LogOutput instances and calls
    # log() on each.
    def log(self, fileName, lineNumber, code, message, severity):
        threadName = currentThread().getName()
        logMessage = ZLogMessage()
        logMessage.setMessage(threadName, fileName, lineNumber, code, message, severity)
        self.queue.put(logMessage)
    # end log()

    # This method must be closed by the application before the application
    # exits.  It closes each of its LogOutput objects (necessary for
    # the LogFileOutput class).
    def _close(self):
        for (_outputName, logOutput) in self.outputMap.items():
            logOutput.close()
    # end close()

    # Note: the exception param should be an instance of ZException
    def exception(self, fileName, lineNumber, code, zexception):
        self.log(fileName, lineNumber, code, zexception.getStackTrace(), u"exception") #$NON-NLS-1$
    # end exception()

    def error(self, fileName, lineNumber, code, errorMessage):
        self.log(fileName, lineNumber, code, errorMessage, u"error") #$NON-NLS-1$
    # end error()

    def warning(self, fileName, lineNumber, code, warningMessage):
        self.log(fileName, lineNumber, code, warningMessage, u"warning") #$NON-NLS-1$
    # end warning()

    def debug(self, fileName, lineNumber, code, debugMessage):
        self.log(fileName, lineNumber, code, debugMessage, u"debug") #$NON-NLS-1$
    # end debug()
    
    def logClob(self, filename, clob):
        logMessage = ZLogMessage()
        logMessage.setClob(filename, clob)
        self.queue.put(logMessage)
    # end logClob()

# end ZLogger
