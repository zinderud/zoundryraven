from zoundry.base.net.http import ZSimpleTextHTTPRequest
from zoundry.base.net.http import ZSimpleXmlHTTPRequest
from zoundry.base.xhtml.xhtmlio import loadXhtmlDocumentFromString
import string

# ------------------------------------------------------------------------------
# An extension of the simple text http request that handles XHTML/HTML output.
# If the response is regular HTML, it will be converted to XHTML.  If the 
# response is XHTML, it will simply be parsed.
# ------------------------------------------------------------------------------
class ZSimpleXHtmlHTTPRequest(ZSimpleXmlHTTPRequest):

    def __init__(self, url, customHeaders = {}, handleEncoding = False, cookieReg = None):
        ZSimpleXmlHTTPRequest.__init__(self, url, customHeaders, handleEncoding, cookieReg)
    # end __init__()

    def _processResponseData(self, resp, txt):
        txt = ZSimpleTextHTTPRequest._processResponseData(self, resp, txt)
        txt = string.lstrip(txt)
        # FIXME (PJ) check resp content-type. If text/plain, then return txt as is isstead of a zdom.
        xhtmlDoc = loadXhtmlDocumentFromString(txt)
        return xhtmlDoc
    # end _processResponseData()

# end ZSimpleXHtmlHTTPRequest
