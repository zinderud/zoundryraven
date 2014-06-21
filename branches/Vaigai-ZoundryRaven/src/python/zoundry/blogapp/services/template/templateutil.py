from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.global_services import getLoggerService
from zoundry.base.util.fileutil import getFileContents
from zoundry.base.util.text.textutil import getSafeString
from zoundry.base.xhtml.xhtmlanalyzers import ZXhtmlBodyFindingAnalyser
from zoundry.base.xhtml.xhtmldoc import ZXhtmlDocument
from zoundry.base.zdom.dom import ZDom
from zoundry.base.zdom.domvisitor import ZDomVisitor
from zoundry.blogapp.constants import IZBlogAppServiceIDs
from zoundry.blogapp.services.template.template import IZTemplateConstants
from zoundry.blogapp.services.template.templatetrim import ZTemplateBodyFindingVisitor
from zoundry.blogapp.services.template.templatetrim import ZTemplateTitleFindingVisitor
import os
import re

DOCTYPE_PATTERN = r"(<!DOCTYPE[^>]*>)" #$NON-NLS-1$
DOCTYPE_RE = re.compile(DOCTYPE_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)

APPLY_TEMPLATE_MODE_FULL = 0
APPLY_TEMPLATE_MODE_TITLE_AND_BODY = 1
APPLY_TEMPLATE_MODE_BODY_ONLY = 2


# ------------------------------------------------------------------------------
# Convenience function for getting a blog's template.
# ------------------------------------------------------------------------------
def getTemplateFromBlog(blog):
    u"""getTemplateFromBlog(IZBlog) -> IZTemplate
    Returns the template configured for the given blog
    or None if none is configured.""" #$NON-NLS-1$
    templateId = blog.getTemplateId()
    if templateId is not None:
        templateSvc = getApplicationModel().getService(IZBlogAppServiceIDs.TEMPLATE_SERVICE_ID)
        return templateSvc.getTemplate(templateId)

    return None
# end getTemplateFromBlog()


# ------------------------------------------------------------------------------
# Applies the given template to the given Raven document.  The return value is
# a xhtml document.
# ------------------------------------------------------------------------------
def applyTemplateToDocument(template, document, mode = APPLY_TEMPLATE_MODE_FULL):
    u"""applyTemplateToDocument(IZTemplate, IZDocument) -> ZXHtmlDocument""" #$NON-NLS-1$

    logger = getLoggerService()

    if template is None or document is None:
        logger.warning(u"applyTemplateToDocument:: Either template or document were None - skipping.") #$NON-NLS-1$
        return None

    title = getSafeString(document.getTitle())
    xhtmlDoc = None
    content = document.getContent()
    if content is not None:
        xhtmlDoc = content.getXhtmlDocument()

    if xhtmlDoc is None:
        logger.warning(u"applyTemplateToDocument:: XHtml document was None, skipping.") #$NON-NLS-1$
        return None

    analyzer = ZXhtmlBodyFindingAnalyser()
    xhtmlDoc.analyse(analyzer)
    xhtmlBody = analyzer.getBody()

    # At this point, we have the document's title and body.
    logger.debug(u"applyTemplateToDocument:: title: %s" % title) #$NON-NLS-1$

    # Get the path to the template file we want to use.
    templateDir = template.getTemplateDirectory()
    templateFileName = template.getAllFileName()
    if mode == APPLY_TEMPLATE_MODE_TITLE_AND_BODY:
        templateFileName = template.getTitleAndBodyFileName()
    elif mode == APPLY_TEMPLATE_MODE_BODY_ONLY:
        templateFileName = template.getBodyOnlyFileName()
    templateFilePath = os.path.join(templateDir, templateFileName)

    logger.debug(u"applyTemplateToDocument:: templateFileName: %s" % templateFileName) #$NON-NLS-1$
    logger.debug(u"applyTemplateToDocument:: templateFilePath: %s" % templateFilePath) #$NON-NLS-1$

    if os.path.isfile(templateFilePath) and xhtmlBody is not None:
        templateContent = getFileContents(templateFilePath)
        templateContent = _preprocessTemplateContent(templateContent, templateDir)
        
        templateDom = ZDom()
        templateDom.loadXML(templateContent)
        templateXHtml = ZXhtmlDocument(templateDom)

        # Get the DOCTYPE value from the root file (if any)
        rootFilePath = template.getResolvedRootFile()
        rootFileContent = None
        if os.path.isfile(rootFilePath):
            rootFile = open(rootFilePath, u"r") #$NON-NLS-1$
            try:
                rootFileContent = rootFile.read()
            finally:
                rootFile.close()
        if rootFileContent:
            results = DOCTYPE_RE.findall(rootFileContent)
            if results:
                docTypeString = results[0]
                templateXHtml.setDocTypeString(docTypeString)

        # Find the template body elements.
        visitor = ZTemplateBodyFindingVisitor()
        visitor.visit(templateDom)
        templateBodyElements = visitor.getBodyElements()

        if not templateBodyElements:
            logger.warning(u"applyTemplateToDocument:: failed to find any template body elements") #$NON-NLS-1$

        # Find the template title elements.
        visitor = ZTemplateTitleFindingVisitor()
        visitor.visit(templateDom)
        templateTitleElements = visitor.getTitleElements()

        if not templateTitleElements:
            logger.warning(u"applyTemplateToDocument:: failed to find any template title elements") #$NON-NLS-1$

        # Do title stuff - replace the ravenTitle elem with a span containing the title
        for templateTitleElem in templateTitleElements:
            titleParentElem = templateTitleElem.parentNode
            newTitleElem = templateDom.createElement(u"span") #$NON-NLS-1$
            newTitleElem.setText(title)
            titleParentElem.replaceChild(newTitleElem, templateTitleElem)

        # Do body stuff - insert all children of xhtmlBody, then remove the ravenBody elem
        for templateBodyElem in templateBodyElements:
            bodyParentElem = templateBodyElem.parentNode
            for node in xhtmlBody.getChildren():
                bodyParentElem.insertBefore(templateDom.importNode(node, True), templateBodyElem)
            bodyParentElem.removeChild(templateBodyElem)

        # IE hates empty DIVs and %20's in attributes.  Dunno why.
        _fixupIECrappiness(templateDom)

        return templateXHtml
    else:
        logger.warning(u"applyTemplateToDocument:: template file not found") #$NON-NLS-1$

    return xhtmlDoc
