from UserDict import DictMixin
from rwproperty import setproperty
from rwproperty import getproperty
from zope.interface import implements
from repoze.lemonade.content import create_content

from pyramid.threadlocal import get_current_registry
from bulbs.model import Node
from bulbs.property import String

from adhocracy.core.models.interfaces import IGraphConnection
from adhocracy.core.models.interfaces import IContainer
from adhocracy.core.models.interfaces import IChild


class ContainerMixin(object, DictMixin):
    """Containers mixing used for subitem access and in object traversal.
       TODO: make this fast, generic and well tested
    """

    def _get_graph(self):
        registry = get_current_registry()
        return registry.getUtility(IGraphConnection)

    def __setitem__(self, key, node):
        #add new "is child" relation and save here the key aka child __name__
        create_content(IChild, parent=self, child=node, child_name=key)

    def __delitem__(self, key):
        items = filter(lambda edge: edge.child_name == key, self.inE("child"))
        if len(items) == 1:
            item = items[0]
            graph = self._get_graph()
            proxy = graph.child
            proxy.delete(item.eid)
        elif len(items) == 0:
            raise KeyError
        else:
            raise KeyError, "multiple items with key %s"%(key)

    def keys(self):
        return [e.child_name for e in self.inE("child")]

    def __getitem__(self, key):
        items = filter(lambda edge: edge.child_name == key, self.inE("child"))
        if len(items) == 1:
            item = items[0].outV()
            graph = self._get_graph()
            proxy_name = self.get_index_name(graph.config)
            proxy = getattr(graph, proxy_name)
            return proxy.get(item.eid)
        elif len(items) == 0:
            raise KeyError
        else:
            raise KeyError, "multiple items with key %s"%(key)
            
    def has_key(self, key):
        items = filter(lambda edge: edge.child_name == key, self.inE("child"))
        return len(items) == 1

    @property
    def children(self):
        ""


class Container(Node, ContainerMixin):

    implements(IContainer)

    element_type = "container"

    text = String(default=u"")
    name = String(nullable=False)

    @property
    def __parent__(self):
        rel = list(self.outE("child"))
        item = rel and rel[0] \
                 or None
        if item:
            graph = self._get_graph()
            proxy = self.get_index_name(graph.config)
            proxy = getattr(graph, proxy)
            item = proxy.get(item.inV().eid)
        return item

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
