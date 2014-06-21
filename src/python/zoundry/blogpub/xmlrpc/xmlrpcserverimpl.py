from zoundry.blogpub.blogserverapi import IZBlogApiParamConstants
from zoundry.base.util.text.textutil import getSafeString
from mimetypes import guess_type
from zoundry.blogpub.blogserverapi import ZBlogMediaServerUploadResult
from zoundry.base.util.text.textutil import getNoneString
from zoundry.blogpub.namespaces import IZBlogPubTagwordNamespaces
from zoundry.blogpub.fotobilder import ZFotoBilderServer
from zoundry.base.util.streamutil import ZStreamWrapper
from zoundry.base.util.zdatetime import convertToLocalTime
from zoundry.base.util.zdatetime import getCurrentLocalTime
from zoundry.blogpub.blogserverapi import IZBlogApiCapabilityConstants
from zoundry.blogpub.blogserverapi import ZBlogServerException
from zoundry.blogpub.namespaces import IZBlogPubAttrNamespaces
from zoundry.blogpub.xmlrpc.transferlistener import ZMetawblogMediaUploadListenerAdapter
from zoundry.blogpub.xmlrpc.xmlrpcapi import ZXmlRpcBlogInfo
from zoundry.blogpub.xmlrpc.xmlrpcapi import ZXmlRpcCategory
from zoundry.blogpub.xmlrpc.xmlrpcapi import ZXmlRpcEntry
from zoundry.blogpub.xmlrpc.xmlrpcapi import ZXmlRpcServer
from zoundry.blogpub.xmlrpc.xmlrpcapi import ZXmlRpcUser
from zoundry.blogpub.xmlrpc.xmlrpcapi import toUnicode, toUtf8
import httplib
import md5
import os
import re
import socket
import zoundry.blogpub.xmlrpc.zpatch.xmlrpclib

