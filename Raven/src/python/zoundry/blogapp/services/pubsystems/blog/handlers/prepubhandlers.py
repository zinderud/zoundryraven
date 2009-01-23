# --------------------------------------------------------------------------
# Basic handlers that are run before publishing a document.
# --------------------------------------------------------------------------
from zoundry.blogapp.ui.util.tagsiteutil import getWordListFromZTagwords
from zoundry.blogpub.blogserverapi import IZBlogApiCapabilityConstants
from zoundry.blogapp.ui.util.blogutil import isCapabilitySupportedByBlog
from zoundry.blogapp.services.links.linksvcutil import getLinkFormattersByUrls
from zoundry.blogapp.services.links.link import IZLinkFormatType
from zoundry.blogapp.constants import IZBlogAppServiceIDs
from zoundry.appframework.global_services import getApplicationModel
from zoundry.blogapp.constants import IZBlogAppUserPrefsKeys
from zoundry.base.util.text.textutil import getNoneString
from zoundry.base.util.urlutil import getFilePathFromUri
from zoundry.base.util.urlutil import isLocalFile
from zoundry.base.zdom.dom import ZDom
from zoundry.blogapp.services.pubsystems.blog.handlers.pubprocesshandlers import ZBlogPostContentAnalyserBase
from zoundry.blogapp.services.pubsystems.blog.handlers.pubprocesshandlers import ZBlogPublishHandlerBase
import os.path

IMAGE_EXTS = u".jpg .jpeg .png .gif" #$NON-NLS-1$
#------------------------------------------------------------
# Cleanup the content for publishing.
# This implements the _prepare() method only and the handler does not do any publshing related work.
# The work units is zero.
#------------------------------------------------------------
class ZInitContentPrePublishHandler(ZBlogPublishHandlerBase):

    def __init__(self):
        ZBlogPublishHandlerBase.__init__(self, u"ZInitContentPrePublishHandler") #$NON-NLS-1$
    # end __init__

    def _prepare(self):
        xhtmlDocument = self._getContext().getXhtmlDocument()
        # fix img src and anchor href paths
        xhtmlDocument.checkFilePaths()
        # add rel = enclosure if needed
        analyser = ZBlogPostRelEnclosureAnalyser()
        xhtmlDocument.analyse(analyser)
        if self._getContext().getPubMetaData().isUploadTNsOnly():
            analyser2 = ZRemoveThumbnailImageLinkAnalyser()
            xhtmlDocument.analyse(analyser2)

        if self._getContext().getPubMetaData().isAddLightbox():
            analyser3 = ZAddLightboxRelEnclosureAnalyser()
            xhtmlDocument.analyse(analyser3)
    # end _prepare

# end ZInitContentPrePublishHandler
#------------------------------------------------------------
# Removes the link if only thumbnail images should be uploaded.
#------------------------------------------------------------
class ZRemoveThumbnailImageLinkAnalyser(ZBlogPostContentAnalyserBase):
    # FIXME (PJ) ZRemoveThumbnailImageLinkAnalyser should use special 'z:' attribute to detetermine parent/large image link
    def _analyseZXhtmlImage(self, iZXhtmlImage):
        tnElem = None
        linkElem = None
        if isLocalFile( iZXhtmlImage.getSrc() ):
            # img source points to a local image file.
            tnElem = iZXhtmlImage.getNode()
            if iZXhtmlImage.isLinked():
                # TN is linked. Check to see if the link exists and if it points to a local image
                iZXhtmlLink = iZXhtmlImage.getLink()
                if isLocalFile( iZXhtmlLink.getHref() ):
                    # parent link points to a local file.
                    # check if link is to an image
                    filePath = getFilePathFromUri( iZXhtmlLink.getHref() )
                    (base, ext) = os.path.splitext(filePath) #@UnusedVariable
                    if ext and IMAGE_EXTS.find(ext.strip()) != -1:
                        linkElem = iZXhtmlLink.getNode()
        if tnElem and linkElem:
            # remove TN
            tnElem = tnElem.parentNode.removeChild(tnElem)
            # import TB back to dom
            tnElem = linkElem.ownerDocument.importNode(tnElem, True)
            # replace link if TN
            linkElem.parentNode.replaceChild(tnElem, linkElem)

