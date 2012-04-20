"""global utilites to work with models, read utilities.zcml"""
import os.path

from zope.interface import implementer
from zope.interface import alsoProvides
from bulbs.rexster import Config
from bulbs.rexster import Graph
from bulbs.config import DEBUG
from pyramid.threadlocal import get_current_registry

import adhocracy.core.models
from adhocracy.core.models.container import Container
from adhocracy.core.models.adhocracyroot import AdhocracyRoot
from adhocracy.core.models.relations import Child
from adhocracy.core.models.interfaces import IGraphConnection
from adhocracy.core.models.interfaces import IContainer
from adhocracy.core.models.interfaces import IChild
from adhocracy.core.models.interfaces import IAdhocracyRoot


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
    #add model proxies
    g.add_proxy("adhocracyroot", AdhocracyRoot)
    g.add_proxy("container", Container)
    g.add_proxy("child", Child)

    return g


@implementer(IAdhocracyRoot)
def adhocracyroot_factory():
    registry = get_current_registry()
    graph = registry.getUtility(IGraphConnection)
    root = graph.adhocracyroot.get_or_create("name", "adhocracyroot",
                                              name=u"adhocracyroot")
    return root


@implementer(IContainer)
def container_factory(name, **kw):
    registry = get_current_registry()
    graph = registry.getUtility(IGraphConnection)
    content = graph.container.get_or_create("name", name, name=name)

    return content


@implementer(IChild)
def child_factory(child, parent, child_name, **kw):
    registry = get_current_registry()
    graph = registry.getUtility(IGraphConnection)
    child_relation = graph.child.create(child, parent, child_name=child_name)

    return child_relation
