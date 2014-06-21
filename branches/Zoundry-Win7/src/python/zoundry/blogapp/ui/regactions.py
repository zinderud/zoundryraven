from zoundry.appframework.ui.actions.image.imageactions import ZCopyImageLocationAction
from zoundry.appframework.ui.actions.image.imageactions import ZOpenImageAction
from zoundry.appframework.ui.actions.link.linkactions import ZCopyLinkLocationAction
from zoundry.appframework.ui.actions.link.linkactions import ZOpenLinkAction
from zoundry.blogapp.constants import IZBlogAppActionIDs
from zoundry.blogapp.ui.actions.blog.blogactions import ZBlogConfigureMenuAction
from zoundry.blogapp.ui.actions.blog.blogactions import ZDownloadBlogTemplateAction
from zoundry.blogapp.ui.actions.blog.blogactions import ZNewPostInBlogMenuAction
from zoundry.blogapp.ui.actions.blog.blogactions import ZViewBlogAction
from zoundry.blogapp.ui.actions.blogpost.postactions import ZCopyBlogPostUrlAction
from zoundry.blogapp.ui.actions.blogpost.postactions import ZDeleteBlogPostAction
from zoundry.blogapp.ui.actions.blogpost.postactions import ZOpenAsUnpublishedBlogPostAction
from zoundry.blogapp.ui.actions.blogpost.postactions import ZOpenBlogPostAction
from zoundry.blogapp.ui.actions.blogpost.postactions import ZViewBlogPostAction
from zoundry.blogapp.ui.menus.account.accountmenu import ZAccountSettingsMenuAction
from zoundry.blogapp.ui.menus.account.accountmenu import ZAccountSynchronizeMenuAction
from zoundry.blogapp.ui.menus.main.feedback import ZFeedbackMenuAction
from zoundry.blogapp.ui.menus.main.file import ZExitMenuAction
from zoundry.blogapp.ui.menus.main.file_new import ZNewBlogPostMenuAction
from zoundry.blogapp.ui.menus.main.file_new import ZNewBlogSiteMenuAction
from zoundry.blogapp.ui.menus.main.file_new import ZNewMediaStorageMenuAction
from zoundry.blogapp.ui.menus.main.help import ZAboutMenuAction
from zoundry.blogapp.ui.menus.main.help import ZCheck4UpdatesMenuAction
from zoundry.blogapp.ui.menus.main.help import ZGetSupportMenuAction
from zoundry.blogapp.ui.menus.main.help import ZManageTranslationsMenuAction
from zoundry.blogapp.ui.menus.main.tools import ZAccountManagerMenuAction
from zoundry.blogapp.ui.menus.main.tools import ZBackgroundTasksMenuAction
from zoundry.blogapp.ui.menus.main.tools import ZManageTemplatesMenuAction
from zoundry.blogapp.ui.menus.main.tools import ZMediaStoragesMenuAction
from zoundry.blogapp.ui.menus.main.tools import ZSettingsMenuAction
from zoundry.blogapp.ui.menus.mediastoragemanager import ZDeleteMediaStorageMenuAction
from zoundry.blogapp.ui.menus.mediastoragemanager import ZEditMediaStorageMenuAction
from zoundry.blogapp.ui.trayactions import ZExitFromTrayAction
from zoundry.blogapp.ui.trayactions import ZMinimizeAction
from zoundry.blogapp.ui.trayactions import ZRestoreAction

