Backend Structure
-----------------

The backend consists of:

adhocracy_core
   application framework to provide a rest api for participation process platforms

adhocracy_sample
   examples how to customize resource/sheet types

adhocracy_mercator:
   configuration and extensions to run the mercator rest api application


Usage of external dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Webframework `pyramid <http://docs.pylonsproject.org/docs/pyramid/en/latest/index.html>`_

    * object `traversal <http://docs.pylonsproject.org/docs/pyramid/en/latest/narr/traversal.html>`_
      and `authorization <http://docs.pylonsproject.org/docs/pyramid/en/latest/narr/security.html>`_
      based on resource location

    * `configuration <http://pyramid-cookbook.readthedocs.org/en/latest/configuration/whirlwind_tour.html>`_
      imperative  prefered

    * zope component architecture may be used directly if usefull
      (`pyramid zca <http://docs.pylonsproject.org/docs/pyramid/en/latest/narr/zca.html>`_,
      `zope.interfaces <http://docs.zope.org/zope.interface>`_)

* Persistence `zodb <http://zodborg.readthedocs.org/en/latest/index.html>`_

   * file system storage (`relstorage <https://pypi.python.org/pypi/RelStorage/>`_
     has advantages for productive installation but is currently not supported for python 3)

   * Different or additional persistence should be possible.
     To make this easier code relying on persistent object attributes
     should specify them with interfaces (like :class:`adhocray_core.interfaces.IResource`).
     Also make dependency modules pluggable.

* Application server `substanced <http://docs.pylonsproject.org/projects/substanced/en/latest>`_

   * concept: content types are sets of sheets to follow open close principle.
     `resource types` (:class:`adhocracy_core.interfaces.IResource`) mapped to `sheet types`
     and a generic class to create the persistent object hierarchy.
     `sheet types` (:class:`adhocracy_core.interfaces.ISheet`) mapped
     to data structures (:class:`colander.Schema`) and generic class that
     encapsulates persistent data access.
     (For performance reasons / implementation issues some code uses
     direct attribute access to retrieve data.)
   * :mod:`substanced.evolution` (migration, see :mod:`adhocracy_core.evolution`)
   * :mod:`substanced.catalog` (search, extended by :mod:`adhocracy_core.catalog`)
   * :mod:`substanced.workflow` (state machines mapped to resource types)
   * :mod:`substanced.content` (provide content types factories, extendend by :mod:`adhocracy_core.content`)
   * :mod:`substanced.objectmap` (reference resources, extented by :mod:`adhocracy_core.graph`)
   * :mod:`substanced.scripts` (command line utilities)
   * :mod:`substanced.folder` (Persistent implemention for :class:`adhocracy_core.interfaces.IPool` resources)

* Data structures / validation `colander <http://colander.readthedocs.org/en/latest/>`_


Extend/Customize modules
~~~~~~~~~~~~~~~~~~~~~~~~

* use `pyramid extension hooks <http://docs.pylonsproject.org/docs/pyramid/en/latest/narr/extending.html>`_:
  configuration, view overriding, assets overriding, event subscribers.

* make modules/packages pluggable dependencies to allow different implementations
  (other authentication, references storage, sheet data storage, search, ..)

* override resource/sheet metadata, see :mod:`adhocracy_sample`



Modules API and separation of responsibility
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. rubric:: Application Level

.. autosummary::

    adhocracy_core

.. rubric:: Client communication Level

.. autosummary::

    adhocracy_core.rest
    adhocracy_core.rest.views
    adhocracy_core.rest.batchview
    adhocracy_core.rest.schemas
    adhocracy_core.rest.subscriber
    adhocracy_core.rest.exceptions
    adhocracy_core.caching
    adhocracy_core.authentication
    adhocracy_core.websockets


.. rubric:: Access to data and meta data Level

.. autosummary::

    adhocracy_core.content

.. rubric:: Data, Authorization, Principals Level

.. autosummary::

    adhocracy_core.resources
    adhocracy_core.resources.resource
    adhocracy_core.resources.simple
    adhocracy_core.resources.pool
    adhocracy_core.resources.item
    adhocracy_core.resources.itemversion
    adhocracy_core.resources.tag
    adhocracy_core.resources.root
    adhocracy_core.resources.principal
    adhocracy_core.resources.subscriber
    adhocracy_core.sheets
    adhocracy_core.catalog
    adhocracy_core.catalog.adhocracy
    adhocracy_core.catalog.subscriber
    adhocracy_core.evolution
    adhocracy_core.authorization
    adhocracy_core.messaging

.. rubric:: Shared base Level

.. autosummary::

    adhocracy_core.graph
    adhocracy_core.interfaces
    adhocracy_core.utils
    adhocracy_core.events
    adhocracy_core.schema
    adhocracy_core.exceptions

.. rubric:: Other stuff

.. autosummary::

    adhocracy_core.scaffolds
    adhocracy_core.scripts


TODO: mark pluggable dependency modules

TODO: move scripts to adhocracy_core.scripts

Modules import rules
~~~~~~~~~~~~~~~~~~~~

* must not import from upper level

* should not import from same level

  (pluggable: must not have imports from other modules or to other pluggable modules)

  (pluggable: must have interface for public methods)

* may import from bottom level

* may import interfaces

* you can use `bin/check_forbidden_imports` to list suspicious imports  # TODO update script


History Notes
~~~~~~~~~~~~~

We started with the plan to port adhocracy2 to pyramid.
This become a long discussion how to implement something completely new
based on fancy graph data structures :doc:`../attic/index.rst`.

We compared multiple framework/database combinations, here in more or
less chronical order:

      * pyramid/kotti/ sql
      * pyramid/bulbflow/ neo4j
      * pyramid/rexster/ neo4j
      * cubicweb/ rdf storage
      * Zope Toolkit/ ZODB
      * pyramid/substanced/ ZODB

Doing this we had the following in mind:

      * python 3 support
      * active community and good documentation
      * good extensibility -> zope component style architecture
      * fast references to python objects and complex reference queries
      * one system to search & store python objects and references (prevent synchronisation issues)
      * transactions
      * object hierarchy / traversal
      * workflows, permissions based on resource location

We did a prototype with a graph database and dropped it mainly because the
python support and transaction features were too much cutting edge.
So we came to the ZODB database. It is stable and can do python object
references in a very simple way because it is an object database.
That lead to the substanced framework that already provides solutions for
multiple other things we wanted to implement.

