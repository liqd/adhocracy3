.. _glossary:

Glossary
========

.. glossary::
   :sorted:

  
   service
      A resource marked as `service`. Services are  kind of `utilities`
      inside the object hierarchy. They may provide special rest api end points
      and helper methods. You can find them by their name with
      :func:`adhocracy.interfaces.IPool.find_service`.
      The `service` has to be in :term:`lineage` or a child of a  the `lineage`
      pools for a given `context`.


