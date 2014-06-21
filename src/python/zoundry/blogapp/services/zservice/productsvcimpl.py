from zoundry.appframework.constants import IZAppServiceIDs
from zoundry.base.net.http import ZSimpleXmlHTTPRequest
from zoundry.base.util.text.textutil import getNoneString
from zoundry.base.zdom.dom import ZDom
from zoundry.blogapp.services.zservice.merchants import ZAmazonProvider
from zoundry.blogapp.services.zservice.merchants import ZCommisionJunctionProvider
from zoundry.blogapp.services.zservice.merchants import ZMerchantInfo
from zoundry.blogapp.services.zservice.merchants import ZMerchantRegistry
from zoundry.blogapp.services.zservice.products import ZProductMetaData
from zoundry.blogapp.services.zservice.products import ZProductUrlRegularExpression
from zoundry.blogapp.services.zservice.productsvc import IZProductService
import re
import string

ADD_PRODUCT_ENDPOINT = u"http://www.zoundry.com/z/c/addproduct" #$NON-NLS-1$
ADD_PRODUCT_REQUEST = u"""<Request type="addproduct">

    <Authorization>
        <Username />
    </Authorization>

    <AddProducts version="1" creator="raven">
        <Product id="1" format="url">
            <Url />
        </Product>
    </AddProducts>

</Request>
""" #$NON-NLS-1$

