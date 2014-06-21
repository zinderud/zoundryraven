from zoundry.base.zdom.dom import ZDom
from zoundry.base.net.http import HTTP_PUT
from zoundry.blogpub.atom.atomapi import ZAtomException
import os.path
from zoundry.base.net.http import HTTP_DELETE
from zoundry.base.net.http import HTTP_POST
from zoundry.base.net.authhandlers import ZAuthenticationManager
from zoundry.base.net.googledata import ZGoogleLoginAuthHandler
from zoundry.blogpub.atom.atomapi import ZAtomServerBase
from zoundry.blogpub.atom.atomapi import ZAtomEntryDocument
from zoundry.blogpub.atom.atomapi import ZAtom10FeedRequestBase
from zoundry.blogpub.atom.atomapi import ZAtomFeedEntry
from zoundry.blogpub.atom.atomapi import ZAtom10RequestBase
from zoundry.blogpub.namespaces import YAHOO_MEDIA
from zoundry.blogpub.namespaces import GOOGLE_PHOTO
from zoundry.blogpub.namespaces import DUBLIN_CORE_ELE_NAMESPACE
from zoundry.blogpub.namespaces import XHTML_NAMESPACE
from zoundry.blogpub.namespaces import ATOM_10_API_CONTROL_NAMESPACE
from zoundry.blogpub.namespaces import ATOM_10_API_NAMESPACE
from zoundry.blogpub.atom.atomapi import getAtomGeneratorVersion
from zoundry.blogpub.atom.atomapi import getAtomGeneratorName
from zoundry.blogpub.namespaces import ATOM_10_FEED_NAMESPACE

#
# http://code.google.com/apis/picasaweb/gdata.html
#

#------------------------------------------------------
# Install Auth manager for Google login
#-------------------------------------------------------
ZAuthenticationManager().registerHandler(ZGoogleLoginAuthHandler.SCHEME, ZGoogleLoginAuthHandler)


#---------------------------------------------
# Generic Picasa exception
#---------------------------------------------
class ZPicasaException(ZAtomException):

    def __init__(self, message = u"", rootCause = None, stage = u"",  code = 0):  #$NON-NLS-1$  #$NON-NLS-2$
        ZAtomException.__init__(self, rootCause, stage, message, code)
    # end __init__()
# end ZPicasaException

#================================================
# Picasa Atom impl.
#================================================

PICASA_NEW_ALBUM_ENTRY_TEMPLATE = u"""<?xml version="1.0" encoding="utf-8"?>
<entry xmlns='http://www.w3.org/2005/Atom'
    xmlns:media='http://search.yahoo.com/mrss/'
    xmlns:gphoto='http://schemas.google.com/photos/2007'>
    <generator version="%s" uri="http://www.zoundry.com">%s</generator>
   <title type='text'></title>
  <category scheme='http://schemas.google.com/g/2005#kind'
    term='http://schemas.google.com/photos/2007#album'></category>
</entry>""" % (getAtomGeneratorVersion(), getAtomGeneratorName() ) #$NON-NLS-1$

PICASA_EDIT_ALBUM_ENTRY_TEMPLATE = u"""<?xml version="1.0" encoding="utf-8"?>
<entry xmlns='http://www.w3.org/2005/Atom'
    xmlns:media='http://search.yahoo.com/mrss/'
    xmlns:gphoto='http://schemas.google.com/photos/2007'>
    <generator version="%s" uri="http://www.zoundry.com">%s</generator>
   <title type='text'></title>
  <category scheme='http://schemas.google.com/g/2005#kind'
    term='http://schemas.google.com/photos/2007#album'></category>
</entry>""" % (getAtomGeneratorVersion(), getAtomGeneratorName() ) #$NON-NLS-1$

PICASA_NEW_PHOTO_ENTRY_TEMPLATE = u"""<?xml version="1.0" encoding="utf-8"?>
<entry xmlns='http://www.w3.org/2005/Atom'
    xmlns:media='http://search.yahoo.com/mrss/'
    xmlns:gphoto='http://schemas.google.com/photos/2007'>
    <generator version="%s" uri="http://www.zoundry.com">%s</generator>
   <title type='text'></title>
  <category scheme='http://schemas.google.com/g/2005#kind'
    term='http://schemas.google.com/photos/2007#photo'></category>
</entry>""" % (getAtomGeneratorVersion(), getAtomGeneratorName() ) #$NON-NLS-1$

