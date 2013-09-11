
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

Installation (obviel front-end)
-------------------------------

Requirements (Tested on Debian\Ubuntu):

1. git
2. build-essentials
3. nodejs (build it from github if you are using testing; the debian packages are broken as of Tue Sep  3 14:52:03 CEST 2013)
4. bower, grunt

if you have not built the server backend (see above) yet ::

    git clone https://github.com/adhocracy/adhocracy-3
    cd adhocracy-3
    git submodule init
    git submodule update
    cd src/frontend

compile jquery-1.7.2 ::

    # jquery 1.10.2 throws some poorly analysed exceptions when playing with obviel traject
    # (hum...  Makefile crash?  Ignore commands in this paragraph; I'll just leave jquery-1.7.2.js in src/frontend/ for now.)
    cd submodules/jquery
    git checkout tags/1.7.2
    make jquery
    cd ../../

compile jquery-1.10.2 ::

    cd submodules/jquery
    git checkout tags/1.10.2
    follow procedure in README.md
    cd ../../

now it gets a little muddy ::

    start a web browser that serves files in src/frontend/, and load
    /index.html from it.  what that page does is still changing a lot.
    these installation instructions will get updated once things get
    more stable.

Run the application
-------------------

running the zodb server (in background) ::

    ./bin/runzeo -C etc/zeo.conf &

updating the object structure ::

    ./bin/sd_evolve etc/development.ini

serving the sdidemo wsgi app using pserve ::

    ./bin/pserve etc/development.ini


Documentation ::
-----------------

build sphinx documentation ::

    cd ./docs
    make html
    xdg-open docs/build/html/index.html


Development ::
-----------------

Check pep8 and pep257 bevore pushing commits::

    bin/flake8 src/adhocracy
