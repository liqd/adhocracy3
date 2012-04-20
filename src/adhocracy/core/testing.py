"""Helper classes for adhocracy.core test"""
import zope.testbrowser.wsgi
from pyramid.threadlocal import get_current_registry
from pyramid import testing

from adhocracy.core.models.interfaces import IGraphConnection


#Functional testing with zope.testbrowser

class Browser(zope.testbrowser.wsgi.Browser):
    """Simplify zope.testbrowser sessions"""

    def dc(self, filename="/tmp/test-output.html"):
        """Write html output to file"""
        open(filename, 'w').write(self.contents)


class AdhocracyFunctionalLayer(zope.testbrowser.wsgi.Layer):
    """Layer to setup the WSGI app"""

    def make_wsgi_app(self):
        from adhocracy.core import main
        return main({}, rexster_uri="http://localhost:8182/graphs/testgraph")

    def setUp(test, *args, **kwargs):
        config = testing.setUp(\
                    settings={'rexster_uri':"http://localhost:8182/graphs/testgraph"},
                    #do not hook global registry intro local pyramid registry
                    hook_zca=False)
        config.include('pyramid_zcml')
        config.load_zcml('adhocracy.core.models:utilities.zcml')
        #TODO start rexter

    def tearDown(self, test=None):
        registry = get_current_registry()
        graph = registry.getUtility(IGraphConnection)
        graph.clear()
        testing.tearDown()


ADHOCRACY_LAYER_FUNCTIONAL = AdhocracyFunctionalLayer()


#Various test helper stuff

class Dummy(dict):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

