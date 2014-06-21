from zoundry.appframework.constants import IZAppServiceIDs
from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.ui.widgets.controls.advanced.mshtml.mshtmlelements import ZMshtmlDomVisitor
from zoundry.appframework.ui.widgets.controls.advanced.mshtml.mshtmlelements import getDispElement
from zoundry.appframework.ui.widgets.controls.advanced.mshtml.mshtmluiproxies import ZMshtmlExtendedEntryMarkerProxy
from zoundry.base.util.text.textutil import getNoneString
from zoundry.base.util.text.textutil import getSafeString
from zoundry.base.util.urlutil import getFilePathFromUri
from zoundry.base.util.urlutil import getUriFromFilePath
from zoundry.base.xhtml.xhtmlio import loadXhtmlDocumentFromString
from zoundry.base.zdom.domvisitor import ZDomVisitor
import os.path
import re

#-----------------------------------------------------
# Module for MSHTML visitors and other support classes
#-----------------------------------------------------

#-----------------------------------------------------
# Visitor for gettting the IHtmlBody elemen dispatch t from the mshtml dom.
#----------------------------------------------------
class ZMshtmlIHtmlBodyDispatchElementVisitorBase(ZMshtmlDomVisitor):


    def visitDocument(self, document):  #@UnusedVariable
        self.mshtmlDoc = document.node
        try:
            if self.mshtmlDoc.body:
                mshtmlBodyElement = getDispElement(self.mshtmlDoc.body)
                self._visitBodyDispatchElement(mshtmlBodyElement)
        except:
            # FIXME (PJ) log error
            return False
    # end visitDocument()

    def getMshtmlDocument(self):
        return self.mshtmlDoc
    # end getMshtmlDocument()

    def _visitBodyDispatchElement(self, mshtmlBodyElement): #@UnusedVariable
        pass
    # end _visitBodyDispatchElement()