PICASA_EDIT_PHOTO_ENTRY_TEMPLATE = u"""<?xml version="1.0" encoding="utf-8"?>
<entry xmlns='http://www.w3.org/2005/Atom'
    xmlns:media='http://search.yahoo.com/mrss/'
    xmlns:gphoto='http://schemas.google.com/photos/2007'>
    <generator version="%s" uri="http://www.zoundry.com">%s</generator>
   <title type='text'></title>
  <category scheme='http://schemas.google.com/g/2005#kind'
    term='http://schemas.google.com/photos/2007#photo'></category>
</entry>""" % (getAtomGeneratorVersion(), getAtomGeneratorName() ) #$NON-NLS-1$

PICASA_MINIMAL_PHOTO_ENTRY_TEMPLATE = u"""<?xml version="1.0" encoding="utf-8"?>
<entry xmlns='http://www.w3.org/2005/Atom'
    xmlns:media='http://search.yahoo.com/mrss/'
    xmlns:gphoto='http://schemas.google.com/photos/2007'>
 <id>%s</id>
 <category term="http://schemas.google.com/photos/2007#photo" scheme="http://schemas.google.com/g/2005#kind"/>
 <title type='text'>%s</title>
 <content src="%s" type="%s"/>
 <link href="%s" type="application/atom+xml" rel="edit"/>
 <link href="%s" type="%s" rel="edit-media"/>
</entry>"""  #$NON-NLS-1$

PICASA_NSS_MAP = {
    u"atom"   : ATOM_10_FEED_NAMESPACE,  #$NON-NLS-1$
    u"app"    : ATOM_10_API_NAMESPACE, #$NON-NLS-1$
    u"pub"    : ATOM_10_API_CONTROL_NAMESPACE, #$NON-NLS-1$
    u"xhtml"  : XHTML_NAMESPACE,  #$NON-NLS-1$
    u"dc"     : DUBLIN_CORE_ELE_NAMESPACE,  #$NON-NLS-1$
    u"gphoto" : GOOGLE_PHOTO,  #$NON-NLS-1$
    u"media"  : YAHOO_MEDIA  #$NON-NLS-1$
}

#================================
# Picasa request base
#================================
class ZPicasaRequest(ZAtom10RequestBase):

    def __init__(self, url, username, password):
        ZAtom10RequestBase.__init__(self, url, username, password)
    # end __init__()

    def _setDomNSS(self, dom):
        dom.setNamespaceMap(PICASA_NSS_MAP)
    # end _setDomNSS()
# end ZPicasaRequest

#================================
# Picasa delete resource
#================================
class ZPicasaDeleteRequest(ZPicasaRequest):

    def __init__(self, resourceUrl, username, password):
        # Init the super class with the various params
        ZPicasaRequest.__init__(self, resourceUrl, username, password)
        self._setMethod(HTTP_DELETE)
    # end __init__()

    # Tests the response object to make sure the request succeeded.
    def _atomResponseIsGood(self, resp):
        u"Tests the response object to make sure the request succeeded." #$NON-NLS-1$
        return resp.status == 410 or ZPicasaRequest._atomResponseIsGood(self, resp)
    # end _responseIsGood()

    # Delete requests probably return no data - so override the _processResponseData() method.
    def _processResponseData(self, resp, txt): #@UnusedVariable
        return ZPicasaRequest._createEmptyFeed(self)
    # end _processResponseData()

# end ZPicasaDeleteRequest


#================================================
# Picasa Atom 1.0 feed Entry
#================================================
class ZPicasaFeedEntry(ZAtomFeedEntry):
    # Constructs a picasa feed entry object from an Atom XML entry node.
    def __init__(self, entryNode, prefix = u"atom:"): #$NON-NLS-1$
        ZAtomFeedEntry.__init__(self, entryNode, prefix)
        dom = self.getDom()
        if dom:
            dom.setNamespaceMap(PICASA_NSS_MAP)
    # end __init__()
