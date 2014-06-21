from zoundry.appframework.ui.widgets.controls.advanced.htmleditcontrol import IZXHTMLEditControl

# ------------------------------------------------------------------------------
# Interface that all blog edit controls must implement.  An edit control is a
# control that allows the user to edit the content of a IZBlogPostDocument.
# Examples of blog edit controls:  blog post content wysiwyg editor, blog post
# content xhtml editor, etc.
# ------------------------------------------------------------------------------
class IZBlogPostEditControl(IZXHTMLEditControl):

    ZCAPABILITY_EXTENDED_ENTRY_MARKER = u"zoundry.xhtmleditcontrol.capability.extended-entry-marker" #$NON-NLS-1$

    def canRemoveExtendedEntryMarker(self):
        u"""canRemoveExtendedEntryMarker() -> bool
        Returns true if the extended entry marker can be removed
        """ #$NON-NLS-1$
    # end canRemoveExtendedEntryMarker()

    def removeExtendedEntryMarker(self):
        u"""removeExtendedEntryMarker() -> void
        Removes the extended entry marker.
        """ #$NON-NLS-1$
    # removeExtendedEntryMarker()

    def insertExtendedEntryMarker(self):
        u"""insertExtendedEntryMarker() -> void
        Inserts the extended entry marker.
        """ #$NON-NLS-1$
    # insertExtendedEntryMarker()

# end IZBlogPostEditControl

