Coding style guideline
=======================

Common
-------

    * 4 spaces instead of tabs (must)
    * no trailing white space (must)

Python
------

testing
++++++++

    * 100% test coverage (must)
    * Test driven development with acceptance/functional, integration und unit test (should)
      testing guideline: http://pyramid.readthedocs.org/en/latest/narr/testing.html
      unit test examples substanced code, http://www.diveintopython.net/unit_testing/
      testdriven concept: http://www.c2.com/cgi/wiki?TestDrivenDevelopment)

code formatting
+++++++++++++++

    * pep8 (must)
    * pyflakes(must)
    * pylint(should)
    * mcabe(should)

    * Advances String Formatting pep3101 (must)
    
    * Single Quotes for strings except for docstrings (must)

docstring formatting
+++++++++++++++++++++

    * pep257 (must, bei tests und zope.Interface classes should)
    function definition sphinx style (input/output parameter raises) (should) http://pythonhosted.org/an_example_pypi_project/sphinx.html#function-definitions In Future use python 3 annotations for type checking and sphinx docu generation (for example: mypy interperter or https://pypi.python.org/pypi/sphinx_typesafe/0.2)

imports
+++++++

    * sort alphabetical, empty line between import .. and import .. from statements.
    * don`t use * to import everything from a module
    * use commas and newlines if you import multiple things from one moudle
    * dont catch ImportError to detect wheter a package is available or not, as it might hide circular import errors. Instead use pkgresources.getdistribution and catch DistributionNotFound. (http://do3.cc/blog/2010/08/20/do-not-catch-import-errors,-use-pkg_resources/)

javascript
-----------

    * jshint formatting rules (should) 
    * tslint: https://github.com/palantir/tslint (must)
      
css/compass
------------

    * csslint (must) (maybe exlcude some rules, TODO) https://github.com/stubbornella/csslint/wiki/Rules http://comcast.github.io/compass-csslint/

restructured text
++++++++++++++++++

    * Headline hierarchy: ===== ----- +++++ ~~~~~~~ ****** (must)
