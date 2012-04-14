import unittest

from pyramid import testing


class ModelTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.config.include('pyramid_zcml')
        self.config.load_zcml('adhocracy.core.models:utilities.zcml')
        #TODO create test database

    def tearDown(self):
        testing.tearDown()

    def test_create_content(self):
        #create a container
        from adhocracy.core.models.interfaces import IContainer
        from repoze.lemonade.content import create_content
        container0 = create_content(IContainer, name=u"g0")
        from zope.interface.verify import verifyObject
        self.assert_(verifyObject(IContainer, container0))
        self.assert_(container0.name == "g0")

    def test_object_hierarchy(self):
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
        self.assert_(container2 == container1["g2"])
        #it can be a children
        self.assert_(container2.__parent__ is not None)
        self.assert_(container2.__parent__ == container1)
