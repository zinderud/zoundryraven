#
# This module contains a variety of constants.
#
from zoundry.appframework.constants import IZAppActionIDs
from zoundry.appframework.constants import IZAppExtensionPoints
from zoundry.appframework.constants import IZAppMenuIds
from zoundry.appframework.constants import IZAppNamespaces
from zoundry.appframework.constants import IZAppServiceIDs
from zoundry.appframework.constants import IZAppUserPrefsDefaults
from zoundry.appframework.constants import IZAppUserPrefsKeys

PASSWORD_ENCRYPTION_KEY = u"n7av45n7ybalbe7nb68yba67ngab9800" #$NON-NLS-1$


# ------------------------------------------------------------------------------
# Interface holding all of the blog application namespaces.
# ------------------------------------------------------------------------------
class IZBlogAppNamespaces(IZAppNamespaces):

    RAVEN_ACCOUNT_NAMESPACE = u"http://www.zoundry.com/schemas/2006/05/zaccount.rng" #$NON-NLS-1$
    RAVEN_DOCUMENT_NAMESPACE = u"http://www.zoundry.com/schemas/2006/05/zdocument.rng" #$NON-NLS-1$
    ATOM_PUBLISHER_NAMESPACE = u"urn:zoundry:atom" #$NON-NLS-1$ # FIXME PJ use pub layer IZBlogPubAttrNamespaces.ATOM_ATTR_NAMESPACE instead of string
    CMS_PUBLISHER_NAMESPACE = u"urn:zoundry:cms" #$NON-NLS-1$ FIXME PJ use pub layer IZBlogPubAttrNamespaces.CMS_ATTR_NAMESPACE instead of string

    # NS for Zoundry Blog Writer 1.x attributes (legacy data)
    ZBW_ACCOUNT_NAMESPACE = u"urn:zoundry:zbw" #$NON-NLS-1$
    # NS for WLW import attributes (legacy data)
    WLW_ACCOUNT_NAMESPACE = u"urn:zoundry:wlw:2008:01" #$NON-NLS-1$
    

    RAVEN_USAGE_STATS_NAMESPACE = u"http://www.zoundry.com/schemas/2007/05/zusage.rng" #$NON-NLS-1$

# end IZBlogAppNamespaces


# ------------------------------------------------------------------------------
# Interface holding all of the blog application service IDs.
# ------------------------------------------------------------------------------
class IZBlogAppServiceIDs(IZAppServiceIDs):

    ACCOUNT_STORE_SERVICE_ID = u"zoundry.blogapp.service.accountstore" #$NON-NLS-1$
    DATA_STORE_SERVICE_ID = u"zoundry.blogapp.service.datastore" #$NON-NLS-1$
    DOCUMENT_INDEX_SERVICE_ID = u"zoundry.blogapp.service.docindex" #$NON-NLS-1$
    MEDIA_STORAGE_SERVICE_ID = u"zoundry.blogapp.service.mediastorage" #$NON-NLS-1$
    PUBLISHING_SERVICE_ID = u"zoundry.blogapp.service.publishing" #$NON-NLS-1$
    SINGLETON_SERVICE_ID = u"zoundry.blogapp.service.singleton" #$NON-NLS-1$
    TEMPLATE_SERVICE_ID = u"zoundry.blogapp.service.template" #$NON-NLS-1$
    CRASH_RECOVERY_SERVICE_ID = u"zoundry.blogapp.service.crash-recovery" #$NON-NLS-1$
    LINKS_SERVICE_ID = u"zoundry.blogapp.service.links" #$NON-NLS-1$
    PRODUCTS_SERVICE_ID = u"zoundry.blogapp.service.products" #$NON-NLS-1$

# end IZBlogAppServiceIDs