#-----------------------------------------------------
# Visitor for fixing img css/border/align attributes as well
# as  src values for local unicode paths
#----------------------------------------------------
class ZMshtmlFixImgSrcVisitor(ZMshtmlIHtmlBodyDispatchElementVisitorBase):

    def _visitBodyDispatchElement(self, mshtmlBodyElement):
        self.mshtmlBodyElement = mshtmlBodyElement
        self._checkImgAttributes()
        self._checkImgUnicodePaths()
    # end _visitBodyDispatchElement

    def _checkImgUnicodePaths(self):
        eleList = self.mshtmlBodyElement.getElementsByTagName(u"IMG") #$NON-NLS-1$
        for ele in eleList:
            src = getNoneString(ele.getAttribute(u"src")) #$NON-NLS-1$
            if not src:
                continue
            localFilePath = getFilePathFromUri(src)
            if localFilePath and os.path.exists(localFilePath):
                # if local file path, then "set" image path - IE MSHTML quirk - to 'update' the image
                dispEle = getDispElement(ele) #@UnusedVariable
                dispEle.src = localFilePath
    # end _checkImgUnicodePaths

    def _checkImgAttributes(self):
        # 1) Set img runtime border if needed to 0 (remove border)
        # 2) Check img align attribtues
        # simple method to make sure if the image CSS has width and heigh but not image width and height
        # attribute, then create image width and height attributes.
        # (Work around for WordPress.com bug)
        eleList = self.mshtmlBodyElement.getElementsByTagName(u"IMG") #$NON-NLS-1$
        for ele in eleList:
            # verify image centering attrs are correct.
            if ele.style and ele.style.textAlign == u"center" and ele.style.display == u"block": #$NON-NLS-1$ #$NON-NLS-2$
                # img is supposed to be centered - add fire fox work around.
                if ele.style.marginLeft != u"auto": #$NON-NLS-1$
                    ele.style.marginLeft = u"auto" #$NON-NLS-1$
                    ele.style.marginRight = u"auto" #$NON-NLS-1$

            # set runtime border = 0, if border is not set by the user.
            # this is so that a border for hyperlinks is not shown
            hasBorder = ele.style.borderWidth != u"" or ele.style.borderLeftWidth != u"" #$NON-NLS-1$ #$NON-NLS-2$
            hasBorder = hasBorder or ele.style.borderRightWidth != u"" or ele.style.borderTopWidth != u"" or ele.style.borderBottomWidth != u"" #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$
            hasRtBorder = ele.runtimeStyle.borderWidth != u"" or ele.runtimeStyle.borderLeftWidth != u"" #$NON-NLS-1$ #$NON-NLS-2$
            hasRtBorder = hasRtBorder or ele.runtimeStyle.borderRightWidth != u"" or ele.runtimeStyle.borderTopWidth != u"" or ele.runtimeStyle.borderBottomWidth != u"" #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$

            if not hasBorder and not hasRtBorder: #$NON-NLS-1$
                # set implicit/runtime border =0
                ele.runtimeStyle.borderWidth = u"0px"; #$NON-NLS-1$
            elif hasBorder and hasRtBorder: #$NON-NLS-1$
                # remove runtime border if user has defined a border.
                ele.runtimeStyle.borderWidth = u""; #$NON-NLS-1$


            src = getNoneString(ele.getAttribute(u"src")) #$NON-NLS-1$
            if not src:
                continue

            # check if the img src is a local resource (file://) and if it exists
            localFilePath = getFilePathFromUri(src)
            if localFilePath and not os.path.exists(localFilePath):
                # Do not modify any local files that do not exist anymore (width and height info will not be available)
                #(i.e. not assign random/default width and heights)
                continue
            cssWidth = None
            cssHeight = None
            # get css sizes
            if ele.style and ele.style.width:
                cssWidth = getSafeString(ele.style.width)
            if ele.style and ele.style.height:
                cssHeight = getSafeString(ele.style.height)
            # get explicit size (i.e. set by the user via img width/height attribute)
            w = getSafeString( ele.getAttribute(u"width", 2) ) #$NON-NLS-1$  # pass flag=2 so that getAttribute() returns value iff one was explicitly specified.
            h = getSafeString( ele.getAttribute(u"height", 2) )#$NON-NLS-1$

            # note: getAttribute may also return the value found in the CSS style.
            # so, we should set it as an attribute in the <img> tag in case it did not exist as an attribute in the img tag.
            # for example, we want <img style="width:10px" src="" /> to be <img width="10" style="width:10px" src="" />
            # (that is add explicit width and height attributes)
            # grab size if explicit size is not available
            actualWidth = actualHeight = -1
            # if local file then get size directly from img.
            if localFilePath:# and (not w or not h):
                (actualWidth, actualHeight) = self._getImageSizeFromFile(localFilePath)
            # if not  local file, then ask IE for implicit img size (i.e. for remote (non-local) images)
            if not localFilePath and not w and not cssWidth and not h and not cssHeight:
                # first, ask IE for implicit width and height (usually returns actual image size)
                w = getSafeString( ele.getAttribute(u"width") ) #$NON-NLS-1$
                h = getSafeString( ele.getAttribute(u"height") ) #$NON-NLS-1$
            if w:
                ele.setAttribute(u"width", w) #$NON-NLS-1$
            elif cssWidth and not w:
                ele.setAttribute(u"width", cssWidth) #$NON-NLS-1$
            elif actualWidth > 0:
                ele.setAttribute(u"width", actualWidth) #$NON-NLS-1$

            if h:
                ele.setAttribute(u"height", h) #$NON-NLS-1$
            elif cssHeight and not h:
                ele.setAttribute(u"height", cssHeight) #$NON-NLS-1$
            elif actualHeight > 0:
                ele.setAttribute(u"height", actualHeight) #$NON-NLS-1$
    # end _checkImgAttributes()

    def _getImageSizeFromFile(self, imgPath):
        imgService = getApplicationModel().getService(IZAppServiceIDs.IMAGING_SERVICE_ID)
        (width, height) = imgService.getImageSize(imgPath)
        return (width, height)
    # end _getImageSize

