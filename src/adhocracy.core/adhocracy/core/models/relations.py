from bulbs.model import Relationship
from bulbs.property import String
from zope.interface import implements

from pyramid.threadlocal import get_current_registry

from adhocracy.core.models.interfaces import IChild
from adhocracy.core.models.interfaces import IGraphConnection


class Child(Relationship):

    implements(IChild)

    label = "child"
    child_name = String(nullable=False)


def child_factory(child, parent, child_name, **kw):
    interface = IChild
    registry = get_current_registry()
    graph = registry.getUtility(IGraphConnection)
    #add model proxy
    proxyname = interface.getTaggedValue('name')
    proxy = getattr(graph, proxyname, None)
    #create object
    return proxy.create(child, parent, child_name=child_name)
