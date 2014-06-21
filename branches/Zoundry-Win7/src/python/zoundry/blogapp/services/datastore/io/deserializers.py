from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.util.xmlutil import ZXmlAttributes
from zoundry.base.util.fileutil import resolveRelativePath
from zoundry.base.util.text.textutil import getNoneString
from zoundry.base.util.text.textutil import getSafeString
from zoundry.base.util.urlutil import encodeUri
from zoundry.base.xhtml.xhtmlio import loadXhtmlDocumentFromDOM
from zoundry.base.xhtml.xhtmlio import loadXhtmlDocumentFromString
from zoundry.base.zdom.domvisitor import ZDomVisitor
from zoundry.blogapp.constants import IZBlogAppServiceIDs
from zoundry.blogapp.exceptions import ZBlogAppException
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.services.commonimpl import ZCategory
from zoundry.blogapp.services.datastore.blogdocumentimpl import ZBlogDocument
from zoundry.blogapp.services.datastore.blogdocumentimpl import ZBlogInfo
from zoundry.blogapp.services.datastore.blogdocumentimpl import ZCustomMetaData
from zoundry.blogapp.services.datastore.blogdocumentimpl import ZPubMetaData
from zoundry.blogapp.services.datastore.blogdocumentimpl import ZPublishInfo
from zoundry.blogapp.services.datastore.blogdocumentimpl import ZTagwords
from zoundry.blogapp.services.datastore.blogdocumentimpl import ZTrackback
from zoundry.blogapp.services.datastore.documentimpl import ZXhtmlContent
from zoundry.blogapp.services.datastore.io.constants import IZDocumentSerializationConstants


# -----------------------------------------------------------------------------------------
# The interface that all document deserializer implementations must implement.
# -----------------------------------------------------------------------------------------
class IZDocumentDeserializer:

    def deserialize(self, documentDom):
        u"Called to deserialize an document.  This should return an instance of IZDocument." #$NON-NLS-1$
    # end deserialize()

# end IZDocumentDeserializer


# ------------------------------------------------------------------------------
# Visitor to turn relative paths into absolute paths in the blog content - this
# is needed for Raven2Go support (portable app).
# ------------------------------------------------------------------------------
class ZResolveRelativeFilePathVisitor(ZDomVisitor):

    def __init__(self, dataDir):
        self.dataDir = dataDir
    # end __init__()

    def visitElement(self, element):
        nodeName = element.nodeName.lower()
        if nodeName == u"a": #$NON-NLS-1$
            href = element.getAttribute(u"href") #$NON-NLS-1$
            if href and self._isRelative(href):
                newHref = self._convertUri(href)
                if newHref:
                    element.setAttribute(u"href", newHref) #$NON-NLS-1$
        elif nodeName == u"img": #$NON-NLS-1$
            src = element.getAttribute(u"src") #$NON-NLS-1$
            if src and self._isRelative(src):
                newSrc = self._convertUri(src)
                if newSrc:
                    element.setAttribute(u"src", newSrc) #$NON-NLS-1$
    # end visitElement()

    def _isRelative(self, uri):
        return IZDocumentSerializationConstants.RAVEN_BLOG_DOCUMENT_PATH_TOKEN in uri
    # end _isRelative()

    def _convertUri(self, uri):
        magicNum = len(IZDocumentSerializationConstants.RAVEN_BLOG_DOCUMENT_PATH_TOKEN) + 1
        relativePath = uri[magicNum:]
        if relativePath:
            resolvedPath = resolveRelativePath(self.dataDir, relativePath)
            return encodeUri(resolvedPath)
        return None
    # end _convertUri()

# end ZResolveRelativeFilePathVisitor


