import wx

# -------------------------------------------------------------------------------------------
# Some constants for Drag and Drop (DnD formats, for example).
# -------------------------------------------------------------------------------------------
class IZDnDConstants:

    DND_FORMAT_BLOGPOST_INTERNAL = u"zoundry.dataformats.blogpost.internal" #$NON-NLS-1$

# end IZDnDConstants


# -------------------------------------------------------------------------------------------
# Custom DnD data formats.
# -------------------------------------------------------------------------------------------
class IZDnDFormats:

    DND_FORMAT_BLOGPOST_INTERNAL = wx.CustomDataFormat(IZDnDConstants.DND_FORMAT_BLOGPOST_INTERNAL)

# end IZDnDFormats
