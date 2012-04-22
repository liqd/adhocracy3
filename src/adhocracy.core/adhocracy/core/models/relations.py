from zope.interface import implements

from bulbs.model import Relationship
from bulbs.property import String

from adhocracy.core.models.interfaces import IChild


class Child(Relationship):

    implements(IChild)

    label = "child"
    child_name = String(nullable=False)
