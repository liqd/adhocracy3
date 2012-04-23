import unittest

from repoze.lemonade.testing import registerContentFactory

from adhocracy.core.testing import setUp
from adhocracy.core.testing import tearDown
from adhocracy.core.testing import get_graph
from adhocracy.core.testing import Person


class ModelChildRelationTests(unittest.TestCase):

    def setUp(self):
        self.config = setUp()
        self.graph = get_graph()
        from adhocracy.core.models.relations import child_factory
        registerContentFactory(child_factory, self._target_interface)
        self.graph.add_proxy("person", Person)

    def tearDown(self):
        tearDown()

    @property
    def _target_interface(self):
        from adhocracy.core.models.interfaces import IChild
        return IChild

    @property
    def _target_class(self):
        from adhocracy.core.models.relations import Child
        return Child

    def _make_one(self, parent=None, child=None, child_name=u""):
        from repoze.lemonade.content import create_content
        content = create_content(self._target_interface,\
                            parent=parent, child=child, child_name=child_name)
        return content

    def _make_dummy_node(self, name=u"node"):
        return self.graph.person.create(name=name)

    def test_factory_register(self):
        from repoze.lemonade.content import get_content_types
        self.assert_(self._target_interface in get_content_types())

    def test_create_relation(self):
        parent = self._make_dummy_node(name=u"parent")
        child = self._make_dummy_node(name=u"child")
        relation = self._make_one(parent=parent, child=child, child_name=u"childname")
        self.assert_(relation.child_name == u"childname")
        from zope.interface.verify import verifyObject
        self.assert_(verifyObject(self._target_interface, relation))
        self.assert_(isinstance(relation, self._target_class))
        self.assert_(relation.outV().eid == child.eid)
        self.assert_(relation.inV().eid == parent.eid)
