from zoundry.appframework.ui.widgets.dialogs.progress import IZRunnableProgress
from zoundry.appframework.ui.widgets.dialogs.progress import IZRunnableProgressListener
from zoundry.base.util.collections import ZListenerSet
from zoundry.blogapp.exceptions import ZBlogAppException
from zoundry.blogapp.messages import _extstr
from zoundry.base.exceptions import ZAbstractMethodCalledException
import os

# ----------------------------------------------------------------------------
# Base Runnable that is responsible for importing data from another profile such as ZBW.
# ----------------------------------------------------------------------------
class ZAbstractProfileImporter(IZRunnableProgress):

    def __init__(self, pathToSourceProfile, pathToRavenProfile, systemProfile):
        self.stopped = True
        self.pathToSourceProfile = pathToSourceProfile
        self.pathToRavenProfile = pathToRavenProfile
        self.systemProfile = systemProfile
        self.listeners = ZListenerSet()
    # end __init__()

    def addListener(self, listener):
        if not isinstance(listener, IZRunnableProgressListener):
            raise ZBlogAppException(_extstr(u"importer.IncorrectListenerType")) #$NON-NLS-1$
        self.listeners.append(listener)
    # end addListener()

    def removeListener(self, listener):
        self.listeners.remove(listener)
    # end removeListener()

    def _getRavenAccountDir(self):
        return os.path.join(self.pathToRavenProfile, u"accounts") #$NON-NLS-1$
    # end _getRavenAccountDir()

    def _notifyWorkDone(self, workunits, progressText):
        for listener in self.listeners:
            listener.onWorkDone(workunits, progressText)
    # end _notifyWorkDone

    def _notifyCancel(self):
        for listener in self.listeners:
            listener.onCancel()
    # end _notifyCancel

    def stop(self):
        self.stopped = True
    # end stop()

    def run(self):
        self.stopped = False
        if self._getWorkAmount() < 1:
            return

        for listener in self.listeners:
            listener.onStarted(self._getWorkAmount())

        # do the import
        self._runImport()

        # notify done
        for listener in self.listeners:
            listener.onComplete()
    # end run()

    def _runImport(self):
        raise ZAbstractMethodCalledException(self.__class__, u"_runImport") #$NON-NLS-1$
    # end _runImport()

    def _getWorkAmount(self):
        raise ZAbstractMethodCalledException(self.__class__, u"_getWorkAmount") #$NON-NLS-1$
    # end getWorkAmount()

# end ZAbstractProfileImporter
