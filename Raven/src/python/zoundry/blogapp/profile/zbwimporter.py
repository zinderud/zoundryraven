from zoundry.appframework.util import crypt
from zoundry.appframework.util.osutilfactory import getOSUtil
from zoundry.base.exceptions import ZException
from zoundry.base.util import fileutil
from zoundry.base.util.schematypes import ZSchemaDateTime
from zoundry.base.util.text.textutil import getNoneString
from zoundry.base.util.text.unicodeutil import convertToUnicode
from zoundry.base.zdom.dom import ZDom
from zoundry.blogapp.constants import IZBlogAppNamespaces
from zoundry.blogapp.constants import PASSWORD_ENCRYPTION_KEY
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.profile.importer import ZAbstractProfileImporter
from zoundry.blogapp.services.pubsystems.publisher import ZQualifiedPublisherId
from zoundry.blogapp.services.pubsystems.sitenames import DefaultSites
import os
import re

ACCOUNT_NSS_MAP = { u"zns" : IZBlogAppNamespaces.RAVEN_ACCOUNT_NAMESPACE } #$NON-NLS-1$
DOCUMENT_NSS_MAP = { u"zns" : IZBlogAppNamespaces.RAVEN_DOCUMENT_NAMESPACE } #$NON-NLS-1$
ZBW_PERSONAL_DICTIONARY_NSS_MAP = { u"pd" : u"http://www.zoundry.com/schemas/2005/10/personal-dictionary.xsd" } #$NON-NLS-1$ #$NON-NLS-2$
RAVEN_SPELLCHECK_NSS_MAP = { u"spl" : IZBlogAppNamespaces.RAVEN_SPELLCHECKER_NAMESPACE } #$NON-NLS-1$


def getZBWProfilePath():
    import _winreg
    try:
        handle = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, u"Software\\Zoundry Blog Writer") #$NON-NLS-1$
        installPath = _winreg.QueryValueEx(handle, u"Path")[0] #$NON-NLS-1$
        if not installPath:
            return None
        userName = getOSUtil().getCurrentUserName()
        path = os.path.join(installPath, u"users", userName) #$NON-NLS-1$
        _winreg.CloseKey(handle)
        return path
    except:
        return None
# end getZBWProfilePath()


def isZoundryBlogWriterInstalled():
    import _winreg
    try:
        handle = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, u"Software\\Zoundry Blog Writer") #$NON-NLS-1$
        _winreg.CloseKey(handle)
        return True
    except:
        return None
# end getZBWProfilePath()


# ----------------------------------------------------------------------------
# Base class representing profile for Zoundry Blog Writer.
# ----------------------------------------------------------------------------
class ZAbstractZBWProfileImporter(ZAbstractProfileImporter):

    def __init__(self, pathToJoeyProfile, pathToRavenProfile, systemProfile):
        self.pathToJoeyProfile = pathToJoeyProfile
        ZAbstractProfileImporter.__init__(self, pathToJoeyProfile, pathToRavenProfile, systemProfile)
    # end __init__()

    def _getJoeyUserConfigDom(self):
        try:
            configFile = os.path.join(self.pathToSourceProfile, u"joey-user-config.xml") #$NON-NLS-1$
            dom = ZDom()
            dom.load(configFile)
            return dom
        except:
            return None
    # end _getJoeyUserConfigDom()

# end ZAbstractZBWProfileImporter