# end ZMshtmlFixImgSrcVisitor()

#-----------------------------------------------------
# Visitor for converting html 4.01 tags to xhtml tags
#----------------------------------------------------
class ZMshtmlXhtmlConvertVisitor(ZMshtmlIHtmlBodyDispatchElementVisitorBase):

    def _visitBodyDispatchElement(self, mshtmlBodyElement):
        # Instead of traversling each element, the following convert methods
        # get calls getElementsByTagName each time it needs to a specific list
        # element since a previous 'convert' function may have modified the
        # underlying document model. (hence the traverser will not work since the document model is modified)

        self.mshtmlBodyElement = mshtmlBodyElement
        self._convertTags()
        self._convertAlignAttribute(u"P") #$NON-NLS-1$
        self._convertAlignAttribute(u"DIV") #$NON-NLS-1$
        self._checkFilePaths(u"A", u"href") #$NON-NLS-1$ #$NON-NLS-2$
        self._checkFilePaths(u"IMG", u"src") #$NON-NLS-1$ #$NON-NLS-2$
        return False
    # end visitDocument()

    def _replaceElement(self,  mshtmlElement, tag, cssStyle = None):
        openTag = tag
        if getNoneString(cssStyle):
            openTag =u"""%s style="%s" """  % (tag, cssStyle) #$NON-NLS-1$
        mshtmlElement.outerHTML = u"""<%s>%s</%s>""" % (openTag, mshtmlElement.innerHTML, tag) #$NON-NLS-1$
    # end _replaceTag

    def _wrapElement(self,  mshtmlElement, tag, cssStyle = None):
        openTag = tag
        if cssStyle:
            openTag =u"""%s style="%s" """  % (tag, cssStyle) #$NON-NLS-1$
        mshtmlElement.outerHTML = u"<%s>%s</%s>" % (openTag, mshtmlElement.outerHTML, tag) #$NON-NLS-1$
    # end _wrapElement

    def _replaceElements(self,  oldTag, newTag, cssStyle = None):
        all = self.mshtmlBodyElement.getElementsByTagName(oldTag)
        for ele in all:
            self._replaceElement(ele, newTag, cssStyle)
            self._replaceElements(oldTag, newTag, cssStyle)
            break
    # end _replaceElements()

    def _convertFonts(self):
        # Convert font tags for spans
        # Harded font-size mapping: 0-7 -> maps to 0.7em thru 3.0em
        EM_SIZES  = [u"0.6", u"0.75", u"0.90", u"1.0", u"1.2", u"1.5", u"2.0"] #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$ #$NON-NLS-4$ #$NON-NLS-5$ #$NON-NLS-6$ #$NON-NLS-7$
        eleList = self.mshtmlBodyElement.getElementsByTagName(u"FONT") #$NON-NLS-1$
        for ele in eleList:
            css = u"" #$NON-NLS-1$
            face = getNoneString(ele.getAttribute(u"face")) #$NON-NLS-1$
            if face:
                css = u"font-family:%s;" % face #$NON-NLS-1$
            sizeIdx = -1
            sizeStr = getNoneString(ele.getAttribute(u"size")) #$NON-NLS-1$
            if sizeStr:
                try:
                    sizeIdx = int(abs(float(sizeStr))) - 1
                    if sizeIdx < 0:
                        sizeIdx = 0
                    elif sizeIdx >= len(EM_SIZES):
                        sizeIdx = EM_SIZES - 1
                except:
                    pass
            if sizeIdx != -1:
                css = css + u"font-size:%sem;" % EM_SIZES[sizeIdx] #$NON-NLS-1$
            color = getNoneString(ele.getAttribute(u"color")) #$NON-NLS-1$
            if color:
                css = css + u"color:%s;" % color #$NON-NLS-1$
            self._replaceElement(ele, u"span", css) #$NON-NLS-1$
    # end _convertFonts()

    def _convertTags(self):
        # Convert HTML 4.0x tags to xhtml markup
        self._convertFonts()
        self._replaceElements(u"STRIKE", u"DEL") #$NON-NLS-1$ #$NON-NLS-2$
        self._replaceElements(u"S", u"DEL") #$NON-NLS-1$ #$NON-NLS-2$
        self._replaceElements(u"B", u"STRONG") #$NON-NLS-1$ #$NON-NLS-2$
        self._replaceElements(u"I", u"EM") #$NON-NLS-1$ #$NON-NLS-2$
        self._replaceElements(u"U", u"SPAN", u"text-decoration:underline") #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$
    # end _convertTags()

    def _convertAlignAttribute(self, tag):
        # Remove align attribute and add it as a css style instead
        eleList = self.mshtmlBodyElement.getElementsByTagName(tag)
        for ele in eleList:
            align = ele.getAttribute(u"align") #$NON-NLS-1$
            if align and align.strip() != u"" and ele.style:  #$NON-NLS-1$
                ele.removeAttribute(u"align") #$NON-NLS-1$
                ele.style.textAlign = align
    # end _convertAlignAttribute()


    def _checkFilePaths(self, nodeName, attrName):
        eleList = self.mshtmlBodyElement.getElementsByTagName(nodeName)
        for ele in eleList:
            pathValue = getNoneString(ele.getAttribute(attrName))
            if not pathValue:
                continue
            try:
                uri = getUriFromFilePath(pathValue)
                if uri and uri != pathValue:
                    ele.setAttribute(attrName, uri ) #$NON-NLS-1$
            except:
                pass
    # end _checkFilePaths()