# end ZPicasaFeedEntry

#================================
# Picasa feed request
#================================
class ZPicasaFeedRequest(ZAtom10FeedRequestBase):

    def __init__(self, url, username, password):
        ZAtom10FeedRequestBase.__init__(self, url, username, password)
    # end __init__()

    def _setDomNSS(self, dom):
        dom.setNamespaceMap(PICASA_NSS_MAP)
    # end _setDomNSS()

    def _getEntryList(self):
        # Map the feed entry constructor onto the list of entry XML nodes.
        return map(ZPicasaFeedEntry, self.getDom().selectNodes(u"/atom:feed/atom:entry")) #$NON-NLS-1$
    # end _getEntryList()
# end ZPicasaFeedRequest

#--------------------------------------------
# List albums request
#--------------------------------------------
class ZPicasaListAlbumsRequest(ZPicasaFeedRequest):

    def __init__(self, url, username, password):
        ZPicasaFeedRequest.__init__(self, url, username, password)
    # end __init__()

    def _getEntryList(self):
        return map(ZPicasaAlbumEntry, self.getDom().selectNodes(u"/atom:feed/atom:entry")) #$NON-NLS-1$
    # end _getEntryList()
# end  ZPicasaListAlbumsRequest

#--------------------------------------------
# Album
#--------------------------------------------
class ZPicasaAlbumEntry(ZPicasaFeedEntry):

    def __init__(self, entryNode, prefix = u"atom:"): #$NON-NLS-1$
        ZPicasaFeedEntry.__init__(self, entryNode, prefix)
    # end __init__()

    def getAlbumId(self):
        return self.getNode().selectSingleNodeText(u"gphoto:id", u"") #$NON-NLS-1$ #$NON-NLS-2$
    # end getAlbumId(

    def getAlbumName(self):
        return self.getNode().selectSingleNodeText(u"gphoto:name", u"") #$NON-NLS-1$ #$NON-NLS-2$
    # end getAlbumName()

    def getNumPhotos(self):
        s = self.getNode().selectSingleNodeText(u"gphoto:numphotos", u"0") #$NON-NLS-1$ #$NON-NLS-2$
        return int(s)
    # end getNumPhotos()
# end ZPicasaAlbumEntry

#--------------------------------------------
# Add album
#--------------------------------------------
class ZPicasaAddAlbumRequest(ZPicasaRequest):

    def __init__(self, url, username, password):
        ZPicasaRequest.__init__(self, url, username, password)
        self._setMethod(HTTP_POST)
    # end __init__()

    def getAlbum(self):
        if self.getDom():
            node = self.getDom().selectSingleNode(u"/atom:entry") #$NON-NLS-1$
            return ZPicasaAlbumEntry(node)
        else:
            return None
    # end  getAlbum()
# end  ZPicasaAddAlbumRequest

#--------------------------------------------
# new album
#--------------------------------------------
class ZPicasaNewAlbumEntryDocument(ZAtomEntryDocument):

    def __init__(self):
        ZAtomEntryDocument.__init__(self)
    # end __init__()

    def _initNode(self, dom):
        dom.loadXML(PICASA_NEW_ALBUM_ENTRY_TEMPLATE)
        dom.setNamespaceMap(PICASA_NSS_MAP)
    # end _initNode
# end ZPicasaNewAlbumEntryDocument

#--------------------------------------------
# update album
#--------------------------------------------
class ZPicasaUpdateAlbumEntryDocument(ZPicasaNewAlbumEntryDocument):

    def __init__(self):
        ZPicasaNewAlbumEntryDocument.__init__(self)
    # end __init__()

    def _initNode(self, dom):
        dom.loadXML(PICASA_EDIT_ALBUM_ENTRY_TEMPLATE)
        dom.setNamespaceMap(PICASA_NSS_MAP)
    # end _initNode
# end ZPicasaUpdateAlbumEntryDocument

