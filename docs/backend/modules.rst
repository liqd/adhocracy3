Modules
=======

API and separation of responsibility
------------------------------------

*responsibility*
    (means reason to change code if functionality changes)
    should lay at one single point of code (packages/modules in this case),
    see also :doc:`../coding_guides/refactore_guidelines`.

*layer*
    loosly group of modules that follow these rules:
    adhocracy_core.evolution
    * must not import from upper layer
    * should not import from same layer
    * may import interfaces from all layers
    * may import from lower layer

.. rubric:: Application Layer

.. autosummary::

    adhocracy_core

.. rubric:: Frontend Views, Client Communication Layer

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

.. rubric:: Registry, Factories, Access to Metadata Layer

.. autosummary::

    adhocracy_core.content
    adhocracy_core.changelog

.. rubric:: Resource Handling Layer

.. autosummary::

    adhocracy_core.resources
    adhocracy_core.resources.base
    adhocracy_core.resources.simple
    adhocracy_core.resources.pool
    adhocracy_core.resources.item
    adhocracy_core.resources.itemversion
    adhocracy_core.resources.root
    adhocracy_core.resources.principal
    adhocracy_core.resources.subscriber
    adhocracy_core.sheets
    adhocracy_core.catalog
    adhocracy_core.catalog.adhocracy
    adhocracy_core.catalog.subscriber
    adhocracy_core.authorization
    adhocracy_core.messaging
    adhocracy_core.graph
    adhocracy_core.evolution
    adhocracy_core.workflows

.. rubric:: Interfaces, Utils Layer

.. autosummary::

    adhocracy_core.interfaces
    adhocracy_core.utils
    adhocracy_core.events
    adhocracy_core.schema
    adhocracy_core.exceptions

.. rubric:: Other stuff

.. autosummary::

    adhocracy_core.scaffolds
    adhocracy_core.scripts
    adhocracy_core.stats
    adhocracy_core.auditing
    adhocracy_core.registry
    adhocracy_core.renderers
    adhocracy_core.templates

TODO: move all scripts to adhocracy_core.scripts


`Substanced` dependencies
-------------------------

   * :mod:`substanced.evolution` (migration, see :mod:`adhocracy_core.evolution`)
   * :mod:`substanced.catalog` (search, extended by :mod:`adhocracy_core.catalog`)
   * :mod:`substanced.workflow` (state machines mapped to resource types, extended by :mod:`adhocracy_core.workflows`)
   * :mod:`substanced.content` (provide content types factories, extendend by :mod:`adhocracy_core.content`)
   * :mod:`substanced.objectmap` (reference resources, extented by :mod:`adhocracy_core.graph`)
   * :mod:`substanced.folder` (Persistent implemention for :class:`adhocracy_core.interfaces.IPool` resources)

Extend/Customize
----------------

* must follow `Rules for extensible pyramid apps <http://docs.pylonsproject.org/projects/pyramid/en/master/narr/extending.html>`_:
  configuration, configuration extentensions, view/asset overriding, event subscribers.
  Use :term:`imperative-configuration` , except for views :term:`configuration-declaration` .

* may use the underlaying `zope component <http://docs.zope.org/zope.component/narr.html>`_ architecture
  provided by the :term:`application registry` directly.
  may not use the global `zope component` registry, see also `ZCA in pyramid <http://docs.pylonsproject.org/projects/pyramid/en/master/narr/extconfig.html>`_.

* must follow rules for module `layer` (see above)

* make code dependencies pluggable to allow different implementations
  (other authentication, references storage, data storage, search, ..)
  Dependencies should have an interface to describe public methods.

* override resource/sheet metadata, see :mod:`adhocracy_sample`

.. note::

 You can use the script `bin/ad_check_forbidden_imports` to list suspicious imports


Naming conventions
------------------

* Non-versionable resources types are named resource.x.IX with a sheet named
  sheet.x.IX.

* Versionable resources types are named resource.x.IXVersion (inherits from IITemVersion)
  with a sheet named sheet.x.IX. They belong to the container (parent) resource
  type called resource.x.IX (inherits from IItem).

* Resource/sheet types to express RDF like statements are named after the `verb`,
  for example: IRate.
