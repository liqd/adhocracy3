adhocracy.core README


Softwarestack (mometan):
=========================


Pyramid/Zope Python framework:
-------------------------------

http://docs.pylonsproject.org/en/latest/docs/pyramid.html
http://bluebream.zope.org/doc/1.0/manual/componentarchitecture.html
http://readthedocs.org/docs/pyramid_zcml/en/latest/narr.html


Graphdb backend:
-----------------

bulbs graphdb python interface, Object persistance:
        http://bulbflow.com

Rexster REST Server für blueprint graph databases:
        https://github.com/tinkerpop/rexster/wiki

blueprint graph database:
        http://neo4j.org
        
Gremlin graphdb Abfragesprache:
        https://github.com/tinkerpop/rexster-console.shop/gremlin/wiki/Getting-Started 



Install:
========


Get the source::

    $ hg clone ssh://hg@bitbucket.org/liqd/adhocracy_playground
    $ cd adhocracy_playground 

Create a virtualenv environment (python2.7)::

    $ virtualenv --no-site-packages .

Update setuptools::

    $ bin/easy_install -U setuptools

Run the buildout::

    $ bin/python bootstap.py
    $ bin/buildout 

Start the graph db::

    $ bin/rexster

Play with the graph db::
    
    $  bin/rexster-console 

Run Tests::

    $ bin/nosetests

Start adhocracy::

    $ bin/pserve etc/development.ini 
