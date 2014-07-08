from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.models.ui.widgets.treemodel import IZTreeNodeModel
from zoundry.blogapp.constants import IZBlogAppServiceIDs
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.services.docindex.index import IZDocumentSearchFilter
from zoundry.blogapp.services.docindex.indeximpl import ZDocumentSearchFilter
from zoundry.blogapp.services.docindex.indeximpl import ZImageSearchFilter
from zoundry.blogapp.services.docindex.indeximpl import ZLinkSearchFilter
from zoundry.blogapp.services.docindex.indeximpl import ZTagSearchFilter


NODE_TYPE_POSTS = 1
NODE_TYPE_LINKS = 4
NODE_TYPE_IMAGES = 8
NODE_TYPE_TAGS = 16
NODE_TYPE_BLOG = 32
NODE_TYPE_ACCOUNT = 64
NODE_TYPE_UNPUBLISHED = 128
NODE_TYPE_DRAFTED = 256 #Vaigai-ZoundryRaven

NODE_PARAMS = {
        NODE_TYPE_POSTS : (_extstr(u"navigator.Posts"), u"posts", u"posts", False), #$NON-NLS-2$ #$NON-NLS-1$ #$NON-NLS-3$
        #NODE_TYPE_UNPUBLISHED : (_extstr(u"ZContextInfoEditedView"), u"posts", u"posts", False), #Vaigai-ZoundryRaven
        NODE_TYPE_DRAFTED : (_extstr(u"navigator.Edited"), u"posts", u"posts", False), #Vaigai-ZoundryRaven
        NODE_TYPE_LINKS : (_extstr(u"navigator.Links"), u"links", u"links", False), #$NON-NLS-2$ #$NON-NLS-1$ #$NON-NLS-3$
        NODE_TYPE_IMAGES : (_extstr(u"navigator.Images"), u"images", u"images", False), #$NON-NLS-2$ #$NON-NLS-1$ #$NON-NLS-3$
        NODE_TYPE_TAGS : (_extstr(u"navigator.Tags"), u"tags", u"tags", False), #$NON-NLS-2$ #$NON-NLS-1$ #$NON-NLS-3$
}


# --------------------------------------------------------------------------------------
# Interface for visitors of the Navigator Tree.
# --------------------------------------------------------------------------------------
class IZNavigatorTreeVisitor:

    def visit(self, node):
        u"Called when the visitor visits a node in the tree." #$NON-NLS-1$
    # end visit()

# end IZNavigatorTreeVisitor


