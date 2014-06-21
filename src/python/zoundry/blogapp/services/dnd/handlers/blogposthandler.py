from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.services.dnd.dnd import IZDnDHandler
from zoundry.appframework.ui.widgets.dialogs.standarddialogs import ZShowInfoMessage
from zoundry.blogapp.constants import IZBlogAppServiceIDs
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.services.dnd.dnd import IZBlogAppDnDSource
from zoundry.blogapp.ui.util.blogutil import getBlogPostUrl


# ------------------------------------------------------------------------------
# A handler that may get used when the user is dropping a blog post.
#
# FIXME (PJ) finish implementation of blog post DnD handler
# ------------------------------------------------------------------------------
class ZBlogPostDnDHandler(IZDnDHandler):
    
    def __init__(self):
        self.dataStore = None
    # end __init__()
    
    def getName(self):
        return _extstr(u"blogposthandler.BlogPost") #$NON-NLS-1$
    # end getName()

    def getDescription(self):
        return _extstr(u"blogposthandler.BlogPostDesc") #$NON-NLS-1$
    # end getDescription()

    def _getDataStore(self):
        if self.dataStore is None:
            self.dataStore = getApplicationModel().getService(IZBlogAppServiceIDs.DATA_STORE_SERVICE_ID)
        return self.dataStore
    # end _getDataStore()

    def canHandle(self, dndSource):
        if dndSource.hasType(IZBlogAppDnDSource.TYPE_BLOG_POST):
            postDnDSource = dndSource.getSource(IZBlogAppDnDSource.TYPE_BLOG_POST)
            docId = postDnDSource.getData()
            document = self._getDataStore().getDocument(docId)
            if document:
                url = getBlogPostUrl(document)
                return url is not None
        return False
    # end canHandle()

    def handle(self, dndSource, dndContext):
        postDnDSource = dndSource.getSource(IZBlogAppDnDSource.TYPE_BLOG_POST)
        docId = postDnDSource.getData()
        document = self._getDataStore().getDocument(docId)
        if document:
            url = getBlogPostUrl(document)
            if url:
                title = document.getTitle()
                return u'<a href="%s">%s</a>' % (url, title) #$NON-NLS-1$
            else:
                ZShowInfoMessage(dndContext.getWindow(), _extstr(u"blogposthandler.NoContentDroppedMsg"), _extstr(u"blogposthandler.NoContentTitle")) #$NON-NLS-2$ #$NON-NLS-1$

        return None
    # end handle()

# end ZBlogPostDnDHandler
