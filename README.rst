
Adhocracy-3 Playground Para-Prototype on ZODB / Substance-D / Obviel
====================================================================


Installation
------------

Requirements (Tested on Debian\Ubuntu):

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

running the zodb server (in background) ::

    ./bin/runzeo -C etc/zeo.conf &

serving the sdidemo wsgi app using pserve ::

    ./bin/pserve etc/development.ini

build sphinx documentation ::

    cd ./docs
    make html
    xdg-open docs/build/html/index.html