# ------------------------------------------------------------------------------
# Interface holding all of the keys used to reference user preferences.
# ------------------------------------------------------------------------------
class IZBlogAppUserPrefsKeys(IZAppUserPrefsKeys):

    AUTO_CONVERT_AFFILIATE_LINKS = u"zoundry.raven.affiliate-links.auto-convert" #$NON-NLS-1$

    # Preferences used by the application window.
    APPWIN_DEFAULT_PERSPECTIVE = u"zoundry.raven.ui.appwin.default.perspective" #$NON-NLS-1$
    APPWIN_WIDTH = u"zoundry.raven.ui.appwin.width" #$NON-NLS-1$
    APPWIN_HEIGHT = u"zoundry.raven.ui.appwin.height" #$NON-NLS-1$
    APPWIN_X = u"zoundry.raven.ui.appwin.x" #$NON-NLS-1$
    APPWIN_Y = u"zoundry.raven.ui.appwin.y" #$NON-NLS-1$
    APPWIN_MAXIMIZED = u"zoundry.raven.ui.appwin.ismax" #$NON-NLS-1$

    # Editor
    EDITOR_FONT_NAME = u"zoundry.raven.ui.editor.font-name" #$NON-NLS-1$
    EDITOR_FONT_SIZE = u"zoundry.raven.ui.editor.font-size" #$NON-NLS-1$
    EDITOR_COPY_NONPORTABLE_FILES = u"zoundry.raven.ui.editor.copy-non-portable-files" #$NON-NLS-1$
    EDITOR_XHTML_VIEW_SASH_POS = u"zoundry.raven.ui.editor.xhtml.sash.pos" #$NON-NLS-1$
    EDITOR_TN_SIZE = u"zoundry.raven.ui.editor.thumbnail-size" #$NON-NLS-1$
    EDITOR_XHTML_SCHEMA = u"zoundry.raven.ui.editor.xhtml-schema" #$NON-NLS-1$

    SYSTRAY_ALWAYS_SHOW = u"zoundry.raven.ui.systray.always-show" #$NON-NLS-1$
    SYSTRAY_HIDE_WHEN_MINIMIZED = u"zoundry.raven.ui.systray.hide-when-minimized" #$NON-NLS-1$

    # Preferences used by the Posts View
    POSTS_VIEW_SASH_POS = u"zoundry.raven.ui.postsview.sash.pos" #$NON-NLS-1$
    # Preferences used by the Images View
    IMAGES_VIEW_SASH_POS = u"zoundry.raven.ui.imagesview.sash.pos" #$NON-NLS-1$
    # Preferences used by the Links View
    LINKS_VIEW_SASH_POS = u"zoundry.raven.ui.linksview.sash.pos" #$NON-NLS-1$
    # Preferences used by the Links View
    TAGS_VIEW_SASH_POS = u"zoundry.raven.ui.tagsview.sash.pos" #$NON-NLS-1$

    # Preferences used by the Standard Perspective.
    STANDARD_PERSPECTIVE_LAYOUT = u"zoundry.raven.ui.perspectives.standard.window.layout" #$NON-NLS-1$

    # Preferences used by the Browse Perspective.
    BROWSE_PERSPECTIVE_LAYOUT = u"zoundry.raven.ui.perspectives.browse.window.layout" #$NON-NLS-1$

    # Preferences for the editor window
    EDITOR_WINDOW = u"zoundry.raven.blogapp.ui.editorwin" #$NON-NLS-1$
    EDITOR_WINDOW_TOOLBAR = u"zoundry.raven.blogapp.ui.editorwin.toolbar" #$NON-NLS-1$

    # Preferences for blog accounts
    BLOG_ACCOUNT_OVERRIDE_PUB_SETTINGS = u"zoundry.raven.blogapp.ui.accounts.blogaccount.override-pub-settings" #$NON-NLS-1$
    BLOG_ACCOUNT_OVERRIDE_PING_SITE = u"zoundry.raven.blogapp.ui.accounts.blogaccount.override-ping-sites-settings" #$NON-NLS-1$
    BLOG_ACCOUNT_OVERRIDE_TAG_SITE = u"zoundry.raven.blogapp.ui.accounts.blogaccount.override-tag-site-settings" #$NON-NLS-1$
    # Preferences for blogs
    BLOG_OVERRIDE_PUB_SETTINGS = u"zoundry.raven.blogapp.ui.accounts.blogaccount.blog.override-pub-settings" #$NON-NLS-1$
    BLOG_OVERRIDE_MEDIA_STORE = u"zoundry.raven.blogapp.ui.accounts.blogaccount.blog.override-media-storage" #$NON-NLS-1$
    BLOG_OVERRIDE_TEMPLATE = u"zoundry.raven.blogapp.ui.accounts.blogaccount.blog.override-template" #$NON-NLS-1$
    BLOG_OVERRIDE_PING_SITE_SETTINGS = u"zoundry.raven.blogapp.ui.accounts.blogaccount.blog.override-ping-sites-settings" #$NON-NLS-1$
    BLOG_OVERRIDE_TAG_SITE_SETTINGS = u"zoundry.raven.blogapp.ui.accounts.blogaccount.blog.override-tag-site-settings" #$NON-NLS-1$

    # Shared preferences (hierarchical):  Application->Blog Account->Blog
    SP_ADD_POWERED_BY = u"zoundry.raven.blogapp.ui.publishing.add-powered-by" #$NON-NLS-1$
    SP_REMOVE_NEWLINES = u"zoundry.raven.blogapp.ui.publishing.remove-newlines" #$NON-NLS-1$
    SP_UPLOAD_TNS_ONLY = u"zoundry.raven.blogapp.ui.publishing.upload-tns-only" #$NON-NLS-1$
    SP_FORCE_REUPLOAD = u"zoundry.raven.blogapp.ui.publishing.force-reupload" #$NON-NLS-1$
    SP_ADD_LIGHTBOX = u"zoundry.raven.blogapp.ui.publishing.add-lightbox" #$NON-NLS-1$
    SP_PING_SITES = u"zoundry.raven.blogapp.ui.publishing.ping-sites" #$NON-NLS-1$
    SP_TAG_SITES = u"zoundry.raven.blogapp.ui.publishing.tag-sites" #$NON-NLS-1$

    SYNCH_DIALOG = u"zoundry.raven.blogapp.ui.dialogs.synch" #$NON-NLS-1$
    IMAGE_DIALOG = u"zoundry.raven.blogapp.ui.dialogs.image" #$NON-NLS-1$
    LINK_DIALOG = u"zoundry.raven.blogapp.ui.dialogs.link" #$NON-NLS-1$

    FIND_REPLACE_DIALOG = u"zoundry.raven.blogapp.ui.dialogs.find-replace" #$NON-NLS-1$
    SPELLCHECK_DIALOG = u"zoundry.raven.blogapp.ui.dialogs.spellcheck" #$NON-NLS-1$

    TEMPLATE_WINDOW = u"zoundry.raven.blogapp.ui.windows.template" #$NON-NLS-1$
    ADD_TEMPLATE_FROM_BLOG_DIALOG = u"zoundry.raven.blogapp.ui.dialogs.template.add-from-blog" #$NON-NLS-1$

    TRANSLATION_WINDOW = u"zoundry.raven.blogapp.ui.windows.translation-manager" #$NON-NLS-1$

    TRANSLATION_DIALOG = u"zoundry.raven.blogapp.ui.dialogs.translation-editor" #$NON-NLS-1$
    
    NAVIGATOR_VIEW_SELECTION = u"zoundry.raven.ui.views.standard.navigator.tree.selection" #$NON-NLS-1$

    POST_PREVIEW_VIEW_USE_TEMPLATE = u"zoundry.raven.ui.views.standard.postPreview.use-template" #$NON-NLS-1$

    DND_THUMBNAIL_DIALOG = u"zoundry.raven.blogapp.ui.dialogs.dnd-thumbnail" #$NON-NLS-1$