# ----------------------------------------------------------------------------
# This class is a Runnable that is responsible for importing a Zoundry Blog
# Writer 1.x profile into a Zoundry Raven profile.  It does this by copying
# all of the data
#
# FIXME (PJ) Import spell check settings including custom/user dictionary
# FIXME (PJ) find bottle neck when importing DEV profile.
# FIXME (PJ) convert Typepad Atom 0.3 -> Typepad xml-rpc
# FIXME (PJ) import media storages
# FIXME (PJ) import per blog media storage settings (ftp or blog), create media storage if needed and do zblog.setUploadMethod(..), zblog.setUploadStoreId(...)
# FIXME (PJ) import media storage registry file and split into on a per store basis.
# ----------------------------------------------------------------------------
class ZBlogWriterProfileImporter(ZAbstractZBWProfileImporter):

    def __init__(self, pathToJoeyProfile, pathToRavenProfile, systemProfile):
        ZAbstractZBWProfileImporter.__init__(self, pathToJoeyProfile, pathToRavenProfile, systemProfile)
        self.pathToJoeyProfile = pathToJoeyProfile
        self.dataTransformFilename = systemProfile.getTransform(u"zbw2raven_jbe.xsl") #$NON-NLS-1$
        self.accountTransformFilename = systemProfile.getTransform(u"zbw2raven_acct.xsl") #$NON-NLS-1$
        self.accountDirList = self._getAccountDirList()
        self.dataFileList = self._getDataFileList()
        self.validAccounts = {}
        self.validBlogs = {}
    # end __init__()

    def _hasAccount(self, ravenAccountId):
        if ravenAccountId and self.validAccounts.has_key(ravenAccountId):
            return True
        else:
            return False
    # end _hasAccount()

    def _hasBlog(self, ravenBlogId):
        if ravenBlogId and self.validBlogs.has_key(ravenBlogId):
            return True
        else:
            return False
    # end _hasBlog()

    def _getAccountTocXmlFilename(self):
        return u"accounts.xml" #$NON-NLS-1$
    # _getAccountTocXmlFilename()

    def _getAccountDirList(self):
        accountDirPath = os.path.join(self.pathToJoeyProfile, u"accounts") #$NON-NLS-1$
        fullDirNames = []
        try:
            # get the account.xml ("table of contents") file into a dom
            accountsTocXmlFileName = os.path.join(accountDirPath, self._getAccountTocXmlFilename() ) #$NON-NLS-1$
            if not os.path.exists(accountsTocXmlFileName):
                return fullDirNames
            tocDom = ZDom()
            tocDom.load(accountsTocXmlFileName)
            accIdNodes = tocDom.selectNodes(u"/blog-accounts/blog-account/@id") #$NON-NLS-1$
            for accIdNode in accIdNodes:
                accId = accIdNode.getText()
                fullPath = os.path.join(accountDirPath, accId)
                if os.path.isdir(fullPath):
                    accountXmlFileName = os.path.join(fullPath, u"account.xml") #$NON-NLS-1$
                    if os.path.isfile(accountXmlFileName):
                        fullDirNames.append( (fullPath, accountXmlFileName) )
        except Exception, e:
            ze = ZException(e)
            ze.printStackTrace()
        return fullDirNames
    # end _getAccountDirList()

    def _getDataFileList(self):
        docStoreDirPath = os.path.join(self.pathToJoeyProfile, u"docrepo") #$NON-NLS-1$
        fileNames = os.listdir(docStoreDirPath)
        fullFileNames = []
        for name in fileNames:
            if name.endswith(u".jbe.xml"): #$NON-NLS-1$
                fullFileNames.append(os.path.join(docStoreDirPath, name))
        return fullFileNames
    # end _getDataFileList()

    def _getWorkAmount(self):
        # work amount = #accountToImport + #docsToImport + 1_FTP +  1_PersonalDictionary
        return len(self.accountDirList) + len(self.dataFileList) + 2
    # end getWorkAmount()

    def _runImport(self):
        # personal dictionary
        dictImporter = ZBlogWriterDictionaryImporter(self.pathToJoeyProfile, self.pathToRavenProfile, self.systemProfile)
        dictImporter.importPersonalDictionary()
        progressText = _extstr(u"importer.ImportedPersonalDictionaryMsg")#$NON-NLS-1$
        self._notifyWorkDone(1, progressText)

        # import the accounts
        accountXmlPathList = []
        total = len(self.accountDirList)
        count = 0
        for (dname, accountXmlPath) in self.accountDirList:
            count = count + 1
            self._importAccount(dname, accountXmlPath)
            accountXmlPathList.append(accountXmlPath)
            progressText = _extstr(u"importer.ImportedBlogAccountMsg") % (count, total) #$NON-NLS-1$
            self._notifyWorkDone(1, progressText)
            if self.stopped:
                self._notifyCancel()
                return
        # end for

        # FTP site and media stores
        mediaStoreImporter = ZBlogWriterMediaStoreImporter(self.pathToJoeyProfile, self.pathToRavenProfile, self.systemProfile)
        mediaStoreImporter.importFtpMediaStore()
        mediaStoreImporter.importAccountBlogMediaStores(accountXmlPathList)
        progressText = _extstr(u"importer.ImportedMediaStoreMsg")#$NON-NLS-1$
        self._notifyWorkDone(1, progressText)


        # Next, import the blog post data
        total = len(self.dataFileList)
        count = 0
        for fname in self.dataFileList:
            count = count + 1
            self._importBlogPost(fname)
            progressText = _extstr(u"importer.ImportedBlogPostMsg") % (count, total) #$NON-NLS-1$
            self._notifyWorkDone(1, progressText)
            if self.stopped:
                self._notifyCancel()
        # end for
    # end run()

    def _importAccount(self, joeyAccountDirName, accountXmlFileName):
        ravenAccountDirName = self._getRavenAccountDirName(joeyAccountDirName)
        ravenAccountXmlName = os.path.join(ravenAccountDirName, u"account.xml") #$NON-NLS-1$
        os.makedirs(ravenAccountDirName)
        # Copy over any icons that have been downloaded (or any other resource).
        fileutil.copyFiles(joeyAccountDirName, ravenAccountDirName)
        dom = ZDom()
        dom.load(accountXmlFileName)
        newDom = dom.transformToXML(self.accountTransformFilename)
        newDom.setNamespaceMap(ACCOUNT_NSS_MAP)
        # Encrypt the account password.
        passwordNode = newDom.selectSingleNode(u"/zns:account/zns:attributes/zns:attribute[@name = 'password']") #$NON-NLS-1$
        if passwordNode:
            password = crypt.encryptPlainText(passwordNode.getText(), PASSWORD_ENCRYPTION_KEY)
            passwordNode.setText(password)

        # convert host, port & path  combo to a single url attribute; also determine the raven publisher site/type.
        self._convertApiInfo(newDom)
        # account id
        accId = newDom.documentElement.getAttribute(u"account-id") #$NON-NLS-1$
        self.validAccounts[accId] = True
        # convert blog and id format to raven format
        blogNodeList = newDom.selectNodes(u"/zns:account/zns:blogs/zns:blog") #$NON-NLS-1$
        for blogNode in blogNodeList:
            self._convertAccBlogInfo(accId, blogNode)

        # Save to disk.
        newDom.save(ravenAccountXmlName, True)
        del dom
        del newDom
    # end _importAccount()

    def _convertAccBlogInfo(self, ravenAccountId,  blogNode):
        joeyBlogId = blogNode.getAttribute(u"blog-id") #$NON-NLS-1$
        # convert blog id
        qid = self._convertBlogId(ravenAccountId, joeyBlogId)
        self.validBlogs[qid.getId()] = True
        # set new qid
        blogNode.setAttribute(u"blog-id", qid.getId()) #$NON-NLS-1$
        attrsElem = blogNode.selectSingleNode(u"zns:attributes") #$NON-NLS-1$
        # add server side id
        self._addAttr(attrsElem, u"id", qid.getServerId(), IZBlogAppNamespaces.CMS_PUBLISHER_NAMESPACE ) #$NON-NLS-1$
        # blog name
        node = attrsElem.selectSingleNode(u"zns:attribute[@name = 'name']") #$NON-NLS-1$
        if node:
            self._addAttr(attrsElem, u"name", node.getText(), IZBlogAppNamespaces.CMS_PUBLISHER_NAMESPACE ) #$NON-NLS-1$

        # convert atom feed-id if needed
        atomFeedIdNode=  attrsElem.selectSingleNode(u"zns:attribute[@name = 'feed-id']") #$NON-NLS-1$
        if atomFeedIdNode:
            atomFeedQid =  self._convertBlogId(ravenAccountId, atomFeedIdNode.getText())
            atomFeedIdNode.setText(atomFeedQid.getServerId())
        # convert categories and id format to raven format
        catNodeList = blogNode.selectNodes(u"zns:categories/zns:category") #$NON-NLS-1$
        for catNode in catNodeList:
            self._convertAccCategoryInfo(ravenAccountId, qid.getServerId(), catNode)
    # end _convertAccBlogInfo()

    def _convertAccCategoryInfo(self, ravenAccountId, serverBlogId, catNode):
        attrsElem = catNode.selectSingleNode(u"zns:attributes") #$NON-NLS-1$
        node = attrsElem.selectSingleNode(u"zns:attribute[@name = 'id']") #$NON-NLS-1$
        qid = None
        if node:
            id = ZJoeyBlogQId( node.getText() ).getId()
            qid = self._convertEntryId(ravenAccountId, serverBlogId, id)
        else:
            return
        node.setText(qid.getId())
        self._addAttr(attrsElem, u"id", qid.getServerId(), IZBlogAppNamespaces.CMS_PUBLISHER_NAMESPACE ) #$NON-NLS-1$
        node = attrsElem.selectSingleNode(u"zns:attribute[@name = 'name']") #$NON-NLS-1$
        if node:
            self._addAttr(attrsElem, u"name", node.getText(), IZBlogAppNamespaces.CMS_PUBLISHER_NAMESPACE ) #$NON-NLS-1$
    # end _convertAccCategoryInfo()

    def _convertBlogId(self, ravenAccountId, joeyBlogId):
        # converts a Joey blog id to a raven blog id
        # returns ZQualifiedPublisherId
        serverBlogId = joeyBlogId
        if joeyBlogId.startswith(u"urn:zoundry:xmlrpc-id"): #$NON-NLS-1$
            serverBlogId = ZJoeyBlogQId(joeyBlogId).getId()
        else:
            # convert Blogger Atom 1.0 ids that were generated during beta phase
            r = r'(http://)(beta|www)(\.blogger.com/feeds/)(\d+)(/blogs/)(\d+)' #$NON-NLS-1$
            m = re.match(r, joeyBlogId)
            if m:
                serverBlogId= u"tag:blogger.com,1999:user-%s.blog-7%s" % (m.group(4), m.group(6))         #$NON-NLS-1$
        urn = u"urn:zoundry:acc:%s" % ravenAccountId  #$NON-NLS-1$
        qid = ZQualifiedPublisherId(localId = urn, serverId = serverBlogId)
        return qid
    # end _convertBlogId()

    def _convertEntryId(self, ravenAccountId, serverBlogId, joeyEntryId):
        serverEntryId = joeyEntryId
        if joeyEntryId.startswith(u"urn:zoundry:xmlrpc-id"): #$NON-NLS-1$
            serverEntryId = ZJoeyBlogQId(joeyEntryId).getId()
        else:
            # convert Blogger Atom 1.0 ids that were generated during beta phase
            # i.e. convert http://zdev.blogspot.com/feeds/posts/default/4279699388877024759
            # to somethlng like tag:blogger.com,1999:blog-323244233.post-4279699388877024759
            (bloggerUserid, bloggerBlogId) =  self._splitBloggerUrn(serverBlogId) #@UnusedVariable
            regex = r'(http://)(.+)(\.blogspot.com/feeds/posts/default/)(\d+)' #$NON-NLS-1$
            m = re.match(regex, joeyEntryId)
            if bloggerBlogId and m:
                serverEntryId = u"tag:blogger.com,1999:blog-%s.post-%s" % (bloggerBlogId, m.group(4))             #$NON-NLS-1$
        urn = u"urn:zoundry:acc:%s,zoundry:blog:%s" % (ravenAccountId , serverBlogId)  #$NON-NLS-1$
        qid = ZQualifiedPublisherId(localId = urn, serverId = serverEntryId)
        return qid
    # end _convertEntryId()

    def _splitBloggerUrn(self, bloggerId):
        # Splits a blogger urn and returns (userid, blogid) or (blogid, postid)
        # eg  "tag:blogger.com,1999:user-787288900931.blog-7018155386029004596"
        # eg  "tag:blogger.com,1999:blog-7018155386029004596.post-4279699388877024759"
        id1 = None
        id2 = None
        regexp  = r'(tag:blogger\.com,1999:)(user|blog)(-)(\d+)(\.)(blog|post)(-)(\d+)' #$NON-NLS-1$
        m = re.match(regexp, bloggerId)

        if m:
            id1 = m.group(4)
            id2 = m.group(8)
        return (id1, id2)
    # end _splitBloggerUrn()

    def _convertApiInfo(self, newDom):
        #
        # Raven uses a single api-info attribute 'url' instead of host, port and path.
        # Raven also uses a single api-info attribute 'type' to indicate publisher site or type id.
        # (The Joey 1.x account-type and api-type values will be converted to a single api-info type attribute value).
        #

        # Remove account type & icon attr. Not used.
        accType = u"" #$NON-NLS-1$
        accTypeNode = newDom.selectSingleNode(u"/zns:account/zns:attributes/zns:attribute[@name = 'type']") #$NON-NLS-1$
        if accTypeNode:
            accType = accTypeNode.getText()
            accTypeNode.parentNode.removeChild(accTypeNode)

        icon = u"" #$NON-NLS-1$
        iconNode = newDom.selectSingleNode(u"/zns:account/zns:attributes/zns:attribute[@name = 'icon']") #$NON-NLS-1$
        if iconNode:
            icon = iconNode.getText()
            iconNode.parentNode.removeChild(iconNode)

        # Remove port and path attribute.
        host = u"" #$NON-NLS-1$
        path = u"" #$NON-NLS-1$
        port = 80
        apiType = u"" #$NON-NLS-1$
        attrsElem = newDom.selectSingleNode(u"/zns:account/zns:api-info/zns:attributes") #$NON-NLS-1$
        apiTypeNode = newDom.selectSingleNode(u"/zns:account/zns:api-info/zns:attributes/zns:attribute[@name = 'type']") #$NON-NLS-1$
        if apiTypeNode:
            apiType = apiTypeNode.getText()
            apiTypeNode.parentNode.removeChild(apiTypeNode)

        apiHostNode = newDom.selectSingleNode(u"/zns:account/zns:api-info/zns:attributes/zns:attribute[@name = 'host']") #$NON-NLS-1$
        if apiHostNode:
            host = apiHostNode.getText()
            apiHostNode.parentNode.removeChild(apiHostNode)

        apiPortNode = newDom.selectSingleNode(u"/zns:account/zns:api-info/zns:attributes/zns:attribute[@name = 'port']") #$NON-NLS-1$
        if apiPortNode:
            # get port # and remove node
            portstr = apiPortNode.getText()
            apiPortNode.parentNode.removeChild(apiPortNode)
            try:
                port = int(portstr)
            except:
                pass

        apiPathNode = newDom.selectSingleNode(u"/zns:account/zns:api-info/zns:attributes/zns:attribute[@name = 'path']") #$NON-NLS-1$
        if apiPathNode:
            # remove path
            path = apiPathNode.getText()
            apiPathNode.parentNode.removeChild(apiPathNode)

        # construct api endpoint url
        url = self._getUrl(host, port, path)
        # determine raven publisher site or type
        pubtype = self._getPubType(apiType, accType, icon, url)
        # Add type attr to api
        self._addAttr(attrsElem, u"type", pubtype) #$NON-NLS-1$
        # Add url as new attr.
        self._addAttr(attrsElem, u"url", url) #$NON-NLS-1$
        # save joey 1.1 attr
        self._addAttr(attrsElem, u"host", host, IZBlogAppNamespaces.ZBW_ACCOUNT_NAMESPACE ) #$NON-NLS-1$
        self._addAttr(attrsElem, u"port", unicode(port), IZBlogAppNamespaces.ZBW_ACCOUNT_NAMESPACE) #$NON-NLS-1$
        self._addAttr(attrsElem, u"path", path, IZBlogAppNamespaces.ZBW_ACCOUNT_NAMESPACE) #$NON-NLS-1$
        self._addAttr(attrsElem, u"resid", icon, IZBlogAppNamespaces.ZBW_ACCOUNT_NAMESPACE) #$NON-NLS-1$
        self._addAttr(attrsElem, u"account-type", accType, IZBlogAppNamespaces.ZBW_ACCOUNT_NAMESPACE) #$NON-NLS-1$
        self._addAttr(attrsElem, u"api-type", apiType, IZBlogAppNamespaces.ZBW_ACCOUNT_NAMESPACE) #$NON-NLS-1$
    # end _convertApiInfo()

    def _addAttr(self, attrsElem, name, value, namespace = None):
        attributeElem = attrsElem.ownerDocument.createElement(u"zns:attribute", IZBlogAppNamespaces.RAVEN_ACCOUNT_NAMESPACE) #$NON-NLS-1$
        attributeElem.setAttribute(u"name", name) #$NON-NLS-1$
        if namespace:
            attributeElem.setAttribute(u"namespace", namespace) #$NON-NLS-1$
        attributeElem.setText(value)
        attrsElem.appendChild(attributeElem)
    # end _addAttr()

    def _getPubType(self, joeyApiType, joeyAccType, joeyResId, url):
        joeyApi = ZJoeyApiInfo()
        type = joeyApi.getRavenApiType(joeyApiType, joeyAccType, joeyResId, url)
        return type
    # end _getPubType()

    def _getUrl(self, host, port, path):
        if not host or len(host) == 0:
            return host
        scheme = u"http" #$NON-NLS-1$ default scheme
        if host and len(host) > 7 and host.lower().startswith(u"http://"):#$NON-NLS-1$
            scheme = u"http" #$NON-NLS-1$
            host = host[7:]
        elif host and len(host) > 8 and host.lower().startswith(u"https://"):#$NON-NLS-1$
            scheme = u"https" #$NON-NLS-1$
            host = host[8:]
        tempHost = host
        if scheme == u"http" and port != 80: #$NON-NLS-1$
            tempHost = host + u":" + unicode(port) #$NON-NLS-1$
        elif scheme == u"https" and port != 443: #$NON-NLS-1$
            tempHost = host + u":" + unicode(port) #$NON-NLS-1$

        url = scheme + u"://" + tempHost#$NON-NLS-1$
        if path:
            url = url + u"/" + path.lstrip(u"/")  #$NON-NLS-1$  #$NON-NLS-2$
        return url
    # end _getUrl()

    def _getRavenAccountDirName(self, joeyAccountDirName):
        basename = os.path.basename(joeyAccountDirName)
        return os.path.join(self.pathToRavenProfile, u"accounts", basename) #$NON-NLS-1$
    # end _getRavenAccountDirName()

    def _importBlogPost(self, jbeXmlFileName):
        ravenXmlFileName = self._getRavenXmlFileName(jbeXmlFileName)
        jbeHtmlFileName = self._getJbeHtmlFileName(jbeXmlFileName)

        dom = ZDom()
        dom.load(jbeXmlFileName)
        newDom = dom.transformToXML(self.dataTransformFilename)
        self._attachContent(newDom, jbeHtmlFileName)

        removeNodeList = []
        blogNodeList = []
        published = False
        for blogNode in newDom.selectNodes(u"/zns:entry/zns:blogs/zns:blog"): #$NON-NLS-1$
            # since there is atleast one blog associated with the entry, assume the post
            # is published
            published = True
            ravenAccountId = blogNode.getAttribute(u"account-id") #$NON-NLS-1$
            joeyBlogId = blogNode.getAttribute(u"blog-id") #$NON-NLS-1$
            qid = self._convertBlogId(ravenAccountId, joeyBlogId)
            if self._hasBlog( qid.getId() ):
                blogNodeList.append(blogNode)
                self._convertBlogPostBlogInfo(ravenAccountId, qid.getId(), qid.getServerId(),  blogNode)
            else:
                removeNodeList.append(blogNode)
        # remove orphan blog infos
        for blogNode in removeNodeList:
            blogNode.parentNode.removeChild(blogNode)
        # save only if there were any blogs associated with the entry or if the post is a draft (published = false)
        if not published or (blogNodeList and len(blogNodeList) > 0):
            newDom.save(ravenXmlFileName, True)
        del dom
        del newDom
    # end _importBlogPost()

    def _convertBlogPostBlogInfo(self, ravenAccountId, ravenBlogId, serverBlogId,  blogNode):
        blogNode.setAttribute(u"blog-id", ravenBlogId) #$NON-NLS-1$
        attrsElem = blogNode.selectSingleNode(u"zns:publish-info/zns:attributes") #$NON-NLS-1$
        joeyEntryIdNode = attrsElem.selectSingleNode(u"zns:attribute[@name = 'blog-entry-id']") #$NON-NLS-1$
        if not joeyEntryIdNode:
            return
        # remove id node
        idNode = attrsElem.selectSingleNode(u"zns:attribute[@name = 'id']") #$NON-NLS-1$
        if idNode:
            idNode.parentNode.removeChild(idNode)
        # convery entry id to raven entry id
        entryQid = self._convertEntryId(ravenAccountId, serverBlogId, joeyEntryIdNode.getText())
        joeyEntryIdNode.setText( entryQid.getId() )
        # add server side entry id
        self._addAttr(attrsElem, u"id", entryQid.getServerId(), IZBlogAppNamespaces.CMS_PUBLISHER_NAMESPACE ) #$NON-NLS-1$
        # convert post-url and alt-link to a single url attribnute
        url = None
        node = attrsElem.selectSingleNode(u"zns:attribute[@name = 'post-url']") #$NON-NLS-1$
        if node:
            url = node.getText()
            node.parentNode.removeChild(node)
        if not url:
            node = attrsElem.selectSingleNode(u"zns:attribute[@name = 'alt-link']") #$NON-NLS-1$
            if node:
                url = node.getText()
        self._addAttr(attrsElem, u"url", url) #$NON-NLS-1$
        # if there is a atom-alt but the blog is xml-rpc, then remove the atom alt-linkg
        node1 = attrsElem.selectSingleNode(u"zns:attribute[@name = 'alt-link']") #$NON-NLS-1$
        node2 = attrsElem.selectSingleNode(u"zns:attribute[@name = 'edit-link']") #$NON-NLS-1$  # if this exists, then assume atom entry blog
        if node1 and not node2:
            node1.parentNode.removeChild(node1)
        # Also remove 'atom-blog-entry-id' which is not needed.
        node1 = attrsElem.selectSingleNode(u"zns:attribute[@name = 'blog-id']") #$NON-NLS-1$
        node2 = attrsElem.selectSingleNode(u"zns:attribute[@name = 'edit-link']") #$NON-NLS-1$  # if this exists, then assume atom entry blog
        if node1 and node2:
            node1.parentNode.removeChild(node1)


        # convert categories and id format to raven format
        catNodeList = blogNode.selectNodes(u"zns:categories/zns:category") #$NON-NLS-1$
        for catNode in catNodeList:
            self._convertAccCategoryInfo(ravenAccountId, serverBlogId, catNode)

        # FIXME (PJ) Import and convert Trackback info (or verify its done)
    # end _convertBlogPostBlogInfo()

    def _attachContent(self, newDom, jbeHtmlFileName):
        # Only do it if the content file exists.
        if os.path.isfile(jbeHtmlFileName):
            newDom.setNamespaceMap(DOCUMENT_NSS_MAP)
            contentNode = newDom.selectSingleNode(u"/zns:entry/zns:content") #$NON-NLS-1$

            html = self._loadContent(jbeHtmlFileName)
            # FIXME (PJ) use xhtml deserializer to load zDom.
            try:
                jbeHtmlDom = ZDom()
                jbeHtmlDom.loadHTML(html)
                contentNode.appendChild(newDom.importNode(jbeHtmlDom.documentElement, True))
                contentNode.setAttribute(u"mode", u"xml") #$NON-NLS-2$ #$NON-NLS-1$
            except:
                contentNode.setText(html)
                contentNode.setAttribute(u"type", u"text/html") #$NON-NLS-2$ #$NON-NLS-1$
                contentNode.setAttribute(u"mode", u"escaped") #$NON-NLS-2$ #$NON-NLS-1$
    # end _attachContent()

    def _loadContent(self, jbeHtmlFileName):
        f = open(jbeHtmlFileName, u"r") #$NON-NLS-1$
        try:
            return convertToUnicode(f.read())
        finally:
            f.close()
    # end _loadContent()

    def _getRavenXmlFileName(self, jbeXmlFileName):
        basename = os.path.basename(jbeXmlFileName)
        id = basename.split(u".")[0] #$NON-NLS-1$
        dirname = os.path.join(self.pathToRavenProfile, u"datastore") #$NON-NLS-1$
        if not os.path.isdir(dirname):
            os.mkdir(dirname)
        return os.path.join(dirname, id) + u".rbe.xml" #$NON-NLS-1$
    # end _getRavenXmlFileName()

    def _getJbeHtmlFileName(self, jbeXmlFileName):
        basename = os.path.basename(jbeXmlFileName)
        dirname = os.path.dirname(jbeXmlFileName)
        (name, _ext) = os.path.splitext(basename)
        return os.path.join(dirname, name) + u".html" #$NON-NLS-1$
    # end _getJbeHtmlFileName()

