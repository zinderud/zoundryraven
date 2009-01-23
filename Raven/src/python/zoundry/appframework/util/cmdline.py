from zoundry.appframework.exceptions import ZAppFrameworkException
from zoundry.appframework.messages import _extstr
from zoundry.base.util.text.unicodeutil import convertToUnicode
import re

CMD_LINE_PARAM_PATTERN_ONE = re.compile(r"--([^=]*)=(.*)") #$NON-NLS-1$
CMD_LINE_PARAM_PATTERN_TWO = re.compile(r"-([^=]*)=(.*)") #$NON-NLS-1$
CMD_LINE_PARAM_PATTERN_THREE = re.compile(r"--(.*)") #$NON-NLS-1$
CMD_LINE_PARAM_PATTERN_FOUR = re.compile(r"-(.*)") #$NON-NLS-1$


# -------------------------------------------------------------------------------------
# A class that wraps the sys.argv command line parameters.  This class parses those
# command line params and creates a map of parameters.  It supports command line params
# in the following formats:
#
# application.exe -key1 value -key2 value -key3 value
# application.exe --key1 value --key2 value --key3 value
# application.exe -key1=value -key2=value -key3=value
# application.exe --key1=value --key2=value --key3=value
# application.exe -key1 -key2
# application.exe --key1 --key2
#
# Users of this class can iterate through the keys, get the value of a single key,
# check for the existance of a single key, etc... You can also mix and match the
# param formats.
# -------------------------------------------------------------------------------------
class ZCommandLineParameters:

    def __init__(self, paramList):
        self.paramMap = {}

        self._parseParamList(paramList)
    # end __init__()

    def _parseParamList(self, paramList):
        i = 0
        while i < len(paramList):
            arg = convertToUnicode(paramList[i])
            match = re.match(CMD_LINE_PARAM_PATTERN_ONE, arg)
            if match:
                i = i + self._parsePatternOne(match)
                continue
            match = re.match(CMD_LINE_PARAM_PATTERN_TWO, arg)
            if match:
                i = i + self._parsePatternTwo(match)
                continue
            match = re.match(CMD_LINE_PARAM_PATTERN_THREE, arg)
            if match:
                i = i + self._parsePatternThree(match, paramList[i + 1:])
                continue
            match = re.match(CMD_LINE_PARAM_PATTERN_FOUR, arg)
            if match:
                i = i + self._parsePatternFour(match, paramList[i + 1:])
                continue
            raise ZAppFrameworkException(_extstr(u"cmdline.InvalidCmdLineError") % arg) #$NON-NLS-1$
    # end _parseParamList()

    def _parsePatternOne(self, match):
        key = match.group(1).lower()
        value = match.group(2)
        self.paramMap[key] = value
        return 1
    # end _parsePatternOne()

    def _parsePatternTwo(self, match):
        return self._parsePatternOne(match)
    # end _parsePatternOne()

    def _parsePatternThree(self, match, remainingParams):
        key = match.group(1).lower()
        value = None
        rval = 1
        if remainingParams:
            arg2 = convertToUnicode(remainingParams[0])
            if not arg2.startswith(u"-"): #$NON-NLS-1$
                value = arg2
                rval = 2
        self.paramMap[key] = value
        return rval
    # end _parsePatternOne()

    def _parsePatternFour(self, match, remainingParams):
        return self._parsePatternThree(match, remainingParams)
    # end _parsePatternOne()

    def hasKey(self, key):
        return key in self.paramMap
    # end hasKey()

    def getValue(self, key, dflt = None):
        if key in self.paramMap:
            return self.paramMap[key]
        return dflt
    # end getValue()

    def getKeys(self):
        return self.paramMap.keys()
    # end getKeys()

    def __len__(self):
        return len(self.paramMap)
    # end __len__()

    def __contains__(self, key):
        return key in self.paramMap
    # end __contains__()

    def __iter__(self):
        return self.getKeys().__iter__()
    # end __iter__()

    def __getitem__(self, key):
        return self.getValue(key, None)
    # end __getitem__()

# end ZCommandLineParameters
