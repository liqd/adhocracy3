from pyramid import testing

import unittest


class IncludemeFunctionalTest(unittest.TestCase):

    def setUp(self):
        from adhocracy.testing import settings_functional
        self.config = testing.setUp(settings=settings_functional())
        self.config.include("adhocracy")

    def tearDown(self):
        testing.tearDown()

    def test_test(self):
        import ipdb; ipdb.set_trace()
