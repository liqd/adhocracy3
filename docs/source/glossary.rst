.. _glossary:

Glossary
========

.. glossary::
   :sorted:

   post_pool
      A normal or :term:`service` :class:`adhocracy.interfaces.IPool` that
      serves as the common place to post resources of a special type for a
      given context.
      If a :term:`resource sheet` field with backreferences sets a
      :class:`adhocracy.schema.PostPool` field, the
      referencing resources can only be postet at the :term:`post_pool`.
      This assumes that a post_pool exists in the lineage of the referenced
      resources.
      If a :term:`resource sheet` field with references sets this, the
      referenced resource type can only be posted to :term:`post_pool`.

   service
      A resource marked as `service`. Services
      may provide special rest api end points
      and helper methods. You can find them by their name with
      :func:`adhocracy.interfaces.IPool.find_service`.
      The `service` has to be in :term:`lineage` or a child of a
      :term:`lineage` pool for a given `context`.

   principal
       `User` or :term:`group`.

   group
       A set of users. Can be mapped to permission :term:`role`s.

   groupid
       Unique id of one :term:`group`: "group:<name>"

   role:
       A set of permissions.

   roleid
       Unique id of one permission :term:`role`: "role:<name>"

   local role:
       A :term:`role` mapped to a :term:`group` within a local context and all
       his children.

