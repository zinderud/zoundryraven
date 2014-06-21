from zoundry.appframework.engine.service import IZService
from zoundry.base.net.http import joinUrl

# --------------------------------------------
# System names assigned to blog definitions
# --------------------------------------------
BLOGGER = u"Blogger.com" #$NON-NLS-1$
TYPEPAD = u"TypePad" #$NON-NLS-1$
CUSTOMATOM = u"Custom Atom" #$NON-NLS-1$
WORDPRESS = u"Wordpress" #$NON-NLS-1$
MTSERVER = u"Six Apart Movable Type" #$NON-NLS-1$
MOVABLETYPE = u"Movable Type" #$NON-NLS-1$
METAWEBLOG = u"MetaWeblog" #$NON-NLS-1$
LIVEJOURNAL = u"LiveJournal" #$NON-NLS-1$
BLOGGER_V1 = u"Blogger v1 API" #$NON-NLS-1$
BLOGGER_V2 = u"Blogger v2 API" #$NON-NLS-1$
MSNSPACES = u"MSNSpaces" #$NON-NLS-1$


# -----------------------------------------------------------------------------------------
# The Blog Systems interface.  The Blog Systems service provides high level information
# about the blog systems that the application has knowledge about.
# -----------------------------------------------------------------------------------------
class IZBlogSystems:

    DRAFT_SUPPORT = u"draft-support" #$NON-NLS-1$
    CATEGORIES_SUPPORT = u"categories-support" #$NON-NLS-1$
    CAN_ADD_CATEGORIES = u"can-add-categories" #$NON-NLS-1$
    SINGLE_SELECT_CATEGORIES = u"single-select-categories" #$NON-NLS-1$
    CAN_EDIT_ENDPOINT = u"can-edit-endpoint" #$NON-NLS-1$
    MEDIA_UPLOAD_SUPPORT = u"media-upload-support" #$NON-NLS-1$
    EXTENDED_ENTRY_SUPPORT = u"extended-entry-support" #$NON-NLS-1$

    REMOVE_LINEBREAK_ON_PUBLISH = u"publish-remove-linebreak" #$NON-NLS-1$
    CONVERT_LINEBREAK_ON_DOWNLOAD = u"download-convert-linebreak" #$NON-NLS-1$
    AUTO_DOWNLOAD_TEMPLATE = u"auto-download-template" #$NON-NLS-1$

    def getBlogSystems(self):
        u"Gets the list of blog systems." #$NON-NLS-1$
    # end getBlogSystems()

    def getBlogSystemNames(self):
        u"Gets the list of blog systems (names only)." #$NON-NLS-1$
    # end getBlogSystems():

    def getBlogSystem(self, name):
        u"Gets a single blog system by its name." #$NON-NLS-1$
    # end getBlogSystem()

    def getAliasList(self):
        u"Gets the list of blog aliases." #$NON-NLS-1$
    # end getAliasList()

    def getAliasByName(self, name):
        u"Gets a single alias by its name." #$NON-NLS-1$
    # end getAliasByName()

# end IZBlogSystems


# -----------------------------------------------------------------------------------------
# The concrete implementation of the IZBlogSystems interface/service.  This class will
# load blog system information from both hard-coded data found here in the code AND from
# the plugin registry.
# -----------------------------------------------------------------------------------------
class ZBlogSystems(IZBlogSystems, IZService):

    def __init__(self):
        pass
    # end __init__()

    def start(self, applicationModel):
        self.applicationModel = applicationModel
        self.systems = self._loadBlogSystems()
        self.aliases = self._createAliases()
    # end start()

    def stop(self):
        pass
    # end stop()

    # Load the list of supported blog systems (from a config file at some point).
    def _loadBlogSystems(self):
        rval = {}

        # blogger.com
        rval[BLOGGER] = ZBlogSystem(BLOGGER, u"Atom", u"https://www.blogger.com", u"443", u"/atom", u"blogger") #$NON-NLS-5$ #$NON-NLS-4$ #$NON-NLS-3$ #$NON-NLS-2$ #$NON-NLS-1$
        rval[BLOGGER].setExtAttribute(u"auth-type", u"BASIC") #$NON-NLS-2$ #$NON-NLS-1$
        rval[BLOGGER].setExtAttribute(IZBlogSystems.DRAFT_SUPPORT, u"true")  #$NON-NLS-1$
        rval[BLOGGER].setExtAttribute(IZBlogSystems.AUTO_DOWNLOAD_TEMPLATE, u"true")  #$NON-NLS-1$
        rval[BLOGGER].setExtAttribute(IZBlogSystems.REMOVE_LINEBREAK_ON_PUBLISH, u"false") #$NON-NLS-1$
