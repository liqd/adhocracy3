Python Guidelines
=================

Testing
-------

* 100% unit test coverage (must)
* Test driven development with functional, integration and unit test (should)
  * test driven concept: http://en.wikipedia.org/wiki/Test-driven_development
  * programming work flow: functional/integration test <-> unit tests <-> code
  * use `pytest <http://pytest.org/>`_ fixtures, functional tests have the
   `functional` marker, integration are using a fixture called `integration`.

Imports
-------

* one import per line
* don't use * to import everything from a module
* don't use relative import paths
* dont catch ``ImportError`` to detect wheter a package is available or not, as
  it might hide circular import errors. Instead use
  ``pkgresources.getdistribution`` and catch ``DistributionNotFound``.
  (http://do3.cc/blog/2010/08/20/do-not-catch-import-errors,-use-pkg_resources/)
* must not import from upper level
 * should not import from same level
   (pluggable: must not have imports from other modules or to other pluggable modules)
   (pluggable: must have interface for public methods)
* may import from bottom level
* may import interfaces
* you can use `bin/check_forbidden_imports` to list suspicious imports  # TODO update script

Code formatting
---------------

* 4 spaces instead of tabs (must)
* no trailing white space (must)

* `pep8 <http://legacy.python.org/dev/peps/pep-0008/>`_ (must)
* pyflakes (must)
* pylint (should)
* mcabe (should)

* Advances String Formatting `pep3101 <http://legacy.python.org/dev/peps/pep-3101/>`_ (must)

* Single Quotes for strings except for docstrings (must)
  

Docstring formatting
--------------------

* pep257 (must, bei tests und zope.Interface classes should)
* python 3 type annotation (must) according to
  https://pypi.python.org/pypi/sphinx_typesafe
* javadoc-style parameter descriptions, see
  http://sphinx-doc.org/domains.html#info-field-lists (should)
* example::

    def methodx(self, a: dict, flag=False) -> str:
        """Do something.

        :param a: description for a
        :param flag: description for flag
        :return: something special
        :raise ValueError: if a is invalid
        """