# end IZBlogAppUserPrefsKeys


# ------------------------------------------------------------------------------
# Interface containing paths to some user properties.
# ------------------------------------------------------------------------------
class IZUserPropertiesPaths:

    FIND_REPLACE_DIALOG_FIND_LIST = u"/user-properties/user-preferences/zoundry/raven/blogapp/ui/dialogs/find-replace/history/find" #$NON-NLS-1$
    FIND_REPLACE_DIALOG_REPLACE_LIST = u"/user-properties/user-preferences/zoundry/raven/blogapp/ui/dialogs/find-replace/history/replace" #$NON-NLS-1$

# end IZUserPropertiesPaths


# ------------------------------------------------------------------------------
# Interface containing default values for user preferences.
# ------------------------------------------------------------------------------
class IZUserPrefsDefaults(IZAppUserPrefsDefaults):

    SYSTRAY_ALWAYS_SHOW = False
    SYSTRAY_HIDE_WHEN_MINIMIZED = False

# end IZUserPrefsDefaults


# ------------------------------------------------------------------------------
# Interface holding all of the blog application extension point type IDs.
# ------------------------------------------------------------------------------
class IZBlogAppExtensionPoints(IZAppExtensionPoints):

    ZEP_ZOUNDRY_PERSPECTIVE = u"zoundry.blogapp.ui.perspective" #$NON-NLS-1$
    ZEP_ZOUNDRY_MEDIASTORE_TYPE = u"zoundry.blogapp.mediastorage.type" #$NON-NLS-1$
    ZEP_ZOUNDRY_MEDIASTORE_SITE = u"zoundry.blogapp.mediastorage.site" #$NON-NLS-1$
    ZEP_ZOUNDRY_STANDARD_POST_DETAILS_PANEL = u"zoundry.blogapp.ui.views.standard.post-details-panel" #$NON-NLS-1$
    ZEP_ZOUNDRY_STANDARD_IMAGE_DETAILS_PANEL = u"zoundry.blogapp.ui.views.standard.image-details-panel" #$NON-NLS-1$
    ZEP_ZOUNDRY_STANDARD_LINK_DETAILS_PANEL = u"zoundry.blogapp.ui.views.standard.link-details-panel" #$NON-NLS-1$
    ZEP_ZOUNDRY_STANDARD_TAG_DETAILS_PANEL = u"zoundry.blogapp.ui.views.standard.tag-details-panel" #$NON-NLS-1$
    ZEP_ZOUNDRY_PUBLISHER_TYPE = u"zoundry.blogapp.pubsystems.publisher.type" #$NON-NLS-1$ #FIXME (PJ): document this ext point.
    ZEP_ZOUNDRY_PUBLISHER_SITE = u"zoundry.blogapp.pubsystems.publisher.site" #$NON-NLS-1$ #FIXME (PJ): document this ext point.
    ZEP_ZOUNDRY_WEBLOGPING_SITE = u"zoundry.blogapp.pubsystems.weblogping.site" #$NON-NLS-1$ #FIXME (PJ): document this ext point.
    ZEP_ZOUNDRY_LINK_PROVIDER_TYPE = u"zoundry.blogapp.links.provider.type" #$NON-NLS-1$ #FIXME (PJ): document this ext point.
    ZEP_ZOUNDRY_SIMPLELINKS_PROVIDER_ENTRIES = u"zoundry.blogapp.links.simplelinkprovider.entries" #$NON-NLS-1$ #FIXME (PJ): document this ext point.