# end ZProfileImporter


class ZJoeyBlogQId:

    def __init__(self, qid = None, uri = None, id = None):
        u"""Constructs ZBW Blog Q-ID given either the qid or uri and id.""" #$NON-NLS-1$
        # qid = uri + joinStr + id
        # eg: https://www.blogger.com/atom/11882722 => https://www.blogger.com/atom + / + 11882722
        # eg: urn:zoundry:xmlrpc-id:/acc/123/blogid/456 => urn:zoundry:xmlrpc-id:/acc/123/blogid + / + 456
        self.qid = u"" #$NON-NLS-1$
        self.uri = u"" #$NON-NLS-1$
        self.id = u"" #$NON-NLS-1$
        if not qid and uri and id:
            # join
            self.uri = uri
            self.id = id
            self.qid = self.uri +  unicode(id)
        elif qid:
            # split
            self.qid = qid
            (self.uri, self.id) = self._splitQId(qid)

    def getQualifiedId(self):
        return self.qid

    def getId(self):
        u"""Returns the 'local' part i.e. the trailing number.""" #$NON-NLS-1$
        return self.id

    def getUri(self):
        u"""Returns the leading URI of the id.""" #$NON-NLS-1$
        return self.uri

    def __str__(self):
        return self.getQualifiedId()

    def _splitQId(self, qid):
        u"""Returns the tuple(uri, id).
        For example:
        Blog Id:
        http://www.blogger.com/atom/11882722 -> returns (http://www.blogger.com/atom,118272)
        http://www.typepad.com/t/atom/weblog/blog_id=100597 -> returns (http://www.typepad.com/t/atom/weblog/blog_id=, 100597)
        urn:zoundry:xmlrpc-id:/acc/123/blogid/456 - returns (urn:zoundry:xmlrpc-id:/acc/123/blogid, 456)

        blog entry id (post-id):
        tag:blogger.com,1999:blog-6404653.post-111015513344974577 => (tag:blogger.com,1999:blog-6404653.post-,111015513344974577)
        tag:typepad.com,2003:post-3243055 => (tag:typepad.com,2003:post-, 3243055)
        urn:zoundry:xmlrpc-id:/acc/123/blogid/456/postid/789 => (tag:urn:zoundry:xmlrpc-id:/acc/123/blogid/456/postid, 789)
        urn:zoundry:xmlrpc-id:/acc/123/blogid/http://www.dasblogtest.com/ => (urn:zoundry:xmlrpc-id:/acc/123/blogid, http://www.dasblogtest.com/)
        urn:zoundry:xmlrpc-id:/acc/123/blogid/http://www.dasblogtest.com//postid/35a02998-4673-430f-9ece-2e5dcb6684d2 => (urn:zoundry:xmlrpc-id:/acc/123/blogid/http://www.dasblogtest.com//postid, 35a02998-4673-430f-9ece-2e5dcb6684d2)
        """ #$NON-NLS-1$

        uri = u"" #$NON-NLS-1$
        id = None

        if qid and qid.startswith(u"urn:zoundry:xmlrpc-id:"):  #$NON-NLS-1$
            (uri, id) = self._splitZUrnQId(qid)

        if id is not None:
            return (uri, id)

        # handle post-id tag cases (simple algo for typepad and blogger format)
        idx = -1
        if qid.lower().startswith(u"tag:"): #$NON-NLS-1$
            idx = qid.find(u"post-") #$NON-NLS-1$
            if idx != -1:
                uri = qid[0:idx + 5]
                id = qid[idx + 5:]
        if idx == -1:
            # typepad blog id
            idx = qid.rfind(u"=")  #$NON-NLS-1$
            if idx != -1:
                uri = qid[0:idx + 1]
                id = qid[idx + 1:]
        if idx == -1:
            # blog atom blog id or any other 'url' format.
            idx = qid.rfind(u"/")  #$NON-NLS-1$
            if idx != -1:
                uri = qid[0:idx + 1]
                id = qid[idx + 1:]
        if idx == -1:
            uri = u"" #$NON-NLS-1$
            id = qid
        return (uri,id)

    def _splitZUrnQId(self, qid):
        u"""Returns the tuple(uri, id) given a zoundry specific urn format.
        urn:zoundry:xmlrpc-id:/acc/123/blogid/456 => (urn:zoundry:xmlrpc-id:/acc/123/blogid, 456)
        urn:zoundry:xmlrpc-id:/acc/123/blogid/456/postid/789 => (tag:urn:zoundry:xmlrpc-id:/acc/123/blogid/456/postid, 789)
        urn:zoundry:xmlrpc-id:/acc/123/blogid/http://www.dasblogtest.com/ => (urn:zoundry:xmlrpc-id:/acc/123/blogid, http://www.dasblogtest.com/)
        urn:zoundry:xmlrpc-id:/acc/123/blogid/http://www.dasblogtest.com//postid/35a02998-4673-430f-9ece-2e5dcb6684d2 => (urn:zoundry:xmlrpc-id:/acc/123/blogid/http://www.dasblogtest.com//postid, 35a02998-4673-430f-9ece-2e5dcb6684d2)

        """ #$NON-NLS-1$
        uri = u"" #$NON-NLS-1$
        id = None
        idx = qid.find(u"/postid/")#$NON-NLS-1$
        if idx == -1:
            idx = qid.find(u"/blogid/")#$NON-NLS-1$
        if idx != -1:
            uri = qid[0:idx + 8]
            id = qid[idx + 8:]
        return (uri,id)
