from zoundry.base.util.types.attrmodel import ZModelWithAttributes
from zoundry.blogapp.services.common import IZCategory

# -----------------------------------------------------------------------------------------
# This class models a single category.
# -----------------------------------------------------------------------------------------
class ZCategory(ZModelWithAttributes, IZCategory):

    def __init__(self):
        ZModelWithAttributes.__init__(self)
    # end __init__()

    def getId(self):
        return self.getAttribute(u"id") #$NON-NLS-1$
    # end getId()

    def setId(self, id):
        self.setAttribute(u"id", id) #$NON-NLS-1$
    # end setId()

    def getName(self):
        return self.getAttribute(u"name") #$NON-NLS-1$
    # end getName()

    def setName(self, name):
        self.setAttribute(u"name", name) #$NON-NLS-1$
    # end setName()

    def getDescription(self):
        return self.getAttribute(u"description") #$NON-NLS-1$
    # end getDescription()

    def setDescription(self, description):
        self.setAttribute(u"description", description) #$NON-NLS-1$
    # end setDescription()

    def __str__(self):
        return  self.getId()
    # end __str__

# end ZCategory
