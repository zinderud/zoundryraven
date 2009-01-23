from zoundry.base.zdom.dom import ZDom
import os

# -----------------------------------------------------------------------------------------
# The interface that all account serializer implementations must implement.
# -----------------------------------------------------------------------------------------
class IZAccountSerializer:

    def serialize(self, account):
        u"Called to serialize an account.  This should write out the account to the account's directory." #$NON-NLS-1$
    # end serialize()

# end IZAccountSerializer


# -----------------------------------------------------------------------------------------
# An implementation of an account serializer for version 1.0 (or 2006/06) of the Zoundry
# Raven account format.
# -----------------------------------------------------------------------------------------
class ZBlogAccountSerializer(IZAccountSerializer):

    def __init__(self, namespace):
        self.namespace = namespace
    # end __init__()

    def serialize(self, account):
        accountDom = ZDom()
        accountDom.loadXML(u"<account xmlns='%s' />" % self.namespace) #$NON-NLS-1$
        accountElem = accountDom.documentElement
        accountElem.setAttribute(u"type", u"weblog") #$NON-NLS-2$ #$NON-NLS-1$
        accountElem.setAttribute(u"account-id", account.getId()) #$NON-NLS-1$

        self._serializeAttributes(account, accountElem)
        self._serializeAPIInfo(account.getAPIInfo(), accountElem)
        self._serializeBlogs(account.getBlogs(), accountElem)

        self._saveDom(accountDom, account.getDirectoryPath())
    # end serialize()

    # Generic serialization of an attribute-based model.
    def _serializeAttributes(self, attrModel, parentElem):
        allAttributes = attrModel.getAllAttributes()
        if allAttributes is None or len(allAttributes) == 0:
            return

        attributesElem = parentElem.ownerDocument.createElement(u"attributes", self.namespace) #$NON-NLS-1$
        parentElem.appendChild(attributesElem)
        for (name, value, ns) in allAttributes:
            attributeElem = parentElem.ownerDocument.createElement(u"attribute", self.namespace) #$NON-NLS-1$
            attributesElem.appendChild(attributeElem)
            attributeElem.setAttribute(u"name", name) #$NON-NLS-1$
            attributeElem.setAttribute(u"namespace", ns) #$NON-NLS-1$
            attributeElem.setText(value)
    # end _serializeAttributes()

    def _serializeAPIInfo(self, apiInfo, parentElem):
        if apiInfo is None:
            return

        apiInfoElem = parentElem.ownerDocument.createElement(u"api-info", self.namespace) #$NON-NLS-1$
        parentElem.appendChild(apiInfoElem)

        self._serializeAttributes(apiInfo, apiInfoElem)
    # end _serializeAPIInfo()

    def _serializeBlogs(self, blogs, parentElem):
        if blogs is None or len(blogs) == 0:
            return

        blogsElem = parentElem.ownerDocument.createElement(u"blogs", self.namespace) #$NON-NLS-1$
        parentElem.appendChild(blogsElem)

        for blog in blogs:
            blogElem = parentElem.ownerDocument.createElement(u"blog", self.namespace) #$NON-NLS-1$
            blogsElem.appendChild(blogElem)
            blogElem.setAttribute(u"blog-id", blog.getId()) #$NON-NLS-1$
            self._serializeAttributes(blog, blogElem)
            self._serializeCategories(blog.getCategories(), blogElem)
    # end _serializeBlogs()

    def _serializeCategories(self, categories, parentElem):
        if categories is None or len(categories) == 0:
            return

        categoriesElem = parentElem.ownerDocument.createElement(u"categories", self.namespace) #$NON-NLS-1$
        parentElem.appendChild(categoriesElem)

        for category in categories:
            categoryElem = parentElem.ownerDocument.createElement(u"category", self.namespace) #$NON-NLS-1$
            categoriesElem.appendChild(categoryElem)
            self._serializeAttributes(category, categoryElem)
    # end _serializeCategories()

    def _saveDom(self, accountDom, accountDirectory):
        if not os.path.exists( accountDirectory ):
            os.makedirs( accountDirectory )
        domPath = os.path.join(accountDirectory, u"account.xml") #$NON-NLS-1$
        accountDom.save(domPath, True)
    # end _saveDom()

# end ZBlogAccountSerializer
