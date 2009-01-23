from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.services.ztest.ztestimpl import ZTest
from zoundry.appframework.services.ztest.ztestimpl import ZTestStep
from zoundry.base.exceptions import ZException
from zoundry.base.net.http import ZHttpBinaryFileDownload
from zoundry.blogapp.messages import _extstr
import os
import time


# ------------------------------------------------------------------------------------------
# Implements step #1 in the testing of a media storage:  uploading a test file to the store.
# ------------------------------------------------------------------------------------------
class ZUploadFileTestStep(ZTestStep):

    def __init__(self):
        ZTestStep.__init__(self, _extstr(u"mediastorageztest.UploadTestFile")) #$NON-NLS-1$
    # end __init__()

    def execute(self, mediaStore, session):
        testImageName = u"z_raven_test_image.png" #$NON-NLS-1$
        testImagePath = getApplicationModel().getResourceRegistry().getImagePath(u"images/common/ztest/%s" % testImageName) #$NON-NLS-1$
        rval = None

        try:
            rval = mediaStore.upload(testImagePath, bypassRegistry = True)
        except Exception, e:
            raise ZException(_extstr(u"mediastorageztest.FailedToUploadTestFileError") % mediaStore.getName(), e) #$NON-NLS-1$

        if not rval:
            raise ZException(_extstr(u"mediastorageztest.NoURLFromUploadError") % mediaStore.getName()) #$NON-NLS-1$
        else:
            session[u"upload.url"] = rval.getUrl() #$NON-NLS-1$
            session[u"upload.name"] = testImageName #$NON-NLS-1$
            session[u"upload.path"] = testImagePath #$NON-NLS-1$
    # end execute()

# end ZUploadFileTestStep


# ------------------------------------------------------------------------------------------
# Implements step #2 in the testing of a media storage:  verify file upload by downloading
# from the URL.
# ------------------------------------------------------------------------------------------
class ZVerifyURLTestStep(ZTestStep):

    def __init__(self):
        ZTestStep.__init__(self, _extstr(u"mediastorageztest.VerifyTestFileURL")) #$NON-NLS-1$
    # end __init__()

    def execute(self, mediaStore, session): #@UnusedVariable
        url = session[u"upload.url"] #$NON-NLS-1$
        if url.startswith(u"http"): #$NON-NLS-1$
            self._verifyHttpURL(url)
        else: # assume file path
            if not os.path.isfile(url):
                raise ZException(_extstr(u"mediastorageztest.FailedToVerifyURLError") % url) #$NON-NLS-1$
    # end execute()

    def _verifyHttpURL(self, url):
        tempFilePath = os.path.join(getApplicationModel().getUserProfile().getTempDirectory(), u"tmp_url_mstore_ztest.bin") #$NON-NLS-1$
        downloader = ZHttpBinaryFileDownload(url, tempFilePath)
        try:
            if not downloader.send():
                raise ZException(_extstr(u"mediastorageztest.FileNotFoundError") % url) #$NON-NLS-1$
            ct = downloader.getContentType()
            if not (ct == u"image/png"): #$NON-NLS-1$
                raise ZException(_extstr(u"mediastorageztest.IncorrectContentTypeError") % (ct, url)) #$NON-NLS-1$
            numBytes = downloader.getResponse()
            if numBytes != 222: # Note: the test file is 222 bytes in size
                raise ZException(_extstr(u"mediastorageztest.TestFileWrongSizeError")) #$NON-NLS-1$
        finally:
            if os.path.isfile(tempFilePath):
                os.remove(tempFilePath)
    # end _verifyHttpURL()

# end ZVerifyURLTestStep


# ------------------------------------------------------------------------------------------
# Implements step #3 in the testing of a media storage:  verify file upload by getting a list
# of files from the store itself.
# ------------------------------------------------------------------------------------------
class ZVerifyFileListTestStep(ZTestStep):

    def __init__(self):
        ZTestStep.__init__(self, _extstr(u"mediastorageztest.VerifyTestFileList")) #$NON-NLS-1$
    # end __init__()

    def execute(self, mediaStore, session):
        testFileName = session[u"upload.name"] #$NON-NLS-1$
        
        if not testFileName in mediaStore.listFiles():
            raise ZException(_extstr(u"mediastorageztest.FileNotInStoreListError")) #$NON-NLS-1$
    # end execute()

# end ZVerifyFileListTestStep


# ------------------------------------------------------------------------------------------
# Implements step #4 in the testing of a media storage:  delete the test file from the store.
# ------------------------------------------------------------------------------------------
class ZDeleteTestFileTestStep(ZTestStep):

    def __init__(self):
        ZTestStep.__init__(self, _extstr(u"mediastorageztest.DeleteTestFile")) #$NON-NLS-1$
    # end __init__()

    def execute(self, mediaStore, session):
        testFilePath = session[u"upload.path"] #$NON-NLS-1$
        mediaStore.delete(testFilePath)
    # end execute()

# end ZDeleteTestFileTestStep


# ------------------------------------------------------------------------------------------
# Implements step #5 in the testing of a media storage:  verify that the test file was deleted
# ------------------------------------------------------------------------------------------
class ZVerifyDeleteTestStep(ZTestStep):

    def __init__(self):
        ZTestStep.__init__(self, _extstr(u"mediastorageztest.VerifyTestFileDeleted")) #$NON-NLS-1$
    # end __init__()

    def execute(self, mediaStore, session): #@UnusedVariable
        url = session[u"upload.url"] #$NON-NLS-1$
        if url.startswith(u"http"): #$NON-NLS-1$
            self._verifyHttpURL(url)
        else: # assume file path
            if os.path.exists(url):
                raise ZException(_extstr(u"mediastorageztest.FailedToDeleteFileError")) #$NON-NLS-1$
    # end execute()

    def _verifyHttpURL(self, url):
        tempFilePath = os.path.join(getApplicationModel().getUserProfile().getTempDirectory(), u"tmp_url_mstore_ztest.bin") #$NON-NLS-1$
        downloader = ZHttpBinaryFileDownload(url, tempFilePath)
        try:
            downloader.send()
            ct = downloader.getContentType()
            numBytes = downloader.getResponse()
            if (ct == u"image/png") and (numBytes == 222): #$NON-NLS-1$
                raise ZException(_extstr(u"mediastorageztest.FileStillExistsError") % url) #$NON-NLS-1$
        finally:
            if os.path.isfile(tempFilePath):
                os.remove(tempFilePath)
    # end _verifyHttpURL()

# end ZVerifyDeleteTestStep


# ------------------------------------------------------------------------------------------
# A class that implements an IZTest for testing the settings of a media storage.
# ------------------------------------------------------------------------------------------
class ZMediaStorageSettingsZTest(ZTest):

    def __init__(self, mediaStore):
        self.mediaStore = mediaStore
        self.session = {}
        
        ZTest.__init__(self)
        
        self.addStep(ZUploadFileTestStep())
        self.addStep(ZVerifyURLTestStep())
        if mediaStore.getCapabilities().supportsFileList():
            self.addStep(ZVerifyFileListTestStep())
        if mediaStore.getCapabilities().supportsDelete():
            self.addStep(ZDeleteTestFileTestStep())
            self.addStep(ZVerifyDeleteTestStep())
    # end __init__()

    def _runStep(self, step):
        time.sleep(0.5)
        step.execute(self.mediaStore, self.session)
    # end _runStep()

# end ZMediaStorageSettingsZTest
