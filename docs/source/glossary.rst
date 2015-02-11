.. _glossary:

Glossary
========

.. glossary::
   :sorted:

   post_pool
      A normal or :term:`service` :class:`adhocracy_core.interfaces.IPool` that
      serves as the common place to post resources of a special type for a
      given context.
      If a :term:`resource sheet` field with backreferences sets a
      :class:`adhocracy_core.schema.PostPool` field, the
      referencing resources can only be postet at the :term:`post_pool`.
      This assumes that a post_pool exists in the lineage of the referenced
      resources.
      If a :term:`resource sheet` field with references sets this, the
      referenced resource type can only be posted to :term:`post_pool`.

   service
      A resource marked as `service`. Services
      may provide special rest api end points
      and helper methods. You can find them by their name with
      :func:`adhocracy_core.interfaces.IPool.find_service`.
      The `service` has to be in :term:`lineage` or a child of a
      :term:`lineage` pool for a given `context`.

   principal
       A principal is a string representing a :term:`userid`, :term:`groupid`,
       or :term:`roleid`. It is provided by an :term:`authentication policy`.
       For more information about the permission system read
       :doc:`api/authentication_api`.

   userid:
      The unique id for one userique id of one :term:`group`: "group:<name>".

   group
       A set of users. Can be mapped to permission :term:`role`s.

   groupid
       Unique id of one :term:`group`: "group:<name>".

   role:
       A set of permissions that can be mapped to :term:`group`s
       or :term:`user`.

   roleid
       Unique id of one permission :term:`role`: "role:<name>".

   local role:
       A :term:`role` mapped to a :term:`group` or :term:`user` within a local
       context and all his children.


