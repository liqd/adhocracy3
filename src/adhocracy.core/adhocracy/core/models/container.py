from bulbs.property import String
from rwproperty import setproperty
from rwproperty import getproperty
from zope.interface import implements

from pyramid.threadlocal import get_current_registry

from adhocracy.core.models.node import NodeAdhocracy
from adhocracy.core.models.interfaces import IGraphConnection
from adhocracy.core.models.interfaces import IContainer


class Container(NodeAdhocracy):

    implements(IContainer)

    element_type = "container"

    text = String(default=u"")
    name = String(nullable=False)

    @property
    def __parent__(self):
        try:
            return self.outV("child").next()
        except StopIteration:
            return None

    @getproperty
    def __name__(self):
        rel = list(self.outE("child"))
        name = rel and rel[0].child_name \
               or ""
        return name

    @setproperty
    def __name__(self, name):
        rel = list(self.outE("child"))
        if rel:
            rel[0].child_name = name
            rel[0].save


def container_factory(name, **kw):
    interface = IContainer
    registry = get_current_registry()
    graph = registry.getUtility(IGraphConnection)
    #add model proxy
    proxyname = interface.getTaggedValue('name')
    proxy = getattr(graph, proxyname, None)
    #create object
    return proxy.get_or_create("name", name, name=name)
