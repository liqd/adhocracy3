"""Resources to handle users and groups."""
from base64 import b64encode
from logging import getLogger
from os import urandom
from smtplib import SMTPException

from pyramid.registry import Registry
from pyramid.traversal import find_resource
from pyramid.request import Request
from substanced.util import find_service
from zope.interface import Attribute
from zope.interface import Interface
from zope.interface import implementer

from adhocracy_core.interfaces import IPool
from adhocracy_core.interfaces import IServicePool
from adhocracy_core.interfaces import IRolesUserLocator
from adhocracy_core.resources import add_resource_type_to_registry
from adhocracy_core.interfaces import IGroupLocator
from adhocracy_core.resources.pool import Pool
from adhocracy_core.resources.pool import pool_metadata
from adhocracy_core.resources.service import service_metadata
from adhocracy_core.utils import raise_colander_style_error
from adhocracy_core.utils import get_sheet
import adhocracy_core.sheets.metadata
import adhocracy_core.sheets.principal
import adhocracy_core.sheets.pool
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
    registry.content.create(IUsersService.__identifier__,
                            parent=context, registry=registry)
    registry.content.create(IGroupsService.__identifier__,
                            parent=context, registry=registry)
    registry.content.create(IPasswordResetsService.__identifier__,
                            parent=context, registry=registry)


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

    active = Attribute('Whether the user account has been activated (bool)')
    activation_path = Attribute(
        'Activation path for not-yet-activated accounts (str)')


@implementer(IUser)
class User(Pool):

    """User implementation.

    With attributes to be compatible with :class:`substanced.principals.User`

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
    logger.debug('Sending registration mail to %s for new user named %s, '
                 'activation path=%s', email, name, context.activation_path)
    args = {'name': name, 'activation_path': activation_path}
    try:
        registry.messenger.render_and_send_mail(
            subject=subject,
            recipients=[email],
            template_asset_base='adhocracy_core:templates/registration_mail',
            args=args)
    except SMTPException as err:
        msg = 'Cannot send registration mail: {}'.format(str(err))
        raise_colander_style_error(adhocracy_core.sheets.principal.IUserBasic,
                                   'email',
                                   msg)


def _generate_activation_path() -> str:
    random_bytes = urandom(18)
    return '/activate/' + b64encode(random_bytes, altchars=b'-_').decode()


user_metadata = pool_metadata._replace(
    iresource=IUser,
    content_class=User,
    after_creation=[send_registration_mail] + pool_metadata.after_creation,
    basic_sheets=[adhocracy_core.sheets.principal.IUserBasic,
                  adhocracy_core.sheets.principal.IPermissions,
                  adhocracy_core.sheets.metadata.IMetadata,
                  adhocracy_core.sheets.pool.IPool,
                  ],
    extended_sheets=[adhocracy_core.sheets.principal.IPasswordAuthentication,
                     adhocracy_core.sheets.rate.ICanRate],
    element_types=[],  # we don't want the frontend to post resources here
    use_autonaming=True,
    permission_add='add_user',
    is_implicit_addable=False,
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


class IGroup(IPool):

    """Group for Users."""


group_metadata = pool_metadata._replace(
    iresource=IGroup,
    extended_sheets=[adhocracy_core.sheets.principal.IGroup,
                     ],
    element_types=[],  # we don't want the frontend to post resources here
)


class IPasswordResetsService(IServicePool):

    """Service Pool for Password Resets."""


passwordresets_metadata = service_metadata._replace(
    iresource=IPasswordResetsService,
    content_name='resets',
    element_types=[]
)


@implementer(IRolesUserLocator)
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

    def get_user_by_userid(self, userid: str) -> IUser:
        """Find user by :term:`userid` or return None."""
        try:
            return find_resource(self.context, userid)
        except KeyError:
            return None

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

    def get_groupids(self, userid: str) -> list:
        """Get :term:`groupid`s for _term:`userid` or return None."""
        user = self.get_user_by_userid(userid)
        if user is None:
            return None
        user_sheet = get_sheet(user,
                               adhocracy_core.sheets.principal.IPermissions,
                               registry=self.request.registry)
        groups = user_sheet.get()['groups']
        groupids = ['group:' + g.__name__ for g in groups]
        return groupids

    def get_roleids(self, userid: str) -> list:
        """Return the roles for :term:`userid` or None."""
        user = self.get_user_by_userid(userid)
        if user is None:
            return None
        roles_sheet = get_sheet(user,
                                adhocracy_core.sheets.principal.IPermissions,
                                registry=self.request.registry)
        roles = roles_sheet.get()['roles']
        roleids = ['role:' + r for r in roles]
        return roleids


@implementer(IGroupLocator)
class GroupLocatorAdapter:

    """Provides helper methods to get information about groups."""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get_roleids(self, groupid: str) -> list:
        """Return the roles for `groupid` or None. Read the interface."""
        group = self.get_group_by_id(groupid)
        if group is None:
            return None
        group_sheet = get_sheet(group, adhocracy_core.sheets.principal.IGroup,
                                registry=self.request.registry)
        roles = group_sheet.get()['roles']
        roleids = ['role:' + r for r in roles]
        return roleids

    def get_group_by_id(self, groupid: str) -> IGroup:
        """Return the group for :term:`groupid` or None. Read the interface."""
        groups = find_service(self.context, 'principals', 'groups')
        if ':' not in groupid:
            return groups.get(groupid, None)
        name = groupid.split(':')[1]
        return groups.get(name, None)


def groups_and_roles_finder(userid: str, request: Request) -> list:
    """A Pyramid authentication policy groupfinder callback."""
    context = request.context
    userlocator = request.registry.getMultiAdapter((context, request),
                                                   IRolesUserLocator)
    groupids = userlocator.get_groupids(userid) or []
    roleids = userlocator.get_roleids(userid) or []
    grouplocator = request.registry.getMultiAdapter((context, request),
                                                    IGroupLocator)
    groups_roleids = []
    for groupid in groupids:
        group_roleids = grouplocator.get_roleids(groupid) or []
        groups_roleids.extend(group_roleids)
    groups_and_roles = set(groupids + roleids + groups_roleids)
    return sorted(list(groups_and_roles))


def includeme(config):
    """Add resource types to registry."""
    add_resource_type_to_registry(principals_metadata, config)
    add_resource_type_to_registry(user_metadata, config)
    add_resource_type_to_registry(users_metadata, config)
    add_resource_type_to_registry(group_metadata, config)
    add_resource_type_to_registry(groups_metadata, config)
    add_resource_type_to_registry(passwordresets_metadata, config)
    config.registry.registerAdapter(UserLocatorAdapter,
                                    (Interface, Interface),
                                    IRolesUserLocator)
    config.registry.registerAdapter(GroupLocatorAdapter,
                                    (Interface, Interface),
                                    IGroupLocator)
