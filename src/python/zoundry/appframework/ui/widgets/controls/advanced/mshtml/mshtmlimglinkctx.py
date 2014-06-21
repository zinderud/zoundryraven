from zoundry.appframework.constants import IZAppServiceIDs
from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.services.imaging.imaging import ZThumbnailParams
from zoundry.appframework.ui.widgets.controls.advanced.htmleditcontrol import IZXHTMLEditControlImageContext
from zoundry.appframework.ui.widgets.controls.advanced.htmleditcontrol import IZXHTMLEditControlLinkContext
from zoundry.appframework.ui.widgets.controls.advanced.mshtml.mshtmluiproxies import ZMshtmlExtendedEntryMarkerProxy
from zoundry.base.css.cssparse import parseCssBorderProperty
from zoundry.base.css.cssparse import parseCssRectangleProperty
from zoundry.base.util.text.textutil import getNoneString
from zoundry.base.util.urlutil import decodeUri
from zoundry.base.util.urlutil import encodeUri
from zoundry.base.util.urlutil import unquote
from zoundry.base.xhtml.xhtmldocutil import createHtmlElement
import re

# ------------------------------------------------------------------------------
# link edit contexts
# ------------------------------------------------------------------------------
class ZMshtmlEditControlLinkContext(IZXHTMLEditControlLinkContext):

    def __init__(self, mshtmlEditControl):
        self.mshtmlEditControl = mshtmlEditControl
    # end __init__()

    def canCreateLink(self):
        selectedText = self.mshtmlEditControl._getMshtmlControl().getSelectedText()
        if getNoneString(selectedText) is not None:
            return True
        mshtmlElem = self.mshtmlEditControl._getMshtmlControl().getSelectedElement()
        # allow linking of images
        if mshtmlElem is not None and mshtmlElem.tagName == u"IMG": #$NON-NLS-1$
            return True
        return False
    # end canCreateLink

    def canEditLink(self):
        return self._getLinkElement() is not None
    # end canEditLink

    def canRemoveLink(self):
        # if current selection is an image
        return self.canEditLink()
    # end canRemoveLink

    def removeLink(self):
        if not self.canRemoveLink():
            return
        linkEle = self._getLinkElement()
        try:
            linkEle.outerHTML = linkEle.innerHTML
            self.mshtmlEditControl._getMshtmlControl()._fireContentModified()
        except:
            pass
    # end canRemoveLink

    def getLinkAttributes(self):
        linkEle = self._getLinkElement()
        attrMap = None
        if linkEle:
            attrMap = {}
            attrNames = [u"className", u"href", u"target", u"rel", u"title"] #$NON-NLS-4$ #$NON-NLS-3$ #$NON-NLS-2$ #$NON-NLS-1$ #$NON-NLS-5$
            for attrName in attrNames:
                value = linkEle.getAttribute(attrName)
                if value:
                    # IE sometimes prefixes 'about:blank'.
                    if value.startswith(u"about:blank"): #$NON-NLS-1$
                        value = value[11:]
                    if attrName == u"className": #$NON-NLS-1$
                        attrName = u"class" #$NON-NLS-1$
                    attrMap[attrName] = value
            if linkEle.innerText:
                attrMap[u"text"] = linkEle.innerText  #$NON-NLS-1$
            if attrMap.has_key(u"href"): #$NON-NLS-1$
                attrMap[u"href"] = decodeUri(attrMap[u"href"]) #$NON-NLS-1$ #$NON-NLS-2$
                # if protocol is file://, then convert to a normal path.
                # FIXME (PJ) move this code to ZLinkModel.
        return attrMap
    # end getLinkAttributes

    def setLinkAttributes(self, attrMap): #@UnusedVariable
        if not attrMap:
            return
        attrMapCopy = attrMap.copy()
        if attrMapCopy.has_key(u"href"): #$NON-NLS-1$
            attrMap[u"href"] = encodeUri(attrMap[u"href"]) #$NON-NLS-1$ #$NON-NLS-2$
