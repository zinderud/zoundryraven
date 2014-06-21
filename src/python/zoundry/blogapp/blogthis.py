from zoundry.appframework.global_services import getCommandLineParameters


# ------------------------------------------------------------------------------
# Information relating to a Blog This command.
# ------------------------------------------------------------------------------
class IZBlogThisInformation:

    def getTitle(self):
        u"""getTitle() -> string""" #$NON-NLS-1$
    # end getTitle()

    def getUrl(self):
        u"""getUrl() -> string""" #$NON-NLS-1$
    # end getUrl()

    def getText(self):
        u"""getText() -> string""" #$NON-NLS-1$
    # end getText()

    def getFile(self):
        u"""getFile() -> string""" #$NON-NLS-1$
    # end getFile()

    def getAuthor(self):
        u"""getAuthor() -> string""" #$NON-NLS-1$
    # end getAuthor()

    def getFormat(self):
        u"""getFormat() -> string""" #$NON-NLS-1$
    # end getFormat()

    def isAutoDiscover(self):
        u"""isAutodiscover() -> boolean""" #$NON-NLS-1$
    # end isAutoDiscover()

    def isQuoted(self):
        u"""isQuoted() -> boolean""" #$NON-NLS-1$
    # end isQuoted()

# end IZBlogThisInformation


# ------------------------------------------------------------------------------
# Implementation of a 'blog this' data object.
# ------------------------------------------------------------------------------
class ZBlogThisInformation(IZBlogThisInformation):

    def __init__(self, title, url, text, file, author, format, isAutoDiscover, isQuoted):
        self.title = title
        self.url = url
        self.text = text
        self.file = file
        self.author = author
        self.format = format
        self.autoDiscover = isAutoDiscover
        self.quoted = isQuoted
    # end __init__()

    def getTitle(self):
        return self.title
    # end getTitle()

    def getUrl(self):
        return self.url
    # end getUrl()

    def getText(self):
        return self.text
    # end getText()

    def getFile(self):
        return self.file
    # end getFile()

    def getAuthor(self):
        return self.author
    # end getAuthor()

    def getFormat(self):
        return self.format
    # end getFormat()

    def isAutoDiscover(self):
        return self.autoDiscover
    # end isAutoDiscover()

    def isQuoted(self):
        return self.quoted
    # end isQuoted()

# end ZBlogThisInformation


def checkCmdLineForBlogThis():
    cmdLineParams = getCommandLineParameters()
    if u"blogthis" in cmdLineParams: #$NON-NLS-1$
        title = cmdLineParams[u"title"] #$NON-NLS-1$
        url = cmdLineParams[u"url"] #$NON-NLS-1$
        text = cmdLineParams[u"text"] #$NON-NLS-1$
        file = cmdLineParams[u"file"] #$NON-NLS-1$
        author = cmdLineParams[u"author"] #$NON-NLS-1$
        format = cmdLineParams[u"format"] #$NON-NLS-1$
        isAutoDiscover = cmdLineParams[u"autodiscover"] #$NON-NLS-1$
        isQuoted = cmdLineParams[u"quote"] #$NON-NLS-1$
        
        return ZBlogThisInformation(title, url, text, file, author, format, isAutoDiscover, isQuoted)
    return None
# end checkCmdLineForBlogThis()

