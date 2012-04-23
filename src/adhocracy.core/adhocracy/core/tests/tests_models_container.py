import unittest

from adhocracy.core.testing import setUp
from adhocracy.core.testing import tearDown
from adhocracy.core.testing import get_graph


class ModelTests(unittest.TestCase):

    def setUp(self):
        self.config = setUp()
        self.graph = get_graph()
        from adhocracy.core.models.container import container_factory
        from repoze.lemonade.testing import registerContentFactory
        registerContentFactory(container_factory, self._target_interface)

    def tearDown(self):
        tearDown()

    @property
    def _target_interface(self):
        from adhocracy.core.models.interfaces import IContainer
        return IContainer

    @property
    def _target_class(self):
        from adhocracy.core.models.container import Container
        return Container

    def _make_one(self, name=u"content"):
        from repoze.lemonade.content import create_content
        content = create_content(self._target_interface, name=name)
        return content

    def test_factory_register(self):
        from repoze.lemonade.content import get_content_types
        self.assert_(self._target_interface in get_content_types())

    def test_create_content(self):
        content = self._make_one()
        self.assert_(content.__parent__ is None)
        self.assert_(content.__name__ == "")
        self.assert_(content.name == "content")
        from zope.interface.verify import verifyObject
        from adhocracy.core.models.interfaces import INode
        self.assert_(verifyObject(INode, content))
        self.assert_(verifyObject(self._target_interface, content))
        self.assert_(isinstance(content, self._target_class))

        #container1.save()
        #self.assert_(container1.name == "g1")
        ##it can have children
        #container2 = create_content(IContainer, name=u"g2")
        #container2.text = u"text2"
        #container2.save()
        #return (container1, container2)

    #def test_child_factory(self):
        #container1, container2 = self.create_two_nodes()
        #from repoze.lemonade.content import create_content
        #from adhocracy.core.models.interfaces import IChild
        #child = create_content(IChild, parent=container1, child=container2, child_name=u"g2")
        #self.assert_(child.outV().eid == container2.eid)
        #self.assert_(child.inV().eid == container1.eid)