# end ZJoeyBlogQId


def getApikey(accType, apiType, resId = None):
    key = accType.strip().lower() + u"|" + apiType.strip().lower(); #$NON-NLS-1$
    if resId and len(resId.strip()) > 0:
        key = key + u"|" + resId.strip().lower() #$NON-NLS-1$
    return key
# end getApikey()


# ------------------------------------------------------------------------------
# Joey API Info.
# ------------------------------------------------------------------------------
class ZJoeyApiInfo:

    #=============================================
    # Joey Account Types
    #============================================
    ACC_BLOGGER = u"Blogger.com" #$NON-NLS-1$
    ACC_TYPEPAD = u"TypePad" #$NON-NLS-1$
    ACC_WORDPRESS = u"Wordpress" #$NON-NLS-1$
    ACC_MTSERVER = u"Six Apart Movable Type" #$NON-NLS-1$
    ACC_MOVABLETYPE = u"Movable Type" #$NON-NLS-1$
    ACC_METAWEBLOG = u"MetaWeblog" #$NON-NLS-1$
    ACC_LIVEJOURNAL = u"LiveJournal" #$NON-NLS-1$
    ACC_BLOGGER_V1 = u"Blogger v1 API" #$NON-NLS-1$
    ACC_BLOGGER_V2 = u"Blogger v2 API" #$NON-NLS-1$
    ACC_MSNSPACES = u"MSNSpaces" #$NON-NLS-1$
    ACC_CUSTOMATOM = u"Custom Atom" #$NON-NLS-1$
    ACC_CUSTOMATOM10 = u"Custom Atom 1.0" #$NON-NLS-1$

    #================================================
    # Joey API Types
    #================================================
    ATOM03 = u"Atom" #$NON-NLS-1$
    ATOM10 = u"Atom10" #$NON-NLS-1$
    XMLRPC_WORDRESS = u"xmlrpc.wordpress"  #$NON-NLS-1$
    XMLRPC_MOVABLETYPE_SA = u"xmlrpc.movabletype"   #$NON-NLS-1$ # Six Apart
    XMLRPC_MOVABLETYPE = u"xmlrpc.mt" #$NON-NLS-1$  # Generic
    XMLRPC_METAWEBLOG = u"xmlrpc.metaweblog"  #$NON-NLS-1$
    XMLRPC_LIVEJOURNAL = u"xmlrpc.livejournal" #$NON-NLS-1$
    XMLRPC_BLOGGER_V1 = u"xmlrpc.bloggerv1" #$NON-NLS-1$
    XMLRPC_BLOGGER_V2 = u"xmlrpc.bloggerv2" #$NON-NLS-1$
    XMLRPC_MSNSPACES = u"xmlrpc.msnspaces" #$NON-NLS-1$


    #=====================================================
    PUB_TYPE_MAP = {}
    # key = acctype|apitype|resId
    PUB_TYPE_MAP[ getApikey(ACC_BLOGGER, ATOM10) ] = DefaultSites.BLOGGER
    # FIXME (PJ) map blogger/atom0.3 -> atom 1.0? (also update api endpoint)
    PUB_TYPE_MAP[ getApikey(ACC_BLOGGER, ATOM03) ] = DefaultSites.BLOGGER_LEGACY
    PUB_TYPE_MAP[ getApikey(ACC_MTSERVER, XMLRPC_MOVABLETYPE_SA, u"typepad") ] = DefaultSites.TYPEPAD_XMLRPC #$NON-NLS-1$
    PUB_TYPE_MAP[ getApikey(ACC_TYPEPAD, ATOM03) ] = DefaultSites.TYPEPAD_ATOM
    PUB_TYPE_MAP[ getApikey(ACC_MSNSPACES, XMLRPC_MSNSPACES) ] = DefaultSites.MSNSPACES
    PUB_TYPE_MAP[ getApikey(ACC_WORDPRESS,XMLRPC_WORDRESS, u"wpdotcom" ) ] = DefaultSites.WPDOTCOM  #$NON-NLS-1$
    PUB_TYPE_MAP[ getApikey(ACC_WORDPRESS,XMLRPC_WORDRESS) ] = DefaultSites.WORDPRESS  #$NON-NLS-1$
    PUB_TYPE_MAP[ getApikey(ACC_LIVEJOURNAL, XMLRPC_LIVEJOURNAL) ] =  DefaultSites.LJ
    PUB_TYPE_MAP[ getApikey(ACC_MTSERVER, XMLRPC_MOVABLETYPE_SA) ] = DefaultSites.SA_MOVABLE_TYPE #$NON-NLS-1$
    PUB_TYPE_MAP[ getApikey(ACC_MOVABLETYPE, XMLRPC_MOVABLETYPE, u"blogharbor") ] = DefaultSites.BLOGHARBOR #$NON-NLS-1$
