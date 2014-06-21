from zoundry.base.util.text.unicodeutil import convertToUnicode
from zoundry.blogapp.exceptions import ZBlogAppException
from zoundry.blogapp.messages import _extstr
import os

# FIXME (EPW) deprecated! there is a ui/util/viewutil.py module - I left this because loadStaticHtml should go away anyway

# ----------------------------------------------------------------------------------------
# Loads a static html file from the given path (absolute path) and returns the contents.  
# If params is given (should be a dictionary), then the params are applied to the html 
# content using the % operator prior to being returned.
#
# Throws a ZException if the file cannot be found.
# FIXME (EPW) need a way to i18n-ize the static html files...
# ----------------------------------------------------------------------------------------
def loadStaticHtml(path, params = None):
    if not os.path.isfile(path):
        raise ZBlogAppException(_extstr(u"viewutil.HtmlFileNotFoundError") % path) #$NON-NLS-1$

    f = open(path, u"rb") #$NON-NLS-1$
    html = f.read()
    f.close()
    
    rval = convertToUnicode(html)
    if params:
        rval = rval % params
    return rval
# end loadStaticHtml()
