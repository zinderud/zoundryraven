from zoundry.appframework.util.portableutil import isPortableEnabled
from zoundry.base.util.fileutil import makeRelativePath
from zoundry.base.util.urlutil import decodeUri
from zoundry.base.zdom.dom import ZDom
from zoundry.base.zdom.domvisitor import ZDomVisitor
from zoundry.blogapp.services.datastore.io.constants import IZDocumentSerializationConstants

# -----------------------------------------------------------------------------------------
# The interface that all document serializer implementations must implement.
# -----------------------------------------------------------------------------------------
class IZDocumentSerializer:

    def serialize(self, document):
        u"Called to serialize a document.  This should return a DOM." #$NON-NLS-1$
    # end serialize()

# end IZDocumentSerializer


# ------------------------------------------------------------------------------
# Visitor to turn absolute paths into relative paths in the blog content - this
# is needed for Raven2Go support (portable app).
# ------------------------------------------------------------------------------
class ZMakeRelativeFilePathVisitor(ZDomVisitor):

    def __init__(self, dataDir):
        self.dataDir = dataDir
    # end __init__()

    def visitElement(self, element):
        nodeName = element.nodeName.lower()
        if nodeName == u"a": #$NON-NLS-1$
            href = element.getAttribute(u"href") #$NON-NLS-1$
            if href and href.startswith(u"file:"): #$NON-NLS-1$
                newHref = self._convertUrl(href)
                if newHref:
                    element.setAttribute(u"href", newHref) #$NON-NLS-1$
        elif nodeName == u"img": #$NON-NLS-1$
            src = element.getAttribute(u"src") #$NON-NLS-1$
            if src and src.startswith(u"file:"): #$NON-NLS-1$
                newSrc = self._convertUrl(src)
                if newSrc:
                    element.setAttribute(u"src", newSrc) #$NON-NLS-1$
    # end visitElement()

    def _convertUrl(self, url):
        decodedFilePath = decodeUri(url)
        relativePath = makeRelativePath(self.dataDir, decodedFilePath)
        if relativePath != decodedFilePath:
            return u"%s/%s" % (IZDocumentSerializationConstants.RAVEN_BLOG_DOCUMENT_PATH_TOKEN, relativePath) #$NON-NLS-1$
    # end _convertUrl()

# end ZMakeRelativeFilePathVisitor


