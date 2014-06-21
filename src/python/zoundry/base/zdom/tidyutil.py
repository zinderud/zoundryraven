import re
from zoundry.base.util.text.unicodeutil import convertToUnicode
from zoundry.base.util.text.unicodeutil import convertToUtf8
from zoundry.base.xhtml.xhtmlutil import hasBody

#==============================================================
# HTML Tidy ref: http://tidy.sourceforge.net/docs/Overview.html
#                http://tidy.sourceforge.net/docs/quickref.html
# -------------------------------------------------------------
#
# U_TIDY:
# uTidy ref    : http://developer.berlios.de/projects/utidylib
#              : http://utidylib.berlios.de/apidoc0.2/index.html
#
# download uTidy  : http://utidylib.berlios.de/
# download Ctypes : http://starship.python.net/crew/theller/ctypes/#
# (CTypes 0.9.0 win32 for Py2.3is required for by UTidy)
#
# --------------------------------------------------------------
# MX_TIDY
# mxTidy ref   : http://www.egenix.com/files/python/mxTidy.html
#
#================================================================

ILLEGAL_ENTITY_PATTERN = r'(&+)(#\W+|[\\\^\$\.\|\?\*\+\(\)\{\}!@%,=/<>";])' #$NON-NLS-1$
ILLEGAL_ENTITY_RE = re.compile(ILLEGAL_ENTITY_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)

MSWORD_BLOCKS = "o:p,dt,dd,v:shape"
MSWORD_INLINE = "st1:date,st1:city,st1:country-region,st1:place,st1:time," \
              "o:smarttagtype,st1:placename,st1:placetype,st1:street,st1:address," \
              "st1:state,st2:place,st2:placename,st2:placetype,st2:city,st2:street," \
              "st2:address,st2:time,st2:state,st2:country-region,quote"

SOURCE_OPTIONS = dict(output_xhtml=1, add_xml_decl=0, add_xml_space=0, quiet=1, char_encoding="utf8", \
                     output_error=0, show_warnings=0, quote_nbsp=1, raw=1, indent="yes", show_body_only=1, \
                     quote_ampersand=1, quote_marks=1, logical_emphasis=1, hide_comments=0, wrap=140, \
                     word_2000=1, break_before_br=1, clean=0, indent_spaces=3, tab_size=1, drop_empty_paras=1, \
                     enclose_block_text=1, lower_literals=1, bare=1,drop_proprietary_attributes=1,
                     new_inline_tags = MSWORD_INLINE, new_blocklevel_tags = MSWORD_BLOCKS)

PREVIEW_OPTIONS = dict(output_xhtml=1, add_xml_decl=0, add_xml_space=0, quiet=1, char_encoding="utf8", \
                     output_error=0, show_warnings=0, quote_nbsp=1, raw=1, indent="no", show_body_only=0, \
                     quote_ampersand=1, quote_marks=1, logical_emphasis=1, hide_comments=0, wrap=140, \
                     word_2000=1, break_before_br=1, clean=0, indent_spaces=0, tab_size=2, drop_empty_paras=1, \
                     enclose_block_text=1, lower_literals=1, bare=1, drop_proprietary_attributes=1,
                     new_inline_tags = MSWORD_INLINE,  new_blocklevel_tags = MSWORD_BLOCKS)

PREVIEW_OPTIONS_NOBODY = dict(output_xhtml=1, add_xml_decl=0, add_xml_space=0, quiet=1, char_encoding="utf8", \
                     output_error=0, show_warnings=0, quote_nbsp=1, raw=1, indent="no", show_body_only=1, \
                     quote_ampersand=1, quote_marks=1, logical_emphasis=1, hide_comments=0, wrap=140, \
                     word_2000=1, break_before_br=1, clean=0, indent_spaces=0, tab_size=2, drop_empty_paras=1, \
                     enclose_block_text=1, lower_literals=1, bare=1, drop_proprietary_attributes=1,
                     new_inline_tags = MSWORD_INLINE, new_blocklevel_tags = MSWORD_BLOCKS)

EDITING_OPTIONS = dict(output_xhtml=1, add_xml_decl=0, add_xml_space=1, quiet=1, char_encoding="utf8", \
                     output_error=0, show_warnings=0, quote_nbsp=1, raw=1, indent="no", show_body_only=0, \
                     quote_ampersand=1, quote_marks=1, logical_emphasis=1, hide_comments=0, wrap=0, \
                     word_2000=1, break_before_br=1, clean=0,  drop_empty_paras=1, fix_bad_comments=1, \
                     enclose_block_text=1, lower_literals=1, bare=1, drop_proprietary_attributes=1,
                     new_inline_tags = MSWORD_INLINE, new_blocklevel_tags = MSWORD_BLOCKS)

XHTML_OPTIONS    = dict(output_xml=1, add_xml_decl=1, add_xml_space=1, quiet=1, char_encoding="utf8", \
                        output_error=0, show_warnings=0, quote_nbsp=0, raw=1)


