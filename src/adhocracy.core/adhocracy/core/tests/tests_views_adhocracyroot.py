import unittest
from pyramid import testing


class AdhocracyRootViewTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    #def test_default_view(self):
        #from adhocracy.core.views.adhocracyroot import AdhocracyRootView
        #from adhocracy.core.testing import Dummy
        #request = testing.DummyRequest()
        #context = Dummy()
        #view = AdhocracyRootView(request, context)()
        #self.assertEqual(view['project'], 'adhocracy.core')
