#
# This module contains a variety of constants.
#

# -------------------------------------------------------------------------------------------
# Interface holding all of the application namespaces.
# -------------------------------------------------------------------------------------------
class IZAppNamespaces:

    RAVEN_PLUGIN_NAMESPACE = u"http://www.zoundry.com/schemas/2006/03/zplugin.rng" #$NON-NLS-1$
    RAVEN_TASK_NAMESPACE = u"http://www.zoundry.com/schemas/2006/05/ztask.rng" #$NON-NLS-1$
    RAVEN_DICTIONARIES_NAMESPACE = u"http://www.zoundry.com/schemas/2006/10/zdictionaries.rng" #$NON-NLS-1$
    RAVEN_WORD_LIST_NAMESPACE = u"http://www.zoundry.com/schemas/2006/10/zwordlist.rng" #$NON-NLS-1$
    RAVEN_SPELLCHECKER_NAMESPACE = u"http://www.zoundry.com/schemas/2006/10/zspellchecker.rng" #$NON-NLS-1$

    RAVEN_COUNTRY_CODES_NAMESPACE_2006_11 = u"http://www.zoundry.com/schemas/2006/11/zcountrycodes.rng" #$NON-NLS-1$
    RAVEN_LANGUAGE_CODES_NAMESPACE_2006_11 = u"http://www.zoundry.com/schemas/2006/11/zlanguagecodes.rng" #$NON-NLS-1$
    RAVEN_TASK_NAMESPACE_2006_05 = u"http://www.zoundry.com/schemas/2006/05/ztask.rng" #$NON-NLS-1$
    RAVEN_MIMETYPES_NAMESPACE = u"http://www.zoundry.com/schemas/2007/03/zmimetypes.rng" #$NON-NLS-1$
    RAVEN_RESOURCE_STORE_ENTRY_NAMESPACE = u"http://www.zoundry.com/schemas/2008/04/zresourceentry.rng" #$NON-NLS-1$
# end IZAppNamespaces


# -------------------------------------------------------------------------------------------
# Interface holding all of the application service IDs.
# -------------------------------------------------------------------------------------------
class IZAppServiceIDs:

    LOGGER_SERVICE_ID = u"zoundry.appframework.service.logger" #$NON-NLS-1$
    I18N_SERVICE_ID = u"zoundry.appframework.service.i18nservice" #$NON-NLS-1$
    BACKGROUND_TASK_SERVICE_ID = u"zoundry.appframework.service.backgroundtask" #$NON-NLS-1$
    URL_FETCH_SERVICE_ID = u"zoundry.appframework.service.urlfetch" #$NON-NLS-1$
    SPELLCHECK_SERVICE_ID = u"zoundry.appframework.service.spellchecker" #$NON-NLS-1$
    IMAGING_SERVICE_ID = u"zoundry.appframework.service.imaging" #$NON-NLS-1$
    DND_SERVICE_ID = u"zoundry.appframework.service.dnd" #$NON-NLS-1$
    MIMETYPE_SERVICE_ID = u"zoundry.appframework.service.mimetypes" #$NON-NLS-1$
    FEEDBACK_SERVICE_ID = u"zoundry.appframework.service.feedback" #$NON-NLS-1$
    RESOURCE_STORE_SERVICE_ID = u"zoundry.appframework.service.resourcestore" #$NON-NLS-1$
    XHTML_VALIDATION_SERVICE_ID = u"zoundry.appframework.service.xhtmlvalidationservice" #$NON-NLS-1$
    AUTO_UPDATE_SERVICE_ID = u"zoundry.appframework.service.auto-update" #$NON-NLS-1$

# end IZAppServiceIDs


# -------------------------------------------------------------------------------------------
# Interface holding all of the keys used to reference user preferences.
# -------------------------------------------------------------------------------------------
class IZAppUserPrefsKeys:

    GUID = u"zoundry.raven.appframework.profile.guid" #$NON-NLS-1$
    ZOUNDRY_ID = u"zoundry.raven.appframework.zoundrysvc.zoundry-id" #$NON-NLS-1$

    LOCALE = u"zoundry.raven.appframework.i18n.locale" #$NON-NLS-1$
    TIMEZONE = u"zoundry.raven.appframework.tzservice.timezone" #$NON-NLS-1$

    BGTASK_WINDOW = u"zoundry.raven.appframework.ui.windows.bgtask" #$NON-NLS-1$

    SPELLCHECKER_ENABLED = u"zoundry.raven.appframework.spellcheck.enabled" #$NON-NLS-1$
    SPELLCHECKER_LANGUAGE = u"zoundry.raven.appframework.spellcheck.language" #$NON-NLS-1$

    MEDIA_STORE_MANAGER_DIALOG = u"zoundry.raven.appframework.ui.dialogs.mediastorageman" #$NON-NLS-1$

    USERPREFS_DIALOG = u"zoundry.raven.appframework.ui.dialogs.userprefs" #$NON-NLS-1$

    ACCOUNT_MANAGER_DIALOG = u"zoundry.raven.appframework.ui.dialogs.accountman" #$NON-NLS-1$

    ERROR_DIALOG = u"zoundry.raven.appframework.ui.dialogs.error" #$NON-NLS-1$

    FEEDBACK_DIALOG = u"zoundry.raven.appframework.ui.dialogs.feedback" #$NON-NLS-1$

    BLOGPUB_CONFIG_POPUP = u"zoundry.blogapp.ui.editors.blogeditorctrls.blogconfig.popup" #$NON-NLS-1$

    PROXY_ENABLE = u"zoundry.raven.appframework.proxy.enable" #$NON-NLS-1$
    PROXY_HOST = u"zoundry.raven.appframework.proxy.host" #$NON-NLS-1$
    PROXY_PORT = u"zoundry.raven.appframework.proxy.port" #$NON-NLS-1$
    PROXY_USERNAME = u"zoundry.raven.appframework.proxy.username" #$NON-NLS-1$
    PROXY_PASSWORD = u"zoundry.raven.appframework.proxy.password" #$NON-NLS-1$
