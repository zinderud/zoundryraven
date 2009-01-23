from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.global_services import getResourceRegistry
from zoundry.appframework.resources.resourceutils import ZMappedImageList
from zoundry.appframework.ui.widgets.controls.common.menu.menu import ZMenu
from zoundry.appframework.ui.widgets.controls.common.menu.menumodel import ZModelBasedMenuContentProvider
from zoundry.appframework.ui.widgets.controls.common.menu.menumodel import ZModelBasedMenuEventHandler
from zoundry.appframework.ui.widgets.controls.listex import IZListViewExContentProvider
from zoundry.appframework.ui.widgets.controls.listex import ZListViewEx
from zoundry.base.exceptions import ZAbstractMethodCalledException
from zoundry.blogapp.constants import IZBlogAppServiceIDs
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.services.docindex.index import IZBlogBasedSearchFilter
from zoundry.blogapp.services.docindex.indeximpl import ZBlogBasedSearchFilter
from zoundry.blogapp.services.docindex.indeximpl import ZDocumentSearchFilter
from zoundry.blogapp.ui.actions.blogpost.postactions import ZOpenBlogPostAction
from zoundry.blogapp.ui.menus.blogpost.postmenu import ZBlogPostActionContext
from zoundry.blogapp.ui.menus.blogpost.postmenumodel import ZBlogPostMenuModel
from zoundry.blogapp.ui.util.blogutil import getBlogFromIds
from zoundry.blogapp.ui.util.dateformatutil import formatLocalDateAndTime
from zoundry.blogapp.ui.util.viewutil import fireViewSelectionEvent
from zoundry.blogapp.ui.util.viewutil import fireViewUnselectionEvent
from zoundry.blogapp.ui.views.viewselimpl import ZDocumentSelection
import wx


# ------------------------------------------------------------------------------
# Model used to query index to get list of posts
# ------------------------------------------------------------------------------
class ZAbstractBlogPostsListQueryModel:

    def __init__(self):
        self.blogPosts = None
        self.accountIdCriteria = None
        self.blogIdCriteria = None
        self.blogEntryIdCriteria = None
        self.indexService = getApplicationModel().getService(IZBlogAppServiceIDs.DOCUMENT_INDEX_SERVICE_ID)
    # end __init__()

    def getBlogPosts(self):
        if self.blogPosts is None:
            self.blogPosts = self._findBlogPosts()
        return self.blogPosts
    # end getBlogPosts()

    def getDocumentIDO(self, index):
        return self.getBlogPosts()[index]

    def _findBlogPosts(self):
        searchFilter = self._createSearchFilter()
        if searchFilter is not None:
            if isinstance( searchFilter, ZBlogBasedSearchFilter):
                searchFilter.setAccountIdCriteria(self.accountIdCriteria)
                searchFilter.setBlogIdCriteria(self.blogIdCriteria)
                searchFilter.setBlogEntryIdCriteria(self.blogEntryIdCriteria)

            return self.indexService.findDocuments(searchFilter)
        else:
            return None
    # end _findBlogPosts()

    def clear(self):
        # reset the result set
        self.blogPosts = None
        self.accountIdCriteria = None
        self.blogIdCriteria = None
        self.blogEntryIdCriteria = None
    # end clear()

    def setAccountIdCriteria(self, id):
        self.accountIdCriteria = id
    # end setAccountIdCriteria()

    def setBlogIdCriteria(self, id):
        self.blogIdCriteria = id
    # end setBlogIdCriteria()

    def setBlogEntryIdCriteria(self, id):
        self.blogEntryIdCriteria = id
    # end setBlogEntryIdCriteria()

    def setBlogSearchCriteriaFilter(self, blogSearchFilter):
        if isinstance(blogSearchFilter, IZBlogBasedSearchFilter):
            self.setAccountIdCriteria( blogSearchFilter.getAccountIdCriteria())
            self.setBlogIdCriteria( blogSearchFilter.getBlogIdCriteria())
            self.setBlogEntryIdCriteria( blogSearchFilter.getBlogEntryIdCriteria())
    # end setBlogSearchCriteriaFilter()

    # Lets sub classes create concrete  filter.
    def _createSearchFilter(self):
        raise ZAbstractMethodCalledException(unicode(self.__class__), u"_createSearchFilter") #$NON-NLS-1$
    # end _createSearchFilter()

