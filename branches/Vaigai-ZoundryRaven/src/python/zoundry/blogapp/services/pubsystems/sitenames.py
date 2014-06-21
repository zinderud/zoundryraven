#==========================================================================================
#  List of well-known type-ids that we ship with.
#==========================================================================================
class DefaultTypes:

    ALL_TYPES = []
    BLOGGER_V1      = u"zoundry.blogapp.pubsystems.publisher.type.xmlrpc.blogger.v1" #$NON-NLS-1$
    ALL_TYPES.append(BLOGGER_V1)

    BLOGGER_V2      = u"zoundry.blogapp.pubsystems.publisher.type.xmlrpc.blogger.v2" #$NON-NLS-1$
    ALL_TYPES.append(BLOGGER_V2)

    METAWEBLOG      = u"zoundry.blogapp.pubsystems.publisher.type.xmlrpc.metaweblog" #$NON-NLS-1$
    ALL_TYPES.append(METAWEBLOG)

    WORDPRESS       = u"zoundry.blogapp.pubsystems.publisher.type.xmlrpc.wordpress" #$NON-NLS-1$
    ALL_TYPES.append(WORDPRESS)

    WIN_LIVE        = u"zoundry.blogapp.pubsystems.publisher.type.xmlrpc.windowslive" #$NON-NLS-1$
    ALL_TYPES.append(WIN_LIVE)

    MOVABLETYPE     = u"zoundry.blogapp.pubsystems.publisher.type.xmlrpc.movabletype" #$NON-NLS-1$
    ALL_TYPES.append(MOVABLETYPE)

    MOVABLETYPE_SA  = u"zoundry.blogapp.pubsystems.publisher.type.xmlrpc.sixapart.movabletype" #$NON-NLS-1$
    ALL_TYPES.append(MOVABLETYPE_SA)

    LIVEJOURNAL     = u"zoundry.blogapp.pubsystems.publisher.type.xmlrpc.lj" #$NON-NLS-1$
    ALL_TYPES.append(LIVEJOURNAL)

    ATOM_03         = u"zoundry.blogapp.pubsystems.publisher.type.atom.atom03" #$NON-NLS-1$
    ALL_TYPES.append(ATOM_03)

    ATOM_10         = u"zoundry.blogapp.pubsystems.publisher.type.atom.atom10" #$NON-NLS-1$
    ALL_TYPES.append(ATOM_10)

    ATOM_03_BLOGGER = u"zoundry.blogapp.pubsystems.publisher.type.atom.atom03.blogger" #$NON-NLS-1$
    ALL_TYPES.append(ATOM_03_BLOGGER)

    ATOM_10_GDATA   = u"zoundry.blogapp.pubsystems.publisher.type.atom.atom10.blogger" #$NON-NLS-1$
    ALL_TYPES.append(ATOM_10_GDATA)


