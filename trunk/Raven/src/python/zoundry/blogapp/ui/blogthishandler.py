from zoundry.blogapp.services.datastore.documentimpl import ZXhtmlContent
from zoundry.blogapp.services.datastore.blogdocumentimpl import ZBlogDocument
from zoundry.base.xhtml.xhtmldocutil import appendHtmlFragment
from zoundry.base.util.text.textutil import getNoneString
from zoundry.base.xhtml.xhtmldocutil import createHtmlElement
from zoundry.base.xhtml.xhtmlio import loadXhtmlDocumentFromString
from zoundry.base.xhtml.xhtmlio import loadXhtmlDocumentFromFile
import os.path
from zoundry.base.util.text.textutil import getSafeString

#-------------------------------------------------
# Class responsible for generating the xhtml content
# document from a IZBlogThisInformation
#-------------------------------------------------
class ZBlogThisHandler:

    def __init__(self, izBlogThisInformation):
        self.izBlogThisInformation = izBlogThisInformation
        format = getSafeString(self.izBlogThisInformation.getFormat()).lower()
        self.xmlFormat = format == u"xml" or format == u"xhtml" #$NON-NLS-1$ #$NON-NLS-2$
    # end __init__()

    def createBlogDocument(self):
        u"""createBlogDocument( -> IZBlogDocument""" #$NON-NLS-1$
        xhtmlDoc = self.createXhtmlDocument()
        doc = ZBlogDocument()
        title = getNoneString( self.izBlogThisInformation.getTitle() )
        if not title:
            title = getSafeString( xhtmlDoc.getTitle() )
        doc.setTitle( title )
        content = ZXhtmlContent()
        content.setMode(u"xml") #$NON-NLS-1$
        content.setType(u"application/xhtml+xml") #$NON-NLS-1$
        content.setXhtmlDocument(xhtmlDoc)
        doc.setContent(content)
        return doc
    # end createBlogDocument

    def createXhtmlDocument(self):
        u"""createXhtmlDocument() -> ZXhtmlDocument""" #$NON-NLS-1$
        file = getSafeString( self.izBlogThisInformation.getFile() )
        xhtmlDom = None
        if os.path.exists(file):
            try:
                xhtmlDom = loadXhtmlDocumentFromFile(file)
                return xhtmlDom
            except:
                pass
        # create new doc since file content was not found
        title = getSafeString( self.izBlogThisInformation.getTitle() )
        htmlString = u"<html><head><title>%s</title></head><body></body></html>" % title #$NON-NLS-1$
        xhtmlDoc = loadXhtmlDocumentFromString(htmlString)
        bodyNode = xhtmlDoc.getBody()
        self._createXhtmlContent(bodyNode)
        return xhtmlDoc
    # end createXhtmlDocument

    def _createXhtmlContent(self, bodyNode):
        # create <p>
        createHtmlElement(bodyNode, u"p")  #$NON-NLS-1$
        # build content
        # 1: if url is given, then add "cited" content
        if getNoneString( self.izBlogThisInformation.getUrl() ):
            #
            self._createContentNodeFromUrlData(bodyNode)

        elif getNoneString(self.izBlogThisInformation.getText()):
            # content given as text (plain or xhtml) data.
            self._createContentNodeFromTextData(bodyNode)

        elif getNoneString( self.izBlogThisInformation.getTitle() ):
            # only the title is available
            createHtmlElement(bodyNode, u"p", elementText = self.izBlogThisInformation.getTitle() )  #$NON-NLS-1$

        # create trailing para
        createHtmlElement(bodyNode, u"p")  #$NON-NLS-1$
    # end _createXhtmlContent

    def _createContentNodeFromTextData(self, parentNode):
        if self.xmlFormat:
            # append xml/xhtml fragment
            contentNode = createHtmlElement(parentNode, u"div")  #$NON-NLS-1$
            appendHtmlFragment(contentNode, self.izBlogThisInformation.getText())
        else:
            # append simple text content
            contentNode = createHtmlElement(parentNode, u"p", elementText = self.izBlogThisInformation.getText())  #$NON-NLS-1$
        return contentNode
    #end _createContentNodeFromTextData

    def _createContentNodeFromUrlData(self, parentNode):
        # create content data base one blog post or web site data including 'cite' element
        # and a link back to original document
        url = getSafeString( self.izBlogThisInformation.getUrl() )
        title = self._escape( self.izBlogThisInformation.getTitle() )
        text = getNoneString(self.izBlogThisInformation.getText())
        author = getNoneString(self.izBlogThisInformation.getAuthor())

        # default title to permanent link
        citeTitle = url
        if title and title != url:
            citeTitle = title
        contentNode = createHtmlElement(parentNode, u"p") #$NON-NLS-1$
        if text:
            # since content is given, create content in <cite> element
            if author:
                citeTitle = citeTitle + u" (" + author + u")" #$NON-NLS-1$ #$NON-NLS-2$
            citeTitle = citeTitle + u": " #$NON-NLS-1$
            citeNode = createHtmlElement(contentNode, u"cite") #$NON-NLS-1$
            attrs = { u"href" : url } #$NON-NLS-1$
            if citeTitle != url:
                attrs[u"title"] =  citeTitle #$NON-NLS-1$
            # create a <a href="url">citeTitle</a> inside the cite element
            createHtmlElement(citeNode, u"a", attrs, citeTitle) #$NON-NLS-1$
            innerContentNode = parentNode
            # block quote if needed, then wrap the content node in a blockquote.
            if self.izBlogThisInformation.isQuoted():
                attrs = { u"cite" : url } #$NON-NLS-1$
                innerContentNode = createHtmlElement(innerContentNode, u"blockquote", attrs) #$NON-NLS-1$

            if self.xmlFormat:
                innerContentNode = createHtmlElement(innerContentNode, u"div", attrs) #$NON-NLS-1$
                appendHtmlFragment(innerContentNode, text)
            else:
                createHtmlElement(innerContentNode, u"p", elementText = text)  #$NON-NLS-1$
        else:
            # content is not given. in this case, simply create a link to the url
            attrs = { u"href" : url } #$NON-NLS-1$
            createHtmlElement(contentNode,u"a", attrs, citeTitle) #$NON-NLS-1$
            createHtmlElement(contentNode,u"br") #$NON-NLS-1$
        return contentNode
    # end _createContentNodeFromUrlData

    def _escape(self, s):
        s = getSafeString(s)
        s = s.replace(u"&apos;", u"'") #$NON-NLS-1$ #$NON-NLS-2$
        s = s.replace(u"&amp;", u"&") #$NON-NLS-1$ #$NON-NLS-2$
        s = s.replace(u"&quot;", u'\"') #$NON-NLS-1$ #$NON-NLS-2$
        s = s.replace(u"&nbsp;", u" ") #$NON-NLS-1$ #$NON-NLS-2$
        s = s.replace(u"&lt;", u"<") #$NON-NLS-1$ #$NON-NLS-2$
        s = s.replace(u"&gt;", u">") #$NON-NLS-1$ #$NON-NLS-2$
        return s
    # end escape

# end ZBlogThisHandler