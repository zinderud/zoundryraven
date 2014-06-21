from zoundry.base.zdom.dom import ZDom

# ------------------------------------------------------------------------------
# Base class for XML serializers.
# ------------------------------------------------------------------------------
class ZBaseXMLSerializer:

    def __init__(self, prefix, namespace):
        self.prefix = prefix
        self.namespace = namespace
        self.dom = None
    # end __init__()

    def _createDocument(self, rootName = u"root"): #$NON-NLS-1$
        u"""Creates the zdom document.""" #$NON-NLS-1$
        dom = ZDom()
        params = {
            u"prefix" : self.prefix, #$NON-NLS-1$
            u"root" : rootName, #$NON-NLS-1$
            u"namespace" : self.namespace #$NON-NLS-1$
        }
        xml = u"""<%(prefix)s:%(root)s xmlns:%(prefix)s="%(namespace)s" />""" % params #$NON-NLS-1$
        dom.loadHTML(xml)
        return dom
    # end _createDocument()

    def _createChildElement(self, dom, parent, elemName, elemValue = None):
        elem = dom.createElement(self.prefix + u":" + elemName, self.namespace) #$NON-NLS-1$
        parent.appendChild(elem)
        if elemValue is not None:
            elem.setText(elemValue)
        return elem
    # end _createChildElement()

# end ZBaseXMLSerializer


# ------------------------------------------------------------------------------
# Serializes a list of strings into a DOM.
# ------------------------------------------------------------------------------
class ZStringListToXMLSerializer(ZBaseXMLSerializer):

    def __init__(self):
        ZBaseXMLSerializer.__init__(self, u"str", u"urn:zoundry:xml-data") #$NON-NLS-1$ #$NON-NLS-2$
    # end __init__()

    def serialize(self, strings):
        dom = self._createDocument(u"stringList") #$NON-NLS-1$
        for string in strings:
            self._createChildElement(dom, dom.documentElement, u"string", string) #$NON-NLS-1$
        return dom.documentElement
    # end serialize()

# end ZStringListToXMLSerializer

