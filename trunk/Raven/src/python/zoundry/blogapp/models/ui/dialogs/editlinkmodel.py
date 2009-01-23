from zoundry.base.util.types.attrmodel import ZModelWithNoneValueAttributes
from zoundry.appframework.ui.util.clipboardutil import getUrlFromClipboard
from zoundry.base.util.text.textutil import getNoneString

# ------------------------------------------------------------------------------------
# Model used by the edit link dialog.
# ------------------------------------------------------------------------------------

class ZEditLinkModel(ZModelWithNoneValueAttributes):

    def __init__(self, linkAttrMap):
        ZModelWithNoneValueAttributes.__init__(self)
        self.editMode = False
        if linkAttrMap is not None:
            self.editMode = True
            for (n,v) in linkAttrMap.iteritems():
                self.setAttribute(n,v)
        if not self.getAttribute(u"href"): #$NON-NLS-1$ 
            url = getUrlFromClipboard()
            if url:
                self.setAttribute(u"href", url) #$NON-NLS-1$
    # end __init__   
    
    def getLinkAttributes(self):     
        attrs = {}
        for (n,v) in self.getAttributes():
            attrs[n] = v
        return attrs

    def isEditMode(self):
        return self.editMode
    # end isEditMode

    def isOpenInNewWindow(self):
        return getNoneString( self.getAttribute(u"target") ) is not None #$NON-NLS-1$
    # end isOpenInNewWindow()
# end ZEditLinkModel