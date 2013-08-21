
Adhocracy-3 Playground Para-Prototype on ZODB / Substance-D / Obviel
====================================================================


Installation
------------

Tested on Debian.  Requirements:

1. python2.7
2. git
3. build-essentials

checkout source code ::
    git clone https://github.com/adhocracy/adhocracy-3
    cd adhocracy-3
    git submodules init

compile python and PIL ::
    cd python
    python ./bootstrap.py
    ./bin/buildout