# -----------------------------------------------------------------------------------------
# An implementation of a document deserializer for version 1.0 (or 2006/06) of the Zoundry
# Raven document format.
# -----------------------------------------------------------------------------------------
class ZBlogDocumentDeserializer(IZDocumentDeserializer):

    def __init__(self, namespace):
        self.namespace = namespace
        self.nssMap = { u"zns" : self.namespace } #$NON-NLS-1$
    # end __init__()

    def deserialize(self, documentDom, deserializationContext):
        documentDom.setNamespaceMap(self.nssMap)
        document = ZBlogDocument()
        document.setId(documentDom.documentElement.getAttribute(u"entry-id")) #$NON-NLS-1$

        self._deserializeAttributes(documentDom.documentElement, document)
        self._deserializeTrackbacks(documentDom, document)
        self._deserializeBlogInfoList(documentDom, document)
        self._deserializePubMetaDataList(documentDom, document)
        self._deserializeTagwordsList(documentDom, document)
        self._deserializeContent(documentDom, document, deserializationContext)

        return document
    # end deserialize()

    def _deserializeAttributes(self, parentNode, model):
        attributesNode = parentNode.selectSingleNode(u"zns:attributes") #$NON-NLS-1$
        # check for NPE (i.e. cases where attributes nodes do not exist).
        if attributesNode:
            xmlAttributes = ZXmlAttributes(attributesNode, self.namespace)
            for (name, value, namespace) in xmlAttributes.getAllAttributes():
                model.setAttribute(name, value, namespace)
    # end _deserializeAttributes()

    def _deserializeBlogInfoList(self, documentDom, document):
        nodes = documentDom.selectNodes(u"/zns:entry/zns:blogs/zns:blog") #$NON-NLS-1$
        for node in nodes:
            self._deserializeBlogInfo(node, document)
    # end _deserializeBlogInfoList()

    def _deserializeBlogInfo(self, blogInfoNode, document):
        blogInfo = ZBlogInfo()
        blogInfo.setAccountId(blogInfoNode.getAttribute(u"account-id")) #$NON-NLS-1$
        blogInfo.setBlogId(blogInfoNode.getAttribute(u"blog-id")) #$NON-NLS-1$

        self._deserializePublishInfo(blogInfoNode, blogInfo)
        self._deserializeCategories(blogInfoNode, blogInfo)

        document.addBlogInfo(blogInfo)
    # end _deserializeBlogInfo()

    def _deserializePublishInfo(self, blogInfoNode, blogInfo):
        pubInfoNode = blogInfoNode.selectSingleNode(u"zns:publish-info") #$NON-NLS-1$
        # pub info node is None for drafts.
        if pubInfoNode:
            pubInfo = ZPublishInfo()
            self._deserializeAttributes(pubInfoNode, pubInfo)
            self._deserializeSentTrackbacks(pubInfoNode, pubInfo)
            blogInfo.setPublishInfo(pubInfo)
    # end _deserializePublishInfo()

    def _deserializePubMetaDataList(self, documentDom, document):
        nodes = documentDom.selectNodes(u"/zns:entry/zns:publishing/zns:meta-data") #$NON-NLS-1$
        for node in nodes:
            self._deserializePubMetaData(node, document)
    # end _deserializePubMetaDataList()

    def _deserializePubMetaData(self, metaDataNode, document):
        pubMetaData = ZPubMetaData()
        self._deserializeAttributes(metaDataNode, pubMetaData)
        self._deserializePingSites(metaDataNode, pubMetaData)
        self._deserializeCategories(metaDataNode, pubMetaData)
        self._deserializePubMetadataTrackbacks(metaDataNode, pubMetaData)
        self._deserializePubMetadataTagspaces(metaDataNode, pubMetaData)
        self._deserializeCustomMetadata(metaDataNode, pubMetaData)
        document.addPubMetaData(pubMetaData)
    # end _deserializePubMetaData()

    def _deserializeCustomMetadata(self, metaDataNode, pubMetaData):
        nodes = metaDataNode.selectNodes(u"zns:customMetaData") #$NON-NLS-1$
        if not nodes:
            return
        for node in nodes:
            ns = node.getAttribute(u"metadata-namespace") #$NON-NLS-1$
            customData = ZCustomMetaData()
            self._deserializeAttributes(node, customData)
            pubMetaData.setCustomMetaData(ns, customData)
    # end _deserializeCustomMetadata()

    def _deserializePingSites(self, metaDataNode, pubMetaData):
        nodes = metaDataNode.selectNodes(u"zns:pingSites/zns:pingSite") #$NON-NLS-1$
        sites = []
        if nodes:
            publisherService = getApplicationModel().getService(IZBlogAppServiceIDs.PUBLISHING_SERVICE_ID)
            for node in nodes:
                siteId = node.getText()
                site = publisherService.findWeblogPingSiteById(siteId)
                if site is not None:
                    sites.append(site)

        pubMetaData.setPingServices(sites)
    # end _deserializePingSites()

    def _deserializePubMetadataTrackbacks(self, metaDataNode, pubMetaData):
        nodes = metaDataNode.selectNodes(u"zns:trackbackrefs/zns:trackbackref") #$NON-NLS-1$
        for node in nodes:
            trackback = ZTrackback()
            self._deserializeAttributes(node, trackback)
            pubMetaData.addTrackback(trackback)
    # end _deserializePubMetadataTrackbacks()

    def _deserializePubMetadataTagspaces(self, metaDataNode, pubMetaData):
        nodes = metaDataNode.selectNodes(u"zns:tagspaces/zns:tagspace") #$NON-NLS-1$
        for node in nodes:
            pubMetaData.addTagspaceUrl(node.getText())
    # end _deserializePubMetadataTagspaces()

    def _deserializeSentTrackbacks(self, pubInfoNode, pubInfo):
        nodes = pubInfoNode.selectNodes(u"zns:trackbackrefs/zns:trackbackref") #$NON-NLS-1$
        for node in nodes:
            sentTrackback = ZTrackback()
            self._deserializeAttributes(node, sentTrackback)
            if getNoneString( sentTrackback.getUrl() ) and sentTrackback.isSent():
                # 9/26/2007: Add only if url exists and tb has been sent. (url=None in docs imported from ZBW using build 0.8.109 or earlier. Ver 0.8.111 or later is OK)
                # (due to change of attr name from 'ping' to 'url'). Should not impact anyone since trackback support will be added ver 0.8.111+
                pubInfo.addTrackback(sentTrackback)
    # end _deserializeSentTrackbacks()

    def _deserializeCategories(self, blogInfoNode, blogInfo):
        nodes = blogInfoNode.selectNodes(u"zns:categories/zns:category") #$NON-NLS-1$
        for node in nodes:
            self._deserializeCategory(node, blogInfo)
    # end _deserializePublishInfoList()

    def _deserializeCategory(self, categoryNode, blogInfo):
        category = ZCategory()
        self._deserializeAttributes(categoryNode, category)
        blogInfo.addCategory(category)
    # end _deserializeCategory()

    def _deserializeTagwordsList(self, documentDom, document):
        nodes = documentDom.selectNodes(u"/zns:entry/zns:tagwordset/zns:tagwords") #$NON-NLS-1$
        for node in nodes:
            self._deserializeTagwords(node, document)
    # end _deserializeTagwordsList()

    def _deserializeTagwords(self, tagwordsNode, document):
        tagwords = ZTagwords()
        tagwords.setUrl(tagwordsNode.getAttribute(u"url")) #$NON-NLS-1$
        tagwords.setValue(getSafeString(tagwordsNode.getText()))
        document.addTagwords(tagwords)
    # end _deserializeTagwords()

    def _deserializeTrackbacks(self, documentDom, document):
        nodes = documentDom.selectNodes(u"/zns:entry/zns:trackbacks/zns:trackback") #$NON-NLS-1$
        for node in nodes:
            trackback = ZTrackback()
            self._deserializeAttributes(node, trackback)
            document.addTrackback(trackback)
    # end _deserializeTrackbacks()

    def _deserializeContent(self, documentDom, document, deserializationContext):
        contentNode = documentDom.selectSingleNode(u"/zns:entry/zns:content") #$NON-NLS-1$

        # Handle the Case of the Missing Content
        if not contentNode:
            xhtmlDoc = loadXhtmlDocumentFromString(u"") #$NON-NLS-1$
            content = ZXhtmlContent()
            content.setMode(u"xml") #$NON-NLS-1$
            content.setType(u"application/xhtml+xml") #$NON-NLS-1$
            content.setXhtmlDocument(xhtmlDoc)
            document.setContent(content)
            return

        self._processContent(contentNode, deserializationContext)

        mode = contentNode.getAttribute(u"mode") #$NON-NLS-1$
        type = contentNode.getAttribute(u"type") #$NON-NLS-1$

        content = ZXhtmlContent()
        content.setMode(mode)
        content.setType(type)

        if mode == u"xml": #$NON-NLS-1$
            xhtmlNode = contentNode.selectSingleNode(u"*") #$NON-NLS-1$
            xhtmlDoc = loadXhtmlDocumentFromDOM(xhtmlNode)
            content.setXhtmlDocument(xhtmlDoc)
        elif mode == u"escaped": #$NON-NLS-1$
            htmlText = contentNode.getText()
            xhtmlDoc = loadXhtmlDocumentFromString(htmlText)
            content.setXhtmlDocument(xhtmlDoc)
        else:
            raise ZBlogAppException(_extstr(u"deserializers.NoContentModeFoundError")) #$NON-NLS-1$

        document.setContent(content)
    # end _deserializeContent()

    def _processContent(self, element, deserializationContext):
        visitor = ZResolveRelativeFilePathVisitor(deserializationContext.getDataDir())
        visitor.visit(element)
    # end _processContent()

# end ZBlogAccountDeserializer