# --------------------------------------------------------------------------------------
# Base class for nodes in the Navigator's tree.
# --------------------------------------------------------------------------------------
class ZNavigatorTreeNode(IZTreeNodeModel):

    def __init__(self):
        self.priority = 0
    # end __init__()

    def setPriority(self, priority):
        self.priority = priority
        for child in self.getChildren():
            priority = child.setPriority(priority + 1)
        return priority
    # end setPriority()

    def getPriority(self):
        return self.priority
    # end getPriority()

    def getLabel(self):
        u"Returns the label." #$NON-NLS-1$
        return None
    # end getLabel()

    def getChildren(self):
        u"Returns the children." #$NON-NLS-1$
        return []
    # end getChildren()

    def getImageLabel(self):
        u"Returns the image index." #$NON-NLS-1$
        return None
    # end getImageLabel()

    def getSelectedImageLabel(self):
        u"Returns the selected image index." #$NON-NLS-1$
        return self.getImageLabel()
    # end getSelectedImageLabel()

    def isBold(self):
        return False
    # end isBold()

    def isExpanded(self):
        return False
    # end isExpanded()

    def compareTo(self, otherNode):
        if self.getPriority() == otherNode.getPriority():
            return 0
        elif self.getPriority() < otherNode.getPriority():
            return -1
        else:
            return 1
    # end compareTo()

    def getType(self):
        u"Returns the node type." #$NON-NLS-1$
        return None
    # end getType()

    def addDocumentIDO(self, documentIDO): #@UnusedVariable
        u"Adds a document IDO to this model.  Returns True if a change was made to this node." #$NON-NLS-1$
        return False
    # end addDocumentIDO()

    def removeDocumentIDO(self, documentIDO): #@UnusedVariable
        u"Removes a document IDO from this model.  Returns True if a change was made to this node." #$NON-NLS-1$
        return False
    # end removeDocumentIDO()

    def addImageIDO(self, imageIDO): #@UnusedVariable
        u"Adds a image IDO to this model.  Returns True if a change was made to this node." #$NON-NLS-1$
        return False
    # end addImageIDO()

    def removeImageIDO(self, imageIDO): #@UnusedVariable
        u"Removes an image IDO from this model.  Returns True if a change was made to this node." #$NON-NLS-1$
        return False
    # end removeImageIDO()

    def addLinkIDO(self, linkIDO): #@UnusedVariable
        u"Adds a link IDO to this model.  Returns True if a change was made to this node." #$NON-NLS-1$
        return False
    # end addLinkIDO()

    def removeLinkIDO(self, linkIDO): #@UnusedVariable
        u"Removes a link IDO from this model.  Returns True if a change was made to this node." #$NON-NLS-1$
        return False
    # end removeLinkIDO()

    def addTagIDO(self, tagIDO): #@UnusedVariable
        u"Adds a tag IDO to this model.  Returns True if a change was made to this node." #$NON-NLS-1$
        return False
    # end addLinkIDO()

    def removeTagIDO(self, tagIDO): #@UnusedVariable
        u"Removes a tag IDO from this model.  Returns True if a change was made to this node." #$NON-NLS-1$
        return False
    # end removeLinkIDO()

    def updateAccount(self, account): #@UnusedVariable
        u"Called when the given account is updated - gives the nodes a chance to update themselves.  Returns True if the node changed as a result." #$NON-NLS-1$
        return False
    # end updateAccount()

    def updateBlog(self, blog): #@UnusedVariable
        u"Called when the given blog is updated - gives the nodes a chance to update themselves.  Returns True if the node changed as a result." #$NON-NLS-1$
        return False
    # end updateBlog()

    def saveLayout(self, metaData): #@UnusedVariable
        u"Called to save the layout of the node." #$NON-NLS-1$
        # Base class does nothing.
        pass
    # end saveLayout()

    def accept(self, visitor):
        visitor.visit(self)
        for child in self.getChildren():
            child.accept(visitor)
    # end accept()

    def hashCode(self):
        val = unicode(self.getType())
        return hash(val)
    # end hashCode()

# end ZNavigatorTreeNode


# --------------------------------------------------------------------------------------
# Base class for the Navigator's tree nodes.
# --------------------------------------------------------------------------------------
class ZNavigatorTreeSubNode(ZNavigatorTreeNode):

    def __init__(self, subNodeType):
        self.subNodeType = subNodeType
        self.parentBlog = None
        ZNavigatorTreeNode.__init__(self)
    # end __init__()

    def getLabel(self):
        return NODE_PARAMS[self.subNodeType][0]
    # end getLabel()

    def getImageLabel(self):
        return NODE_PARAMS[self.subNodeType][1]
    # end getImageLabel()

    def getSelectedImageLabel(self):
        return NODE_PARAMS[self.subNodeType][2]
    # end getSelectedImageLabel()

    def isBold(self):
        return NODE_PARAMS[self.subNodeType][3]
    # end isBold()

    def getParentBlog(self):
        return self.parentBlog
    # end getParentBlog()

    def setParentBlog(self, parentBlog):
        self.parentBlog = parentBlog
    # end setParentBlog()

    def getType(self):
        return self.subNodeType
    # end getType()

    def hashCode(self):
        vals = [
            self.getType(),
            self.parentBlog.getId()
        ]
        val = u"".join(map(unicode, vals)) #$NON-NLS-1$
        return hash(val)
    # end hashCode()

# end ZNavigatorTreeSubNode


