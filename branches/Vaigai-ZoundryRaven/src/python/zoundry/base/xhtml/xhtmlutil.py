import re

# XHTML tag regular expressions
HTML_TITLE_PATTERN = r'<title[^<>]*?>(.*?)</title[^<>]*?>' #$NON-NLS-1$
HTML_TITLE_RE = re.compile(HTML_TITLE_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
HTML_BODY_PATTERN = r'<body[^<>]*?>(.*?)</body[^<>]*?>' #$NON-NLS-1$
HTML_BODY_RE = re.compile(HTML_BODY_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
HTML_P_PATTERN = r'<p[^<>]*?>(.*?)</p[^<>]*?>' #$NON-NLS-1$
HTML_P_RE = re.compile(HTML_P_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
HTML_DIV_PATTERN = r'<div[^<>]*?>(.*?)</div[^<>]*?>' #$NON-NLS-1$
HTML_DIV_RE = re.compile(HTML_DIV_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
HTML_TABLE_PATTERN = r'<table[^<>]*?>(.*?)</table[^<>]*?>' #$NON-NLS-1$
HTML_TABLE_RE = re.compile(HTML_TABLE_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
HTML_PRE_PATTERN = r'<pre[^<>]*?>(.*?)</pre[^<>]*?>' #$NON-NLS-1$
HTML_PRE_RE = re.compile(HTML_PRE_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
HTML_BQ_PATTERN = r'<blockquote[^<>]*?>(.*?)</blockquote[^<>]*?>' #$NON-NLS-1$
HTML_BQ_RE = re.compile(HTML_BQ_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)

# MS Word/Office tags
MSO_P_PATTERN = r'<o:p[^<>]*?>(.*?)</o:p[^<>]*?>' #$NON-NLS-1$
MSO_P_RE = re.compile(MSO_P_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
MSO_NS_PATTERN = r'<[owv]\s*:[^<>]*?>' #$NON-NLS-1$
MSO_NS_RE = re.compile(MSO_NS_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)

MSO_VNS_PATTERN = r'=\s*"urn:schemas-microsoft-com:vml"' #$NON-NLS-1$
MSO_VNS_RE = re.compile(MSO_VNS_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
MSO_ONS_PATTERN = r'=\s*"urn:schemas-microsoft-com:office:office"' #$NON-NLS-1$
MSO_ONS_RE = re.compile(MSO_ONS_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
MSO_WNS_PATTERN = r'=\s*"urn:schemas-microsoft-com:office:word"' #$NON-NLS-1$
MSO_WNS_RE = re.compile(MSO_WNS_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)

# <?xml:namespace prefix = o ns = "urn:schemas-microsoft-com:office:office" />
# FIXME (PJ) refine regular expression to include ns = '...' attribute
MSO_NSDECL_PATTERN = r'<\?xml:namespace\s+[^<>]*?>' #$NON-NLS-1$
MSO_NSDECL_RE = re.compile(MSO_NSDECL_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)

# Pattern for file protocol
FILE_PROTOCOL_PATTERN = r"^file://[.]*" #$NON-NLS-1$
FILE_PROTOCOL_RE = re.compile(FILE_PROTOCOL_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
# Http protocol
HTTP_PROTOCOL_PATTERN = r"^http[s]?://[.]*" #$NON-NLS-1$
HTTP_PROTOCOL_RE = re.compile(HTTP_PROTOCOL_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)

# Img tag with local file:// based images.
LOCAL_IMAGE_TAG_PATTERN = r"""<img.*src\s*=\s*\"file://""" #$NON-NLS-1$
LOCAL_IMAGE_TAG_RE = re.compile(LOCAL_IMAGE_TAG_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)

BLOCK_LEVEL_TAGS = u"body,address,center,div,blockquote,hr,h1,h2,h3,h4,h5,h6,ol,dl,pre,table,ul,p".split(u",") #$NON-NLS-1$ #$NON-NLS-2$
# -----------------------------------------------------------------------------------------
# Extracts and returns html title contents (excluding title tag)
# -----------------------------------------------------------------------------------------
def extractTitle(xhtmlStringContent):
    u"""Extracts and returns html title contents (excluding title tag)""" #$NON-NLS-1$
    title = u"" #$NON-NLS-1$
    if xhtmlStringContent:
        findList = HTML_TITLE_RE.findall(xhtmlStringContent)
        if findList:
            title = findList[0]
    return title

# -----------------------------------------------------------------------------------------
# Extracts and returns html body contents (excluding body tag)
# -----------------------------------------------------------------------------------------
def extractBody(xhtmlStringContent):
    u"""Extracts and returns html body contents (excluding body tag)""" #$NON-NLS-1$
    if xhtmlStringContent:
        findList = HTML_BODY_RE.findall(xhtmlStringContent)
        if findList:
            xhtmlStringContent = findList[0]
    return xhtmlStringContent

# -----------------------------------------------------------------------------------------
# Returns true if the given content has <body/>
# -----------------------------------------------------------------------------------------
def hasBody(xhtmlStringContent):
    u"""Returns true if the htmlSrc has <body>  element.""" #$NON-NLS-1$
    rVal = False
    if xhtmlStringContent:
        findList = HTML_BODY_RE.findall(xhtmlStringContent)
        if findList:
            rVal = True
    return rVal

# -----------------------------------------------------------------------------------------
# Wraps the give source in <html><head><body></body></html> tags
# -----------------------------------------------------------------------------------------
def wrapHtmlBody(xhtmlStringContent, title = None):
    u"""Wraps the give source in <html><head><body></body></html> tags""" #$NON-NLS-1$
    if not title:
        title = extractTitle(xhtmlStringContent)
    xhtml = u"<html>\n<head>\n<title>" + title + u"</title>\n</head>\n<body>\n" + extractBody(xhtmlStringContent) + u"\n</body>\n</html>" #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$
    return xhtml

# -----------------------------------------------------------------------------------------
# Returns true if the content has either a <p></p> or <div></div> tags.
# This method is used to check to see if the content is plain text i.e. no xhtml structural markup.
# -----------------------------------------------------------------------------------------
def hasXhtmlMarkup(xhtmlStringContent):
    u"""Returns true if the content has either a <p></p> or <div></div> tags""" #$NON-NLS-1$
    rVal = False
    if xhtmlStringContent:
        sample = xhtmlStringContent
        if len(xhtmlStringContent) > 15:
            sample = xhtmlStringContent[0:14]
        # check if content starts with markup.
        sample = sample.lower().strip()
        for blocktag in BLOCK_LEVEL_TAGS:
            if sample.startswith(u"<%s>" % blocktag) or sample.startswith(u"<%s " % blocktag): #$NON-NLS-1$ #$NON-NLS-2$
                # also verify there are <p> or <div> contents.
                try:
                    findList = HTML_P_RE.findall(xhtmlStringContent)
                    if not findList:
                        findList = HTML_DIV_RE.findall(xhtmlStringContent)
                    if findList:
                        rVal = True
                        break
                except:
                    pass
                # end try
            # end if starts with
        # end for
    return rVal
# end hasXhtmlMarkup()

# -----------------------------------------------------------------------------------------
# Returns true if the content has either a <o:p></o:p> or MS Word/Office namespaces.
# -----------------------------------------------------------------------------------------
def hasMsOfficeMarkup(xhtmlStringContent):
    u"""Returns true if the content has MS Office/Word specific markup tags.""" #$NON-NLS-1$
    rVal = False
    if xhtmlStringContent:
        try:
            findList = MSO_P_RE.findall(xhtmlStringContent)
            if not findList:
                findList = MSO_WNS_RE.findall(xhtmlStringContent)
            if not findList:
                findList = MSO_ONS_RE.findall(xhtmlStringContent)
            if not findList:
                findList = MSO_VNS_RE.findall(xhtmlStringContent)
            if not findList:
                findList = MSO_NS_RE.findall(xhtmlStringContent)
            if findList:
                rVal = True
        except:
            pass
    return rVal
# end hasMsOfficeMarkup()

# -----------------------------------------------------------------------------------------
# Attempts to remove MSWord tags.
# -----------------------------------------------------------------------------------------
def cleanUpMsOfficeMarkup(xhtmlStringContent):
    u"""Attempts to clean up MS Office/Word tags. Rethrows errors.""" #$NON-NLS-1$

    # remove NS declaration processing instrcutions
    xhtmlStringContent = MSO_NSDECL_RE.sub(u"", xhtmlStringContent)#$NON-NLS-1$
    import wordunmunger
    xhtmlStringContent = wordunmunger.unmungeHtml(xhtmlStringContent)
    return xhtmlStringContent
# end cleanUpMsOfficeMarkup ()

