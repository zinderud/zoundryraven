from zoundry.base.util.zdatetime import convertToLocalTime
from zoundry.base.util import dateutil
from zoundry.base.util.classloader import ZClassLoader
from zoundry.base.util.text.unicodeutil import convertToUnicode
from zoundry.base.util.text.unicodeutil import convertToUtf8
from zoundry.base.util.zdatetime import convertToUtcDateTime
from zoundry.base.util.zdatetime import getCurrentUtcDateTime
from zoundry.blogpub.blogserverapi import IZBlogApiParamConstants
from zoundry.blogpub.blogserverapi import IZBlogServerFactory
from zoundry.blogpub.blogserverapi import ZBlogServer
from zoundry.blogpub.blogserverapi import ZServerBlogCategory
from zoundry.blogpub.blogserverapi import ZServerBlogEntry
from zoundry.blogpub.blogserverapi import ZServerBlogInfo
from zoundry.blogpub.blogserverapi import ZServerBlogUser
import zoundry.blogpub.xmlrpc.zpatch.xmlrpclib

#=============================================================
# XML RPC based API for Blog Servers
#=============================================================
# ---------------------------------------------------------
# string conversion
# ---------------------------------------------------------
def toUnicode(s):
    rVal = None
    if s is not None:
        if isinstance(s,basestring):
            rVal = convertToUnicode(s)
        elif isinstance(s, zoundry.blogpub.xmlrpc.zpatch.xmlrpclib.Binary):
            rVal = convertToUnicode(str(s))
        else:
            try:
                rVal = unicode(s)
            except:
                try:
                    rVal = convertToUnicode(str(s))
                except:
                    pass
    if rVal:
        return rVal
    else:
        return u"" #$NON-NLS-1$
# end toUnicode()

def toUtf8(s):
    if s is not None and isinstance(s,basestring):
        return convertToUtf8(s)
    else:
        try:
            return convertToUtf8(unicode(s))
        except:
            try:
                return str(s)
            except:
                return s

#=============================================================
# Blog info impl.
#=============================================================
class ZXmlRpcBlogInfo (ZServerBlogInfo):

    def __init__(self, id, name, url):
        ZServerBlogInfo.__init__(self, id, name, url)
# end ZXmlRpcBlogInfo


#=============================================================
# User info impl.
#=============================================================
class ZXmlRpcUser(ZServerBlogUser):

    def __init__(self, id, name, email = u""):  #$NON-NLS-1$:
        ZServerBlogUser.__init__(self, id, name, email)
# end  ZXmlRpcUser

#=============================================================
# Category impl.
#=============================================================
class ZXmlRpcCategory(ZServerBlogCategory):

    def __init__(self, id, name):
        ZServerBlogCategory.__init__(self, id, name)
# end ZXmlRpcCategory

#=============================================================
# Entry impl.
#=============================================================
class ZXmlRpcEntry(ZServerBlogEntry):

    def __init__(self, id = None):
        ZServerBlogEntry.__init__(self, id)
        self.haveCategoryList = False
        self.description = None
        self.textMore = None
        self.allowPings = False
        self.allowComments = False

    def hasCategories(self):
        return self.haveCategoryList

    def setHasCategories(self, haveCategoryList):
        self.haveCategoryList = haveCategoryList

# end  ZXmlRpcEntry