# --------------------------------------------------------------------------------------
# Class to specifically model the "Posts" Blog sub-node.
# --------------------------------------------------------------------------------------
class ZNavigatorTreePostsNode(ZNavigatorTreeSubNode):

    def __init__(self):
        ZNavigatorTreeSubNode.__init__(self, NODE_TYPE_POSTS)
        self.filter = ZDocumentSearchFilter()
        self.postsCount = -1
    # end __init__()

    def getPostsCount(self):
        if self.postsCount == -1:
            self._configureFilter()
            self.postsCount = self._getPostsCount()
        return self.postsCount
    # end getPostsCount()

    def _configureFilter(self):
        if self.parentBlog:
            self.filter.setBlogIdCriteria(self.parentBlog.getId())
    # end _configureFilter()

    def _getPostsCount(self):
        docIndex = getApplicationModel().getEngine().getService(IZBlogAppServiceIDs.DOCUMENT_INDEX_SERVICE_ID)
        return docIndex.getDocumentCount(self.filter)
    # end _getPostsCount()

    def getSearchFilter(self):
        return self.filter
    # end getSearchFilter()

    def getLabel(self):
        label = ZNavigatorTreeSubNode.getLabel(self)
        return u"%s (%d)" % (label, self.getPostsCount()) #$NON-NLS-1$
    # end getLabel()

    def addDocumentIDO(self, documentIDO):
        if self.postsCount != -1 and self.filter.matches(documentIDO):
            self.postsCount = self.postsCount + 1
            return True
        return False
    # end addDocumentIDO()

    def removeDocumentIDO(self, documentIDO):
        if self.postsCount != -1 and self.filter.matches(documentIDO):
            self.postsCount = self.postsCount - 1
            return True
        return False
    # end removeDocumentIDO()

# end ZNavigatorTreePostsNode

# --------------------------------------------------------------------------------------
#ZNavigatorTreeEditedPostsNode added
# by pitchaimuthu2050 21-06-2014 22:07 IST
# Class to specifically model the "Unpublished Posts" Blog sub-node.
# Vaigai-ZoundryRaven branch added this class if user edit existing blog the post is flaged as un published and un tagged from posts
# --------------------------------------------------------------------------------------
class ZNavigatorTreeEditedPostsNode(ZNavigatorTreeSubNode):

    def __init__(self):
        ZNavigatorTreeSubNode.__init__(self, NODE_TYPE_DRAFTED)
        self.filter = ZDocumentSearchFilter()
        self.postsCount = -1
    # end __init__()

    def getPostsCount(self):
        if self.postsCount == -1:
            self._configureFilter()
            self.postsCount = self._getPostsCount()
        return self.postsCount
    # end getPostsCount()

    def _configureFilter(self):
        self.filter.setAccountIdCriteria(IZDocumentSearchFilter.UNPUBLISHED_ACCOUNT_ID)
        if self.parentBlog:
        	self.filter.setBlogIdCriteria(IZDocumentSearchFilter.UNPUBLISHED_POSTS)
        self.filter.setBlogIdCriteria(True)
    # end _configureFilter()

    def _getPostsCount(self):
        docIndex = getApplicationModel().getEngine().getService(IZBlogAppServiceIDs.DOCUMENT_INDEX_SERVICE_ID)
        return docIndex.getDocumentCount(self.filter)
    # end _getPostsCount()

    def getSearchFilter(self):
        return self.filter
    # end getSearchFilter()

    def getLabel(self):
        label = ZNavigatorTreeSubNode.getLabel(self)
        return u"%s (%d)" % (label, self.getPostsCount()) #$NON-NLS-1$
    # end getLabel()

    def addDocumentIDO(self, documentIDO):
        if self.postsCount != -1 and self.filter.matches(documentIDO):
            self.postsCount = self.postsCount + 1
            return True
        return False
    # end addDocumentIDO()

    def removeDocumentIDO(self, documentIDO):
        if self.postsCount != -1 and self.filter.matches(documentIDO):
            self.postsCount = self.postsCount - 1
            return True
        return False
    # end removeDocumentIDO()

# end ZNavigatorTreeEditedPostsNode


# --------------------------------------------------------------------------------------
# Extends the Posts node to provide a model for the Posts child of the Unpublished
# account.  Sets the criteria on the filter to be "unpublished".
# --------------------------------------------------------------------------------------
class ZNavigatorTreeUnpublishedPostsNode(ZNavigatorTreePostsNode):

    def __init__(self):
        ZNavigatorTreePostsNode.__init__(self)
    # end __init__()

    def _configureFilter(self):
        self.filter.setAccountIdCriteria(IZDocumentSearchFilter.UNPUBLISHED_ACCOUNT_ID)
        self.filter.setBlogIdCriteria(IZDocumentSearchFilter.UNPUBLISHED_BLOG_ID)
    # end _configureFilter()

    def hashCode(self):
        vals = [
            self.getType(),
            IZDocumentSearchFilter.UNPUBLISHED_BLOG_ID
        ]
        val = u"".join(map(unicode, vals)) #$NON-NLS-1$
        return hash(val)
    # end hashCode()

