from bulbs.model import Node
from bulbs.property import String
from bulbs.property import List

from adhocracy.core.models.container import ContainerMixin
from adhocracy.core.security import SITE_ACL


class AdhocracyRoot(Node, ContainerMixin):
    """no parent == this is the application root object"""

    element_type = "adhocracyroot"

    __parent__ = None
    __name__ = ''

    __acl__ = List()
    name = String(nullable=False)


def appmaker(graph):
    root = graph.adhocracyroot.get_or_create("name", "adhocracyroot",
                                              name=u"adhocracyroot")
    if not root.__acl__:
        root.__acl__ = SITE_ACL
        root.save()
    return root
