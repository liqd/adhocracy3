"""global utilites to work with models, read utilities.zcml"""
import os.path
from bulbs.rexster import Config
from bulbs.rexster import Graph
from zope.interface import implementer
from zope.interface import alsoProvides

from pyramid.threadlocal import get_current_registry

import adhocracy.core.models
from adhocracy.core.models.interfaces import IGraphConnection


@implementer(IGraphConnection)
def graph_object():

    registry = get_current_registry()
    config = registry.settings and Config(registry.settings['rexster_uri']) \
             or None
    #graphdb connection
    g = Graph(config)
    alsoProvides(g, IGraphConnection)
    #enable loggin
    #g.config.set_logger(DEBUG)
    #add custom gremlin scripts
    package_path = adhocracy.core.models.__path__[0]
    file_path = os.path.join(package_path, "gremlin.groovy")
    g.scripts.update(file_path)

    return g



