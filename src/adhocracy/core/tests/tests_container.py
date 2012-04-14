import unittest

from pyramid.threadlocal import get_current_registry
from pyramid import testing

from adhocracy.core.models.interfaces import IGraphConnection

class ModelTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp(settings={'rexster_uri':"http://localhost:8182/graphs/testgraph"})
        self.config.include('pyramid_zcml')
        self.config.load_zcml('adhocracy.core.models:utilities.zcml')
        #TODO create test database

    def tearDown(self):
        registry = get_current_registry()
        graph = registry.getUtility(IGraphConnection)
        graph.clear()
        testing.tearDown()

    def test_create_content(self):
        #create a container
        from adhocracy.core.models.interfaces import IContainer
        from repoze.lemonade.content import create_content
        container0 = create_content(IContainer, name=u"g0")
        from zope.interface.verify import verifyObject
        self.assert_(verifyObject(IContainer, container0))
        self.assert_(container0.name == "g0")

    def create_child(self):
        #create a container
        from adhocracy.core.models.interfaces import IContainer
        from repoze.lemonade.content import create_content
        container1 = create_content(IContainer, name=u"g1")
        container1.text = u"text1"
        container1.save()
        self.assert_(container1.name == "g1")
        #it can have children
        container2 = create_content(IContainer, name=u"g2")
        container2.text = u"text2"
        container2.save()
        container1["g2"] = container2
        return (container1, container2)

    def test_set_item(self):
        container1, container2 = self.create_child()
        self.assert_(container1.has_key("g2"))
        self.assert_(container2.eid == container1["g2"].eid)
        self.assert_(not container1.has_key("not_available"))
        self.assertRaises(KeyError, container1.__getitem__, ("not_available"))
        #it can be a children
        self.assert_(container2.__parent__ is not None)
        self.assert_(container2.__parent__ == container1)

    def test_del_item(self):
        container1, container2 = self.create_child()
        del container1["g2"]
        self.assert_(not container1.has_key("g2"))
        self.assertRaises(KeyError, container1.__delitem__, ("g2"))
