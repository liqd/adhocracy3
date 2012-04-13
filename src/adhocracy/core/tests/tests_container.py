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

    def test_content_factory(self):
        #create a container
        from adhocracy.core.models.interfaces import IContainer
        from repoze.lemonade.content import create_content
        container0 = create_content(IContainer, name=u"g0")
        assert(container0.name == "g0")

    def test_object_hierarchy(self):
        #create a container
        from adhocracy.core.models.interfaces import IContainer
        from repoze.lemonade.content import create_content
        container1 = create_content(IContainer, name=u"g1")
        container1.text = u"text1"
        container1.save()
        assert(container1.name == "g1")
        #it can have children
        container2 = create_content(IContainer, name=u"g2")
        container2.text = u"text2"
        container2.save()
        container1["g2"] = container2
        assert(container2 == container1["g2"])
        #it can be a children
        assert(container2.__parent__ is not None)
        assert(container2.__parent__ == container1)


