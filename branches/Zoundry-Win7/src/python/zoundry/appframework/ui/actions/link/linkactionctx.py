from zoundry.appframework.ui.actions.menuaction import ZMenuActionContext

# ------------------------------------------------------------------------------
# Link action context.
# ------------------------------------------------------------------------------
class ZLinkActionContext(ZMenuActionContext):
    
    def __init__(self, window, url):
        self.url = url
        ZMenuActionContext.__init__(self, window)
    # end __init__()
    
    def getUrl(self):
        return self.url
    # end getUrl()

# end ZLinkActionContext


# ------------------------------------------------------------------------------
# Link action context based on usig LinkIDO object
# ------------------------------------------------------------------------------
class ZLinkIDOActionContext(ZLinkActionContext):
    
    def __init__(self, window, linkIDO):
        self.linkIDO = linkIDO
        ZLinkActionContext.__init__(self, window, linkIDO.getUrl() )
    # end __init__()
    
    def getLinkIDO(self):
        return self.linkIDO
    # end getLinkIDO()

# end ZLinkIDOActionContext