# end ZNavigatorTreeUnpublishedPostsNode


# --------------------------------------------------------------------------------------
# Class to specifically model the "Links" Blog sub-node.
# --------------------------------------------------------------------------------------
class ZNavigatorTreeLinksNode(ZNavigatorTreeSubNode):

    def __init__(self):
        ZNavigatorTreeSubNode.__init__(self, NODE_TYPE_LINKS)
        self.filter = ZLinkSearchFilter()
        self.linksCount = -1
    # end __init__()

    def getSearchFilter(self):
        return self.filter
    # end getSearchFilter()

    def getLinksCount(self):
        if self.linksCount == -1:
            self._configureFilter()
            self.linksCount = self._getLinksCount()
        return self.linksCount
    # end getLinksCount()

    def _configureFilter(self):
        if self.parentBlog:
            self.filter.setBlogIdCriteria(self.parentBlog.getId())
    # end _configureFilter()

    def _getLinksCount(self):
        docIndex = getApplicationModel().getEngine().getService(IZBlogAppServiceIDs.DOCUMENT_INDEX_SERVICE_ID)
        return docIndex.getLinkCount(self.filter)
    # end _getLinksCount()

    def getLabel(self):
        label = ZNavigatorTreeSubNode.getLabel(self)
        return u"%s (%d)" % (label, self.getLinksCount()) #$NON-NLS-1$
    # end getLabel()

    def addLinkIDO(self, linkIDO):
        if self.linksCount != -1 and self.filter.matches(linkIDO):
            self.linksCount = self.linksCount + 1
            return True
        return False
    # end addLinkIDO()

    def removeLinkIDO(self, linkIDO):
        if self.linksCount != -1 and self.filter.matches(linkIDO):
            self.linksCount = self.linksCount - 1
            return True
        return False
    # end removeLinkIDO()

# end ZNavigatorTreeLinksNode


# --------------------------------------------------------------------------------------
# Extends the Links node to provide a model for the Links child of the Unpublished
# account.  Sets the criteria on the filter to be "unpublished".
# --------------------------------------------------------------------------------------
class ZNavigatorTreeUnpublishedLinksNode(ZNavigatorTreeLinksNode):

    def __init__(self):
        ZNavigatorTreeLinksNode.__init__(self)
    # end __init__()

    def _configureFilter(self):
        self.filter.setAccountIdCriteria(IZDocumentSearchFilter.UNPUBLISHED_ACCOUNT_ID)
        self.filter.setBlogIdCriteria(IZDocumentSearchFilter.UNPUBLISHED_BLOG_ID)
    # end _configureFilter()

    def hashCode(self):
        vals = [
            self.getType(),
            IZDocumentSearchFilter.UNPUBLISHED_BLOG_ID
        ]
        val = u"".join(map(unicode, vals)) #$NON-NLS-1$
        return hash(val)
    # end hashCode()

# end ZNavigatorTreeUnpublishedLinksNode


