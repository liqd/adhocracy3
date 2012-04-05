from bulbs.model import Relationship
from bulbs.property import String


class Child(Relationship):

    label = "child"
    child_name = String(nullable=False)