# end IZBlogAppExtensionPoints


# ------------------------------------------------------------------------------
# Interface holding all of the blog application menu IDs (the ID used when
# a plugin contributes a menu item).
# ------------------------------------------------------------------------------
class IZBlogAppMenuIds(IZAppMenuIds):

    ZID_MAINMENU = u"zoundry.blogapp.ui.core.menu.mainmenubar" #$NON-NLS-1$
    ZID_MAINMENU_FILE = u"zoundry.blogapp.ui.core.menugroup.file" #$NON-NLS-1$
    ZID_MAINMENU_FILE_NEW = u"zoundry.blogapp.ui.core.menugroup.file.new" #$NON-NLS-1$
    ZID_MAINMENU_VIEW = u"zoundry.blogapp.ui.core.menugroup.view" #$NON-NLS-1$
    ZID_MAINMENU_VIEW_PERSPECTIVE = u"zoundry.blogapp.ui.core.menugroup.view.perspective" #$NON-NLS-1$
    ZID_MAINMENU_TOOLS = u"zoundry.blogapp.ui.core.menugroup.tools" #$NON-NLS-1$
    ZID_MAINMENU_HELP = u"zoundry.blogapp.ui.core.menugroup.help" #$NON-NLS-1$

    ZID_TRAY_MENU = u"zoundry.blogapp.ui.tray.menu" #$NON-NLS-1$

    ZID_INSERT_LINK_MENU = u"zoundry.blogapp.ui.editor.menu.insert-link" #$NON-NLS-1$
    ZID_INSERT_IMAGE_MENU = u"zoundry.blogapp.ui.editor.menu.insert-image" #$NON-NLS-1$
    ZID_INSERT_TABLE_MENU = u"zoundry.blogapp.ui.editor.menu.insert-table" #$NON-NLS-1$
    ZID_IMAGE_ALIGN_MENU = u"zoundry.blogapp.ui.editor.menu.image-align" #$NON-NLS-1$
    ZID_IMAGE_BORDER_MENU = u"zoundry.blogapp.ui.editor.menu.image-border" #$NON-NLS-1$
    ZID_IMAGE_THUMBNAIL_MENU = u"zoundry.blogapp.ui.editor.menu.image-thumbnail" #$NON-NLS-1$
    ZID_HTML_FORMAT_MENU = u"zoundry.blogapp.ui.editor.menu.html-fortmat-tags" #$NON-NLS-1$

    ZID_BLOG_ACCOUNT_MENU = u"zoundry.blogapp.ui.core.menu.blog-account" #$NON-NLS-1$
    ZID_BLOG_MENU = u"zoundry.blogapp.ui.core.menu.blog" #$NON-NLS-1$
    ZID_BLOG_POST_MENU = u"zoundry.blogapp.ui.core.menu.blog-post" #$NON-NLS-1$

    ZID_BLOG_EDITOR_DESIGNER_CONTEXT_MENU = u"zoundry.blogapp.ui.editors.blog.designer.contextmenu" #$NON-NLS-1$
    ZID_BLOG_EDITOR_DESIGNER_CONTEXT_MENU_LINKS = u"zoundry.blogapp.ui.editors.blog.designer.contextmenu.groupmenu.links" #$NON-NLS-1$
    ZID_BLOG_EDITOR_DESIGNER_CONTEXT_MENU_IMAGES = u"zoundry.blogapp.ui.editors.blog.designer.contextmenu.groupmenu.images" #$NON-NLS-1$