# --------------------------------------------------------------------------------------
# Class to specifically model the "Images" Blog sub-node.
# --------------------------------------------------------------------------------------
class ZNavigatorTreeImagesNode(ZNavigatorTreeSubNode):

    def __init__(self):
        ZNavigatorTreeSubNode.__init__(self, NODE_TYPE_IMAGES)
        self.filter = ZImageSearchFilter()
        self.imagesCount = -1
    # end __init__()

    def getSearchFilter(self):
        return self.filter
    # end getSearchFilter()

    def getImagesCount(self):
        if self.imagesCount == -1:
            self._configureFilter()
            self.imagesCount = self._getImagesCount()
        return self.imagesCount
    # end getImagesCount()

    def _configureFilter(self):
        if self.parentBlog:
            self.filter.setBlogIdCriteria(self.parentBlog.getId())
    # end _configureFilter()

    def _getImagesCount(self):
        docIndex = getApplicationModel().getEngine().getService(IZBlogAppServiceIDs.DOCUMENT_INDEX_SERVICE_ID)
        return docIndex.getImageCount(self.filter)
    # end _getImagesCount()

    def getLabel(self):
        label = ZNavigatorTreeSubNode.getLabel(self)
        return u"%s (%d)" % (label, self.getImagesCount()) #$NON-NLS-1$
    # end getLabel()

    def addImageIDO(self, imageIDO):
        if self.imagesCount != -1 and self.filter.matches(imageIDO):
            self.imagesCount = self.imagesCount + 1
            return True
        return False
    # end addImageIDO()

    def removeImageIDO(self, imageIDO):
        if self.imagesCount != -1 and self.filter.matches(imageIDO):
            self.imagesCount = self.imagesCount - 1
            return True
        return False
    # end removeImageIDO()

# end ZNavigatorTreeImagesNode


# --------------------------------------------------------------------------------------
# Extends the Links node to provide a model for the Images child of the Unpublished
# account.  Sets the criteria on the filter to be "unpublished".
# --------------------------------------------------------------------------------------
class ZNavigatorTreeUnpublishedImagesNode(ZNavigatorTreeImagesNode):

    def __init__(self):
        ZNavigatorTreeImagesNode.__init__(self)
    # end __init__()

    def _configureFilter(self):
        self.filter.setAccountIdCriteria(IZDocumentSearchFilter.UNPUBLISHED_ACCOUNT_ID)
        self.filter.setBlogIdCriteria(IZDocumentSearchFilter.UNPUBLISHED_BLOG_ID)
    # end _configureFilter()

    def hashCode(self):
        vals = [
            self.getType(),
            IZDocumentSearchFilter.UNPUBLISHED_BLOG_ID
        ]
        val = u"".join(map(unicode, vals)) #$NON-NLS-1$
        return hash(val)
    # end hashCode()

# end ZNavigatorTreeUnpublishedImagesNode


# --------------------------------------------------------------------------------------
# Class to specifically model the "Tags" Blog sub-node.
# --------------------------------------------------------------------------------------
class ZNavigatorTreeTagsNode(ZNavigatorTreeSubNode):

    def __init__(self):
        ZNavigatorTreeSubNode.__init__(self, NODE_TYPE_TAGS)
        self.filter = ZTagSearchFilter()
        self.tagCount = -1
        self.tagIdList = []
    # end __init__()

    def getSearchFilter(self):
        return self.filter
    # end getSearchFilter()

    def getTagCount(self):
        if self.tagCount == -1:
            self._configureFilter()
            self.tagCount = self._getTagCount()
        return self.tagCount
    # end getTagCount()

    def _configureFilter(self):
        if self.parentBlog:
            self.filter.setBlogIdCriteria(self.parentBlog.getId())
    # end _configureFilter()

    def _getTagCount(self):
        docIndex = getApplicationModel().getEngine().getService(IZBlogAppServiceIDs.DOCUMENT_INDEX_SERVICE_ID)
        return docIndex.getTagCount(self.filter)
    # end _getTagCount()

    def getLabel(self):
        label = ZNavigatorTreeSubNode.getLabel(self)
        return u"%s (%d)" % (label, self.getTagCount()) #$NON-NLS-1$
    # end getLabel()

    def addTagIDO(self, tagIDO):
        if self.tagCount != -1 and self.filter.matches(tagIDO)and tagIDO.getId() not in self.tagIdList:
            self.tagCount = self.tagCount + 1
            self.tagIdList.append( tagIDO.getId() )
            return True
        return False
    # end addTagIDO()

    def removeTagIDO(self, tagIDO):
        if self.tagCount != -1 and self.filter.matches(tagIDO) and tagIDO.getId() in self.tagIdList:
            self.tagCount = self.tagCount - 1
            try:
                self.tagIdList.remove(tagIDO.getId())
            except:
                pass
            return True
        return False
    # end removeTagIDO()

# end ZNavigatorTreeTagsNode


