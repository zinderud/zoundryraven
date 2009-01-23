
# ------------------------------------------------------------------------------
# The return result of uploading a file to a media storage.
# ------------------------------------------------------------------------------
class IZUploadResponse:

    def getUrl(self):
        u"""getUrl() -> string
        Returns the URL of the uploaded file.""" #$NON-NLS-1$
    # end getUrl()

    def getEmbedFragment(self):
        u"""getFragment() -> ZElement
        Returns the 'embed' fragment of the uploaded file.  This
        will return None for most file types (images, etc), but
        it might return a valid ZElement for things like Videos.""" #$NON-NLS-1$
    # end getEmbedFragment()

    def hasEmbedFragment(self):
        u"""hasEmbedFragment() -> boolean
        Returns True if the response includes an 'embed' html fragment.""" #$NON-NLS-1$
    # end hasEmbedFragment()

    def getMetaData(self):
        u"""getMetaData() -> ZElement
        Returns any meta data associated with the upload.  This
        meta data might include information that the media storage
        provider requires to perform future operations.""" #$NON-NLS-1$
    # end getMetaData()

# end IZUploadResponse


# ------------------------------------------------------------------------------
# Implementation of a media storage upload response.
# ------------------------------------------------------------------------------
class ZUploadResponse(IZUploadResponse):

    def __init__(self, url = None, embedFragment = None, metaData = None):
        self.url = url
        self.embedFragment = embedFragment
        self.metaData = metaData
    # end __init__()

    def getUrl(self):
        return self.url
    # end getUrl()

    def setUrl(self, url):
        self.url = url
    # end setUrl()

    def getEmbedFragment(self):
        return self.embedFragment
    # end getEmbedFragment()

    def setEmbedFragment(self, embedFragment):
        self.embedFragment = embedFragment
    # end setEmbedFragment()

    def hasEmbedFragment(self):
        return self.embedFragment is not None
    # end hasEmbedFragment()

    def getMetaData(self):
        return self.metaData
    # end getMetaData()

    def setMetaData(self, metaData):
        self.metaData = metaData
    # end setMetaData()

# end ZUploadResponse