# end ZAbstractBlogPostsListQueryModel()

# ------------------------------------------------------------------------------
# Model used to query based on post
# ------------------------------------------------------------------------------
class ZBlogPostsListQueryModel(ZAbstractBlogPostsListQueryModel):

    def __init__(self):
        ZAbstractBlogPostsListQueryModel.__init__(self)
    # end __init__()

    def _createSearchFilter(self):
        return ZDocumentSearchFilter()
    # end _createSearchFilter()

# end ZBlogPostsListQueryModel


# ------------------------------------------------------------------------------
# Model used to query based on tag
# ------------------------------------------------------------------------------
class ZBlogPostsListByTagQueryModel(ZBlogPostsListQueryModel):

    def __init__(self):
        ZBlogPostsListQueryModel.__init__(self)
        self.tagIDO = None
        self.tagId = None

    def setTagIDO(self, tagIDO):
        self.tagIDO = tagIDO
        id = None
        if self.tagIDO:
            id = self.tagIDO.getId()
        self.setTagId(id)

    def setTagId(self, id):
        self.tagId = id
        self.clear()

    def _createSearchFilter(self):
        searchFilter = None
        if self.tagId is not None:
            searchFilter = ZDocumentSearchFilter()
            searchFilter.setTagIdCriteria(self.tagId)
        return searchFilter
# end ZBlogPostsListByTagQueryModel

# ------------------------------------------------------------------------------
# Model used to query based on image url
# ------------------------------------------------------------------------------
class ZBlogPostsListByImageQueryModel(ZBlogPostsListQueryModel):

    def __init__(self):
        ZBlogPostsListQueryModel.__init__(self)
        self.imageIDO = None
        self.imageUrl = None
    # end __init__()

    def setImageIDO(self, imageIDO):
        self.imageIDO = imageIDO
        url = None
        if self.imageIDO:
            url = self.imageIDO.getUrl()
        self.setImageUrl(url)
    # end setImageIDO()

    def setImageUrl(self, imageUrl):
        self.imageUrl = imageUrl
        self.clear()
    # end setImageUrl()

    def _createSearchFilter(self):
        searchFilter = None
        if self.imageUrl is not None:
            searchFilter = ZDocumentSearchFilter()
            searchFilter.setImageURLCriteria(self.imageUrl)
        return searchFilter
    # end _createSearchFilter()

# end ZBlogPostsListByImageQueryModel


# ------------------------------------------------------------------------------
# Model used to query based on iurl link url name
# ------------------------------------------------------------------------------
class ZBlogPostsListByLinkQueryModel(ZBlogPostsListQueryModel):

    def __init__(self):
        ZBlogPostsListQueryModel.__init__(self)
        self.linkIDO = None
        self.linkUrl = None

    def setLinkIDO(self, linkIDO):
        self.linkIDO = linkIDO
        url = None
        if self.linkIDO:
            url = self.linkIDO.getUrl()
        self.setLinkUrl(url)

    def setLinkUrl(self, linkUrl):
        self.linkUrl = linkUrl
        self.clear()

    def _createSearchFilter(self):
        searchFilter = None
        if self.linkUrl is not None:
            searchFilter = ZDocumentSearchFilter()
            searchFilter.setLinkURLCriteria(self.linkUrl)
        return searchFilter
# end ZBlogPostsListByLinkQueryModel


# FIXME share with image info and posts view?
IMAGE_LIST_DATA = [
       (u"document", u"images/perspectives/standard/contextinfo/postsview/document.png"), #$NON-NLS-1$ #$NON-NLS-2$
       (u"draft", u"images/perspectives/standard/contextinfo/postsview/draft.png") #$NON-NLS-1$ #$NON-NLS-2$
]


