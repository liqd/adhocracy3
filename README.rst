Welcome to Adhocracy-3!
=======================

Adhocracy 3 is a software for online participation.
It is an effort to rewrite Adhocracy 2 from scratch.
It aims to be a flexible framework and an easy customizable web application.


Status
------

Adhocracy-3 is in a very early stage: The software architecture design (the big picture) is mostly done. The code currently implements just some very basic database backend functionality with a test suite.

The current, stable and functional version is adhocracy-2:

* `adhocracy-2 website <https://adhocracy.de>`_
* `adhocracy-2 source code <https://bitbucket.org/liqd/adhocracy/src>`_



How to get involved
-------------------

We appreciate any form of cooperation: feedback, software design (review), API design, coding, community work, UI design, etc.. The main places where work on Adhocracy-3 is coordinated are:

* the `github repo <https://github.com/adhocracy/adhocracy-3>`_
* the `issue tracker <https://github.com/adhocracy/adhocracy-3/issues>`_ on github
* the `adhocracy-dev <http://lists.liqd.net/cgi-bin/mailman/listinfo/adhocracy-dev>`_ mailing list
* the #liqdem IRC channel (Use an IRC client or `visit the chat through your browser <http://webchat.freenode.net/?channels=liqdem>`_.)

Documentation
-------------

* `adhocracy-3 source code documentation and software architecture <http://adhocracy-3-playground.readthedocs.org/en/latest/index.html>`_

If you want to work on the documentation: It is written using `reStructuredText <http://docutils.sourceforge.net/rst.html>`_ inside the normal github repo. We will gladly accept pull requests.

build instructions
~~~~~~~~~~~~~~~~~~


Install virtualenvt::

    virtualenv --python=python2.7 --no-site-packages adhocracy-3
    source bin/activate

Install buildout::

    ./bin/easy_install -U distribute
    ./bin/python2.7 bootstrap.py

Install and generate the documentation::

    ./bin/buildout install sphinxbuilder
    .bin/sphinxbuilder
    xdg-open ./docs/build/html/index.html

Install the example adhocracy 3 implementation.
The following *may* work, but there may be broken dependencies left in the config files::

    ./bin/buildout install sphinxbuilder