# --------------------------------------------------------------------------------------
# Extends the Links node to provide a model for theTags child of the Unpublished
# account.  Sets the criteria on the filter to be "unpublished".
# --------------------------------------------------------------------------------------
class ZNavigatorTreeUnpublishedTagsNode(ZNavigatorTreeTagsNode):

    def __init__(self):
        ZNavigatorTreeTagsNode.__init__(self)
    # end __init__()

    def _configureFilter(self):
        self.filter.setAccountIdCriteria(IZDocumentSearchFilter.UNPUBLISHED_ACCOUNT_ID)
        self.filter.setBlogIdCriteria(IZDocumentSearchFilter.UNPUBLISHED_BLOG_ID)
    # end _configureFilter()

    def hashCode(self):
        vals = [
            self.getType(),
            IZDocumentSearchFilter.UNPUBLISHED_BLOG_ID
        ]
        val = u"".join(map(unicode, vals)) #$NON-NLS-1$
        return hash(val)
    # end hashCode()

# end ZNavigatorTreeUnpublishedTagsNode

# --------------------------------------------------------------------------------------
# Class for a blog node in the Navigator's tree.
# --------------------------------------------------------------------------------------
class ZNavigatorTreeBlogNode(ZNavigatorTreeNode):

    def __init__(self, blog):
        self.blog = blog
        self.children = [
                 ZNavigatorTreePostsNode(),
                 ZNavigatorTreeEditedPostsNode(),#pitchaimuthu
                 ZNavigatorTreeLinksNode(),
                 ZNavigatorTreeImagesNode(),
                 ZNavigatorTreeTagsNode(),
        ]
        for child in self.children:
            child.setParentBlog(blog)
        ZNavigatorTreeNode.__init__(self)
    # end __init__()

    def getLabel(self):
        return self.blog.getName()
    # end getLabel()

    def getChildren(self):
        return self.children
    # end getChildren()

    def getImageLabel(self):
        return u"blog" #$NON-NLS-1$
    # end getImageLabel()

    def getBlog(self):
        return self.blog
    # end getBlog()

    def _getExpandedXPath(self):
        return u"/user-properties/user-preferences/zoundry/raven/ui/views/standard/navigator/tree/blog-node[@id = \"%s\"]/expanded" % self.getBlog().getId() #$NON-NLS-1$
    # end _getExpandedXpath()

    def hashCode(self):
        return hash(self._getExpandedXPath())
    # end hashCode()

    def isExpanded(self):
        props = getApplicationModel().getUserProfile().getProperties()
        return props.getPropertyBool(self._getExpandedXPath(), True)
    # end isExpanded()

    def saveLayout(self, metaData):
        props = getApplicationModel().getUserProfile().getProperties()
        props.setProperty(self._getExpandedXPath(), unicode(metaData[u"expanded"]), False) #$NON-NLS-1$
    # end saveLayout()

    def getType(self):
        return NODE_TYPE_BLOG
    # end getType()

# end ZNavigatorTreeBlogNode


# --------------------------------------------------------------------------------------
# Class for an account node in the Navigator's tree.
# --------------------------------------------------------------------------------------
class ZNavigatorTreeAccountNode(ZNavigatorTreeNode):
    def __init__(self, account):
        self.account = account
        self.refreshChildren()
        ZNavigatorTreeNode.__init__(self)
    # end __init__()

    def refreshChildren(self):
        self.children = map(ZNavigatorTreeBlogNode, self.account.getBlogs())
    # end refreshChildren()

    def getLabel(self):
        return self.account.getName()
    # end getLabel()

    def getChildren(self):
        return self.children
    # end getChildren()

    def getImageLabel(self):
        return u"account" #$NON-NLS-1$
    # end getImageLabel()

    def getAccount(self):
        return self.account
    # end getAccount()

    def _getExpandedXPath(self):
        return u"/user-properties/user-preferences/zoundry/raven/ui/views/standard/navigator/tree/account-node[@id = \"%s\"]/expanded" % self.getAccount().getId() #$NON-NLS-1$
    # end _getExpandedXpath()

    def hashCode(self):
        return hash(self._getExpandedXPath())
    # end hashCode()

    def isExpanded(self):
        props = getApplicationModel().getUserProfile().getProperties()
        return props.getPropertyBool(self._getExpandedXPath(), True)
    # end isExpanded()

    def saveLayout(self, metaData):
        props = getApplicationModel().getUserProfile().getProperties()
        props.setProperty(self._getExpandedXPath(), unicode(metaData[u"expanded"]), False) #$NON-NLS-1$
    # end saveLayout()

    def updateAccount(self, account):
        if self.account == account:
            self.refreshChildren()
            return True
        return False
    # end updateAccount()

    def getType(self):
        return NODE_TYPE_ACCOUNT
    # end getType()

