from UserDict import DictMixin
from rwproperty import setproperty
from rwproperty import getproperty

from pyramid.threadlocal import get_current_registry
from bulbs.model import Node
from bulbs.property import String

from adhocracy.core.models.interfaces import IGraphConnection


class ContainerMixin(object, DictMixin):
    """Containers mixing used for subitem access and in object traversal.
       TODO: make this fast, generic and well tested
    """

    def _get_graph(self):
        registry = get_current_registry()
        return registry.getUtility(IGraphConnection)

    def __setitem__(self, key, node):
        g = self._get_graph()
        #add new "is child" relation and save here the key aka child __name__
        g.child.create(node, self, child_name=key)

    def __delitem__(self, key):
        ""

    def keys(self):
        return [e.child_name for e in  self.inE("child")]

    def __getitem__(self, path):
        #case path == child_name
        item = self.inE("child").next().outV()
        if item:
            graph = self._get_graph()
            proxy = self.get_index_name(graph.config)
            proxy = getattr(graph, proxy)
            return proxy.get(item.eid)
        raise KeyError

    @property
    def children(self):
        ""


class Container(Node, ContainerMixin):

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
            item = proxy.get(item.eid)
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



