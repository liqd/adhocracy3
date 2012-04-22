import doctest
from doctest import DocFileSuite
import unittest

from adhocracy.core.testing import tearDown

try:
    import interlude
    """To use ipython shell in doctests: >>> interact( locals() )
        mind bug: https://github.com/collective/interlude/issues/2
    """
    interact = interlude.interact
except ImportError:
    interact = None


flags = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)

def tearDownDoctest(self, test=None):
    tearDown()

def globs():
    globs = {}
    if interact:
        globs["interact"] = interact
    return globs


class DoctestTestCase(unittest.TestCase):

    def __new__(self, test):
        return getattr(self, test)()

    @classmethod
    def test_suite(self):
        return DocFileSuite(
            "docs/supergraph.rst",
            "models.rst",
            tearDown=tearDownDoctest,
            globs = globs(),
            optionflags = flags
        )

