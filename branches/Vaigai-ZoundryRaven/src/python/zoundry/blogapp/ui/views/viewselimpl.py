from zoundry.blogapp.ui.views.viewsel import IZViewSelection
from zoundry.blogapp.ui.views.viewsel import IZViewSelectionTypes

# ------------------------------------------------------------------------------
# Implementation of a view selection.
# ------------------------------------------------------------------------------
class ZViewSelection(IZViewSelection):

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

# end ZViewSelection


# ------------------------------------------------------------------------------
# Implementation of ZViewSelection for selecting an image.
# ------------------------------------------------------------------------------
class ZImageSelection(ZViewSelection):

    def __init__(self, imageIDO, blog):
        ZViewSelection.__init__(self, IZViewSelectionTypes.IMAGE_SELECTION, (blog, imageIDO))
    # end __init__()

# end ZImageViewSelection


# ------------------------------------------------------------------------------
# Implementation of ZViewSelection for selecting a link.
# ------------------------------------------------------------------------------
class ZLinkSelection(ZViewSelection):

    def __init__(self, linkIDO, blog):
        ZViewSelection.__init__(self, IZViewSelectionTypes.LINK_SELECTION, (blog, linkIDO))
    # end __init__()

# end ZLinkSelection

# ------------------------------------------------------------------------------
# Implementation of ZViewSelection for selecting a tag.
# ------------------------------------------------------------------------------
class ZTagSelection(ZViewSelection):

    def __init__(self, tagIDO, blog):
        ZViewSelection.__init__(self, IZViewSelectionTypes.TAG_SELECTION, (blog, tagIDO))
    # end __init__()

# end ZTagSelection


# ------------------------------------------------------------------------------
# Implementation of ZViewSelection for when a document is selected.
# ------------------------------------------------------------------------------
class ZDocumentSelection(ZViewSelection):

    def __init__(self, document, blog):
        ZViewSelection.__init__(self, IZViewSelectionTypes.DOCUMENT_SELECTION, (blog, document))
    # end __init__()

# end ZDocumentSelection