# end applyTemplateToDocument()


#-------------------------------------------------------------------------------
# Preprocess the template content by replacing the base path token with the 
# path to the template directory.
#-------------------------------------------------------------------------------
def _preprocessTemplateContent(content, templateDir):
    return content.replace(IZTemplateConstants.TEMPLATE_BASE_TOKEN, templateDir)
# end _preprocessTemplateContent()


#-------------------------------------------------------------------------------
# hack - override template font and margins
#-------------------------------------------------------------------------------
def _fixFontAndMargins(xhtmlDoc):
    # hack - override template font and margins.. FIXME (PJ) resovle template font and margin issues.
    # this method assigns a font size and margins to the body element if it does not already
    # have margins and fonts assigned. May not work with all templates since child elems of the body (e.g <p>)
    # can overrider the font size. In general, setting the font size on the body sets the "global" font size for
    # document.  Relative fonts will be based on the body font.
    body = xhtmlDoc.getBody()
    if body:
        style = xhtmlDoc.getBody().getAttribute(u"style") #$NON-NLS-1$
        if not style:
            style = u"" #$NON-NLS-1$
        if style.find(u"font-size") == -1: #$NON-NLS-1$
            style = style  + u" ;font-size:13px" #$NON-NLS-1$
        if style.find(u"margin") == -1: #$NON-NLS-1$
            style = style  + u" ;margin:10px;" #$NON-NLS-1$
        body.setAttribute(u"style", style) #$NON-NLS-1$
# end _fixFontAndMargins


def _fixupIECrappiness(xhtmlDom):
    # hack - when applying the template, converting to dom would have made
    # some syntactic changes to the html (since it's being treated as xml).
    # Syntactic changes that IE doesn't like are:
    #  1) empty divs go from:  "<div></div>" to "<div/>"
    #  2) change all %20's in attributes to spaces (might need to be done elsewhere)
    visitor = ZIEFixupDomVisitor()
    visitor.visit(xhtmlDom)
# end _fixupIECrappiness()


# ------------------------------------------------------------------------------
# Visitor used to fix up IE crappiness.
# ------------------------------------------------------------------------------
class ZIEFixupDomVisitor(ZDomVisitor):

    def visitElement(self, element):
        if not self._hasChildren(element) and element.getText() == u"": #$NON-NLS-1$
            divTxt = element.getText()
            if not divTxt:
                element.setText(u" ") #$NON-NLS-1$
        # Fix up a problem with Wordpress stats javascript
        if u"st_go(" in element.getText(): #$NON-NLS-1$
            text = element.getText().replace(u"st_go", u"//st_go") #$NON-NLS-2$ #$NON-NLS-1$
            text = text.replace(u"ex_go", u"//ex_go") #$NON-NLS-2$ #$NON-NLS-1$
            element.setText(text)
    # end visitElement()

    def visitAttribute(self, attribute):
        attrText = attribute.getText()
        if attrText and u"%20" in attrText: #$NON-NLS-1$
            attribute.setText(attrText.replace(u"%20", u" ")) #$NON-NLS-2$ #$NON-NLS-1$
        u"Called when an attribute is visited." #$NON-NLS-1$
    # end visitAttribute()

    def _hasChildren(self, element):
        return len(element.selectNodes(u"./*")) > 0 #$NON-NLS-1$
    # end _hasChildren()

# end ZIEFixupDomVisitor