# ------------------------------------------------------------------------------
# A list view provider that provides the blog post information for the tag.
# ------------------------------------------------------------------------------
class ZBlogPostListProvider(IZListViewExContentProvider):

    def __init__(self, blogPostsListQueryModel):
        self.blogPostsListQueryModel = blogPostsListQueryModel
        self.imageList = self._createImageList()
        self.columnInfo = self._createColumnInfo()
    # end __init__()

    def _createColumnInfo(self):
        cstyle = wx.LIST_FORMAT_LEFT
        # FIXME (PJ / EPW) cols should be: Title, LastModified, Post/PublishedDate and CreatedDate (the post/published date is imported when viewing published entries)
        columnInfo = [
            (_extstr(u"blogpostslist.Title"), None, cstyle, ZListViewEx.COLUMN_RELATIVE, 70), #$NON-NLS-1$
            (_extstr(u"blogpostslist.Created"), None, cstyle, ZListViewEx.COLUMN_RELATIVE, 30) #$NON-NLS-1$
        ]
        return columnInfo

    def _createImageList(self):
        imgList = ZMappedImageList()
        for (label, imagePath) in IMAGE_LIST_DATA:
            imgList.addImage(label, getResourceRegistry().getBitmap(imagePath))
        return imgList
    # end _createImageList()

    def getImageList(self):
        return self.imageList
    # end getImageList()

    def getNumColumns(self):
        return len(self.columnInfo)
    # end getNumColumns()

    def getNumRows(self):
        rows = self.blogPostsListQueryModel.getBlogPosts()
        if rows is not None:
            return len(rows)
        return 0
    # end getNumRows()

    def getColumnInfo(self, columnIndex):
        if columnIndex >= 0 and columnIndex < len(self.columnInfo):
            return self.columnInfo[columnIndex]
        else:
            return (u"unknown-col-%d" % columnIndex, None, 0, ZListViewEx.COLUMN_RELATIVE, 20) #$NON-NLS-1$
    # end getColumnInfo()

    def getRowText(self, rowIndex, columnIndex):
        posts = self.blogPostsListQueryModel.getBlogPosts()
        if posts and rowIndex < len(posts):            
            data = posts[rowIndex]
            if columnIndex == 0:
                title = data.getTitle()
                if not title:
                    title = u"(%s)" % _extstr(u"blogpostslist.NoTitle") #$NON-NLS-1$ #$NON-NLS-2$
                return title
            if columnIndex == 1:
                # note: data.getPublishedTime() is None for local/unpublished documents
                return formatLocalDateAndTime (data.getCreationTime() )
        return u"" #$NON-NLS-1$
    # end getRowText()

    def getRowImage(self, rowIndex, columnIndex):
        if columnIndex == 0:
            posts = self.blogPostsListQueryModel.getBlogPosts()
            if posts and rowIndex < len(posts):
                docIDO = posts[rowIndex]
                if self._isDraft(docIDO):
                    return self.imageList[u"draft"] #$NON-NLS-1$
                else:
                    return self.imageList[u"document"] #$NON-NLS-1$
        return -1
    # end getRowImage()

    def _isDraft(self, docIDO):
        for pubIDO in docIDO.getPubDataIDOs():
            if pubIDO.getDraft():
                return True
        return False
    # end _isDraft()

# end ZBlogPostListProvider


# ------------------------------------------------------------------------------
# List view control panel that displays a list of blog posts.
# ------------------------------------------------------------------------------
class ZBlogPostListView(ZListViewEx):

    def __init__(self, parent, blogPostsListQueryModel = None, provider = None):
        if not blogPostsListQueryModel:
            blogPostsListQueryModel = ZBlogPostsListQueryModel()
        self.blogPostsListQueryModel = blogPostsListQueryModel
        if provider is None:
            provider = ZBlogPostListProvider(self.blogPostsListQueryModel)
        self.openAction = ZOpenBlogPostAction()
        self.blogPostContextMenu = ZBlogPostMenuModel()

        ZListViewEx.__init__(self, provider, parent)

        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onEntryActivated, self)
        self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.onEntryRightClick, self)
    # end __init__()

    def getModel(self):
        return self.blogPostsListQueryModel
    # end getModel()

    def onEntryActivated(self, event):
        index = event.GetIndex()
        docIDO = self.blogPostsListQueryModel.getDocumentIDO(index)
        actionContext = ZBlogPostActionContext(self, docIDO)
        self.openAction.runAction(actionContext)
    # end onEntryActivated()

    def onEntryRightClick(self, event):
        index = event.GetIndex()
        docIDO = self.blogPostsListQueryModel.getDocumentIDO(index)
        actionContext = ZBlogPostActionContext(self, docIDO)
        provider = ZModelBasedMenuContentProvider(self.blogPostContextMenu, actionContext)
        handler = ZModelBasedMenuEventHandler(self.blogPostContextMenu, actionContext)
        menu = ZMenu(self, self.blogPostContextMenu.getRootNode(), provider, handler)
        self.PopupMenu(menu)
        event.Skip()
    # end onEntryRightClick()

