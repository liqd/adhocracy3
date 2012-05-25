from UserDict import DictMixin
from zope.interface import implements
from zope.component import adapts

from pyramid.threadlocal import get_current_registry
from repoze.lemonade.content import create_content

from adhocracy.dbgraph.interfaces import INode
from adhocracy.core.models.interfaces import IChildsDict
from adhocracy.core.models.interfaces import IChild


class NodeChildsDictAdapter(object, DictMixin):
    """Adapter to set and get child nodes to allow object traversal
    """

    implements(IChildsDict)
    adapts(INode)

    def __init__(self, context):
        self.context = context

    def _get_graph(self):
        registry = get_current_registry()
        return registry.getUtility(IGraphConnection)

    def __setitem__(self, key, node):
        #add new "is child" relation and save here the key aka child __name__
        create_content(IChild, parent=self.context, child=node, child_name=key)

    def __delitem__(self, key):
        items = filter(lambda edge: edge.child_name == key,\
                                    self.context.inE("child"))
        if len(items) == 1:
            item = items[0]
            graph = self._get_graph()
            proxy = graph.child
            proxy.delete(item.eid)
        elif len(items) == 0:
            raise KeyError
        else:
            raise KeyError("multiple items with key %s" % (key))

    def keys(self):
        return [e.child_name for e in self.context.inE("child")]

    def __getitem__(self, key):
        items = list(self.context.inV("child", property_key="child_name",\
                        property_value=key))
        if len(items) == 1:
            return items[0]
        elif len(items) == 0:
            raise KeyError
        else:
            raise KeyError("multiple items with key %s" % (key))

    def has_key(self, key):
        items = filter(lambda edge: edge.child_name == key,\
                                    self.context.inE("child"))
        return len(items) == 1

    @property
    def children(self):
        ""
