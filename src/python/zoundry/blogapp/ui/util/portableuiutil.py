from zoundry.base.util.streamutil import IZStreamWrapperListener
from zoundry.base.util.fileutil import getFileMetaData
from zoundry.appframework.constants import IZAppServiceIDs
from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.ui.widgets.dialogs.progress import ZShowProgressDialog
from zoundry.appframework.ui.widgets.dialogs.standarddialogs import ZShowPersistentYesNoMessage
from zoundry.blogapp.constants import IZBlogAppUserPrefsKeys
from zoundry.appframework.util.portableutil import ZXhtmlContentPortablePathAnalyser
from zoundry.appframework.global_services import getLoggerService
from zoundry.appframework.ui.widgets.dialogs.progress import ZAbstractRunnableProgress
from zoundry.blogapp.messages import _extstr

# ------------------------------------------------------------------------------
# Util class to copy non portable files to resource store.
# ------------------------------------------------------------------------------
def copyNonPortableFiles(parentWindow, xhtmlDocument):
    u"""Copies any non-portable resources to the profile store
    and return True.
    """ #$NON-NLS-1$
    analyser = ZXhtmlContentPortablePathAnalyser()
    xhtmlDocument.analyse(analyser)
    if analyser.hasNonPortablePaths():
        title = _extstr(u"blogeditor.CopyNonPortableFiles") #$NON-NLS-1$
        question =  _extstr(u"blogeditor.CopyNonPortableFilesDesc")                  #$NON-NLS-1$
        rval = ZShowPersistentYesNoMessage(parentWindow, question, title, IZBlogAppUserPrefsKeys.EDITOR_COPY_NONPORTABLE_FILES, canRememberNoOption = True)
        if rval:
            runnable = ZCopyNonPortableFilesRunnable( analyser.getNonPortablePathElementInfos() )
            ZShowProgressDialog(parentWindow, _extstr(u"blogeditor.CopyNonPortableFilesProgressTitle"), runnable) #$NON-NLS-1$
            return True
    return False

# end copyNonPortableFiles

# ------------------------------------------------------------------------------
# This runnable used to copy non portable files.
# ------------------------------------------------------------------------------
class ZCopyNonPortableFilesRunnable(ZAbstractRunnableProgress, IZStreamWrapperListener):

    def __init__(self, nonPortablePathElementInfos):
        self.nonPortablePathElementInfos = nonPortablePathElementInfos
        self.logger = getLoggerService()
        self.copiedContent  = {}
        self.currFileCopiedBytes = 0
        self.currFileTotalBytes = 0
        self.currProgressText = u"" #$NON-NLS-1$
        ZAbstractRunnableProgress.__init__(self)
    # end __init__()


    def _calculateWork(self):
        return len( self.nonPortablePathElementInfos )
    # end _calculateWork()

    def streamRead(self, blockSize, data): #@UnusedVariable
        # IZStreamWrapperListener callback
        s = self.currProgressText
        if self.currFileTotalBytes > 0 :
            self.currFileCopiedBytes = self.currFileCopiedBytes +  blockSize
            per = int( float(self.currFileCopiedBytes)/float(self.currFileTotalBytes) * 100.0 )
            s = u"%s (%d%%)" %(self.currProgressText, per)         #$NON-NLS-1$
        self._fireWorkDoneEvent(0, s)
    # end streamRead()

    def streamWrite(self, blockSize, data): #@UnusedVariable
        # IZStreamWrapperListener callback
        pass
    # end streamWrite()

    def _doRun(self):
        resStore = getApplicationModel().getEngine().getService(IZAppServiceIDs.RESOURCE_STORE_SERVICE_ID)
        fileNumber = 1
        totalFiles = len(self.nonPortablePathElementInfos)
        for zxhtmlPortablePathElementInfo in self.nonPortablePathElementInfos:
            if self.isCancelled():
                break
            self._copyNonPortableFile(resStore, zxhtmlPortablePathElementInfo, fileNumber, totalFiles)
            fileNumber = fileNumber + 1
    # end _doRun()

    def _copyNonPortableFile(self, resourceStore, zxhtmlPortablePathElementInfo, fileNumber, totalFiles): #@UnusedVariable
        srcPath = zxhtmlPortablePathElementInfo.getPath()
        (name, path, fsize, schemadt) = getFileMetaData( srcPath ) #@UnusedVariable
        self.currFileCopiedBytes = 0
        self.currFileTotalBytes = fsize
        progress = u"%d/%d %s" % (fileNumber, totalFiles, name) #$NON-NLS-1$
        self.currProgressText = _extstr(u"blogeditor.CopyNonPortableFilesProgressAction") % progress #$NON-NLS-1$
        self._fireWorkDoneEvent(1, self.currProgressText) #$NON-NLS-1$
        # check if already uploaded (i.e. duplicate entries e.g. second <img> pointing to same image)
        if self.copiedContent.has_key(srcPath):
            (dstPath, fsize) = self.copiedContent[srcPath]
            zxhtmlPortablePathElementInfo.setPath( dstPath )
            # call back for progress meter
            self.streamRead(fsize, None)
        else:
            try:

                self.logger.debug(u"Copying non-portable path %s " % srcPath ) #$NON-NLS-1$
                resEntry = resourceStore.addResource( srcPath, self )
                if resEntry:
                    zxhtmlPortablePathElementInfo.setPath( resEntry.getFilePath() )
                    self.copiedContent[srcPath] = (resEntry.getFilePath(), fsize)
                else:
                    self.logger.debug(u"Failed to copy non-portable path %s " % zxhtmlPortablePathElementInfo.getPath() ) #$NON-NLS-1$
            except Exception, e:
                self.logger.exception(e)
    # end _copyNonPortableFile()

    def stop(self):
        ZAbstractRunnableProgress.stop(self)
        self._fireCancelEvent()
    # end stop()