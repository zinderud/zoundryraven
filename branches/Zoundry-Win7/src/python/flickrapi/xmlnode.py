#@PydevCodeAnalysisIgnore

u'''FlickrAPI uses its own in-memory XML representation, to be able to easily
use the info returned from Flickr.

There is no need to use this module directly, you'll get XMLNode instances
from the FlickrAPI method calls.
''' #$NON-NLS-1$

import xml.dom.minidom

__all__ = (u'XMLNode', ) #$NON-NLS-1$

class XMLNode:
    u"""XMLNode -- generic class for holding an XML node

    >>> xml_str = '''<xml foo="32">
    ... <taggy bar="10">Name0</taggy>
    ... <taggy bar="11" baz="12">Name1</taggy>
    ... </xml>'''
    >>> f = XMLNode.parse(xml_str)
    >>> f.name
    u'xml'
    >>> f['foo']
    u'32'
    >>> f.taggy[0].name
    u'taggy'
    >>> f.taggy[0]["bar"]
    u'10'
    >>> f.taggy[0].text
    u'Name0'
    >>> f.taggy[1].name
    u'taggy'
    >>> f.taggy[1]["bar"]
    u'11'
    >>> f.taggy[1]["baz"]
    u'12'

    """ #$NON-NLS-1$

    def __init__(self):
        u"""Construct an empty XML node.""" #$NON-NLS-1$
        self.name = u"" #$NON-NLS-1$
        self.text = u"" #$NON-NLS-1$
        self.attrib = {}
        self.xml = None

    def __setitem__(self, key, item):
        u"""Store a node's attribute in the attrib hash.""" #$NON-NLS-1$
        self.attrib[key] = item

    def __getitem__(self, key):
        u"""Retrieve a node's attribute from the attrib hash.""" #$NON-NLS-1$
        return self.attrib[key]

    def __contains__(self, item):
        return item in self.attrib
    # end __contains__()

    @classmethod
    def __parse_element(cls, element, this_node):
        u"""Recursive call to process this XMLNode.""" #$NON-NLS-1$

        this_node.name = element.nodeName

        # add element attributes as attributes to this node
        for i in range(element.attributes.length):
            an = element.attributes.item(i)
            this_node[an.name] = an.nodeValue

        for a in element.childNodes:
            if a.nodeType == xml.dom.Node.ELEMENT_NODE:

                child = XMLNode()
                # Ugly fix for an ugly bug. If an XML element <name />
                # exists, it now overwrites the 'name' attribute
                # storing the XML element name.
                if not hasattr(this_node, a.nodeName) or a.nodeName == u'name': #$NON-NLS-1$
                    setattr(this_node, a.nodeName, [])

                # add the child node as an attrib to this node
                children = getattr(this_node, a.nodeName)
                children.append(child)

                cls.__parse_element(a, child)

            elif a.nodeType == xml.dom.Node.TEXT_NODE:
                this_node.text += a.nodeValue
        
        return this_node

    @classmethod
    def parse(cls, xml_str, store_xml=False):
        u"""Convert an XML string into a nice instance tree of XMLNodes.

        xml_str -- the XML to parse
        store_xml -- if True, stores the XML string in the root XMLNode.xml

        """ #$NON-NLS-1$

        dom = xml.dom.minidom.parseString(xml_str)

        # get the root
        root_node = XMLNode()
        if store_xml: root_node.xml = xml_str

        return cls.__parse_element(dom.firstChild, root_node)
