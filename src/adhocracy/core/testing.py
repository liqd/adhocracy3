"""Helper classes for adhocracy.core test"""
import zope.testbrowser.wsgi


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
        print("\n-----------------------------------------------------------------"
              "\n---    Setting up database test environment, please stand by. ---"
              "\n-----------------------------------------------------------------\n")
        #TODO start rexter

    def tearDown(self, test):
        pass


ADHOCRACY_LAYER_FUNCTIONAL = AdhocracyFunctionalLayer()


#Various test helper stuff

class Dummy(dict):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

