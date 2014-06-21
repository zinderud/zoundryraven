from zoundry.appframework.util.xmlutil import ZXmlAttributes
from zoundry.blogapp.services.accountstore.accountimpl import ZAccountAPIInfo
from zoundry.blogapp.services.accountstore.accountimpl import ZBlogAccount
from zoundry.blogapp.services.accountstore.accountimpl import ZBlogFromAccount
from zoundry.blogapp.services.commonimpl import ZCategory


# -----------------------------------------------------------------------------------------
# The interface that all account deserializer implementations must implement.
# -----------------------------------------------------------------------------------------
class IZAccountDeserializer:

    def deserialize(self, accountDirectory, accountDom):
        u"Called to deserialize an account.  This should return an instance of ZAccount." #$NON-NLS-1$
    # end deserialize()

# end IZAccountDeserializer


# -----------------------------------------------------------------------------------------
# An implementation of an account deserializer for version 1.0 (or 2006/06) of the Zoundry
# Raven account format.
# -----------------------------------------------------------------------------------------
class ZBlogAccountDeserializer(IZAccountDeserializer):

    def __init__(self, namespace):
        self.namespace = namespace
        self.nssMap = { u"zns" : self.namespace } #$NON-NLS-1$
    # end __init__()

    def deserialize(self, accountDirectory, accountDom):
        accountDom.setNamespaceMap(self.nssMap)
        account = ZBlogAccount(accountDirectory)
        account.setId(accountDom.documentElement.getAttribute(u"account-id")) #$NON-NLS-1$

        self._deserializeAttributes(accountDom.documentElement, account)
        self._deserializeApiInfo(accountDom, account)
        self._deserializeBlogs(accountDom, account)

        return account
    # end deserialize()

    def _deserializeAttributes(self, parentNode, model):
        attributesNode = parentNode.selectSingleNode(u"zns:attributes") #$NON-NLS-1$
        xmlAttributes = ZXmlAttributes(attributesNode, self.namespace)
        for (name, value, namespace) in xmlAttributes.getAllAttributes():
            model.setAttribute(name, value, namespace)
    # end _deserializeAttributes()

    def _deserializeApiInfo(self, accountDom, account):
        apiInfo = ZAccountAPIInfo()

        apiInfoNode = accountDom.selectSingleNode(u"/zns:account/zns:api-info") #$NON-NLS-1$
        self._deserializeAttributes(apiInfoNode, apiInfo)

        account.setAPIInfo(apiInfo)
    # end _deserializeApiInfo()

    def _deserializeBlogs(self, accountDom, account):
        blogNodes = accountDom.selectNodes(u"/zns:account/zns:blogs/zns:blog") #$NON-NLS-1$
        for blogNode in blogNodes:
            self._deserializeBlog(blogNode, account)
    # end _deserializeApiInfo()

    def _deserializeBlog(self, blogNode, account):
        blog = ZBlogFromAccount()

        blog.setId(blogNode.getAttribute(u"blog-id")) #$NON-NLS-1$
        self._deserializeAttributes(blogNode, blog)
        self._deserializeBlogCategories(blogNode, blog)

        account.addBlog(blog)
    # end _deserializeBlog()

    def _deserializeBlogCategories(self, blogNode, blog):
        categoryNodes = blogNode.selectNodes(u"zns:categories/zns:category") #$NON-NLS-1$
        for categoryNode in categoryNodes:
            self._deserializeBlogCategory(categoryNode, blog)
    # end _deserializeBlogCategories()
    
    def _deserializeBlogCategory(self, categoryNode, blog):
        category = ZCategory()
        
        self._deserializeAttributes(categoryNode, category)
        
        blog.addCategory(category)
    # end _deserializeBlogCategory()

# end ZBlogAccountDeserializer
