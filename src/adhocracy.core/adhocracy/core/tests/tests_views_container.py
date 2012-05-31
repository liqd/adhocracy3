import unittest
from zope import interface
from zope import component
from pyramid import testing

from adhocracy.core.testing import setUpFunctional
from adhocracy.core.testing import load_registry
from adhocracy.core.testing import setUp
from adhocracy.core.testing import tearDown


class ContainerViewTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_default_view(self):
        from adhocracy.core.views.container import ContainerView
        from adhocracy.core.models.container import IContainerMarker
        from adhocracy.core.testing import Dummy
        request = testing.DummyRequest()
        context = Dummy()
        interface.alsoProvides(context, IContainerMarker)
        view = ContainerView(request, context)()
        self.assertEqual(view['project'], 'container')


class ContainerViewFunctionalTests(unittest.TestCase):

    def setUp(self, **kwargs):
        tools = setUpFunctional()
        self.browser = tools["browser"]
        self.app = tools["app"]
        self.root = self.app.root_factory(None)

        from adhocracy.dbgraph.embeddedgraph import get_graph
        self.graph = get_graph()
        global_registry = component.getGlobalSiteManager()
        from adhocracy.core.models.relations import NodeChildsDictAdapter
        global_registry.registerAdapter(NodeChildsDictAdapter)

        from repoze.lemonade.testing import registerContentFactory
        from adhocracy.core.models.references import child_factory
        from adhocracy.core.models.references import IChildMarker
        registerContentFactory(child_factory, IChildMarker)

        from adhocracy.core.models.container import container_factory
        from adhocracy.core.models.container import IContainerMarker
        registerContentFactory(container_factory, IContainerMarker)

        from adhocracy.core.models.references import Child
        global_registry.registerAdapter(Child)

    def tearDown(self):
        tearDown()

    def test_default_view(self):
        #add container object
        root = self.app.root_factory(None)
        from adhocracy.core.models.interfaces import IChildsDict
        rootchilds = IChildsDict(root)
        tx = self.graph.start_transaction()
        from repoze.lemonade.content import create_content
        from adhocracy.core.models.container import IContainerMarker
        content = create_content(IContainerMarker)
        rootchilds["child"] = content
        self.graph.stop_transaction(tx)

        #test object traversal
        self.browser.open("http://localhost:6543/child")
        assert("container" in self.browser.contents)

    def test_measure_time_object_traversal(self):
        #"""Measure time object traversal level 10"""
        import datetime
        #add container object
        tx = self.graph.start_transaction()
        root = self.app.root_factory(None)
        from adhocracy.core.models.interfaces import IChildsDict
        from adhocracy.core.models.container import IContainerMarker
        from repoze.lemonade.content import create_content
        container = root
        for x in range(10):
            name = u"child" + str(x)
            child = create_content(IContainerMarker)
            IChildsDict(container)[name] = child
            container = IChildsDict(container)[name]
        self.graph.stop_transaction(tx)

        ##test object traversal
        start = datetime.datetime.now()
        self.browser.open('http://localhost:6543/child0/child1/child2/' +
                          'child3/child4/child5/child6/child7/child8/child9')
        end = datetime.datetime.now()
        #echo measured time
        output = """\n\n\n
            Measure time object traversal level 10 - 1. run
            ===============================================
            \n
            browser.open('http://localhost/child0/../child8/child9'):\n
            %s
            \n\n\n
        """ % (str(end - start))
        print output
        start = datetime.datetime.now()
        self.browser.open('http://localhost:6543/child0/child1/child2/' +
                          'child3/child4/child5/child6/child7/child8/child9')
        end = datetime.datetime.now()
        #echo measured time
        output = """\n\n\n
            Measure time object traversal level 10 - 2. run
            ================================================
            \n
            browser.open('http://localhost/child0/../child8/child9'):\n
            %s
            \n\n\n
        """ % (str(end - start))
        print output
        start = datetime.datetime.now()
        self.browser.open('http://localhost:6543/child0/child1/child2/' +
                          'child3/child4/child5/child6/child7/child8/child9')
        end = datetime.datetime.now()
        #echo measured time
        output = """\n\n\n
            Measure time object traversal level 10 - 3. run
            ================================================
            \n
            browser.open('http://localhost/child0/../child8/child9'):\n
            %s
            \n\n\n
        """ % (str(end - start))
        print output