#==========================================================================================
#  List of well-known site-ids that we ship with.
#==========================================================================================
class DefaultSites:

    ALL_SITES = []

    BLOGGER= u"zoundry.blogapp.pubsystems.publishers.site.blogger.atom10" #$NON-NLS-1$
    ALL_SITES.append(BLOGGER)
    #   legacy api=Atom10, acc=Blogger.com

    BLOGGER_LEGACY = u"zoundry.blogapp.pubsystems.publishers.site.blogger.atom03" #$NON-NLS-1$
    ALL_SITES.append(BLOGGER_LEGACY)
    #   legacy api=Atom, acc=Blogger.com

    TYPEPAD_XMLRPC = u"zoundry.blogapp.pubsystems.publishers.site.typepad.xmlrpc" #$NON-NLS-1$
    ALL_SITES.append(TYPEPAD_XMLRPC)
    #   legacy api=xmlrpc.movabletype , acc=Six Apart Movable Type, resid=typepad

    TYPEPAD_ATOM = u"zoundry.blogapp.pubsystems.publishers.site.typepad.atom03" #$NON-NLS-1$
    ALL_SITES.append(TYPEPAD_ATOM)
    #   legacy api=atom, acc=TypePad

    MSNSPACES = u"zoundry.blogapp.pubsystems.publishers.site.windowslivespaces" #$NON-NLS-1$
    ALL_SITES.append(MSNSPACES)
    #   legacy api=xmlrpc.msnspaces, acc=MSNSpaces, res=msnspaces

    WPDOTCOM = u"zoundry.blogapp.pubsystems.publishers.site.wordpress.com" #$NON-NLS-1$
    ALL_SITES.append(WPDOTCOM)
    #   legacy api=xmlrpc.wordpress, acc=Wordpress, res=wpdotcom

    WORDPRESS = u"zoundry.blogapp.pubsystems.publishers.site.wordpress" #$NON-NLS-1$
    ALL_SITES.append(WORDPRESS)
    #   legacy api=xmlrpc.wordpress acc=Wordpress, res=wordpress

    WORDPRESS22 = u"zoundry.blogapp.pubsystems.publishers.site.wordpress22" #$NON-NLS-1$
    ALL_SITES.append(WORDPRESS22)

    LJ = u"zoundry.blogapp.pubsystems.publishers.site.livejournal.com" #$NON-NLS-1$
    ALL_SITES.append(LJ)
    #   legacy api=xmlrpc.livejournal  acc=LiveJournal, HOST=www.livejournal.com (default to custom live-journal)

    SA_MOVABLE_TYPE = u"zoundry.blogapp.pubsystems.publishers.site.movabletype.sixapart" #$NON-NLS-1$
    ALL_SITES.append(SA_MOVABLE_TYPE)
    #   legacy api=xmlrpc.movabletype   acc=Six Apart Movable Type, res=?, HOST=match(/mt-xmlrpc.cgi)

    BLOGHARBOR = u"zoundry.blogapp.pubsystems.publishers.site.blogharbor" #$NON-NLS-1$
    ALL_SITES.append(BLOGHARBOR)
    #    legacy  api=  acc=MetaWeblog, res=blogharbor (check this before blogware, below)

    BLOGWARE = u"zoundry.blogapp.pubsystems.publishers.site.blogware" #$NON-NLS-1$
    ALL_SITES.append(BLOGWARE)
    #   legacy  api= acc=MetaWeblog, res=NA, URL=https://www.blogware.com/xmlrpc.cgi

    LIFETYPE = u"zoundry.blogapp.pubsystems.publishers.site.lifetype" #$NON-NLS-1$
    ALL_SITES.append(LIFETYPE)
    #    legacy api=xmlrpc.metaweblog  acc=MetaWeblog, res=lifetype

    NUCLEUS = u"zoundry.blogapp.pubsystems.publishers.site.nucleus" #$NON-NLS-1$
    ALL_SITES.append(NUCLEUS)
    #    legacy api=xmlrpc.mt  acc=Movable Type, res=nucleus

    DRUPAL = u"zoundry.blogapp.pubsystems.publishers.site.drupal" #$NON-NLS-1$
    ALL_SITES.append(DRUPAL)
    #    legacy api=xmlrpc.mt  acc=Movable Type, res=drupal

    COMMUNITY_SERVER = u"zoundry.blogapp.pubsystems.publishers.site.communityserver" #$NON-NLS-1$
    ALL_SITES.append(COMMUNITY_SERVER)
    #    legacy  api=xmlrpc.metaweblog , acc=MetaWeblog, res=communityserver

    ROLLER = u"zoundry.blogapp.pubsystems.publishers.site.roller" #$NON-NLS-1$
    ALL_SITES.append(ROLLER)
    #    legacy api=xmlrpc.metaweblog  acc=MetaWeblog, res=roller

    SQUARESPACE = u"zoundry.blogapp.pubsystems.publishers.site.squarespace"#$NON-NLS-1$
    ALL_SITES.append(SQUARESPACE)
    #    legacy api=xmlrpc.metaweblog  acc=MetaWeblog, res=squarespace

    DASBLOG = u"zoundry.blogapp.pubsystems.publishers.site.dasblog" #$NON-NLS-1$
    ALL_SITES.append(DASBLOG)
    #    legacy api=xmlrpc.metaweblog  acc=MetaWeblog, res=dasblog

    TEXTPATTERN = u"zoundry.blogapp.pubsystems.publishers.site.textpattern" #$NON-NLS-1$
    ALL_SITES.append(TEXTPATTERN)
    #    legacy api=xmlrpc.mt  acc=Movable Type, res=textpattern

    XOOPS = u"zoundry.blogapp.pubsystems.publishers.site.xoops" #$NON-NLS-1$
    ALL_SITES.append(XOOPS)
    #    legacy api=xmlrpc.metaweblog  acc=MetaWeblog, res=xoops

    XARAYA = u"zoundry.blogapp.pubsystems.publishers.site.xaraya" #$NON-NLS-1$
    ALL_SITES.append(XARAYA)
    #    legacy api=xmlrpc.metaweblog  acc=MetaWeblog, res=xaraya

    CUSTOM_ATOM10 = u"zoundry.blogapp.pubsystems.publishers.site.atom10" #$NON-NLS-1$
    ALL_SITES.append(CUSTOM_ATOM10)
    #    legacy api=Atom10, acc=Custom Atom 1.0

    CUSTOM_ATOM03 = u"zoundry.blogapp.pubsystems.publishers.site.atom03" #$NON-NLS-1$
    ALL_SITES.append(CUSTOM_ATOM03)
    #    legacy api=Atom, acc=Custom Atom

    CUSTOM_MT = u"zoundry.blogapp.pubsystems.publishers.site.movabletype" #$NON-NLS-1$
    ALL_SITES.append(CUSTOM_MT)
    #    legacy api=xmlrpc.mt, acc=Movable Type

    CUSTOM_METAWEBLOG = u"zoundry.blogapp.pubsystems.publishers.site.metaweblog" #$NON-NLS-1$
    ALL_SITES.append(CUSTOM_METAWEBLOG)
    #    legacy api=xmlrpc.metaweblog  acc=MetaWeblog, res=

    CUSTOM_LJ = u"zoundry.blogapp.pubsystems.publishers.site.livejournal" #$NON-NLS-1$
    ALL_SITES.append(CUSTOM_LJ)
    #   legacy api=xmlrpc.livejournal  acc=LiveJournal

    CUSTOM_BLOGGERV1 = u"zoundry.blogapp.pubsystems.publishers.site.bloggerv1" #$NON-NLS-1$
    ALL_SITES.append(CUSTOM_BLOGGERV1)
    #    legacy  api=xmlrpc.bloggerv1 acc=Blogger v1 API

    CUSTOM_BLOGGERV2 = u"zoundry.blogapp.pubsystems.publishers.site.bloggerv2" #$NON-NLS-1$
    ALL_SITES.append(CUSTOM_BLOGGERV2)
    #    legacy  api=xmlrpc.bloggerv2  acc=Blogger v2 API