# end ZBlogPostListView


# ------------------------------------------------------------------------------
# Convenience class for a list of blog posts with a static box.
# ------------------------------------------------------------------------------
class ZBlogPostListViewWithStaticBox(wx.Panel):

    def __init__(self, parent, blogPostsListQueryModel, provider = None, label = u""): #$NON-NLS-1$
        wx.Panel.__init__(self, parent, wx.ID_ANY)
        self.model = blogPostsListQueryModel
        self.blogPostsStaticBox = wx.StaticBox(self, wx.ID_ANY, label)
        self.blogPostListView = ZBlogPostListView(self, self.model, provider = provider)
        bpSBox = wx.StaticBoxSizer(self.blogPostsStaticBox, wx.HORIZONTAL)
        bpSBox.Add(self.blogPostListView, 1, wx.EXPAND | wx.ALL, 2)
        vBox = wx.BoxSizer(wx.VERTICAL)
        vBox.AddSizer(bpSBox, 1, wx.EXPAND)
        self.SetSizer(vBox)
        self.SetAutoLayout(True)
    # end __init__()

    def getModel(self):
        return self.model
    # end getModel()

    def getListView(self):
        return self.blogPostListView
    # end getListView()

# end ZBlogPostListViewWithStaticBox


# ------------------------------------------------------------------------------
# Convenience class for where found list view with static box.
# ------------------------------------------------------------------------------
class ZWhereFoundBlogPostListView(ZBlogPostListViewWithStaticBox):

    def __init__(self, parent, blogPostsListQueryModel, provider = None): #$NON-NLS-1$
        self.document = None
        self.blog = None
        self.docStore = getApplicationModel().getService(IZBlogAppServiceIDs.DATA_STORE_SERVICE_ID)

        label = _extstr(u"blogpostslist.WhereFound") #$NON-NLS-1$
        ZBlogPostListViewWithStaticBox.__init__(self, parent, blogPostsListQueryModel, provider, label)

        self._bindWidgetEvents()
    # end __init__()
    
    def refresh(self):
        self.getListView().deselectAll()
        self.getListView().refresh()
    # end refresh()

    def _bindWidgetEvents(self):
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onBlogPostSelected, self.blogPostListView)

        wx.EVT_SET_FOCUS(self.blogPostListView, self.onFocus)
        wx.EVT_KILL_FOCUS(self.blogPostListView, self.onUnFocus)
    # end _bindWidgetEvents()

    def onBlogPostSelected(self, event):
        index = event.GetIndex()
        docIDO = self.model.getBlogPosts()[index]
        docId = docIDO.getId()
        self.document = self.docStore.getDocument(docId)
        self.blog = None
        
        if docIDO.getPubDataIDOs():
            pubDataIDO = docIDO.getPubDataIDOs()[0]
            self.blog = getBlogFromIds(pubDataIDO.getAccountId(), pubDataIDO.getBlogId())

        if self.document:
            fireViewSelectionEvent(ZDocumentSelection(self.document, self.blog))
        else:
            fireViewUnselectionEvent()

        event.Skip()
    # end onBlogPostSelected()

    def onFocus(self, event):
        if self.document:
            fireViewSelectionEvent(ZDocumentSelection(self.document, self.blog))
        else:
            fireViewUnselectionEvent()
        event.Skip()
    # end onFocus()

    def onUnFocus(self, event):
        fireViewUnselectionEvent()
        event.Skip()
    # end onUnFocus()

# end ZWhereFoundBlogPostListView
