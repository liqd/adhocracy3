Adhocracy 3 - application/framework for online participation projects
=====================================================================

.. note::

    This isn't meant for general consumption at this stage. Many expected
    things do not work yet!


What is adhocracy?
------------------

Adhocracy 3 aims to be a:

*   python framework to build a REST-API *backend* for cms-like applications
    with a focus on `participation processes` and `collaborative text work`.

*   javascript framework to build SinglePageApplication *frontends*.

It comes with these features out of the box:

*   Generic :doc:`../api/rest_api` based on the following concepts:

    *   `Hypermedia REST API`: loose coupling frontend/backend, no fixed endpoints,
        (only half implemented, possible future:`A3 Hypermedia REST-API <http://www.jokasis.de/docs/api_talk/html/>`_)

    *   `Supergraph`: Resources are versioned and build non hierachical data structures with other Resources,
        Versions never change, see :doc:`../attic/supergraph` and :doc:`../attic/no_patches`.
        (only half implemented, Problem: build a usable REST-API on top of this concept).

*   Generic `API Specifiaction to build generic frontend` (see :doc:`../api/rest_api`)

*   Generic `Admin interface` (not implemented yet)

*   `Resource and workflow modellings` for participation processes.

*   `SinglePageApplication` frontends and backend customizations for `specific participation projects`



Contents
--------

.. toctree::
   :maxdepth: 2

   concepts
   development/index
   administration
   backend/index
   api/index
   frontend/index
   projects/index
   attic/index
   CHANGES
   roadmap
   glossary


Indices and tables
==================

* :ref:`glossary`
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