#=============================================================
# Regular expresssions for Blogger v1 API
#=============================================================
CONTENT_TITLE_PATTERN = r'<title[^<>]*?>(.*?)</title[^<>]*?>' #$NON-NLS-1$
CONTENT_TITLE_RE = re.compile(CONTENT_TITLE_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
CONTENT_CATS1_PATTERN = r'<category[^<>]*?>(.*?)</category[^<>]*?>' #$NON-NLS-1$
CONTENT_CATS1_RE = re.compile(CONTENT_CATS1_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
CONTENT_CATS2_PATTERN = r'<categories[^<>]*?>(.*?)</categories[^<>]*?>' #$NON-NLS-1$
CONTENT_CATS2_RE = re.compile(CONTENT_CATS2_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
CONTENT_BODY_PATTERN = r'<body[^<>]*?>(.*?)</body[^<>]*?>' #$NON-NLS-1$
CONTENT_BODY_RE = re.compile(CONTENT_BODY_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
CONTENT_MORE_PATTERN = r'<more[^<>]*?>(.*?)</more[^<>]*?>' #$NON-NLS-1$
CONTENT_MORE_RE = re.compile(CONTENT_MORE_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
CONTENT_HOMETEXT_PATTERN = r'<hometext[^<>]*?>(.*?)</hometext[^<>]*?>' #$NON-NLS-1$
CONTENT_HOMETEXT_RE = re.compile(CONTENT_HOMETEXT_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
CONTENT_MORETEXT_PATTERN = r'<moretext[^<>]*?>(.*?)</moretext[^<>]*?>' #$NON-NLS-1$
CONTENT_MORETEXT_RE = re.compile(CONTENT_MORETEXT_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)

TITLE_RE_LIST = [CONTENT_TITLE_RE]
CAT_RE_LIST = [CONTENT_CATS1_RE, CONTENT_CATS2_RE]
BODY_RE_LIST = [CONTENT_BODY_RE, CONTENT_MORE_RE, CONTENT_HOMETEXT_RE, CONTENT_MORETEXT_RE]

#=============================================================
# Regular expresssion for text-more tag
#=============================================================

EXTENDED_ENTRY_COMMENT_PATTERN = u'''<!--\s*more\s*-->''' #$NON-NLS-1$
EXTENDED_ENTRY_COMMENT_RE = re.compile(EXTENDED_ENTRY_COMMENT_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE)


def hasMetaData(content):
    u"Returns true if the post body content has meta data." #$NON-NLS-1$
    if not content or content.strip() == u"": #$NON-NLS-1$
        return False #$NON-NLS-1$
    content = content.strip()
    reList = []
    reList.extend(TITLE_RE_LIST)
    reList.extend(CAT_RE_LIST)
    reList.extend(BODY_RE_LIST)
    for reExpr in reList:
        if reExpr.findall(content):
            return True
    return False

def extractMetaData(content, rpcEntry):
    u"""Extracts meta data (e.g. title)""" #$NON-NLS-1$
    if not content or content.strip() == u"": #$NON-NLS-1$
        return
    content = content.strip()

    prevContent = rpcEntry.getContent()
    prevTitle = rpcEntry.getTitle()

    # if title is present, then extract the title.
    # exract title
    title = u"" #$NON-NLS-1$
    for reExpr in TITLE_RE_LIST:
        findList = reExpr.findall(content)
        if findList:
            s = findList[0]
            content = reExpr.sub(u"" , content) #$NON-NLS-1$
            if s and s.strip() != u"": #$NON-NLS-1$
                title = title + s + u" " #$NON-NLS-1$
    title = title.strip()
    if title != u"" and (not prevTitle or prevTitle.strip() == u""): #$NON-NLS-2$ #$NON-NLS-1$
        rpcEntry.setTitle(title)

    # strip categories
    for reExpr in CAT_RE_LIST:
        findList = reExpr.findall(content)
        if findList:
            content = reExpr.sub(u"" , content) #$NON-NLS-1$
    # extract body content
    htmlList = []
    for reExpr in BODY_RE_LIST:
        findList = reExpr.findall(content)
        if findList:
            s = findList[0]
            content = reExpr.sub(u"" , content) #$NON-NLS-1$
            if s and s.strip() != u"": #$NON-NLS-1$
                htmlList.append(s)
    # replace content is content if need after removing meta tags.
    if htmlList and (not prevContent or prevContent.strip() == u""): #$NON-NLS-1$
        htmlList.reverse()
        rpcEntry.setContent( u"<br/>".join( htmlList ))  #$NON-NLS-1$
    elif (not prevContent or prevContent.strip() == u""): #$NON-NLS-1$
        rpcEntry.setContent(content)
#===================================================
# XML RPC related base exception
#===================================================

class ZXmlRpcException(ZBlogServerException):

    def __init__(self, rootCause = None, stage = u"", message = u"", code = 0):  #$NON-NLS-1$  #$NON-NLS-2$
        ZBlogServerException.__init__(self, rootCause, stage, message, code)

    def _analyze(self):
        if not self.rootCause:
            self.type = u"Publishing Error" #$NON-NLS-1$

        elif isinstance(self.rootCause,socket.error):
            self.code = 0
            self.type = u"Socket Error" #$NON-NLS-1$
            self.message = toUnicode(self.rootCause)

        elif isinstance(self.rootCause,httplib.HTTPException):
            self.code = 0
            self.type = u"HTTP Error" #$NON-NLS-1$
            self.message = toUnicode(self.rootCause)

        elif isinstance(self.rootCause,zoundry.blogpub.xmlrpc.zpatch.xmlrpclib.ProtocolError):
            self.code = self.rootCause.errcode
            self.type = u"XMLRPC Protocol Error" #$NON-NLS-1$
            self.message = self.rootCause.errmsg + u"(" + self.rootCause.url + u")" #$NON-NLS-1$ #$NON-NLS-2$

        elif isinstance(self.rootCause,zoundry.blogpub.xmlrpc.zpatch.xmlrpclib.Fault):
            self.code = self.rootCause.faultCode
            self.type = u"XMLRPC Fault" #$NON-NLS-1$
            self.message = self.rootCause.faultString
# end ZXmlRpcException

class ZXmlRpcGetPostException(ZXmlRpcException):

    def __init__(self, rootCause = None, stage = u"", message = u"", code = 0):  #$NON-NLS-1$  #$NON-NLS-2$
        ZXmlRpcException.__init__(self, rootCause, stage, message, code)

class ZXmlRpcPostException(ZXmlRpcException):
    def __init__(self, rootCause = None, edit = False, blogid = None, postid = None):
        if edit:
            s = u"Editing post-id %s on blog-id %s " % (toUnicode(postid), toUnicode(blogid)) #$NON-NLS-1$
        else:
            s = u"Posting new entry to blog-id %s " % toUnicode(blogid) #$NON-NLS-1$
        ZXmlRpcException.__init__(self, rootCause, stage = s)

class ZXmlRpcDeleteError(ZXmlRpcException):
    def __init__(self, rootCause = None, blogid = None, postid = None):
        s = u"Deleting post-id %s on blog-id %s " % (toUnicode(postid), toUnicode(blogid)) #$NON-NLS-1$
        ZXmlRpcException.__init__(self, rootCause, stage = s)

class ZXmlRpcUploadError(ZXmlRpcException):
    def __init__(self, rootCause = None, message = u"", url = None):  #$NON-NLS-1$
        self.url = url
        ZXmlRpcException.__init__(self, rootCause, message = message, stage = u"Fileupload") #$NON-NLS-1$

    def getUrl(self):
        u"""Returns the calculated remote image url - based on blog url and filename.""" #$NON-NLS-1$
        return self.url


#===================================================
# Base impl class
#===================================================
class ZXmlRpcServerBase(ZXmlRpcServer):


    def __init__(self, apiUrl, username, password, version):
        ZXmlRpcServer.__init__(self,apiUrl, username, password, version)
        self.server = None # xml-rpc server
        self.blogList = None
        self.userList = None
        self._setConnected(False)

    def _connect(self):
        u"""Connect to the server""" #$NON-NLS-1$
        if self._isConnected():
            self.server.setTransportListener(None)
            return
        url = self.getApiUrl()
        self._debug(u"Connecting to " + url) #$NON-NLS-1$
        try:
            self.server = self._createServer(url)
            self._setConnected(True)
        except Exception , e:
            raise
            pe = ZXmlRpcException(e, u"Error creating connecting to " + url) #$NON-NLS-1$
            raise pe
    # end _connect()

    def _createServer(self, url):
        u"""Returns a xml-rpc server""" #$NON-NLS-1$
        # create transport
        transportProxy = None
        verbose = self.isDebug()
        serv = zoundry.blogpub.xmlrpc.zpatch.xmlrpclib.ServerProxy(url, transport = transportProxy, verbose=verbose, zlogger=self.getLogger())
        serv.setClientVersion(self.getVersion())
        serv.setCredentials( self.getUsername(), self.getPassword() )
        return serv
    
    def _getSafeNumPosts(self, numPosts):
        rval = numPosts
        # check for max cap
        maxPostsStr = self._getParameters().getParameter(IZBlogApiParamConstants.MAX_POSTS)
        if maxPostsStr:
            try:
                rval = int(maxPostsStr)
            except:
                pass
        if rval < 1:
            # set minimum
            rval = 1        
        return rval
    # end _getSafeNumPosts

    def getUsers(self):
        u""" Return list of users (XmlRpcUser)""" #$NON-NLS-1$
        if not (self.userList is None):
            return self.userList
        self._connect()
        self.userList = self._getUserList()
        return self.userList

    def _getUserList(self):
        userList = []
        # create a placeholder username
        user = ZXmlRpcUser(u"_userid", u"_username", u"_useremail") #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$
        userList.append(user)
        return userList

    def getBlogs(self):
        u"""Return list of Blog entries (XmlRpcBlog)""" #$NON-NLS-1$
        if not (self.blogList is None):
            return self.blogList
        self._connect()
        xmlrpcResponseList = self._getUserBlogs()
        self.blogList = self._convertUserBlogList(xmlrpcResponseList)
        return self.blogList

    def _getUserBlogs(self):
        u"""Return raw xml-rpc response from server""" #$NON-NLS-1$
        blogs = None
        self._debug(u"getting list of blogs.") #$NON-NLS-1$
        try:
            blogs = self.server.blogger.getUsersBlogs(self._appID, self.getUsername(), self.getPassword() )
        except Exception , e:
            pe = ZXmlRpcException(e, u"blogger.getUsersBlogs", u"xmlrpcapi.error_getting_blog_list_from %s" + self.getApiUrl() ) #$NON-NLS-1$ #$NON-NLS-2$
            raise pe

        if not blogs:
            pe = ZXmlRpcException(stage = u"xmlrpcapi.getbloglist", message = u"xmlrpcapi.blog_list_unavailable_error") #$NON-NLS-1$ #$NON-NLS-2$
            raise pe
        return blogs

    def _convertUserBlogList(self, xmlrpcGetUserBlogsResponseList):
        u"""Return list of Blog entries (XmlRpcBlog) given raw xml-rpc response""" #$NON-NLS-1$
        rVal = []
        for b in xmlrpcGetUserBlogsResponseList:
            # convert map keys to lowercase since some servers use the wrong/mixed case for keys.
            # eg. blogname vs blogName.
            b = self._toLowerCaseMap(b)
            id = None
            name = None
            url = None
            # blogName is per spec. if not available, try 'name'.
            if b.has_key(u'blogname'): #$NON-NLS-1$
                name = toUnicode( b[u'blogname']) #$NON-NLS-1$
            elif b.has_key(u'name'): #$NON-NLS-1$
                name = toUnicode( b[u'name']) #$NON-NLS-1$

            # blogId is per spec. if not available, try 'id'.
            if b.has_key(u'blogid'):  #$NON-NLS-1$
                id = toUnicode( b[u'blogid']) #$NON-NLS-1$
            elif b.has_key(u'id'): #$NON-NLS-1$
                id = toUnicode( b[u'id']) #$NON-NLS-1$

            if not name and id:
                self._warning(u"Blog %s does not have a name or title." % id) #$NON-NLS-1$
                name = u"[Blog %s]" % id #$NON-NLS-1$

            # 'url' is per spec. if not available, use api url base.
            if b.has_key(u'url'): #$NON-NLS-1$
                url = self._checkUrl( b[u'url']) #$NON-NLS-1$
            else:
                self._warning(u"Blog %s does not have a home page url." % name) #$NON-NLS-1$
                url = self.getBaseUrl()

            # create and add to list.
            zblog = ZXmlRpcBlogInfo(id, name, url)
            rVal.append(zblog)
        # end for  b in blogs
        return rVal

    def uploadFile(self, blogId, srcFile, destName, izMediaUploadListener = None):  #@UnusedVariable #@UnusedVariable #@UnusedVariable  #@UnusedVariable
        if not srcFile or not os.path.exists(srcFile):
            pe = ZXmlRpcException(stage = u"uploadFile", message = u"file not found: %s" % toUnicode(srcFile)) #$NON-NLS-1$ #$NON-NLS-2$
            raise pe
        if not destName or destName.strip() == u"": #$NON-NLS-1$
            destName = os.path.basename(srcFile)
        return self._uploadFile(blogId, srcFile, destName, izMediaUploadListener)

    def _uploadFile(self, blogId, srcFile, destName, izMediaUploadListener = None):  #@UnusedVariable #@UnusedVariable #@UnusedVariable  #@UnusedVariable
        self._debug(u"Warning - base _uploadFile() method called.") #$NON-NLS-1$
        return None

    def _setCustomAttribute(self, attrName, attrNamespace, rpcEntry, rpcMap):
        # extract custom attrs such as wp_author_id
        if attrName and rpcEntry and rpcMap and rpcMap.has_key(attrName):
            rpcEntry.setAttribute(attrName, toUnicode(rpcMap[attrName]), attrNamespace)
    # end _setCustomAttribute()

# end ZXmlRpcServerBase

#===================================================
# Blogger (v2) API
#===================================================
class ZBloggerV2XmlRpcServer(ZXmlRpcServerBase):


    def __init__(self, apiUrl, username, password, version):
        ZXmlRpcServerBase.__init__(self,apiUrl, username, password, version)
        self._setName(u"BloggerV2")  #$NON-NLS-1$
        self._appID = u"urn:zoundry.com:raven:pub:xmlrpc:bloggerv2"  #$NON-NLS-1$
        if self.getVersion():
            self._clientID = self.getVersion()
        else:
            self._clientID = u"ZoundryBlogWriter/Raven" #$NON-NLS-1$


    def post(self, blogId, rpcEntry, editMode, draftMode):
        u"""Post and return true if successful.""" #$NON-NLS-1$
        # see http://www.blogger.com/developers/api/documentation20.html
        self._connect()
        postTitle = toUtf8( rpcEntry.getTitle() )
        # FIXME (PJ) add support to override date format.
        postDate = self._toRpcDateTime( rpcEntry.getUtcDateTime() )
        postEntry = toUtf8( self._formatContentForPublishing( rpcEntry ) )

        postId = u"" #$NON-NLS-1$
        if editMode:
            postId = rpcEntry.getId()

        publish = not draftMode
        # FIXME (PJ) copy categories to list
        catList = []

        # Blogger API v2
        v2Login = {
            u"username" : self.getUsername(), #$NON-NLS-1$
            u"password" : self.getPassword(), #$NON-NLS-1$
            u"appkey" : self._appID, #$NON-NLS-1$
            u"clientID" : self._clientID #$NON-NLS-1$
        }

        v2Options = {
                     u"title" : postTitle, #$NON-NLS-1$
                     u"categories" : catList,  #$NON-NLS-1$
                     u"convertLineBreaks" : u"no",  #$NON-NLS-1$  #$NON-NLS-2$
                     } #$NON-NLS-1$
        v2Post = {
            u"blogID" : toUtf8(blogId), #$NON-NLS-1$
            u"body" : postEntry, #$NON-NLS-1$
            u"title" : postTitle, #$NON-NLS-1$
            u"dateCreated" : postDate, #$NON-NLS-1$
            u"postOptions" : v2Options #$NON-NLS-1$
        }
#        v2EditPost = {
#            u"blogID" : toUtf8(blogId), #$NON-NLS-1$
#            u"postID" : toUtf8(postId), #$NON-NLS-1$
#            u"body" : postEntry, #$NON-NLS-1$
#            u"title": postTitle, #$NON-NLS-1$
#            u"dateCreated" : postDate, #$NON-NLS-1$
#            u"postOptions" : v2Options #$NON-NLS-1$
#        }
        v2Actions = {
                     u"doPublish" : publish, #$NON-NLS-1$
                     u"makeDraft" : draftMode,  #$NON-NLS-1$
                      }

        try:
            editOk = False
            if editMode:
                # FIXME (PJ) use call  blogger2.editPost instead of blogger v1.
                editOk = self.server.blogger.editPost(self._appID, toUtf8(postId), self.getUsername(), self.getPassword(), postEntry, publish)
            else :
                postId = self.server.blogger2.newPost(v2Login, v2Post, v2Actions)

            bOk = False
            postId = toUnicode(postId)
            if not editMode and postId:
                bOk = True
                postId = toUnicode(postId)
                rpcEntry.setId(postId)
                try:
                    # call get post to grab the perm. link
                    pd = self.getPost(blogId, postId)
                    if pd and pd.getUrl():
                        rpcEntry.setUrl(pd.getUrl())
                except:
                    rpcEntry.setUrl( self._getPostUrl(blogId) )

            elif editOk:
                bOk = True
            return bOk

        except Exception, e:
            pe = ZXmlRpcPostException(e, editMode, blogid = blogId, postid = postId)
            raise pe
    # end post()

    def getPost(self, blogId, blogEntryId):
        u"""Returns a specific post as XmlRpcEntry object or None if failed.""" #$NON-NLS-1$
        # see http://www.blogger.com/developers/api/documentation20.html
        self._connect()
        postId = blogEntryId

        # Blogger API v2
        v2Login = {
            u"username": self.getUsername(), #$NON-NLS-1$
            u"password" : self.getPassword(), #$NON-NLS-1$
            u"appkey" : self._appID, #$NON-NLS-1$
            u"clientID" : self._clientID #$NON-NLS-1$
        }
        v2Post = {
            u"blogID" : toUtf8(blogId), #$NON-NLS-1$
            u"postID" : toUtf8(postId) #$NON-NLS-1$
        }

        try:
            retPost = self.server.blogger2.getPost(v2Login, v2Post)
            # sample resp: {'body': 'This is a <strong>Test</strong> post', 'postParams': {'permalinkUrl': '', 'convertLineBreaks': False, 'relatedUrl': '', 'dateCreated': <DateTime u'20050724T12:07:41' at 13d2058>, 'commentsUrl': '', 'allowComments': False, 'draft': False, 'categories': []}, 'postID': '112223206128166858', 'blogID': '6404653', 'title': 'Test Post'}
            entry = self._createEntryFromRpcResult(blogId, retPost, postId)
            return entry
        except Exception, e:
            pe = ZXmlRpcGetPostException(e,u"blogger2.getPost", u"post-id %s" % toUnicode(postId)) #$NON-NLS-1$ #$NON-NLS-2$
            raise pe

    def deletePost(self, blogId, blogEntryId):
        u"""Deletes the given post. Returns true on success""" #$NON-NLS-1$
        self._connect()
        postId = blogEntryId
        rVal = False
        try:
            self._debug(u"calling blogger.deletePost for id " + toUnicode(postId)) #$NON-NLS-1$
            if postId:
                rVal = self._bloggerDeletePost(blogId, toUtf8(postId), self.getUsername(), self.getPassword())
                rVal = self._getBoolean(rVal)
        except Exception, e:
            de = ZXmlRpcDeleteError(e, blogid = blogId, postid = postId)
            raise de
        return rVal

    def _bloggerDeletePost(self, blogId, postId, username, password): #@UnusedVariable
        return self.server.blogger.deletePost(self._appID, postId,username, password, True)
    # end _bloggerDeletePost

    def getRecentPosts(self, blogId, numPosts = 1):
        u"""Return recent posts as a list of XmlRpcEntry items""" #$NON-NLS-1$        
        numPosts = self._getSafeNumPosts(numPosts)
        retList = []
        results = None
        self._connect()
        try:
            results = self.server.blogger.getRecentPosts(self._appID, toUtf8(blogId), self.getUsername(), self.getPassword(), numPosts)
        except Exception, e:
            pe = ZXmlRpcGetPostException(e,u"blogger.getRecentPosts", u"blog-id %s, num-posts %s" % (toUnicode(blogId), toUnicode(numPosts) ) )#$NON-NLS-1$ #$NON-NLS-2$
            raise pe

        if results:
            sz = len(results)
            self._debug(u"Retrieved %s of %s posts from blog-id %s" % ( toUnicode(sz),  toUnicode(numPosts) , toUnicode(blogId)))#$NON-NLS-1$
            for r in results:
                postId = self._getPostIdFromRpcResponse(r)
                if not postId:
                    self._warning(u"A post did not have post-id attribute in blog-id %s" % blogId) #$NON-NLS-1$
                    continue
                # call getPost method since it returns more data.
                entry = self.getPost(blogId, postId)
                if entry:
                    retList.append(entry)
        return retList

    def getTemplate(self, blogId, templateId = None):
        u"""Return template or None if failed.""" #$NON-NLS-1$
        if not templateId:
            templateId = u"main" #$NON-NLS-1$
        results = None
        self._connect()
        try:
            results = self.server.blogger.getTemplate(self._appID, toUtf8(blogId), self.getUsername(), self.getPassword(), templateId)
            results = toUnicode(results)
        except Exception, e:
            pe = ZXmlRpcException(e, stage = u"xmlrpcapi.blogger.getTemplate", message = u"xmlrpcapi.get_template_error") #$NON-NLS-1$ #$NON-NLS-2$
            raise pe

        return results

    def _createEntryFromRpcResult(self, blogId, map = {}, blogEntryId = None):
        u"""Creates a XmlRpcEntry object given the raw post data from the xml-rpc result."""   #$NON-NLS-1$
        postId = self._getPostIdFromRpcResponse(map, blogEntryId)
        if not postId:
            return None

        # sample post result:
        # expect: dateCreated, String userid, String postid, String content;
        # {'status': '1', 'postDate': <DateTime u'20050721T07:05:00' at f6a9e0>, 'url': ' ',
        # 'lastModified': <DateTime u'20050724T09:11:09' at f6af30>, 'userid': '2785438', 'dateCreated': <DateTime u'20050711T05:00:45' at f6afa8>,
        # 'content': 'the content', 'authorName': 'Priyantha', 'postid': '112108324515829473'}

        # Dates
        rpcDateStr = None
        if map.has_key(u'dateCreated'): #$NON-NLS-1$
            rpcDateStr = toUnicode(map[u'dateCreated']) #$NON-NLS-1$
        elif map.has_key(u'datecreated'): #$NON-NLS-1$
            self._warning(u"Response using lowercase attribute 'datecreated' for post-id " % postId) #$NON-NLS-1$
            rpcDateStr = toUnicode(map[u'datecreated']) #$NON-NLS-1$
        elif map.has_key(u'postCreated'): #$NON-NLS-1$
            rpcDateStr = toUnicode(map[u'postCreated']) #$NON-NLS-1$
        elif map.has_key(u'postcreated'): #$NON-NLS-1$
            self._warning(u"Response using lowercase attribute 'u'postcreated' for post-id " % postId) #$NON-NLS-1$
            rpcDateStr = toUnicode(map[u'postcreated']) #$NON-NLS-1$

        # title
        entryTitle = None
        if map.has_key(u'title'):                 #$NON-NLS-1$
            entryTitle =  toUnicode(map[u'title'])#$NON-NLS-1$

        convertLineBreak = False
        draftMode = False
        if map.has_key(u'status') and not map[u'status']: #$NON-NLS-2$ #$NON-NLS-1$
            draftMode = True
        if map.has_key(u'convertLineBreaks') and map[u'convertLineBreaks']: #$NON-NLS-2$ #$NON-NLS-1$
            convertLineBreak = True

        # urls
        entryUrl = None
        if map.has_key(u'postParams'):     #$NON-NLS-1$
            # Blogger V2 data
            # look for permalinkUrl, convertLineBreaks, draft, dateCreated
            retOptions = map[u'postParams'] #$NON-NLS-1$
            if retOptions.has_key(u'permalinkUrl'): #$NON-NLS-1$
                entryUrl = toUnicode(retOptions[u'permalinkUrl']) #$NON-NLS-1$
            elif retOptions.has_key(u'url'):                 #$NON-NLS-1$
                entryUrl = toUnicode(retOptions[u'url']) #$NON-NLS-1$
            if not rpcDateStr and retOptions.has_key(u'dateCreated'): #$NON-NLS-1$
                rpcDateStr = toUnicode(retOptions[u'dateCreated']) #$NON-NLS-1$
            if retOptions.has_key(u'convertLineBreaks') and retOptions[u'convertLineBreaks']: #$NON-NLS-2$ #$NON-NLS-1$
                convertLineBreak = True
            if retOptions.has_key(u'draft') and retOptions[u'draft']: #$NON-NLS-2$ #$NON-NLS-1$
                draftMode = True

        if not entryUrl or entryUrl.strip() == u'': #$NON-NLS-1$
            if map.has_key(u'permalinkUrl'):                 #$NON-NLS-1$
                entryUrl = toUnicode(map[u'permalinkUrl']) #$NON-NLS-1$
            elif map.has_key(u'url'):                 #$NON-NLS-1$
                entryUrl = toUnicode(map[u'url']) #$NON-NLS-1$

        if map.has_key(u'postOptions'):     #$NON-NLS-1$
            # Blogger V2 - another variation
            # FIXME (PJ) check for 'categories'
            retOptions = map[u'postOptions'] #$NON-NLS-1$
            if not entryUrl or entryUrl.strip() == u'' and retOptions.has_key(u'permalinkUrl'):  #$NON-NLS-1$  #$NON-NLS-2$
                entryUrl = retOptions[u'permalinkUrl']  #$NON-NLS-1$
            if not convertLineBreak and retOptions.has_key(u'convertLineBreaks'):  #$NON-NLS-1$  #$NON-NLS-2$
                convertLineBreak = retOptions[u'convertLineBreaks']  #$NON-NLS-1$

        entryUrl = self._checkEntryUrl(blogId, entryUrl) #$NON-NLS-1$
        # content
        entryContent = u"" #$NON-NLS-1$
        if map.has_key(u'content'): #$NON-NLS-1$
            entryContent = toUnicode(map[u'content'])        #$NON-NLS-1$
        elif map.has_key(u'body'):                 #$NON-NLS-1$
            entryContent = toUnicode(map[u'body'])     #$NON-NLS-1$

        entryDate = self._fromRpcDateTime( rpcDateStr )

        entry = ZXmlRpcEntry(postId)
        entry.setTitle(entryTitle)
        entry.setDraft(draftMode)
        entry.setUrl(entryUrl)
        entry.setUtcDateTime(entryDate)
        entry.setContent( entryContent )
        entry.setConvertNewLines(convertLineBreak)

        if hasMetaData(entryContent):
            extractMetaData(entryContent, entry)

        # convert \n with <br/>
        if entry.getContent():
            entry.setContent(entry.getContent().replace(u'&nbsp;', u' ') ) #$NON-NLS-2$ #$NON-NLS-1$

        # FIXME (PJ) move this to blog service/publishing layer
        # if not xhtml, then convertToXhtml,
        # else if convertLineBreak then replace \n with <br/>
        return entry
# end ZBloggerV2XmlRpcServer

#===================================================
# Blogger (v1) API  - the original api
#===================================================
class ZBloggerV1XmlRpcServer(ZBloggerV2XmlRpcServer):


    def __init__(self, apiUrl, username, password, version):
        ZBloggerV2XmlRpcServer.__init__(self,apiUrl, username, password, version)
        self._setName(u"BloggerV1")  #$NON-NLS-1$
        self._appID = u"urn:zoundry.com:raven:pub:xmlrpc:bloggerv1"  #$NON-NLS-1$

    def post(self, blogId, rpcEntry, editMode, draftMode):
        u"""Post and return true if successful.""" #$NON-NLS-1$

        self._connect()
        postTitle = toUtf8( rpcEntry.getTitle() ) #@UnusedVariable
        # FIXME (PJ) add support to override date format.
        postDate = self._toRpcDateTime( rpcEntry.getUtcDateTime() ) #@UnusedVariable
        postEntry = toUtf8( self._formatContentForPublishing( rpcEntry ) )
        # FIXME (PJ) prepend title to content
#         # always append post title
#        titleNode = createHtmlElement(None, u"title", elementText = rpcEntry.title) #$NON-NLS-1$
#        postEntry = toUtf8( titleNode.serialize() + rpcEntry.description)

        postId = u"" #$NON-NLS-1$
        if editMode:
            postId = rpcEntry.getId()

        publish = not draftMode
        if editMode:
            self._debug(u"calling blogger.editPost postId:" + toUnicode(postId)) #$NON-NLS-1$
        else:
            self._debug(u"calling blogger.newPost blogId:" + toUnicode(blogId)) #$NON-NLS-1$


        try:
            editOk = False
            if editMode:
                editOk = self.server.blogger.editPost(self._appID, toUtf8(postId),self.getUsername(), self.getPassword(), postEntry, publish)
            else:
                postId = self.server.blogger.newPost(self._appID, toUtf8(blogId),self.getUsername(), self.getPassword(), postEntry, publish)
                postId = toUnicode(postId)

            bOk = False
            if not editMode and postId:
                bOk = True
                postId = toUnicode(postId)
                rpcEntry.setId(postId)
                try:
                    # call get post to grab the perm. link
                    pd = self.getPost(blogId, postId)
                    if pd and pd.getUrl():
                        rpcEntry.setUrl(pd.getUrl())
                except:
                    rpcEntry.setUrl( self._getPostUrl(blogId) )

            elif editOk:
                bOk = True
            return bOk

        except Exception, e:
            pe = ZXmlRpcPostException(e, editMode, blogid = blogId, postid = postId)
            raise pe
    # end post()


    def getPost(self, blogId, blogEntryId):
        u"""Returns a specific post as XmlRpcEntry object or None if failed.""" #$NON-NLS-1$
        self._connect()
        postId = blogEntryId
        try:
            retPost = self.server.blogger.getPost(self._appID, toUtf8(postId), self.getUsername(), self.getPassword())
            entry = self._createEntryFromRpcResult(blogId, retPost, postId)
            return entry
        except Exception, e:
            pe = ZXmlRpcGetPostException(e,u"blogger.getPost", u"post-id %s" % toUnicode(postId)) #$NON-NLS-1$ #$NON-NLS-2$
            raise pe

    def getRecentPosts(self, blogId, numPosts = 1):
        u"""Return recent posts as a list of XmlRpcEntry items""" #$NON-NLS-1$        
        numPosts = self._getSafeNumPosts(numPosts)
        retList = []
        results = None
        self._connect()
        try:
            results = self.server.blogger.getRecentPosts(self._appID, toUtf8(blogId), self.getUsername(), self.getPassword(), numPosts)
        except Exception, e:
            pe = ZXmlRpcGetPostException(e,u".blogger.getRecentPosts", u"blog-id %s, num-posts %s" % (toUnicode(blogId), toUnicode(numPosts) ) )#$NON-NLS-1$ #$NON-NLS-2$
            raise pe

        if results:
            sz = len(results)
            self._debug(u"Retrieved %s of %s posts from blog-id %s" % ( toUnicode(sz),  toUnicode(numPosts) , toUnicode(blogId)))#$NON-NLS-1$
            for r in results:
                postId = self._getPostIdFromRpcResponse(r)
                if not postId:
                    self._warning(u"A post did not have post-id attribute in blog-id %s" % blogId) #$NON-NLS-1$
                    continue
                entry = self._createEntryFromRpcResult(blogId, r, None)
                if entry:
                    retList.append(entry)
        return retList
#end ZBloggerV1XmlRpcServer

#===================================================
# Metaweblog API
#===================================================
class ZMetaweblogXmlRpcServer(ZBloggerV2XmlRpcServer):

    def __init__(self, apiUrl, username, password, version):
        ZBloggerV2XmlRpcServer.__init__(self,apiUrl, username, password, version)
        self._setName(u"Metaweblog")  #$NON-NLS-1$
        self._appID = u"urn:zoundry.com:raven:pub:xmlrpc:metaweblog"  #$NON-NLS-1$

    def post(self, blogId, rpcEntry, editMode, draftMode):
        return self._post(blogId,rpcEntry,editMode, draftMode)

    def _post(self, blogId, rpcEntry, editMode, draftMode, includeCategories=True,  mtDataMap = {}):
        publishFlag = not draftMode
        postTitle = toUtf8(rpcEntry.getTitle() )
        postEntry = toUtf8(  self._formatContentForPublishing( rpcEntry ) )
        postId = u"0" #$NON-NLS-1$
        if editMode and rpcEntry.getId():
            postId = rpcEntry.getId()

        # modify mt data map if needed
        if not mtDataMap.has_key(u"mt_convert_breaks"):  #$NON-NLS-1$
            mtConvertLinebreaks = u"0" #$NON-NLS-1$
            if rpcEntry.isConvertNewLines():
                mtConvertLinebreaks = u"1" #$NON-NLS-1$
            mtDataMap[u'mt_convert_breaks'] = mtConvertLinebreaks #$NON-NLS-1$
        # tags
        self._convertRavenTags2MtKeywords(rpcEntry, mtDataMap, editMode)

        # Copy custom cms attrs over
        self._copyEntryAttributesToMap(rpcEntry, mtDataMap, IZBlogPubAttrNamespaces.CMS_ATTR_NAMESPACE)

        self._connect()
        postStruct = {}
        for key,value in mtDataMap.iteritems():
            if key and value:
                postStruct[key] = value
        postStruct[u"title"] = postTitle #$NON-NLS-1$
        postStruct[u"description"] = postEntry #$NON-NLS-1$
        supportsExtendedEntry = self._getCapabilities().hasCapability(IZBlogApiCapabilityConstants.EXTENDED_ENTRY)
        if supportsExtendedEntry and postEntry:
            data = EXTENDED_ENTRY_COMMENT_RE.split(postEntry, 1)
            if len(data) == 2:
                postStruct[u"description"] = data[0]  #$NON-NLS-1$
                postStruct[u"mt_text_more"] = data[1] #$NON-NLS-1$

        if rpcEntry.getSummary():
            # FIXME (PJ) used params and capabilities to figure out excerpt field name and support
            postStruct[u'mt_excerpt'] = toUtf8( rpcEntry.getSummary() ) #$NON-NLS-1$

        if rpcEntry.getUtcDateTime():
            postStruct[u'dateCreated'] = self._toRpcDateTime( rpcEntry.getUtcDateTime() ) #$NON-NLS-1$

        if includeCategories and rpcEntry.getCategories() and len(rpcEntry.getCategories()) > 0:
            postCatList = []
            for cat in rpcEntry.getCategories():
                postCatList.append( toUtf8(cat.getName()) )
            postStruct[u'categories'] = postCatList #$NON-NLS-1$

        # key words
        self._convertRavenTags2MtKeywords(rpcEntry, postStruct, editMode)
        # set custom properties, if any.
        self._setCustomPublishProperties(rpcEntry, postStruct)

        if editMode:
            self._debug(u"calling metaWeblog.editPost postId:" + toUnicode(postId)) #$NON-NLS-1$
        else:
            self._debug(u"calling metaWeblog.newPost blogId:" + toUnicode(blogId)) #$NON-NLS-1$

        try:
            editOk = False
            if editMode:
                editOk = self._metaWeblogEditPost(toUtf8(blogId), toUtf8(postId), self.getUsername(), self.getPassword(), postStruct, publishFlag)
            else :
                postId = self._metaWeblogNewPost(toUtf8(blogId), self.getUsername(), self.getPassword(), postStruct, publishFlag)
            bOk = False
            if not editMode and postId and postId != u"": #$NON-NLS-1$
                bOk = True
                postId = toUnicode(postId)
                rpcEntry.setId( postId )
                self._setNewPostUrl(blogId , rpcEntry)
            elif editOk:
                bOk = True
            return bOk
        except Exception, e:
            pe = ZXmlRpcPostException(e, editMode, blogid = blogId, postid = postId)
            raise pe
    # end _post()

    def _setCustomPublishProperties(self, rpcEntry, postStruct): #@UnusedVariable
        # Set custom properties to be published.
        pass
    # end _setCustomProperties

    def _metaWeblogNewPost(self, blogId, username, password, postStruct, publishFlag):
        return self.server.metaWeblog.newPost(blogId, username, password, postStruct, publishFlag)
    # end _metaWeblogNewPost

    def _metaWeblogEditPost(self, blogId, postId, username, password, postStruct, publishFlag): #@UnusedVariable
        return self.server.metaWeblog.editPost(postId, username, password, postStruct, publishFlag)
    # end _metaWeblogEditPost

    def _metaWeblogGetPost(self, blogId, postId, username, password): #@UnusedVariable
        return self.server.metaWeblog.getPost( postId, username, password )
    # end _metaWeblogGetPost()

    def _metaWeblogGetRecentPosts(self, blogId, username, password, numPosts):
        return self.server.metaWeblog.getRecentPosts(blogId, username, password, numPosts)
    # end _metaWeblogGetRecentPosts()

    def _metaWeblogGetCategories(self, blogId, username, password):
        return self.server.metaWeblog.getCategories(blogId, username, password)
    # end _metaWeblogGetCategories()

    def _setNewPostUrl(self, blogId, rpcEntry):
        u"""Sets the post's permalink by downloading the post and using the url attribute from the downloaded post. """ #$NON-NLS-1$
        url = None
        try:
            # call get post to grab the perm. link
            publishedEntry = self.getPost( blogId, rpcEntry.getId() )
            if publishedEntry:
                url = publishedEntry.getUrl()
        except:
            pass
        url = self._getPostUrl(blogId, url)
        rpcEntry.setUrl(url)

    def getPost(self, blogId, blogEntryId):
        postId = blogEntryId
        self._connect()
        try:
            result = self._metaWeblogGetPost( toUtf8(blogId), toUtf8(postId), self.getUsername(), self.getPassword() )
            entry = self._createEntryFromRpcResult(blogId, result, postId)
            return entry
        except Exception, e:
            pe = ZXmlRpcGetPostException(e,u"metaWeblog.getPost", u"post-id %s" % toUnicode(postId)) #$NON-NLS-1$ #$NON-NLS-2$
            raise pe

    def _createEntryFromRpcResult(self, blogId, map = {}, blogEntryId = None):
        u"""Creates a XmlRpcEntry object given the raw post data from the xml-rpc result."""   #$NON-NLS-1$
        postId = self._getPostIdFromRpcResponse(map, blogEntryId)
        if not postId:
            return None

        entryUrl = None
        if map.has_key(u'permaLink'): #$NON-NLS-1$
            entryUrl = self._getPostUrl(blogId, map[u'permaLink']) #$NON-NLS-1$
        elif map.has_key(u'permalink'): #$NON-NLS-1$
            entryUrl = self._getPostUrl(blogId, map[u'permalink']) #$NON-NLS-1$
            self._warning(u"metaweblog.GetPost:: incorrect lowercase key permalink.")  #$NON-NLS-1$
        if not entryUrl and map.has_key(u'link'): #$NON-NLS-1$
            entryUrl = self._getPostUrl(blogId, map[u'link']) #$NON-NLS-1$
        elif not entryUrl and  map.has_key(u'url'): #$NON-NLS-1$
            entryUrl = self._getPostUrl(blogId, map[u'url']) #$NON-NLS-1$

        entryUrl = self._checkEntryUrl(blogId, entryUrl) #$NON-NLS-1$

        entryContent = u"" #$NON-NLS-1$
        if map.has_key(u'description') and map[u'description']: #$NON-NLS-2$ #$NON-NLS-1$
            entryContent = toUnicode(map[u'description']) #$NON-NLS-1$
        # 'mt_text_more'
        if map.has_key(u'mt_text_more') and map[u'mt_text_more']:     #$NON-NLS-2$ #$NON-NLS-1$
            entryContent = entryContent + u"\n<!--more-->\n" + toUnicode(map[u'mt_text_more']) #$NON-NLS-2$ #$NON-NLS-1$

        entrySummary = None
        # FIXME (PJ) used params and capabilities to figure out excerpt field name and support
        if map.has_key(u'mt_excerpt'): #$NON-NLS-1$
            entrySummary = toUnicode(map[u'mt_excerpt']) #$NON-NLS-1$

        entryTitle = None
        if map.has_key(u'title'): #$NON-NLS-1$
            entryTitle = toUnicode(map[u'title']) #$NON-NLS-1$

        rpcDateStr = None
        if map.has_key(u'date_created_gmt'): #$NON-NLS-1$
            rpcDateStr = toUnicode(map[u'date_created_gmt']) #$NON-NLS-1$
            if rpcDateStr.lower().find(u"z") == -1: #$NON-NLS-1$
                rpcDateStr = rpcDateStr + u"Z" #$NON-NLS-1$
        elif map.has_key(u'dateCreated'): #$NON-NLS-1$
            rpcDateStr = toUnicode(map[u'dateCreated']) #$NON-NLS-1$
        elif map.has_key(u'datecreated'): #$NON-NLS-1$
            rpcDateStr = toUnicode(map[u'datecreated']) #$NON-NLS-1$
            self._warning(u"metaweblog.GetPost:: incorrect lowercase key datecreated.")  #$NON-NLS-1$

        entryCategories = None
        if map.has_key(u'categories'): #$NON-NLS-1$
            entryCategories = self._createCategoryListFromNames(blogId, map[u'categories']) #$NON-NLS-1$
        elif map.has_key(u'Categories'): #$NON-NLS-1$
            entryCategories = self._createCategoryListFromNames(blogId, map[u'Categories']) #$NON-NLS-1$
            self._warning(u"metaweblog.GetPost:: incorrect uppercase key Categories.")  #$NON-NLS-1$

        # wp draft option
        postStatus = u"" #$NON-NLS-1$
        if map.has_key(u'wp_post_status') and map[u'wp_post_status']:     #$NON-NLS-2$ #$NON-NLS-1$
            postStatus = toUnicode(map[u'wp_post_status'])         #$NON-NLS-1$
        elif map.has_key(u'post_status') and map[u'post_status']:     #$NON-NLS-2$ #$NON-NLS-1$
            postStatus = toUnicode(map[u'post_status']) #$NON-NLS-1$
        draftMode = False
        if postStatus.lower().find(u"draft") != -1: #$NON-NLS-2$ #$NON-NLS-1$
            draftMode = True

        #FIXME (PJ) get mt attrs mt_keywords, mt_allow_comments[1=open, 2=closed], mt_allow_pings

        # FIXME (PJ) read in ext attrs such as mt_ fields.

        convertLineBreak = False
        if map.has_key(u'mt_convert_breaks'): #$NON-NLS-1$
            s = toUnicode(map[u'mt_convert_breaks']) #$NON-NLS-1$
            if s and (s == u"1" or s.strip().lower() == u"true" or s.strip().lower() == u"yes"): #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$
                convertLineBreak = True

        entryDate = self._fromRpcDateTime( rpcDateStr )
        entry = ZXmlRpcEntry(postId)
        entry.setTitle( entryTitle )
        entry.setDraft( draftMode )
        entry.setUrl( entryUrl )
        entry.setUtcDateTime(entryDate)
        entry.setContent( entryContent )
        entry.setSummary( entrySummary )
        entry.setConvertNewLines( convertLineBreak )
        if entryCategories is not None:
            entry.setHasCategories(True)
            entry.getCategories().extend( entryCategories )

        self._convertMtKeywords2RavenTags(map, entry, None)
        if hasMetaData(entryContent):
            extractMetaData(entryContent, entry)

        if entry.getContent():
            entry.setContent(entry.getContent().replace(u'\r\n', u'\r') ) #$NON-NLS-2$ #$NON-NLS-1$
            entry.setContent(entry.getContent().replace(u'\r', u'\n') ) #$NON-NLS-2$ #$NON-NLS-1$
            entry.setContent(entry.getContent().replace(u'&nbsp;', u' ') ) #$NON-NLS-2$ #$NON-NLS-1$
        # FIXME (PJ) move this to blog service/publishing layer
        # if not xhtml, then convertToXhtml,
        # else if convertLineBreak then replace \n with <br/>
        return entry

    def _convertRavenTags2MtKeywords(self, rpcEntry, postStruct, editMode): #@UnusedVariable
        hastags = rpcEntry.getTagwords() and len( rpcEntry.getTagwords() ) > 0
        if hastags:
            postStruct[u"mt_keywords"] = toUtf8( u",".join(rpcEntry.getTagwords() ) ) #$NON-NLS-2$ #$NON-NLS-1$
        elif not hastags and editMode:
            # clear keywords
            postStruct[u"mt_keywords"] = u"" #$NON-NLS-2$ #$NON-NLS-1$
    # end _convertRavenTags2MtKeywords

    def _convertMtKeywords2RavenTags(self, postStruct, rpcEntry, tagSpace): #@UnusedVariable
        if postStruct.has_key(u"mt_keywords"): #$NON-NLS-1$
            mtkeywords = getNoneString(postStruct[u"mt_keywords"]) #$NON-NLS-1$
            if mtkeywords:
                entryTagwords = mtkeywords.split(u",") #$NON-NLS-1$
                rpcEntry.setTagwords(entryTagwords)
                if tagSpace:
                    rpcEntry.setTagspaceUrl(tagSpace)
    # end _convertMtKeywords2RavenTags

    def getRecentPosts(self, blogId, numPosts = 1):
        numPosts = self._getSafeNumPosts(numPosts)        
        self._connect()
        results = None
        try:
            results = self._metaWeblogGetRecentPosts(toUtf8(blogId), self.getUsername(), self.getPassword(), numPosts)
        except Exception, e:
            pe = ZXmlRpcGetPostException(e,u"metaWeblog.getRecentPosts", u"blog-id %s" % toUnicode(blogId)) #$NON-NLS-1$ #$NON-NLS-2$
            raise pe
        retList = []
        if results:
            for r in results:
                entry = self._createEntryFromRpcResult(blogId, r, None)
                if entry:
                    retList.append(entry)
        return retList


    def getCategories(self, blogId):
        categoryList = self._getCachedCategoryList(blogId)
        if categoryList:
            return categoryList

        self._debug(u"calling metaWeblog.getCategories blogId:" + toUnicode(blogId)) #$NON-NLS-1$

        self._connect()
        results = None
        try:
            results = self._metaWeblogGetCategories(toUtf8(blogId), self.getUsername(), self.getPassword() )
        except Exception, e:
            pe = ZXmlRpcException(e, stage = u"metaWeblog.getCategories", message = u"blog-id %s" % toUnicode(blogId)) #$NON-NLS-1$ #$NON-NLS-2$
            raise pe

        # sample:{'rssUrl': 'http://reviews.zoundry.com/category/uncategorized/feed/',
        #   'htmlUrl': 'http://reviews.zoundry.com/category/uncategorized/',
        #   'categoryId': '1',
        #   'categoryName': 'Uncategorized',
        #    'description': 'Uncategorized'},
        categoryList = []
        nameMap = {}

        if isinstance(results, dict):
            # metaweblog api specs out that categories are returned as dict (but most servers return as a list)
            # convert to a list
            tempList = []
            for key,value in results.iteritems():
                if isinstance(value, dict):
                    # add category name if not present in the map.
                    if key and not value.has_key(u"categoryName"): #$NON-NLS-1$
                        value[u"categoryName"] = key #$NON-NLS-1$
                tempList.append(value)
            results = tempList
        catName = None
        catId = None
        for d in results:
            if not d:
                continue
            # we expect d to be a map containing categoryId, htmlUrl etc.
            # but, some servers implement the API wrong (XOOPS for one)
            # instead, d is a map containing the actual map. So, if this is the case
            # we have to extract the nested map.
            if len(d) == 1:
                # check for nested map.
                temp = d
                (k,v) = d.popitem()
                if isinstance(v, dict):
                    self._warning(u"metaweblog.getCategories:: incorrect server implementation - nested structs.")  #$NON-NLS-1$
                    # if nested map, reassign d to the nested map.
                    d = v
                    # add category name if not present in the map.
                    if not d.has_key(u"categoryName"): #$NON-NLS-1$
                        d[u"categoryName"] = k #$NON-NLS-1$
                else:
                    # restore
                    d = temp

            catName = None
            catId = None
            if d.has_key(u'categoryId'): #$NON-NLS-1$
                catId = toUnicode(d[u'categoryId']) #$NON-NLS-1$
            elif d.has_key(u'categoryid'): #$NON-NLS-1$
                # lowercase version
                catId = toUnicode(d[u'categoryid']) #$NON-NLS-1$
                self._warning(u"metaweblog.getCategories:: incorrect lowercase key categoryid.")  #$NON-NLS-1$
            elif d.has_key(u'categoryID'): #$NON-NLS-1$
                catId = toUnicode(d[u'categoryID']) #$NON-NLS-1$
                self._warning(u"metaweblog.getCategories:: incorrect case key categoryID.")  #$NON-NLS-1$

            elif d.has_key(u'htmlUrl'): #$NON-NLS-1$
                catId = toUnicode(d[u'htmlUrl']) #$NON-NLS-1$
            elif d.has_key(u'htmlurl'): #$NON-NLS-1$
                catId = toUnicode(d[u'htmlurl']) #$NON-NLS-1$
                self._warning(u"metaweblog.getCategories:: incorrect lowercase key htmlurl.")  #$NON-NLS-1$
            elif d.has_key(u'rssUrl'): #$NON-NLS-1$
                catId = toUnicode(d[u'rssUrl'])                 #$NON-NLS-1$
            elif d.has_key(u'rssurl'): #$NON-NLS-1$
                catId = toUnicode(d[u'rssurl'])                 #$NON-NLS-1$
                self._warning(u"metaweblog.getCategories:: incorrect lowercase key rssurl.")  #$NON-NLS-1$

            if d.has_key(u'categoryName'): #$NON-NLS-1$
                catName = toUnicode(d[u'categoryName']) #$NON-NLS-1$
            elif d.has_key(u'categoryname'): #$NON-NLS-1$
                catName = toUnicode(d[u'categoryname']) #$NON-NLS-1$
                self._warning(u"metaweblog.getCategories:: incorrect lowercase key categoryname.")  #$NON-NLS-1$
            elif d.has_key(u'description'): #$NON-NLS-1$
                catName = toUnicode(d[u'description']) #$NON-NLS-1$

            if not catName or catName.strip() == u"": #$NON-NLS-1$
                # cat name or description is required - else skip
                continue
            catName = catName.strip()
            if not catId or catId == u"": #$NON-NLS-1$
                # if catId (based on categoryId, htmlUrl or rssUrl) is not avaialble,
                # then use the catName as id.
                catId = catName

            c = ZXmlRpcCategory(catId, catName)
            categoryList.append(c)
            nameMap[catName] = c
        # end for d in results

        # cache results
        self.categoryListMap[blogId] = categoryList
        self.categoryNameMap[blogId] = nameMap
        return categoryList


    def _uploadFile(self, blogId, srcFile, destName, izMediaUploadListener = None):  #@UnusedVariable #@UnusedVariable #@UnusedVariable  #@UnusedVariable
        self._debug(u"calling metaWeblog.newMediaObject blogId:" + toUnicode(blogId)) #$NON-NLS-1$
        self._connect()
        blogUrl = self._getBlogUrl(blogId)
        medUrl = None
        result = None
        # url to return if upload failed (e.g. server replied with 'file already exists')
        backupUrl = blogUrl.rstrip(u"/") + u"/" + destName #$NON-NLS-1$ #$NON-NLS-2$
        newMediaObjectUploadListener = None
        try:
            mediaBits = None
            if izMediaUploadListener:
                newMediaObjectUploadListener = ZMetawblogMediaUploadListenerAdapter(srcFile, izMediaUploadListener)
            self.server.setTransportListener(newMediaObjectUploadListener)
            # is the file sent as a media repo file reader wrapper.
            if newMediaObjectUploadListener:
                f = file(srcFile, u'rb') #$NON-NLS-1$
                base64InputStream = ZStreamWrapper(f, newMediaObjectUploadListener)
                mediaBits = zoundry.blogpub.xmlrpc.zpatch.xmlrpclib.Binary(fileStream = base64InputStream)
            else:
                # standard filename .
                f = file(srcFile, u'rb') #$NON-NLS-1$
                fileData = f.read()
                f.close()
                mediaBits = zoundry.blogpub.xmlrpc.zpatch.xmlrpclib.Binary(fileData)

            mediaStruct = {
                u'name' : destName,  #$NON-NLS-1$
                u'bits' : mediaBits #$NON-NLS-1$
            }

            result = self.server.metaWeblog.newMediaObject(toUtf8(blogId), self.getUsername(), self.getPassword(), mediaStruct)
            self.server.setTransportListener(None)
            if result and isinstance(result, dict) and result.has_key(u"url"):                 #$NON-NLS-1$
                medUrl = toUnicode(result[u'url']) #$NON-NLS-1$
            elif result and isinstance(result, list) and len(result) > 0:
                medUrl = toUnicode(result[0])
            elif result and isinstance(result, basestring):
                medUrl = toUnicode(result)
        except Exception, e:
            pe = ZXmlRpcUploadError(e, u"file: " + toUnicode(srcFile), url = backupUrl) #$NON-NLS-1$
            if newMediaObjectUploadListener:
                newMediaObjectUploadListener.notifyFailure(pe)
            raise pe
        if not medUrl or len(medUrl.strip()) < 5:
            pe = ZXmlRpcUploadError(message = u"url missing from upload response", url = backupUrl) #$NON-NLS-1$
            if newMediaObjectUploadListener:
                newMediaObjectUploadListener.notifyFailure(pe)
            raise pe
        # replace &amp; with & character.
        medUrl = medUrl.replace(u"&amp;", u"&"); #$NON-NLS-2$ #$NON-NLS-1$
        medUrl = medUrl.strip()
        medUrl = medUrl.lstrip(u"/") #$NON-NLS-1$
        if not medUrl.lower().startswith(u"http://") and not medUrl.lower().startswith(u"https://"): #$NON-NLS-1$ #$NON-NLS-2$
            medUrl = blogUrl.rstrip(u"/") + u"/" + medUrl #$NON-NLS-1$ #$NON-NLS-2$
        return ZBlogMediaServerUploadResult(medUrl)
    # end _uploadFile()

    def getTemplate(self, blogId, templateId = None):    #@UnusedVariable #@UnusedVariable
        # not implemented
        return None
# end ZMetaweblogXmlRpcServer

#===================================================
# WordPress API
#===================================================

class ZWordPressXmlRpcServer(ZMetaweblogXmlRpcServer):

    def __init__(self, apiUrl, username, password, version):
        ZMetaweblogXmlRpcServer.__init__(self,apiUrl, username, password, version)
        self._setName(u"WordPress")  #$NON-NLS-1$
        self._appID = u"urn:zoundry.com:raven:pub:xmlrpc:metaweblog:wordpress"  #$NON-NLS-1$
    # emd __init__()

    def _setCustomPublishProperties(self, rpcEntry, postStruct): #@UnusedVariable
        # Set custom properties to be published.
        s = rpcEntry.getAttribute(u"wp_slug",IZBlogPubAttrNamespaces.WP_ATTR_NAMESPACE) #$NON-NLS-1$
        if getNoneString(s):
            postStruct[u"wp_slug"] = s #$NON-NLS-1$
        s = rpcEntry.getAttribute(u"post_status",IZBlogPubAttrNamespaces.WP_ATTR_NAMESPACE) #$NON-NLS-1$
        if getNoneString(s):
            postStruct[u"post_status"] = s #$NON-NLS-1$
        s = rpcEntry.getAttribute(u"wp_password",IZBlogPubAttrNamespaces.WP_ATTR_NAMESPACE) #$NON-NLS-1$
        postStruct[u"wp_password"] = getSafeString(s) #$NON-NLS-1$        
            
    # end _setCustomProperties

    def _extractWPCustomAttributes(self, rpcEntry, rpcMap):
        attrNames = [u"userid", u"wp_slug", u"wp_password", u"wp_author", u"wp_author_id", u"wp_author_display_name", u"post_status", u"wp_page_template",  #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$ #$NON-NLS-4$ #$NON-NLS-5$ #$NON-NLS-6$ #$NON-NLS-7$ #$NON-NLS-8$
                      u"wp_page_order", u"page_id", u"page_status", u"wp_page_parent_id", u"wp_page_parent_title", u"date_created_gmt"]  #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$ #$NON-NLS-4$ #$NON-NLS-5$ #$NON-NLS-6$
        for attrName in attrNames:
            self._setCustomAttribute(attrName, IZBlogPubAttrNamespaces.WP_ATTR_NAMESPACE, rpcEntry, rpcMap)
    # end _extractWPCustomAttributes

    def _createEntryFromRpcResult(self, blogId, map = {}, blogEntryId = None):
        entry = ZMetaweblogXmlRpcServer._createEntryFromRpcResult(self, blogId, map, blogEntryId)
        self._extractWPCustomAttributes(entry, map)
        entry.setTagspaceUrl(IZBlogPubTagwordNamespaces.WORDPRESS_TAGWORDS_URI)
        return entry
    # end _createEntryFromRpcResult()
# end ZWordPressXmlRpcServer

#===================================================
# WordPress 2.2+ API
#===================================================

class ZWordPress22XmlRpcServer(ZWordPressXmlRpcServer):

    def __init__(self, apiUrl, username, password, version):
        ZWordPressXmlRpcServer.__init__(self,apiUrl, username, password, version)
        self._setName(u"WordPress22")  #$NON-NLS-1$
        self._appID = u"urn:zoundry.com:raven:pub:xmlrpc:metaweblog:wordpress22"  #$NON-NLS-1$
    # end __init__()

    def _getUserBlogs(self):
        xmlrpcGetUserBlogsResponseList = ZWordPressXmlRpcServer._getUserBlogs(self)
        if xmlrpcGetUserBlogsResponseList and len(xmlrpcGetUserBlogsResponseList) == 1:
            b = self._toLowerCaseMap( xmlrpcGetUserBlogsResponseList[0].copy() )
            if b.has_key(u'blogname'): #$NON-NLS-1$
                b[u'blogname'] = u"WP-Pages (%s)" %  toUnicode(b[u'blogname']) #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$
            elif b.has_key(u'name'): #$NON-NLS-1$
                b[u'name'] = u"WP-Pages (%s)" %  toUnicode(b[u'name']) #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$
            # blogId is per spec. if not available, try 'id'.
            blogId = None
            if b.has_key(u'blogid'):  #$NON-NLS-1$
                blogId = b[u'blogid'] #$NON-NLS-1$
                b[u'blogid'] = u"urn:zoundry:wp_pages:%s" % toUnicode( b[u'blogid']) #$NON-NLS-1$ #$NON-NLS-3$ #$NON-NLS-2$
            elif b.has_key(u'id'): #$NON-NLS-1$
                blogId = b[u'id'] #$NON-NLS-1$
                b[u'id'] = u"urn:zoundry:wp_pages:%s" % toUnicode( b[u'id']) #$NON-NLS-1$ #$NON-NLS-3$ #$NON-NLS-2$
            # check if wp api supports pages, if so add psuedo blog named 'page'.
            if blogId:
                try:
                    self.server.wp.getPageList(blogId, self.getUsername(), self.getPassword())
                    xmlrpcGetUserBlogsResponseList.append(b)
                except:
                    # wp server does not support pages api
                    pass
        return xmlrpcGetUserBlogsResponseList
    # end _getUserBlogs

    def _isWpPagesDomain(self, postOrBlogId):
        return postOrBlogId.startswith(u"urn:zoundry:wp_pages:") #$NON-NLS-1$
    # end _isWpPagesDomain()

    def _getWpPagesRawId(self, postOrBlogId):
        if postOrBlogId.startswith(u"urn:zoundry:wp_pages:"): #$NON-NLS-1$
            return postOrBlogId[ len(u"urn:zoundry:wp_pages:")+1:] #$NON-NLS-1$
        else:
            return None
    # end _getWpPagesRawId

    def _getPostIdFromRpcResponse(self, rpcResult, defaultPostId = None):
        # override to use page id if postId is not available.
        postId = ZWordPressXmlRpcServer._getPostIdFromRpcResponse(self, rpcResult, defaultPostId)
        if postId is None and rpcResult.has_key(u"page_id"): #$NON-NLS-1$
            postId = toUnicode(rpcResult[u"page_id"]) #$NON-NLS-1$
        return postId
    # end _getPostIdFromRpcResponse

    def _createEntryFromRpcResult(self, blogId, map = {}, blogEntryId = None):
        entry = ZWordPressXmlRpcServer._createEntryFromRpcResult(self, blogId, map, blogEntryId)
        if entry and self._isWpPagesDomain(blogId):
            entry.setAttribute(u"post_type", u"post_page", IZBlogPubAttrNamespaces.WP_ATTR_NAMESPACE) #$NON-NLS-1$ #$NON-NLS-2$
        return entry
    # end _createEntryFromRpcResult

    def _bloggerDeletePost(self, blogId, postId, username, password):
        pageBlogId = self._getWpPagesRawId(blogId)
        if pageBlogId is not None:
            return self.server.wp.deletePage(pageBlogId, username, password, postId)
        else:
            return ZWordPressXmlRpcServer._bloggerDeletePost(self, blogId, postId, username, password)
    # end _bloggerDeletePost

    def _metaWeblogNewPost(self, blogId, username, password, postStruct, publishFlag):
        pageBlogId = self._getWpPagesRawId(blogId)
        if pageBlogId is not None:
            return self.server.wp.newPage(pageBlogId, username, password, postStruct, publishFlag)
        else:
            return ZWordPressXmlRpcServer._metaWeblogNewPost(self, blogId, username, password, postStruct, publishFlag)
    # end _metaWeblogNewPost

    def _metaWeblogEditPost(self, blogId, postId, username, password, postStruct, publishFlag):
        pageBlogId = self._getWpPagesRawId(blogId)
        if pageBlogId is not None:
            return self.server.wp.editPage(pageBlogId, postId, username, password, postStruct, publishFlag)
        else:
            return ZWordPressXmlRpcServer._metaWeblogEditPost(self, blogId, postId, username, password, postStruct, publishFlag)
    # end _metaWeblogEditPost

    def _metaWeblogGetPost(self, blogId, postId, username, password):
        pageBlogId = self._getWpPagesRawId(blogId)
        if pageBlogId is not None:
            return self.server.wp.getPage(pageBlogId, postId, username, password)
        else:
            return ZWordPressXmlRpcServer._metaWeblogGetPost(self, blogId, postId, username, password)
    # end _metaWeblogGetPost()

    def _metaWeblogGetRecentPosts(self, blogId, username, password, numPosts):
        pageBlogId = self._getWpPagesRawId(blogId)
        if pageBlogId is not None:
            return self.server.wp.getPages(pageBlogId, username, password)
        else:
            return ZWordPressXmlRpcServer._metaWeblogGetRecentPosts(self, blogId, username, password, numPosts)
    # end _metaWeblogGetRecentPosts()

    def _metaWeblogGetCategories(self, blogId, username, password):
        if self._isWpPagesDomain(blogId):
            # categories not supported in paegs.
            return []
        else:
            return ZWordPressXmlRpcServer._metaWeblogGetCategories(self, blogId, username, password)
    # end _metaWeblogGetCategories()
    
    def _uploadFile(self, blogId, srcFile, destName, izMediaUploadListener = None):  #@UnusedVariable #@UnusedVariable #@UnusedVariable  #@UnusedVariable
        # FIXME (PJ) refactor so that common code is used between this impl and that of base class (metaweblog API
        self._debug(u"calling  wp.uploadFile blogId:" + toUnicode(blogId)) #$NON-NLS-1$
        self._connect()
        blogUrl = self._getBlogUrl(blogId)
        medUrl = None
        result = None
        # url to return if upload failed (e.g. server replied with 'file already exists')
        backupUrl = blogUrl.rstrip(u"/") + u"/" + destName #$NON-NLS-1$ #$NON-NLS-2$
        newMediaObjectUploadListener = None
        try:
            mediaBits = None
            if izMediaUploadListener:
                newMediaObjectUploadListener = ZMetawblogMediaUploadListenerAdapter(srcFile, izMediaUploadListener)
            self.server.setTransportListener(newMediaObjectUploadListener)
            # is the file sent as a media repo file reader wrapper.
            if newMediaObjectUploadListener:
                f = file(srcFile, u'rb') #$NON-NLS-1$
                base64InputStream = ZStreamWrapper(f, newMediaObjectUploadListener)
                mediaBits = zoundry.blogpub.xmlrpc.zpatch.xmlrpclib.Binary(fileStream = base64InputStream)
            else:
                # standard filename .
                f = file(srcFile, u'rb') #$NON-NLS-1$
                fileData = f.read()
                f.close()
                mediaBits = zoundry.blogpub.xmlrpc.zpatch.xmlrpclib.Binary(fileData)
            # FIXME (PJ) move 'overwrite' and contentType as a parameter to API. 
            overwrite = False
            (contentType, contentEnc) = guess_type(srcFile) #@UnusedVariable
            if not contentType:
                contentType = u"application/octet-stream" #$NON-NLS-1$
            mediaStruct = {
                u'name' : destName,  #$NON-NLS-1$
                u'type' : contentType,  #$NON-NLS-1$
                u'bits' : mediaBits, #$NON-NLS-1$
                u'overwriter' : overwrite #$NON-NLS-1$
            }

            result = self.server.wp.uploadFile(toUtf8(blogId), self.getUsername(), self.getPassword(), mediaStruct)
            
            self.server.setTransportListener(None)
            if result and isinstance(result, dict) and result.has_key(u"url"):                 #$NON-NLS-1$
                medUrl = toUnicode(result[u'url']) #$NON-NLS-1$
            elif result and isinstance(result, list) and len(result) > 0:
                medUrl = toUnicode(result[0])
            elif result and isinstance(result, basestring):
                medUrl = toUnicode(result)
        except Exception, e:
            pe = ZXmlRpcUploadError(e, u"file: " + toUnicode(srcFile), url = backupUrl) #$NON-NLS-1$
            if newMediaObjectUploadListener:
                newMediaObjectUploadListener.notifyFailure(pe)
            raise pe
        if not medUrl or len(medUrl.strip()) < 5:
            pe = ZXmlRpcUploadError(message = u"url missing from upload response", url = backupUrl) #$NON-NLS-1$
            if newMediaObjectUploadListener:
                newMediaObjectUploadListener.notifyFailure(pe)
            raise pe
        # replace &amp; with & character.
        medUrl = medUrl.replace(u"&amp;", u"&"); #$NON-NLS-2$ #$NON-NLS-1$
        medUrl = medUrl.strip()
        medUrl = medUrl.lstrip(u"/") #$NON-NLS-1$
        if not medUrl.lower().startswith(u"http://") and not medUrl.lower().startswith(u"https://"): #$NON-NLS-1$ #$NON-NLS-2$
            medUrl = blogUrl.rstrip(u"/") + u"/" + medUrl #$NON-NLS-1$ #$NON-NLS-2$
        return ZBlogMediaServerUploadResult(medUrl)
    # end _uploadFile()

# end ZWordPress22XmlRpcServer

#===================================================
# Windows LiveSpaces API
#===================================================
class ZLiveSpacesXmlRpcServer(ZMetaweblogXmlRpcServer):

    def __init__(self, apiUrl, username, password, version):
        ZMetaweblogXmlRpcServer.__init__(self,apiUrl, username, password, version)
        self._setName(u"LiveSpaces")  #$NON-NLS-1$
        self._appID = u"urn:zoundry.com:raven:pub:xmlrpc:metaweblog:livespaces"  #$NON-NLS-1$

    def _setNewPostUrl(self, blogId, rpcEntry):
        u"""Sets the post's permalink hardcoding the entry id to with the blog's url """   #$NON-NLS-1$
        altUrl = self._getSpacePermUrl(blogId, rpcEntry.getId())
        rpcEntry.setUrl(altUrl)

    def _createEntryFromRpcResult(self, blogId, map = {}, blogEntryId = None):
        u"""Creates a XmlRpcEntry object given the raw post data from the xml-rpc result."""            #$NON-NLS-1$
        entry = ZMetaweblogXmlRpcServer._createEntryFromRpcResult(self, blogId, map, blogEntryId)
        altUrl = self._getSpacePermUrl(blogId, entry.getId() )
        blogUrl = self._getBlogUrl(blogId)
        if blogUrl == entry.getUrl():
            entry.setUrl(altUrl)
        return entry

    def _getSpacePermUrl(self, blogId, postId):
        u"""Since MSN Spaces does not return the permUrl, construct it based on post id""" #$NON-NLS-1$
        # MSN Spaces permLink format: http://spaces.msn.com/members/MEMBERNAME/Blog/cns!1p4wqmJcyu30AS-WwxQElvCQ!491.entry
        # Live Spaces http://MEMBERNAME.spaces.live.com/blog/cns!46862DC828C3B532!110.entry
        blogUrl = self._getBlogUrl(blogId)
        permUrl = blogUrl.rstrip(u"/") + u"/Blog/cns!" + postId + u".entry" #$NON-NLS-3$ #$NON-NLS-2$ #$NON-NLS-1$
        if blogUrl.lower().find(u".spaces.live.com") != -1: #$NON-NLS-1$
            # use lower case 'b' in '/blog/' for spaces.live.
            permUrl = blogUrl.rstrip(u"/") + u"/blog/cns!" + postId + u".entry" #$NON-NLS-3$ #$NON-NLS-2$ #$NON-NLS-1$
        return permUrl
# end ZLiveSpacesXmlRpcServer

#===================================================
# Generic MovableType API
#===================================================

class ZMovableTypeXmlRpcServer(ZMetaweblogXmlRpcServer):

    def __init__(self, apiUrl, username, password, version):
        ZMetaweblogXmlRpcServer.__init__(self,apiUrl, username, password, version)
        self._setName(u"MovableType")  #$NON-NLS-1$
        self._appID = u"urn:zoundry.com:raven:pub:xmlrpc:movabletype"  #$NON-NLS-1$

    def post(self, blogId, rpcEntry, editMode, draftMode):
        mtData = {}
        rVal = self._post(blogId, rpcEntry, editMode, draftMode, False, mtDataMap = mtData)
        # set post categories
        if rVal and rpcEntry.getCategories():
            self.setPostCategoryList(blogId, rpcEntry.getId(), rpcEntry.getCategories())

        return rVal

    def getPost(self, blogId, blogEntryId):
        rpcEntry = ZMetaweblogXmlRpcServer.getPost(self, blogId, blogEntryId)
        self._assignPostCategories(blogId, rpcEntry)
        return rpcEntry

    def getRecentPosts(self, blogId, numPosts = 1):
        u"""Returns list of XmlRpcEntry items.""" #$NON-NLS-1$
        retList = ZMetaweblogXmlRpcServer.getRecentPosts(self, blogId, numPosts)
        for rpcEntry in retList:
            self._assignPostCategories(blogId, rpcEntry)
        return retList

    def getRecentPostTitles(self, blogId, numPosts = 1):
        # MovableType API specific call.
        self._connect()        
        numPosts = self._getSafeNumPosts(numPosts)
        results = None
        try:
            results = self.server.mt.getRecentPostTitles(toUtf8(blogId), self.getUsername(), self.getPassword(), numPosts)
        except Exception, e:
            pe = ZXmlRpcGetPostException(e,u"mt.getRecentPostTitles", u"blog-id %s" % toUnicode(blogId)) #$NON-NLS-1$ #$NON-NLS-2$
            raise pe
        retList = []
        if results:
            for r in results:
                entry = self._createEntryFromRpcResult(blogId, r, None)
                if entry:
                    retList.append(entry)
        return retList


    def _assignPostCategories(self, blogId, rpcEntry):
        # retrieve per post categories if not already included as part of the metaweblog call.
        if not rpcEntry.hasCategories():
            try:
                entryCategories = self.getPostCategoryList( blogId, rpcEntry.getId() )
                if entryCategories:
                    rpcEntry.setHasCategories(True)
                    rpcEntry.getCategories().extend( entryCategories )
            except Exception, e:
                self._error(u"Error getting mt post categories. %s" % e)  #$NON-NLS-1$


    def getCategories(self, blogId):
        u"""Returns list of XmlRpcCategory items.""" #$NON-NLS-1$
        categoryList = self._getCachedCategoryList(blogId)
        if categoryList:
            return categoryList

        self._debug(u"calling mt.getCategoryList blogId:" + toUnicode(blogId)) #$NON-NLS-1$

        self._connect()
        results = None
        try:
            results = self.server.mt.getCategoryList(toUtf8(blogId), self.getUsername(), self.getPassword() )
        except Exception, e:
            pe = ZXmlRpcException(e, stage = u"mt.getCategoryList", message = u"blog-id %s" % toUnicode(blogId)) #$NON-NLS-1$ #$NON-NLS-2$
            raise pe

        # EG:
        # [{'categoryId': '1580985', 'categoryName': 'Toys and Games'}, {'categoryId': '1523101', 'categoryName': 'Books'}]
        categoryList = []
        nameMap = {}
        for d in results:
            d = self._toLowerCaseMap(d)
            if not d.has_key(u'categoryid') or not d.has_key(u'categoryname'): #$NON-NLS-2$ #$NON-NLS-1$
                continue
            catId = toUnicode(d[u'categoryid']) #$NON-NLS-1$
            catName = toUnicode(d[u'categoryname']) #$NON-NLS-1$
            c = ZXmlRpcCategory(catId, catName)
            categoryList.append(c)
            nameMap[catName] = c

        self.categoryListMap[blogId] = categoryList
        self.categoryNameMap[blogId] = nameMap
        return categoryList

    def getPostCategoryList(self, blogId, blogEntryId):
        u"""Return list of categories for the given blog id""" #$NON-NLS-1$

        postId = blogEntryId
        self._debug(u"calling  mt.getPostCategories for postId: " + toUnicode(postId)) #$NON-NLS-1$
        self._connect()
        results = None
        try:
            results = self.server.mt.getPostCategories(toUtf8(postId), self.getUsername(), self.getPassword() )
        except Exception, e:
            pe = ZXmlRpcException(e, stage = u"mt.getPostCategories", message = u"blog-id %s, post-id %s" % (toUnicode(blogId), toUnicode(postId)) ) #$NON-NLS-1$ #$NON-NLS-2$
            raise pe
        categoryList = []
        for d in results:
            d = self._toLowerCaseMap(d)
            if not d.has_key(u'categoryid') or not d.has_key(u'categoryname'): #$NON-NLS-2$ #$NON-NLS-1$
                continue
            catId = toUnicode(d[u'categoryid']) #$NON-NLS-1$
            catName = toUnicode(d[u'categoryname']) #$NON-NLS-1$
            c = ZXmlRpcCategory(catId, catName)
            categoryList.append(c)
        return categoryList

    def setPostCategoryList(self, blogId, blogEntryId, categoryList):
        u"""Sets list of categories for the given post""" #$NON-NLS-1$
        # call set categories
        return self._setPostCategoryList(blogId, blogEntryId, categoryList)

    def _setPostCategoryList(self, blogId, blogEntryId, categoryList):
        u"""Sets list of categories for the given post""" #$NON-NLS-1$
        postId = blogEntryId

        # verify cat list.
        verifiedList = []
        for cat in categoryList:
            if ( not cat.getId() or len(toUnicode( cat.getId() )) == 0 ) and cat.getName():
                cat = self._getCategoryByName(blogId, cat.getName() )
                if cat:
                    verifiedList.append(cat)
            else:
                verifiedList.append(cat)

        if not verifiedList:
            return False
        # build list to be sent
        sendList = []
        for cat in verifiedList:
            d = {}
            d[u'categoryId'] =  toUtf8( cat.getId() ) #$NON-NLS-1$
            d[u'categoryName'] = toUtf8( cat.getName() ) #$NON-NLS-1$
            d[u'isPrimary'] = False #$NON-NLS-1$
            sendList.append(d)

        # Make the first category as primary
        d = sendList[0]
        d[u'isPrimary'] = True  #$NON-NLS-1$

        self._debug(u"calling mt.setPostCategories for postId: " + toUnicode(postId)) #$NON-NLS-1$
        self._connect()
        results = False
        try:
            results = self.server.mt.setPostCategories(toUtf8(postId), self.getUsername(), self.getPassword(), sendList )
        except Exception, e:
            pe = ZXmlRpcException(e, stage = u"mt.setPostCategories", message = u"blog-id %s, post-id %s" % (toUnicode(blogId), toUnicode(postId)) ) #$NON-NLS-1$ #$NON-NLS-2$
            raise pe
        return results

    def publishPost(self, blogId, blogEntryId):
        u"""Republishes the given post i.e. server rebuilds the html.""" #$NON-NLS-1$
        postId = blogEntryId
        self._debug(u"calling mt.publishPost for postId: " + toUnicode(postId)) #$NON-NLS-1$
        self._connect()
        results = False
        try:
            results = self.server.mt.publishPost(toUtf8(postId), self.getUsername(), self.getPassword() )
        except Exception, e:
            pe = ZXmlRpcException(e, stage = u"mt.publishPost", message = u"blog-id %s, post-id %s" % (toUnicode(blogId), toUnicode(postId)) ) #$NON-NLS-1$ #$NON-NLS-2$
            raise pe
        return results

# end ZMovableTypeXmlRpcServer

#===================================================
# SixApart's impl of MovableType API
#===================================================

class ZSixApartMovableTypeXmlRpcServer(ZMovableTypeXmlRpcServer):

    def __init__(self, apiUrl, username, password, version):
        ZMovableTypeXmlRpcServer.__init__(self,apiUrl, username, password, version)
        self._setName(u"SixApartMovableType")  #$NON-NLS-1$
        self._appID = u"urn:zoundry.com:raven:pub:xmlrpc:movabletype:sixapart"  #$NON-NLS-1$

    def post(self, blogId, rpcEntry, editMode, draftMode):
        # FIXME (PJ) Make this a 'feature' (e.g. postandpublish = true)
        rVal = ZMovableTypeXmlRpcServer.post(self, blogId, rpcEntry, editMode, draftMode)
        if rVal and rpcEntry.getCategories():
            # now try and set its publish flag - as a work around a MT category bug. (equivalent to a double post?)
            self.publishPost(blogId, rpcEntry.getId())
        return rVal
# end ZSixApartMovableTypeXmlRpcServer

#===================================================
# LiveJournal API
# See http://www.livejournal.com/doc/server/ljp.csp.xml-rpc.protocol.html
#===================================================
class ZLiveJournalXmlRpcServer(ZXmlRpcServerBase):

    LJ_CLIENT_VER = u"Win32-Zoundry/Raven" #$NON-NLS-1$

    def __init__(self, apiUrl, username, password, version):
        if version:
            version = u"Win32-Zoundry/" + version #$NON-NLS-1$
        else:
            version = ZLiveJournalXmlRpcServer.LJ_CLIENT_VER
        ZXmlRpcServerBase.__init__(self, apiUrl, username, password, version)
        self._setName(u"LiveJournal")  #$NON-NLS-1$
        self._appID = u"urn:zoundry.com:raven:pub:xmlrpc:livejournal"  #$NON-NLS-1$
        self.hpassword = self._md5digest( self.getPassword() )
        self.challengeAttempted = False
        self.authMethod = u"hpassword" #$NON-NLS-1$
        self.authExpireTime = 0
        self.authChallenge = None
        self.authServerTime = 0
        self.authChallengeResponse = None
        self.loginCountMap = {}


    def _getLoginCount(self, blogId):
        rval = 0
        key = unicode(blogId)
        if self.loginCountMap.has_key(key):
            rval = self.loginCountMap[key]
        return rval

    def _incLoginCount(self, blogId):
        key = unicode(blogId)
        count = 0
        if self.loginCountMap.has_key(key):
            count = self.loginCountMap[key]
        count = count + 1
        self.loginCountMap[key] = count

    def _connect(self):
        if not self._isConnected():
            ZXmlRpcServerBase._connect(self)
        self._getChallenge()

    def _md5digest(self,text):
        rval = None
        try:
            m = md5.new()
            m.update(text)
            rval = m.hexdigest()
        except AttributeError:
            pass
        return rval

    def _getChallenge(self):
        self.authExpireTime = 0
        self.authChallenge = None
        self.authServerTime = 0
        self.authChallengeResponse = None
        try:
            result = self.server.LJ.XMLRPC.getchallenge()
            self.authMethod = u"challenge" #$NON-NLS-1$
            self.authExpireTime = result[u"expire_time"] #$NON-NLS-1$
            self.authChallenge = result[u"challenge"] #$NON-NLS-1$
            self.authServerTime = result[u"server_time"] #$NON-NLS-1$
            s = str(self.authChallenge) + str(self.hpassword)
            self.authChallengeResponse = self._md5digest(s)
        except:
            self.authMethod = u"hpassword" #$NON-NLS-1$
        self.challengeAttempted = True
    # end  _getChallenge

    def _getAuthData(self):
        authData = {}
        authData[u"username"] = self.getUsername() #$NON-NLS-1$
        authData[u"ver"] = u"1"         #$NON-NLS-2$ #$NON-NLS-1$
        if self.authMethod == u"challenge": #$NON-NLS-1$
            authData[u"auth_method"] = self.authMethod #$NON-NLS-1$
            authData[u"auth_challenge"] = self.authChallenge #$NON-NLS-1$
            authData[u"auth_response"] = self.authChallengeResponse #$NON-NLS-1$
        else:
            authData[u"hpassword"] = self.hpassword #$NON-NLS-1$
        return authData
    # end _getAuthData

    def _login(self, blogId):
        req = self._getAuthData()
        req[u"getmoods"] = u"0" #$NON-NLS-2$ #$NON-NLS-1$
        req[u"clientversion"] = self.getVersion() #$NON-NLS-1$
        self._debug(u"Calling LJ.XMLRPC.login") #$NON-NLS-1$
        results = self.server.LJ.XMLRPC.login(req)
#        fullname = None
#        if results.has_key(u"fullname"): #$NON-NLS-1$
#            fullname = toUnicode(results[u"fullname"]) #$NON-NLS-1$

        usejournals = []
        if results.has_key(u"usejournals"): #$NON-NLS-1$
            usejournals = results[u"usejournals"] #$NON-NLS-1$

        usejournals.append( self.getUsername() )
        moods = []
        if results.has_key(u"moods"): #$NON-NLS-1$
            moods = results[u"moods"] #$NON-NLS-1$
        self._parseMoods(blogId, moods)
        self._incLoginCount(blogId)
    # end _login

    def _parseMoods(self, blogId, moods):
        # moods is a list of dict items, where sample dict item is: {'name': 'aggravated', 'parent': 2, 'id': 1}
        categoryList = []
        nameMap = {}
        for mood in moods:
            catName = mood[u"name"] #$NON-NLS-1$
            catId = unicode(mood[u"id"]) #$NON-NLS-1$  $ mood id is an int - convert to unicode
            c = ZXmlRpcCategory(catId, catName)
            categoryList.append(c)
            nameMap[catName] = c

        # cache results
        self.categoryListMap[blogId] = categoryList
        self.categoryNameMap[blogId] = nameMap

    def _isIntAttr(self, attrName):
        intValNames = [u"allowmask", u"revtime", u"current_moodid",  u"opt_preformatted", u"opt_backdated", u"revnum"]  #$NON-NLS-1$  #$NON-NLS-2$ #$NON-NLS-3$  #$NON-NLS-4$  #$NON-NLS-5$ #$NON-NLS-6$
        return attrName in intValNames

    def _getLJAttrValue(self, attrName, attrValue):
        # convert certain attrs to int instead of string where applicable or to utf8 incase of string.
        rval = None
        if self._isIntAttr(attrName):
            rval = int(attrValue)
        else:
            rval = toUtf8(attrValue)
        return rval

    def _getLJAttrMapValue(self, attrMap, attrName):
        # convert certain attrs to int instead of string.
        # E.g: 'revtime': 1127344356, 'current_moodid': 44, 'opt_preformatted': 1, 'opt_backdated': 1, 'revnum': 2
        rval = None
        if attrMap.has_key(attrName):
            rval = attrMap[attrName]
            if self._isIntAttr(attrName):
                rval = int(rval)
        return rval

    def _createEntryFromRpcResult(self, blogId, map = {}, blogEntryId = None): #@UnusedVariable
        # sample evt:
        # {'itemid': 1, 'eventtime': '2005-09-13 17:06:00',
        #   'url': 'http://www.livejournal.com/users/sandun/398.html',
        #   'props': {'current_moodid': 15, 'opt_nocomments': 1, 'current_music': 'Blues Traveler, Aimee Maan', 'taglist': 'tagone, tag3, tag two'},
        #  'subject': 'Test Post (ignore, public)',
        #  'event': 'text.', 'anum': 142}

        if not map.has_key(u'itemid') or not map.has_key(u"anum"): #$NON-NLS-2$ #$NON-NLS-1$
            self._debug(u"entry itemid or enum missing.") #$NON-NLS-1$
            return None

        itemid = map[u"itemid"] #$NON-NLS-1$
        anum = map[u"anum"] #$NON-NLS-1$
        postId = toUnicode(itemid) + u"." + toUnicode(anum) #$NON-NLS-1$

        # LJ main level custom attrs
        entryCustomMainAttrs = {}
        # LJ props level custom attrs
        entryCustomPropsAttrs = {}
        # url
        entryUrl = None
        if map.has_key(u'url'): #$NON-NLS-1$
            entryUrl = self._getPostUrl(blogId, toUnicode(map[u'url']) ) #$NON-NLS-1$
        elif map.has_key(u'link'): #$NON-NLS-1$
            entryUrl.url = self._getPostUrl(blogId, toUnicode(map[u'link']) ) #$NON-NLS-1$
        entryUrl = self._checkEntryUrl(blogId, entryUrl)

        # body content
        entryContent = u"" #$NON-NLS-1$
        if map.has_key(u'event') and map[u'event']: #$NON-NLS-2$ #$NON-NLS-1$
            entryContent = toUnicode(map[u'event']) #$NON-NLS-1$
        # no summary
        entrySummary = None
        # title
        entryTitle = None
        if map.has_key(u'subject'): #$NON-NLS-1$
            entryTitle = toUnicode(map[u'subject']) #$NON-NLS-1$

        rpcDateStr = None
        if map.has_key(u'eventtime'): #$NON-NLS-1$
            rpcDateStr = toUnicode(map[u'eventtime']) #  e.g '2005-09-13 17:06:00' #$NON-NLS-1$
            rpcDateStr = rpcDateStr.replace(u' ', u'T') #$NON-NLS-2$ #$NON-NLS-1$
            # remove '-' to the format similar to WP xml-rpc ISO860 datetime (local dt)
            rpcDateStr = rpcDateStr.replace(u'-', u'') #$NON-NLS-2$ #$NON-NLS-1$
            # expect dt to YYYYMMDDTHH:MM:SS

        # Security attr. Map to draft status. Also save attr under entry attrs.
        draftMode = False
        if map.has_key(u'security') and map[u"security"]: #$NON-NLS-2$ #$NON-NLS-1$
            entryCustomMainAttrs[u"security"] = toUnicode(map[u"security"]) #$NON-NLS-2$ #$NON-NLS-1$
            if map[u"security"] == u"private": #$NON-NLS-2$ #$NON-NLS-1$
                draftMode = True
            elif map[u"security"] == u"usemask" and map.has_key(u'allowmask'): #$NON-NLS-3$ #$NON-NLS-2$ #$NON-NLS-1$
                usemask = map[u"allowmask"] #$NON-NLS-1$
                entryCustomMainAttrs[u"allowmask"] = toUnicode(usemask) #$NON-NLS-1$

        # Categories (Moods)
        entryCategories = None
        entryTagwords = None
        entryTagspace = None
        # entry formatting
        entryPreformatted = False
        mood = None
        moodId = u"-1" #$NON-NLS-1$
        if map.has_key(u'props'): #$NON-NLS-1$
            # grab attrs such as currrent_mood, current_moodid, current_music
            props = map[u"props"] #$NON-NLS-1$
            if props.has_key(u"current_mood"): #$NON-NLS-1$
                entryCustomPropsAttrs[u"current_mood"] = toUnicode(props[u"current_mood"]) #$NON-NLS-2$ #$NON-NLS-1$
                mood = props[u"current_mood"]             #$NON-NLS-1$
            if props.has_key(u"current_moodid"): #$NON-NLS-1$
                entryCustomPropsAttrs[u"current_moodid"] = toUnicode(props[u"current_moodid"]) #$NON-NLS-2$ #$NON-NLS-1$
                moodId = unicode(props[u"current_moodid"]) #$NON-NLS-1$
            if props.has_key(u"current_music"): #$NON-NLS-1$
                entryCustomPropsAttrs[u"current_music"] = toUnicode(props[u"current_music"]) #$NON-NLS-2$ #$NON-NLS-1$

            if props.has_key(u"taglist"): #$NON-NLS-1$
                l = toUnicode(props[u"taglist"]) #$NON-NLS-1$
                entryCustomPropsAttrs[u"taglist"] = l #$NON-NLS-1$
                entryTagwords = l.split(u",") #$NON-NLS-1$
                entryTagspace = IZBlogPubTagwordNamespaces.LIVEJOURNAL_TAGWORDS_URI

            if props.has_key(u"opt_preformatted"): #$NON-NLS-1$
                entryPreformatted = props[u"opt_preformatted"] #$NON-NLS-1$
                entryCustomPropsAttrs[u"opt_preformatted"] = entryPreformatted #$NON-NLS-1$


        if moodId and moodId != u"-1": #$NON-NLS-1$
            idList = [toUnicode(moodId)]
            entryCategories = self._createCategoryListFromIds(blogId, idList)
        elif mood and len (mood.strip()) > 0:
            nameList = [mood]
            entryCategories = self._createCategoryListFromNames(blogId, nameList)

        # convert line breaks if entry is not preformatted (in html)
        convertLineBreak = not entryPreformatted
        # rpcDate is str "20061217T19:10:00" local time. Convert to py DateTime UTC.
        entryDate = self._fromRpcDateTime( rpcDateStr )
        entry = ZXmlRpcEntry(postId)
        entry.setTitle( entryTitle )
        entry.setDraft( draftMode )
        entry.setUrl( entryUrl )
        entry.setUtcDateTime(entryDate)
        entry.setContent( entryContent )
        entry.setSummary( entrySummary )
        entry.setConvertNewLines( convertLineBreak )
        if entryCategories is not None:
            entry.setHasCategories(True)
            entry.getCategories().extend( entryCategories )

        if entryTagwords:
            entry.setTagwords(entryTagwords)
        if entryTagspace:
            entry.setTagspaceUrl(entryTagspace)

        if hasMetaData(entryContent):
            extractMetaData(entryContent, entry)

        for (k,v) in entryCustomMainAttrs.iteritems():
            entry.setAttribute(k, unicode(v), IZBlogPubAttrNamespaces.LJ_ATTR_NAMESPACE)

        for (k,v) in entryCustomPropsAttrs.iteritems():
            entry.setAttribute(k, unicode(v), IZBlogPubAttrNamespaces.LJ_PROPS_ATTR_NAMESPACE)

        if entry.getContent():
            entry.setContent(entry.getContent().replace(u'\r\n', u'\r') ) #$NON-NLS-2$ #$NON-NLS-1$
            entry.setContent(entry.getContent().replace(u'\r', u'\n') ) #$NON-NLS-2$ #$NON-NLS-1$
            entry.setContent(entry.getContent().replace(u'&nbsp;', u' ') ) #$NON-NLS-2$ #$NON-NLS-1$
        return entry

    def _splitPostId(self, postId):
        u"""Returns tuple(itemid, anum, htmlpostid)""" #$NON-NLS-1$
        (s1, s2) = postId.split(u".") #$NON-NLS-1$
        itemid = int(s1)
        anum = int(s2)
        htmlNum = self._getHtmlPostNumber(itemid, anum)
        return (itemid, anum, htmlNum)

    def _getHtmlPostNumber(self, itemid, anum):
        htmlNum = itemid * 256 + anum
        return htmlNum

    def _getPostUrlFromIdAnum(self, blogId, itemid, anum):
        u"""Returns calculated url given blogid, itemid and anum""" #$NON-NLS-1$
        baseUrl  = self._getBlogUrl(blogId)
        htmlNum = self._getHtmlPostNumber(itemid, anum)
        url = baseUrl.rstrip(u"/") + u"/" + toUnicode(htmlNum) + u".html" #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$
        return url

    def _getBloggerApiUrl(self):
        # convert host/interface/xmprpc url to host/interface/blogger
        l = self.getApiUrl().split(u"/") #$NON-NLS-1$
        l[len(l)-1] = u"blogger" #$NON-NLS-1$
        bloggerApiUrl = u"/".join(l) #$NON-NLS-1$
        return bloggerApiUrl


    def _getUserBlogs(self):
        u"""Return raw xml-rpc response from server""" #$NON-NLS-1$
        blogs = None
        bloggerApiUrl = self._getBloggerApiUrl()
        self._debug(u"Gettting list of blogs via blogger.getUsersBlogs method from %s" % bloggerApiUrl) #$NON-NLS-1$
        try:
            bloggerServer = self._createServer(bloggerApiUrl)
            blogs = bloggerServer.blogger.getUsersBlogs(self._appID, self.getUsername(), self.getPassword() )
        except Exception , e:
            pe = ZXmlRpcException(e, u"blogger.getUsersBlogs", u"xmlrpcapi.error_getting_blog_list_from %s" + bloggerApiUrl ) #$NON-NLS-1$ #$NON-NLS-2$
            raise pe

        if not blogs:
            pe = ZXmlRpcException(stage = u"xmlrpcapi.getbloglist", message = u"xmlrpcapi.blog_list_unavailable_error") #$NON-NLS-1$ #$NON-NLS-2$
            raise pe
        return blogs

    def post(self, blogId, rpcEntry, editMode, draftMode):
        postTitle = toUtf8( rpcEntry.getTitle() )
        postEntry = toUtf8( self._formatContentForPublishing(rpcEntry) )
        postId = 0
        itemid = 0
        anum = 0
        self._connect()
        req = self._getAuthData()
        req[u"usejournal"] = toUtf8(blogId) #$NON-NLS-1$
        req[u"subject"] = postTitle #$NON-NLS-1$
        req[u"event"] = postEntry #$NON-NLS-1$
        req[u"lineendings"] = u"unix" #$NON-NLS-2$ #$NON-NLS-1$

        if draftMode:
            req[u"security"] = u"private" #$NON-NLS-2$ #$NON-NLS-1$
        elif rpcEntry.getAttribute(u"security",IZBlogPubAttrNamespaces.LJ_ATTR_NAMESPACE) != None and rpcEntry.getAttribute(u"allowmask", IZBlogPubAttrNamespaces.LJ_ATTR_NAMESPACE) != None: #$NON-NLS-2$ #$NON-NLS-1$
            try:
                req[u"security"] = toUtf8( rpcEntry.getAttribute(u"security", IZBlogPubAttrNamespaces.LJ_ATTR_NAMESPACE) ) #$NON-NLS-2$ #$NON-NLS-1$
                req[u"allowmask"] = int( rpcEntry.getAttribute(u"allowmask", IZBlogPubAttrNamespaces.LJ_ATTR_NAMESPACE) ) #$NON-NLS-2$ #$NON-NLS-1$
            except:
                pass


        if editMode and rpcEntry.getId():
            postId = rpcEntry.getId()
            (itemid, anum, htmlNum) = self._splitPostId(postId) #@UnusedVariable
            req[u"itemid"] = itemid #$NON-NLS-1$

        backDatePost = False
        nowDtLocal = getCurrentLocalTime()
        entryDate = rpcEntry.getUtcDateTime()
        if entryDate:
            # convert to local time
            entryDate = convertToLocalTime(entryDate)
            # check to see if this is backdated.
            try:
                td = nowDtLocal - entryDate
                if td.days > 0:
                    backDatePost = True
            except:
                pass
        else:
            entryDate = nowDtLocal

        req[u"year"] = entryDate.year #$NON-NLS-1$
        req[u"mon"] = entryDate.month #$NON-NLS-1$
        req[u"day"] = entryDate.day #$NON-NLS-1$
        req[u"hour"] = entryDate.hour #$NON-NLS-1$
        req[u"min"] = entryDate.minute #$NON-NLS-1$

        props = {}
        props[u"opt_preformatted"] = True #$NON-NLS-1$
        if rpcEntry.getTagwords() and len( rpcEntry.getTagwords() ) > 0:
            props[u"taglist"] = toUtf8( u",".join(rpcEntry.getTagwords() ) ) #$NON-NLS-2$ #$NON-NLS-1$
        if backDatePost:
            props[u"opt_backdated"] = True  #$NON-NLS-1$

        if rpcEntry.getCategories():
            for cat in rpcEntry.getCategories():
                try:
                    props[u"current_moodid"] = int( cat.getId() ) #$NON-NLS-1$
                except:
                    pass
                break

        if len(props) > 0:
            req[u"props"] = props #$NON-NLS-1$

        bOk = False
        results = None

        if editMode:
            self._debug(u"calling LJ.XMLRPC.editevent postId:" + toUnicode(postId)) #$NON-NLS-1$
        else:
            self._debug(u"calling LJ.XMLRPC.postevent blogId:" + toUnicode(blogId)) #$NON-NLS-1$

        if editMode:
            try:
                results = self.server.LJ.XMLRPC.editevent(req)
            except Exception, e:
                pe = ZXmlRpcPostException(e, editMode, blogid = blogId, postid = postId)
                raise pe
            if results:
                bOk = True
        else:
            try:
                results = self.server.LJ.XMLRPC.postevent(req)
            except Exception, e:
                pe = ZXmlRpcPostException(e, editMode, blogid = blogId, postid = postId)
                raise pe

            if results and results.has_key(u'itemid') or results.has_key(u"anum"):             #$NON-NLS-2$ #$NON-NLS-1$
                itemid = results[u"itemid"] #$NON-NLS-1$
                anum = results[u"anum"] #$NON-NLS-1$
                postId = toUnicode(itemid) + u"." + toUnicode(anum) #$NON-NLS-1$
                rpcEntry.setId( postId )
                url = self._getPostUrlFromIdAnum(blogId, itemid, anum)
                rpcEntry.setUrl(url)
                bOk = True
        return bOk
#    # end post()

    def getPost(self, blogId, blogEntryId = 0):
        u"""Returns a specific post as a XmlRpcEntry object or None if failed.""" #$NON-NLS-1$
        postId = blogEntryId
        (itemid, anum, htmlNum) = self._splitPostId(postId)#@UnusedVariable
        self._connect()
        req = self._getAuthData()
        req[u"usejournal"] = toUtf8(blogId) #$NON-NLS-1$
        req[u"selecttype"] = u"one" #$NON-NLS-2$ #$NON-NLS-1$
        req[u"lineendings"] = u"unix" #$NON-NLS-2$ #$NON-NLS-1$
        req[u"itemid"] =  itemid #$NON-NLS-1$
        self._debug(u"Calling getPost::LJ.XMLRPC.getevents") #$NON-NLS-1$
        try:
            results = self.server.LJ.XMLRPC.getevents(req)
            events = []
            if results and results.has_key(u"events") and results[u"events"]: #$NON-NLS-2$ #$NON-NLS-1$
                events = results[u"events"] #$NON-NLS-1$
            entry = None
            if events and len(events) > 0:
                entry = self._createEntryFromRpcResult(blogId, events[0], postId)
            return entry

        except Exception , e:
            pe = ZXmlRpcGetPostException(e,u"LJ.XMLRPC.getevents", u"post-id %s" % toUnicode(postId)) #$NON-NLS-1$ #$NON-NLS-2$
            raise pe
    # end getPost
#
    def deletePost(self, blogId, blogEntryId = None):
        u"""Deletes the given post. Returns true on success""" #$NON-NLS-1$
        postId = blogEntryId
        (itemid, anum, htmlNum) = self._splitPostId(postId)   #@UnusedVariable
        self._connect()
        req = self._getAuthData()
        req[u"usejournal"] = toUtf8(blogId) #$NON-NLS-1$
        # send empty subject and body to delete an event.
        req[u"subject"] = u"" #$NON-NLS-2$ #$NON-NLS-1$
        req[u"event"] = u"" #$NON-NLS-2$ #$NON-NLS-1$
        req[u"lineendings"] = u"unix" #$NON-NLS-2$ #$NON-NLS-1$
        req[u"itemid"] = itemid #$NON-NLS-1$
        rVal = False
        self._debug(u"Calling deletePost::LJ.XMLRPC.editevent") #$NON-NLS-1$
        try:
            results = self.server.LJ.XMLRPC.editevent(req) #@UnusedVariable
            rVal = True
        except Exception, e:
            de = ZXmlRpcDeleteError(e, blogid = blogId, postid = postId)
            raise de
        return rVal


    def getRecentPosts(self, blogId, numPosts = 1):
        u"""Returns list of XmlRpcEntry items.""" #$NON-NLS-1$
        if not numPosts or numPosts < 0:
            numPosts = 20
        self._connect()
        req = self._getAuthData()
        req[u"usejournal"] = toUtf8(blogId) #$NON-NLS-1$
        req[u"selecttype"] = u"lastn" #$NON-NLS-2$ #$NON-NLS-1$
        req[u"howmany"] = numPosts #$NON-NLS-1$
        req[u"lineendings"] = u"unix" #$NON-NLS-2$ #$NON-NLS-1$

        self._debug(u"Calling getRecentPosts::LJ.XMLRPC.getevents") #$NON-NLS-1$
        results = None
        try:
            results = self.server.LJ.XMLRPC.getevents(req)
        except Exception, e:
            pe = ZXmlRpcGetPostException(e,u"LJ.XMLRPC.getevents", u"blog-id %s, num-posts %s" % (toUnicode(blogId), toUnicode(numPosts) ) )#$NON-NLS-1$ #$NON-NLS-2$
            raise pe

        events = []
        if results and results.has_key(u"events") and results[u"events"]: #$NON-NLS-2$ #$NON-NLS-1$
            events = results[u"events"] #$NON-NLS-1$

        rList = []
        for evt in events:
            if not evt:
                continue
            if evt.has_key(u"poster") and evt[u"poster"] and toUnicode(evt[u"poster"]) != self.getUsername(): #$NON-NLS-3$ #$NON-NLS-2$ #$NON-NLS-1$
                # for community journals, skip if this user is not the poster.
                continue
            entry = self._createEntryFromRpcResult(blogId, evt, None)
            if entry:
                rList.append(entry)
        return rList
        # end getRecentPosts()

    def getCategories(self, blogId):
        categoryList = self._getCachedCategoryList(blogId)
        if categoryList:
            return categoryList
        retList = []
        if self._getLoginCount(blogId) == 0:
            self._connect()
            self._login(blogId)
            categoryList = self._getCachedCategoryList(blogId)
            if categoryList:
                retList = categoryList
        return retList

    def _uploadFile(self, blogId, srcFile, destName, izMediaUploadListener = None):  #@UnusedVariable #@UnusedVariable #@UnusedVariable  #@UnusedVariable
        fbServer = ZFotoBilderServer(self.getUsername(), self.getPassword() )
        fbResult = fbServer.uploadFile(srcFile, None, None, izMediaUploadListener) #@UnusedVariable
        if fbResult:
            if fbResult.getUploadPicResponseNode():
                return ZBlogMediaServerUploadResult(fbResult.getUrl(), metaData=fbResult.getUploadPicResponseNode())
            else:
                return ZBlogMediaServerUploadResult(fbResult.getUrl())
        
        return None
    # end _uploadFile

## end livejournal server