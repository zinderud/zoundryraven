
# ------------------------------------------------------------------------------
# Base class for XML deserializers.
# ------------------------------------------------------------------------------
class ZBaseXMLDeserializer:

    def __init__(self, prefix, namespace):
        self.prefix = prefix
        self.namespace = namespace

        self.nsMap = { self.prefix : self.namespace }
    # end __init__()

    def _selectNodes(self, element, xpath):
        return element.selectNodes(xpath, self.nsMap)
    # end _selectNodes()

# end ZBaseXMLDeserializer


# ------------------------------------------------------------------------------
# Serializes a list of strings into a DOM.
# ------------------------------------------------------------------------------
class ZXMLToStringListDeserializer(ZBaseXMLDeserializer):

    def __init__(self):
        ZBaseXMLDeserializer.__init__(self, u"str", u"urn:zoundry:xml-data") #$NON-NLS-1$ #$NON-NLS-2$
    # end __init__()

    def deserialize(self, element):
        strings = []
        for strNode in self._selectNodes(element, u"str:string"): #$NON-NLS-1$
            string = strNode.getText()
            strings.append(string)
        return strings
    # end deserialize()

# end ZXMLToStringListDeserializer