# --------------
# BEGIN MX_TIDY
# --------------
#from mx.Tidy import tidy
#def tidyHtml(htmlSrc, options = XHTML_OPTIONS):
#    """mxTidy - Cleans up the html source. Exceptions are thrown back to the calling code. """
#    try:
#        htmlSrc = convertToUtf8(htmlSrc)
#        (_x, _y, output, errors) = tidy(htmlSrc, **options)
#        print "Tidy x=", _x, "y=", _y, "e=", errors
#        if errors:
#            raise ZException(unicode(errors))
#        else:
#            return convertToUnicode(output)
#    except:
#        raise
## end tidyHtml

# ---- END MX_TIDY ----

# --------------
# BEGIN U_TIDY
# ------------

import tidy

# ----------------------------------------------------------------------------
# Global list of custom (non-xhtml) tags - built dynamically as they occur
# ----------------------------------------------------------------------------
# inline custom tags eg: <ttag>blag</ttag>
TIDY_CUSTOM_INLINE_TAG_LIST = []
TIDY_CUSTOM_INLINE_TAG_LIST = MSWORD_INLINE.split(u",") #$NON-NLS-1$  # seed list with known MS Office/word tags
# custom empty tags eg: <ttag />
TIDY_CUSTOM_EMPTY_TAG_LIST = []
# custom block level tag list
TIDY_CUSTOM_BLOCK_TAG_LIST = []
TIDY_CUSTOM_BLOCK_TAG_LIST = MSWORD_BLOCKS.split(u",") #$NON-NLS-1$  # seed list with known MS Office/word tags
# pre tags
TIDY_CUSTOM_PRE_TAG_LIST = [u"coolcode"]  #$NON-NLS-1$


def tidyHtml(htmlSrc, options = XHTML_OPTIONS):
    """uTidy - Cleans up the html source. Exceptions are thrown back to the calling code. """
    (tidyHtml, errorList) = runTidy(htmlSrc, options)  #@UnusedVariable
    return tidyHtml
# end tidyHtml()

def runTidy(htmlSrc, options = XHTML_OPTIONS):
    """Runs Tidy and returns tuple (cleanHtml, errList)."""
    # use the global custom tag list so that we can append new tags as we find them.
    # (Tidy normally fails if it does not understand the tag - hence we need to supply it with a list of custom tags.)
    global TIDY_CUSTOM_INLINE_TAG_LIST
    global TIDY_CUSTOM_EMPTY_TAG_LIST
    global TIDY_CUSTOM_BLOCK_TAG_LIST
    global TIDY_CUSTOM_PRE_TAG_LIST

    # set new-inline-tags, new-empty-tags and new_blocklevel_tags.
    if TIDY_CUSTOM_INLINE_TAG_LIST:
        options['new_inline_tags'] = u','.join(TIDY_CUSTOM_INLINE_TAG_LIST)
    if TIDY_CUSTOM_EMPTY_TAG_LIST:
        options['new_empty_tags'] = u','.join(TIDY_CUSTOM_EMPTY_TAG_LIST)
    if TIDY_CUSTOM_BLOCK_TAG_LIST:
        options['new_blocklevel_tags'] = u','.join(TIDY_CUSTOM_BLOCK_TAG_LIST)
    if TIDY_CUSTOM_PRE_TAG_LIST:
        options['new_pre_tags'] = u','.join(TIDY_CUSTOM_PRE_TAG_LIST)

    # run Tidy
    (tidyHtml, errorList) = _internalRunTidy(htmlSrc, options)
    # check to see if Tidy failed due to unknown (custom) tags
    if _checkCustomTagErrors(errorList):
        # Since Tidy failed due to unrecognized tags, add them to the global list and re-run tidy.
        # if we found custom tags, then run tidy again.
        if TIDY_CUSTOM_INLINE_TAG_LIST:
            options['new_inline_tags'] = u','.join(TIDY_CUSTOM_INLINE_TAG_LIST)
        if TIDY_CUSTOM_EMPTY_TAG_LIST:
            options['new_empty_tags'] = u','.join(TIDY_CUSTOM_EMPTY_TAG_LIST)
        if TIDY_CUSTOM_BLOCK_TAG_LIST:
            options['new_blocklevel_tags'] = u','.join(TIDY_CUSTOM_BLOCK_TAG_LIST)

        (tidyHtml, errorList) = _internalRunTidy(htmlSrc, options)
    return (tidyHtml, errorList)
# end runTidy()

