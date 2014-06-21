from zoundry.base.util.types.attrmodel import IZAttributeModel

# -----------------------------------------------------------------------------------------
# Interface that defines a category (typically found in a blog).
# -----------------------------------------------------------------------------------------
class IZCategory(IZAttributeModel):

    def getId(self):
        u"Gets the category id." #$NON-NLS-1$
    # end getId()

    def setId(self, id):
        u"Sets the category id." #$NON-NLS-1$
    # end setId()

    def getName(self):
        u"Gets the category name." #$NON-NLS-1$
    # end getName()
    
    def setName(self, name):
        u"Sets the category name." #$NON-NLS-1$
    # end setName()

# end IZCategory
