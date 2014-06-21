from zoundry.appframework.engine.service import IZService


# ------------------------------------------------------------------------------
# Zoundry Service product and merchant services
# ------------------------------------------------------------------------------
class IZProductService(IZService):

    def listMerchants(self):
        u"""listMerchants() -> list
        Returns list of ZMerchantInfo""" #$NON-NLS-1$
    # end listMerchants()

    def findProductByUrl(self, productUrl):
        u"""findProductByUrl(string) -> ZProductMetaData
        Returns ZProductMetaData if a match is found or None otherwise.""" #$NON-NLS-1$
    # end findProductByUrl()

    def createZoundryAffiliateLink(self, productUrl):
        u"""createZoundryAffiliateLink(string) -> string
        Returns Zoundry donation jar affiliate link if the product and merchant 
        is supported or None otherwise.""" #$NON-NLS-1$
    # end createZoundryAffiliateLink()

    def convertProductLink(self, productUrl, zoundryServiceId):
        u"""convertProductLink(string, string) -> string
        Makes a web service call to the Zoundry service to convert
        a link from a product link into a Zoundry affiliate link.""" #$NON-NLS-1$
    # end convertProductLink()

# end IZProductService