# -----------------------------------------------------------------------------------------
# An implementation of a document serializer for version 1.0 (or 2006/06) of the Zoundry
# Raven blog document format.
# -----------------------------------------------------------------------------------------
class ZBlogDocumentSerializer(IZDocumentSerializer):

    def __init__(self, namespace):
        self.namespace = namespace
        self.nssMap = { u"zns" : self.namespace } #$NON-NLS-1$
    # end __init__()

    def serialize(self, document, serializationContext):
        documentDom = ZDom()
        documentDom.loadXML(u"<entry xmlns='%s' />" % self.namespace) #$NON-NLS-1$

        entryElem = documentDom.documentElement
        entryElem.setAttribute(u"entry-id", document.getId()) #$NON-NLS-1$
        self._serializeAttributes(document, entryElem)
        self._serializeBlogs(document.getBlogInfoList(), entryElem)
        self._serializePubMetaData(document.getPubMetaDataList(), entryElem)
        self._serializeTagwords(document.getTagwordsList(), entryElem)
        self._serializeContent(document.getContent(), entryElem, serializationContext)
        self._serializeTrackbacks(document.getTrackbacks(), entryElem)
        return documentDom
    # end deserialize()

    def _serializeBlogs(self, blogInfoList, parentElem):
        if blogInfoList is None or len(blogInfoList) == 0:
            return

        blogsElem = parentElem.ownerDocument.createElement(u"blogs", self.namespace) #$NON-NLS-1$
        parentElem.appendChild(blogsElem)

        for blogInfo in blogInfoList:
            blogElem = parentElem.ownerDocument.createElement(u"blog", self.namespace) #$NON-NLS-1$
            blogsElem.appendChild(blogElem)
            blogElem.setAttribute(u"account-id", blogInfo.getAccountId()) #$NON-NLS-1$
            blogElem.setAttribute(u"blog-id", blogInfo.getBlogId()) #$NON-NLS-1$

            self._serializePublishInfo(blogInfo.getPublishInfo(), blogElem)
            self._serializeCategories(blogInfo.getCategories(), blogElem)
    # end _serializeBlogs()

    def _serializePubMetaData(self, pubMetaDataList, parentElem):
        if pubMetaDataList is None or len(pubMetaDataList) == 0:
            return

        pubElem = parentElem.ownerDocument.createElement(u"publishing", self.namespace) #$NON-NLS-1$
        parentElem.appendChild(pubElem)

        for pubMetaData in pubMetaDataList:
            metaDataElem = parentElem.ownerDocument.createElement(u"meta-data", self.namespace) #$NON-NLS-1$
            pubElem.appendChild(metaDataElem)
            self._serializeAttributes(pubMetaData, metaDataElem)
            self._serializePingSites(pubMetaData.getPingServices(), metaDataElem)
            self._serializeCategories(pubMetaData.getCategories(), metaDataElem)
            self._serializeTrackbackRefs(pubMetaData.getTrackbacks(), metaDataElem)
            self._serializeTagspaceUrls(pubMetaData.getTagspaceUrls(), metaDataElem)
            self._serializeCustomMetaData(pubMetaData, metaDataElem)
    # end _serializePubMetaData()

    def _serializeCustomMetaData(self, pubMetaData, parentElem):
        for namespace in pubMetaData.getCustomMetaDataNamespaces():
            izCustomMetaData = pubMetaData.getCustomMetaData(namespace)
            if not izCustomMetaData or len(izCustomMetaData.getAllAttributes()) == 0:
                continue
            custMetaDataElem = parentElem.ownerDocument.createElement(u"customMetaData", self.namespace) #$NON-NLS-1$
            parentElem.appendChild(custMetaDataElem)
            custMetaDataElem.setAttribute(u"metadata-namespace", namespace) #$NON-NLS-2$ #$NON-NLS-1$
            self._serializeAttributes(izCustomMetaData, custMetaDataElem)
    # end _serializeCustomMetaData

    def _serializePingSites(self, pingSites, parentElem):
        if not pingSites:
            return

        sitesElem = parentElem.ownerDocument.createElement(u"pingSites", self.namespace) #$NON-NLS-1$
        parentElem.appendChild(sitesElem)

        for site in pingSites:
            siteElem = sitesElem.ownerDocument.createElement(u"pingSite", self.namespace) #$NON-NLS-1$
            sitesElem.appendChild(siteElem)
            siteElem.setText(site.getAttribute(u"id")) #$NON-NLS-1$
    # end _serializePingSites()

    def _serializeTagwords(self, tagwordsList, parentElem):
        if tagwordsList is None or len(tagwordsList) == 0:
            return

        tagwordsetElem = parentElem.ownerDocument.createElement(u"tagwordset", self.namespace) #$NON-NLS-1$
        parentElem.appendChild(tagwordsetElem)

        for tagwords in tagwordsList:
            tagwordsElem = parentElem.ownerDocument.createElement(u"tagwords", self.namespace) #$NON-NLS-1$
            tagwordsetElem.appendChild(tagwordsElem)
            tagwordsElem.setAttribute(u"url", tagwords.getUrl()) #$NON-NLS-1$
            tagwordsElem.setText(tagwords.getValue())
    # end _serializeTagwords()

    def _serializeTagspaceUrls(self, tagspaceUrlList, parentElem):
        if not tagspaceUrlList:
            return
        tagspacesElem = parentElem.ownerDocument.createElement(u"tagspaces", self.namespace)  #$NON-NLS-1$
        for url in tagspaceUrlList:
            elem = parentElem.ownerDocument.createElement(u"tagspace", self.namespace)  #$NON-NLS-1$
            elem.setText(url)
            tagspacesElem.appendChild(elem)
        parentElem.appendChild(tagspacesElem)
    # end  _serializeTagspaceUrls

    def _serializeTrackbackRefs(self, trackbacks, parentElem):
        self._serializeTrackbackList(u"trackbackrefs", u"trackbackref", trackbacks, parentElem) #$NON-NLS-1$ #$NON-NLS-2$
    # end  _serializeTrackbackRefs

    def _serializeTrackbacks(self, trackbacks, parentElem):
        self._serializeTrackbackList(u"trackbacks", u"trackback", trackbacks, parentElem) #$NON-NLS-1$ #$NON-NLS-2$
    # end  _serializeTrackbackRefs

    def _serializeTrackbackList(self, tbContainerElemName, tbElemName, trackbacks, parentElem):
        if trackbacks is None or len(trackbacks) == 0:
            return

        trackbacksElem = parentElem.ownerDocument.createElement(tbContainerElemName, self.namespace)
        parentElem.appendChild(trackbacksElem)

        for trackback in trackbacks:
            trackbackElem = parentElem.ownerDocument.createElement(tbElemName, self.namespace)
            trackbacksElem.appendChild(trackbackElem)
            self._serializeAttributes(trackback, trackbackElem)
    # end _serializeTrackbacks()

    def _serializeContent(self, content, parentElem, serializationContext):
        if not content:
            return

        contentElem = parentElem.ownerDocument.createElement(u"content", self.namespace) #$NON-NLS-1$
        parentElem.appendChild(contentElem)
        contentElem.setAttribute(u"mode", u"xml") #$NON-NLS-2$ #$NON-NLS-1$
        contentElem.setAttribute(u"type", u"application/xhtml+xml") #$NON-NLS-2$ #$NON-NLS-1$

        dom = content.toDocument()
        elem = dom
        if isinstance(dom, ZDom):
            elem = dom.documentElement
        elem = contentElem.ownerDocument.importNode(elem, True)
        self._processContent(elem, serializationContext)
        contentElem.appendChild(elem)
    # end _serializeContent()

    def _processContent(self, element, serializationContext):
        if isPortableEnabled():
            visitor = ZMakeRelativeFilePathVisitor(serializationContext.getDataDir())
            visitor.visit(element)
    # end _processContent()

    def _serializePublishInfo(self, pubInfo, parentElem):
        if pubInfo is None:
            return

        publishInfoElem = parentElem.ownerDocument.createElement(u"publish-info", self.namespace) #$NON-NLS-1$
        parentElem.appendChild(publishInfoElem)

        self._serializeAttributes(pubInfo, publishInfoElem)
        self._serializeTrackbackRefs(pubInfo.getTrackbacks(), publishInfoElem)
    # end _serializePublishInfo()

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

    # Generic serialization of an attribute-based model.
    def _serializeAttributes(self, attrModel, parentElem):
        if attrModel is None:
            return

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
            if value is not None:
                attributeElem.setText(unicode(value))
    # end _serializeAttributes()

# end ZBlogDocumentSerializer
