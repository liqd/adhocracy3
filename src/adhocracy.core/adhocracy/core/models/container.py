from rwproperty import setproperty
from rwproperty import getproperty
from zope import interface
from zope import schema
from zope.component import adapts

from adhocracy.dbgraph.interfaces import INode
from adhocracy.dbgraph.embeddedgraph import get_graph
from adhocracy.dbgraph.fieldproperty import AdoptedFieldProperty

from adhocracy.core.models.interfaces import ILocationAware


class IContainerMarker(INode):
    """
    Container object Marker.
    """


class IContainer(interface.Interface):
    """
    Container object basic interface.
    """

    text = schema.TextLine(title=u"Text")


class Container(object):
    interface.implements(IContainer)
    adapts(IContainerMarker)

    def __init__(self, context):
         self.context = context

    text = AdoptedFieldProperty(IContainer["text"])


class ContainerLocationAware(object):
    interface.implements(ILocationAware)
    adapts(IContainerMarker)

    def __init__(self, context):
         self.context = context

    @property
    def __parent__(self):
        childs = list(self.context.out_edges(label="child"))
        child = childs and childs[0] or None
        return child

    @getproperty
    def __name__(self):
        childs = list(self.context.out_edges(label="child"))
        name = childs and childs[0].child_name or ""
        return name

    @setproperty
    def __name__(self, name):
        childs = list(self.context.out_edges(label="child"))
        if childs:
            childs[0].set_property("child_name", name)

    __acl__ = AdoptedFieldProperty(ILocationAware["__acl__"])


@interface.implementer(IContainerMarker)
def container_factory():
    graph = get_graph()
    content = graph.add_vertex(IContainerMarker)
    return content
