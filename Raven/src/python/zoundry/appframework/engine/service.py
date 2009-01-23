
# ------------------------------------------------------------------------------
# This is the interface for all Zoundry Services.  
# ------------------------------------------------------------------------------
class IZService:

    def start(self, applicationModel):
        u"Called by the Engine to start the service." #$NON-NLS-1$
    # end start()

    def stop(self):
        u"Called by the Engine to stop the service." #$NON-NLS-1$
    # end stop()

# end IZService