# end IZAppUserPrefsKeys


# ------------------------------------------------------------------------------
# Interface containing default values for user preferences.
# ------------------------------------------------------------------------------
class IZAppUserPrefsDefaults:

    SPELLCHECKER_ENABLED = False

# end IZAppUserPrefsDefaults


# ------------------------------------------------------------------------------
# Interface holding all of the application extension point type IDs.
# ------------------------------------------------------------------------------
class IZAppExtensionPoints:

    ZEP_ZOUNDRY_EXTENSION = u"zoundry.extension" #$NON-NLS-1$

    ZEP_ZOUNDRY_SERVICE = u"zoundry.engine.service" #$NON-NLS-1$
    ZEP_ZOUNDRY_CORE_ACTION = u"zoundry.appframework.ui.core.action" #$NON-NLS-1$
    ZEP_PREFERENCE_PAGE = u"zoundry.appframework.ui.preferences.prefpage" #$NON-NLS-1$
    ZEP_STARTUP_ACTION = u"zoundry.appframework.startup-action" #$NON-NLS-1$
    ZEP_SHUTDOWN_ACTION = u"zoundry.appframework.shutdown-action" #$NON-NLS-1$
    ZEP_ZOUNDRY_CORE_MENU = u"zoundry.appframework.ui.core.menu" #$NON-NLS-1$
    ZEP_ZOUNDRY_CORE_MENUGROUP = u"zoundry.appframework.ui.core.menugroup" #$NON-NLS-1$
    ZEP_ZOUNDRY_CORE_MENUITEM = u"zoundry.appframework.ui.core.menuitem" #$NON-NLS-1$
    ZEP_ZOUNDRY_CORE_TOOLBARITEM = u"zoundry.appframework.ui.core.toolbaritem" #$NON-NLS-1$
    ZEP_ZOUNDRY_CORE_ACCELERATOR = u"zoundry.appframework.ui.core.accelerator" #$NON-NLS-1$
    ZEP_SPELLCHECK_HANDLER = u"zoundry.appframework.spellcheck.dictionary-handler" #$NON-NLS-1$
    ZEP_SPELLCHECK_PROVIDER = u"zoundry.appframework.spellcheck.provider" #$NON-NLS-1$
    ZEP_DRAG_AND_DROP_HANDLER = u"zoundry.appframework.dnd.handler" #$NON-NLS-1$

# end IZAppExtensionPoints


# ------------------------------------------------------------------------------
# Interface holding all of the names of the command line params.
# ------------------------------------------------------------------------------
class IZAppCommandLineParameterKeys:

    ZCMD_KEY_PROFILE = u"profile" #$NON-NLS-1$

# end IZAppCommandLineParameterKeys


# ------------------------------------------------------------------------------
# Interface holding all of the application menu IDs (the ID used when a plugin
# contributes a menu item).
# ------------------------------------------------------------------------------
class IZAppMenuIds:

    ZID_LINK_MENU = u"zoundry.appframework.ui.core.menu.link" #$NON-NLS-1$
    ZID_IMAGE_MENU = u"zoundry.appframework.ui.core.menu.image" #$NON-NLS-1$

# end IZBlogAppToolBarIds


# ------------------------------------------------------------------------------
# Built in action IDs.
# ------------------------------------------------------------------------------
class IZAppActionIDs:

    OPEN_LINK_ACTION = u"zoundry.blogapp.ui.link.actions.open" #$NON-NLS-1$
    COPY_LINK_LOCATION_ACTION = u"zoundry.blogapp.ui.link.actions.copy-location" #$NON-NLS-1$
    OPEN_IMAGE_ACTION = u"zoundry.blogapp.ui.image.actions.open" #$NON-NLS-1$
    COPY_IMAGE_LOCATION_ACTION = u"zoundry.blogapp.ui.image.actions.copy-location" #$NON-NLS-1$

# end IZBlogAppActionIDs
