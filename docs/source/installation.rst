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
----------------------

Requirements (Tested on Debian\Ubuntu,  64-Bit is mandatory):

1. python3 (FIXME probably not required?)
2. git
3. build-essential libbz2-dev libyaml-dev python3-dev libncurses5-dev python-virtualenv python-setuptools
4. graphviz
5. ruby-dev

checkout source code ::

    git clone ssh://git@foucault.liqd.net:22012/a3.git
    cd a3
    git submodule update --init

compile python 3 and PIL ::

    cd python
    python ./bootstrap.py
    ./bin/buildout
    ./bin/install-links
    cd ..

install adhocracy ::

    ./bin/python3.4 ./bootstrap.py
    ./bin/buildout

update your shell environment::

    source ./source_env


Documentation
-------------

build sphinx documentation ::

    bin/sphinx_build_adhocracy
    xdg-open docs/build/html/index.html  # (alternatively, cut & paste the url into your browser)


Run the application
-------------------

Start supervisor (which manages the ZODB database, the Pyramid application
and the Autobahn websocket server)::

    ./bin/supervisord

Check that everything is running smoothly::

    ./bin/supervisorctl status


Open the javascript front-end with your web browser::

    xdg-open http://localhost:6541/

Shutdown everything nicely::

    ./bin/supervisorctl shutdown