#        rval[BLOGGER].setExtAttribute(IZBlogSystems.CONVERT_LINEBREAK_ON_DOWNLOAD, u"false") #$NON-NLS-1$

        # Typepad
        rval[TYPEPAD] = ZBlogSystem(TYPEPAD, u"Atom", u"http://www.typepad.com", u"80", u"/t/atom/weblog", u"typepad") #$NON-NLS-5$ #$NON-NLS-4$ #$NON-NLS-3$ #$NON-NLS-2$ #$NON-NLS-1$
        rval[TYPEPAD].setExtAttribute(IZBlogSystems.CATEGORIES_SUPPORT, u"atom-typepad") #$NON-NLS-1$
        rval[TYPEPAD].setExtAttribute(IZBlogSystems.MEDIA_UPLOAD_SUPPORT, u"true") #$NON-NLS-1$
        rval[TYPEPAD].setExtAttribute(IZBlogSystems.AUTO_DOWNLOAD_TEMPLATE, u"true")  #$NON-NLS-1$
        rval[TYPEPAD].setExtAttribute(IZBlogSystems.REMOVE_LINEBREAK_ON_PUBLISH, u"false") #$NON-NLS-1$
#        rval[TYPEPAD].setExtAttribute(IZBlogSystems.CONVERT_LINEBREAK_ON_DOWNLOAD, u"false") #$NON-NLS-1$

        # Custom Atom
        rval[CUSTOMATOM] = ZBlogSystem(CUSTOMATOM, u"Atom", u"", u"", u"", u"atom")         #$NON-NLS-5$ #$NON-NLS-4$ #$NON-NLS-3$ #$NON-NLS-2$ #$NON-NLS-1$
        rval[CUSTOMATOM].setExtAttribute(IZBlogSystems.CAN_EDIT_ENDPOINT, u"true") #$NON-NLS-1$
        rval[CUSTOMATOM].setExtAttribute(IZBlogSystems.REMOVE_LINEBREAK_ON_PUBLISH, u"false") #$NON-NLS-1$
        rval[CUSTOMATOM].setExtAttribute(IZBlogSystems.CONVERT_LINEBREAK_ON_DOWNLOAD, u"false") #$NON-NLS-1$

        # xml-rpc Wordpress
        rval[WORDPRESS] = ZBlogSystem(WORDPRESS, u"xmlrpc.wordpress", u"", u"80", u"", u"wordpress")         #$NON-NLS-5$ #$NON-NLS-4$ #$NON-NLS-3$ #$NON-NLS-2$ #$NON-NLS-1$
        rval[WORDPRESS].setExtAttribute(IZBlogSystems.CATEGORIES_SUPPORT, u"xmlrpc-mt") #$NON-NLS-1$
        rval[WORDPRESS].setExtAttribute(IZBlogSystems.CAN_EDIT_ENDPOINT, u"true") #$NON-NLS-1$
        rval[WORDPRESS].setExtAttribute(IZBlogSystems.MEDIA_UPLOAD_SUPPORT, u"true") #$NON-NLS-1$
        rval[WORDPRESS].setExtAttribute(IZBlogSystems.DRAFT_SUPPORT, u"true")  #$NON-NLS-1$
        rval[WORDPRESS].setExtAttribute(IZBlogSystems.EXTENDED_ENTRY_SUPPORT, u"true")  #$NON-NLS-1$
        rval[WORDPRESS].setExtAttribute(IZBlogSystems.REMOVE_LINEBREAK_ON_PUBLISH, u"false") #$NON-NLS-1$
        rval[WORDPRESS].setExtAttribute(IZBlogSystems.CONVERT_LINEBREAK_ON_DOWNLOAD, u"false") #$NON-NLS-1$

        # Six Apart xml-rpc MovableType
        rval[MTSERVER] = ZBlogSystem(MTSERVER, u"xmlrpc.movabletype", u"", u"80", u"", u"movabletype")         #$NON-NLS-5$ #$NON-NLS-4$ #$NON-NLS-3$ #$NON-NLS-2$ #$NON-NLS-1$
        rval[MTSERVER].setExtAttribute(IZBlogSystems.CATEGORIES_SUPPORT, u"xmlrpc-mt") #$NON-NLS-1$
        rval[MTSERVER].setExtAttribute(IZBlogSystems.CAN_EDIT_ENDPOINT, u"true") #$NON-NLS-1$
        rval[MTSERVER].setExtAttribute(IZBlogSystems.MEDIA_UPLOAD_SUPPORT, u"true") #$NON-NLS-1$
        rval[MTSERVER].setExtAttribute(IZBlogSystems.REMOVE_LINEBREAK_ON_PUBLISH, u"false") #$NON-NLS-1$
        rval[MTSERVER].setExtAttribute(IZBlogSystems.EXTENDED_ENTRY_SUPPORT, u"true")  #$NON-NLS-1$
        rval[MTSERVER].setExtAttribute(IZBlogSystems.AUTO_DOWNLOAD_TEMPLATE, u"true")  #$NON-NLS-1$
        rval[MTSERVER].setExtAttribute(IZBlogSystems.DRAFT_SUPPORT, u"true")  #$NON-NLS-1$

        #  generic xml-rpc MovableType
        rval[MOVABLETYPE] = ZBlogSystem(MOVABLETYPE, u"xmlrpc.mt", u"", u"80", u"", u"mt-xmlrpc")         #$NON-NLS-5$ #$NON-NLS-4$ #$NON-NLS-3$ #$NON-NLS-2$ #$NON-NLS-1$
        rval[MOVABLETYPE].setExtAttribute(IZBlogSystems.CATEGORIES_SUPPORT, u"xmlrpc-mt") #$NON-NLS-1$
        rval[MOVABLETYPE].setExtAttribute(IZBlogSystems.CAN_EDIT_ENDPOINT, u"true") #$NON-NLS-1$
        rval[MOVABLETYPE].setExtAttribute(IZBlogSystems.MEDIA_UPLOAD_SUPPORT, u"true") #$NON-NLS-1$
        rval[MOVABLETYPE].setExtAttribute(IZBlogSystems.DRAFT_SUPPORT, u"true")  #$NON-NLS-1$
        rval[MOVABLETYPE].setExtAttribute(IZBlogSystems.EXTENDED_ENTRY_SUPPORT, u"true")  #$NON-NLS-1$
        rval[MOVABLETYPE].setExtAttribute(IZBlogSystems.REMOVE_LINEBREAK_ON_PUBLISH, u"false") #$NON-NLS-1$

        #  generic xml-rpc MetaWeblog
        rval[METAWEBLOG] = ZBlogSystem(METAWEBLOG, u"xmlrpc.metaweblog", u"", u"80", u"", u"metaweblog-xmlrpc")         #$NON-NLS-5$ #$NON-NLS-4$ #$NON-NLS-3$ #$NON-NLS-2$ #$NON-NLS-1$
        rval[METAWEBLOG].setExtAttribute(IZBlogSystems.CATEGORIES_SUPPORT, u"xmlrpc-metweblog") #$NON-NLS-1$
        rval[METAWEBLOG].setExtAttribute(IZBlogSystems.CAN_EDIT_ENDPOINT, u"true") #$NON-NLS-1$
        rval[METAWEBLOG].setExtAttribute(IZBlogSystems.MEDIA_UPLOAD_SUPPORT, u"true") #$NON-NLS-1$
        rval[METAWEBLOG].setExtAttribute(IZBlogSystems.DRAFT_SUPPORT, u"true")  #$NON-NLS-1$
        rval[METAWEBLOG].setExtAttribute(IZBlogSystems.REMOVE_LINEBREAK_ON_PUBLISH, u"false") #$NON-NLS-1$

        # xml-rpc live journal
        rval[LIVEJOURNAL] = ZBlogSystem(LIVEJOURNAL, u"xmlrpc.livejournal", u"", u"80", u"", u"livejournal")         #$NON-NLS-5$ #$NON-NLS-4$ #$NON-NLS-3$ #$NON-NLS-2$ #$NON-NLS-1$
        rval[LIVEJOURNAL].setExtAttribute(IZBlogSystems.CATEGORIES_SUPPORT, u"xmlrpc-lj") #$NON-NLS-1$
        rval[LIVEJOURNAL].setExtAttribute(IZBlogSystems.CAN_EDIT_ENDPOINT, u"true") #$NON-NLS-1$
        rval[LIVEJOURNAL].setExtAttribute(IZBlogSystems.MEDIA_UPLOAD_SUPPORT, u"true") #$NON-NLS-1$
        rval[LIVEJOURNAL].setExtAttribute(IZBlogSystems.DRAFT_SUPPORT, u"true")  #$NON-NLS-1$
        rval[LIVEJOURNAL].setExtAttribute(IZBlogSystems.REMOVE_LINEBREAK_ON_PUBLISH, u"false") #$NON-NLS-1$
        rval[LIVEJOURNAL].setExtAttribute(IZBlogSystems.CONVERT_LINEBREAK_ON_DOWNLOAD, u"false") #$NON-NLS-1$
        rval[LIVEJOURNAL].setExtAttribute(IZBlogSystems.SINGLE_SELECT_CATEGORIES, u"true") #$NON-NLS-1$

        # blogger v1 xml rpc API
        rval[BLOGGER_V1] = ZBlogSystem(BLOGGER_V1, u"xmlrpc.bloggerv1", u"", u"80", u"", u"bloggerv1-xmlrpc")         #$NON-NLS-5$ #$NON-NLS-4$ #$NON-NLS-3$ #$NON-NLS-2$ #$NON-NLS-1$
        rval[BLOGGER_V1].setExtAttribute(IZBlogSystems.CAN_EDIT_ENDPOINT, u"true") #$NON-NLS-1$
        rval[BLOGGER_V1].setExtAttribute(IZBlogSystems.DRAFT_SUPPORT, u"true")  #$NON-NLS-1$
        rval[BLOGGER_V1].setExtAttribute(IZBlogSystems.REMOVE_LINEBREAK_ON_PUBLISH, u"false") #$NON-NLS-1$

        # blogger v2 xml rpc API
        rval[BLOGGER_V2] = ZBlogSystem(BLOGGER_V2, u"xmlrpc.bloggerv2", u"", u"80", u"", u"bloggerv2-xmlrpc")  #$NON-NLS-5$ #$NON-NLS-4$ #$NON-NLS-3$ #$NON-NLS-2$ #$NON-NLS-1$
        rval[BLOGGER_V2].setExtAttribute(IZBlogSystems.CAN_EDIT_ENDPOINT, u"true") #$NON-NLS-1$
        rval[BLOGGER_V2].setExtAttribute(IZBlogSystems.DRAFT_SUPPORT, u"true")  #$NON-NLS-1$
        rval[BLOGGER_V2].setExtAttribute(IZBlogSystems.REMOVE_LINEBREAK_ON_PUBLISH, u"false") #$NON-NLS-1$

        rval[MSNSPACES] = ZBlogSystem(MSNSPACES, u"xmlrpc.msnspaces", u"https://storage.msn.com", u"443", u"/storageservice/MetaWeblog.rpc", u"msnspaces")  #$NON-NLS-5$ #$NON-NLS-4$ #$NON-NLS-3$ #$NON-NLS-2$ #$NON-NLS-1$
        rval[MSNSPACES].setExtAttribute(IZBlogSystems.CAN_EDIT_ENDPOINT, u"false") #$NON-NLS-1$
        rval[MSNSPACES].setExtAttribute(IZBlogSystems.DRAFT_SUPPORT, u"true") #$NON-NLS-1$
        rval[MSNSPACES].setExtAttribute(IZBlogSystems.CATEGORIES_SUPPORT, u"xmlrpc-metweblog,single,editable")#$NON-NLS-1$
        rval[MSNSPACES].setExtAttribute(IZBlogSystems.REMOVE_LINEBREAK_ON_PUBLISH, u"false")#$NON-NLS-1$
        rval[MSNSPACES].setExtAttribute(IZBlogSystems.CONVERT_LINEBREAK_ON_DOWNLOAD, u"false")        #$NON-NLS-1$
        rval[MSNSPACES].setExtAttribute(IZBlogSystems.SINGLE_SELECT_CATEGORIES, u"true")#$NON-NLS-1$
        rval[MSNSPACES].setExtAttribute(IZBlogSystems.CAN_ADD_CATEGORIES, u"true")#$NON-NLS-1$
        rval[MSNSPACES].setExtAttribute(IZBlogSystems.AUTO_DOWNLOAD_TEMPLATE, u"true")  #$NON-NLS-1$

        return rval
    # end _loadBlogSystems()

    def _createAliases(self):
        aList = []

        # community server
        ba = ZBlogSystemAlias(ZBlogSystemAlias.COMMUNITY_SERVER, self.systems[METAWEBLOG], u"", u"communityserver") #$NON-NLS-3$ #$NON-NLS-2$ #$NON-NLS-1$
        ba.setEndpointHint(u"http://HOST/blogs/metablog.ashx")  #$NON-NLS-1$
        aList.append(ba)

        # blogger.
        ba = ZBlogSystemAlias(ZBlogSystemAlias.BLOGGER, self.systems[BLOGGER], endpointEditable=False)
        aList.append(ba)

        # blog harbor
        ba = ZBlogSystemAlias(ZBlogSystemAlias.BLOGHARBOR, self.systems[MOVABLETYPE], u"https://www.blogware.com/xmlrpc.cgi", u"blogharbor") #$NON-NLS-3$ #$NON-NLS-2$ #$NON-NLS-1$
        aList.append(ba)

        # blogware
        ba = ZBlogSystemAlias(ZBlogSystemAlias.BLOGWARE, self.systems[MOVABLETYPE], u"https://www.blogware.com/xmlrpc.cgi") #$NON-NLS-2$ #$NON-NLS-1$
        aList.append(ba)

        # dasBlog
        ba = ZBlogSystemAlias(ZBlogSystemAlias.DASBLOG, self.systems[METAWEBLOG], u"", u"dasblog") #$NON-NLS-3$ #$NON-NLS-2$ #$NON-NLS-1$
        ba.setEndpointHint(u"http://HOST/PATH_to_BLOG/blogger.aspx")  #$NON-NLS-1$
        aList.append(ba)

        # drupal
        ba = ZBlogSystemAlias(ZBlogSystemAlias.DRUPAL, self.systems[MOVABLETYPE], u"", u"drupal") #$NON-NLS-3$ #$NON-NLS-2$ #$NON-NLS-1$
        ba.setEndpointHint(u"http://HOST/PATH_to_BLOG/xmlrpc.php")  #$NON-NLS-1$
        aList.append(ba)

        # lifetype
        ba = ZBlogSystemAlias(ZBlogSystemAlias.LIFETYPE, self.systems[METAWEBLOG], u"", u"lifetype") #$NON-NLS-3$ #$NON-NLS-2$ #$NON-NLS-1$
        ba.setEndpointHint(u"http://HOST/PATH_to_BLOG/xmlrpc.php")  #$NON-NLS-1$
        aList.append(ba)

        # LJ.
        ba = ZBlogSystemAlias(ZBlogSystemAlias.LIVEJOURNAL, self.systems[LIVEJOURNAL], u"http://www.livejournal.com/interface/xmlrpc", endpointEditable=False) #$NON-NLS-2$ #$NON-NLS-1$
        aList.append(ba)

        # MSN Spaces.
        ba = ZBlogSystemAlias(ZBlogSystemAlias.MSNSPACES, self.systems[MSNSPACES], endpointEditable=False, maxNumPosts=20)
        ba.setEndpointHint(u"https://storage.msn.com/storageservice/MetaWeblog.rpc")  #$NON-NLS-1$
        aList.append(ba)

        # nucleus
        ba = ZBlogSystemAlias(ZBlogSystemAlias.NUCLEUS, self.systems[MOVABLETYPE], u"", u"nucleus", maxNumPosts=20) #$NON-NLS-3$ #$NON-NLS-2$ #$NON-NLS-1$
        ba.setEndpointHint(u"http://HOST/PATH_to_BLOG/nucleus/xmlrpc/server.php")  #$NON-NLS-1$
        aList.append(ba)

        # six apart mt server.
        ba = ZBlogSystemAlias(ZBlogSystemAlias.MOVABLETYPE, self.systems[MTSERVER], u"") #$NON-NLS-2$ #$NON-NLS-1$
        ba.setEndpointHint(u"http://HOST/PATH_to_BLOG/cgi-bin/mt/mt-xmlrpc.cgi")  #$NON-NLS-1$
        aList.append(ba)

        # roller
        ba = ZBlogSystemAlias(ZBlogSystemAlias.ROLLER, self.systems[METAWEBLOG], u"", u"roller") #$NON-NLS-3$ #$NON-NLS-2$ #$NON-NLS-1$
        ba.setEndpointHint(u"http://HOST/xmlrpc or http://blogs.HOST/roller/xmlrpc")  #$NON-NLS-1$
        aList.append(ba)

        # squarespace
        ba = ZBlogSystemAlias(ZBlogSystemAlias.SQUARESPACE, self.systems[METAWEBLOG], u"http://www.squarespace.com/do/process/external/PostInterceptor", u"squarespace") #$NON-NLS-3$ #$NON-NLS-2$ #$NON-NLS-1$
        aList.append(ba)

        # text pattern
        ba = ZBlogSystemAlias(ZBlogSystemAlias.TEXTPATTERN, self.systems[MOVABLETYPE], u"", u"textpattern", maxNumPosts=20) #$NON-NLS-3$ #$NON-NLS-2$ #$NON-NLS-1$
        ba.setEndpointHint(u"http://HOST/rpc/ or http://HOST/textpattern/xmlrpcs.php")  #$NON-NLS-1$
        aList.append(ba)

        # typepad - atom
        ba = ZBlogSystemAlias(ZBlogSystemAlias.TYPEPAD_ATOM, self.systems[TYPEPAD], endpointEditable=False) #$NON-NLS-1$
        aList.append(ba)

        # typepad xmlrpc mt server.
        ba = ZBlogSystemAlias(ZBlogSystemAlias.TYPEPAD_MT, self.systems[MTSERVER], u"http://www.typepad.com/t/api", u"typepad") #$NON-NLS-3$ #$NON-NLS-2$ #$NON-NLS-1$
        aList.append(ba)

        # wordpress.
        ba = ZBlogSystemAlias(ZBlogSystemAlias.WORDPRESS, self.systems[WORDPRESS], u"") #$NON-NLS-1$
        ba.setEndpointHint(u"http://HOST/PATH_to_BLOG/xmlrpc.php")  #$NON-NLS-1$
        aList.append(ba)

        # wordpress.
        ba = ZBlogSystemAlias(ZBlogSystemAlias.WPDOTCOM, self.systems[WORDPRESS], u"", u"wpdotcom") #$NON-NLS-1$ #$NON-NLS-2$
        ba.setEndpointHint(u"http://blogname.wordpress.com/xmlrpc.php")  #$NON-NLS-1$
        aList.append(ba)

        # Xaraya
        ba = ZBlogSystemAlias(ZBlogSystemAlias.XARAYA, self.systems[METAWEBLOG], u"", u"xaraya") #$NON-NLS-3$ #$NON-NLS-2$ #$NON-NLS-1$
        aList.append(ba)

        # Xoops
        ba = ZBlogSystemAlias(ZBlogSystemAlias.XOOPS, self.systems[METAWEBLOG], u"", u"xoops") #$NON-NLS-3$ #$NON-NLS-2$ #$NON-NLS-1$
        ba.setEndpointHint(u"http://HOST/xmlrpc.php")  #$NON-NLS-1$
        aList.append(ba)


        # custom atom.
        ba = ZBlogSystemAlias(ZBlogSystemAlias.CUSTOM_ATOM, self.systems[CUSTOMATOM], u"") #$NON-NLS-2$ #$NON-NLS-1$
        aList.append(ba)

        # custom LJ.
        ba = ZBlogSystemAlias(ZBlogSystemAlias.CUSTOM_LIVEJOURNAL, self.systems[LIVEJOURNAL], u"") #$NON-NLS-2$ #$NON-NLS-1$
        ba.setEndpointHint(u"http://HOST/interface/xmlrpc")  #$NON-NLS-1$
        aList.append(ba)

        # metaweblog api
        ba = ZBlogSystemAlias(ZBlogSystemAlias.CUSTOM_METAWEBLOG, self.systems[METAWEBLOG], u"", maxNumPosts=20) #$NON-NLS-2$ #$NON-NLS-1$
        aList.append(ba)

        # mt api
        ba = ZBlogSystemAlias(ZBlogSystemAlias.CUSTOM_MOVABLETYPE, self.systems[MOVABLETYPE], u"", maxNumPosts=20) #$NON-NLS-2$ #$NON-NLS-1$
        aList.append(ba)

        # blogger v1 api
        ba = ZBlogSystemAlias(ZBlogSystemAlias.CUSTOM_BLOGGER_V1, self.systems[BLOGGER_V1], u"", maxNumPosts=20) #$NON-NLS-2$ #$NON-NLS-1$
        aList.append(ba)

        # blogger v2 api
        ba = ZBlogSystemAlias(ZBlogSystemAlias.CUSTOM_BLOGGER_V2, self.systems[BLOGGER_V2], u"", maxNumPosts=20) #$NON-NLS-2$ #$NON-NLS-1$
        aList.append(ba)

        return aList
    # end _createAliases()

    # Gets the list of blog systems.
    def getBlogSystems(self):
        return self.systems.values()
    # end getBlogSystems()

    # Gets the list of blog systems (names only).
    def getBlogSystemNames(self):
        return self.systems.keys()
    # end getBlogSystems():

    # Gets a single blog system by its name.
    def getBlogSystem(self, name):
        return self.systems[name]
    # end getBlogSystem()

    def getAliasList(self):
        return self.aliases
    # end getAliasList()

    def getAliasByName(self, name):
        rVal = None
        for alias in self.aliases:
            if alias.getName() == name:
                rVal = alias
                break
        return rVal
    # end getAliasByName()

