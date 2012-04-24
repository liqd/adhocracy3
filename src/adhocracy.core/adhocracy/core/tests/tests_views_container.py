import unittest
from pyramid import testing

from adhocracy.core.testing import setUpFunctional
from adhocracy.core.testing import load_registry
from adhocracy.core.testing import setUp
from adhocracy.core.testing import get_graph
from adhocracy.core.testing import tearDown


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

    def setUp(self, **kwargs):
        self.config = setUp()
        self.registry = load_registry(self.config)

    def tearDown(self):
        tearDown()

    def test_default_view(self):
        #add container object
        #from repoze.lemonade.content import create_content
        #from adhocracy.core.models.interfaces import IAdhocracyRoot
        #root = create_content(IAdhocracyRoot)
        #from adhocracy.core.models.interfaces import IContainer
        #content = create_content(IContainer, name=u"child")
        #from adhocracy.core.models.interfaces import IChildsDict
        #IChildsDict(root)["child"] = content


        #test object traversal
        from adhocracy.core.testing import setUpFunctional
        tools = setUpFunctional()
        browser = tools["browser"]
        browser.open("http://localhost:6543")

        #functional testing not working right at the moment - joka

        #self.__dict__.update(setUpFunctional())
        #self.browser.open('http://localhost:6543')
        #self.browser.open('http://localhost:6543/child')
        #self.assert_("container" in self.browser.contents)

    #def test_measure_time_object_traversal(self):
        #"""Measure time object traversal level 10"""
        #import datetime
        ##add container object
        #from repoze.lemonade.content import create_content
        #from adhocracy.core.models.interfaces import IAdhocracyRoot
        #root = create_content(IAdhocracyRoot)

        #from adhocracy.core.models.interfaces import IContainer
        #from adhocracy.core.models.interfaces import IChildsDict
        #container = root
        #for x in  range(10):
            #name = u"child"  + str(x)
            #child = create_content(IContainer, name=name)
            #IChildsDict(container)[name] = child
            #container = IChildsDict(container)[name]

        ##test object traversal
        #start = datetime.datetime.now()
        #self.browser.open('http://localhost:6543/child0/child1/child2/child3/child4/child5/child6/child7/child8/child9')
        #self.assert_("container" in self.browser.contents)
        #end = datetime.datetime.now()
        ##echo measured time
        #output = """\n\n\n
            #Measure time object traversal level 10
            #======================================
            #\n
            #browser.open('http://localhost/child0/child1/child2/child3/child4/child5/child6/child7/child8/child9'):\n
            #%s
            #\n\n\n
        #""" % (str(end - start))
        #print output