#    PUB_TYPE_MAP[ getApikey(ACC_METAWEBLOG, XMLRPC_METAWEBLOG, u"HOST=blogware.com") ] = BLOGWARE #$NON-NLS-1$ # SPECIAL CASE on HOST (vs BLOGHARBOR)
    PUB_TYPE_MAP[ getApikey(ACC_METAWEBLOG, XMLRPC_METAWEBLOG, u"lifetype") ] = DefaultSites.LIFETYPE  #$NON-NLS-1$
    PUB_TYPE_MAP[ getApikey(ACC_MOVABLETYPE, XMLRPC_MOVABLETYPE, u"nucleus") ] = DefaultSites.NUCLEUS  #$NON-NLS-1$
    PUB_TYPE_MAP[ getApikey(ACC_MOVABLETYPE, XMLRPC_MOVABLETYPE, u"drupal") ] = DefaultSites.DRUPAL  #$NON-NLS-1$
    PUB_TYPE_MAP[ getApikey(ACC_METAWEBLOG, XMLRPC_METAWEBLOG, u"communityserver") ] = DefaultSites.COMMUNITY_SERVER  #$NON-NLS-1$
    PUB_TYPE_MAP[ getApikey(ACC_METAWEBLOG, XMLRPC_METAWEBLOG, u"roller") ] = DefaultSites.ROLLER  #$NON-NLS-1$
    PUB_TYPE_MAP[ getApikey(ACC_METAWEBLOG, XMLRPC_METAWEBLOG, u"squarespace") ] = DefaultSites.SQUARESPACE  #$NON-NLS-1$
    PUB_TYPE_MAP[ getApikey(ACC_METAWEBLOG, XMLRPC_METAWEBLOG, u"dasblog") ] = DefaultSites.DASBLOG  #$NON-NLS-1$
    PUB_TYPE_MAP[ getApikey(ACC_MOVABLETYPE, XMLRPC_MOVABLETYPE, u"textpattern") ] = DefaultSites.TEXTPATTERN  #$NON-NLS-1$
    PUB_TYPE_MAP[ getApikey(ACC_METAWEBLOG, XMLRPC_METAWEBLOG, u"xoops") ] = DefaultSites.XOOPS  #$NON-NLS-1$
    PUB_TYPE_MAP[ getApikey(ACC_METAWEBLOG, XMLRPC_METAWEBLOG, u"xaraya") ] = DefaultSites.XARAYA  #$NON-NLS-1$
    PUB_TYPE_MAP[ getApikey(ACC_CUSTOMATOM10, ATOM10) ] = DefaultSites.CUSTOM_ATOM10
    PUB_TYPE_MAP[ getApikey(ACC_CUSTOMATOM, ATOM03) ] = DefaultSites.CUSTOM_ATOM03
    PUB_TYPE_MAP[ getApikey(ACC_METAWEBLOG, XMLRPC_METAWEBLOG) ] = DefaultSites.CUSTOM_METAWEBLOG
    PUB_TYPE_MAP[ getApikey(ACC_MOVABLETYPE, XMLRPC_MOVABLETYPE) ] = DefaultSites.CUSTOM_MT
