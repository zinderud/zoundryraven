#from threading import Thread
from zoundry.base.exceptions import ZException
from zoundry.base.messages import _extstr
from zoundry.base.util.zthread import ZThread

# ----------------------------------------------------------------------------------------
# A object to emulate the command pattern.
# ----------------------------------------------------------------------------------------
class IZCommand:

    def getName(self):
        u"""getName() -> string
        Returns command name.""" #$NON-NLS-1$
    # end getName()

    def cancel(self):
        u"""cancel() -> void
        Flag as cancelled.""" #$NON-NLS-1$
    # end cancel()

    def isCancelled(self):
        u"""isCancelled() -> bool
        Returns true if the command has been cancelled.""" #$NON-NLS-1$
    # end isCancelled()

    def doCommand(self, *args):
        u"""doCommand(tuple of args) -> void
        Subclasses should override this method to do the actual work.""" #$NON-NLS-1$
    # end doCommand()

# end IZCommand


# ----------------------------------------------------------------------------------------
# Listener on command activity
# ----------------------------------------------------------------------------------------
class IZCommandActivityListener:

    def onBeginCommand(self, command, totalWorkamount): #@UnusedVariable
        pass
    # end onBeginCommand()

    def onCommandActivity(self, command, message, workamount, logMessage): #@UnusedVariable
        pass
    # end onCommandActivity()

    def onEndCommand(self, command): #@UnusedVariable
        pass
    # end onEndCommand()

    def onLogActivity(self, command, message): #@UnusedVariable
        pass
    # end onLogActivity()

# end IZCommandActivityListener


# ----------------------------------------------------------------------------------------
# Basic (abstract)implemenation of a command
# ----------------------------------------------------------------------------------------
class ZCommandBase(IZCommand):

    def __init__(self, name = None):
        if name:
            self.name = name
        else:
            self.name = str(self.__class__.__name__)
        self.cancelled = False
        self.listeners = []

    def addListener(self, listener):
        if listener and listener not in self.listeners:
            self.listeners.append(listener)

    def _checkIfCanceled(self):
        if self.isCancelled():
            self._debug(u"Cancelled") #$NON-NLS-1$
            self._notifyEnd()            
            return True
        return False
    # end _checkIfCanceled()     

    def _notifyActivity(self, message, workamount, logMessage):
        for l in self.listeners:
            l.onCommandActivity(self, message, workamount, logMessage)

    def _logActivity(self, message):
        for l in self.listeners:
            l.onLogActivity(self, message)
    # end_logActivity()

    def _notifyBegin(self, totalWorkamount):
        for l in self.listeners:
            l.onBeginCommand(self, totalWorkamount)

    def _notifyEnd(self):
        for l in self.listeners:
            l.onEndCommand(self)

    def _setName(self, name):
        u"""_setName(string) -> void
        Sets the command name.""" #$NON-NLS-1$
        self.name = name

    def getName(self):
        u"""getName() -> string
        Returns command name.""" #$NON-NLS-1$
        return self.name

    def cancel(self):
        u"""cancel() -> void
        Flag as cancelled.""" #$NON-NLS-1$
        self.cancelled = True
        self._handleCancel()
    # end cancel()

    def _handleCancel(self):
        u"""_handleCancel() -> void
        """ #$NON-NLS-1$
        pass
    # end _handleCancel()

    def isCancelled(self):
        u"""isCancelled() -> bool
        Returns true if the command has been cancelled.
        The subclasses should poll isCancelled() to abort current work.
        """ #$NON-NLS-1$
        return self.cancelled

    def doCommand(self): #@UnusedVariable
        u"""doCommand() -> void
        Subclasses should override this method to do the actual work.
        The subclasses should also poll isCancelled() to abort current work.
        """ #$NON-NLS-1$
        pass

    def undoCommand(self): #@UnusedVariable
        u"""undoCommand() -> void
        Subclasses should override this method to UNDO the work.""" #$NON-NLS-1$
        pass

# ----------------------------------------------------------------------------------------
#
# ----------------------------------------------------------------------------------------
class ZCommandGroup(ZCommandBase):
    u"""Encapsulates a group of commands.""" #$NON-NLS-1$

    def __init__(self, command = None, name = None):
        ZCommandBase.__init__(self,name)
        self.commands = []
        self.addCommand(command)

    def addCommand(self, command):
        u"""addCommand(IZCommand) -> void
        Adds the given command to internal collection.""" #$NON-NLS-1$
        if command and command != self and command not in self.commands:
            self.commands.append(command)

    def getCommands(self):
        u"""getCommands() -> list of IZCommand objects
        Returns list of commands.""" #$NON-NLS-1$
        return self.commands

    def cancel(self):
        u"""Flags all commands in the collection as cancelled.""" #$NON-NLS-1$
        for command in self.getCommands():
            command.cancel()
        ZCommandBase.cancel(self)

    def doCommand(self):
        u"""Sequentially invokes doCommand on each of the commands in the collection.""" #$NON-NLS-1$
        for command in self.getCommands():
            if not self.isCancelled():
                try:
                    command.doCommand()
                except Exception, e:
                    self._handleException(ZException(_extstr(u"zcommand.UnexpectedErrorInDoCommand"), e)) #$NON-NLS-1$
                except:
                    self._handleException(ZException(_extstr(u"zcommand.UnexpectedErrorInDoCommand"))) #$NON-NLS-1$

    def undoCommand(self):
        u"""Sequentially (in reverse order) invokes undoCommand on each of the commands in the collection.""" #$NON-NLS-1$
        cmdList = []
        cmdList.extend( self.getCommands() )
        cmdList.reverse()
        for command in cmdList:
            try:
                command.undoCommand()
            except Exception, e:
                self._handleException(ZException(_extstr(u"zcommand.UnexpectedErrorInUnDoCommand"), e)) #$NON-NLS-1$
            except:
                self._handleException(ZException(_extstr(u"zcommand.UnexpectedErrorInUnDoCommand"))) #$NON-NLS-1$

# ----------------------------------------------------------------------------------------
#
# ----------------------------------------------------------------------------------------
class ZAsyncCommand(ZThread, IZCommand):
    u"""Command which executes the given command on a daemon thread.""" #$NON-NLS-1$

    def __init__(self, command):
        self.command = command
        self.running = False
        name = command.getName() +  u"_ZAsyncCommand" #$NON-NLS-1$
        ZThread.__init__(self, name = name, daemonic = True)
    # end __init__()

    def isRunning(self):
        u"""Returns true if the daemon thread is executing.""" #$NON-NLS-1$
        return self.running

    def getName(self):
        return self.command.getName()

    def cancel(self):
        self.command.cancel()

    def isCancelled(self):
        return self.command.isCancelled()

    def doCommand(self): #@UnusedVariable
        u"""Starts the daemon thread and sequentially invokes doCommand on each of the commands in the collection.""" #$NON-NLS-1$
        if not self.running:
            self.start()

    def undoCommand(self):
        # can run undo while thread is running?
        self.command.undoCommand()

    def _run(self):
        self.running = True
        self.command.doCommand()
        self.running = False
    # end run()