# end ZNavigatorTreeAccountNode


# --------------------------------------------------------------------------------------
# Class for an 'account' node in the Navigator's tree for all data that is not yet
# published.
# --------------------------------------------------------------------------------------
class ZNavigatorTreeUnpublishedNode(ZNavigatorTreeNode):

    def __init__(self):
        self.children = [
                 ZNavigatorTreeUnpublishedPostsNode(),
                 ZNavigatorTreeUnpublishedLinksNode(),
                 ZNavigatorTreeUnpublishedImagesNode(),
                 ZNavigatorTreeUnpublishedTagsNode(),
        ]
        ZNavigatorTreeNode.__init__(self)
    # end __init__()

    def getLabel(self):
        return _extstr(u"navigator.Unpublished") #$NON-NLS-1$
    # end getLabel()

    def getImageLabel(self):
        return u"unpublished" #$NON-NLS-1$
    # end getImageLabel()

    def _getExpandedXPath(self):
        return u"/user-properties/user-preferences/zoundry/raven/ui/views/standard/navigator/tree/unpublished-node/expanded" #$NON-NLS-1$
    # end _getExpandedXpath()

    def hashCode(self):
        return hash(self._getExpandedXPath())
    # end hashCode()

    def isExpanded(self):
        props = getApplicationModel().getUserProfile().getProperties()
        return props.getPropertyBool(self._getExpandedXPath(), True)
    # end isExpanded()

    def saveLayout(self, metaData):
        props = getApplicationModel().getUserProfile().getProperties()
        props.setProperty(self._getExpandedXPath(), unicode(metaData[u"expanded"]), False) #$NON-NLS-1$
    # end saveLayout()

    def getType(self):
        return NODE_TYPE_UNPUBLISHED
    # end getType()

    def getChildren(self):
        return self.children
    # end getChildren()

# end ZNavigatorTreeUnpublishedNode


# --------------------------------------------------------------------------------------
# Class for the root node in the Navigator's tree.
# --------------------------------------------------------------------------------------
class ZNavigatorTreeRootNode(ZNavigatorTreeNode):

    def __init__(self, accountList):
        self.children = [ZNavigatorTreeUnpublishedNode()] + map(ZNavigatorTreeAccountNode, accountList)
        ZNavigatorTreeNode.__init__(self)
        self.setPriority(0)
    # end __init__()

    def getLabel(self):
        return u"" #$NON-NLS-1$
    # end getLabel()

    def getChildren(self):
        return self.children
    # end getChildren()

    def addAccount(self, account):
        self.children.append(ZNavigatorTreeAccountNode(account))
    # end addAccount()

    def removeAccount(self, account):
        for child in self.children:
            if isinstance(child, ZNavigatorTreeAccountNode) and child.getAccount() == account:
                self.children.remove(child)
                return
    # end removeAccount()

# end ZNavigatorTreeRootNode


# -------------------------------------------------------------------------------------------
# Visits the Navigator tree in order to deliver index events.  This class builds up a list
# of nodes that have been modified by the visit.
# -------------------------------------------------------------------------------------------
class ZIndexEventTreeVisitor(IZNavigatorTreeVisitor):

    def __init__(self, ido, method):
        self.ido = ido
        self.method = method
        self.dirtyNodes = []
    # end __init__()

    def visit(self, node):
        method = getattr(node, self.method)
        if method(self.ido):
            self.dirtyNodes.append(node)
    # end visit()

    def getDirtyNodes(self):
        return self.dirtyNodes
    # end getDirtyNodes()

# end ZIndexEventTreeVisitor


