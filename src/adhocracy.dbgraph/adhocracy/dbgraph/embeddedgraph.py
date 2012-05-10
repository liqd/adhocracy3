from zope.interface import implements
from pyramid.threadlocal import get_current_registry

from adhocracy.dbgraph.interfaces import IGraph


class EmbeddedGraph():
    implements(IGraph)



def graph_factory(self):
    registry = get_current_registry()
    connection_string = registry.settings['graphdb_connection_string'] \
                        or "http://localhost:7475/db/data"
    return EmbeddedGraph(connection_string)