#-----------------------------------------------------
# Visitor removing html comments based on regular expression matching
#----------------------------------------------------
class ZMshtmlRemoveCommentsVisitor(ZMshtmlIHtmlBodyDispatchElementVisitorBase):

    TEXT_MORE_RE = re.compile( r'\s*more\s*', re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL) #$NON-NLS-1$
    START_FRAG_RE = re.compile( r'\s*startFragment\s*', re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL) #$NON-NLS-1$
    END_FRAG_RE = re.compile( r'\s*endFragment\s*', re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL) #$NON-NLS-1$

    DEFAULT_PATTERNS = [TEXT_MORE_RE, START_FRAG_RE, END_FRAG_RE]
    FRAGMENT_PATTERNS = [START_FRAG_RE, END_FRAG_RE]

    def __init__(self, commentPatternList = []):
        self.commentPatternList = commentPatternList
    # end __init__()

    def _visitBodyDispatchElement(self, mshtmlBodyElement):  #@UnusedVariable
        self.mshtmlBodyElement = mshtmlBodyElement
        eleList = self.mshtmlBodyElement.getElementsByTagName(u"!") #$NON-NLS-1$
        for ele in eleList:
            for regex in self.commentPatternList:
                if regex.match(ele.nodeValue):
                    ele.removeNode(True)
        return False
    # end visitDocument()
# end class ZMshtmlRemoveCommentsVisitor

