import unittest

from bulbs.model import Relationship
from bulbs.property import String
from bulbs.property import Integer

from pyramid import testing
from pyramid.threadlocal import get_current_registry

from adhocracy.core.models.interfaces import IGraphConnection
from adhocracy.core.models.node import NodeAdhocracy


class Person(NodeAdhocracy):

    element_type = "person"
    name = String(nullable=False)
    age  = Integer()


class Knows(Relationship):

    label = "knows"
    place = String()


class NodeTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp(settings={'rexster_uri':"http://localhost:8182/graphs/testgraph"})
        self.config.include('pyramid_zcml')
        self.config.load_zcml('adhocracy.core.models:utilities.zcml')

        #create example node and relation proxies
        registry = get_current_registry()
        g = registry.getUtility(IGraphConnection)
        g.add_proxy("person", Person)
        g.add_proxy("knows", Knows)
        self.g = g

    def tearDown(self):
        testing.tearDown()

    def test_outV(self):
        #add example nodes and relations
        g = self.g
        self.james = g.person.create(name="James", age=34)
        self.time = g.person.create(name="Time", age=3)
        self.tom = g.person.create(name="Tom", age=3)
        self.knows1 = g.knows.create(self.james, self.time, place=u"city")
        self.knows2 = g.knows.create(self.james, self.tom, place=u"village")
        #outV filters edge label, and property key/value
        self.assert_(len([x for x in  self.james.outV()]) == 2)
        self.assert_(len([x for x in  self.james.outV(property_key="place", property_value="city")]) == 1)
        self.assert_(len([x for x in  self.james.outV(label="knows")]) == 2)
        self.assert_(len([x for x in  self.james.outV(label="knows", property_key="place", property_value="city")]) == 1)
        #outV returns initialized node objects
        res_object = self.james.outV().next()
        self.assert_(isinstance(res_object, Person))

