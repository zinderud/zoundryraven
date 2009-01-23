
# ------------------------------------------------------------------------------
# Describes product + merchant information
# ------------------------------------------------------------------------------
class ZProductMetaData:

    def __init__(self, productUrl, productSku, merchant):
        self.url = productUrl
        # sku, amazon asin etc.
        self.sku = productSku
        # vendor selling the product.
        self.merchant = merchant
    #end __init__()

    def getUrl(self):
        return self.url
    # end getUrl()

    def getSku(self):
        return self.sku
    # end getSku()

    def getMerchant(self):
        u"""getMerchant() -> ZMerchant
        """ #$NON-NLS-1$
        return self.merchant
    # end getMerchant()
# end end ZProductMetaData

# ------------------------------------------------------------------------------
# Product url regular expression matcher.
# ------------------------------------------------------------------------------
class ZProductUrlRegularExpression:

    def __init__(self, regularExpression, groupId1, groupId2):
        self.regularExpression = regularExpression
        self.groupId1 = groupId1
        self.groupId2 = groupId2
    #end __init__()

    def getExpression(self):
        return self.regularExpression
    # end getExpression()

    def getGroupId1(self):
        return self.groupId1
    # end getGroupId1()

    def getGroupId2(self):
        return self.groupId2
    # end getGroupId2()

# end ZProductUrlRegularExpression
