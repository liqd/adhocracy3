import unittest
from pyramid import testing

from adhocracy.core.security import SITE_ACL


class ModelTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.config.include('pyramid_zcml')
        import adhocracy.core.models
        self.config.load_zcml('adhocracy.core.models:utilities.zcml')

    def tearDown(self):
        testing.tearDown()

    def test_acl_persistance(self):
        from adhocracy.core.models.interfaces import IGraphConnection
        from pyramid.threadlocal import get_current_registry
        registry = get_current_registry()
        graph = registry.getUtility(IGraphConnection)
        node = graph.adhocracyroot.get_or_create("name", u"testnode",
                                                  name=u"testnode")
        testlist = [[u"d",[[u"c"],[]], u"a"]]
        node.__acl__ = testlist
        node.save()
        node_ = graph.adhocracyroot.get_or_create("name", u"testnode",
                                                   name=u"testnode")
        assert(node_.__acl__ == testlist)


    def test_root_factory(self):
        from adhocracy.core import main
        request = testing.DummyRequest()
        settings = {}
        app = main({}, **settings)
        root =  app.root_factory(request)
        assert(root == app.root_factory(request))
        assert(root.__acl__ == SITE_ACL)
        assert(root.__parent__ is None)
        assert(root.__name__ is '')


class ViewTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_default_view(self):
        from adhocracy.core.views.adhocracyroot import AdhocracyRootView
        from adhocracy.core.testing import Dummy
        request = testing.DummyRequest()
        context = Dummy()
        view = AdhocracyRootView(request, context)()
        self.assertEqual(view['project'], 'adhocracy.core')
