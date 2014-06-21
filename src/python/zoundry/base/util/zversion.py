import string

# ----------------------------------------------------------------------------
# Represents a Zoundry Version number.  The version number is a string of
# digits separated by periods.  Some examples:
#   - 1.0
#   - 2.1.7
#   - 1.0.1.3
#   - 6.11.3.19
# This class parses the string into its component parts.  In addition, this
# class can be compared to other instances of ZVersion in order to test 
# whether a version is less than, greater than, or equal to it.
# ----------------------------------------------------------------------------
class ZVersion:
    
    def __init__(self, versionString):
        self.versionString = versionString
        self.versionComponents = self._parseVersionString(versionString)
    # end __init__()

    def _parseVersionString(self, versionString):
        return map(int, versionString.split(u".")) #$NON-NLS-1$
    # end _parseVersionString()

    def __getitem__(self, index):
        return self.versionComponents[index]
    # end __getitem__()

    def __str__(self):
        return string.join(map(unicode, self.versionComponents), u".") #$NON-NLS-1$
    # end __str__()

    def __len__(self):
        return len(self.versionComponents)
    # end __len__()

    def __eq__(self, other):
        if not other:
            return False
        return self.versionComponents == other.versionComponents
    # end __eq__()

    def __ge__(self, other):
        if not other:
            return False
        return self.versionComponents >= other.versionComponents
    # end __ge__()

    def __gt__(self, other):
        if not other:
            return False
        return self.versionComponents > other.versionComponents
    # end __gt__()

    def __le__(self, other):
        if not other:
            return False
        return self.versionComponents <= other.versionComponents
    # end __le__()

    def __lt__(self, other):
        if not other:
            return False
        return self.versionComponents < other.versionComponents
    # end __lt__()

    def __ne__(self, other):
        if not other:
            return False
        return self.versionComponents != other.versionComponents
    # end __ne__()

# end ZVersion


# ----------------------------------------------------------------------------
# The version pattern class is a class that is used to compare the value of
# a version pattern in a license file with an actual version of the product.
# The logic for comparing what is in the license to the product version is
# a bit different.  For example, if you have a 1.0 license, you are also
# licensed for any 1.0.x product version (meaning you would get patch updates
# for free).  However, you would NOT be licensed for version 1.1 or higher.
# ----------------------------------------------------------------------------
class ZVersionPattern(ZVersion):

    def __init__(self, versionPattern):
        ZVersion.__init__(self, versionPattern)
    # end __init__()

    def __eq__(self, other):
        if not other:
            return False
        subcomponents = other.versionComponents[0:len(self.versionComponents)]
        return self.versionComponents == subcomponents
    # end __eq__()

    def __ne__(self, other):
        if not other:
            return False
        subcomponents = other.versionComponents[0:len(self.versionComponents)]
        return self.versionComponents != subcomponents
    # end __ne__()

# end ZVersionPattern
