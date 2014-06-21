
# ------------------------------------------------------------------------------
# The built-in Drag and Drop Source types.
# ------------------------------------------------------------------------------
class IZDnDSourceTypes:

    TYPE_MULTI_FILE = u"zoundry.appframework.dnd.source.multi-file" #$NON-NLS-1$
    TYPE_FILE = u"zoundry.appframework.dnd.source.file" #$NON-NLS-1$
    TYPE_IMG = u"zoundry.appframework.dnd.source.image" #$NON-NLS-1$
    TYPE_LINK = u"zoundry.appframework.dnd.source.link" #$NON-NLS-1$
    TYPE_HTML = u"zoundry.appframework.dnd.source.html" #$NON-NLS-1$
    TYPE_URL = u"zoundry.appframework.dnd.source.url" #$NON-NLS-1$

# end IZDnDSourceTypes


# ------------------------------------------------------------------------------
# Interface for a Drag & Drop source.  This object provides the source type and
# source data for the DnD operation.
# ------------------------------------------------------------------------------
class IZDnDSource(IZDnDSourceTypes):

    def getType(self):
        u"""getType() -> type
        Returns the drag and drop operation's source data type.""" #$NON-NLS-1$
    # end getType()

    def getData(self):
        u"""getData() -> data
        Returns the drag and drop operation's source data.  The
        actual return value will depend on the source data's type.
        For instance, if the type of data is file, then this method
        might return the path to the file.""" #$NON-NLS-1$
    # end getData()

# end IZDnDSource


# ------------------------------------------------------------------------------
# The composite DnD source interface.  This is the interface that DnD handlers
# will interact with.  A composite DnD source has a list of DnD data sources
# that a handler can use to access the data on the clipboard/drag.
# ------------------------------------------------------------------------------
class IZCompositeDnDSource:

    def hasType(self, dndSourceType):
        u"""hasType(type) -> boolean
        Returns true if this composite DnD source contains data of
        the given type.""" #$NON-NLS-1$
    # end hasType()

    def getSource(self, dndSourceType):
        u"""getSource(type) -> IZDnDSource
        Returns the specific DnD source with the given type.""" #$NON-NLS-1$
    # end getSource()

# end IZCompositeDnDSource


# ------------------------------------------------------------------------------
# A composite DnD source impl.
# ------------------------------------------------------------------------------
class ZCompositeDnDSource(IZCompositeDnDSource):

    def __init__(self):
        self.sources = {}
    # end __init__()

    def hasType(self, dndSourceType):
        return dndSourceType in self.sources
    # end hasType()

    def getSource(self, dndSourceType):
        if self.hasType(dndSourceType):
            return self.sources[dndSourceType]
        return None
    # end getSource()

    def addSource(self, dndSource):
        self.sources[dndSource.getType()] = dndSource
    # end addSource()

# end ZCompositeDnDSource


# ------------------------------------------------------------------------------
# A base class for all concrete DnD source implementations.
# ------------------------------------------------------------------------------
class ZDnDSource(IZDnDSource):

    def __init__(self, type, data):
        self.type = type
        self.data = data
    # end __init__()

    def getType(self):
        return self.type
    # end getType()
    
    def getData(self):
        return self.data
    # end getData()

# end ZDnDSource


# ------------------------------------------------------------------------------
# An implementation of a Drag & Drop source for multi-file drop.  The return
# type of the data is a list of files.
# ------------------------------------------------------------------------------
class ZMultiFileDnDSource(ZDnDSource):

    def __init__(self, files):
        ZDnDSource.__init__(self, IZDnDSource.TYPE_MULTI_FILE, files)
    # end __init__()

# end ZMultiDnDSource


# ------------------------------------------------------------------------------
# An implementation of a Drag & Drop source for CF_HDROP (file) data.
# ------------------------------------------------------------------------------
class ZFileDnDSource(ZDnDSource):

    def __init__(self, file):
        ZDnDSource.__init__(self, IZDnDSource.TYPE_FILE, file)
    # end __init__()

# end ZFileDnDSource


# ------------------------------------------------------------------------------
# An implementation of a Drag & Drop source for CF_HTML data whose top level
# xhtml element is an anchor tag with an href attr (link).
# ------------------------------------------------------------------------------
class ZLinkDnDSource(ZDnDSource):

    def __init__(self, link):
        ZDnDSource.__init__(self, IZDnDSource.TYPE_LINK, link)
    # end __init__()

# end ZLinkDnDSource


# ------------------------------------------------------------------------------
# An implementation of a Drag & Drop source for CF_HTML data whose top level
# xhtml element is an img tag.
# ------------------------------------------------------------------------------
class ZImageDnDSource(ZDnDSource):

    def __init__(self, img):
        ZDnDSource.__init__(self, IZDnDSource.TYPE_IMG, img)
    # end __init__()

# end ZImageDnDSource


# ------------------------------------------------------------------------------
# An implementation of a Drag & Drop source for CF_HTML data whose top level
# xhtml element is any html element.
# ------------------------------------------------------------------------------
class ZHtmlDnDSource(ZDnDSource):

    def __init__(self, html):
        ZDnDSource.__init__(self, IZDnDSource.TYPE_HTML, html)
    # end __init__()

# end ZHtmlDnDSource


# ------------------------------------------------------------------------------
# An implementation of a Drag & Drop source for CF_URL data.  The data is 
# simply the URL.
# ------------------------------------------------------------------------------
class ZUrlDnDSource(ZDnDSource):

    def __init__(self, url):
        ZDnDSource.__init__(self, IZDnDSource.TYPE_URL, url)
    # end __init__()

# end ZUrlDnDSource