#            # url encode and add proper file:// (if local file).
#            # FIXME (PJ) move this code to ZLinkModel.
        linkEle = self._getLinkElement()
        if linkEle:
            self._updateLink(linkEle, attrMapCopy)
        else:
            self._createLink(attrMapCopy)

        # run img visitor to set img runtime border = 0 
        self.mshtmlEditControl._getMshtmlControl()._runImgCleanupVisitor()
        self.mshtmlEditControl._getMshtmlControl()._fireContentModified()
    # end setLinkAttributes

    def _createLink(self, attrMap):
        attrs = attrMap.copy()
        linkText = None
        if attrs.has_key(u"text"): #$NON-NLS-1$
            linkText = getNoneString(attrs[u"text"]) #$NON-NLS-1$
            del attrs[u"text"] #$NON-NLS-1$

        selectedElem = self.mshtmlEditControl._getMshtmlControl().getSelectedElement()
        replaceTextPattern = u"${_zraven_link_child_nodes_}$" #$NON-NLS-1$
        if selectedElem:
            textRange = self.mshtmlEditControl._getMshtmlControl().getSelectedTextRange()
            linkNode = createHtmlElement(None, u"a", attrs, replaceTextPattern) #$NON-NLS-1$
            linkNodeHtml = linkNode.serialize()

            if textRange:
                if linkText and linkText != textRange.text:
                    # replace link text
                    if textRange.htmlText == textRange.text:
                        # simple text selection
                        newText = linkNodeHtml.replace(replaceTextPattern, linkText)
                        textRange.pasteHTML(newText)
                    else:
                        # has html (img) + text. replace only the text.
                        s = textRange.htmlText
                        # replace the current text with the new link text
                        s = s.replace(textRange.text, linkText)
                        # wrap in <a>
                        newText = linkNodeHtml.replace(replaceTextPattern, s)
                else:
                    if textRange.htmlText and selectedElem.outerHTML == textRange.htmlText:
                        newText = linkNodeHtml.replace(replaceTextPattern, selectedElem.innerHTML)
                        selectedElem.innerHTML = newText
                    elif textRange.htmlText and selectedElem.innerHTML == textRange.htmlText:
                        newText = linkNodeHtml.replace(replaceTextPattern, selectedElem.innerHTML)
                        selectedElem.innerHTML = newText
                    elif textRange.htmlText:
                        newText = linkNodeHtml.replace(replaceTextPattern, textRange.htmlText)
                        textRange.pasteHTML(newText)
                    else:
                        newText = linkNodeHtml.replace(replaceTextPattern, selectedElem.innerHTML)
                        selectedElem.innerHTML = newText
            else:
                if linkText:
                    selectedElem.innerText = linkText
                newHtml = linkNodeHtml.replace(replaceTextPattern, selectedElem.outerHTML)
                selectedElem.outerHTML = newHtml
        else:
            # if text is not provided, then use the link location as the text.
            if not linkText:
                linkText = unquote(attrs[u"href"]) #$NON-NLS-1$
            linkNode = createHtmlElement(None,u"a",attrs, linkText) #$NON-NLS-1$
            linkNodeHtml = linkNode.serialize()
            self.mshtmlEditControl._getMshtmlControl().insertHtml(linkNodeHtml)
    # end _createLink

    def _updateLink(self, linkEle, attrMap):
        if attrMap.has_key(u"href"): #$NON-NLS-1$
            linkEle.setAttribute(u"href", attrMap[u"href"]) #$NON-NLS-1$ #$NON-NLS-2$
        self._updateAttribute(linkEle, attrMap, u"class", u"className")#$NON-NLS-1$ #$NON-NLS-2$
        self._updateAttribute(linkEle, attrMap, u"title", u"title")#$NON-NLS-1$ #$NON-NLS-2$
        self._updateAttribute(linkEle, attrMap, u"rel", u"rel")#$NON-NLS-1$ #$NON-NLS-2$
        self._updateAttribute(linkEle, attrMap, u"target", u"target")#$NON-NLS-1$ #$NON-NLS-2$


    def _updateAttribute(self, linkEle, attrMap, attrName, mshtmlAttrName):
        if self._shouldSetAttribute(linkEle, attrMap, attrName, mshtmlAttrName):
            linkEle.setAttribute(mshtmlAttrName, attrMap[attrName])
        elif self._shouldRemoveAttribute(linkEle, attrMap, attrName, mshtmlAttrName):
            linkEle.removeAttribute(mshtmlAttrName)

    def _shouldSetAttribute(self, linkEle, attrMap, attrName, mshtmlAttrName): #@UnusedVariable
        if attrMap.has_key(attrName) and attrMap[attrName] is not None and attrMap[attrName] != u"":#$NON-NLS-1$
            return True
        else:
            return False
    # end _shouldSetAttribute()

    def _shouldRemoveAttribute(self, linkEle, attrMap, attrName, mshtmlAttrName):
        if attrMap.has_key(attrName) and attrMap[attrName] is None and linkEle.getAttribute(mshtmlAttrName) != u"": #$NON-NLS-1$
            return True
        else:
            return False
    # end _shouldRemoveAttribute()

    def _getLinkElement(self):
        # Returns link element under the caret/cursor or None if there is no link.
        linkEle = None
        mshtmlElem = self.mshtmlEditControl._getMshtmlControl().getSelectedElement(True)
        if mshtmlElem is not None:
            while linkEle is None and mshtmlElem.tagName != u"BODY": #$NON-NLS-1$
                if mshtmlElem.tagName == u"A": #$NON-NLS-1$
                    linkEle = mshtmlElem
                else:
                    mshtmlElem = mshtmlElem.parentElement
        return linkEle
    # end _getLinkElement()