#=============================================================
# server api def.
#=============================================================
class ZXmlRpcServer(ZBlogServer):


    def __init__(self, apiUrl, username, password, version = None, name =  u"ZXmlRpcServer"): #$NON-NLS-1$
        ZBlogServer.__init__(self,apiUrl, username, password, version, name)
        # category map blogId:ListOfCategories
        self.categoryListMap = {}
        # map of maps -> map blogId : map_of{catName:ZXmlRpcCategory object)
        self.categoryNameMap = {}
        self.connected = False

    def _getBoolean(self, value):
        # some servers return string true/false instead of xmlrpc::boolean struct.
        # we need to handle this case by checking for string instance.
        rVal = value
        if value and isinstance(value, basestring):
            try:
                if value.lower().strip() == u"true" or value.lower().strip() == u"1": #$NON-NLS-1$ #$NON-NLS-2$
                    rVal = True
                else:
                    rVal = False
            except:
                pass
        return rVal

    def _toLowerCaseMap(self, map):
        # returns map where the key name is in lower case.
        rVal = None
        try:
            rVal = {}
            for (key, value) in map.iteritems():
                if isinstance(key,basestring):
                    rVal[ key.strip().lower() ] = value
                else:
                    rVal[ key ] = value
        except:
            rVal = map
        return rVal

    def _setConnected(self, bConnected):
        self.connected = bConnected

    def _isConnected(self):
        return self.connected

    def _toRpcDateTime(self, date):
        u"""Converts the given date time to xml-rpc UTC time object.""" #$NON-NLS-1$
        date = convertToUtcDateTime(date)
        format = self._getParameters().getParameter(IZBlogApiParamConstants.DATEFORMAT_OUT)
        if not format:
            format = u"%Y%m%dT%H:%M:%SZ"  #$NON-NLS-1$
        # if not UTC, use local time
        if not format.endswith(u"Z"): #$NON-NLS-1$
            date = convertToLocalTime(date)
        xdts = date.strftime(str(format))
        xdt = zoundry.blogpub.xmlrpc.zpatch.xmlrpclib.DateTime(xdts)
        return xdt

    def _fromRpcDateTime(self, rpcDateTimeStr):
        u"""Converts the xml rpc date time string to datetime.datetime object.""" #$NON-NLS-1$
        # eg: 20050417T09:57:06  (Wordpress - it does not have time zone though it returns zulu time)
        # eg: 2005-07-29T01:47:13Z (Typepad)
        # eg: 2005-03-25T01:21:54Z (another Typepad for 2005-03-24T20:21:54-05:00 local time))

        # FIXME (PJ) use params to figure out if the dateformat needs to be overridden and handle cases where incoming time is in local tz (eg LiveJournal)
        schemaDateTime = dateutil.getIso8601Date( toUnicode(rpcDateTimeStr) )
        if schemaDateTime:
            return schemaDateTime.getDateTime()
        else:
            return getCurrentUtcDateTime()

    def _resolveRelativeUrl(self, url):
        u"""If the url is relative (starts with /), then an absolute path is created based on the xmlrpc server host.""" #$NON-NLS-1$
        if url and url.startswith(u"/"): #$NON-NLS-1$
            url = self.getBaseUrl().rstrip(u"/") + u"/" + url.lstrip(u"/")      #$NON-NLS-3$ #$NON-NLS-2$ #$NON-NLS-1$
        return url

    def _checkUrl(self, url):
        url = self._resolveRelativeUrl(url)
        if url and not (url.lower().startswith(u"http://") or url.lower().startswith(u"https://") ): #$NON-NLS-2$ #$NON-NLS-1$
            url = u"http://" + url #$NON-NLS-1$
        return url

    def _createEntryFromRpcResult(self, blogId, map = {}, blogEntryId = None): #@UnusedVariable  #@UnusedVariable
        u"""Creates a XmlRpcEntry object given the raw post data from the xml-rpc result.""" #$NON-NLS-1$
        self._debug(u"Warning - base _createEntryFromRpcResult() method called.") #$NON-NLS-1$
        return None

    def _getCachedCategoryList(self, blogId):
        if self.categoryListMap and self.categoryListMap.has_key(blogId) :
            return self.categoryListMap[blogId]
        else:
            return None

    def _getCategoryById(self, blogId, catId):
        catList = self.getCategories(blogId)
        for cat in catList:
            if cat.getId() == catId:
                return cat
        return None

    def _getCategoryByName(self, blogId, catName):
        self.getCategories(blogId)
        if not self.categoryNameMap.has_key(blogId):
            return None
        nameMap = self.categoryNameMap[blogId]
        if not catName or not nameMap.has_key(catName.strip()):
            return None
        category = nameMap[catName.strip()]
        return category

    def _createCategoryByName(self, blogId, catName):
        category = self._getCategoryByName(blogId, catName)
        cloneCat = None
        if category:
            cloneCat = ZXmlRpcCategory( category.getId(), category.getName() )
        return cloneCat

    def _createCategoryListFromNames(self, blogId, catNames):
        u"""Creates the XmlRpcCategory list given the list of category names.""" #$NON-NLS-1$
        # load list
        self.getCategories(blogId)
        retList = []
        for catName in catNames:
            if not catName or len(catName.strip()) == 0:
                continue
            c =  self._createCategoryByName(blogId, toUnicode(catName.strip()))
            if c:
                retList.append(c)
        return retList

    def _createCategoryListFromIds(self, blogId, idList):
        u"""Creates the XmlRpcCategory list given the list of category ids.""" #$NON-NLS-1$
        self.getCategories(blogId)
        retList = []
        for catId in idList:
            c = self._getCategoryById(blogId, catId)
            if c:
                c =  self._createCategoryByName(blogId, c.getName() )
                if c:
                    retList.append(c)
        return retList

    def _getBlogUrl(self, blogId):
        blog = self._getBlogByID(blogId)
        if blog:
            return blog.getUrl()
        else:
            return u"" #$NON-NLS-1$

    def _getPostUrl(self, blogId, url = None):
        u"""Checks if post url is in proper format, if not attempts to fix it.
         If post url is not available, then the blog url is used.""" #$NON-NLS-1$
        if url and url.strip() != u"":             #$NON-NLS-1$
            url = toUnicode( url.strip() )
        elif url:
            url = None
        if url and url == u"link":  #$NON-NLS-1$
            # SquareSpace.com sends only 'link' for url.
            url = None
        rVal = None
        if url and (url.lower().startswith(u"http://") or url.lower().startswith(u"https://")): #$NON-NLS-2$ #$NON-NLS-1$
            # url is ok - use as is.
            rVal =  url
        elif url and url.startswith(u"/"): #$NON-NLS-1$
            # relative url?
            blogUrl = self._getBlogUrl(blogId)
            rVal = blogUrl.rstrip(u"/") + url #$NON-NLS-1$
        elif url and url != u"":   #$NON-NLS-1$
            # url does not start with http or https
            rVal = u"http://" + url             #$NON-NLS-1$
        else:
            # url not given - use blog url
            rVal = self._getBlogUrl(blogId)
        return rVal

    def _getPostIdFromRpcResponse(self, rpcResult, defaultPostId = None):
        u"""Returns the postID or postid parameter the map (case-insensitive).""" #$NON-NLS-1$
        postId = None
        if rpcResult:
            try:
                for k in rpcResult.iterkeys():
                    if k and k.lower() == u"postid" and rpcResult[k] and rpcResult[k].strip() != u"": #$NON-NLS-2$ #$NON-NLS-1$
                        postId = toUnicode( rpcResult[k].strip() )
                        break
            except:
                pass

        if not postId:
            if not defaultPostId:
                self._error(u"postId attribute not found.") #$NON-NLS-1$
                return None
            else:
                self._warning(u"postId attribute not found. Using default/known id %s " % defaultPostId) #$NON-NLS-1$
                postId = defaultPostId
        return postId

    def _checkEntryUrl(self, blogId, url):
        url = self._getPostUrl(blogId, url)
        # convert entities to normal characters. ZDom will reconvert to entities when using Node.setAttribute()
        # (this avoids double escape of entitity characters)
        if url:
            url = url.replace(u"&amp;", u"&")  #$NON-NLS-2$ #$NON-NLS-1$
        return url

    def _getDefaultUser(self):
        u"""Return first XmlRpcUser found. If a user is not found then returns None.""" #$NON-NLS-1$
        list = self.getUsers()
        if len(list) > 0:
            return list[0]
        raise None
    # end getDefaultUser()

    def _getUserByID(self, userId):
        u"""Return user object given userid. If the user is not found then returns None.""" #$NON-NLS-1$
        list = self.getUsers()
        for u in list:
            if u.getId() == userId:
                return u
        raise None
    # end getUserByID()

    def _getBlogByID(self, blogId):
        u"""Return the blog given blog id None if a blog is not found.""" #$NON-NLS-1$
        blogList = self.getBlogs()
        for blog in blogList:
            if blog.getId() == blogId:
                return blog
        self._debug(u"Blog not found for id " + blogId) #$NON-NLS-1$
        # if default - first available
        if len(blogList) > 0:
            b = blogList[0]
            self._debug(u"Using default blog with id " + b.getId()) #$NON-NLS-1$
            return b
        self._debug(u"Returning None for blogid " + blogId) #$NON-NLS-1$
        return None
    # end getBlogByID()

    def _connect(self):
        u"""Connect to the server""" #$NON-NLS-1$
        pass

    def getUsers(self):
        u""" Return list of users (XmlRpcUser)""" #$NON-NLS-1$
        self._debug(u"Warning - base getUsers() method called.") #$NON-NLS-1$
        return []

    def getBlogs(self):
        u"""Return list of Blog entries (XmlRpcBlog)""" #$NON-NLS-1$
        self._debug(u"Warning - base getBlogs() method called.") #$NON-NLS-1$
        return []

    def post(self, blogId, rpcEntry, editMode, draftMode):  #@UnusedVariable  #@UnusedVariable #@UnusedVariable  #@UnusedVariable
        u"""Post and returns true if successful.""" #$NON-NLS-1$
        self._debug(u"Warning - base post() method called.") #$NON-NLS-1$
        return False

    def getPost(self, blogId, blogEntryId):  #@UnusedVariable  #@UnusedVariable
        u"""Returns a specific post or None if failed.""" #$NON-NLS-1$
        self._debug(u"Warning - base getPost() method called.") #$NON-NLS-1$
        return None


    def deletePost(self, blogId, blogEntryId):  #@UnusedVariable #@UnusedVariable
        u"""Deletes the given post. Returns true on success""" #$NON-NLS-1$
        self._debug(u"Warning - base deletePost() method called.") #$NON-NLS-1$
        return False

    def getRecentPosts(self, blogId, numPosts = 100):  #@UnusedVariable  #@UnusedVariable
        u"""Return list of recent posts as XmlRpcEntry objects""" #$NON-NLS-1$
        self._debug(u"Warning - base getRecentPosts() method called.") #$NON-NLS-1$
        return []

    def getCategories(self, blogId):  #@UnusedVariable
        u"""Return list of XmlRpcCategory objects for the given blog id""" #$NON-NLS-1$
        self._debug(u"Warning - base getCategories() method called.") #$NON-NLS-1$
        return []

    def getTemplate(self, blogId, templateId = None):  #@UnusedVariable #@UnusedVariable
        u"""Return template if available or None otherwise""" #$NON-NLS-1$
        self._debug(u"Warning - base getTemplate() method called.") #$NON-NLS-1$
        return None

    def uploadFile(self, blogId, srcFile, destName, izMediaUploadListener = None):  #@UnusedVariable #@UnusedVariable #@UnusedVariable  #@UnusedVariable
        u"""Uploads a given file and returns the IZBlogMediaServerUploadResult or None if failed.""" #$NON-NLS-1$
        self._debug(u"Warning - base uploadFile() method called.") #$NON-NLS-1$
        return None

# end ZXmlRpcServer


class ZXmlRpcServerFactory(IZBlogServerFactory):

    def createServer(self, properties): #@UnusedVariable
        u"""createServer(dict) ->  ZXmlRpcServer
        Creates and returns an xmlrpc server."""#$NON-NLS-1$
        className = properties[IZBlogApiParamConstants.SERVER_CLASSNAME]
        url = properties[IZBlogApiParamConstants.API_ENDPOINT_URL]
        username = properties[IZBlogApiParamConstants.API_USERNAME]
        password = properties[IZBlogApiParamConstants.API_PASSWORD]
        version = None
        if properties.has_key(IZBlogApiParamConstants.API_CLIENT_VERSION):
            version = properties[IZBlogApiParamConstants.API_CLIENT_VERSION]
        # Load class
        serverClass = ZClassLoader().loadClass(className)
        # Create new instance, with url = base data dir.
        server = serverClass(url, username, password,version)
        return server
    #end createServer
#end ZXmlRpcServerFactory