
# ------------------------------------------------------------------------------
# This interface should be implemented by all listeners of the document index.
# ------------------------------------------------------------------------------
class IZDocumentIndexListener:

    def onIndexChange(self, event):
        u"This event is fired when the index changes." #$NON-NLS-1$
    # end onIndexChange()

# end IZDocumentIndexListener


# ------------------------------------------------------------------------------
# The base interface for docindex events.  All events fired by the index will
# implement (at least) this interface.
# ------------------------------------------------------------------------------
class IZDocIndexEvent:

    # Event types.
    DOCINDEX_EVENTTYPE_ADD = 0
    DOCINDEX_EVENTTYPE_REMOVE = 1
    DOCINDEX_EVENTTYPE_UPDATE = 2
    
    # Event data types.
    DOCINDEX_DATATYPE_DOCUMENT = 0
    DOCINDEX_DATATYPE_TAG = 1
    DOCINDEX_DATATYPE_IMAGE = 2
    DOCINDEX_DATATYPE_LINK = 3

    def getEventType(self):
        u"Returns the type of event (add, remove, update)." #$NON-NLS-1$
    # end getEventType()

    def getDataType(self):
        u"Returns the data type associated with this event (document, image, tag, etc...)." #$NON-NLS-1$
    # end getDataType()

# end IZDocIndexEvent


# ------------------------------------------------------------------------------
# The interface for document index events.  All events related to modifying 
# document IDO's will be of this type.
# ------------------------------------------------------------------------------
class IZDocIndexDocumentEvent(IZDocIndexEvent):

    def getDocumentIDO(self):
        u"Returns the data associated with this document event." #$NON-NLS-1$
    # end getDocumentIDO()

# end IZDocIndexDocumentEvent


# ------------------------------------------------------------------------------
# The interface for image index events.  All events related to modifying 
# image IDO's will be of this type.
# ------------------------------------------------------------------------------
class IZDocIndexImageEvent(IZDocIndexEvent):

    def getImageIDO(self):
        u"Returns the data associated with this image event." #$NON-NLS-1$
    # end getImageIDO()

# end IZDocIndexImageEvent


# ------------------------------------------------------------------------------
# The interface for tag index events.  All events related to modifying 
# document IDO's will be of this type.
# ------------------------------------------------------------------------------
class IZDocIndexTagEvent(IZDocIndexEvent):

    def getTagIDO(self):
        u"Returns the data associated with this tag event." #$NON-NLS-1$
    # end getTagIDO()

# end IZDocIndexTagEvent


# ------------------------------------------------------------------------------
# The interface for link index events.  All events related to modifying 
# document IDO's will be of this type.
# ------------------------------------------------------------------------------
class IZDocIndexLinkEvent(IZDocIndexEvent):

    def getLinkIDO(self):
        u"Returns the data associated with this link event." #$NON-NLS-1$
    # end getLinkIDO()

# end IZDocIndexLinkEvent