#    PUB_TYPE_MAP[ getApikey(ACC_LIVEJOURNAL, XMLRPC_LIVEJOURNAL, u"CHECK HOST") ] =  CUSTOM_LJ    # SPECIAL CASE on HOST (vs Custom LJ)
    PUB_TYPE_MAP[ getApikey(ACC_BLOGGER_V1, XMLRPC_BLOGGER_V1) ] = DefaultSites.CUSTOM_BLOGGERV1
    PUB_TYPE_MAP[ getApikey(ACC_BLOGGER_V2, XMLRPC_BLOGGER_V2) ] = DefaultSites.CUSTOM_BLOGGERV2


    def __init__(self):
        pass

    def getRavenApiType(self, joeyApiType, joeyAccType, joeyResId, url):
        rval = None
        # Look up using  acctype, apitype and resid
        key = getApikey(joeyAccType,joeyApiType, joeyResId )
        if ZJoeyApiInfo.PUB_TYPE_MAP.has_key(key):
            rval = ZJoeyApiInfo.PUB_TYPE_MAP[key]
        else:
            # Look up using just acctype and api type
            key = getApikey(joeyAccType,joeyApiType)
            if ZJoeyApiInfo.PUB_TYPE_MAP.has_key(key):
                rval = ZJoeyApiInfo.PUB_TYPE_MAP[key]

        if not rval:
            # guess default - metaweblog
            rval = DefaultSites.CUSTOM_METAWEBLOG

        # special case - custom LJ (i.e user hosted livejournal server - not www.livejournal.com)
        if rval == DefaultSites.LJ and url and url.lower().find(u"livejournal.com") == -1: #$NON-NLS-1$
            rval = DefaultSites.CUSTOM_LJ
        # special case blogware
        elif rval == DefaultSites.CUSTOM_MT and url and url.lower().find(u"blogware.com") != -1: #$NON-NLS-1$
            rval = DefaultSites.BLOGWARE
        return rval
    # end getRavenApiType()