# ------------------------------------------------------------------------------
# Zoundry Service product and merchant services
# ------------------------------------------------------------------------------
class ZProductService(IZProductService):

    def __init__(self):
        self.merchantRegistry = ZMerchantRegistry()
        self.amazonProvider = ZAmazonProvider()
        self.affiliateLinkProviders = {}
        self.affiliateLinkProviders[u"www.amazon.com"] = self.amazonProvider #$NON-NLS-1$
        self.affiliateLinkProviders[u"www.buy.com"] = ZCommisionJunctionProvider() #$NON-NLS-1$
    # end __init()__

    def _getMerchantRegistry(self):
        return self.merchantRegistry
    # end _getMerchantRegistry()

    def start(self, applicationModel):
        self.logger = applicationModel.getEngine().getService(IZAppServiceIDs.LOGGER_SERVICE_ID)
        self.applicationModel = applicationModel
        self._loadMerchantRegistry()
    # end start

    def listMerchants(self):
        u"""listMerchants() -> list
        Returns list of ZMerchantInfo
        """ #$NON-NLS-1$
        return self._getMerchantRegistry().getMerchants()
    # end listMerchants

    def findProductByUrl(self, productUrl): #@UnusedVariable
        u"""findProductByUrl(string) -> ZProductMetaData
        Returns ZProductMetaData if a match is found or None otherwise.
        """ #$NON-NLS-1$
        productUrl = getNoneString(productUrl)
        if not productUrl:
            return None
        merchantInfo = None
        # check for Amazon ASIN match (todo: move this code to a regular expression within a merchant config).
        sku = self.amazonProvider.getAsinFromUrl(productUrl)
        if sku:
            merchantInfo = self._getMerchantRegistry().getMerchantById(u"www.amazon.com") #$NON-NLS-1$
        else:
            (sku, merchantInfo) = self._findSkuAndMerchant(productUrl)
        if merchantInfo:
            return ZProductMetaData(productUrl, sku, merchantInfo)
        return None
    # end findProductByUrl()

    def createZoundryAffiliateLink(self, productUrl): #@UnusedVariable
        u"""createZoundryAffiliateLink(string) -> string
        Returns Zoundry donation jar affiliate link if the product and merchant
        is supported or None otherwise.""" #$NON-NLS-1$
        # hard code test amazon.com for donation jar
        amazon = productUrl and productUrl.startswith(u"http://www.amazon.com") and not productUrl.startswith(u"http://www.amazon.com/exec/obidos/redirect?") #$NON-NLS-1$ #$NON-NLS-2$
        prodMetaData = self.findProductByUrl(productUrl)

        if (not prodMetaData or not prodMetaData.getMerchant() ) and not amazon:
            return None
        sku = None
        if prodMetaData:
            merchantInfo = prodMetaData.getMerchant()
            sku = prodMetaData.getSku()
        elif amazon: #$NON-NLS-1$
            # hard code amazon.com for donation jar
            merchantInfo = self._getMerchantRegistry().getMerchantById(u"www.amazon.com") #$NON-NLS-1$

        if not merchantInfo:
            return None
        if not self.affiliateLinkProviders.has_key( merchantInfo.getId() ):
            return None
        provider = self.affiliateLinkProviders[ merchantInfo.getId() ]
        link = provider.createAffiliateLink(productUrl, sku, None)
        return link
    # end createZoundryAffiliateLink

    def _findSkuAndMerchant(self, productUrl):
        rMerchant = None
        rSku = None
        for merchantInfo in self._getMerchantRegistry().getMerchants():
            if not merchantInfo.isEnabled():
                continue
            for productUrlRegularExpression in merchantInfo.getRegExpressionList():
                results = productUrlRegularExpression.getExpression().findall(productUrl);
                if results and len(results) > 0:
                    if productUrlRegularExpression.getGroupId1() > -1:
                        rSku = results[0][productUrlRegularExpression.getGroupId1()]
                    rMerchant = merchantInfo
                    break
        return (rSku, rMerchant)
    # end _findSkuAndMerchant

    def _loadMerchantRegistry(self):
        resourceReg = self.applicationModel.getResourceRegistry()
        merchantsXMLPath = resourceReg.getResourcePath(u"zservice/merchants.xml") #$NON-NLS-1$
        dom = ZDom()
        dom.load(merchantsXMLPath)
        nodeList = dom.selectNodes(u"//Merchants/Merchant") #$NON-NLS-1$
        if not nodeList:
            return
        for node in nodeList:
            merchant = self._createMerchant(node)
            if merchant:
                self.merchantRegistry.add(merchant)
    # end _loadMerchantRegistry()

    def _createMerchant(self, node):
        menableStr = getNoneString(node.getAttribute(u"enabled")) #$NON-NLS-1$
        menable = False
        if menableStr and (menableStr == u"yes" or menableStr == u"true"): #$NON-NLS-1$ #$NON-NLS-2$
            menable = True
        if not menable:
            return None
        merchantId = node.getAttribute(u"mid") #$NON-NLS-1$
        name = node.getAttribute(u"name") #$NON-NLS-1$
        url = node.getAttribute(u"website") #$NON-NLS-1$
        id = node.getAttribute(u"uri") #$NON-NLS-1$
        regExpressionList = self._createRegExprList(node)
        merchant = ZMerchantInfo(id, merchantId, url, name, True, regExpressionList)
        return merchant
    # end _createMerchant()

    def _createRegExprList(self, merchantNode):
        reListNode = merchantNode.selectSingleNode(u"ReList") #$NON-NLS-1$
        if not reListNode:
            return []
        reEnableStr = getNoneString(reListNode.getAttribute(u"enabled")) #$NON-NLS-1$
        reEnable = False
        if reEnableStr and (reEnableStr == u"yes" or reEnableStr == u"true"): #$NON-NLS-1$ #$NON-NLS-2$
            reEnable = True
        if not reEnable:
            return []
        # get regular expression list
        reNodes = reListNode.selectNodes(u"Re") #$NON-NLS-1$
        if not reNodes:
            return []
        regExprList = []
        for reNode in reNodes:
            groupId1 = self._parseGroupId( reNode.getAttribute(u"group") ) #$NON-NLS-1$
            groupId2 = self._parseGroupId( reNode.getAttribute(u"group2") ) #$NON-NLS-1$
            reText = getNoneString( reNode.getText() )
            if reText and groupId1 >= 0:
                rePattern = re.compile(reText,re.IGNORECASE);
                prodExpr = ZProductUrlRegularExpression(rePattern, groupId1, groupId2)
                regExprList.append(prodExpr )
        return regExprList
    # end _createRegExprList()

    def _parseGroupId(self, groupIdStr):
        groupId = -1
        if groupIdStr and groupIdStr != u"-1": #$NON-NLS-1$
            try:
                groupId = string.atoi(groupIdStr) - 1
            except:
                pass
        return groupId
    # end _parseGroupId()

    def convertProductLink(self, productUrl, zoundryServiceId):
        postData = self._getAddProductPostDataForUrl(productUrl, zoundryServiceId)
        headers = {
            u"Content-Type" : u"text/xml", #$NON-NLS-2$ #$NON-NLS-1$
            u"Content-Length" : u"%d" % len(postData) #$NON-NLS-1$ #$NON-NLS-2$
        }
        request = ZSimpleXmlHTTPRequest(ADD_PRODUCT_ENDPOINT, headers, True)
        if request.send(postData):
            dom = request.getResponse()
            respCode = dom.selectSingleNodeText(u"/Response/Status/Code") #$NON-NLS-1$
            if respCode == u"200": #$NON-NLS-1$
                return dom.selectSingleNodeText(u"/Response/AddProductsResponse/Product/ProxyUrl").strip() #$NON-NLS-1$
        return None
    # end convertProductLink()

    def _getAddProductPostDataForUrl(self, productUrl, zoundryServiceId):
        dom = ZDom(ADD_PRODUCT_REQUEST)
        dom.selectSingleNode(u"/Request/Authorization/Username").setText(zoundryServiceId) #$NON-NLS-1$
        dom.selectSingleNode(u"/Request/AddProducts/Product/Url").setText(productUrl) #$NON-NLS-1$
        return dom.serialize(True)
    # end _getAddProductPostDataForUrl()

# end ZProductService