#------------------------------------------------------------
# Adds a rel="lightbox" attr if the link points to a image
#------------------------------------------------------------
class ZAddLightboxRelEnclosureAnalyser(ZBlogPostContentAnalyserBase):

    def _analyseZXhtmlLink(self, iZXhtmlLink):
        if not iZXhtmlLink.getHref() or len(iZXhtmlLink.getHref()) < 3:
            return
        idx = iZXhtmlLink.getHref().rfind(u".") #$NON-NLS-1$
        if idx < 1:
            return
        ext = iZXhtmlLink.getHref()[idx:].lower().strip()
        if ext and IMAGE_EXTS.find(ext.strip()) != -1 and not self._hasLightBoxRel( iZXhtmlLink.getRel() ):
            iZXhtmlLink.addRel(u"lightbox") #$NON-NLS-1$
    # end _analyseZXhtmlLink

    def _hasLightBoxRel(self, rel):
        if rel:
            relList = rel.lower().split(u" ") #$NON-NLS-1$
            for r in relList:
                if r == u"lightbox" or r.startswith(u"lightbox["): #$NON-NLS-1$ #$NON-NLS-2$
                    return True
        return False
    # end _hasLightBoxRel
# end ZAddLightboxRelEnclosureAnalyser

#------------------------------------------------------------
# Adds a rel="enclosure" attr if the link points to a local audio or video resource.
#------------------------------------------------------------
class ZBlogPostRelEnclosureAnalyser(ZBlogPostContentAnalyserBase):

    def _analyseZXhtmlLink(self, iZXhtmlLink):
        if iZXhtmlLink.isEnclosure():
            iZXhtmlLink.addRel(u"enclosure") #$NON-NLS-1$
            title = getNoneString( iZXhtmlLink.getTitle())
            if not title:
                name = iZXhtmlLink.getResourceName()
                size = iZXhtmlLink.getSize()
                if name and size > 0:
                    title = u"%s (%d bytes)" % (name, size) #$NON-NLS-1$
                elif name:
                    title = name
                if title:
                    iZXhtmlLink.setTitle(title)
    # end _analyseZXhtmlLink
# end ZBlogPostRelEnclosureAnalyser
#------------------------------------------------------------
# Adds the Powered By text to the bottom of the post during the process phase.
#------------------------------------------------------------
class ZAddPoweredByPrePublishHandler(ZBlogPublishHandlerBase):

    def __init__(self):
        ZBlogPublishHandlerBase.__init__(self, u"ZAddPoweredByPrePublishHandler") #$NON-NLS-1$

    def _process(self):
        xhtmlDocument = self._getContext().getXhtmlDocument()
        pubMetaData = self._getContext().getPubMetaData()
        if not pubMetaData or not pubMetaData.isAddPoweredBy():
            return
        bodyNode = xhtmlDocument.getDom().selectSingleNode(u"xhtml:body") #$NON-NLS-1$
        pNL = bodyNode.selectNodes(u"//xhtml:p[@class='poweredbyzoundry']") #$NON-NLS-1$
        if pNL and len(pNL) > 0 and pNL[-1]:
            # FIXME (PJ) check if the 'Zoundry BW' if so, change to 'Raven'.
            # grab the last para from the list
            # do we have a link to Zoundry?
            aLinkNode = pNL[-1].selectSingleNode(u"xhtml:a[@class='poweredbyzoundry_link']") #$NON-NLS-1$
            if aLinkNode:
                href= aLinkNode.getAttribute(u"href") #$NON-NLS-1$
                if href and href.find(u"zoundry.com") != -1: #$NON-NLS-1$
                    # we already have a link.
                    return
                # No link.  Continue and add a link in a new para to the end of the post
        xhtml = u'<p class="poweredbyzoundry">Powered by <a class="poweredbyzoundry_link" href="http://www.zoundryraven.com" rel="nofollow">Zoundry Raven</a></p>' #$NON-NLS-1$
        newDom = ZDom()
        newDom.loadXML(xhtml)
        poweredbyParaNode = xhtmlDocument.getDom().importNode(newDom.documentElement, True)
        bodyNode.appendChild(poweredbyParaNode)
    # end process()
