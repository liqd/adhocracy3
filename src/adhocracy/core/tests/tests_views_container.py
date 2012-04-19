import unittest
from pyramid import testing


class ViewTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_default_view(self):
        from adhocracy.core.views.container import ContainerView
        from adhocracy.core.testing import Dummy
        request = testing.DummyRequest()
        context = Dummy()
        view = ContainerView(request, context)()
        self.assertEqual(view['project'], 'container')
