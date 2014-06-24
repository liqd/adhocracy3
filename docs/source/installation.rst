Installation
==============

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


Installation (backend)
---------------------

Requirements (Tested on Debian\Ubuntu,  64-Bit is mandatory):

1. python3
2. git
3. build-essential libyaml-dev python3-dev libncurses5-dev python-setuptools
4. graphviz
5. ruby-dev

checkout source code ::

    git clone ssh://git@foucault.liqd.net:22012/a3.git
    cd a3
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

    source ./source_env

Installation (frontend)
------------------------

install javascript front-end ::

    cd src/adhocracy/adhocracy/frontend/static/js/
    make
    cd ../../../../../..  # (or 'cd -')

Documentation
-------------

build sphinx documentation ::

    bin/sphinx_build_adhocracy
    xdg-open docs/build/html/index.html  # (alternatively, cut & paste the url into your browser)

Run the application
-------------------

running the zodb server (in background) ::

    ./bin/runzeo -C etc/zeo.conf &

updating the object structure ::

    ./bin/sd_evolve etc/development.ini

serving the sample wsgi app using pserve ::

    ./bin/pserve etc/development.ini

open the javascript front-end with your web browser ::

    xdg-open http://localhost:6541/frontend_static/root.html


