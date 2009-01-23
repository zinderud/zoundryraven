from zoundry.appframework.engine.service import IZService

# ------------------------------------------------------------------------------
# Interface for the crash recovery service.  The blog post editor uses this
# service to periodically save snapshots of its content (when dirty).  The
# snapshots are deleted when the editor's content is saved.  On startup, this
# service should make available any previous snapshots so that they can be
# recovered by the user.  If a snapshot exists on startup, it means that the
# application crashed and some work needs to be recovered.
# ------------------------------------------------------------------------------
class IZCrashRecoveryService(IZService):

    def takeRecoverySnapshot(self, document):
        u"""takeRecoverySnapshot(IZDocument) -> None
        Takes a snapshot of a document for the purposes of recovery.  Note
        that only a single snapshot will be saved for any given in-progress
        document.  This mapping is made either by document ID (if one exists)
        or python id() of the document instance.""" #$NON-NLS-1$
    # end taskRecoverySnapshot()

    def clearRecoverySnapshot(self, document = None):
        u"""clearRecoverySnapshots(IZDocument) -> None
        Deletes any snapshots associated with the given document (note
        that there should be only one).  This method is typically called
        when a document is saved or discarded - at that point, there is
        no longer a need for a recovery snapshot of the document.""" #$NON-NLS-1$
    # end clearRecoverySnapshot()

    def getRecoverySnapshots(self):
        u"""getRecoverySnapshots() -> IZDocument[]
        Gets a list of recovered documents.  This method is typically only
        called during startup to determine if the application needs to
        recover any work that was lost due to a crash.""" #$NON-NLS-1$
    # end getRecoverySnapshots()

# end IZCrashRecoveryService
