from zoundry.base.util.text.textutil import getNoneString
import re

# ----------------------------------------------------------------------------------------
# Common interface to convert, modifiy or filter plain text content.
#
# This interface is more than meets the eye.
# ----------------------------------------------------------------------------------------
class IZTextTransformer:

    def transform(self, text):
        u"Tranforms the given text and returns the resultant text string." #$NON-NLS-1$
    # end transform()

# end IZTextTransformer


# ----------------------------------------------------------------------------------------
# Demo impl.
# ----------------------------------------------------------------------------------------
class ZHelloTransformer(IZTextTransformer):

    def __init__(self):
        pass
    # end __init__()

    def transform(self, text):
        return u"Hello " + text  #$NON-NLS-1$
    # end transform()

# end ZHelloTransformer


# ----------------------------------------------------------------------------------------
# List of common regular expressions.
# ----------------------------------------------------------------------------------------

REPEATING_WS_PATTERN = r'\s\s+' #$NON-NLS-1$
REPEATING_WS_RE = re.compile(REPEATING_WS_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)

REPEATING_NL_PATTERN = r'\n\n+' #$NON-NLS-1$
REPEATING_NL_RE = re.compile(REPEATING_NL_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)


BODY_PATTERN = r'<body[^<>]*?>(.*?)</body[^<>]*?>' #$NON-NLS-1$
BODY_RE = re.compile(BODY_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
PRE_PATTERN = r'(<pre.*?>)(.*?)</pre>' #$NON-NLS-1$
PRE_RE = re.compile(PRE_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
SCRIPT_PATTERN = r'(<script.*?>)(.*?)</script>' #$NON-NLS-1$
SCRIPT_RE = re.compile(SCRIPT_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
STYLE_PATTERN = r'(<style.*?>)(.*?)</style>' #$NON-NLS-1$
STYLE_RE = re.compile(STYLE_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
BRNEWLINE_PATTERN = r'<br\s*/>\s*\n+' #$NON-NLS-1$
BRNEWLINE_RE = re.compile(BRNEWLINE_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)

# Regular expressions to convert WP plain text to html
TEXT2HTML_ADDNL1_PATTERN = r'(<(?:table|thead|tfoot|caption|colgroup|tbody|tr|td|th|div|dl|dd|dt|ul|ol|li|pre|select|form|blockquote|address|math|p|h[1-6])[^>]*>)';#$NON-NLS-1$
TEXT2HTML_ADDNL1_RE = re.compile(TEXT2HTML_ADDNL1_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
TEXT2HTML_ADDNL2_PATTERN = r'(</(?:table|thead|tfoot|caption|colgroup|tbody|tr|td|th|div|dl|dd|dt|ul|ol|li|pre|select|form|blockquote|address|math|p|h[1-6])>)'; #$NON-NLS-1$
TEXT2HTML_ADDNL2_RE = re.compile(TEXT2HTML_ADDNL2_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
TEXT2HTML_NL_PATTERN = r'\n\n+' #$NON-NLS-1$
TEXT2HTML_NL_RE = re.compile(TEXT2HTML_NL_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
TEXT2HTML_P_PATTERN = r'\n?(.+?)(?:\n\s*\n)' #$NON-NLS-1$
TEXT2HTML_P_RE = re.compile(TEXT2HTML_P_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
TEXT2HTML_EXTRACT1_PATTERN = r'<p>\s*(</?(?:table|thead|tfoot|caption|colgroup|tbody|tr|td|th|div|dl|dd|dt|ul|ol|li|hr|pre|select|form|blockquote|address|math|p|h[1-6])[^>]*>)\s*</p>' #$NON-NLS-1$
TEXT2HTML_EXTRACT1_RE = re.compile(TEXT2HTML_EXTRACT1_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
TEXT2HTML_EXTRACT2_PATTERN = r'<p>(<li.+?)</p>' #$NON-NLS-1$
TEXT2HTML_EXTRACT2_RE = re.compile(TEXT2HTML_EXTRACT2_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
TEXT2HTML_BQ1_PATTERN = r'<p><blockquote([^>]*)>' #$NON-NLS-1$
TEXT2HTML_BQ1_RE = re.compile(TEXT2HTML_BQ1_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
TEXT2HTML_BQ2_PATTERN = r'</blockquote></p>' #$NON-NLS-1$
TEXT2HTML_BQ2_RE = re.compile(TEXT2HTML_BQ2_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
TEXT2HTML_EXTRACT3_PATTERN = r'<p>\s*(</?(?:table|thead|tfoot|caption|colgroup|tbody|tr|td|th|div|dl|dd|dt|ul|ol|li|hr|pre|select|form|blockquote|address|math|p|h[1-6])[^>]*>)' #$NON-NLS-1$
TEXT2HTML_EXTRACT3_RE = re.compile(TEXT2HTML_EXTRACT3_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
TEXT2HTML_EXTRACT4_PATTERN = r'(</?(?:table|thead|tfoot|caption|colgroup|tbody|tr|td|th|div|dl|dd|dt|ul|ol|li|pre|select|form|blockquote|address|math|p|h[1-6])[^>]*>)\s*</p>' #$NON-NLS-1$
TEXT2HTML_EXTRACT4_RE = re.compile(TEXT2HTML_EXTRACT4_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
TEXT2HTML_EXTRACT5_PATTERN = r'(</?(?:table|thead|tfoot|caption|tbody|tr|td|th|div|dl|dd|dt|ul|ol|li|pre|select|form|blockquote|address|math|p|h[1-6])[^>]*>)\s*<br />' #$NON-NLS-1$
TEXT2HTML_EXTRACT5_RE = re.compile(TEXT2HTML_EXTRACT5_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
TEXT2HTML_BR_PATTERN = r'(?<!<br />)\s*\n' #$NON-NLS-1$
TEXT2HTML_BR_RE = re.compile(TEXT2HTML_BR_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
TEXT2HTML_EXTRACT6_PATTERN = r'<br />(\s*</?(?:p|li|div|dl|dd|dt|th|pre|td|ul|ol)>)' #$NON-NLS-1$
TEXT2HTML_EXTRACT6_RE = re.compile(TEXT2HTML_EXTRACT6_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)

# ----------------------------------------------------------------------------------------
# Convers \r\n to use \n .
# ----------------------------------------------------------------------------------------
class ZNormalizeNewlinesTransformer(IZTextTransformer):
    u"""Converts \r\n occurances with \n character.""" #$NON-NLS-1$
    def __init__(self):
        pass

    def transform(self, text):
        if not text:
            return text
        text = text.replace(u"\r\n", u"\n") #$NON-NLS-1$ #$NON-NLS-2$
        text = text.replace(u"\r", u"\n") #$NON-NLS-1$ #$NON-NLS-2$
        return text
    # end transform()

# end ZNormalizeNewlinesTransformer

# ----------------------------------------------------------------------------------------
# Replaces repeating newlines, spaces etc. with a single white space.
# ----------------------------------------------------------------------------------------
class ZNormalizeTextTransformer(ZNormalizeNewlinesTransformer):
    u"""Replaces repeating white spaces and newlines with a single white space (single new line).""" #$NON-NLS-1$
    def __init__(self, removeNewLines = False):
        self.removeNewLines = removeNewLines

    def transform(self, text):
        # normalize new liness i.e. \n\r and \r becomes \n.
        text = ZNormalizeNewlinesTransformer.transform(self, text)
        if not text:
            return text
        # replace repeating newlines with a single new line
        text = REPEATING_NL_RE.sub(u"\n", text)  #$NON-NLS-1$
        # if new lines are to be removed, then replace them with a space
        # (so that they will be removed in the next step - removing repeating white spaces)
        if self.removeNewLines:
            text = text.replace(u"\n", u" ") #$NON-NLS-1$ #$NON-NLS-2$
        # replace repeating newlines, spaces, tabs etc with  single white space.
        text = REPEATING_WS_RE.sub(u" ", text)  #$NON-NLS-1$
        return text
    # end transform()

# ----------------------------------------------------------------------------------------
# Converts \r\n to use \n  and removes any newlines following <br> tag.
# ----------------------------------------------------------------------------------------
class ZXhtmlNormalizeNewlinesTransformer(ZNormalizeNewlinesTransformer):
    u"""Converts \r\n occurances with \n characters and removes any lines feeds following a <br/> tag.""" #$NON-NLS-1$
    def __init__(self):
        pass

    def transform(self, text):
        if not text:
            return text
        # nornmalized new lines
        text = ZNormalizeNewlinesTransformer.transform(self, text)
        # remove newlines after a <br> otherwise, some CMS servers add extra <br> during "convert newlines to <br>".
        text = BRNEWLINE_RE.sub(u"<br/>", text)  #$NON-NLS-1$
        return text
    # end transform()

# end ZXhtmlNormalizeNewlinesTransformer


# ----------------------------------------------------------------------------------------
# Removes new lines in a xhtml string while preserving newlines in elements such as <pre> element,
# ----------------------------------------------------------------------------------------
class ZXhtmlRemoveNewLinesTransformer(ZXhtmlNormalizeNewlinesTransformer):
    u"""Removes new lines in a xhtml string while preserving newlines in a <pre> element.""" #$NON-NLS-1$

    def __init__(self, removeAll = False):
        self.removeAll = removeAll

    def transform(self, text):
        if not text:
            return text
        # nornmalized new lines
        text = ZXhtmlNormalizeNewlinesTransformer.transform(self, text)
        # first replace newlines inside <pre> tags with a special marker  <__zbwnl__/> (see callback func).
        try:
            text = PRE_RE.sub(self._filterPreNewLine, text)
            #do same for <script> and  <style>.  TODO: (PJ) and any tag with xml:preserve space.
            text = SCRIPT_RE.sub(self._filterScriptNewLine, text)
            text = STYLE_RE.sub(self._filterStyleNewLine, text)
        except:
            pass
        # stripnewlines
        text = text.replace(u" \n", u" ") #$NON-NLS-1$ #$NON-NLS-2$
        text = text.replace(u"\n ", u" ") #$NON-NLS-1$ #$NON-NLS-2$
        text = text.replace(u"\n", u" ") #$NON-NLS-1$ #$NON-NLS-2$
        # restore newlines inside the pre tag
        text = text.replace(u"<__zbwnl__/>", u"\n") #$NON-NLS-1$ #$NON-NLS-2$
        return text
    # end transform()

    #-------------------------------------------------------------
    # Callback function for regular expression PRE_RE where newlines inside a <pre>
    # tags are replaced with a special marker. (same for <script> and <style>)
    #-------------------------------------------------------------
    def _filterNewLineContent(self, match, tag):
        # get tuple of matches - must be 2 other wise assume failure.
        s = match.groups()
        if len(s) == 2 and s[0] and s[1]:
            # s[0]: pre start tag
            # s[1]: pre tag contents except the end tag

            # mark newlines (\n) with special <__zbwnl__/> tag. (which we will later replace with \n.
            return u"<__zbwnl__/>" + s[0] + s[1].replace(u"\n", u"<__zbwnl__/>") + u"</" + tag + u"><__zbwnl__/>"  #$NON-NLS-1$  #$NON-NLS-2$  #$NON-NLS-3$ #$NON-NLS-4$ #$NON-NLS-5$
        else:
            # match failed - return unchanged.
            return match.group()

    def _filterPreNewLine(self, match):
        return self._filterNewLineContent(match, u"pre") #$NON-NLS-1$
    # end _filterPreNewLine()

    def _filterScriptNewLine(self, match):
        return self._filterNewLineContent(match, u"script") #$NON-NLS-1$
    # end _filterScriptNewLine()

    def _filterStyleNewLine(self, match):
        return self._filterNewLineContent(match, u"style") #$NON-NLS-1$
    # end _filterStyleNewLine()

# end ZXhtmlRemoveNewLinesTransformer


# ----------------------------------------------------------------------------------------
# Transforms plain text content into the string with xhtml markup
# ----------------------------------------------------------------------------------------
class ZTextToXhtmlTransformer(ZNormalizeNewlinesTransformer):
    u"""Transforms plain text content into the string with xhtml markup.""" #$NON-NLS-1$
    def __init__(self):
        pass

    def transform(self, text):
        if not text:
            return text
        # normalize newlines (i.e. \r\n becomes \n)
        text = ZNormalizeNewlinesTransformer.transform(self, text)
        try:
            text = text + u"\n\n" #$NON-NLS-1$
            # add new line before start of block element (such as pre, p, table etc).
            text = TEXT2HTML_ADDNL1_RE.sub(u"\n\g<1>", text) #$NON-NLS-1$
            # add new line after end of block level element.
            text = TEXT2HTML_ADDNL2_RE.sub(u"\g<1>\n\n", text) #$NON-NLS-1$
            # replace multi consecutive (two or more) newlines with just two new lines.
            text = TEXT2HTML_NL_RE.sub(u"\n\n", text) #$NON-NLS-1$
            # next wrap contents between newlines with a <p> tag. (which also wraps other blocks such as table)
            text = TEXT2HTML_P_RE.sub(u"<p>\g<1></p>\n", text)#$NON-NLS-1$
            # remove <p> wrapper (from above) for some block level elements that should be outside a <p>. eg <pre>.
            text = TEXT2HTML_EXTRACT1_RE.sub(u"\g<1>", text) #$NON-NLS-1$
            # same for <li>
            text = TEXT2HTML_EXTRACT2_RE.sub(u"\g<1>", text) #$NON-NLS-1$
            # invert <p><blockquote/></p> to <blockquote></p><blockquote>
            text = TEXT2HTML_BQ1_RE.sub(u"<blockquote\g<1>><p>", text) #$NON-NLS-1$
            text = TEXT2HTML_BQ2_RE.sub(u"</p></blockquote>", text) #$NON-NLS-1$
            # remove <p> wrapper if wrapping block level element.
            text = TEXT2HTML_EXTRACT3_RE.sub(u"\g<1>", text) #$NON-NLS-1$
            text = TEXT2HTML_EXTRACT4_RE.sub(u"\g<1>", text) #$NON-NLS-1$
            # normalize spaces after a <br> and before newline.
            text = TEXT2HTML_BR_RE.sub(u"<br />\n", text) #$NON-NLS-1$
            # remove <br /> if immedietly before block level tag
            text = TEXT2HTML_EXTRACT5_RE.sub(u"\g<1>", text) #$NON-NLS-1$
            # remove <br /> if immedietly after block level tag
            text = TEXT2HTML_EXTRACT6_RE.sub(u"\g<1>", text) #$NON-NLS-1$
        except:
            pass
        return text
    # end transform()

# end ZTextToXhtmlTransformer


MARKUP_TAG_PATTERN= r'<(.|\n)+?>' #$NON-NLS-1$
MARKUP_TAG_RE = re.compile(MARKUP_TAG_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL )

# ----------------------------------------------------------------------------------------
# Transforms html content string into a plain text string (i.e. xhtml markup stripped)
# ----------------------------------------------------------------------------------------
class ZXhtmlToTextTransformer(ZNormalizeNewlinesTransformer):
    u"""Transforms html content string into a plain text string (i.e. xhtml markup stripped).""" #$NON-NLS-1$
    def __init__(self):
        pass
    # end __init__()

    def transform(self, text):
        if text:
            text = MARKUP_TAG_RE.sub(u"", text) #$NON-NLS-1$
        return text
    # end transform()
# end ZXhtmlToTextTransformer

# ----------------------------------------------------------------------------------------
# Removes element attribute prefixes.
# Ref: see http://tim.mackey.ie/CleanWordHTMLUsingRegularExpressions.aspx
# ----------------------------------------------------------------------------------------
class ZRemoveXmlAttributePrefixTransformer(IZTextTransformer):
    u"""Removes xml: and xmlns: prefixes in attributes.""" #$NON-NLS-1$
    def __init__(self, prefixes = u"xml,xmlns"): #$NON-NLS-1$
        prefixes = getNoneString(prefixes)
        self.reCompileList = []
        if prefixes:
            prefixList = prefixes.split(u",") #$NON-NLS-1$
            for prefix in prefixList:
                rePattern = r'''<([^>]*)(?:%s[:]\w+)=(?:'[^']*'|""[^""]*""|[^\s>]+)([^>]*)>''' % prefix.strip() #$NON-NLS-1$
                reCompile = re.compile(rePattern, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL )
                self.reCompileList.append( reCompile )
    # end __init()__

    def transform(self, text):
        if not text or len(self.reCompileList) == 0:
            return text
        for reCompile in self.reCompileList:
            # the reg expression only removes a single attribute.
            # so, repeat - 4 times to remove upto 4 attributes
            text = reCompile.sub(u"<\g<1>\g<2>>", text) #$NON-NLS-1$
            text = reCompile.sub(u"<\g<1>\g<2>>", text) #$NON-NLS-1$
            text = reCompile.sub(u"<\g<1>\g<2>>", text) #$NON-NLS-1$
            text = reCompile.sub(u"<\g<1>\g<2>>", text) #$NON-NLS-1$
        return text
    # end transform()
# end ZRemoveXmlAttributePrefixTransformer()


