import unittest
from repoze.lemonade.testing import registerContentFactory
from pyramid import testing

from adhocracy.core.testing import setUp
from adhocracy.core.testing import tearDown
from adhocracy.core.testing import load_registry
from adhocracy.core.testing import get_graph


class AdhocracyRootTests(unittest.TestCase):

    def setUp(self):
        self.config = setUp()
        from adhocracy.core.models.adhocracyroot import adhocracyroot_factory
        registerContentFactory(adhocracyroot_factory, self._target_marker_interface)
        from adhocracy.core.models.adhocracyroot import AdhocracyRootLocationAware
        self.config.registry.registerAdapter(AdhocracyRootLocationAware)
        self.graph = get_graph()

    def tearDown(self):
        tearDown()

    @property
    def _target_marker_interface(self):
        from adhocracy.core.models.adhocracyroot import IAdhocracyRootMarker
        return IAdhocracyRootMarker

    def _make_one(self):
        from repoze.lemonade.content import create_content
        content = create_content(self._target_marker_interface)
        return content

    def test_factory_register(self):
        from repoze.lemonade.content import get_content_types
        self.assert_(self._target_marker_interface in get_content_types())

    def test_create_content(self):
        tx = self.graph.start_transaction()
        content = self._make_one()
        self.graph.stop_transaction(tx)
        from zope.interface.verify import verifyObject
        assert(self._target_marker_interface.providedBy(content))
        assert(verifyObject(self._target_marker_interface, content))

    def test_location_aware_adapter(self):
        tx = self.graph.start_transaction()
        content = self._make_one()
        self.graph.stop_transaction(tx)
        from zope.interface.verify import verifyObject
        from adhocracy.core.models.interfaces import ILocationAware
        content = ILocationAware(content)
        assert(verifyObject(ILocationAware, content))
        assert(content.__parent__ is None)
        assert(content.__name__ == "")
        from adhocracy.core.security import SITE_ACL
        assert(content.__acl__ == SITE_ACL)

    def test_root_factory(self):
        from adhocracy.core import main
        request = testing.DummyRequest()
        settings = {}
        app = main({}, **settings)
        tx = self.graph.start_transaction()
        root = app.root_factory(request)
        self.graph.stop_transaction(tx)
        self.assert_(root.get_dbId() == app.root_factory(request).get_dbId())
        self.assert_(self._target_marker_interface.providedBy(root))


class ModelFunctionalTests(unittest.TestCase):

    def setUp(self):
        config = setUp()
        self.registry = load_registry(config)

    def tearDown(self):
        tearDown()


#class ViewTests(unittest.TestCase):

    #def test_default_view(self):
        #from adhocracy.core.views.adhocracyroot import AdhocracyRootView
        #from adhocracy.core.testing import Dummy
        #request = testing.DummyRequest()
        #context = Dummy()
        #view = AdhocracyRootView(request, context)()
        #self.assertEqual(view['project'], 'adhocracy.core')
