"""Resources to handle users and groups."""
from base64 import b64encode
from logging import getLogger
from os import urandom

from pyramid.registry import Registry
from substanced.util import find_service
from substanced.interfaces import IUserLocator
from zope.interface import Interface
from zope.interface import implementer

from adhocracy_core.interfaces import IPool
from adhocracy_core.interfaces import IServicePool
from adhocracy_core.resources import add_resource_type_to_registry
from adhocracy_core.resources.pool import Pool
from adhocracy_core.resources.pool import pool_metadata
from adhocracy_core.resources.service import service_metadata
import adhocracy_core.sheets.user
import adhocracy_core.sheets.pool
import adhocracy_core.sheets.metadata
import adhocracy_core.sheets.rate


logger = getLogger(__name__)


class IPrincipalsService(IServicePool):

    """Service Pool representing a collection of principals.

    If the object is created via
    :func:`substanced.content.ContentRegistry.create`, it will contain
    three sub services:

      users: an instance of the content type :class:`IUsers`

      group:  an instance of the content type ``Groups``

      resets: an instance of the content type ``Password Resets``
    """


def create_initial_content_for_principals(context: IPool, registry: Registry,
                                          options: dict):
    """Add users, groups and resets subobjects to context."""
    registry.content.create(IUsersService.__identifier__, parent=context)
    registry.content.create(IGroupsService.__identifier__, parent=context)
    registry.content.create(IPasswordResetsService.__identifier__,
                            parent=context)


principals_metadata = service_metadata._replace(
    iresource=IPrincipalsService,
    content_name='principals',
    after_creation=[create_initial_content_for_principals] +
    service_metadata.after_creation,
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
    name = ''
    active = False
    activation_path = None


def send_registration_mail(context: IUser,
                           registry: Registry,
                           options: dict={}):
    """Send a registration mail to validate the email of a user account."""
    # FIXME subject should be configurable
    subject = 'Adhocracy Account Authentication'
    name = context.name
    email = context.email
    activation_path = _generate_activation_path()
    context.activation_path = activation_path
    logger.warn('Sending registration mail to %s for new user named %s, '
                'activation path=%s', email, name, context.activation_path)
    args = {'name': name, 'activation_path': activation_path}
    registry.messenger.render_and_send_mail(
        subject=subject,
        recipients=[email],
        template_asset_base='adhocracy_core:templates/registration_mail',
        args=args)


def _generate_activation_path() -> str:
    random_bytes = urandom(18)
    return '/activate/' + b64encode(random_bytes, altchars=b'-_').decode()


user_metadata = pool_metadata._replace(
    iresource=IUser,
    content_class=User,
    after_creation=[send_registration_mail] + pool_metadata.after_creation,
    basic_sheets=[adhocracy_core.sheets.user.IUserBasic,
                  adhocracy_core.sheets.metadata.IMetadata,
                  adhocracy_core.sheets.pool.IPool,
                  ],
    extended_sheets=[adhocracy_core.sheets.user.IPasswordAuthentication,
                     adhocracy_core.sheets.rate.ICanRate],
    element_types=[],  # we don't want the frontend to post resources here
    use_autonaming=True
)


class IUsersService(IServicePool):

    """Service Pool for Users."""


users_metadata = service_metadata._replace(
    iresource=IUsersService,
    content_name='users',
    element_types=[IUser]
)


class IGroupsService(IServicePool):

    """Pool for Groups."""


groups_metadata = service_metadata._replace(
    iresource=IGroupsService,
    content_name='groups',
    element_types=[]
)


class IPasswordResetsService(IServicePool):

    """Service Pool for Password Resets."""


passwordresets_metadata = service_metadata._replace(
    iresource=IPasswordResetsService,
    content_name='resets',
    element_types=[]
)


@implementer(IUserLocator)
class UserLocatorAdapter(object):

    """Provides helper methods to find users."""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get_user_by_login(self, login: str) -> IUser:
        """Find user per `login` name or return None."""
        # FIXME use catalog for all get_user_by_ methods
        users = find_service(self.context, 'principals', 'users')
        for user in users.values():
            if user.name == login:
                return user

    def get_user_by_userid(self, user_id: int) -> IUser:
        """Find user per `user_id` (zodb oid) or return None."""
        raise NotImplementedError

    def get_user_by_email(self, email: str) -> IUser:
        """Find user per email or return None."""
        users = find_service(self.context, 'principals', 'users')
        for user in users.values():
            if user.email == email:
                return user

    def get_user_by_activation_path(self, activation_path: str) -> IUser:
        """Find user per activation path or return None."""
        users = find_service(self.context, 'principals', 'users')
        for user in users.values():
            if user.activation_path == activation_path:
                return user

    def get_groupids(self, user_id: int):
        """Get user groups for `user_id` (zodb oid)."""
        raise NotImplementedError


def includeme(config):
    """Add resource types to registry."""
    add_resource_type_to_registry(principals_metadata, config)
    add_resource_type_to_registry(user_metadata, config)
    add_resource_type_to_registry(users_metadata, config)
    add_resource_type_to_registry(groups_metadata, config)
    add_resource_type_to_registry(passwordresets_metadata, config)
    config.registry.registerAdapter(UserLocatorAdapter,
                                    (Interface, Interface),
                                    IUserLocator)
