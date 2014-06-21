from zoundry.appframework.ui.widgets.controls.advanced.mshtml.mshtmlelements import XHTML_HR_PARENT_ELEMENTS
from zoundry.appframework.ui.widgets.controls.advanced.mshtml.mshtmlelements import getDispElement

#------------------------------------------------------
# This module contains classes and methods to create
# UI proxy elements with in the mshtml document. For example,
# a place holder image or hr element with a green dashed line
# is used in place of the <!-- more --> extended entry comment
# marker.
#------------------------------------------------------


#------------------------------------------------------
# Extended entry marker
#------------------------------------------------------
class ZMshtmlExtendedEntryMarkerProxy:

    EXTENDED_ENTRY_MARKER_ID = u"_zoundry_extended_entry_marker_id_"  #$NON-NLS-1$
    EXTENDED_ENTRY_MARKER_STYLE = u"height:2px;width:100%;border-bottom:2px dotted #090; display:block" #$NON-NLS-1$

    HR_MARKER = u"""<HR id="%s" class="%s" style="%s"/>""" % (EXTENDED_ENTRY_MARKER_ID, EXTENDED_ENTRY_MARKER_ID, EXTENDED_ENTRY_MARKER_STYLE) #$NON-NLS-1$
    IMG_MARKER = u"""<img id="%s" class="%s" style="%s" src="%s"/>""" % (EXTENDED_ENTRY_MARKER_ID, EXTENDED_ENTRY_MARKER_ID, EXTENDED_ENTRY_MARKER_STYLE, u"") #$NON-NLS-1$ #$NON-NLS-2$

    def replaceWithExtendedEntry(self, mshtmlDispElement):
        u"""
        replaceWithExtendedEntry(mshtmlDispElement) -> void
        Replaces the given element with an Extended Entry marker (either an image or an hr).
        """ #$NON-NLS-1$
        if mshtmlDispElement.parentNode and (mshtmlDispElement.parentNode.nodeName == u"BODY" or mshtmlDispElement.parentNode.nodeName == u"BLOCKQUOTE"): #$NON-NLS-1$ #$NON-NLS-2$
            mshtmlDispElement.insertAdjacentHTML(u"afterEnd", ZMshtmlExtendedEntryMarkerProxy.HR_MARKER) #$NON-NLS-1$
        else:
            mshtmlDispElement.insertAdjacentHTML(u"afterEnd", ZMshtmlExtendedEntryMarkerProxy.IMG_MARKER) #$NON-NLS-1$
        mshtmlDispElement.removeNode(True)
    # end replaceWithExtendedEntry

    def insertExtendedEntry(self, mshtmlElement):
        u"""
        insertExtendedEntry(IHtmlElement) -> void
        Inserts an Extended Entry marker (either an image or an hr).
        """ #$NON-NLS-1$
        # remove current marker, then insert new marker.
        self.removeExtendedEntry(mshtmlElement)
        try:
            if mshtmlElement.tagName.lower() in XHTML_HR_PARENT_ELEMENTS:
                mshtmlElement.insertAdjacentHTML(u"beforeEnd", ZMshtmlExtendedEntryMarkerProxy.HR_MARKER) #$NON-NLS-1$
            else:
                while not mshtmlElement.parentElement.tagName.lower() in XHTML_HR_PARENT_ELEMENTS:
                    mshtmlElement = mshtmlElement.parentElement
                if mshtmlElement and mshtmlElement.parentElement and mshtmlElement.parentElement.tagName.lower() in XHTML_HR_PARENT_ELEMENTS:
                    mshtmlElement.insertAdjacentHTML(u"afterEnd", ZMshtmlExtendedEntryMarkerProxy.HR_MARKER) #$NON-NLS-1$
            # end else
        except:
            pass
    # end insertExtendedEntry()

    def removeExtendedEntry(self, mshtmlElement): #@UnusedVariable
        u"""
        removeExtendedEntry(mshtmlElement) -> bool
        Removes Extended Entry marker and returns True on success.
        """ #$NON-NLS-1$

        # find body element
        while mshtmlElement.tagName != u"BODY" and mshtmlElement.parentElement: #$NON-NLS-1$
            mshtmlElement = mshtmlElement.parentElement
        if not mshtmlElement or mshtmlElement.tagName != u"BODY": #$NON-NLS-1$
            return False

        mshtmlDispElement = getDispElement(mshtmlElement)
        hrEleList = mshtmlDispElement.getElementsByTagName(u"HR")  #$NON-NLS-1$
        # remove all markers with special id
        for ele in hrEleList:
            id = ele.getAttribute(u"id")#$NON-NLS-1$
            if id == ZMshtmlExtendedEntryMarkerProxy.EXTENDED_ENTRY_MARKER_ID: #$NON-NLS-1$
                ele.removeNode(True)
        hrEleList = mshtmlDispElement.getElementsByTagName(u"IMG")  #$NON-NLS-1$
        # remove all markers with special id
        for ele in hrEleList:
            id = ele.getAttribute(u"id")#$NON-NLS-1$
            if id == ZMshtmlExtendedEntryMarkerProxy.EXTENDED_ENTRY_MARKER_ID: #$NON-NLS-1$
                ele.removeNode(True)
        return True
    # end removeExtendedEntry()
# end ZMshtmlExtendedEntryMarkerProxy()
