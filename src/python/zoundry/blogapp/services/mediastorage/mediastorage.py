
# -----------------------------------------------------------------------------------
# A media storage upload listener is used to listen to the events associated with the
# upload of a single file using a media storage.
# -----------------------------------------------------------------------------------
class IZMediaStorageUploadListener:

    def onUploadStarted(self, fileName, totalBytes):
        u"Called when an upload has started." #$NON-NLS-1$
    # end onUploadStarted()

    def onUploadChunk(self, fileName, chunkBytes):
        u"Called when a chunk of the file has been uploaded." #$NON-NLS-1$
    # end onUploadChunk()

    def onUploadFailed(self, fileName, exception):
        u"Called when an upload fails for some reason." #$NON-NLS-1$
    # end onUploadFailed()

    def onUploadComplete(self, fileName):
        u"Called when the upload is finished." #$NON-NLS-1$
    # end onUploadComplete()

# end IZMediaStorageUploadListener


# -----------------------------------------------------------------------------------
# The interface that must be implemented by all media storage classes.
# -----------------------------------------------------------------------------------
class IZMediaStorage:

    def getId(self):
        u"Returns the media uploader's ID." #$NON-NLS-1$
    # end getId()

    def getName(self):
        u"Returns the (user supplied) name of the uploader." #$NON-NLS-1$
    # end getName()

    def getMediaSiteId(self):
        u"Returns the media site id of the site associated with this store." #$NON-NLS-1$
    # end getMediaSiteId()

    def getProperties(self):
        u"Returns the uploader's properties (python map of properties)." #$NON-NLS-1$
    # end getProperties()

    def getCapabilities(self):
        u"Returns the set of IZMediaStorageCapabilities for this media storage." #$NON-NLS-1$
    # end getCapabilities()

    def upload(self, fileName, listener, bypassRegistry = False):
        u"""upload(string, IZMediaStorageUploadListener, boolean) -> IZUploadResponse
        Uploads the given file (sends upload events to the given listener).  Returns the 
        upload result associated with the uploaded file.""" #$NON-NLS-1$
    # end upload()

    def delete(self, fileName):
        u"Called to delete the file from the remote location." #$NON-NLS-1$
    # end delete()

    def listFiles(self, relativePath = None):
        u"Called to list the files at the remote location.  To get the root list, pass None." #$NON-NLS-1$
    # end listFiles()
    
    def supportsFile(self, fileName): #@UnusedVariable
        u"""Returns true of the media storage supports the given file (based on capabilities).
        For example, image files can be uploaded to most sites, but movie files cannot be
        uploaded to image hosting sites such as Flikr and Picasa.
        """ #$NON-NLS-1$
    # end supportsFile

# end IZMediaStorage
