import unittest

from repoze.lemonade.testing import registerContentFactory

from adhocracy.core.testing import setUp
from adhocracy.core.testing import tearDown
from adhocracy.core.testing import get_graph


class ModelChildRelationTests(unittest.TestCase):

    def setUp(self):
        self.config = setUp()
        self.graph = get_graph()
        from adhocracy.core.models.utilities import child_factory
        from adhocracy.core.models.interfaces import IChild
        registerContentFactory(child_factory, IChild)
        from adhocracy.core.models.utilities import container_factory
        from adhocracy.core.models.interfaces import IContainer
        registerContentFactory(container_factory, IContainer)

        from adhocracy.core.models.interfaces import INode
        self.config.registry.registerAdapter(self._target_class(), (INode,),\
                                             self._target_interface())

    def tearDown(self):
        tearDown()

    def _target_interface(self):
        from adhocracy.core.models.interfaces import IChildsDict
        return IChildsDict

    def _target_class(self):
        from adhocracy.core.models.adapters import NodeChildsDictAdapter
        return NodeChildsDictAdapter

    def _make_dummy_node(self, name=u"node"):
        from adhocracy.core.models.interfaces import IContainer
        from repoze.lemonade.content import create_content
        content = create_content(IContainer, name=name)
        return content

    def test_create_adapter(self):
        parent = self._make_dummy_node()
        adapter = self._target_interface()(parent)
        from adhocracy.core.models.adapters import NodeChildsDictAdapter
        self.assert_(isinstance(adapter, NodeChildsDictAdapter))
        from zope.interface.verify import verifyObject
        self.assert_(verifyObject(self._target_interface(), adapter))
        self.assert_(adapter.context == parent)

    def test_interface_inheritance(self):
        parent = self._make_dummy_node()
        from pyramid_adoptedtraversal.interfaces import IChildsDictLike
        self.assert_(self._target_interface()(parent) == IChildsDictLike(parent))

    def test_set_item(self):
        parent = self._make_dummy_node(name=u"parent")
        child = self._make_dummy_node(name=u"child")
        parent_adapter = self._target_interface()(parent)
        parent_adapter["g2"] = child
        self.assertIsNotNone(parent)
        self.assertIsNotNone(child)
        self.assertEquals([parent.eid],
            map (lambda x: x.eid, list(child.outV("child"))))
        self.assert_(parent_adapter.has_key("g2"))
        self.assert_(child.eid == parent_adapter["g2"].eid)
        self.assert_(not parent_adapter.has_key("not_available"))
        self.assertRaises(KeyError, parent_adapter.__getitem__, ("not_available"))
        self.assert_(parent.__parent__ is None)
        self.assert_(child.__parent__ is not None)
        self.assert_(child.__parent__.eid == parent.eid)

    def test_del_item(self):
        parent = self._make_dummy_node(name=u"parent")
        child = self._make_dummy_node(name=u"child")
        parent_adapter = self._target_interface()(parent)
        parent_adapter["g2"] = child
        del parent_adapter["g2"]
        self.assert_(not parent_adapter.has_key("g2"))
