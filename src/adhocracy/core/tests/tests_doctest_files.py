import doctest
from doctest import DocFileSuite
import unittest


flags = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)
globs = {}


class DoctestTestCase(unittest.TestCase):

    def __new__(self, test):
        return getattr(self, test)()

    @classmethod
    def test_suite(self):
        return DocFileSuite(
            "test.rst",
            #add here aditional testfiles
            globs = globs,
            optionflags = flags
        )