# end ZBlogSystems


# -----------------------------------------------------------------------------------------
# A user friendly alias/wrapper for the blog system or account type.
# -----------------------------------------------------------------------------------------
class ZBlogSystemAlias:

    # well known names
    BLOGGER = u"Blogger"#$NON-NLS-1$
    TYPEPAD_ATOM = u"Typepad (Atom API)"#$NON-NLS-1$
    TYPEPAD_MT = u"Typepad (MT API)"#$NON-NLS-1$
    MSNSPACES = u"MSN Spaces"#$NON-NLS-1$
    WORDPRESS = u"Wordpress"#$NON-NLS-1$
    WPDOTCOM = u"Wordpress.Com (Hosted)"#$NON-NLS-1$
    LIVEJOURNAL = u"LiveJournal"#$NON-NLS-1$
    MOVABLETYPE = u"Six Apart MovableType Server"#$NON-NLS-1$
    BLOGHARBOR = u"BlogHarbor"#$NON-NLS-1$
    BLOGWARE = u"Blogware"#$NON-NLS-1$
    LIFETYPE = u"LifeType (pLog)"#$NON-NLS-1$
    NUCLEUS = u"Nucleus"#$NON-NLS-1$
    DRUPAL = u"Drupal"#$NON-NLS-1$
    COMMUNITY_SERVER = u"CommunityServer"#$NON-NLS-1$
    ROLLER = u"Roller"#$NON-NLS-1$
    SQUARESPACE = u"SquareSpace"#$NON-NLS-1$
    DASBLOG = u"dasBlog"#$NON-NLS-1$
    TEXTPATTERN = u"TextPattern"#$NON-NLS-1$
    XOOPS = u"Xoops"#$NON-NLS-1$
    XARAYA = u"Xaraya"#$NON-NLS-1$
    CUSTOM_ATOM = u"Custom Atom API"#$NON-NLS-1$
    CUSTOM_MOVABLETYPE = u"Custom MovableType API"#$NON-NLS-1$
    CUSTOM_METAWEBLOG = u"Custom MetaWeblog API"#$NON-NLS-1$
    CUSTOM_LIVEJOURNAL = u"Custom LiveJournal API"#$NON-NLS-1$
    CUSTOM_BLOGGER_V1 = u"Custom Blogger V1 API"#$NON-NLS-1$
    CUSTOM_BLOGGER_V2 = u"Custom Blogger V2 API"#$NON-NLS-1$

    def __init__(self, name, blogSystem, url = None, resId = None, endpointEditable=True, maxNumPosts=500):
        self.name = name
        self.blogSystem = blogSystem
        self.endpointEditable = endpointEditable
        self.maxNumPosts = maxNumPosts
        self.endpointHint = u""#$NON-NLS-1$
        if url:
            self.url = url
        else:
            self.url = blogSystem.getUrl()
        if resId:
            self.resourceId = resId
        else:
            self.resourceId = blogSystem.getResourceId()
    # end __init__()

    def getMaxNumPosts(self):
        return self.maxNumPosts
    # end getMaxNumPosts()

    def getName(self):
        return self.name
    # end getName()

    def getBlogSystem(self):
        return self.blogSystem
    # end getBlogSystem()

    def getUrl(self):
        return self.url
    # end getUrl()

    def setUrl(self, url):
        self.url = url
    # end setUrl()

    def getResourceId(self):
        return self.resourceId
    # end getResourceId()

    def isEndpointEditable(self):
        return self.endpointEditable
    # end isEndpointEditable()

    def setEndpointEditable(self, bEditable):
        self.endpointEditable = bEditable
    # end setEndpointEditable()

    def setEndpointHint(self, hint):
        if hint:
            self.endpointHint = hint
    # end setEndpointHint()

    def getEndpointHint(self):
        return self.endpointHint
    # end getEndpointHint()

