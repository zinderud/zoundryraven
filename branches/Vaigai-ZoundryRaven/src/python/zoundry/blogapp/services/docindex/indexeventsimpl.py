from zoundry.blogapp.services.docindex.indexevents import IZDocIndexDocumentEvent
from zoundry.blogapp.services.docindex.indexevents import IZDocIndexEvent
from zoundry.blogapp.services.docindex.indexevents import IZDocIndexImageEvent
from zoundry.blogapp.services.docindex.indexevents import IZDocIndexLinkEvent
from zoundry.blogapp.services.docindex.indexevents import IZDocIndexTagEvent

# ------------------------------------------------------------------------------
# The base implementation for docindex events.
# ------------------------------------------------------------------------------
class ZDocIndexEvent(IZDocIndexEvent):

    def __init__(self, eventType, dataType):
        self.eventType = eventType
        self.dataType = dataType
    # end __init__()

    def getEventType(self):
        return self.eventType
    # end getEventType()

    def getDataType(self):
        return self.dataType
    # end getDataType()

# end ZDocIndexEvent


# ------------------------------------------------------------------------------
# The implementation for document index events.
# ------------------------------------------------------------------------------
class ZDocIndexDocumentEvent(ZDocIndexEvent, IZDocIndexDocumentEvent):

    def __init__(self, eventType, documentIDO):
        ZDocIndexEvent.__init__(self, eventType, IZDocIndexEvent.DOCINDEX_DATATYPE_DOCUMENT)
        self.documentIDO = documentIDO
    # end __init__()

    def getDocumentIDO(self):
        return self.documentIDO
    # end getDocumentIDO()

# end ZDocIndexDocumentEvent


# ------------------------------------------------------------------------------
# A document add event implementation.
# ------------------------------------------------------------------------------
class ZDocIndexDocumentAddEvent(ZDocIndexDocumentEvent):
    
    def __init__(self, documentIDO):
        ZDocIndexDocumentEvent.__init__(self, IZDocIndexEvent.DOCINDEX_EVENTTYPE_ADD, documentIDO)
    # end __init__()

# end ZDocIndexDocumentAddEvent


# ------------------------------------------------------------------------------
# A document removed event implementation.
# ------------------------------------------------------------------------------
class ZDocIndexDocumentRemoveEvent(ZDocIndexDocumentEvent):

    def __init__(self, documentIDO):
        ZDocIndexDocumentEvent.__init__(self, IZDocIndexEvent.DOCINDEX_EVENTTYPE_REMOVE, documentIDO)
    # end __init__()

# end ZDocIndexDocumentRemoveEvent


# ------------------------------------------------------------------------------
# The implementation for image index events.
# ------------------------------------------------------------------------------
class ZDocIndexImageEvent(ZDocIndexEvent, IZDocIndexImageEvent):

    def __init__(self, eventType, imageIDO):
        ZDocIndexEvent.__init__(self, eventType, IZDocIndexEvent.DOCINDEX_DATATYPE_IMAGE)
        self.imageIDO = imageIDO
    # end __init__()

    def getImageIDO(self):
        return self.imageIDO
    # end getImageIDO()

# end ZDocIndexImageEvent


# ------------------------------------------------------------------------------
# An image add event implementation.
# ------------------------------------------------------------------------------
class ZDocIndexImageAddEvent(ZDocIndexImageEvent):
    
    def __init__(self, imageIDO):
        ZDocIndexImageEvent.__init__(self, IZDocIndexEvent.DOCINDEX_EVENTTYPE_ADD, imageIDO)
    # end __init__()

# end ZDocIndexImageAddEvent


# ------------------------------------------------------------------------------
# An image remove event implementation.
# ------------------------------------------------------------------------------
class ZDocIndexImageRemoveEvent(ZDocIndexImageEvent):
    
    def __init__(self, imageIDO):
        ZDocIndexImageEvent.__init__(self, IZDocIndexEvent.DOCINDEX_EVENTTYPE_REMOVE, imageIDO)
    # end __init__()

# end ZDocIndexImageRemoveEvent


# ------------------------------------------------------------------------------
# The implementation for tag index events.
# ------------------------------------------------------------------------------
class ZDocIndexTagEvent(ZDocIndexEvent, IZDocIndexTagEvent):

    def __init__(self, eventType, tagIDO):
        ZDocIndexEvent.__init__(self, eventType, IZDocIndexEvent.DOCINDEX_DATATYPE_TAG)
        self.tagIDO = tagIDO
    # end __init__()

    def getTagIDO(self):
        return self.tagIDO
    # end getTagIDO()

# end ZDocIndexTagEvent


# ------------------------------------------------------------------------------
# An tag add event implementation.
# ------------------------------------------------------------------------------
class ZDocIndexTagAddEvent(ZDocIndexTagEvent):
    
    def __init__(self, tagIDO):
        ZDocIndexTagEvent.__init__(self, IZDocIndexEvent.DOCINDEX_EVENTTYPE_ADD, tagIDO)
    # end __init__()
# end ZDocIndexTagAddEvent

# ------------------------------------------------------------------------------
# An tag remove event implementation.
# ------------------------------------------------------------------------------
class ZDocIndexTagRemoveEvent(ZDocIndexTagEvent):
    
    def __init__(self, tagIDO):
        ZDocIndexTagEvent.__init__(self, IZDocIndexEvent.DOCINDEX_EVENTTYPE_REMOVE, tagIDO)
    # end __init__()
# end ZDocIndexTagRemoveEvent

# ------------------------------------------------------------------------------
# The implementation for link index events.
# ------------------------------------------------------------------------------
class ZDocIndexLinkEvent(ZDocIndexEvent, IZDocIndexLinkEvent):

    def __init__(self, eventType, linkIDO):
        ZDocIndexEvent.__init__(self, eventType, IZDocIndexEvent.DOCINDEX_DATATYPE_LINK)
        self.linkIDO = linkIDO
    # end __init__()

    def getLinkIDO(self):
        return self.linkIDO
    # end getLinkIDO()

# end ZDocIndexLinkEvent


# ------------------------------------------------------------------------------
# An link add event implementation.
# ------------------------------------------------------------------------------
class ZDocIndexLinkAddEvent(ZDocIndexLinkEvent):
    
    def __init__(self, linkIDO):
        ZDocIndexLinkEvent.__init__(self, IZDocIndexEvent.DOCINDEX_EVENTTYPE_ADD, linkIDO)
    # end __init__()

# end ZDocIndexLinkAddEvent


# ------------------------------------------------------------------------------
# An image add event implementation.
# ------------------------------------------------------------------------------
class ZDocIndexLinkRemoveEvent(ZDocIndexLinkEvent):
    
    def __init__(self, linkIDO):
        ZDocIndexLinkEvent.__init__(self, IZDocIndexEvent.DOCINDEX_EVENTTYPE_REMOVE, linkIDO)
    # end __init__()

# end ZDocIndexLinkRemoveEvent