# end IZBlogAppToolBarIds


# ------------------------------------------------------------------------------
# Interface holding all of the blog application toolbar IDs (the ID used when
# a plugin contributes a toolbar item).
# ------------------------------------------------------------------------------
class IZBlogAppToolBarIds:

    ZID_STANDARD_PERSPECTIVE_TOOLBAR = u"zoundry.blogapp.ui.perspective.standard.toolbar" #$NON-NLS-1$
    ZID_BLOG_EDITOR_TOOLBAR = u"zoundry.blogapp.ui.editors.blog.toolbar" #$NON-NLS-1$
    ZID_BLOG_EDITOR_DESIGNER_TOOLBAR = u"zoundry.blogapp.ui.editors.blog.designer.toolbar" #$NON-NLS-1$
    ZID_BLOG_EDITOR_DESIGNER_CONTEXT_TOOLBAR = u"zoundry.blogapp.ui.editors.blog.designer.contexttoolbar" #$NON-NLS-1$
    ZID_TEMPLATE_MANAGER_TOOLBAR = u"zoundry.blogapp.ui.windows.template.toolbar" #$NON-NLS-1$

# end IZBlogAppToolBarIds


# ------------------------------------------------------------------------------
# Interface holding all of the blog application accelerator IDs (the ID used
# when a plugin contributes an accelerator).
# ------------------------------------------------------------------------------
class IZBlogAppAcceleratorIds:

    ZID_MAIN_WINDOW_ACCEL = u"zoundry.blogapp.ui.accelerators.main" #$NON-NLS-1$
    ZID_BLOG_POST_EDITOR_ACCEL = u"zoundry.blogapp.ui.accelerators.editor.blog-post" #$NON-NLS-1$
    ZID_BLOG_POST_EDITOR_CONTENT_ACCEL = u"zoundry.blogapp.ui.accelerators.editor.blog-post.content" #$NON-NLS-1$
    ZID_BLOG_POST_LIST_ACCEL = u"zoundry.blogapp.ui.accelerators.blog-post-list" #$NON-NLS-1$

# end IZBlogAppAcceleratorIds


