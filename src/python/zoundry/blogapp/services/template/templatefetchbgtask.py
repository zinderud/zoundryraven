from zoundry.appframework.services.backgroundtask.backgroundtaskimpl import ZBackgroundTask
from zoundry.base.exceptions import ZException
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.services.template.templatefetch import IZTemplateFetchListener
from zoundry.blogapp.services.template.templatefetch import ZTemplateFetcher

# ------------------------------------------------------------------------------
# Implements a background task for fetching a template.
# ------------------------------------------------------------------------------
class ZTemplateFetchBGTask(ZBackgroundTask, IZTemplateFetchListener):

    def __init__(self):
        self.fetcher = None
        self.rootMessage = u"" #$NON-NLS-1$

        ZBackgroundTask.__init__(self)
    # end __init__()

    def initializeTaskParams(self, blog):
        self.fetcher = ZTemplateFetcher(blog, self)
        self.setName(u"%s (%s)" % (_extstr(u"templatefetchbgtask.DownloadingTemplate"), blog.getName())) #$NON-NLS-1$ #$NON-NLS-2$
        self.setNumWorkUnits(6)
    # end initializeTaskParams()

    def getCustomAttributes(self):
        pass
    # end getCustomAttributes()

    def setCustomAttributes(self, attributeMap):
        pass
    # end setCustomAttributes()

    def isResumable(self):
        return False
    # end isResumable()

    def cancel(self):
        self.fetcher.cancel()
    # end cancel()

    def _run(self):
        self.fetcher.run()
    # end _run()

    def onFetchStart(self):
        msg = _extstr(u"templatefetchbgtask.PublishingTemplateBlogPost") #$NON-NLS-1$
        self._incrementWork(u"%s..." % msg, 1, True) #$NON-NLS-1$
        self.rootMessage = u"%s: " % msg #$NON-NLS-1$
    # end onFetchStart()

    def onFetchTemplatePublished(self, permaLink): #@UnusedVariable
        msg = _extstr(u"templatefetchbgtask.DownloadingBlogTemplate") #$NON-NLS-1$
        self._incrementWork(u"%s..." % msg, 1, True) #$NON-NLS-1$
        self.rootMessage = u"%s: " % msg #$NON-NLS-1$
    # end onFetchTemplatePublished()

    def onFetchTemplateDownloaded(self):
        msg = _extstr(u"templatefetchbgtask.CleaningUpTemplateHTML") #$NON-NLS-1$
        self._incrementWork(u"%s..." % msg, 1, True) #$NON-NLS-1$
        self.rootMessage = u"%s: " % msg #$NON-NLS-1$
    # end onFetchTemplateDownloaded()

    def onFetchTemplateTrimmed(self):
        msg = _extstr(u"templatefetchbgtask.SavingTemplateToDisk") #$NON-NLS-1$
        self._incrementWork(u"%s..." % msg, 1, True) #$NON-NLS-1$
        self.rootMessage = u"%s: " % msg #$NON-NLS-1$
    # end onFetchTemplateTrimmed()

    def onFetchTemplateSaved(self):
        self._incrementWork(u"Template Downloaded Successfully.", 1, True) #$NON-NLS-1$
    # end onFetchTemplateSaved()

    def onFetchProgressInfo(self, text):
        text = self.rootMessage + text
        self._incrementWork(text, 0, False)
    # end onFetchProgressInfo()

    def onFetchComplete(self, templateId): #@UnusedVariable
        self._incrementWork(u"Done.", 1, True) #$NON-NLS-1$
    # end onFetchComplete()

    def onFetchError(self, error):
        if isinstance(error, ZException):
            self._raiseError(error.getMessage(), error.getStackTrace())
        else:
            self._raiseError(unicode(error), u"") #$NON-NLS-1$
    # end onFetchError()

# end ZTemplateFetchBGTask

