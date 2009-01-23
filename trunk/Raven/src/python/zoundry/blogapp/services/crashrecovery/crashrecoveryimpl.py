from zoundry.base.util.fileutil import deleteDirectory
from zoundry.base.util.fileutil import deleteFile
from zoundry.blogapp.constants import IZBlogAppServiceIDs
from zoundry.blogapp.services.crashrecovery.crashrecovery import IZCrashRecoveryService
from zoundry.blogapp.services.datastore.io.factory import ZDocumentSerializerFactory
from zoundry.base.util.fileutil import getDirectoryListing
from zoundry.blogapp.services.datastore.io.factory import ZDocumentDeserializerFactory
from zoundry.base.zdom.dom import ZDom
from zoundry.blogapp.services.datastore.io.factory import ZBlogDocumentSerializationContext
import os

# ------------------------------------------------------------------------------
# Concrete implementation of the crash recovery service.
# ------------------------------------------------------------------------------
class ZCrashRecoveryService(IZCrashRecoveryService):

    def __init__(self):
        self.logger = None
        self.recoveryDir = None
    # end __init__()

    def start(self, applicationModel):
        userProfile = applicationModel.getUserProfile()
        self.recoveryDir = userProfile.getDirectory(u"recovery") #$NON-NLS-1$

        engine = applicationModel.getEngine()
        self.logger = engine.getService(IZBlogAppServiceIDs.LOGGER_SERVICE_ID)
        self.logger.debug(u"Crash Recovery Service started.") #$NON-NLS-1$
    # end start()

    def stop(self):
        self.logger = None
        self.recoveryDir = None
    # end stop()

    def takeRecoverySnapshot(self, document):
        self.logger.debug(u"Taking a snapshot of document.") #$NON-NLS-1$
        try:
            docSerializer = ZDocumentSerializerFactory().getSerializer()
            context = ZBlogDocumentSerializationContext(self.recoveryDir)
            documentDom = docSerializer.serialize(document, context)
            snapshotFile = self._getSnapshotFileName(document)
            documentDom.save(snapshotFile, True)
            self.logger.debug(u"Snapshot taken.") #$NON-NLS-1$
        except Exception, e:
            self.logger.exception(e)
    # end taskRecoverySnapshot()

    def clearRecoverySnapshot(self, document = None):
        if document is None:
            self._clearAllSnapshots()
        else:
            snapshotFile = self._getSnapshotFileName(document)
            deleteFile(snapshotFile)
        self.logger.debug(u"Recovery snapshot cleared.") #$NON-NLS-1$
    # end clearRecoverySnapshot()

    def getRecoverySnapshots(self):
        return self._loadSnapshots()
    # end getRecoverySnapshots()

    def _loadSnapshots(self):
        self.logger.debug(u"Loading recovery snapshots.") #$NON-NLS-1$
        snapshotFiles = getDirectoryListing(self.recoveryDir)
        snapshots = []

        for snapshotFile in snapshotFiles:
            documentDom = ZDom()
            documentDom.load(snapshotFile)
            namespace = documentDom.documentElement.getNamespaceUri()
            docDeserializer = ZDocumentDeserializerFactory().getDeserializer(namespace)
            context = ZBlogDocumentSerializationContext(self.recoveryDir)
            document = docDeserializer.deserialize(documentDom, context)
            snapshots.append(document)
            self.logger.debug(u"Recovery snapshot loaded.") #$NON-NLS-1$

        return snapshots
    # end _loadSnapshots()

    def _getDocumentId(self, document):
        documentId = document.getId()
        if documentId is None:
            documentId = id(document)
        return documentId
    # end _getDocumentId()

    def _clearAllSnapshots(self):
        deleteDirectory(self.recoveryDir, False)
    # end _clearAllSnapshots()

    def _getSnapshotFileName(self, document):
        documentId = self._getDocumentId(document)
        return os.path.join(self.recoveryDir, u"snapshot_" + unicode(documentId) + u".xml") #$NON-NLS-1$ #$NON-NLS-2$
    # end _getSnapshotFileName()

# end ZCrashRecoveryService