# ------------------------------------------------------------------------------
# Built in action IDs.
# ------------------------------------------------------------------------------
class IZBlogAppActionIDs(IZAppActionIDs):

    EXIT_ACTION = u"zoundry.blogapp.ui.core.actions.exit" #$NON-NLS-1$
    ACCOUNT_MANAGER_ACTION = u"zoundry.blogapp.ui.core.actions.account-manager" #$NON-NLS-1$
    SETTINGS_ACTION = u"zoundry.blogapp.ui.core.actions.settings" #$NON-NLS-1$
    BACKGROUND_TASKS_ACTION = u"zoundry.blogapp.ui.core.actions.bgtasks" #$NON-NLS-1$
    MANAGE_TEMPLATES_ACTION = u"zoundry.blogapp.ui.core.actions.template-manager" #$NON-NLS-1$
    MANAGE_TRANSLATIONS_ACTION = u"zoundry.blogapp.ui.core.actions.translation-manager" #$NON-NLS-1$
    MEDIA_STORES_ACTION = u"zoundry.blogapp.ui.core.actions.media-storages" #$NON-NLS-1$
    ABOUT_ACTION = u"zoundry.blogapp.ui.core.actions.about" #$NON-NLS-1$
    FEEDBACK_ACTION = u"zoundry.blogapp.ui.core.actions.feedback" #$NON-NLS-1$
    CHECK_FOR_UPDATES_ACTION = u"zoundry.blogapp.ui.core.actions.check4updates" #$NON-NLS-1$
    GET_SUPPORT_ACTION = u"zoundry.blogapp.ui.core.actions.get-support" #$NON-NLS-1$
    NEW_MEDIA_STORAGE_ACTION = u"zoundry.blogapp.ui.core.actions.new-store" #$NON-NLS-1$
    NEW_BLOG_ACCOUNT_ACTION = u"zoundry.blogapp.ui.core.actions.new-blog-account" #$NON-NLS-1$
    NEW_BLOG_POST_ACTION = u"zoundry.blogapp.ui.core.actions.new-blog-post" #$NON-NLS-1$

    EDIT_MEDIA_STORE_ACTION = u"zoundry.blogapp.ui.media-storage.actions.edit" #$NON-NLS-1$
    DELETE_MEDIA_STORE_ACTION = u"zoundry.blogapp.ui.media-storage.actions.delete" #$NON-NLS-1$

    OPEN_BLOG_POST_ACTION = u"zoundry.blogapp.ui.blog-post.actions.open" #$NON-NLS-1$
    OPEN_BLOG_POST_AS_UNPUBLISHED_ACTION = u"zoundry.blogapp.ui.blog-post.actions.open-as-unpublished" #$NON-NLS-1$
    VIEW_BLOG_POST_ACTION = u"zoundry.blogapp.ui.blog-post.actions.view" #$NON-NLS-1$
    COPY_BLOG_POST_URL_ACTION = u"zoundry.blogapp.ui.blog-post.actions.copy-blog-post-url" #$NON-NLS-1$
    DELETE_BLOG_POST_ACTION = u"zoundry.blogapp.ui.blog-post.actions.delete" #$NON-NLS-1$

    MINIMIZE_ACTION = u"zoundry.blogapp.ui.tray.actions.minimize" #$NON-NLS-1$
    RESTORE_ACTION = u"zoundry.blogapp.ui.tray.actions.restore" #$NON-NLS-1$
    EXIT_FROM_TRAY_ACTION = u"zoundry.blogapp.ui.tray.actions.exit" #$NON-NLS-1$

    CONFIGURE_BLOG_ACTION = u"zoundry.blogapp.ui.blog.actions.configure" #$NON-NLS-1$
    BLOG_NEW_BLOG_POST_ACTION = u"zoundry.blogapp.ui.blog.actions.new-post" #$NON-NLS-1$
    VIEW_BLOG_ACTION = u"zoundry.blogapp.ui.blog.actions.view" #$NON-NLS-1$
    DOWNLOAD_BLOG_TEMPLATE_ACTION = u"zoundry.blogapp.ui.blog.actions.download-template" #$NON-NLS-1$

    ACCOUNT_SETTINGS_ACTION = u"zoundry.blogapp.ui.account.actions.settings" #$NON-NLS-1$
    ACCOUNT_SYNCHRONIZE_ACTION = u"zoundry.blogapp.ui.core.actions.synchronize" #$NON-NLS-1$

# end IZBlogAppActionIDs
