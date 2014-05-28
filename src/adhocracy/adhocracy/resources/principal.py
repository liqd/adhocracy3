"""Resources to handle users and groups."""
from pyramid.registry import Registry
from zope.interface import implementer

from adhocracy.interfaces import IPool
from adhocracy.resources import add_resource_type_to_registry
from adhocracy.resources.pool import Pool
from adhocracy.resources.pool import pool_metadata


class IPrincipalsPool(IPool):

    """Pool representing a collection of principals.

    If the object is created via
    :func:`substanced.content.ContentRegistry.create`, it will contain
    three subobjects:

      users: an instance of the content type :class:`IUsers`

      group:  an instance of the content type ``Groups``

      resets: an instance of the content type ``Password Resets``
    """


def create_initial_content_for_principals(context: IPool, registry: Registry,
                                          options: dict):
    """Add users, groups and resets subobjects to context."""
    users = registry.content.create(IUsersPool.__identifier__)
    context.add('users', users)
    groups = registry.content.create(IGroupsPool.__identifier__)
    context.add('groups', groups)
    resets = registry.content.create(IPasswordResetsPool.__identifier__)
    context.add('resets', resets)


# @implementer(IPrincipalsPool)
# class PrincipalsPool(Pool):
#     """Service object representing a collection of principals."""
#
#     def add_user(self, login: str, registry=None) -> object:
#         """ Add a user to this principal service with the id `login`."""
#         registry = registry or get_current_registry()
#         user = registry.content.create('User')
#         self['users'][login] = user  # FIXME don`t override users
#         return user
#
#     def add_group(self, name: str, registry=None) -> object:
#         """ Add a group to this principal service using the name ``name``."""
#         registry = registry or get_current_registry()
#         group = registry.content.create('Group')  # FIXME don`t overrideusers
#         self['groups'][name] = group
#         return group
#
#     def add_reset(self, user, registry=None) -> object:
#         """ Add a password reset to this principal service for the user
#         ``user`` (either a user object or a user id).  ``name``. """
#         registry = registry or get_current_registry()
#         token = ''
#         while True:
#             token = _gen_random_token()
#             if not token in self:
#                 break
#         reset = registry.content.create('Password Reset')
#         self['resets'][token] = reset
#         objectmap = find_objectmap(self)
#         objectmap.connect(user, reset, UserToPasswordReset)
#         return reset


principals_metadata = pool_metadata._replace(
    iresource=IPrincipalsPool,
    after_creation=[create_initial_content_for_principals],
    element_types=[]  # we don't want the frontend to post resources here
)


class IUserPool(IPool):

    """Pool for Groups."""


@implementer(IUserPool)
class UserPool(Pool):

    """User pool."""

    tzname = 'UTC'
    password = ''
    email = ''


user_metadata = pool_metadata._replace(
    iresource=IUserPool,
    content_class=UserPool,
    element_types=[]  # we don't the frontend to post resources here
)


class IUsersPool(IPool):

    """Pool for Users."""


users_metadata = pool_metadata._replace(
    iresource=IUsersPool,
    element_types=[IUserPool]
)


class IGroupsPool(IPool):

    """Pool for Groups."""


groups_metadata = pool_metadata._replace(
    iresource=IGroupsPool,
    element_types=[]
)


class IPasswordResetsPool(IPool):

    """Pool for Groups."""


passwordresets_metadata = pool_metadata._replace(
    iresource=IPasswordResetsPool,
    element_types=[]
)


def includeme(config):
    """Add resource types to registry."""
    add_resource_type_to_registry(principals_metadata, config)
    add_resource_type_to_registry(user_metadata, config)
    add_resource_type_to_registry(users_metadata, config)
    add_resource_type_to_registry(groups_metadata, config)
    add_resource_type_to_registry(passwordresets_metadata, config)
