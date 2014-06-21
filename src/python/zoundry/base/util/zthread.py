from threading import Thread
from zoundry.base.exceptions import ZException
from zoundry.base.messages import _extstr


# ----------------------------------------------------------------------------------------
# An interface that must be implemented in order to be a Runnable.  The runnable interface
# is used when creating a ZThread.
# ----------------------------------------------------------------------------------------
class IZRunnable:

    def run(self):
        u"Called to execute the runnable." #$NON-NLS-1$
    # end run()

# end IZRunnable


# ----------------------------------------------------------------------------------------
# A Zoundry Thread.  The ZThread class is designed to emulate the Java Thread class.  The
# constructor can either take a IZRunnable or None.  If a runnable is supplied, it is used
# for the execution context, otherwise the thread calls its own run method.
# ----------------------------------------------------------------------------------------
class ZThread(Thread):

    def __init__(self, runnable = None, name = None, daemonic = False):
        self.done = False
        self.runnable = None

        if runnable and isinstance(runnable, IZRunnable):
            self.runnable = runnable
        if not name:
            name = u"ZThread" #$NON-NLS-1$
        Thread.__init__(self, None, None, name)
        self.setDaemon(daemonic)
    # end __init__()

    def run(self):
        self.done = False
        try:
            if self.runnable:
                self.runnable.run()
            else:
                self._run()
        except Exception, e:
            self._handleException(ZException(_extstr(u"zthread.UnexpectedErrorInThread"), e)) #$NON-NLS-1$
        except:
            self._handleException(ZException(_extstr(u"zthread.UnexpectedErrorInThread"))) #$NON-NLS-1$
        self.done = True
    # end run()

    def _handleException(self, zexception): #@UnusedVariable
        zexception.printStackTrace()
    # end _handleException()

    def _run(self):
        pass
    # end _run()

    def isDone(self):
        return self.done
    # end isDone()

# end ZThread
