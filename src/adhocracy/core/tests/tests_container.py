import unittest

from pyramid import testing


class ModelTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.config.include('pyramid_zcml')
        import adhocracy.core.models
        self.config.load_zcml('adhocracy.core.models:utilities.zcml')
        #TODO create test database

    def tearDown(self):
        testing.tearDown()

    def test_object_hierarchy(self):
        from adhocracy.core.models.interfaces import IGraphConnection
        from pyramid.threadlocal import get_current_registry
        registry = get_current_registry()
        graph = registry.getUtility(IGraphConnection)
        #create a container
        container1 = graph.container.get_or_create("name", u"g1", name=u"g1")
        container1.text = u"text1"
        container1.save()
        assert(container1.name == "g1")
        #it can have children
        container2 = graph.container.get_or_create("name", u"g2", name=u"g2")
        container2.text = u"text2"
        container2.save()
        container1["g2"] = container2
        assert(container2 == container1["g2"])
        #it can be a children
        assert(container2.__parent__ is not None)
        assert(container2.__parent__ == container1)
        graph.clear()


