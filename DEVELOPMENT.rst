Development
============

Development
-----------

Check pep8 and pep257 bevore pushing commits::

    bin/flake8 src/adhocracy


Running the Testsuite
---------------------

with server setup and teardown (wsgi) ::

    bin/py.test -s src/adhocracy

run the test against already running server ::

    A3_TEST_SERVER=localhost:6541 bin/py.test src/adhocracy

The second case is interesting if you want to create a few objects in
a running backend in order to make the js front-end tests more
colorful.


haskell backend mockup
----------------------

Frontend test suite currently (2013-11-13) works best with haskell
backend:

    git clone https://github.com/zerobuzz/a3-backend-mockup/

Installation instructions will be added soon in README.md