#end ZBlogSystemAlias


#-----------------------------------------------------------------------------------
# Class Definition for BlogSystem.
#
# A Blog System describes services such as Blogger.com and TypePad.
#-----------------------------------------------------------------------------------
class ZBlogSystem:
    def __init__(self, name, type, host, port, path, resId):
        self.name = name
        self.type = type
        self.host = host
        self.port = port
        self.path = path
        self.resId = resId
        self.extAttrs = {}
    # end __init__()

    def getName(self):
        return self.name
    # end getName()

    def getType(self):
        return self.type
    # end getType()

    def getHost(self):
        return self.host
    # end getHost()

    def getPort(self):
        return self.port
    # end getPort()

    def getPath(self):
        return self.path
    # end getPath()

    def getUrl(self):
        return joinUrl(None, self.getHost(), self.getPort(), self.getPath())
    # end getUrl()

    def getResourceId(self):
        return self.resId
    # end getResourceId()

    def getExtAttribute(self, attrName, dflt = None):
        try:
            val = self.extAttrs[attrName]
            if not val:
                val = dflt
        except:
            val = dflt
        return val
    # end getExtAttribute()

    def setExtAttribute(self, attrName, attrVal):
        self.extAttrs[attrName] = attrVal
    # end setExtAttribute()

    # Returns true if this blog system supports categories.
    def supportsCategories(self):
        u"Returns true if this blog system supports categories." #$NON-NLS-1$
        return self.getExtAttribute(IZBlogSystems.CATEGORIES_SUPPORT) is not None
    # end supportsCategories()

    def canAddCategory(self):
        u"Returns true if this blog system supports user generated categories." #$NON-NLS-1$
        return self._getBoolAttribute(IZBlogSystems.CAN_ADD_CATEGORIES, False)
    # end canAddCategory()

    def isSingleSelectCategories(self):
        u"Returns true if this blog system supports only single select categories." #$NON-NLS-1$
        return self._getBoolAttribute(IZBlogSystems.SINGLE_SELECT_CATEGORIES, False)
    # end isSingleSelectCategories()

    def supportsMediaUpload(self):
        u"Returns true if this blog system supports a native file upload mechanism." #$NON-NLS-1$
        return self._getBoolAttribute(IZBlogSystems.MEDIA_UPLOAD_SUPPORT, False)
    # end supportsMediaUpload()

    def supportsDraftMode(self):
        return self._getBoolAttribute(IZBlogSystems.DRAFT_SUPPORT, False)
    # end supportsDraftMode()

    def supportsExtendedEntry(self):
        return self._getBoolAttribute(IZBlogSystems.EXTENDED_ENTRY_SUPPORT, False)
    # end supportsExtendedEntry()

    def canEditEndpoint(self):
        u"Returns true if this blog system api endpoint can be changed by the user" #$NON-NLS-1$
        return self._getBoolAttribute(IZBlogSystems.CAN_EDIT_ENDPOINT, False)
    # end canEditEndpoint()

    def shouldAutoDownloadTemplate(self):
        u"Returns true if the template should be automatically downloaded on new account creation." #$NON-NLS-1$
        return self._getBoolAttribute(IZBlogSystems.AUTO_DOWNLOAD_TEMPLATE, False)
    # end shouldAutoDownloadTemplate()

    # Returns the auth type for this blog system.
    def getAuthType(self):
        u"Returns the auth type for this blog system." #$NON-NLS-1$
        return self.getExtAttribute(u"auth-type") #$NON-NLS-1$
    # end getAuthType()

    def shouldRemoveLineBreak(self):
        u"Returns true if the linebreaks must be removed before posting" #$NON-NLS-1$
        return self._getBoolAttribute(IZBlogSystems.REMOVE_LINEBREAK_ON_PUBLISH, True)
    # end shouldRemoveLineBreak()

    def shouldConvertLineBreak(self):
        u"Returns true if the linebreaks should be converted to <br/> on download." #$NON-NLS-1$
        return self._getBoolAttribute(IZBlogSystems.CONVERT_LINEBREAK_ON_DOWNLOAD, True)
    # end shouldConvertLineBreak()

    def _getBoolAttribute(self, name, defaultValue=False):
        s =  self.getExtAttribute(name)
        rVal = defaultValue
        if s:
            s = s.strip().lower()
            if s == u"true": #$NON-NLS-1$
                rVal = True
            elif s == u"false": #$NON-NLS-1$
                rVal = False
        return rVal
    # end _getBoolAttribute()

# end ZBlogSystem
