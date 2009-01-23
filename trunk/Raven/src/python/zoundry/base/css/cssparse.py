from zoundry.base.css.csscolor import ZCssColor
import re

# "top right bottom left" Eg: 2px 2px 2px 2px
SIZE1_PATTERN = r"(\d+\.?\d*(px|em)*)\s+(\d+\.?\d*(px|em)*)\s+(\d+\.?\d*(px|em)*)\s+(\d+\.?\d*(px|em)*)" #$NON-NLS-1$
SIZE1_RE = re.compile(SIZE1_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)

# "top right bottom" Eg: 2px 3px 4px  (left=right=3px)
SIZE2_PATTERN = r"(\d+\.?\d*(px|em)*)\s+(\d+\.?\d*(px|em)*)\s+(\d+\.?\d*(px|em)*)" #$NON-NLS-1$
SIZE2_RE = re.compile(SIZE2_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)

# "top right" Eg: 2px 2px  (bottom=top and left=right)
SIZE3_PATTERN = r"(\d+\.?\d*(px|em)*)\s+(\d+\.?\d*(px|em)*)" #$NON-NLS-1$
SIZE3_RE = re.compile(SIZE3_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)

# one size.
SIZE4_PATTERN = r"(\d+\.?\d*(px|em)*)" #$NON-NLS-1$
SIZE4_RE = re.compile(SIZE4_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)

DIGIT_ONLY_PATTERN = r"^\d+$" #$NON-NLS-1$
DIGIT_ONLY_RE = re.compile(DIGIT_ONLY_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)

COLOR1_PATTERN = r"(#\w\w\w\w\w\w)\s+" #$NON-NLS-1$
COLOR1_RE = re.compile(COLOR1_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
COLOR2_PATTERN = r"(rgb\s*\(\s*\d+%?\s*,\s*\d+%?\s*,\s*\d+%?\s*\))" #$NON-NLS-1$
COLOR2_RE = re.compile(COLOR2_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
COLOR3_PATTERN = r"(#\w\w\w)\s+" #$NON-NLS-1$
COLOR3_RE = re.compile(COLOR3_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
COLOR4_PATTERN = r"(\w+)\s+" #$NON-NLS-1$
COLOR4_RE = re.compile(COLOR4_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)


BORDER_IE_PATTERN = r"((#\w+)|(rgb\(.*\))|(\w+))\s+(\d+\.?\d*(px|em))\s+(\w+)\s*" #$NON-NLS-1$
BORDER_IE_RE = re.compile(BORDER_IE_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)

BORDER_W3C_PATTERN = r"(\d+\.?\d*(px|em))\s+(\w+)\s+((#\w+)|(\w+))" #$NON-NLS-1$
BORDER_W3C_RE = re.compile(BORDER_W3C_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)

def _getSafeLength(cssLength):
    # appends "px" if unit is not represent
    if cssLength and DIGIT_ONLY_RE.match(cssLength) is not None:
        return cssLength + u"px" #$NON-NLS-1$
    else:
        return cssLength;

def parseCssRectangleProperty(cssRectangleStr):
    u"""parseCssRectangleProperty(string) -> (string, string, string, string)
    Parses formats "top right bottom left", "top right" and always 
    returns string tuple (top, right, bottom, left).
    Useful for parsing margin and padding properties.
    """ #$NON-NLS-1$
    if not cssRectangleStr:
        return (None, None, None, None)
    cssRectangleStr = cssRectangleStr + u" " #$NON-NLS-1$
    t = r = b = l = None
    m = SIZE1_RE.match(cssRectangleStr)
    if m:
        (t, r, b, l) = ( m.group(1), m.group(3), m.group(5), m.group(7) )
    if not m:
        m = SIZE2_RE.match(cssRectangleStr)
        if m:
            (t, r, b, l) = ( m.group(1), m.group(3), m.group(5), m.group(3) )            
    if not m:
        m = SIZE3_RE.match(cssRectangleStr)
        if m:
            (t, r, b, l) = ( m.group(1), m.group(3), m.group(1), m.group(3) )
    if not m:
        m = SIZE4_RE.match(cssRectangleStr)
        if m:
            (t, r, b, l) = ( m.group(1), m.group(1), m.group(1), m.group(1) )
    return (_getSafeLength(t), _getSafeLength(r), _getSafeLength(b), _getSafeLength(l))
# end parseCssRectangleProperty

def parseCssColorProperty(cssColorStr):
    u"""parseCssColorProperty(string) -> ZCssColor
    Parses CSS color property such as #RRGGBB or rgb(r,g,b)
    and returns ZCssColor or None if parsing fails.
    """ #$NON-NLS-1$
    if cssColorStr:
        cssColorStr = cssColorStr + u" " #$NON-NLS-1$
        val = None
        reList = [COLOR1_RE, COLOR2_RE, COLOR3_RE, COLOR4_RE]
        for regexp in reList:
            m = regexp.match(cssColorStr)
            if m:
                val = m.group(1).lower() 
                break
        color = ZCssColor()
        if color.setCssColor(val):
            return color
    return None
# end parseCssColorProperty()

    
def parseCssBorderProperty(cssBorderStr):
    u"""parseCssBorderProperty(string) -> (string, string, ZCssColor)
    Parses css border property and returns tuple(width_string, style_string and ZCssColor).
    Tuple values maybe None if value is not specified.
    """ #$NON-NLS-1$
    if not cssBorderStr:
        return (None, None, None)
    cssBorderStr = cssBorderStr + u" " #$NON-NLS-1$  
    width = None
    color = None
    style = None
    m = BORDER_IE_RE.match(cssBorderStr)        
    if m:
        # color, length, style
        color = m.group(1)
        width = m.group(5)
        style = m.group(7)
    else:
        m = BORDER_W3C_RE.match(cssBorderStr)        
        if m:
            # width style color
            width = m.group(1)
            style = m.group(3)
            color = m.group(4)
    return (_getSafeLength(width), style, parseCssColorProperty(color))
# end parseCssBorderProperty
    
