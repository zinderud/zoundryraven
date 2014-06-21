from zoundry.base.util.text.textutil import getSafeString
from zoundry.blogapp.ui.dnd.dnd import IZDnDFormats
import wx

# --------------------------------------------------------------------------------------------
# A data object implementation used to transfer a blog post internally within the application.
# This class simply uses the blog post's ID to transfer the post from the drag source to the
# drop target.  It can both send and receive data.
# --------------------------------------------------------------------------------------------
class ZBlogPostDataObjectInternal(wx.CustomDataObject):

    def __init__(self, data = None):
        wx.CustomDataObject.__init__(self, IZDnDFormats.DND_FORMAT_BLOGPOST_INTERNAL)
        
        if data is not None:
            self.SetData(str(getSafeString(data)))
    # end __init__()

# end ZBlogPostDataObjectInternal
