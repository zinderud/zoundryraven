from zoundry.appframework.global_services import getApplicationModel
from zoundry.base.util.text.textutil import getNoneString
from zoundry.base.util.text.textutil import getSafeString
from zoundry.blogapp.constants import IZBlogAppServiceIDs
from zoundry.blogapp.services.datastore.blogdocumentimpl import ZTagwords
from zoundry.blogapp.ui.editors.blogeditorctrls.blogselector import IZBlogSelectorModel
from zoundry.blogapp.ui.util.blogutil import createDefaultPubMetaData
from zoundry.blogapp.ui.util.blogutil import getWPPublishedInfoAttribute
from zoundry.blogapp.ui.util.blogutil import setCustomWPMetaDataAttribute
from zoundry.blogpub.namespaces import IZBlogPubTagwordNamespaces

# ------------------------------------------------------------------------------
# Data model for blog meta data
# ------------------------------------------------------------------------------
class ZBlogPostMetaDataModel(IZBlogSelectorModel):

    def __init__(self):
        self.accountStore = getApplicationModel().getService(IZBlogAppServiceIDs.ACCOUNT_STORE_SERVICE_ID)
        self.title = u"" #$NON-NLS-1$
        self.tagwords = u"" #$NON-NLS-1$
        self.pubmetaDataList = []
    # end __init__()

    def setInitDocument(self, document):
        u"""setInitDocument(IZBlogDocument) -> void
        Copies the document data to the model.""" #$NON-NLS-1$
        # Initialize the model data  with the given document
        title = getSafeString(document.getTitle())
        self.setTitle(title)

        self.setTagwords(u"") #$NON-NLS-1$
        # get tagwords based on default NS
        iZTagwordsObj = document.getTagwords(IZBlogPubTagwordNamespaces.DEFAULT_TAGWORDS_URI)
        if not iZTagwordsObj:
            # legacy, pre alpha build 132 support. check technorati ns. # FIXME (PJ) remove technorati tags NS for final release
            iZTagwordsObj = document.getTagwords(u"http://technorati.com/tag/") #$NON-NLS-1$
        if iZTagwordsObj:
            self.setTagwords( iZTagwordsObj.getValue() )

        # Use any existing pub meta data if it exists, else fall back to
        # blog info list data.
        pubMetaDataList = document.getPubMetaDataList()
        if pubMetaDataList is None or len(pubMetaDataList) == 0:
            pubMetaDataList = []
            # create pub meta data from blog info list.
            blogInfoList = document.getBlogInfoList()
            if blogInfoList is not None and len(blogInfoList) > 0:
                for blogInfo in blogInfoList:
                    pubMetaData = self._createPubMetaData(blogInfo)
                    pubMetaDataList.append(pubMetaData)

        if pubMetaDataList is not None:
            self.setPubMetaDataList(pubMetaDataList)
    # end setInitDocument()

    def updateDocument(self, document):
        u"""updateDocument(IZBlogDocument) -> void
        Copies the model data to the document.""" #$NON-NLS-1$
        # set title in document
        document.setTitle( self.getTitle() )
        tagwords = ZTagwords()
        tagwords.setUrl(IZBlogPubTagwordNamespaces.DEFAULT_TAGWORDS_URI)
        tagwords.setValue( self.getTagwords() )
        document.addTagwords(tagwords )

        # Meta data draft, date, image props
        document.setPubMetaDataList( self.getPubMetaDataList() )

    # end updateDocument()

    def getAllBlogs(self):
        blogs = []
        for account in self.accountStore.getAccounts():
            for blog in account.getBlogs():
                blogs.append(blog)
        return blogs
    # end getAllBlogs()

    def getAllAccounts(self):
        return self.accountStore.getAccounts()
    # end getAllAccounts()

    def _createPubMetaData(self, blogInfo):
        pubMetaData = createDefaultPubMetaData(blogInfo.getAccountId(), blogInfo.getBlogId())
        pubMetaData.setPublishAsDraft(blogInfo.getPublishInfo().isDraft())
        pubMetaData.setPublishTime(blogInfo.getPublishInfo().getPublishedTime())
        categories = blogInfo.getCategories()
        if categories is not None and len(categories) > 0:
            for category in categories:
                pubMetaData.addCategory(category)
        # WP custom attrs
        slug = getNoneString( getWPPublishedInfoAttribute(blogInfo.getPublishInfo(), u"wp_slug") ) #$NON-NLS-1$
        if slug:
            setCustomWPMetaDataAttribute(pubMetaData, u"wp_slug", slug) #$NON-NLS-1$
        pw = getSafeString( getWPPublishedInfoAttribute(blogInfo.getPublishInfo(), u"wp_password") ) #$NON-NLS-1$
        setCustomWPMetaDataAttribute(pubMetaData, u"wp_password", pw) #$NON-NLS-1$
        status = getNoneString( getWPPublishedInfoAttribute(blogInfo.getPublishInfo(), u"post_status") ) #$NON-NLS-1$
        if status:
            setCustomWPMetaDataAttribute(pubMetaData, u"post_status", status) #$NON-NLS-1$            
        return pubMetaData
    # end _createPubMetaData()

    def getPubMetaDataList(self):
        return self.pubmetaDataList
    # end getPubMetaDataList()

    def setPubMetaDataList(self, metaDataList):
        self.pubmetaDataList = metaDataList
    # end setPubMetaDataList()

    def getTitle(self):
        return self.title
    # end getTitle()

    def setTitle(self, title):
        self.title = getSafeString(title)
    # end setTitle()

    def getTagwords(self):
        return self.tagwords
    # end getTagwords()

    def setTagwords(self, tags):
        self.tagwords = getSafeString(tags)
    # end setTagwords()

# end ZBlogPostMetaDataModel


# ------------------------------------------------------------------------------
# Models the data needed by the blog post editor.
# ------------------------------------------------------------------------------
class ZBlogPostEditorModel:

    def __init__(self):
        self.metaDataModel = ZBlogPostMetaDataModel()
        self.document = None
        self.tagwords = u"" #$NON-NLS-1$
    # end __init__()

    def getMetaDataModel(self):
        return self.metaDataModel
    # end getMetaDataModel()

    def setDocument(self, document):
        self.document = document
        # update pub meta data
        if document and self.getMetaDataModel():
            self.getMetaDataModel().setInitDocument(document)
    # end setDocument()

    def getDocument(self):
        return self.document
    # end getDocument()

    def getTitle(self):
        return self.metaDataModel.getTitle()
    # end getTitle()

    def setTitle(self, title):
        self.metaDataModel.setTitle(title)
    # end setTitle()

    def saveDocument(self):
        u"""saveDocument() -> void
        Invoked by the editor framework when document needs to be saved.
        """ #$NON-NLS-1$
        if self.getDocument():
            dataStore = getApplicationModel().getService(IZBlogAppServiceIDs.DATA_STORE_SERVICE_ID)
            dataStore.saveDocument(self.getDocument())
    # end saveDocument()

# end ZBlogPostEditorModel
