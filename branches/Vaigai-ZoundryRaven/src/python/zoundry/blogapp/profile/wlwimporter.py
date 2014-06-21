from zoundry.appframework.profile.userprefs import IZUserPreferences
from zoundry.appframework.util.osutilfactory import ZOSUtilFactory
from zoundry.base.util.guid import generate
from zoundry.blogapp.constants import IZBlogAppNamespaces
from zoundry.blogapp.messages import _extstr
from zoundry.blogapp.profile.importer import ZAbstractProfileImporter
from zoundry.blogapp.profile.wlwtypemapper import LIVE_WRITER_PROVIDER_MAP
from zoundry.blogapp.services.accountstore.accountimpl import ZAccountAPIInfo
from zoundry.blogapp.services.accountstore.accountimpl import ZBlogAccount
from zoundry.blogapp.services.accountstore.accountimpl import ZBlogFromAccount
from zoundry.blogapp.services.accountstore.io.factory import ZAccountSerializerFactory
from zoundry.blogapp.services.commonimpl import ZCategory
from zoundry.blogapp.services.pubsystems.sitenames import DefaultSites
from zoundry.appframework.util.osutilfactory import getOSUtil
import os


def isLiveWriterInstalled():
    import _winreg
    try:
        handle = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, u"Software\\Microsoft\\Windows Live\\Writer") #$NON-NLS-1$
        _winreg.CloseKey(handle)
        return True
    except:
        pass

    try:
        handle = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, u"Software\\Windows Live Writer") #$NON-NLS-1$
        _winreg.CloseKey(handle)
        return True
    except:
        pass

    return False
# end _openRootRegistryKey()


# ------------------------------------------------------------------------------
# Information about a particular blog in the registry.
# ------------------------------------------------------------------------------
class ZWindowsLiveWriterBlogInfo:

    def __init__(self, handle):
        import _winreg
        self.blogId = _winreg.QueryValueEx(handle, u"BlogId")[0] #$NON-NLS-1$
        self.blogName = _winreg.QueryValueEx(handle, u"BlogName")[0] #$NON-NLS-1$
        # clientType (api) = Metaweblog, Wordpress, BloggerAtom, LiveJournal, MovableType, Blogger2, WindowsLiveSpaces
        self.clientType = _winreg.QueryValueEx(handle, u"ClientType")[0] #$NON-NLS-1$
        # fileUploadSupport = 2:ftp, 1:blogapi, 0: no
        self.fileUploadSupport = _winreg.QueryValueEx(handle, u"FileUploadSupport")[0] #$NON-NLS-1$
        self.forceManualConfig = _winreg.QueryValueEx(handle, u"ForceManualConfig")[0] #$NON-NLS-1$
        self.homepageUrl = _winreg.QueryValueEx(handle, u"HomepageUrl")[0] #$NON-NLS-1$
        self.isSharepointBlog = _winreg.QueryValueEx(handle, u"IsSharepointBlog")[0] #$NON-NLS-1$
        self.isSpacesBlog = _winreg.QueryValueEx(handle, u"IsSpacesBlog")[0] #$NON-NLS-1$
        self.postApiUrl = _winreg.QueryValueEx(handle, u"PostApiUrl")[0] #$NON-NLS-1$
        self.providerId = _winreg.QueryValueEx(handle, u"ProviderId")[0] #$NON-NLS-1$
        # service name = Weblog, WordPress, Blogger
        self.serviceName = _winreg.QueryValueEx(handle, u"ServiceName")[0] #$NON-NLS-1$

        credsHandle = _winreg.OpenKey(handle, u"Credentials") #$NON-NLS-1$
        self.username = _winreg.QueryValueEx(credsHandle, u"Username")[0] #$NON-NLS-1$

        self.ftpId = None
        self.ftpServer = None
        self.ftpPath = None
        self.ftpPath = None
        self.ftpUrl = None
        self.ftpUsername = None
        # FTP info:
        if self.fileUploadSupport == 2:
            fileUploadHandle = _winreg.OpenKey(handle, u"FileUploadSettings") #$NON-NLS-1$
            self.ftpServer = _winreg.QueryValueEx(fileUploadHandle, u"FtpServer")[0] #$NON-NLS-1$
            self.ftpPath = _winreg.QueryValueEx(fileUploadHandle, u"PublishPath")[0] #$NON-NLS-1$
            self.ftpUrl = _winreg.QueryValueEx(fileUploadHandle, u"UrlMapping")[0] #$NON-NLS-1$
            self.ftpUsername = _winreg.QueryValueEx(fileUploadHandle, u"Username")[0] #$NON-NLS-1$
            # create id for FTP
            self.ftpId = u"FTPID-%s-%s-%s-%s" % (self.ftpServer, self.ftpPath, self.ftpUrl, self.ftpUsername) #$NON-NLS-1$
        _winreg.CloseKey(credsHandle)
        self.categories = []
        try:
            catsHandle = _winreg.OpenKey(handle, u"Categories") #$NON-NLS-1$

            (numSubKeys, b, c) = _winreg.QueryInfoKey(catsHandle) #@UnusedVariable
            for index in range(0, numSubKeys):
                subKey = _winreg.EnumKey(catsHandle, index)
                catHandle = _winreg.OpenKey(catsHandle, subKey)
                catName = _winreg.QueryValueEx(catHandle, u"Name")[0] #$NON-NLS-1$
                self.categories.append( (subKey, catName) )
                _winreg.CloseKey(catHandle)
            _winreg.CloseKey(catsHandle)
        except:
            pass
    # end __init__()

    def __str__(self):
        return u"LiveWriterBlog[ID: %s, Name: %s, Type: %s, Url: %s, Api: %s, ProviderId: %s, ServiceName: %s" % ( self.blogId, self.blogName, self.clientType, self.homepageUrl, self.postApiUrl, self.providerId, self.serviceName ) #$NON-NLS-1$
    # end __str__()