def _internalRunTidy(htmlSrc, options = XHTML_OPTIONS):
    # Runs tidy and returns tuple (html, errorList)
    unsupportedOptions = ["raw", "output_error", "show_warnings"]
    try:
        # remove unsupported options.
        if options:
            options['tidy_mark'] = 0
            for s in unsupportedOptions:
                if options.has_key(s):
                    del options[s]
    except:
        pass

    lineOffset = 0
    if htmlSrc:
        # escape illegal entities. E.g. convert &##! to &amp;##!
        try:
            htmlSrc = ILLEGAL_ENTITY_RE.sub(u"&amp;\g<2>", htmlSrc)  #$NON-NLS-1$
        except:
            pass        
    if not hasBody(htmlSrc):
        # wrap content inside a <html><head/><body> [CONTENT] </body></html>
        htmlSrc = XHTML_TEMPLATE % htmlSrc
        lineOffset = XHTML_TEMPLATE_LINE_OFFSET

    tidySrc = convertToUtf8(htmlSrc)
    tidyRet = tidy.parseString(tidySrc, **options)
    errList = []
    severities = dict(W=ZTidyError.WARN, E=ZTidyError.ERROR, C=ZTidyError.OTHER)
    for err in tidyRet.get_errors():
        te = ZTidyError()
        if err.line is not None:
            te.line = err.line - lineOffset
        if err.col is not None:
            te.col = err.col
        if err.message is not None:
            te.message = err.message
        te.severity = ZTidyError.NONE
        if severities.has_key(err.severity):
            te.severity = severities[err.severity]
        errList.append(te)

    outHtml = str(tidyRet)
    return (convertToUnicode(outHtml), errList)
# end _internalRunTidy()

# ----- END U_TIDY ----

# --------------
# class for containing Tidy errors and warnings.
# --------------
class ZTidyError:

    NONE = 0
    WARN = 1
    ERROR = 2
    OTHER = 3
    
    def __init__(self):
        self.severity = 0
        self.line = -1
        self.col = -1
        self.message = u""
    # end __init__()

# end ZTidyError

# ----------------------------------------------------------------------------
# Regular expressions to match Tidy errors with regard to unkown (schema) tags.
# ----------------------------------------------------------------------------
TIDY_CUSTOM_TAG_PATTERN = r'(<)(.*?)(>)(\s+is not recognized)' #$NON-NLS-1$
TIDY_CUSTOM_TAG_RE = re.compile(TIDY_CUSTOM_TAG_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
TIDY_CUSTOM_OPENTAG_PATTERN = r'(discarding unexpected )(<)([^/.].*?)(>)' #$NON-NLS-1$
TIDY_CUSTOM_OPENTAG_RE = re.compile(TIDY_CUSTOM_OPENTAG_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
TIDY_CUSTOM_CLOSETAG_PATTERN = r'(discarding unexpected )(</)(.*?)(>)' #$NON-NLS-1$
TIDY_CUSTOM_CLOSETAG_RE = re.compile(TIDY_CUSTOM_CLOSETAG_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)


def _checkCustomTagErrors(errList):
    u"""Checks the error list to see if there are any custom (non-xhtml) tag errors - if so,
    this returns true after adding the tags to a global list of custom tags."""
    if not errList:
        return False
    rVal = False
    tagList = []
    openList = []
    closeList = []
    for err in errList:
        if not err.message:
            continue
        customTag = _getTag(err.message, TIDY_CUSTOM_TAG_RE, 1, 4)
        if customTag and not customTag in tagList:
            tagList.append(customTag)
            continue
        customTag = _getTag(err.message, TIDY_CUSTOM_OPENTAG_RE, 2, 4)
        if customTag and not customTag in openList:
            openList.append(customTag)
            continue
        customTag = _getTag(err.message, TIDY_CUSTOM_CLOSETAG_RE, 2, 4)
        if customTag and not customTag in closeList:
            closeList.append(customTag)

    # Sort out tags between inline and empty tags.  Inline tags should have entries in both - open and close list.
    global TIDY_CUSTOM_INLINE_TAG_LIST
    global TIDY_CUSTOM_EMPTY_TAG_LIST
    # build inline tags
    for tag in closeList:
        if not tag in TIDY_CUSTOM_INLINE_TAG_LIST:
            TIDY_CUSTOM_INLINE_TAG_LIST.append(tag)
            rVal = True
    # build empty tags
    for tag in openList:
        if not (tag in closeList) and not (tag in TIDY_CUSTOM_EMPTY_TAG_LIST):
            TIDY_CUSTOM_EMPTY_TAG_LIST.append(tag)
            rVal = True

    return rVal
# end _checkCustomTagErrors()

def _getTag(aString, aRe, aGroupIndex, aExpectedLen):
    rTag = None
    theMatch = aRe.match(aString)
    if theMatch:
        matchList =  theMatch.groups()
        if matchList and len(matchList) == aExpectedLen and matchList[aGroupIndex]:
            rTag = matchList[aGroupIndex].strip()
    return rTag
# end _getTag()

# --------------
# string conversion util methods.
# --------------

def isunicode(s):
    is_unicode = False
    if s and isinstance(s, unicode):
        is_unicode = True
    return is_unicode
# end isunicode()

# -----------------------------------------------------------------------
# XHTML TEMPLATE - wrap content in xhtml head/body only the body content is given.
# (Note - body starts at line 6,on 0 based index)
# -----------------------------------------------------------------------
XHTML_TEMPLATE_LINE_OFFSET = 6
XHTML_TEMPLATE=u"""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html>
<head>
<title>simple document</title>
</head>
<body>
%s
</body>
</html>
"""
