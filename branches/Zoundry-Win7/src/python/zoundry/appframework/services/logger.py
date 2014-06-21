from zoundry.appframework.engine.service import IZService
from zoundry.appframework.util.osutilfactory import getOSUtil
from zoundry.base.exceptions import ZException
from zoundry.base.zdom.dom import ZDom
from zoundry.base.zlog.logger import ZLogger
import traceback

DEFAULT_LOG_XML = u"""
  <log-config>
    <outputs>
      <output>
        <name>Error Log File</name>
        <type>file</type>
        <init>
          <severity>exception</severity>
          <severity>error</severity>
          <severity>warning</severity>
          <format>xml</format>
          <file-location>raven-errors.xml</file-location>
        </init>
      </output>
    </outputs>
  </log-config>
""" #$NON-NLS-1$

# ------------------------------------------------------------------------------
# This defines the methods found on the Zoundry Logger Service.
# ------------------------------------------------------------------------------
class IZLoggerService:

    def isDebugLoggingEnabled(self):
        u"Returns True if debug logging is enabled." #$NON-NLS-1$
    # end isDebugLoggingEnabled()

    def enableDebugLogging(self):
        u"Enables debug logging (to file)." #$NON-NLS-1$
    # end enableDebugLogging()
    
    def disableDebugLogging(self):
        u"Disables debug logging (to file)." #$NON-NLS-1$
    # end disableDebugLoggin()

    def debug(self, message):
        u"Logs a debug message to the log." #$NON-NLS-1$
    # end debug()

    def warning(self, message):
        u"Logs a warning to the log." #$NON-NLS-1$
    # end warning()

    def error(self, message):
        u"Logs an error to the log." #$NON-NLS-1$
    # end error()

    def exception(self, exception):
        u"""Logs an exception to the log.""" #$NON-NLS-1$
    # end exception()

    def logClob(self, filename, clob):
        u"""Writes the text/character content to the given filename.""" #$NON-NLS-1$
    # end logClob()

# end IZLoggerService


# ------------------------------------------------------------------------------
# This is an implementation of the Zoundry Logger Service.
# ------------------------------------------------------------------------------
class ZLoggerService(IZService, IZLoggerService):

    def __init__(self):
        pass
    # end __init__()

    def _loadDefaultLoggerNode(self):
        dom = ZDom()
        dom.loadXML(DEFAULT_LOG_XML)
        return dom.selectSingleNode(u"/") #$NON-NLS-1$
    # end _loadDefaultLoggerNode()

    def start(self, applicationModel): #@UnusedVariable
        self.userProfile = applicationModel.getUserProfile()
        userProps = self.userProfile.getProperties()

        loggerConfigNode = userProps.getPropertyNode(u"/user-properties/logger") #$NON-NLS-1$
        if not loggerConfigNode:
            loggerConfigNode = self._loadDefaultLoggerNode()
        isInstalled = getOSUtil().isInstalledAsExe()
        isMaster = userProps.getPropertyBool(u"/user-properties/logger/master", False) #$NON-NLS-1$
        isEclipse = userProps.getPropertyBool(u"/user-properties/logger/eclipse", not isInstalled) #$NON-NLS-1$
        isConsole = userProps.getPropertyBool(u"/user-properties/logger/console", False) #$NON-NLS-1$

        self.logger = ZLogger(loggerConfigNode, isMaster, isEclipse, isConsole, self.userProfile.getLogDirectory())
        self.logger.start()
    # end start()

    def stop(self):
        self.logger.shutdown()
    # end stop()

    def isDebugLoggingEnabled(self):
        userProps = self.userProfile.getProperties()
        return userProps.getPropertyBool(u"/user-properties/logger/master", False) #$NON-NLS-1$
    # end isDebugLoggingEnabled()

    def enableDebugLogging(self):
        userProps = self.userProfile.getProperties()
        userProps.setProperty(u"/user-properties/logger/master", u"true") #$NON-NLS-1$ #$NON-NLS-2$
        self.logger.enableMasterDebugLoggerOutput(True)
    # end enableDebugLogging()

    def disableDebugLogging(self):
        userProps = self.userProfile.getProperties()
        userProps.setProperty(u"/user-properties/logger/master", u"false") #$NON-NLS-1$ #$NON-NLS-2$
        self.logger.enableMasterDebugLoggerOutput(True)
    # end disableDebugLoggin()

    def debug(self, message):
        (fileName, lineNumber, code) = self._getStackInfo()
        self.logger.debug(fileName, lineNumber, code, message)
    # end debug()

    def warning(self, message):
        (fileName, lineNumber, code) = self._getStackInfo()
        self.logger.warning(fileName, lineNumber, code, message)
    # end warning()

    def error(self, message):
        (fileName, lineNumber, code) = self._getStackInfo()
        self.logger.error(fileName, lineNumber, code, message)
    # end error()

    def exception(self, exception):
        (fileName, lineNumber, code) = self._getStackInfo()
        if not isinstance(exception, ZException):
            exception = ZException(rootCause = exception)
        self.logger.exception(fileName, lineNumber, code, exception)
    # end exception()
    
    def logClob(self, filename, clob):
        self.logger.logClob(filename, clob)
    

    def _getStackInfo(self):
        stack = traceback.extract_stack()
        (fileName, lineNumber, _dummy, code) = stack[len(stack) - 3]
        return (fileName, lineNumber, code)
    # end _getStackInfo()


# end ZLoggerService
