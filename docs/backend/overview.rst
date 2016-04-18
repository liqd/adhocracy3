Overview
========

The adhocracy backend is python framework to build a REST-API *backend* for
cms-like applications.

It was developed with the use cases and limitations of the policy drafing and
decision making tool `adhocracy2 <https://github.com/liqd/adhocracy>`_  and
the :doc:`../attic/supergraph` concept in mind.
The main focus lies on being *extensible*, allow modelling complex
*participation workflows* and *graph data structures* , and ensure *privacy*
and *data integrity*.

Note::

    The implementation is largely based on `substanced D`_, but has a lot
    of customization. One possible refactoring would be to make it a
    nice behaving REST-API extension.



You can work with the following concepts.

Resource Handling
-----------------

:term:`resource tree` to ease working with hierarchical data

URL Routing supports both, :term:`url dispatch` (fixed endpoints) and resource
hierarchy :term:`traversal` .

`Fine grained security system`:

    - permission protect operations (like 'view' a resource, sheet or field)
    - granted to :term:`role` s, which in turn are granted to :term:`principal` s.
    - local permission and roles: grants can be modified for every resource and
      its ancestors in the :term:`resource tree` .

`Workflows`:

  - `Finite State machine <https://en.wikipedia.org/wiki/Finite-state_machine>`_ for resources
  - change local permissions or run scripts on phase transition

`Resources`:

    - composed by a set of sheets (see :doc:`../attic/instance_modelling_example`)
    - runtime adding/removing of sheets possible
    - `open/close principal <https://en.wikipedia.org/wiki/Open/closed_principle>`_ for resource modelling

`Sheets`:

    - interface to for a specific resource behaviour:
      - api methods
      - data structure (:class:`colander.Schema`) with following field types:
         - data
         - metadata
         - computed data
         - references
         - backreferences
    - encapsulate data/reference storage

TODO:: Here it would be great to have a small overview of what sheets
do and how they work. Maybe give a concrete example of how they are
used in combination with Colander for the JSON serialization and how
they are used by the object factory. Also explain the link between
resources and sheets and how they reference each other could be
explain (with a diagram?).

`Versioned Resources`:

    - lineare history or allow forking and merging (not implemented)
    - data fields do never change

`References`:

    - allow complex non hierachical data structures
    - references (unidirectional) and backreferences (computed) between resource
      sheets

`Reference Update policies` if referenced Resource has new version:

    - No Update
    - Auto Update (new Version is created / reference is updated)
    - Optional Update, User has to comfirm (examle "like reference") (not implemented)


Data Storage
------------

`Auditing`:

    - every data/reference change is logged
    - no lost data for versioned Resources

`Optimistic Concurency Control`, atomic requests

    - no manual data lock or transaction handling needed

`Object database` for persistence storage and search

    - no sync problems, easy to debug

`alternative storages` for sheet data/references/search indexes (not implemented)

    - support databases with more sophisticaed reference graph/search features

`import/export scripts`

Code
----

`Type hinting`

    - play nice with code autocompletion (and static type checks).

`Extensible`:

    - `Pyramid extensibility <http://docs.pylonsproject.org/projects/pyramid/en/latest/designdefense.html#apps-are-extensible>`_
    - Resource/Sheet concept, type definitions are easy to customize in extension packages


