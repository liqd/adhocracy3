#import unittest

#from adhocracy.core.testing import setUp
#from adhocracy.core.testing import tearDown
#from adhocracy.core.testing import get_graph
#from adhocracy.core.testing import Person
#from adhocracy.core.testing import Knows
#from adhocracy.core.models.interfaces import INode


#class NodeTests(unittest.TestCase):

    #def setUp(self):
        #self.config = setUp()
        #self.graph = get_graph()
        #self.graph.add_proxy("person", Person)
        #self.graph.add_proxy("knows", Knows)

    #def tearDown(self):
        #tearDown()

    #def test_list_persistence(self):
        #node = self.graph.person.get_or_create("name", u"testnode",
                                                  #name=u"testnode")
        #testlist = [[u"d", [[u"c"], []], u"a"]]
        #node.__acl__ = testlist
        #node.save()
        #node_ = self.graph.person.get_or_create("name", u"testnode",
                                                   #name=u"testnode")
        #self.assert_(node_.__acl__ == testlist)

    #def _populate(self):
        #"""add example nodes and relations"""
        #g = self.graph
        #self.james = g.person.create(name="James", age=34)
        #self.time = g.person.create(name="Time", age=3)
        #self.tom = g.person.create(name="Tom", age=3)
        #self.knows1 = g.knows.create(self.james, self.time, place=u"city")
        #self.knows2 = g.knows.create(self.james, self.tom, place=u"village")
        #self.knows3 = g.knows.create(self.time, self.tom, place=u"country")

    #def test_outV(self):
        #self._populate()
        ##outV filters edge label, and property key/value
        #self.assert_(len([x for x in  self.james.outV()]) == 2)
        #self.assert_(len([x for x in  self.james.outV(property_key="place",\
                                         #property_value="city")]) == 1)
        #self.assert_(len([x for x in  self.james.outV(label="knows")]) == 2)
        #self.assert_(len([x for x in  self.james.outV(label="knows",\
                                         #property_key="place",\
                                         #property_value="city")]) == 1)
        ##outV returns initialized node objects
        #res_object = self.james.outV().next()
        #self.assert_(isinstance(res_object, Person))
        #from zope.interface.verify import verifyObject
        #self.assert_(verifyObject(INode, res_object))

    ## like test_outV for inV
    #def test_inV(self):
        #self._populate()
        #self.assertEquals(len(list(self.tom.inV())), 2)
        #self.assertEquals(len(list(self.tom.inV(property_key="place",\
                                         #property_value="village"))), 1)
        #self.assertEquals(len(list(self.tom.inV(label="knows"))), 2)
        #self.assertEquals(len(list(self.tom.inV(label="knows",\
                                         #property_key="place",\
                                         #property_value="village"))), 1)
        ##inV returns initialized node objects
        #for res_object in self.tom.inV():
            #self.assert_(isinstance(res_object, Person))
            #from zope.interface.verify import verifyObject
            #self.assert_(verifyObject(INode, res_object))
