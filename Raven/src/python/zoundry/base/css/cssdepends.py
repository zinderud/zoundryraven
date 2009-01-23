from zoundry.base.resdepends import IZResourceDependencyFinder
from zoundry.base.resdepends import IZResourceDependencyTypes
from zoundry.base.resdepends import ZResourceDependency
import re

IMPORT_PATTERN = re.compile(r"@import[\s]+url[\s]*\([\s]*[\"']?([^\"')\s]*)[\"']?[\s]*\)", re.IGNORECASE) #$NON-NLS-1$
BG_IMAGE_PATTERN = re.compile(r"background(?:-image)?[\s]*:[^u]*url[\s]*\([\s]*[\"']?([^\"')\s]*)[\"']?[\s]*\)") #$NON-NLS-1$

# ------------------------------------------------------------------------------
# Finds dependencies in the css content.  This class looks for images and other,
# @imported, css files.
# ------------------------------------------------------------------------------
class ZCSSDependencyFinder(IZResourceDependencyFinder):

    def __init__(self, css):
        self.css = css
    # end __init__()

    def findDependencies(self):
        dependencies = []
        # Find imports
        imports = IMPORT_PATTERN.findall(self.css)
        for cssImport in imports:
            dependencies.append(ZResourceDependency(IZResourceDependencyTypes.CSS, cssImport))
        # Find background images
        bgImages = BG_IMAGE_PATTERN.findall(self.css)
        for bgImage in bgImages:
            dependencies.append(ZResourceDependency(IZResourceDependencyTypes.IMAGE, bgImage))

        return dependencies
    # end findDependencies()

# end ZCSSDependencyFinder
