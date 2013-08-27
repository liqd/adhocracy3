
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


Installation
------------

Requirements (Tested on Debian\Ubuntu,  64-Bit is mandatory):

1. python2.7
2. git
3. build-essentials
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

Run the application
--------------------

running the zodb server (in background) ::

    ./bin/runzeo -C etc/zeo.conf &

updating the object structure ::

    .bin/sd_evolve etc/development.ini

serving the sdidemo wsgi app using pserve ::

    ./bin/pserve etc/development.ini


Documentation ::
-----------------

build sphinx documentation ::

    cd ./docs
    make html
    xdg-open docs/build/html/index.html

