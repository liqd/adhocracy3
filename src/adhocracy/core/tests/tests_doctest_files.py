import doctest
from doctest import DocFileSuite
import unittest
from adhocracy.core.testing import ADHOCRACY_LAYER_FUNCTIONAL
from adhocracy.core.testing import Browser


flags = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)

def globs():
    app = ADHOCRACY_LAYER_FUNCTIONAL.make_wsgi_app()
    globs =  {"browser" : Browser(wsgi_app=app),
              "app"     : app,
              "app_url" : "http://localhost",
             }
    return globs


class DoctestTestCase(unittest.TestCase):

    def __new__(self, test):
        return getattr(self, test)()

    @classmethod
    def test_suite(self):
        return DocFileSuite(
            "docs/supergraph.rst",
            "models.rst",
            #add here aditional testfiles
            setUp = ADHOCRACY_LAYER_FUNCTIONAL.setUp,
            tearDown = ADHOCRACY_LAYER_FUNCTIONAL.tearDown,
            globs = globs(),
            optionflags = flags
        )

