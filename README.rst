
Adhocracy-3 Playground Para-Prototype on ZODB / Substance-D / Obviel
====================================================================

Softwarestack ::
----------------

- `substance <http://docs.pylonsproject.org/projects/substanced/en/latest>`_ (application framework/server)

- `Pyramid <http://pylonsproject.org>`_  (web framework)

- `hypatia <https://github.com/Pylons/hypatia>`_ (search)

- `colander <http://docs.pylonsproject.org/projects/colander/en/latest/>`_ (data schema)

- `deform <http://docs.pylonsproject.org/projects/deform/en/latest/>`_ (form generation)

- `ZODB <http://zodb.org>`_ (database)

- `buildout <http://www.buildout.org/en/latest/>`_ (build system)

- `python 3 <http://www.python.org>`_ (programming language)


Installation (server)
---------------------

Requirements (Tested on Debian\Ubuntu,  64-Bit is mandatory):

1. python2.7
2. git
3. build-essentials, libyaml-dev, python-dev
4. graphviz

checkout source code ::

    git clone https://github.com/adhocracy/adhocracy-3
    cd adhocracy-3
    git submodule init
    git submodule update

compile python 3 and PIL ::

    cd python
    python ./bootstrap.py
    ./bin/buildout
    cd ..
    ./python/python-3.3/bin/python --version

install adhocracy and the substance-d demo app ::

    ./python/python-3.3/bin/python ./bootstrap.py
    ./bin/buildout

Installation (obviel front-end)
-------------------------------

Requirements (Tested on Debian\Ubuntu):

1. git
2. build-essentials
3. npm (node package manager, install with debian)
    (for installing typescript; usage: npm -i <package name>@<package version>)
4. nodejs (>= 0.10)
    (for running typescript, FIXME: test debian stable version against tsc-0.9.1.1)
5. typescript (>= 0.9.1.1)
    (usage: "tsc --version")
6. bower (?)
7. grunt (?)

if you have not built the server backend (see above) yet ::

    git clone https://github.com/adhocracy/adhocracy-3
    cd adhocracy-3
    git submodule init
    git submodule update
    cd src/adhocracy/adhocracy/frontend/static/js/
    make
    open http://localhost:6541/static/frontend/proposal_workbench.html in browser


Run the application
-------------------

running the zodb server (in background) ::

    ./bin/runzeo -C etc/zeo.conf &

updating the object structure ::

    ./bin/sd_evolve etc/development.ini

serving the sdidemo wsgi app using pserve ::

    ./bin/pserve etc/development.ini


Documentation
-------------

build sphinx documentation ::

    cd ./docs
    make html
    xdg-open docs/build/html/index.html


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
