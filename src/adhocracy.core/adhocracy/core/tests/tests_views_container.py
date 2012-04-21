import unittest
from pyramid import testing

from adhocracy.core.testing import Browser
from adhocracy.core.testing import  ADHOCRACY_LAYER_FUNCTIONAL


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


class ViewFunctionalTests(unittest.TestCase):

    layer =  ADHOCRACY_LAYER_FUNCTIONAL

    def setUp(self):
        self.layer.setUp()
        app = ADHOCRACY_LAYER_FUNCTIONAL.make_wsgi_app()
        self.browser = Browser(wsgi_app=app)
        self.app = app

    def tearDown(self):
        self.layer.tearDown()

    def test_default_view(self):
        #add container object
        request = testing.DummyRequest()
        root =  self.app.root_factory(request)
        browser = self.browser
        from adhocracy.core.models.interfaces import IContainer
        from repoze.lemonade.content import create_content
        container0 = create_content(IContainer, name=u"g0")
        root["g0"] = container0
        #test object traversal
        browser.open('http://localhost/')
        browser.open('http://localhost/g0')
        self.assert_("container" in browser.contents)

    def test_measure_time_object_traversal(self):
        """Measure time object traversal level 10"""
        import datetime
        #add container objects
        request = testing.DummyRequest()
        root =  self.app.root_factory(request)
        browser = self.browser
        from adhocracy.core.models.interfaces import IContainer
        from repoze.lemonade.content import create_content
        container = root
        for x in  range(10):
            name = u"child"  + str(x)
            container[name] = create_content(IContainer, name=name)
            container = container[name]
        #test object traversal
        start = datetime.datetime.now()
        browser.open('http://localhost/child0/child1/child2/child3/child4/child5/child6/child7/child8/child9')
        self.assert_("container" in browser.contents)
        end = datetime.datetime.now()
        #echo measured time
        output = """\n\n\n
            Measure time object traversal level 10
            ======================================
            \n
            browser.open('http://localhost/child0/child1/child2/child3/child4/child5/child6/child7/child8/child9'):\n
            %s
            \n\n\n
        """ % (str(end - start))
        print output




