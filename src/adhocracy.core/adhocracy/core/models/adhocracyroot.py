from bulbs.property import String
from bulbs.property import List

from zope.interface import implements

from repoze.lemonade.content import create_content

#from adhocracy.core.models.container import ContainerMixin
from adhocracy.core.models.interfaces import IAdhocracyRoot
from adhocracy.core.models.node import NodeAdhocracy
from adhocracy.core.security import SITE_ACL


class AdhocracyRoot(NodeAdhocracy):
    """no parent == this is the application root object"""

    implements(IAdhocracyRoot)

    element_type = "adhocracyroot"

    __parent__ = None
    __name__ = ''

    __acl__ = List()
    name = String(nullable=False)


def appmaker():
    root = create_content(IAdhocracyRoot)
    if not root.__acl__:
        root.__acl__ = SITE_ACL
        root.save()
    return root