#--------------------------------------------
# List photos
#--------------------------------------------
class ZPicasaListPhotosRequest(ZPicasaFeedRequest):

    def __init__(self, url, username, password):
        ZPicasaFeedRequest.__init__(self, url, username, password)
    # end __init__()

    def _getEntryList(self):
        return map(ZPicasaPhotoEntry, self.getDom().selectNodes(u"/atom:feed/atom:entry")) #$NON-NLS-1$
    # end _getEntryList()

# end  ZPicasaListPhotosRequest

#--------------------------------------------
# Photos
#--------------------------------------------
class ZPicasaPhotoEntry(ZPicasaFeedEntry):

    def __init__(self, entryNode, prefix = u"atom:"): #$NON-NLS-1$
        ZPicasaFeedEntry.__init__(self, entryNode, prefix)
    # end __init__()

    def getEditMediaLink(self):
        u"Gets the edit-media link url for the entry." #$NON-NLS-1$
        if self.getNode():
            linkElem = self.getNode().selectSingleNode(u"%slink[@rel = 'edit-media']" % self.prefix) #$NON-NLS-1$
            if not linkElem:
                linkElem = self.getNode().selectSingleNode(u"%slink[@rel = 'media-edit']" % self.prefix) #$NON-NLS-1$
            if linkElem:
                return linkElem.getAttribute(u"href") #$NON-NLS-1$
        return None
    # end getEditMediaLink()

    def getEditMediaContentType(self):
        u"Gets the edit-media content-type for the entry." #$NON-NLS-1$
        if self.getNode():
            linkElem = self.getNode().selectSingleNode(u"%slink[@rel = 'edit-media']" % self.prefix) #$NON-NLS-1$
            if not linkElem:
                linkElem = self.getNode().selectSingleNode(u"%slink[@rel = 'media-edit']" % self.prefix) #$NON-NLS-1$
            if linkElem:
                return linkElem.getAttribute(u"type") #$NON-NLS-1$
        return None
    # end getEditMediaContentType()

    def getPhotoId(self):
        return self.getNode().selectSingleNodeText(u"gphoto:id", u"") #$NON-NLS-1$ #$NON-NLS-2$
    # end getPhotoId()

    def getUrl(self):
        return self.getNode().selectSingleNodeText(u"atom:content/@src", u"") #$NON-NLS-1$ #$NON-NLS-2$
    # end getUrl()

    def getContentType(self):
        return self.getNode().selectSingleNodeText(u"atom:content/@type", u"") #$NON-NLS-1$ #$NON-NLS-2$
    # end getContentType()

    def getAlbumId(self):
        return self.getNode().selectSingleNodeText(u"gphoto:albumid", u"") #$NON-NLS-1$ #$NON-NLS-2$
    # end getAlbumId()

    def getWidth(self):
        s = self.getNode().selectSingleNodeText(u"gphoto:width", u"0") #$NON-NLS-1$ #$NON-NLS-2$
        return int(s)
    # end getWidth()

    def getHeight(self):
        s = self.getNode().selectSingleNodeText(u"gphoto:height", u"0") #$NON-NLS-1$ #$NON-NLS-2$
        return int(s)
    # end getHeight()

    def getSize(self):
        s = self.getNode().selectSingleNodeText(u"gphoto:size", u"0") #$NON-NLS-1$ #$NON-NLS-2$
        return int(s)
    # end getSize()

    def getMimimalMetaDataNode(self):
        u"""getMimimalMetaDataNode() -> ZElement or None
        Returns node with minimal meta data (e.g. just id, title, edit links etc).
        """ #$NON-NLS-1$
        if self.getNode():
            id = self.getId()
            title = self.getTitle()
            url = self.getUrl()
            ct = self.getContentType()
            editLink = self.getEditLink()
            editMediaLink = self.getEditMediaLink()
            editMediaCT = self.getEditMediaContentType()
            xml = PICASA_MINIMAL_PHOTO_ENTRY_TEMPLATE  % (id, title, url, ct, editLink, editMediaLink, editMediaCT)
            dom = ZDom()
            dom.loadXML(xml)
            return dom.documentElement
        else:
            return None
    # end getMimimalMetaDataNode