# end ZAddPoweredByPrePublishHandler

#------------------------------------------------------------
# Adds the Tagwords to the bottom of the post during the process phase.
#------------------------------------------------------------
class ZAddTagwordsPrePublishHandler(ZBlogPublishHandlerBase):
    TAGS_TEMPLATE = u"""
<p class="zoundry_raven_tags">
  <!-- Tag links generated by Zoundry Raven. Do not manually edit. http://www.zoundryraven.com -->
  %s
</p>
"""         #$NON-NLS-1$

    def __init__(self):
        ZBlogPublishHandlerBase.__init__(self, u"ZAddTagwordsPrePublishHandler") #$NON-NLS-1$
    # end __init__()
    
    def _validateConfiguration(self,validationReporter): #@UnusedVariable
        blogName = self._getContext().getBlog().getName()
        listOfWords = self._getWordList()
        linkFormatterList = linkFormatterList = self._getFormatterList() #@UnusedVariable
        taggingSupported = isCapabilitySupportedByBlog(IZBlogApiCapabilityConstants.TAGGING, self._getContext().getBlog())
        if listOfWords and len(listOfWords) > 0:
            if not taggingSupported and (not linkFormatterList or len(linkFormatterList) == 0):
                s = u"One or more tag sites must be selected to create links to tagspaces for blog %s." % blogName #$NON-NLS-1$
                validationReporter.addWarning(u"Tagging", s) #$NON-NLS-1$ #$NON-NLS-2$
                self._getContext().logWarning(self, s)
        # end _validateConfiguration()

    def _process(self):
        u"""process() -> void
        """  #$NON-NLS-1$
                
        xhtmlDocument = self._getContext().getXhtmlDocument()
        # remove tagswords div if exists
        # for each tag space,  insert csv of tags.
        dom = xhtmlDocument.getDom()
        bodyNode = dom.selectSingleNode(u"xhtml:body") #$NON-NLS-1$
        # select new format that uses class="..."
        paraNode = dom.selectSingleNode(u"//xhtml:p[@class='zoundry_raven_tags']") #$NON-NLS-1$
        if not paraNode:
            # check if old bw class style is found. if found, remove it.
            paraNode = dom.selectSingleNode(u"//xhtml:p[@class='zoundry_bw_tags']") #$NON-NLS-1$
            if paraNode:
                # remove p tag
                paraNode.parentNode.removeChild(paraNode)
                paraNode = None

        if not paraNode:
            paraNode = dom.createElement(u"p") #$NON-NLS-1$
            paraNode.setAttribute(u"class", u"zoundry_raven_tags") #$NON-NLS-1$ #$NON-NLS-2$
            bodyNode.appendChild(paraNode)

        tagParaNode = None
        listOfWords = self._getWordList()
        linkFormatterList = self._getFormatterList()        
        if linkFormatterList and len(linkFormatterList) > 0 and listOfWords and len(listOfWords) > 0:
            # create document containg list of tags
            tagParaNode = self._createTagsPNode(linkFormatterList, listOfWords)
        if tagParaNode:
            # append tag <p> tag
            tagParaNode = dom.importNode(tagParaNode, True)
            paraNode.parentNode.replaceChild(tagParaNode, paraNode)
        else:
            # remove p tag
            paraNode.parentNode.removeChild(paraNode)
    # end process()
    
    def _createTagsPNode(self, linkFormatterList, listOfWords):        
        allSitesHtml = u"" #$NON-NLS-1$
        count = 0
        for formatter in linkFormatterList:
            tagHtml = self._createTagSiteHtml(formatter, listOfWords)
            allSitesHtml = allSitesHtml + tagHtml
            count = count + 1
            if len ( linkFormatterList ) > 1 and count < len( linkFormatterList ):
                allSitesHtml = allSitesHtml + u" <br/>\n " #$NON-NLS-1$
        html = ZAddTagwordsPrePublishHandler.TAGS_TEMPLATE % allSitesHtml
        html = html.replace(u'&', u'&amp;') #$NON-NLS-1$ #$NON-NLS-2$
        newDom = ZDom()
        newDom.loadXML(html)
        return newDom.documentElement
    # end _createTagsPNode()
    
    def _createTagSiteHtml(self, izLinkFormatter, listOfWords):        
        tagName = izLinkFormatter.getName()
        tagCount = 0
        tagHtml = u'<span class="ztags"><span class="ztagspace">' + tagName + u'</span> : ' #$NON-NLS-1$ #$NON-NLS-2$
        for tag in listOfWords:
            tagCount = tagCount + 1
            url = izLinkFormatter.formatUrl(tag)
            tagHtml = tagHtml + u'<a class="ztag" href="' + url + u'" rel="tag">' + tag + u'</a>' #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$
            if len ( listOfWords ) > 1 and tagCount < len( listOfWords ):
                tagHtml = tagHtml + u", " #$NON-NLS-1$
        #end for tag
        tagHtml = tagHtml + u"</span> " #$NON-NLS-1$
        return tagHtml
    # end _createTagSiteHtml() 
    
    def _getFormatterList(self):
        pubMetaData = self._getContext().getPubMetaData()
        tagsiteUrls = pubMetaData.getTagspaceUrls() 
        # get list of tag site formatters
        linkFormatterList = getLinkFormattersByUrls(IZLinkFormatType.TAG, tagsiteUrls)  
        return linkFormatterList      
    # end _getFormatterList()
    
    def _getWordList(self):
        # get list of IZTagwords
        izTagwordsList = self._getContext().getTagwordList()
        # extract a string list from the list of IZTagwords
        listOfWords = getWordListFromZTagwords(izTagwordsList)
        return listOfWords
    # end _getWordList()