# end ZJoeyApiInfo


#------------------------------------------------------------------
# Joey Dictionary Importer
#------------------------------------------------------------------
class ZBlogWriterDictionaryImporter(ZAbstractZBWProfileImporter):

    SPELLCHECK_TEMPLATE = u"""<spellchecker xmlns="http://www.zoundry.com/schemas/2006/10/zspellchecker.rng">
      <language url="http://www.zoundry.com/download/dictionaries/aspell/en.zip" display-name="English (US)" handler="zoundry.appframework.spellcheck.dictionary-handler.aspell" type="zoundry.appframework.spellcheck.provider.aspell" lang-code="en_US"/>
      <provider>zoundry.appframework.services.spellcheck.aspell.aspellprovider.ZAspellSpellCheckProvider</provider>
      <personal-dictionary />
      <auto-corrections/>
    </spellchecker>
    """ #$NON-NLS-1$

    def __init__(self, pathToJoeyProfile, pathToRavenProfile, systemProfile):
        ZAbstractZBWProfileImporter.__init__(self, pathToJoeyProfile, pathToRavenProfile, systemProfile)
    # end __ init__

    def _getWorkAmount(self):
        return 1
    # end getWorkAmount()

    def _runImport(self):
        self.importPersonalDictionary()
        progressText = _extstr(u"importer.ImportedPersonalDictionaryMsg")#$NON-NLS-1$
        self._notifyWorkDone(1, progressText)
    # end _runImport

    def importPersonalDictionary(self):
        joeyConfigDom = self._getJoeyUserConfigDom()
        if not joeyConfigDom:
            return
        try:
            node = joeyConfigDom.selectSingleNode(u"/joey/user-config/spell-check/language") #$NON-NLS-1$
            if not node:
                return
            spellcheckLang = getNoneString( node.getText())
            if not spellcheckLang:
                return

            # FIXME (EPW) we could support other languages...
            if not spellcheckLang == u"en_US": #$NON-NLS-1$
                return

            # 1) read all words from ZBW personal-dictionary.xml file
            # 2) create new spellchecker.xml DOM
            # 3) save new Raven spellchecker file to 'PROFILE\LANG\spellchecker.xml'

            joeyDictFile = os.path.join(self.pathToJoeyProfile, u"spelling/personal-dictionary.xml") #$NON-NLS-1$
            dom = ZDom()
            dom.load(joeyDictFile)
            dom.setNamespaceMap(ZBW_PERSONAL_DICTIONARY_NSS_MAP)
            wordNodeList = dom.selectNodes(u"/pd:personal-dictionary/pd:word") #$NON-NLS-1$
            
            newDom = ZDom()
            newDom.loadXML(ZBlogWriterDictionaryImporter.SPELLCHECK_TEMPLATE)
            newDom.setNamespaceMap(RAVEN_SPELLCHECK_NSS_MAP)
            personalDictElem = newDom.selectSingleNode(u"/spl:spellchecker/spl:personal-dictionary") #$NON-NLS-1$
            
            for wordNode in wordNodeList:
                word = wordNode.getText()
                newWordElem = newDom.createElement(u"word", IZBlogAppNamespaces.RAVEN_SPELLCHECKER_NAMESPACE) #$NON-NLS-1$
                newWordElem.setText(word)
                personalDictElem.appendChild(newWordElem)
            
            outputDir = os.path.join(self.pathToRavenProfile, u"spellcheck/en_US") #$NON-NLS-1$
            os.makedirs(outputDir)
            outputFile = os.path.join(outputDir, u"spellchecker.xml") #$NON-NLS-1$
            newDom.save(outputFile, True)
        except ZException, ze:
            # FIXME (EPW) need to report errors in some way
            ze.printStackTrace()
        except Exception, e:
            # FIXME (EPW) need to report errors in some way
            ze = ZException(rootCause = e)
            ze.printStackTrace()
    # end importPersonalDictionary()

