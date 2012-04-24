import unittest
from repoze.lemonade.testing import registerContentFactory
from pyramid import testing

from adhocracy.core.testing import setUp
from adhocracy.core.testing import tearDown
from adhocracy.core.testing import get_graph


class ModelTests(unittest.TestCase):

    def setUp(self):
        self.config = setUp()
        from adhocracy.core.models.adhocracyroot import adhocracyroot_factory
        registerContentFactory(adhocracyroot_factory, self._target_interface)
        self.graph = get_graph()

    def tearDown(self):
        tearDown()

    @property
    def _target_interface(self):
        from adhocracy.core.models.interfaces import IAdhocracyRoot
        return IAdhocracyRoot

    @property
    def _target_class(self):
        from adhocracy.core.models.adhocracyroot import AdhocracyRoot
        return AdhocracyRoot

    def _make_one(self):
        from repoze.lemonade.content import create_content
        content = create_content(self._target_interface)
        return content

    def test_factory_register(self):
        from repoze.lemonade.content import get_content_types
        self.assert_(self._target_interface in get_content_types())

    def test_create_content(self):
        content = self._make_one()
        self.assert_(content.__parent__ is None)
        self.assert_(content.__name__ == "")
        self.assert_(content.name == "adhocracyroot")
        from zope.interface.verify import verifyObject
        from adhocracy.core.models.interfaces import INode
        self.assert_(verifyObject(INode, content))
        self.assert_(verifyObject(self._target_interface, content))
        self.assert_(isinstance(content, self._target_class))

    def test_root_factory(self):
        from adhocracy.core import main
        request = testing.DummyRequest()
        settings = {}
        app = main({}, **settings)
        root = app.root_factory(request)
        self.assert_(root.eid == app.root_factory(request).eid)
        from adhocracy.core.security import SITE_ACL
        self.assert_(root.__acl__ == SITE_ACL)
        self.assert_(isinstance(root, self._target_class))


class ViewTests(unittest.TestCase):

    def test_default_view(self):
        from adhocracy.core.views.adhocracyroot import AdhocracyRootView
        from adhocracy.core.testing import Dummy
        request = testing.DummyRequest()
        context = Dummy()
        view = AdhocracyRootView(request, context)()
        self.assertEqual(view['project'], 'adhocracy.core')
