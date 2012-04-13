"""global utilites to work with models, read utilities.zcml"""

from zope.interface import implementer
from zope.interface import alsoProvides
from bulbs.rexster import Config
from bulbs.rexster import REXSTER_URI
from bulbs.rexster import Graph
from bulbs.config import DEBUG
from adhocracy.core.models.container import Container
from adhocracy.core.models.adhocracyroot import AdhocracyRoot
from adhocracy.core.models.relations import Child
from adhocracy.core.models.interfaces import IGraphConnection



@implementer(IGraphConnection)
def graph_object():

    config = Config(REXSTER_URI)
    #graphdb connection
    g = Graph(config)
    alsoProvides(g, IGraphConnection)
    #enable loggin
    g.config.set_logger(DEBUG)
    #add model proxies
    g.add_proxy("adhocracyroot", AdhocracyRoot)
    g.add_proxy("container", Container)
    g.add_proxy("child", Child)

    return g

