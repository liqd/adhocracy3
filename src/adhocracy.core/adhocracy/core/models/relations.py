from UserDict import DictMixin
from zope import interface
from zope.component import adapts

from repoze.lemonade.content import create_content

from adhocracy.dbgraph.interfaces import INode
from adhocracy.dbgraph.embeddedgraph import get_graph
from adhocracy.core.models.interfaces import IChildsDict
from adhocracy.core.models.references import IChildMarker
from adhocracy.core.models.references import IChild


class NodeChildsDictAdapter(object, DictMixin):
    """Adapter to set and get child nodes to allow object traversal
    """

    interface.implements(IChildsDict)
    adapts(INode)

    def __init__(self, context):
        self.context = context

    def __setitem__(self, key, node):
        create_content(IChildMarker, parent=self.context, child=node, child_name=key)

    def __delitem__(self, key):
        edges = filter(lambda edge: IChild(edge).child_name == key,\
                                    self.context.in_edges("child"))
        if len(edges) == 1:
            edge = edges[0]
            graph = get_graph()
            graph.remove_edge(edge)
        elif len(edges) == 0:
            raise KeyError
        else:
            raise KeyError("multiple child nodes with key %s" % (key))

    def keys(self):
        return [IChild(e).child_name for e in self.context.in_edges("child")]

    def __getitem__(self, key):
        edges = filter(lambda edge: IChild(edge).child_name == key,\
                                    self.context.in_edges("child"))

        if len(edges) == 1:
            return edges[0].start_vertex()
        elif len(edges) == 0:
            raise KeyError
        else:
            raise KeyError("multiple child nodes with key %s" % (key))

    def has_key(self, key):
        items = filter(lambda edge: IChild(edge).child_name == key,\
                                    self.context.in_edges("child"))
        return len(items) == 1

    @property
    def children(self):
        ""
