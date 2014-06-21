from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.services.spellcheck.aspell.aspell import Speller
from zoundry.appframework.services.spellcheck.spellcheckimpl import IZSpellCheckDictionaryHandler
from zoundry.appframework.services.spellcheck.spellcheckimpl import IZSpellCheckProvider
from zoundry.base.util.fileutil import copyFiles
from zoundry.base.util.fileutil import deleteDirectory
from zoundry.base.util.text.textutil import isUnicodePath
from zoundry.base.util.ziputil import unpackZip
from zoundry.base.exceptions import ZException
from zoundry.appframework.util.osutilfactory import getOSUtil
import os

# ---------------------------------------------------------------------------------------
# A handler for when Aspell dictionaries are downloaded.  This handler simply unpacks
# the downloaded dictionary file into the spelling/aspell directory.
# ---------------------------------------------------------------------------------------
class ZAspellSpellCheckDictionaryHandler(IZSpellCheckDictionaryHandler):

    def processDictionaryFile(self, dictionaryFilePath):
        spellingDir = getApplicationModel().getUserProfile().getDirectory(u"spellcheck") #$NON-NLS-1$
        aspellDir = os.path.join(spellingDir, u"aspell") #$NON-NLS-1$
        unpackZip(dictionaryFilePath, aspellDir)
    # end processDictionaryFile()

    def initializeAspellDirectory(self):
        spellingDir = getApplicationModel().getUserProfile().getDirectory(u"spellcheck") #$NON-NLS-1$
        aspellDir = os.path.join(spellingDir, u"aspell") #$NON-NLS-1$
        keyFilePath = os.path.join(aspellDir, u"data", u"ASCII.dat") #$NON-NLS-2$ #$NON-NLS-1$
        if not os.path.isfile(keyFilePath):
            aspellBaseZip = getApplicationModel().getResourceRegistry().getResourcePath(u"spellcheck/aspell/aspell-base.zip") #$NON-NLS-1$
            unpackZip(aspellBaseZip, aspellDir)
    # end initializeAspellDirectory()

# end ZAspellSpellCheckDictionaryHandler


# ---------------------------------------------------------------------------------------
# An implementation of a spell check provider that uses the free GNU Aspell spelling
# library.  For more information on the GNU Aspell library, see:
#
#    http://aspell.sourceforge.net/
#
# ---------------------------------------------------------------------------------------
class ZAspellSpellCheckProvider(IZSpellCheckProvider):

    def __init__(self, dictionaryLanguage):
        self.dictionaryLanguage = dictionaryLanguage
        self.dictionaryEncoding = None
        self.isTempAspellDir = False
        self.spellingDir = getApplicationModel().getUserProfile().getDirectory(u"spellcheck") #$NON-NLS-1$
        self.aspellDir = os.path.join(self.spellingDir, u"aspell") #$NON-NLS-1$

        # Initialize the aspell directory (only if it is not already initialized).
        ZAspellSpellCheckDictionaryHandler().initializeAspellDirectory()

        if isUnicodePath(self.aspellDir):
            self.aspellDir = self._copyAspellDirToTemp(self.aspellDir)
            self.isTempAspellDir = True

        dataDir = os.path.abspath(os.path.join(self.aspellDir, u"data")) #$NON-NLS-1$
        dictDir = os.path.abspath(os.path.join(self.aspellDir, u"dict")) #$NON-NLS-1$
        language = dictionaryLanguage.getLanguageCode()

        self.speller = Speller(
            (u"lang", language), #$NON-NLS-1$
            (u"data-dir", dataDir), #$NON-NLS-1$
            (u"dict-dir", dictDir) #$NON-NLS-1$
        )
    # end __init__()

    def _copyAspellDirToTemp(self, spellingDir):
        osutil = getOSUtil()
        tempDir = osutil.getSystemTempDirectory()
        if not os.path.isdir(tempDir):
            raise ZException(u"System temp directory not found.") #$NON-NLS-1$
        tempSpellingDir = os.path.join(tempDir, u"_RavenSpellcheck_tmp") #$NON-NLS-1$
        if not os.path.exists(tempSpellingDir):
            os.mkdir(tempSpellingDir)
        copyFiles(spellingDir, tempSpellingDir)
        return tempSpellingDir
    # end _copyAspellDirToTemp()

    def check(self, word):
        # I realize this looks strange - but aspell's check() returns 1 or 0 and I want to return a bool
        if self.speller.check(self._encodeString(word)):
            return True
        else:
            return False
    # end check()

    def suggest(self, word):
        tmpList = self.speller.suggest(self._encodeString(word))
        return map(self._decodeString, tmpList)
    # end suggest()

    def destroy(self):
        del self.speller
        self.speller = None
        if self.isTempAspellDir:
            deleteDirectory(self.aspellDir, True)
    # end destroy()

    def _getDictionaryEncoding(self):
        if self.dictionaryEncoding is None:
            self.dictionaryEncoding = [i for i in self.speller.ConfigKeys() if i[0] == u'encoding'][0][2] #$NON-NLS-1$
        return self.dictionaryEncoding
    # end _getDictionaryEncoding()

    def _encodeString(self, value):
        try:
            return value.encode(self._getDictionaryEncoding())
        except:
            return u"" #$NON-NLS-1$
    # end _encodeString()

    def _decodeString(self, value):
        try:
            return value.decode(self._getDictionaryEncoding())
        except:
            return value
    # end _decodeString()

# end ZAspellSpellCheckProvider