# end  ZBlogWriterDictionaryImporter


#------------------------------------------------------------------
# Joey Media store importer
#------------------------------------------------------------------
class ZBlogWriterMediaStoreImporter(ZAbstractZBWProfileImporter):

    def __init__(self, pathToJoeyProfile, pathToRavenProfile, systemProfile):
        ZAbstractZBWProfileImporter.__init__(self, pathToJoeyProfile, pathToRavenProfile, systemProfile)
    # end __ init__

    def _getJoeyRemoteFilesDom(self):
        try:
            f = os.path.join(self.pathToSourceProfile, u"mediarep\\zremotefiles.xml") #$NON-NLS-1$
            dom = ZDom()
            dom.load(f)
            return dom
        except:
            return None
    # end _getJoeyRemoteFilesDom()

    def _getJoeyLocalFilesDom(self):
        try:
            f = os.path.join(self.pathToSourceProfile, u"mediarep\\zlocalfiles.xml") #$NON-NLS-1$
            dom = ZDom()
            dom.load(f)
            return dom
        except:
            return None
    # end _getJoeyLocalFilesDom()

    def _getWorkAmount(self):
        return 1
    # end getWorkAmount()

    def _runImport(self):
        self.importAll()
        progressText = _extstr(u"importer.ImportedMediaStoreMsg")#$NON-NLS-1$
        self._notifyWorkDone(1, progressText)
    # end _runImport

    def importAll(self):
        self.importFtpMediaStore()
        self.importAccountBlogMediaStores()
    # end importAll

    def _getRegistryEntries(self, joeyBlogId):
        # returns list of maps, where is map contains registry entry information url, filepath, filesize, and time.
        rval = []
        localFileDom = self._getJoeyLocalFilesDom()
        if not localFileDom:
            return rval
        remoteFileDom = self._getJoeyRemoteFilesDom()
        if not remoteFileDom:
            return rval
        # build map of file id:url of uploaded images
        xpath = None
        if joeyBlogId is not None:
            xpath = u"""//blog[@id="%s"]/store[@type='xmlrpc']/file""" % joeyBlogId #$NON-NLS-1$
        else:
            xpath = u"//store[@type='ftp']/file" #$NON-NLS-1$
        nodeList = remoteFileDom.selectNodes(xpath)
        if not nodeList or len(nodeList) == 0:
            return
        remoteEntries = []
        for node in nodeList:
            id = node.getAttribute(u"id") #$NON-NLS-1$
            url = node.getText()
            if id and url:
                remoteEntries.append( (id, url) )
        # get local file path, size and time
        for (id, url) in remoteEntries:
            node = localFileDom.selectSingleNode(u"""//file[@id="%s"]""" % id) #$NON-NLS-1$
            if node:
                fileTime = ZSchemaDateTime( long(node.getAttribute(u"time")) ) #$NON-NLS-1$
                regEntry = {}
                regEntry[u"url"] = url #$NON-NLS-1$
                regEntry[u"timestamp"] = fileTime.__str__() #$NON-NLS-1$
                regEntry[u"size"] = node.getAttribute(u"size") #$NON-NLS-1$ #$NON-NLS-2$
                regEntry[u"path"] = node.getText() #$NON-NLS-1$
                rval.append(regEntry)
        return rval
    # end _getRegistryEntries()

    def importAccountBlogMediaStores(self, accountXmlPathList):
        for accountXmlPath in accountXmlPathList:
            joeyAccountDom = ZDom()
            joeyAccountDom.load(accountXmlPath)
            for blogNode in joeyAccountDom.selectNodes(u"//blogs/blog[child::mediarep/text()='publisher']"): #$NON-NLS-1$
                try:
                    blogId =  blogNode.selectSingleNode(u"id").getText()  #$NON-NLS-1$
                    regList = self._getRegistryEntries(blogId) #@UnusedVariable
                    # FIXME (PJ) create Raven metaweblog media site for blogId. Add regFiles to media store reg. Associate *raven* account with media store
                except:
                    pass
    # end importAccountBlogMediaStores()

    def importFtpMediaStore(self):
        joeyConfigDom = self._getJoeyUserConfigDom()
        if not joeyConfigDom:
            return
        try:
            url = getNoneString( joeyConfigDom.selectSingleNode(u"/joey/user-config/media-rep/url").getText() ) #$NON-NLS-1$
            host = getNoneString( joeyConfigDom.selectSingleNode(u"/joey/user-config/media-rep/remote/ip").getText() ) #$NON-NLS-1$
            port = getNoneString( joeyConfigDom.selectSingleNode(u"/joey/user-config/media-rep/remote/port").getText() ) #$NON-NLS-1$
            path = joeyConfigDom.selectSingleNode(u"/joey/user-config/media-rep/remote/path").getText() #$NON-NLS-1$
            username = getNoneString( joeyConfigDom.selectSingleNode(u"/joey/user-config/media-rep/remote/username").getText() )#$NON-NLS-1$
            password = getNoneString( joeyConfigDom.selectSingleNode(u"/joey/user-config/media-rep/remote/password").getText() ) #$NON-NLS-1$

            props = None
            if url and len(url) > 7 and  host and port and username and password:
                props = {}
                props[u"host"] = host  #$NON-NLS-1$
                props[u"port"] = int(port)  #$NON-NLS-1$
                props[u"username"] = username  #$NON-NLS-1$
                props[u"password"] = password  #$NON-NLS-1$
                props[u"path"] = path  #$NON-NLS-1$
                props[u"url"] = url #$NON-NLS-1$
                props[u"passive"] = True #$NON-NLS-1$
                registryList = self._getRegistryEntries(None) #@UnusedVariable
                # FIXME (PJ) create Raven FTP media site. Add regFiles to media store reg. Associate *imported raven* account that do not have publisher type fileupload with ftp.
                # store = self.mediaStoreService.createMediaStorage(u"FTP (BlogWriter)", u"zoundry.blogapp.mediastorage.site.customftp", properties) #$NON-NLS-2$ #$NON-NLS-1$
        except:
            pass
    # end importFtpMediaStore()

# end ZBlogWriterMediaStoreImporter