# ------------------------------------------------------------------------------
# Convenience function for registering all built-in actions with the action
# registry.
# ------------------------------------------------------------------------------
def registerBlogAppActions(actionRegistry):

    # Main menu actions.
    actionRegistry.registerAction(IZBlogAppActionIDs.EXIT_ACTION, ZExitMenuAction())
    actionRegistry.registerAction(IZBlogAppActionIDs.ACCOUNT_MANAGER_ACTION, ZAccountManagerMenuAction())
    actionRegistry.registerAction(IZBlogAppActionIDs.SETTINGS_ACTION, ZSettingsMenuAction())
    actionRegistry.registerAction(IZBlogAppActionIDs.BACKGROUND_TASKS_ACTION, ZBackgroundTasksMenuAction())
    actionRegistry.registerAction(IZBlogAppActionIDs.MANAGE_TEMPLATES_ACTION, ZManageTemplatesMenuAction())
    actionRegistry.registerAction(IZBlogAppActionIDs.MANAGE_TRANSLATIONS_ACTION, ZManageTranslationsMenuAction())
    actionRegistry.registerAction(IZBlogAppActionIDs.MEDIA_STORES_ACTION, ZMediaStoragesMenuAction())
    actionRegistry.registerAction(IZBlogAppActionIDs.ABOUT_ACTION, ZAboutMenuAction())
    actionRegistry.registerAction(IZBlogAppActionIDs.FEEDBACK_ACTION, ZFeedbackMenuAction())
    actionRegistry.registerAction(IZBlogAppActionIDs.CHECK_FOR_UPDATES_ACTION, ZCheck4UpdatesMenuAction())
    actionRegistry.registerAction(IZBlogAppActionIDs.GET_SUPPORT_ACTION, ZGetSupportMenuAction())
    actionRegistry.registerAction(IZBlogAppActionIDs.NEW_MEDIA_STORAGE_ACTION, ZNewMediaStorageMenuAction())
    actionRegistry.registerAction(IZBlogAppActionIDs.NEW_BLOG_ACCOUNT_ACTION, ZNewBlogSiteMenuAction())
    actionRegistry.registerAction(IZBlogAppActionIDs.NEW_BLOG_POST_ACTION, ZNewBlogPostMenuAction())

    actionRegistry.registerAction(IZBlogAppActionIDs.EDIT_MEDIA_STORE_ACTION, ZEditMediaStorageMenuAction())
    actionRegistry.registerAction(IZBlogAppActionIDs.DELETE_MEDIA_STORE_ACTION, ZDeleteMediaStorageMenuAction())

    actionRegistry.registerAction(IZBlogAppActionIDs.OPEN_BLOG_POST_ACTION, ZOpenBlogPostAction())
    actionRegistry.registerAction(IZBlogAppActionIDs.OPEN_BLOG_POST_AS_UNPUBLISHED_ACTION, ZOpenAsUnpublishedBlogPostAction())
    actionRegistry.registerAction(IZBlogAppActionIDs.VIEW_BLOG_POST_ACTION, ZViewBlogPostAction())
    actionRegistry.registerAction(IZBlogAppActionIDs.DELETE_BLOG_POST_ACTION, ZDeleteBlogPostAction())
    actionRegistry.registerAction(IZBlogAppActionIDs.COPY_BLOG_POST_URL_ACTION, ZCopyBlogPostUrlAction())

    actionRegistry.registerAction(IZBlogAppActionIDs.MINIMIZE_ACTION, ZMinimizeAction())
    actionRegistry.registerAction(IZBlogAppActionIDs.RESTORE_ACTION, ZRestoreAction())
    actionRegistry.registerAction(IZBlogAppActionIDs.EXIT_FROM_TRAY_ACTION, ZExitFromTrayAction())

    actionRegistry.registerAction(IZBlogAppActionIDs.CONFIGURE_BLOG_ACTION, ZBlogConfigureMenuAction())
    actionRegistry.registerAction(IZBlogAppActionIDs.BLOG_NEW_BLOG_POST_ACTION, ZNewPostInBlogMenuAction())
    actionRegistry.registerAction(IZBlogAppActionIDs.VIEW_BLOG_ACTION, ZViewBlogAction())
    actionRegistry.registerAction(IZBlogAppActionIDs.DOWNLOAD_BLOG_TEMPLATE_ACTION, ZDownloadBlogTemplateAction())

    actionRegistry.registerAction(IZBlogAppActionIDs.ACCOUNT_SETTINGS_ACTION, ZAccountSettingsMenuAction())
    actionRegistry.registerAction(IZBlogAppActionIDs.ACCOUNT_SYNCHRONIZE_ACTION, ZAccountSynchronizeMenuAction())

    actionRegistry.registerAction(IZBlogAppActionIDs.OPEN_LINK_ACTION, ZOpenLinkAction())
    actionRegistry.registerAction(IZBlogAppActionIDs.COPY_LINK_LOCATION_ACTION, ZCopyLinkLocationAction())

    actionRegistry.registerAction(IZBlogAppActionIDs.OPEN_IMAGE_ACTION, ZOpenImageAction())
    actionRegistry.registerAction(IZBlogAppActionIDs.COPY_IMAGE_LOCATION_ACTION, ZCopyImageLocationAction())

# end registerBlogAppActions()
