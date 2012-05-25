adhocracy.dbgraph 
=================

Basic graph db abstraction layer used by adhocracy.core, similar to the "python-blueprint" egg.
The only implementatin is based on http://pypi.python.org/pypi/neo4j-embedded/.


Get the graph object:
---------------------

Set a custom databse connection string in your pyramid settings:

    >>> from pyramid import testing
    >>> from adhocracy.dbgraph.tests import GRAPHDB_CONNECTION_STRING 
    >>> settings = {'graphdb_connection_string': GRAPHDB_CONNECTION_STRING}
    >>> config = testing.setUp(settings=settings)

Get the graph object to play with::

    >>> from adhocracy.dbgraph.embeddedgraph import get_graph, del_graph
    >>> from adhocracy.dbgraph.interfaces import IGraph
    >>> graph1 = get_graph()
    >>> IGraph.providedBy(graph1)
    True
    >>> from zope.interface.verify import verifyObject
    >>> verifyObject(IGraph, graph1)
    True

The graph object object has to be a singleton for all you python processes:

    >>> graph2 = get_graph()
    >>> graph1 is graph2
    True

Getting the root vertex to start with:
    >>> graph1.get_root_vertex()
    <Vertex 0>

Manually shutdown the database::

    >>> del_graph()
    >>> testing.tearDown()


How to work with the graph object:
-----------------------------------

Read adhocracy/dbgraph/interfaces.py

