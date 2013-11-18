
Adhocracy-3 Playground Para-Prototype on ZODB / Substance-D / Obviel
====================================================================

Softwarestack ::
----------------

server:

- `substance <http://docs.pylonsproject.org/projects/substanced/en/latest>`_ (application framework/server)

- `Pyramid <http://pylonsproject.org>`_  (web framework)

- `hypatia <https://github.com/Pylons/hypatia>`_ (search)

- `colander <http://docs.pylonsproject.org/projects/colander/en/latest/>`_ (data schema)

- `deform <http://docs.pylonsproject.org/projects/deform/en/latest/>`_ (form generation)

- `ZODB <http://zodb.org>`_ (database)

- `buildout <http://www.buildout.org/en/latest/>`_ (build system)

- `python 3 <http://www.python.org>`_ (programming language)

client (frontend):

- `javascript` (programming language)

- `typescript` <http://www.typescriptlang.org/> (module system)

- `obviel` <http://www.obviel.org> (application framework)

- `robotframework` <http://robotframework.org/> (acceptance and frontend tests)

Installation with Vagrant virtual machine
-----------------------------------------

Requirements:

1. virtualbox: https://virtualbox.org/wiki/Downloads
2. vagrant: http://docs.vagrantup.com/v2/installation/index.html

create virtual machine and login:

    wget https://raw.github.com/adhocracy/adhocracy-3/master/Vagrantfile
    vagrant up
    vagrant ssh
    cd /home/vagrant/

proceed with installing the server
TODO: make the automatic setup work (vagrant shell provisioner or salt)


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

install adhocracy ::

    ./python/python-3.3/bin/python ./bootstrap.py
    ./bin/buildout

update your shell environment::

    ./source source_env

install javascript front-end ::

    cd src/adhocracy/adhocracy/frontend/static/js/
    make

install robotframework for accpetance testing ::

    cd robotframework/
    python2.7 bootstrap.py
    bin/buildout 


Run the application
-------------------

running the zodb server (in background) ::

    ./bin/runzeo -C etc/zeo.conf &

updating the object structure ::

    ./bin/sd_evolve etc/development.ini

serving the sdidemo wsgi app using pserve ::

    ./bin/pserve etc/development.ini

open the javascript front-end with your web browser ::

    xdg-open http://localhost:6541/frontend_static/proposal_workbench.html


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


haskell backend mockup
----------------------

Frontend test suite currently (2013-11-13) works best with haskell
backend:

    git clone https://github.com/zerobuzz/a3-backend-mockup/

Installation instructions will be added soon in README.md



