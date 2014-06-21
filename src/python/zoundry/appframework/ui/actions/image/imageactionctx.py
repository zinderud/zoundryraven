from zoundry.appframework.ui.actions.menuaction import ZMenuActionContext


# ------------------------------------------------------------------------------
# Image action context.
# ------------------------------------------------------------------------------
class ZImageActionContext(ZMenuActionContext):

    def __init__(self, window, imageUrl):
        self.imageUrl = imageUrl
        ZMenuActionContext.__init__(self, window)
    # end __init__()

    def getUrl(self):
        return self.imageUrl
    # end getUrl()

# end ZImageActionContext

# ------------------------------------------------------------------------------
# Image action context based on image IDO object
# ------------------------------------------------------------------------------
class ZImageIDOActionContext(ZImageActionContext):

    def __init__(self, window, imageIDO):
        self.imageIDO = imageIDO
        ZImageActionContext.__init__(self, window, imageIDO.getUrl())
    # end __init__()

    def getImageIDO(self):
        return self.imageIDO
    # end getImageIDO()
# end ZImageIDOActionContext