# end ZAddTagwordsPrePublishHandler


#------------------------------------------------------------
# Converts product links to affiliate links
#------------------------------------------------------------
class ZCreateAffiliateLinksPublishHandler(ZBlogPublishHandlerBase):

    def __init__(self, zblog):
        ZBlogPublishHandlerBase.__init__(self, u"ZCreateAffiliateLinksPublishHandler") #$NON-NLS-1$
        self.zblog = zblog
    # end __init__()

    def _process(self):
        blogPrefs = self.zblog.getPreferences()
        convert = blogPrefs.getUserPreferenceBool(IZBlogAppUserPrefsKeys.AUTO_CONVERT_AFFILIATE_LINKS, True)
        if not convert:
            return        
        xhtmlDocument = self._getContext().getXhtmlDocument()
        analyser = ZCreateDonationJarAffiliateLinksAnalyser()
        xhtmlDocument.analyse(analyser)
    # end process()    
# end ZCreateAffiliateLinksPublishHandler

#------------------------------------------------------------
# Converts Amazon and Buy.com links to affiliate links
#------------------------------------------------------------
class ZCreateDonationJarAffiliateLinksAnalyser(ZBlogPostContentAnalyserBase):

    def __init__(self):
        self.productService = getApplicationModel().getService(IZBlogAppServiceIDs.PRODUCTS_SERVICE_ID)
    # end __init__()
    
    def _analyseZXhtmlLink(self, iZXhtmlLink):
        href = getNoneString( iZXhtmlLink.getHref() )
        if not href or len(href) < 10:
            return
        affiliateLink = self.productService.createZoundryAffiliateLink(href)
        if affiliateLink:
            iZXhtmlLink.setHref(affiliateLink)            
    # end _analyseZXhtmlLink
# end ZCreateDonationJarAffiliateLinksAnalyser