# end ZWindowsLiveWriterBlogInfo


# ------------------------------------------------------------------------------
# Extension to base blog account class to override some methods that don't make
# sense at this level.
# ------------------------------------------------------------------------------
class ZWindowsLiveWriterAccount(ZBlogAccount):

    def __init__(self, accountDirectory):
        ZBlogAccount.__init__(self, accountDirectory)
    # end __init__()

    def _createPreferences(self):
        return IZUserPreferences()
    # end _createPreferences()

    def _createBlogPreferences(self, blog): #@UnusedVariable
        return IZUserPreferences()
    # end _createBlogPreferences()

# end ZWindowsLiveWriterAccount


# ------------------------------------------------------------------------------
# Base class for Windows Live Writer importers.
# ------------------------------------------------------------------------------
class ZAbstractWLWProfileImporter(ZAbstractProfileImporter):

    def __init__(self, pathToWLWProfile, pathToRavenProfile, systemProfile):
        ZAbstractProfileImporter.__init__(self, pathToWLWProfile, pathToRavenProfile, systemProfile)
    # end __init__()

# end ZAbstractWLWProfileImporter


# ------------------------------------------------------------------------------
# Importer that imports the Windows Live Writer information into the new Raven
# profile.
# ------------------------------------------------------------------------------
class ZLiveWriterProfileImporter(ZAbstractWLWProfileImporter):

    def __init__(self, pathToWLWProfile, pathToRavenProfile, systemProfile):
        if not pathToWLWProfile:
            self._getDefaultWLWProfilePath()
        ZAbstractWLWProfileImporter.__init__(self, pathToWLWProfile, pathToRavenProfile, systemProfile)
        self.accountDir = self._getRavenAccountDir()
        self.wlwBlogs = self._loadLiveWriterBlogsFromRegistry()
    # end __init__()

    def _getDefaultWLWProfilePath(self):
        osutil = getOSUtil()
        return os.path.join(osutil.getApplicationDataDirectory(), u"Windows Live Writer") #$NON-NLS-1$
    # end _getDefaultWLWProfilePath()

    def _openRootRegistryKey(self):
        import _winreg
        try:
            return _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, u"Software\\Microsoft\\Windows Live\\Writer\\Weblogs") #$NON-NLS-1$
        except:
            return _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, u"Software\\Windows Live Writer\\Weblogs") #$NON-NLS-1$
    # end _openRootRegistryKey()

    def _loadLiveWriterBlogsFromRegistry(self):
        factory = ZOSUtilFactory()
        if not factory._isWin32():
            return []

        blogs = []
        osutil = factory.createOSUtil()
        self.wlwDirectory = os.path.join(osutil.getApplicationDataDirectory(), u"Windows Live Writer") #$NON-NLS-1$
        try:
            import _winreg
            rootHandle = self._openRootRegistryKey()
            (numSubKeys, b, c) = _winreg.QueryInfoKey(rootHandle) #@UnusedVariable
            for index in range(0, numSubKeys):
                subKey = _winreg.EnumKey(rootHandle, index)
                wlwBlogInfo = self._loadLiveWriterBlog(rootHandle, subKey)
                if wlwBlogInfo:
                    blogs.append(wlwBlogInfo)
            _winreg.CloseKey(rootHandle)
        except:
            pass
        return blogs
    # end _loadLiveWriterBlogsFromRegistry()

    def _loadLiveWriterBlog(self, handle, subKey):
        import _winreg
        try:
            subHandle = _winreg.OpenKey(handle, subKey)
            wlwBlogInfo = ZWindowsLiveWriterBlogInfo(subHandle)
            _winreg.CloseKey(subHandle)
            return wlwBlogInfo
        except:
            return None
    # end _loadLiveWriterBlog()

    def _runImport(self):
        for wlwBlog in self.wlwBlogs:
            account = self._createAccountFromWLWBlogInfo(wlwBlog)
            ZAccountSerializerFactory().getSerializer().serialize(account)
            self._notifyWorkDone(1, _extstr(u"wlwimporter.ImportedWLWBlogMsg") % account.getBlogs()[0].getName()) #$NON-NLS-1$

            # FIXME (EPW) also import templates
    # end _runImport()

    def _createAccountFromWLWBlogInfo(self, wlwBlogInfo):
        accountId = generate()
        accountDir = os.path.join(self.accountDir, accountId)
        account = ZWindowsLiveWriterAccount(accountDir)
        account.setId(accountId)
        account.setUsername(wlwBlogInfo.username) 
        (siteName, siteId) = LIVE_WRITER_PROVIDER_MAP[wlwBlogInfo.providerId] #@UnusedVariable
        # Over rides fop WP 2.2
        if wlwBlogInfo.clientType == u"WordPress" and wlwBlogInfo.serviceName == u"WordPress": #$NON-NLS-1$ #$NON-NLS-2$
            siteId = u"zoundry.blogapp.pubsystems.publishers.site.wordpress22" #$NON-NLS-1$
        apiInfo = ZAccountAPIInfo()
        apiInfo.setType(siteId)
        apiInfo.setUrl(wlwBlogInfo.postApiUrl)
        account.setAPIInfo(apiInfo)
        account.setName(wlwBlogInfo.blogName + u" Account") #$NON-NLS-1$

        blog = ZBlogFromAccount()
        blog.setAccount(account)
        blogId = u"{urn:zoundry:acc:%s}%s" % (account.getId(), wlwBlogInfo.blogId) #$NON-NLS-1$
        blog.setId(blogId)
        blog.setName(wlwBlogInfo.blogName)
        blog.setUrl(wlwBlogInfo.homepageUrl)

        # set WLW import attributes
        blog.setAttribute(u"clientType", unicode(wlwBlogInfo.clientType), IZBlogAppNamespaces.WLW_ACCOUNT_NAMESPACE) #$NON-NLS-1$
        blog.setAttribute(u"serviceName", unicode(wlwBlogInfo.serviceName), IZBlogAppNamespaces.WLW_ACCOUNT_NAMESPACE) #$NON-NLS-1$
        blog.setAttribute(u"providerId", unicode(wlwBlogInfo.providerId), IZBlogAppNamespaces.WLW_ACCOUNT_NAMESPACE) #$NON-NLS-1$
        blog.setAttribute(u"fileUploadSupport", unicode(wlwBlogInfo.fileUploadSupport), IZBlogAppNamespaces.WLW_ACCOUNT_NAMESPACE) #$NON-NLS-1$
        if wlwBlogInfo.fileUploadSupport == 2:
            blog.setAttribute(u"ftpServer", unicode(wlwBlogInfo.ftpServer), IZBlogAppNamespaces.WLW_ACCOUNT_NAMESPACE) #$NON-NLS-1$
            blog.setAttribute(u"ftpPath", unicode(wlwBlogInfo.ftpPath), IZBlogAppNamespaces.WLW_ACCOUNT_NAMESPACE) #$NON-NLS-1$
            blog.setAttribute(u"ftpUrl", unicode(wlwBlogInfo.ftpUrl), IZBlogAppNamespaces.WLW_ACCOUNT_NAMESPACE) #$NON-NLS-1$
            blog.setAttribute(u"ftpUsername", unicode(wlwBlogInfo.ftpUsername), IZBlogAppNamespaces.WLW_ACCOUNT_NAMESPACE) #$NON-NLS-1$

        blog.setAttribute(u"id", wlwBlogInfo.blogId, IZBlogAppNamespaces.CMS_PUBLISHER_NAMESPACE) #$NON-NLS-1$
        blog.setAttribute(u"name", unicode(wlwBlogInfo.blogName), IZBlogAppNamespaces.CMS_PUBLISHER_NAMESPACE) #$NON-NLS-1$

        if siteId == DefaultSites.BLOGGER:
            # WLW may have the blogger legacy URL. Use the new url for api
            apiInfo.setUrl(u"http://www.blogger.com/feeds/default/blogs") #$NON-NLS-1$
            linkBase = wlwBlogInfo.homepageUrl
            if not linkBase.endswith(u"/"): #$NON-NLS-1$
                linkBase = linkBase + u"/" #$NON-NLS-1$
            feedLink = linkBase + u"feeds/posts/default" #$NON-NLS-1$
            altLink = wlwBlogInfo.homepageUrl
            postLink = wlwBlogInfo.postApiUrl
            catsLink = feedLink
            feedTitle = wlwBlogInfo.blogName
            atomId = wlwBlogInfo.blogId
            blog.setAttribute(u"feed-link", feedLink, IZBlogAppNamespaces.ATOM_PUBLISHER_NAMESPACE) #$NON-NLS-1$
            blog.setAttribute(u"alt-link", altLink, IZBlogAppNamespaces.ATOM_PUBLISHER_NAMESPACE) #$NON-NLS-1$
            blog.setAttribute(u"post-link", postLink, IZBlogAppNamespaces.ATOM_PUBLISHER_NAMESPACE) #$NON-NLS-1$
            blog.setAttribute(u"categories-link", catsLink, IZBlogAppNamespaces.ATOM_PUBLISHER_NAMESPACE) #$NON-NLS-1$
            blog.setAttribute(u"feed-title", feedTitle, IZBlogAppNamespaces.ATOM_PUBLISHER_NAMESPACE) #$NON-NLS-1$
            blog.setAttribute(u"id", atomId, IZBlogAppNamespaces.ATOM_PUBLISHER_NAMESPACE) #$NON-NLS-1$

        for (catId, catName) in wlwBlogInfo.categories:
            category = ZCategory()
            category.setId(catId)
            category.setName(catName)
            blog.addCategory(category)

        account.addBlog(blog)
        # CANNOT CREATE MEDIA STORES HERE: as it needs mediastore service - which is not started until after
        # profile has started (i.e. after profile manager)
        # This part of the code needs to be run after the app has started.

        return account
    # end _createAccountFromWLWBlogInfo()

    def _getWorkAmount(self):
        return len(self.wlwBlogs) * 1
    # end getWorkAmount()

# end ZLiveWriterProfileImporter
