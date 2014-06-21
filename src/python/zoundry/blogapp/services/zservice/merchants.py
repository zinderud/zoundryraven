from zoundry.base.util.urlutil import encodeUri
from zoundry.base.util.text.textutil import getNoneString
import re

# ------------------------------------------------------------------------------
# Describes product merchant.
# ------------------------------------------------------------------------------
class ZMerchantInfo:

    def __init__(self, id, merchantId, url, name, enabled, regExpressionList):
        # string id - uri. e.g. www.amazon.com
        self.id = id
        # zservice db id (int)
        self.merchantId = merchantId
        self.url = url
        self.name = name
        self.enabled = enabled
        self.regExpressionList = regExpressionList
    # end __init__

    def getId(self):
        return self.id
    # getId()

    def getName(self):
        return self.name
    # end getName()

    def getUrl(self):
        return self.url
    # end getUrl()

    def isEnabled(self):
        return self.enabled
    # end isEnabled()

    def getRegExpressionList(self):
        return self.regExpressionList
    # end getRegExpressionList()
# end ZMerchantInfo

# ------------------------------------------------------------------------------
# Contains list of merchants.
# ------------------------------------------------------------------------------
class ZMerchantRegistry:

    def __init__(self, merchants = []):
        self.merchants = merchants
    # end __init__()

    def add(self, merchant):
        self.merchants.append(merchant)
    # end add()

    def getSize(self):
        return len(self.merchantsMap)
    # end getSize()

    def getMerchants(self):
        return self.merchants
    # end getMerchants

    def getMerchantById(self, id):
        for merchant in self.merchants:
            if merchant.getId() == id:
                return merchant
        return None
    # end getMerchantById()
# end ZMerchantRegistry


#----------------------------------------------------------------------------------------------
# Affiliate link creation provider
#----------------------------------------------------------------------------------------------
class IZAffiliateLinkProvider:

    def createAffiliateLink(self, productUrl, sku, zoundryId):
        u"""createAffiliateLink(string, string, string) -> string
        Returns an affiate link.
        """ #$NON-NLS-1$

    # end createAffiliateLink()

# end class IZAffiliateLinkProvider


#----------------------------------------------------------------------------------------------
# Util class used to match Amazon ASIN
#----------------------------------------------------------------------------------------------
class ZCommisionJunctionProvider:

    def __init__(self):
        pass
    # end __init__

    def createAffiliateLink(self, productUrl, sku, zoundryId): #@UnusedVariable
        zoundryId = getNoneString(zoundryId)
        if not zoundryId:
            zoundryId = u"zoundry-0" #$NON-NLS-1$
        productUrl = encodeUri(productUrl)
        return u"http://www.kqzyfj.com/click-1670306-10388132?sid=%s&url=%s" % (zoundryId, productUrl)#$NON-NLS-1$
    # end createAffiliateLink()

# end ZCommisionJunctionProvider()


#----------------------------------------------------------------------------------------------
# Util class used to match Amazon ASIN
#----------------------------------------------------------------------------------------------
class ZAmazonProvider:

    def __init__(self):
        #
        # Amazon URL Eg:
        # 1. http://www.amazon.com/exec/obidos/tg/detail/-/0446532681/ref=pd_ts_tb_2/103-2983607-5273457?v=glance&s=books&n=283155
        # 2. http://www.amazon.com/exec/obidos/ASIN/B000634DCC/ref=nosim/pjsnet09-20
        # 3. http://www.amazon.com/exec/obidos/tg/stores/detail/-/books/0312307047/reviews/102-0387682-3029720#03123070477299
        # 4. http://www.amazon.com/exec/obidos/am/102-4178221-7691369?p=tg%2Fdetail%2F%2D%2FB0002ZAILY%2Fref%3Dpd%5Fnfy%
        # 4. http://www.amazon.com/exec/obidos/am/102-4178221-7691369?p=ASIN%2FB0003RA29O%2Fref%3Damb%5Fcenter%2D4
        amazon1 = r"(http://www.amazon.com/exec/obidos/tg/detail/-/)(\w+)(/.*)" #$NON-NLS-1$
        amazon2 = r"(http://www.amazon.com/exec/obidos/ASIN/)(\w+)(/.*)*" #$NON-NLS-1$
        amazon3 =  r"(http://www.amazon.com/exec/obidos/tg/stores/detail/-/)(\w+/)(\w+)(/.*)*" #$NON-NLS-1$
        amazon4 = r"(http://www.amazon.com)(/.*)*((detail/-/)|(.ASIN/))(\w+)(/.*)*" #$NON-NLS-1$
        self.reAmazonPattern1 = re.compile(amazon1,re.IGNORECASE)
        self.reAmazonPattern2 = re.compile(amazon2,re.IGNORECASE)
        self.reAmazonPattern3 = re.compile(amazon3,re.IGNORECASE)
        self.reAmazonPattern4 = re.compile(amazon4,re.IGNORECASE)
    # end __init()__

    def getAsinFromUrl(self, productUrl):
        return self._extractAmazonAsin(productUrl)
    # end getAsinFromUrl()

    def createAffiliateLink(self, productUrl, sku, zoundryId): #@UnusedVariable
        return self._createAmazonAssociateLink(productUrl, sku, u"zoundry0b-20") #$NON-NLS-1$
    # end createAffiliateLink()

    def _createAmazonAssociateLink(self, productUrl, asin, assoicateId):
        asin = getNoneString(asin)
        if asin:
            return u"http://www.amazon.com/exec/obidos/ASIN/%s/ref=nosim/%s" % (asin, assoicateId) #$NON-NLS-1$
        productUrl = getNoneString(productUrl)
        if not productUrl:
            return None
        productUrl = encodeUri(productUrl)
        return u"http://www.amazon.com/exec/obidos/redirect?tag=%s&path=%s" % (assoicateId, productUrl) #$NON-NLS-1$
    # end _createAffiliateLink()

    def _extractAmazonAsin(self, productUrl = u""): #$NON-NLS-1$
        result = self.reAmazonPattern1.findall(productUrl)
        if (result and len(result) > 0):
            return result[0][1]

        result = self.reAmazonPattern2.findall(productUrl)
        if (result and len(result) > 0):
            list = result[0]
            # make sure this is not already an affiliate link
            #if (not list[2] or list[2] == '/'):
            #    return list[1]
            return list[1]

        result = self.reAmazonPattern3.findall(productUrl)
        if (result and len(result) > 0):
            return result[0][2]

        result = self.reAmazonPattern4.findall(productUrl)
        if (result and len(result) > 0):
            return result[0][5]
        return None
    # end _getAmazonAsin()

# end ZAmazonProvider
