from zoundry.appframework.engine.service import IZService

# ------------------------------------------------------------------------------
# Interface for the auto-update service.
# ------------------------------------------------------------------------------
class IZAutoUpdateService(IZService):

    def checkForUpdate(self, onlyPromptWhenNewVersionIsAvailable = True):
        u"""checkForUpdate(boolean) -> None
        Called when the application wants to check for an application
        update.""" #$NON-NLS-1$
    # end checkForUpdate()

# end IZAutoUpdateService
