from zoundry.blogapp.constants import IZBlogAppNamespaces
from zoundry.base.zdom.dom import ZDom

# ------------------------------------------------------------------------------
# Usage packet serializer.
# ------------------------------------------------------------------------------
class ZUsagePacketSerializer:

    def __init__(self):
        pass
    # end __init__()
    
    def serialize(self, packet):
        dom = ZDom()
        dom.loadXML(u"<zup:usage-packet xmlns:zup='%s' />" % IZBlogAppNamespaces.RAVEN_USAGE_STATS_NAMESPACE) #$NON-NLS-1$
        
        rootElem = dom.documentElement
        rootElem.setAttribute(u"packet-id", packet.getId()) #$NON-NLS-1$
        
        for key in packet.getAttributes():
            value = packet.getAttributes()[key]
            attrElem = dom.createElement(u"zup:attribute", IZBlogAppNamespaces.RAVEN_USAGE_STATS_NAMESPACE) #$NON-NLS-1$
            rootElem.appendChild(attrElem)
            attrElem.setAttribute(u"name", key) #$NON-NLS-1$
            attrElem.setText(value)
        
        return dom
    # end serialize()

# end ZUsagePacketSerializer
