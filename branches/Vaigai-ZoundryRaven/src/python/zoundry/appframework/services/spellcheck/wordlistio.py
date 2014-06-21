from zoundry.appframework.constants import IZAppNamespaces
from zoundry.base.zdom.dom import ZDom

# ---------------------------------------------------------------------------------------
# Returns the text of an element.
# ---------------------------------------------------------------------------------------
def _getElementText(node):
    return node.getText()
# end _getElementText()


# ---------------------------------------------------------------------------------------
# Loads the information in a wordlist.xml file.
# ---------------------------------------------------------------------------------------
def loadWordListXML(filePath):
    u"""loadWordListXML(string) -> string []
    Loads the wordlist.xml file at the given path and parses
    it into a list of strings.""" #$NON-NLS-1$
    dom = ZDom()
    dom.load(filePath)
    nssMap = { u"ns" : IZAppNamespaces.RAVEN_WORD_LIST_NAMESPACE } #$NON-NLS-1$
    nodes = dom.selectNodes(u"/ns:word-list/ns:word", nssMap) #$NON-NLS-1$
    return map(_getElementText, nodes)
# end loadWordListXML()