# end ZMshtmlEditControlLinkContext

# ------------------------------------------------------------------------------
# image edit contexts
# ------------------------------------------------------------------------------
class ZMshtmlEditControlImageContext(IZXHTMLEditControlImageContext):

    TN_PATTERN = r"^(file:\/\/)(.*)(\/thumbnails\/)([a-f0-9]+_tn\.png)$" #$NON-NLS-1$
    TN_RE = re.compile(TN_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)

    def __init__(self, mshtmlEditControl):
        self.mshtmlEditControl = mshtmlEditControl
    # end __init__()

    def _getImageElement(self):
        mshtmlElem = self.mshtmlEditControl._getMshtmlControl().getSelectedElement()
        if mshtmlElem is not None and mshtmlElem.tagName == u"IMG": #$NON-NLS-1$
            # also check for placeholder image that is used as an extend entry marker.
            if mshtmlElem.getAttribute(u"id") != ZMshtmlExtendedEntryMarkerProxy.EXTENDED_ENTRY_MARKER_ID: #$NON-NLS-1$
                return mshtmlElem
        return None
    # end _getImageElement

    def canCreateImage(self):
        return self._getImageElement() is None
    # end canCreateImage

    def canEditImage(self):
        return self._getImageElement() is not None
    # end canEditLink

    def isThumbnail(self):
        imageEle = self._getImageElement()
        return self._checkIfThumbnail(imageEle)
    # end isThumbnail

    def _checkIfThumbnail(self, imageEle):
        if imageEle:
            # temp code: matches  file:// image ending with _tn.png.
            return ZMshtmlEditControlImageContext.TN_RE.match( imageEle.getAttribute(u"src") ) is not None  #$NON-NLS-1$
        else:
            return False
    # end _checkIfThumbnail

    def canCreateThumbnail(self):
        imageEle = self._getImageElement()
        # FIXME (PJ) : logic: can create TN: if image is local image and not already thumbnailed. Use special z:tn attribute to determine if image is a thumbnail.
        return imageEle is not None and not self._checkIfThumbnail(imageEle) and imageEle.getAttribute(u"src").startswith(u"file://") #$NON-NLS-1$ #$NON-NLS-2$
    # end canCreateThumbnail

    def createThumbnail(self, width, height, options = {}): #@UnusedVariable
        if not self.canCreateThumbnail() or (width < 10 and height < 10):
            return False
        imageEle = self._getImageElement()
        # get src. Assume local image. (TODO: support remote images.)
        srcFile = imageEle.getAttribute(u"src") #$NON-NLS-1$
        if not srcFile:
            return False
        try:
            tnService = getApplicationModel().getService(IZAppServiceIDs.IMAGING_SERVICE_ID)
            tnParams = ZThumbnailParams(width, height)
            (tn_name, tn_width, tn_height) = tnService.generateThumbnail( decodeUri(srcFile) , tnParams)
            # encode uri
            tn_name = encodeUri(tn_name)
            if imageEle.parentElement is not None and imageEle.parentElement.tagName == u"A": #$NON-NLS-1$
                # current image is already linked, so just update the src and width/height.
                self._setImageAttribute(imageEle, u"width", unicode(tn_width)) #$NON-NLS-1$
                self._setImageAttribute(imageEle, u"height", unicode(tn_height)) #$NON-NLS-1$
                imageEle.setAttribute(u"src", tn_name) #$NON-NLS-1$
            else:
                # generate html for the tn as well as a link to the large image
                # transfer the CSS from current image to the TN image
                self._setImageAttribute(imageEle, u"width", unicode(tn_width)) #$NON-NLS-1$
                self._setImageAttribute(imageEle, u"height", unicode(tn_height)) #$NON-NLS-1$
                css = self._getImageStyle(imageEle)
                if not css:
                    css = u"" #$NON-NLS-1$
                html = u"""<a href="%s"><img src="%s" width="%s" height="%s" style="%s"/></a>""" % (srcFile, tn_name, tn_width, tn_height, css)  #$NON-NLS-1$
                imageEle.outerHTML = html
            self._runCleanupAndFireModified()
        except:
            return False
    # end createThumbnail


    def getImageAttributes(self):
        attrMap = None
        imageEle = self._getImageElement()
        if imageEle:
            attrMap = {}
            # get all, but css style attrs.
            attrNames = u"id,src,alt,title,className,width,height,align,border,margin".split(u",") #$NON-NLS-1$ #$NON-NLS-2$
            for attrName in attrNames:
                value = self._getImageAttribute(imageEle, attrName)
                if value and attrName == u"className": #$NON-NLS-1$
                    attrMap[u"class"] = value                 #$NON-NLS-1$
                elif value:
                    attrMap[attrName] = value
            # get css style.
            css = self._getImageStyle(imageEle)
            if css:
                attrMap[u"style"] = css #$NON-NLS-1$
            # FIXME (PJ) move this to zeditimagemodel
            if attrMap.has_key(u"src"): #$NON-NLS-1$
                attrMap[u"src"] = decodeUri(attrMap[u"src"]) #$NON-NLS-1$ #$NON-NLS-2$
        return attrMap
    # end getImageAttributes

    def setImageAttributes(self, attrMap):
        imageEle = self._getImageElement()
        return self._insertOrUpdateImage(attrMap, imageEle)
    # end setImageAttributes

    def _insertOrUpdateImage(self, attrMap, imageEle):
        if not attrMap:
            return False
        attrMapCopy = attrMap.copy()
