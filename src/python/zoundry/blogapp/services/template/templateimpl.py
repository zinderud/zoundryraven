from zoundry.base.util.fileutil import resolveRelativePath
from zoundry.blogapp.services.template.template import IZTemplate

# ------------------------------------------------------------------------------
# An implementation of an IZTemplate.
# ------------------------------------------------------------------------------
class ZTemplate(IZTemplate):

    def __init__(self, rootDir, id):
        self.rootDir = rootDir
        self.id = id
        self.name = None
        self.source = None
        self.rootFileName = None
        self.allFileName = None
        self.titleAndBodyFileName = None
        self.bodyOnlyFileName = None
        self.creationTime = None
        self.lastModifiedTime = None
    # end __init__()

    def getId(self):
        return self.id
    # end getId()

    def getName(self):
        return self.name
    # end getName()

    def setName(self, name):
        self.name = name
    # end setName()

    def getSource(self):
        return self.source
    # end getSource()

    def setSource(self, source):
        self.source = source
    # end setSource()

    def getTemplateDirectory(self):
        return self.rootDir
    # end getTemplateDirectory()

    def getRootFileName(self):
        return self.rootFileName
    # end getRootFileName()

    def setRootFileName(self, fileName):
        self.rootFileName = fileName
    # end setRootFileName()

    def getResolvedRootFile(self):
        return resolveRelativePath(self.getTemplateDirectory(), self.getRootFileName())
    # end getResolvedRootFile()

    def getAllFileName(self):
        return self.allFileName
    # end getAllFileName()

    def setAllFileName(self, fileName):
        self.allFileName = fileName
    # end setAllFileName()

    def getTitleAndBodyFileName(self):
        return self.titleAndBodyFileName
    # end getTitleAndBodyFileName()

    def setTitleAndBodyFileName(self, fileName):
        self.titleAndBodyFileName = fileName
    # end setTitleAndBodyFileName()

    def getBodyOnlyFileName(self):
        return self.bodyOnlyFileName
    # end getBodyOnlyFileName()

    def setBodyOnlyFileName(self, fileName):
        self.bodyOnlyFileName = fileName
    # end setBodyOnlyFileName()

    def getCreationTime(self):
        return self.creationTime
    # end getCreationTime()

    def setCreationTime(self, creationTime):
        self.creationTime = creationTime
    # end setCreationTime()

    def getLastModifiedTime(self):
        return self.lastModifiedTime
    # end getLastModifiedTime()

    def setLastModifiedTime(self, lastModifiedTime):
        self.lastModifiedTime = lastModifiedTime
    # end setLastModifiedTime()

# end ZTemplate