# end ZPicasaPhotoEntry

#--------------------------------------------
# Add photos
#--------------------------------------------
class ZPicasaAddPhotoRequest(ZPicasaRequest):

    def __init__(self, url, username, password):
        ZPicasaRequest.__init__(self, url, username, password)
        self._setMethod(HTTP_POST)
    # end __init__()

    def getPhoto(self):
        if self.getDom():
            node = self.getDom().selectSingleNode(u"/atom:entry") #$NON-NLS-1$
            return ZPicasaPhotoEntry(node)
        else:
            return None
    # end  getPhoto()
# end  ZPicasaAddPhotoRequest

#--------------------------------------------
# Update photos
#--------------------------------------------
class ZPicasaUpdatePhotoRequest(ZPicasaAddPhotoRequest):

    def __init__(self, url, username, password):
        ZPicasaAddPhotoRequest.__init__(self, url, username, password)
        self._setMethod(HTTP_PUT)
    # end __init__()
# end  ZPicasaUpdatePhotoRequest

#--------------------------------------------
# new photo
#--------------------------------------------
class ZPicasaNewPhotoEntryDocument(ZAtomEntryDocument):

    def __init__(self):
        ZAtomEntryDocument.__init__(self)
    # end __init__()

    def _initNode(self, dom):
        # FIXME - need template
        dom.loadXML(PICASA_NEW_ALBUM_ENTRY_TEMPLATE)
        dom.setNamespaceMap(PICASA_NSS_MAP)
    # end _initNode
# end ZPicasaNewPhotoEntryDocument

#--------------------------------------------
# update photo
#--------------------------------------------
class ZPicasaUpdatePhotoEntryDocument(ZPicasaNewPhotoEntryDocument):

    def __init__(self):
        ZPicasaNewPhotoEntryDocument.__init__(self)
    # end __init__()

    def _initNode(self, dom):
        # FIXME - need template
        dom.loadXML(PICASA_NEW_ALBUM_ENTRY_TEMPLATE)
        dom.setNamespaceMap(PICASA_NSS_MAP)
    # end _initNode
# end ZPicasaUpdatePhotoEntryDocument

