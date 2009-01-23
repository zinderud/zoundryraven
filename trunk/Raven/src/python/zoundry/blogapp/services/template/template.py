
# ------------------------------------------------------------------------------
# Template constants
# ------------------------------------------------------------------------------
class IZTemplateConstants:
    TEMPLATE_BASE_TOKEN = u"__RAVEN_TEMPLATE_DIR__" #$NON-NLS-1$
# end IZTemplateConstants


# ------------------------------------------------------------------------------
# Template interface.
# ------------------------------------------------------------------------------
class IZTemplate:

    def getId(self):
        u"""getId() -> id
        Returns the template id.""" #$NON-NLS-1$
    # end getId()

    def getName(self):
        u"""getName() -> string
        Returns the name of the template.""" #$NON-NLS-1$
    # end getName()

    def getSource(self):
        u"""getSource() -> string
        Returns the source of the template (how it was
        added - e.g. from a blog, from a URL, etc...""" #$NON-NLS-1$
    # end getSource()

    def getTemplateDirectory(self):
        u"""getTemplateDirectory() -> path
        Returns the root directory for the template.""" #$NON-NLS-1$
    # end getTemplateDirectory()

    def getRootFileName(self):
        u"""getRootFileName() -> string
        Returns the name of the template's root file.""" #$NON-NLS-1$
    # end getRootFileName()

    def setRootFileName(self, fileName):
        u"""setRootFileName(string) -> None
        Sets the template's root filename.""" #$NON-NLS-1$
    # end setRootFileName()

    def getResolvedRootFile(self):
        u"""getResolvedRootFile() -> string
        Returns the full absolute path to the root file.""" #$NON-NLS-1$
    # end getResolvedRootFile()

    def getAllFileName(self):
        u"""getAllFileName() -> string
        Returns the name of the file containing the trimmed-down
        version of the template.  This trimmed down version has
        placeholders for 'title' and 'body', but everything else
        in the content is unchanged.  This is suitable for the
        'preview' tab in the editor.""" #$NON-NLS-1$
    # end getAllFileName()

    def setAllFileName(self, fileName):
        u"""setAllFileName(string) -> None
        Sets the file name of the "all" trimmed-down xhtml
        template file.""" #$NON-NLS-1$
    # end setAllFileName()

    def getTitleAndBodyFileName(self):
        u"""getTitleAndBodyFileName() -> string
        Gets the name of the file containing the trimmed-down
        version of the template that has the 'title' and 'body'
        placeholders and everything else removed.  Suitable
        for display as a preview in the Standard Perspective,
        for example.""" #$NON-NLS-1$
    # end getTitleAndBodyFileName()

    def setTitleAndBodyFileName(self, fileName):
        u"""setTitleAndBodyFileName(string) -> None
        Sets the file name of the "title + body" trimmed-down xhtml
        template file.""" #$NON-NLS-1$
    # end setTitleAndBodyFileName()

    def getBodyOnlyFileName(self):
        u"""getBodyOnlyFileName() -> string
        Gets the name of the file containing the trimmed-down
        version of the template that has the 'body' placeholder
        only, with everything else removed.  Suitable for
        use when editing.""" #$NON-NLS-1$
    # end getBodyOnlyFileName()

    def setBodyOnlyFileName(self, fileName):
        u"""setBodyOnlyFileName(string) -> None
        Sets the file name of the "body only" trimmed-down xhtml
        template file.""" #$NON-NLS-1$
    # end setBodyOnlyFileName()

    def getCreationTime(self):
        u"""getCreationTime() -> ZSchemaDateTime
        Returns the time the template was created.""" #$NON-NLS-1$
    # end getCreationTime()

    def getLastModifiedTime(self):
        u"""getLastModifiedTime() -> ZSchemaDateTime
        Returns the last modified time of the template.""" #$NON-NLS-1$
    # end getLastModifiedTime()

# end IZTemplate