#        if attrMapCopy.has_key(u"src"): #$NON-NLS-1$
#            # FIXME (PJ) move this code to ZImageModel.
#            attrMapCopy[u"src"] = encodeUri(attrMapCopy[u"src"]) #$NON-NLS-1$ #$NON-NLS-2$
        rval = False
        if imageEle:
            rval = self._updateImage(imageEle, attrMapCopy)
        elif attrMapCopy.has_key(u"src"): #$NON-NLS-1$
            rval = self._createImage(attrMapCopy)
        if rval:
            self._runCleanupAndFireModified()
        return rval
    # end _insertOrUpdateImage()
    
    def _runCleanupAndFireModified(self):
        self.mshtmlEditControl._getMshtmlControl()._runImgCleanupVisitor()            
        self.mshtmlEditControl._getMshtmlControl()._fireContentModified()
    # end _runCleanupAndFireModified

    def insertImage(self, attrMap):
        return self._insertOrUpdateImage(attrMap, None)
    # end insertImage

    def _updateImage(self, imageEle, attrMap):
        for (attrName,attrVal) in attrMap.iteritems():
            attrName = attrName.lower()
            if attrName == u"style": #$NON-NLS-1$
                self._setImageStyle(imageEle, attrVal)
            elif attrName == u"class": #$NON-NLS-1$
                self._setImageAttribute(imageEle, u"className", attrVal)    #$NON-NLS-1$
            else:
                self._setImageAttribute(imageEle, attrName, attrVal)        
        return True
    # end _updateImage

    def _createImage(self, attrMap):
        if not attrMap.has_key(u"src"): #$NON-NLS-1$
            return
        src = attrMap[u"src"] #$NON-NLS-1$
        self.mshtmlEditControl._getMshtmlControl().insertImage(src)
        imageEle = self._getImageElement()
        if imageEle:
            self._updateImage(imageEle, attrMap)
            return True
        else:
            return False
    # end _createImage()

    def _getImageAttribute(self, imageEle, attrName):
        rval = imageEle.getAttribute(attrName)
        if attrName == u"width" and not rval: #$NON-NLS-1$  #$NON-NLS-2$
            rval = imageEle.style.width
        elif attrName == u"height" and not rval: #$NON-NLS-1$  #$NON-NLS-2$
            rval = imageEle.style.height
        elif attrName == u"border": #$NON-NLS-1$
            rval = self._parseBorder(imageEle)
        elif attrName == u"margin": #$NON-NLS-1$
            rval = self._parseMargin(imageEle)
        elif attrName == u"align": #$NON-NLS-1$
            supportedAlign = [u"left", u"right", u"center"]  #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$
            if not rval or not rval.lower() in supportedAlign: #$NON-NLS-1$  #$NON-NLS-2$ #$NON-NLS-3$
                rval = imageEle.style.styleFloat
            if not rval: #$NON-NLS-1$  #$NON-NLS-2$
                rval = imageEle.style.textAlign
            if rval and not rval.lower() in supportedAlign : #$NON-NLS-1$  #$NON-NLS-2$ #$NON-NLS-3$
                rval = None
        return rval
    # end _getImageAttribute()

    def _setImageAttribute(self, imageEle, attrName, attrValue):
        if attrName == u"align" and attrValue:  #$NON-NLS-1$
            # handle CSS align
            imageEle.removeAttribute(attrName) # remove non CSS align attribute
            imageEle.style.styleFloat = u"" #$NON-NLS-1$
            imageEle.style.textAlign = u""  #$NON-NLS-1$
            imageEle.style.display = u"inline" #$NON-NLS-1$
            if attrValue == u"left" or attrValue == u"right":  #$NON-NLS-1$  #$NON-NLS-2$
                imageEle.style.styleFloat = attrValue
            elif attrValue == u"center":  #$NON-NLS-1$
                imageEle.style.textAlign = u"center"  #$NON-NLS-1$
                imageEle.style.display = u"block" #$NON-NLS-1$
                imageEle.style.marginLeft = u"auto" #$NON-NLS-1$
                imageEle.style.marginRight = u"auto" #$NON-NLS-1$
        elif attrName == u"width" and attrValue: #$NON-NLS-1$
            imageEle.setAttribute(u"width", attrValue) #$NON-NLS-1$
            imageEle.style.width = attrValue
        elif attrName == u"height" and attrValue: #$NON-NLS-1$
            imageEle.setAttribute(u"height", attrValue) #$NON-NLS-1$
            imageEle.style.height = attrValue
        elif attrName == u"border": #$NON-NLS-1$
            if attrValue is not None:
                imageEle.style.border = attrValue
            else:
                imageEle.style.borderStyle = u"" #$NON-NLS-1$
                imageEle.style.borderColor = u"" #$NON-NLS-1$
                imageEle.style.borderWidth = u"" #$NON-NLS-1$
        elif attrName == u"margin": #$NON-NLS-1$
            if attrValue is not None:
                imageEle.style.margin = attrValue
            else:
                imageEle.style.margin = u"" #$NON-NLS-1$
        elif attrValue:
            imageEle.setAttribute(attrName, attrValue, 0)
    # end _setImageAttribute()

    def _getImageStyle(self, imageEle):
        rval = None
        styleObj = imageEle.getAttribute(u"style") #$NON-NLS-1$
        if styleObj is not None:
            try:
                rval = styleObj.cssText
            except:
                pass
        return rval
    # end _getImageStyle()

    def _setImageStyle(self, imageEle, cssStyle):
        styleObj = imageEle.getAttribute(u"style") #$NON-NLS-1$
        if styleObj is not None and cssStyle:
            try:
                styleObj.cssText = cssStyle
            except:
                pass
    # end _setImageStyle()

    def _parseBorder(self, imageEle):
        # return: "length style color". Eg "1px dotted #FFDDAA".
        cssStr = None
        cssAttrs = self._getStyleMap(imageEle)
        keys = u"border,border-left,border-right,border-top,border-bottom" #$NON-NLS-1$
        for key in keys.split(u","): #$NON-NLS-1$
            if cssAttrs.has_key(key) and getNoneString(cssAttrs[key]) is not None:
                cssStr = cssAttrs[key]
                break
        if cssStr:
            (width, style, cssColor) = parseCssBorderProperty(cssStr)
            hexColor = u"" #$NON-NLS-1$
            if cssColor:
                hexColor = cssColor.getCssColor()
            return u"%s %s %s" %(width, style, hexColor) #$NON-NLS-1$
        return None
    # _parseBorder()

    def _parseMargin(self, imageEle):
        # return "top right bottom left"
        cssAttrs = self._getStyleMap(imageEle)
        if cssAttrs.has_key(u"margin") and getNoneString(cssAttrs[u"margin"]) is not None: #$NON-NLS-1$ #$NON-NLS-2$
            (t, r, b, l) = parseCssRectangleProperty(cssAttrs[u"margin"]) #$NON-NLS-1$
            return u"%s %s %s %s" % (t, r, b, l) #$NON-NLS-1$
        return None
    # _parseMargin()

    def _getStyleMap(self, imageEle):
        rval = {}
        cssText = self._getImageStyle(imageEle)
        if cssText:
            for entry in cssText.split(u";"): #$NON-NLS-1$
                (n,v) = entry.split(u":")#$NON-NLS-1$
                rval[n.strip().lower()]= v.strip()
        return rval
    # _getStyleMap()
# end ZMshtmlEditControlImageContext