#-----------------------------------------------------
# Visitor for checking all <object> elements which have flash <embeds>
# but do not specify (for IE) Flash player via
# classid="clsid:D27CDB6E-AE6D-11cf-96B8-444553540000
# In this case, we simply uwrap the <object> elem to expose the <embed>.
#----------------------------------------------------
class ZMshtmlCheckFlashObjectElementVisitor(ZMshtmlIHtmlBodyDispatchElementVisitorBase):

    def __init__(self):
        pass
    # end __init__()

    def _visitBodyDispatchElement(self, mshtmlBodyElement):  #@UnusedVariable
        self.mshtmlBodyElement = mshtmlBodyElement
        eleList = self.mshtmlBodyElement.getElementsByTagName(u"OBJECT") #$NON-NLS-1$
        for ele in eleList:
            if getNoneString(ele.classid) is not None: #$NON-NLS-1$
                # Class ID already defined. Skip!
                continue
            # 1. Lookup <embed> child element
            # 2. If child <embed> element is application/x-shockwave-flash, then remove OBJECT elem wrapper
            # The problem is, IE does not parse <embed> as an element. Instead, it is represented as OBJECT nodes' text.
            # Work around is to do load the content into ZDOm and select embed elem.

            content = getNoneString(ele.outerHTML)
            if not content:
                continue
            xhtmlDoc = loadXhtmlDocumentFromString(content)
            dom = xhtmlDoc.getDom()
            embed = dom.selectSingleNode(u"//xhtml:embed") #$NON-NLS-1$ #$NON-NLS-1$
            if not embed:
                continue
            if embed.getAttribute(u"type") == u"application/x-shockwave-flash": #$NON-NLS-1$ #$NON-NLS-2$
                embedNode = self.mshtmlDoc.createElement(u"embed") #$NON-NLS-1$
                ele.insertAdjacentElement(u"AfterEnd",embedNode) #$NON-NLS-1$
                embedEle = getDispElement(embedNode)
                for attrNode in embed.getAttributes():
                    embedEle.setAttribute( attrNode.nodeName, attrNode.getText() )
                ele.parentNode.removeChild(ele)
                classes = getSafeString(ele.getAttribute(u"className")).split(u" ") #$NON-NLS-1$ #$NON-NLS-2$
                if not u"_Z_RAVEN_OBJECT_WRAPPER_" in classes: #$NON-NLS-1$
                    classes.append(u"_Z_RAVEN_OBJECT_WRAPPER_") #$NON-NLS-1$
                embedEle.setAttribute(u"className", u" ".join(classes).strip() ) #$NON-NLS-2$ #$NON-NLS-1$
        return False
    # end visitDocument()
# end class ZMshtmlCheckFlashObjectElementVisitor


#-----------------------------------------------------
# Visitor removing html comments based on regular expression matching
#----------------------------------------------------
class ZMshtmlMsOfficeCleanupVisitor(ZMshtmlIHtmlBodyDispatchElementVisitorBase):

    def _visitBodyDispatchElement(self, mshtmlBodyElement):  #@UnusedVariable
        # FIXME Need to impl. MS Office cleanup
        return False
    # end visitDocument()
# end class  ZMshtmlMsOfficeCleanupVisitor


# FIXME (PJ) move these comment2marker and marker2comment to
# zoundry/blogapp/ui/editors/blogeditorctrls/editcontrol.py
# (its very specific to ZMSHTMLBlogPostEditControl)

##-----------------------------------------------------
## Visitor for setting table element as unselectable
##----------------------------------------------------
class ZMshtmlSetUnSelectableOnVisitor(ZMshtmlIHtmlBodyDispatchElementVisitorBase):

    def _visitBodyDispatchElement(self, mshtmlBodyElement):
        self.mshtmlBodyElement = mshtmlBodyElement
        self._makeUnSelectable(u"TABLE") #$NON-NLS-1$
    # end _visitBodyDispatchElement

    def _makeUnSelectable(self, tagName):
        eleList = self.mshtmlBodyElement.getElementsByTagName(tagName)
        for ele in eleList:
            ele.setAttribute(u"UNSELECTABLE", u"on") #$NON-NLS-1$ #$NON-NLS-2$
    # end _makeUnSelectable
# end ZMshtmlSetUnSelectableOnVisitor