#================================================
# Picasa Atom Server
#================================================
class ZPicasaServer(ZAtomServerBase):
    BASE_URL = u"http://picasaweb.google.com/data/feed/api/user/" #$NON-NLS-1$

    def __init__(self, username, password, url = None): #$NON-NLS-1$
        scheme = ZGoogleLoginAuthHandler.SCHEME
        self.baseURL = url
        if not self.baseURL:
            self.baseURL = ZPicasaServer.BASE_URL
        ZAtomServerBase.__init__(self, self.baseURL, username, password, scheme, None, u"ZPicasaServer") #$NON-NLS-1$
        self.userID = username
    # end __init__()

    def _sendAtomRequest(self, atomRequest):
        self._debug(u"ZPicasaServer using userid %s " % self.userID) #$NON-NLS-1$
        self._debug(u"ZPicasaServer sendAtomRequest %s" % atomRequest.getUrl()) #$NON-NLS-1$
        try:
            ZAtomServerBase._sendAtomRequest(self, atomRequest)
            self._debug(u"ZPicasaServer response %s %s" % (atomRequest.getHttpStatusCode(), atomRequest.getHttpStatusMessage()) )#$NON-NLS-1$
        except Exception, e:
            self._warning(u"ZPicasaServer error %s %s" % (atomRequest.getHttpStatusCode(), atomRequest.getHttpStatusMessage()) )#$NON-NLS-1$
            # code 404 = album or photo not found.
            if atomRequest.getHttpStatusCode() != 404:
                raise e
    # end _sendAtomRequest()

    def _getUserID(self):
        return self.userID
    # end _getUserID()

    def _getUserIDUrl(self):
        return self.baseURL + self._getUserID()
    # end _getUserIDUrl()

    def listAlbums(self):
        # list albums GET http://picasaweb.google.com/data/feed/api/user/<userID>?kind=album
        self._debug(u"ZPicasaServer issue listAlbums") #$NON-NLS-1$
        url = self._getUserIDUrl() + u"?kind=album" #$NON-NLS-1$
        req = ZPicasaListAlbumsRequest(url, self.getUsername(), self.getPassword())
        self._sendAtomRequest(req)
        rval = req.getEntries()
        self._debug(u"ZPicasaServer album count %d" % len(rval)) #$NON-NLS-1$
        return rval
    # end listAlbums()

    def listPhotosByAlbumName(self, albumName):
        # list photos GET http://picasaweb.google.com/data/feed/api/user/<userID>/album/<albumName>?kind=photo
        url = self._getUserIDUrl() + u"/album/%s?kind=photo" % albumName #$NON-NLS-1$
        return self._listPhotos(url)
    # end listPhotosByAlbumName()

    def listPhotosByAlbumID(self, albumID):
        # list photos GET http://picasaweb.google.com/data/feed/api/user/<userID>/albumID/<albumID>?kind=photo
        url = self._getUserIDUrl() + u"/albumID/%s?kind=photo" % albumID #$NON-NLS-1$
        return self._listPhotos(url)
    # end listPhotosByAlbumID()

    def _listPhotos(self, listPhotosUrl):
        req = ZPicasaListPhotosRequest(listPhotosUrl, self.getUsername(), self.getPassword())
        self._sendAtomRequest(req)
        return req.getEntries()
    # end _listPhotos()

    def addAlbum(self, albumName):
        self._debug(u"ZPicasaServer issue addAlbum %s" % albumName) #$NON-NLS-1$
        albumNewEntry = ZPicasaNewAlbumEntryDocument()
        albumNewEntry.setTitle(albumName)
        url = self._getUserIDUrl()
        req = ZPicasaAddAlbumRequest(url, self.getUsername(), self.getPassword())
        self._sendAtomDocument(req, albumNewEntry)
        album = req.getAlbum()
        self._debug(u"ZPicasaServer new album name is  %s" % album.getAlbumName()) #$NON-NLS-1$
        return album
    # end addAlbum()

    def deleteResource(self, resourceEditLink):
        req = ZPicasaDeleteRequest(resourceEditLink, self.getUsername(), self.getPassword() )
        self._sendAtomRequest(req)
        return True
    # end deleteResource

    def addPhotoFile(self, albumName, photoFilename):
        self._debug(u"ZPicasaServer issue addPhotoFile (album %s) %s" % (albumName, photoFilename)) #$NON-NLS-1$
        url = self._getUserIDUrl() + u"/album/%s" % albumName #$NON-NLS-1$
        req = ZPicasaAddPhotoRequest(url, self.getUsername(), self.getPassword() )
        return self._sendPhotoFile(req, photoFilename)
    # end addPhotoFile

    def updatePhotoFile(self, resourceEditLink, photoFilename):
        self._debug(u"ZPicasaServer issue updatePhotoFile (edit %s) %s" % (resourceEditLink, photoFilename)) #$NON-NLS-1$
        req = ZPicasaUpdatePhotoRequest(resourceEditLink, self.getUsername(), self.getPassword() )
        return self._sendPhotoFile(req, photoFilename)
    # end updatePhotoFile

    def _sendPhotoFile(self, picasaAtomRequest, photoFilename):
        if hasattr(photoFilename, u'read'): #$NON-NLS-1$
            fd = photoFilename
        else:
            photoFilename = os.path.abspath( photoFilename )
            if not os.path.exists(photoFilename):
                raise ZPicasaException(u"File not found: %s" % photoFilename) #$NON-NLS-1$
            fd = open(photoFilename, u'rb') #$NON-NLS-1$
        try:
            self._initAtomRequest(picasaAtomRequest)
            picasaAtomRequest.send( fd )
        finally:
            fd.close()
        photoEntry = picasaAtomRequest.getPhoto()
        self._debug(u"ZPicasaServer sendPhotoFile response url %s" % photoEntry.getUrl()) #$NON-NLS-1$
        return photoEntry
    # end _sendPhotoFile

# end ZPicasaServer



