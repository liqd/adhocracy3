"""Resources to handle users and groups."""
from pyramid.registry import Registry
from zope.interface import implementer

from adhocracy.interfaces import IPool
from adhocracy.resources import add_resource_type_to_registry
from adhocracy.resources.pool import Pool
from adhocracy.resources.pool import pool_metadata
from adhocracy.sheets.user import IPasswordAuthentication
from adhocracy.sheets.user import IUserBasic


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


principals_metadata = pool_metadata._replace(
    iresource=IPrincipalsPool,
    after_creation=[create_initial_content_for_principals] +
    pool_metadata.after_creation,
    basic_sheets=[IUserBasic],
    extended_sheets=[IPasswordAuthentication],
    element_types=[]  # we don't want the frontend to post resources here
)


class IUser(IPool):

    """User resource.

    This inherits from IPool in order to allow to use this resource as a
    namespace for user objects.

    """


@implementer(IUser)
class User(Pool):

    """User implementation.

    With attributes to be compatible with :class:`substanced.prinipals.User`

    """

    tzname = 'UTC'
    password = ''
    email = ''


user_metadata = pool_metadata._replace(
    iresource=IUser,
    content_class=User,
    element_types=[]  # we don't want the frontend to post resources here
)


class IUsersPool(IPool):

    """Pool for Users."""


users_metadata = pool_metadata._replace(
    iresource=IUsersPool,
    element_types=[IUser]
)


class IGroupsPool(IPool):

    """Pool for Groups."""


groups_metadata = pool_metadata._replace(
    iresource=IGroupsPool,
    element_types=[]
)


class IPasswordResetsPool(IPool):

    """Pool for Password Resets."""


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