#-----------------------------------------------------
# Add table borders
#----------------------------------------------------
class ZMshtmlAddTableBordersVisitor(ZMshtmlIHtmlBodyDispatchElementVisitorBase):

    def _visitBodyDispatchElement(self, mshtmlBodyElement):
        eleList = mshtmlBodyElement.getElementsByTagName(u"TABLE") #$NON-NLS-1$
        for ele in eleList:
            table = getDispElement(ele)
            if not table.border or unicode(table.border).lower() in [u"0", u"0px", u"0em", u"0%"]: #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$ #$NON-NLS-4$
                self._setRuntimeBorder(table, u"#bcbcbc") #$NON-NLS-1$
                #table.runtimeStyle.borderCollapse = u"separate" #$NON-NLS-1$
                for tdEle in table.getElementsByTagName(u"TD"): #$NON-NLS-1$
                    self._setRuntimeBorder( getDispElement(tdEle), u"#bcbcbc" ) #$NON-NLS-1$
                for tdEle in table.getElementsByTagName(u"TH"): #$NON-NLS-1$
                    self._setRuntimeBorder( getDispElement(tdEle), u"#bcbcbc" ) #$NON-NLS-1$
            else:
                # remove rt style if table has border.
                self._removeRuntimeBorder(table) #$NON-NLS-1$
                for tdEle in table.getElementsByTagName(u"TD"): #$NON-NLS-1$
                    self._removeRuntimeBorder( getDispElement(tdEle)) #$NON-NLS-1$
                for tdEle in table.getElementsByTagName(u"TH"): #$NON-NLS-1$
                    self._removeRuntimeBorder( getDispElement(tdEle) ) #$NON-NLS-1$
    # end _visitBodyDispatchElement

    def _setRuntimeBorder(self, dispEle, color):
        dispEle.runtimeStyle.borderWidth = u"1px"; #$NON-NLS-1$
        dispEle.runtimeStyle.borderColor = color
        dispEle.runtimeStyle.borderStyle = u"dotted" #$NON-NLS-1$
    # end _setRuntimeBorder()

    def _removeRuntimeBorder(self, dispEle):
        dispEle.runtimeStyle.borderWidth = u""; #$NON-NLS-1$
        dispEle.runtimeStyle.borderColor = u""; #$NON-NLS-1$
        dispEle.runtimeStyle.borderStyle = u""; #$NON-NLS-1$
    # end _removeRuntimeBorder()

# end ZMshtmlAddTableBordersVisitor

#-----------------------------------------------------
# Visitor for converting "text more" comment to an internal marker.
#----------------------------------------------------
class ZMshtmlTextMoreComment2ExtEntryMarkerVisitor(ZMshtmlIHtmlBodyDispatchElementVisitorBase):

    TEXT_MORE_RE = re.compile( r'\s*more\s*', re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL) #$NON-NLS-1$

    def __init__(self, commentPatternList = []):
        self.commentPatternList = commentPatternList
    # end __init__()

    def _visitBodyDispatchElement(self, mshtmlBodyElement):  #@UnusedVariable
        self.mshtmlBodyElement = mshtmlBodyElement
        extendedEntryMarker = ZMshtmlExtendedEntryMarkerProxy()
        eleList = self.mshtmlBodyElement.getElementsByTagName(u"!") #$NON-NLS-1$
        for ele in eleList:
            if ZMshtmlTextMoreComment2ExtEntryMarkerVisitor.TEXT_MORE_RE.match(ele.nodeValue):
                extendedEntryMarker.replaceWithExtendedEntry(ele)
                break
        return False
    # end _visitBodyDispatchElement()
# end ZMshtmlTextMoreComment2ExtEntryMarkerVisitor()

# ------------------------------------------------------------------------------------
# This is a ZDom (not mshtml dom) visitor that converts element with special marker to
# a <!-- more --> comment.
# ------------------------------------------------------------------------------------
class ZMshtmlExtEntryMarker2CommentZDomVisitor(ZDomVisitor):


    def visitElement(self, element):
        id = element.getAttribute(u"id") #$NON-NLS-1$
        if id != ZMshtmlExtendedEntryMarkerProxy.EXTENDED_ENTRY_MARKER_ID:
            return
        document = element.ownerDocument
        comment = document.createComment(u"more")#$NON-NLS-1$
        element.parentNode.replaceChild(comment, element)
    # end visitElement()

