"""global utilites to work with models, read utilities.zcml"""
from pyblueprints.neo4j import Neo4jTransactionalIndexableGraph
from zope.interface import implementer
from zope.interface import alsoProvides
from pyramid.threadlocal import get_current_registry

from adhocracy.core.models.interfaces import IGraphConnection


@implementer(IGraphConnection)
def graph_object():

    registry = get_current_registry()
    url = registry.settings['neo4j_uri'] \
          or "http://localhost:7475/db/data"
    g = Neo4jTransactionalIndexableGraph(url)
    alsoProvides(g, IGraphConnection)

    return g