# -------------------------------------------------------------------------------------------
# This is the data model class for the Navigator view (found in the Standard Perspective).
# -------------------------------------------------------------------------------------------
class ZNavigatorModel:

    def __init__(self):
        engine = getApplicationModel().getEngine()
        accountStore = engine.getService(IZBlogAppServiceIDs.ACCOUNT_STORE_SERVICE_ID)

        self.rootNode = ZNavigatorTreeRootNode(accountStore.getAccounts())
    # end __init__()

    def getNavigatorTreeRoot(self):
        return self.rootNode
    # end getNavigatorTreeRoot()

    def addAccount(self, account):
        self.rootNode.addAccount(account)
    # end addAccount()

    def removeAccount(self, account):
        self.rootNode.removeAccount(account)
    # end removeAccount()

    def updateAccount(self, account):
        # FIXME (EPW) need a different name for ZIndexEventTreeVisitor - more generic
        visitor = ZIndexEventTreeVisitor(account, u"updateAccount") #$NON-NLS-1$
        self.rootNode.accept(visitor)
        return visitor.getDirtyNodes()
    # end updateAccount()

    # Called when the indexer fires a 'document added' event.  This adds the document IDO to
    # the model and returns a list of nodes that have changed.
    def addDocumentIDO(self, documentIDO):
        visitor = ZIndexEventTreeVisitor(documentIDO, u"addDocumentIDO") #$NON-NLS-1$
        self.rootNode.accept(visitor)
        return visitor.getDirtyNodes()
    # end addDocumentIDO()

    # Called when the indexer fires an 'document removed' event.  This removes the document IDO from
    # the model and returns a list of nodes that have changed.
    def removeDocumentIDO(self, documentIDO):
        visitor = ZIndexEventTreeVisitor(documentIDO, u"removeDocumentIDO") #$NON-NLS-1$
        self.rootNode.accept(visitor)
        return visitor.getDirtyNodes()
    # end removeDocumentIDO()

    # Called when the indexer fires a 'image added' event.  This adds the image IDO to
    # the model and returns a list of nodes that have changed.
    def addImageIDO(self, imageIDO):
        visitor = ZIndexEventTreeVisitor(imageIDO, u"addImageIDO") #$NON-NLS-1$
        self.rootNode.accept(visitor)
        return visitor.getDirtyNodes()
    # end addImageIDO()

    # Called when the indexer fires an 'image removed' event.  This removes the image IDO from
    # the model and returns a list of nodes that have changed.
    def removeImageIDO(self, imageIDO):
        visitor = ZIndexEventTreeVisitor(imageIDO, u"removeImageIDO") #$NON-NLS-1$
        self.rootNode.accept(visitor)
        return visitor.getDirtyNodes()
    # end removeImageIDO()

    # Called when the indexer fires a 'link added' event.  This adds the link IDO to
    # the model and returns a list of nodes that have changed.
    def addLinkIDO(self, linkIDO):
        visitor = ZIndexEventTreeVisitor(linkIDO, u"addLinkIDO") #$NON-NLS-1$
        self.rootNode.accept(visitor)
        return visitor.getDirtyNodes()
    # end addLinkIDO()

    # Called when the indexer fires an 'link removed' event.  This removes the link IDO from
    # the model and returns a list of nodes that have changed.
    def removeLinkIDO(self, linkIDO):
        visitor = ZIndexEventTreeVisitor(linkIDO, u"removeLinkIDO") #$NON-NLS-1$
        self.rootNode.accept(visitor)
        return visitor.getDirtyNodes()
    # end removeLinkIDO()

    # Called when the indexer fires a 'tag added' event.  This adds the tag IDO to
    # the model and returns a list of nodes that have changed.
    def addTagIDO(self, tagIDO):
        visitor = ZIndexEventTreeVisitor(tagIDO, u"addTagIDO") #$NON-NLS-1$
        self.rootNode.accept(visitor)
        return visitor.getDirtyNodes()
    # end addTagIDO()

    # Called when the indexer fires an 'tag removed' event.  This removes the tag IDO from
    # the model and returns a list of nodes that have changed.
    def removeTagIDO(self, tagIDO):
        visitor = ZIndexEventTreeVisitor(tagIDO, u"removeTagIDO") #$NON-NLS-1$
        self.rootNode.accept(visitor)
        return visitor.getDirtyNodes()
    # end removeTagIDO()

# end ZNavigatorModel