# end ZMshtmlExtEntryMarker2CommentZDomVisitor

# ------------------------------------------------------------------------------------
# This is a ZDom (not mshtml dom) visitor removes empty elements.
# ------------------------------------------------------------------------------------
class ZMshtmlRemoveEmptyElementZDomVisitor(ZDomVisitor):

    def __init__(self, elementNameList):
        self.elementNameList = elementNameList
    # end __init__()

    def visitElement(self, element):
        if element.localName.lower() in self.elementNameList:
            element.normalize()
            if len(element.getChildren()) == 0:
                element.parentNode.removeChild(element)
    # end visitElement()

# end ZMshtmlRemoveEmptyElementZDomVisitor

# ------------------------------------------------------------------------------------
# This is a ZDom (not mshtml dom) visitor which wraps special <embeds> in a <object> element
# ------------------------------------------------------------------------------------
class ZMshtmlWrapEmbedElementZDomVisitor(ZDomVisitor):

    def __init__(self):
        pass
    # end __init__()

    def visitElement(self, element):
        if element.localName.lower() == u"embed": #$NON-NLS-1$
            classes = getSafeString(element.getAttribute(u"class")).split(u" ") #$NON-NLS-1$ #$NON-NLS-2$
            if not u"_Z_RAVEN_OBJECT_WRAPPER_" in classes: #$NON-NLS-1$
                return
            try:
                element.removeAttribute(u"class") #$NON-NLS-1$
                classes.remove( u"_Z_RAVEN_OBJECT_WRAPPER_" ) #$NON-NLS-1$
                objNode = element.ownerDocument.createElement(u"object") #$NON-NLS-1$
                objNode.setAttribute( u"width", element.getAttribute(u"width") ) #$NON-NLS-1$ #$NON-NLS-2$
                objNode.setAttribute( u"height", element.getAttribute(u"height") ) #$NON-NLS-1$ #$NON-NLS-2$
                paramNode = element.ownerDocument.createElement(u"param") #$NON-NLS-1$
                paramNode.setAttribute( u"name", u"movie" ) #$NON-NLS-1$ #$NON-NLS-2$
                paramNode.setAttribute( u"value", element.getAttribute(u"src") ) #$NON-NLS-1$ #$NON-NLS-2$
                objNode.appendChild(paramNode)
                paramNode = element.ownerDocument.createElement(u"param") #$NON-NLS-1$
                paramNode.setAttribute( u"name", u"wmode" ) #$NON-NLS-1$ #$NON-NLS-2$
                paramNode.setAttribute( u"value", element.getAttribute(u"wmode") ) #$NON-NLS-1$ #$NON-NLS-2$
                objNode.appendChild(paramNode)
                if classes:
                    objNode.setAttribute(u"class", u" ".join(classes).strip() ) #$NON-NLS-2$ #$NON-NLS-1$
                element.parentNode.replaceChild(objNode, element)
                objNode.appendChild(element)
            except:
                pass

    # end visitElement()

# end ZMshtmlWrapEmbedElementZDomVisitor

# ------------------------------------------------------------------------------------
# This is a ZDom (not mshtml dom) visitor removes the mshtml UNSELECTABLE=on attribute
# ------------------------------------------------------------------------------------
class ZMshtmlRemoveUnSelectableZDomVisitor(ZDomVisitor):

    def __init__(self):
        pass
    # end __init__()

    def visitElement(self, element):
        if getNoneString( element.getAttribute(u"unselectable")): #$NON-NLS-1$ #$NON-NLS-2$
            # Note: not getting to this point probably because Tidy may have removed 'unselectable' attr.
            element.removeAttribute(u"unselectable") #$NON-NLS-1$
    # end visitElement

# end ZMshtmlRemoveUnSelectableZDomVisitor
