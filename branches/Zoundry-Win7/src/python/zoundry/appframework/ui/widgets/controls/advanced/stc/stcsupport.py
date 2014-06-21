from zoundry.base.css.cssfont import ZCssFontSizes
from zoundry.appframework.services.validation.xhtmlvalidation import IZXhtmlSchemaVersion
from zoundry.appframework.constants import IZAppServiceIDs
from zoundry.appframework.global_services import getApplicationModel
from zoundry.base.css.csscolor import ZCssColor
import wx #@UnusedImport
from wx.stc import *
import re

#----------------------
# Returns current schema
#----------------------
def getXhtmlSchema():
    valService = getApplicationModel().getEngine().getService(IZAppServiceIDs.XHTML_VALIDATION_SERVICE_ID)
    schema = valService.getSchema(IZXhtmlSchemaVersion.XHTML_1_STRICT)
    return schema
# end getXhtmlSchema()

# todo: autocomplete does not work alchemist sample document at the root.
# todo: autocomplete - if br or hr, enter close tag
# todo: autocomplete - if close tag, append '>' char
# todo: autocomplete - does not work if caret is just before close '>' char
# todo: autocomplete - if showing attr name or values, insert space before value if needed. '<a*'

class ZStcAutoCompleteHandler:

    # Special value to indicate show dialog to all posts, custom colour dialog etc.
    ALL_POSTS_HREF = u"[All Posts]"#$NON-NLS-1$
    CUSTOM_COLORS = u"[More Colors]"#$NON-NLS-1$

    #-------------------
    # CSS attribute names
    #-------------------
    STYLE_ATTRS = [u"color", u"background", u"width", u"height", u"vertical-align"]   #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$  #$NON-NLS-4$ #$NON-NLS-5$
    FONT_ATTRS = [u'font-family', u'font-style', u'font-variant', u'font-weight', u'font-size', u'line-height' ]  #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$  #$NON-NLS-4$ #$NON-NLS-5$  #$NON-NLS-6$
    MARGIN_ATTRS = [u"margin", u"margin-top", u"margin-right", u"margin-bottom", u"margin-left"]  #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$  #$NON-NLS-4$ #$NON-NLS-5$
    PADD_ATTRS = [u"padding", u"padding-top", u"padding-right", u"padding-bottom", u"padding-left"]  #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$  #$NON-NLS-4$ #$NON-NLS-5$
    TEXT_ATTRS = [u"text-align", u"text-decoration", u"text-transform"]  #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$

    ALL_ATTR_NAMES = []
    ALL_ATTR_NAMES.extend(STYLE_ATTRS)
    ALL_ATTR_NAMES.extend(FONT_ATTRS)
    ALL_ATTR_NAMES.extend(MARGIN_ATTRS)
    ALL_ATTR_NAMES.extend(PADD_ATTRS)
    ALL_ATTR_NAMES.extend(TEXT_ATTRS)

    #-------------------
    # CSS attribute values
    #-------------------
    FONT_STYLES = [u"normal", u"italic", u"oblique"] #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$
    FONT_VARIANT = [ u"normal",  u"small-caps"]  #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$
    FONT_WEIGHT = [u"normal", u"bold", u"bolder", u"lighter"]  #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$ #$NON-NLS-4$
    TEXT_ALIGN = [u"left", u"right", u"center", u"justify"]  #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$ #$NON-NLS-4$
    TEXT_DECO = [u"none", u"underline", u"overline", u"line-through"]  #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$ #$NON-NLS-4$
    TEXT_TRANS = [u"none", u"capitalize", u"uppercase", u"lowercase"]  #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$ #$NON-NLS-4$
    V_ALIGN = [u"baseline", u"sub", u"super", u"top", u"text-top",   #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$  #$NON-NLS-4$ #$NON-NLS-5$
               u"middle", u"bottom ", u"text-bottom"]     #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$

    # attribute value look up map
    ATTR_VALUE_MAP = {}
    ATTR_VALUE_MAP[u"font-style"] = FONT_STYLES #$NON-NLS-1$
    ATTR_VALUE_MAP[u"font-variant"] = FONT_VARIANT #$NON-NLS-1$
    ATTR_VALUE_MAP[u"font-weight"] = FONT_WEIGHT #$NON-NLS-1$
    ATTR_VALUE_MAP[u"text-align"] = TEXT_ALIGN #$NON-NLS-1$
    ATTR_VALUE_MAP[u"text-decoration"] = TEXT_DECO #$NON-NLS-1$
    ATTR_VALUE_MAP[u"text-transform"] = TEXT_TRANS #$NON-NLS-1$
    ATTR_VALUE_MAP[u"vertical-align"] = V_ALIGN #$NON-NLS-1$

    #FONT_SIZE_ABS = [xx-small | x-small | small | medium | large | x-large | xx-large]

    # Regular expressions
    HREF_RE_PATTERN = r'(href\s*=\s*\")([^\s\"<]*?)(\")' #$NON-NLS-1$
    HREF_RE = re.compile(HREF_RE_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
    CLASS_RE_PATTERN = r'(class\s*=\s*\")([^\s\"<]*?)(\")' #$NON-NLS-1$
    CLASS_RE = re.compile(CLASS_RE_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
    SRC_RE_PATTERN = r'(src\s*=\s*\")([^\s\"<]*?)(\")' #$NON-NLS-1$
    SRC_RE = re.compile(SRC_RE_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
    TARGET_RE_PATTERN = r'(target\s*=\s*\")([^\s\"<]*?)(\")' #$NON-NLS-1$
    TARGET_RE = re.compile(TARGET_RE_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)

    def __init__(self):

        fontsEnum = wx.FontEnumerator()
        fontsEnum.EnumerateFacenames()
        self.fontNames = fontsEnum.GetFacenames()
        self.fontNames.sort()
        self.colorNames = ZCssColor.COLOR_NAMES.keys()
        self.cssFontSizeList = []
        self.cssFontSizeList.extend( ZCssFontSizes.CSS_SIZES )
    # end __init__()

    def _getHrefListFromHistory(self):
        rList = []
        # FIXME : populate list with recently added links
        return rList
    # end _getHrefListFromHistory()

    def _populateAttrValues(self, aLocator, aAttrRegularExpr, aList=[]):
        u"""Returns list of attribute values found in the document based on the given attribute regular expression. """  #$NON-NLS-1$
        text = aLocator.getStcControl().GetText()
        if text:
            matchList = aAttrRegularExpr.findall(text)
            for match in matchList:
                if len(match) == 3 and match[1] and len(match[1].strip()) > 0 and match[1].strip() not in aList:
                    aList.append(match[1].strip())
        return aList
    # end _populateAttrValues()

    def getHrefList(self, aLocator, absUrlOnly=False):
        u"""Returns list of href urls found in the document. """  #$NON-NLS-1$
        rList = self._getHrefListFromHistory()
        text = aLocator.getStcControl().GetText()
        if text:
            linkList = ZStcAutoCompleteHandler.HREF_RE.findall(text)
            for link in linkList:
                if len(link) == 3 and link[1] and len(link[1].strip()) > 0:
                    href = link[1].strip()
                    if href not in rList and (not absUrlOnly or (absUrlOnly and href.lower().startswith(u"http")) ): #$NON-NLS-1$
                        rList.append(href)
        return rList
     # end getHrefList()

    def getClassList(self, aLocator):
        u"""Returns list of class attribute values found in the document. """  #$NON-NLS-1$
        rList = []
        self._populateAttrValues(aLocator, ZStcAutoCompleteHandler.CLASS_RE, rList)
        return rList
    # end getClassList()

    def getSrcList(self, aLocator):
        u"""Returns list of src attribute values found in the document. """  #$NON-NLS-1$
        rList = []
        self._populateAttrValues(aLocator, ZStcAutoCompleteHandler.SRC_RE, rList)
        return rList
    # end getSrcList()

    def getTargetList(self, aLocator):
        u"""Returns list of target attribute values found in the document. """  #$NON-NLS-1$
        rList = []
        self._populateAttrValues(aLocator, ZStcAutoCompleteHandler.TARGET_RE, rList)
        return rList
    # end getTargetList()

    def getChildTagsFor(self, aParentTagName):
        u"""Returns list of valid element names given parent element name. """  #$NON-NLS-1$
        rList = []
        if aParentTagName:
            rList = getXhtmlSchema().getElementChildren(aParentTagName)
        else:
            rList = [u"a", u"p", u"div", u"img", u"span", u"br"] #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$  #$NON-NLS-4$ #$NON-NLS-5$  #$NON-NLS-6$
        return rList
    # end getChildTagsFor()

    def getAttrListFor(self, aTagName, bRequiredAttrsOnly=False):
        u"""Returns list of valid attribute names element name. """  #$NON-NLS-1$
        rList = []
        if aTagName:
            rList = getXhtmlSchema().getElementAttributes(aTagName, bRequiredAttrsOnly)
        return rList
    # end getAttrListFor

    def getAttrValuesFor(self, aTagName, aAttrName, aLocator): #@UnusedVariable
        u"""Returns list of known attribute values given element name and attribute name. (applies only to CSS styles) """  #$NON-NLS-1$
        rList = []
        if aAttrName and aAttrName.strip().lower() == u"style": #$NON-NLS-1$
            rList = ZStcAutoCompleteHandler.ALL_ATTR_NAMES
        elif aAttrName and aAttrName.strip().lower() == u"href": #$NON-NLS-1$
            #rList = [ZStcAutoCompleteHandler.ALL_POSTS_HREF]
            rList = []
            rList.extend(self.getHrefList(aLocator, False))
        elif aAttrName and aAttrName.strip().lower() == u"class": #$NON-NLS-1$
            rList = self.getClassList(aLocator)
        elif aAttrName and aAttrName.strip().lower() == u"src": #$NON-NLS-1$
            rList = self.getSrcList(aLocator)
        elif aAttrName and aAttrName.strip().lower() == u"target": #$NON-NLS-1$
            rList = self.getTargetList(aLocator)
        return rList
    # end getAttrValuesFor()

    def getStyleValuesFor(self, aTagName, aAttrName, aStyleName): #@UnusedVariable
        u"""Returns list of known CSS style attribute values given CSS style name."""  #$NON-NLS-1$
        rList = []
        aStyleName = aStyleName.strip().lower()
        if aStyleName == u"color" or aStyleName == u"background": #$NON-NLS-1$ #$NON-NLS-2$
            rList = [ZStcAutoCompleteHandler.CUSTOM_COLORS]
            rList.extend(self.colorNames)
        elif aStyleName == u"font-family": #$NON-NLS-1$
            rList = self.fontNames
        elif aStyleName == u"font-size": #$NON-NLS-1$
            rList.extend(self.cssFontSizeList)
        elif ZStcAutoCompleteHandler.ATTR_VALUE_MAP.has_key(aStyleName):
                rList = ZStcAutoCompleteHandler.ATTR_VALUE_MAP[aStyleName]
        return rList
    # end getStyleValuesFor()

    def isMixedType(self, aTagName):
        u"""Returns true if the tag is a mixed type based on xhtml schema.""" #$NON-NLS-1$
        return getXhtmlSchema().isMixedType(aTagName)
    # end isMixedType()

    def isEmptyTag(self, aTagName):
        u"""Returns true if the tag is an empty tag such as img and br.""" #$NON-NLS-1$
        return len(self.getChildTagsFor(aTagName)) == 0
    # end isEmptyTag()

    def getCallTip(self, aLocator):
        zLocatorInfo = aLocator.getLocationInfo() #@UnusedVariable
        rVal = None
        if zLocatorInfo.locationType == ZStcLocator.INSIDETAG and zLocatorInfo.tagName:
            # show call tip for tag name based on xsd document annotation
            rVal = getXhtmlSchema().getElementDocumentation(zLocatorInfo.tagName)
        return rVal
    # end getCallTip()

    def getAutocompleteList(self, aLocator):
        zLocatorInfo = aLocator.getLocationInfo()
        rList = []
        if zLocatorInfo.locationType == ZStcLocator.CLOSETAG and zLocatorInfo.matchedTag:
            # autoComplete mode = close
            rList.append(zLocatorInfo.matchedTag)
        elif zLocatorInfo.locationType == ZStcLocator.OPENTAG and zLocatorInfo.parentList and len(zLocatorInfo.parentList) > 0:
            (parentPos, parentTagName) = zLocatorInfo.parentList[0] #@UnusedVariable
            rList = self.getChildTagsFor(parentTagName)
        elif zLocatorInfo.locationType == ZStcLocator.INSIDETAG:
            rList = self.getAttrListFor(zLocatorInfo.tagName)
        elif zLocatorInfo.locationType == ZStcLocator.ATTRVALUE and zLocatorInfo.attributeName:
            rList = self.getAttrValuesFor(zLocatorInfo.tagName, zLocatorInfo.attributeName, aLocator)
        elif zLocatorInfo.locationType == ZStcLocator.SUBATTRNAME and zLocatorInfo.attributeName and zLocatorInfo.attributeName == u"style" and zLocatorInfo.subAttributeName: #$NON-NLS-1$
            rList = self.getStyleValuesFor(zLocatorInfo.tagName, zLocatorInfo.attributeName, zLocatorInfo.subAttributeName)
        else:
            pass
        return (rList, zLocatorInfo)
    # end getAutocompleteList()
#end ZStcAutoCompleteHandler


# --------------------------------------------------------------
# Locator results
# --------------------------------------------------------------
class ZStcLocatorInfo:

    def __init__(self, locationType, tagName, attributeName, subAttributeName, matchedTag, parentList):
        # type: e.g. UNKNOWN, OPENTAG, INSIDETAG etc.
        # locationType is UNKOWN, OPENTAG, CLOSETAG etc.;
        # tagName is name of element tag if type is not UNKNOWN;
        # attributeName is the attributeName for ATTRNAME, ATTRVALUE and ATTRSUBNAME;
        # subAttributeName is value of the sub attribute for type ATTRSUBNAME;
        # matchedTag is the matching closing tagName for CLOSETAG;
        # parentList is a list containing tuples (pos, tagName) of the parent heirarchy.
        # position of the parent tag.

        self.locationType = locationType
        self.tagName = tagName
        self.attributeName = attributeName
        self.subAttributeName = subAttributeName
        self.matchedTag = matchedTag
        self.parentList = parentList
    # end __init__()
# end ZStcLocatorInfo


# --------------------------------------------------------------
# Simple regular expression based "html tree" locator.
# (ideally we should try and access the html parse tree, if exposed, via Stc Edit control.)
#
# --------------------------------------------------------------
class ZStcLocator:
    u"Util class to help with location context information" #$NON-NLS-1$

    # current location information type
    UNKNOWN     = 0 # unknown location
    OPENTAG     = 1 # in start of tag e.g. < - display list of valid child tags
    CLOSETAG    = 2 # in close tag e.g. </ - display matching tag
    INSIDETAG   = 3 # inside a tag - display list of valid attr names
    ATTRVALUE   = 4 # in attribute value e.g. id="inside attr" - display list of attr values
    SUBATTRNAME = 5 # in a sub attribute e.g. 'font-name' in style="width:1px; font-name:helvetica"

    LOCTYPE_NAMES = [u"Unknown", u"Open", u"Close", u"Inside",  u"AttrValue", u"ShowStyleNames"] #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$  #$NON-NLS-4$ #$NON-NLS-5$  #$NON-NLS-6$

    def __init__(self, stcCtrl):
        self.stcCtrl = stcCtrl
    # end __init__()

    def getStcControl(self):
        return self.stcCtrl
    # end getStcControl()

    def getLocationInfo(self):
        u"""Returns location info tuple (locationType, tagName, attrName, subAttrName, matchTag, parentList)
        where locationType is UNKOWN, OPENTAG, CLOSETAG etc.;
        tagName is name of element tag if type is not UNKNOWN;
        attrName is the attributeName for ATTRNAME, ATTRVALUE and ATTRSUBNAME;
        subAttrName is value of the sub attribute for type ATTRSUBNAME;
        matchTag is the matching closing tagName for CLOSETAG;
        parentList is a list containing tuples (pos, tagName) of the parent heirarchy.
        """ #$NON-NLS-1$

        # curr position
        pos = self.stcCtrl.GetCurrentPos()

        # default return values
        locType = ZStcLocator.UNKNOWN
        tagName = None
        attrName = None
        subAttrName = None
        matchTag = None
        parentList = []
        if self.isPosValid(pos):
            parentList = self.findParentHierarchy(pos)
            tagName = self.findPrevTagword(pos)
            if self.isOpenTag(pos):
                locType = ZStcLocator.OPENTAG
            elif self.isCloseTag(pos):
                locType = ZStcLocator.CLOSETAG
                (p, matchTag) = self.matchOpenTag(pos) #@UnusedVariable
            elif tagName :
                # by default,assume inside tag if a tag name is found.
                locType = ZStcLocator.INSIDETAG

                # find attr name
                attrName = self.findPrevAttrWord(pos)

                # find attr quote position.
                qp = self.findPrevQuotePos(pos)
                if qp != -1:
                    # inside an attribute.
                    # get attribute name
                    attrName = self.findPrevAttrWord(qp)
                    if attrName:
                        locType = ZStcLocator.ATTRVALUE
                        subAttrName = self.findPrevStyleAttr(pos)
                        if subAttrName:
                            # inside style attribute value style name (e.g font-name:)
                            locType = ZStcLocator.SUBATTRNAME

        return ZStcLocatorInfo(locType, tagName, attrName, subAttrName, matchTag, parentList)
    # end getLocationInfo()

    def isPosValid(self, p):
        if p < 0 or p > self.stcCtrl.GetTextLength():
            return False
        else:
            return True
    # end isPosValid()

    def isOpenTag(self, p):
        rVal = False
        if self.isChar(p-1,u'<') and not self.isChar(p,u'/'): #$NON-NLS-1$ #$NON-NLS-2$
            rVal = True
        return rVal
    # end isOpenTag()

    def isCloseTag(self, p):
        rVal = False
        if (p-2) >=0 and self.isChar(p-2,u'<') and self.isChar(p-1,u'/'): #$NON-NLS-1$ #$NON-NLS-2$
            rVal = True
        return rVal
    # end isCloseTag()

    def findTagStartPos(self, p):
        # Traverses backwords from the current position until html start tag '<' is found.
        # Returns -1 if not found.
        rVal = -1
        if self.isChar(p,u'>') or self.isCloseTag(p): #$NON-NLS-1$
            p = p - 1

        while p >= 0:
            if self.isChar(p,u'>') or self.isCloseTag(p): #$NON-NLS-1$
                # found > or </ closures before open tag
                p = -1
                break
            elif self.isChar(p,u'<') : #$NON-NLS-1$
                rVal = p
                break
            p = p - 1
        if p < 0:
            p = -1
        return rVal
    # end findTagStartPos()

    def findPrevTagword(self, p):
        # Traverses backwords from the current position until html start tag '<tagName' is found.
        # Returns the 'tagName if found else returns None.

        rVal = None
        p =  self.findTagStartPos(p)
        max = self.stcCtrl.GetTextLength()
        if p != -1:
            maxwordlen = 15
            if p + maxwordlen < max:
                max = p + maxwordlen
            idx = p + 1
            while idx < max:
                if self.isChar(idx,u' ') or self.isChar(idx,u'=') : #$NON-NLS-1$ #$NON-NLS-2$
                    rVal = self.stcCtrl.GetTextRange(p+1,idx).strip()
                    break
                idx = idx + 1
        if rVal and len(rVal) > 0:
            return rVal
        else:
            return None
    # end findPrevTagword()

    def findPrevAttrWord(self, p):
        # cursor must be right of '='  not on the '=' char..
        if self.isChar(p,u'='): #$NON-NLS-1$
            return None
            #pass

        # attribute name e.g. 'attrName = ' if currently inside a html element tag.
        tagPos = self.findTagStartPos(p)
        if tagPos == -1:
            # Not inside a tag.
            return None
        rVal = None #@UnusedVariable
        idx = p
        # move back until '=' is found.
        while idx > tagPos:
            if not self.isChar(idx,u' ') and not self.isChar(idx,u'=') and not self.isChar(idx,u'"'): #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$
                # already at a word char i.e. in the middle of a attribute or tag name. Not allowed.
                idx = tagPos
                break
            if self.isChar(idx,u'='): #$NON-NLS-1$
                break
            idx = idx -1
        if idx == tagPos:
            # not found
            return None
        # idx is now at the '=' position.
        idx = idx - 1
        # move back until a non white space is found.
        while idx > tagPos:
            if not self.isChar(idx,u' '): #$NON-NLS-1$
                break
            idx = idx -1
        if idx == tagPos:
            # not found
            return None
        # save word end pos
        endPos = idx + 1
        idx = idx
        # move back until a non white space is found.
        while idx > tagPos:
            if self.isChar(idx,u' '): #$NON-NLS-1$
                break
            idx = idx -1
        if idx == tagPos:
            # not found
            return None
        startPos = idx + 1
        rVal = self.stcCtrl.GetTextRange(startPos,endPos)
        if rVal and len(rVal) > 0:
            return rVal
        else:
            return None
    # end findPrevAttrWord()

    def findPrevQuotePos(self, p):
        # finds the quote position.
        rVal = -1
        # work around when the curr pos is at the matching close quote.
        if self.isChar(p,u'"') and ( self.isChar(p-1,u' ') or self.isChar(p-1,u';')  or self.isChar(p-1,u':')): #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$ #$NON-NLS-4$
            p = p - 1
        tagPos = self.findTagStartPos(p)
        if tagPos == -1:
            return -1
        idx = p
        tagPos = tagPos + 1
        while idx > tagPos:
            if self.isChar(idx,u'"') and not self.isChar(idx-1,u'\\'): #$NON-NLS-1$ #$NON-NLS-2$
                rVal = idx
                break
            idx = idx -1
        if idx == tagPos:
            rVal = -1
        return rVal
    # end findPrevQuotePos()

    def findPrevStyleAttr(self, p):
        # returns the style attr name. Eg. style="width:1px;font-size:1em;color:#fff"
        # will return the attr name (width, font-size, color) left of the cursor.
        # Returns None if not found.

        # cursor must be right of ':' - not on the ':' char..
        if self.isChar(p,u':'): #$NON-NLS-1$
            return None

        qp = self.findPrevQuotePos(p)
        if qp == -1:
            # most likely not in a attr value (i.e not inside quotes)
            return None
        rVal = None    #@UnusedVariable
        idx = p
        while idx > qp:
            # find ':' (colon). Skip spaces.
            if self.isChar(idx,u':'): #$NON-NLS-1$
                break
            elif self.isChar(idx,u';'): #$NON-NLS-1$
                idx = qp;
                break
            else:
                idx = idx -1
        # not found.
        if idx == qp:
            return None

        # skip spaces before ':'.
        while idx > qp:
            if not self.isChar(idx, u' ') and not self.isChar(idx, u':'): #$NON-NLS-1$ #$NON-NLS-2$
                break
            else:
                idx = idx -1

        # not found.
        if idx == qp:
            return None

        endPos = idx
        # find start pos
        idx = idx - 1
        while idx > qp:
            if self.isChar(idx,u' ') or self.isChar(idx,u';'): #$NON-NLS-1$ #$NON-NLS-2$
                break
            else:
                idx = idx - 1
        startPos = idx + 1
        rVal = self.stcCtrl.GetTextRange(startPos,endPos + 1)
        if rVal and len(rVal) > 0:
            return rVal
        else:
            return None
    # end findPrevStyleAttr()

    def matchOpenTag(self, p):
        # find matching open tag postion given close tag position.
        # eg: <a href="">hello  <br/> <strong>blue</strong> world</a>
        # should return position of '<a' if cursor was at start of '</a>'.
        # This method return tuple (pos, matchingTagName) if found
        # else return (-1, None)

        # dangle count set to 1 to indicate current closed tag.
        #n = 1
        #while p > 0:
        # (t,p) = find tag(p).
        # if t == <t/>:
        #   continue
        # elif t ==  </t>:
        #   n = n + 1
        # elif t == <t>:
        #   n = n - 1
        # elif n == 0:
        #   break
        #if n == 0 and t:
        #  match found.
        if not self.isCloseTag(p):
            return (-1, None)
        count = -1
        tagword = None
        p1 = p
        while p1 >= 0 and count != 0:
            (p1,tagword, ttype) = self.findTag(p1 - 1)
            count = count + ttype
        if count == 0:
            return (p1, tagword)
        else:
            return (-1, None)
    # end matchOpenTag()

    def findParentTag(self, p):
        # Returns the tuple (pos, parentTagName) if found or (-1,None) other wise.

        # start of document? return root element.
        if p < 2:
            return (-1, None)
        count = 0
        tagword = None
        p1 = p
        while p1 >= 0 and count != 1:
            (p1,tagword, ttype) = self.findTag(p1 - 1)
            count = count + ttype
        if count == 1:
            return (p1, tagword)
        else:
            return (-1, None)
    # end findParentTag

    def findParentHierarchy(self, p):
        # Returns list containing a tuples of the parent tag hierarchy.
        # The list takes the form [(deepest parent tuple), ..., (root tuple)]
        # where each tuple is (pos,tagName). The pos is -1 if not found.

        rList = []
        (p,tag) = self.findParentTag(p)
        while p >= 0:
            rList.append( (p,tag) )
            if p == 0:
                break
            (p,tag) = self.findParentTag(p + 1)
        # add root
        rList.append( (0,u"body") ) #$NON-NLS-1$
        return rList
    # end findParentHierarchy()

    def findTag(self,p):
        # search until contents of < > are found.
        # return tuple(pos,tagword, type) where type is +1 for <tag>, -1 for </tag>, and 0 for <tag/>

        # todo: handle html comment <!-- and -->
        p2 = self.findPrevCharPos(p,u'>') #$NON-NLS-1$
        p1 = self.findPrevCharPos(p2,u'<') #$NON-NLS-1$
        if p1 == p2 or p1 == -1 or p2 == -1:
            return (-1, None, 0)
        tag = self.stcCtrl.GetTextRange(p1,p2 + 1)
        t = 1 # t =1 for open tag, t = 0 for self contained tags (<br/>), and -1 for close tags.
        startpos = p1 + 1
        if len(tag) > 2:
            if tag.startswith(u"</"): #$NON-NLS-1$
                t = -1
                startpos = p1 + 2
            elif tag.endswith(u"/>"): #$NON-NLS-1$
                t = 0
            elif tag.startswith(u"<!--") and tag.endswith(u"-->"): #$NON-NLS-1$ #$NON-NLS-2$
                t = 0
        endpos = startpos
        while endpos < p2 and not self.isChar(endpos,u' ') and not self.isChar(endpos,u'>') and not self.isChar(endpos,u'/'): #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$
            endpos = endpos + 1
        tag = self.stcCtrl.GetTextRange(startpos, endpos)
        return (p1, tag, t)
    # end findTag()

    def findPrevCharPos(self,p,c):
        while p >= 0 and self.stcCtrl.GetCharAt(p) != ord(c):
            p = p - 1
        return p
    # end findPrevCharPos()

    def isChar(self, p, c):
        return self.stcCtrl.GetCharAt(p) == ord(c)
    # end isChar()
# end ZStcLocator
