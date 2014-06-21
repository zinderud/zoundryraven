
# ------------------------------------------------------------------------------
# The types of resource dependencies.
# ------------------------------------------------------------------------------
class IZResourceDependencyTypes:

    CSS = u"text/css" #$NON-NLS-1$
    IMAGE = u"image/*" #$NON-NLS-1$
    SCRIPT = u"script/*" #$NON-NLS-1$

# end IZResourceDependencyTypes


# ------------------------------------------------------------------------------
# This class models a single dependency from a resource file such as an xhtml
# or css file.  It contains the href and the type of dependency.
# ------------------------------------------------------------------------------
class ZResourceDependency:

    def __init__(self, type, href):
        self.type = type
        self.href = href
    # end __init__()

    def getType(self):
        return self.type
    # end getType()

    def getHref(self):
        return self.href
    # end getHref()

# end ZResourceDependency


# ------------------------------------------------------------------------------
# Interface that all dependency finders implement.
# ------------------------------------------------------------------------------
class IZResourceDependencyFinder:

    def findDependencies(self):
        u"""findDependencies() -> ZResourceDependency[]""" #$NON-NLS-1$
    # end findDependencies()

# end IZResourceDependencyFinder

