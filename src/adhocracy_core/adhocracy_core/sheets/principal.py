"""Sheets for :term:`principal`s."""
import colander
from cryptacular.bcrypt import BCRYPTPasswordManager
from pyramid.traversal import resource_path
from pyramid.traversal import find_resource

from adhocracy_core.interfaces import ISheet
from substanced.interfaces import IUserLocator
from adhocracy_core.interfaces import SheetToSheet
from adhocracy_core.sheets import add_sheet_to_registry
from adhocracy_core.sheets import sheet_meta
from adhocracy_core.sheets import AnnotationRessourceSheet
from adhocracy_core.sheets import AttributeResourceSheet
from adhocracy_core.schema import Email
from adhocracy_core.schema import Password
from adhocracy_core.schema import SingleLine
from adhocracy_core.schema import TimeZoneName
from adhocracy_core.schema import UniqueReferences
from adhocracy_core.schema import Roles


class IGroup(ISheet):

    """Marker interface for the group sheet."""


class IUserBasic(ISheet):

    """Marker interface for the basic user sheet."""


class IUserExtended(ISheet):

    """Marker interface for the extended user sheet."""


class IPermissions(ISheet):

    """Marker interface for the permissions sheet."""


class PermissionsGroupsReference(SheetToSheet):

    """permissions sheet reference to preceding versions."""

    source_isheet = IPermissions
    source_isheet_field = 'groups'
    target_isheet = IGroup


class GroupSchema(colander.MappingSchema):

    """Group sheet data structure."""

    users = UniqueReferences(readonly=True,
                             backref=True,
                             reftype=PermissionsGroupsReference)
    roles = Roles()


group_meta = sheet_meta._replace(
    isheet=IGroup,
    schema_class=GroupSchema,
    sheet_class=AttributeResourceSheet,
)


@colander.deferred
def deferred_validate_user_name(node: colander.SchemaNode, kw: dict)\
        -> callable:
    """Return validator to check that the user login `name` is unique or None.

    :param kw: dictionary with 'request' key and
               :class:`pyramid.request.Request` object.
               If this is not available the validator is None.
    :raise: colander.Invalid: if name is not unique.
    """
    request = kw.get('request', None)
    if not request:
        return None
    locator = request.registry.getMultiAdapter((request.root, request),
                                               IUserLocator)

    def validate_user_name_is_unique(node, value):
        if locator.get_user_by_login(value):
            raise colander.Invalid(node, 'The user login name is not unique',
                                   value=value)
    return validate_user_name_is_unique


@colander.deferred
def deferred_validate_user_email(node: colander.SchemaNode, kw: dict)\
        -> callable:
    """Return validator to check that the `email` is unique and valid or None.

    :param kw: dictionary with 'request' key and
               :class:`pyramid.request.Request` object
               If this is not available the validator is None.
    :raise: colander.Invalid: if name is not unique or not an email address.
    """
    request = kw.get('request', None)
    if not request:
        return None
    locator = request.registry.getMultiAdapter((request.root, request),
                                               IUserLocator)

    def validate_user_email_is_unique(node, value):
        if locator.get_user_by_email(value):
            raise colander.Invalid(node, 'The user login email is not unique',
                                   value=value)
    validate_email = Email.validator
    return colander.All(validate_email, validate_user_email_is_unique)


class UserBasicSchema(colander.MappingSchema):

    """Basic user sheet data structure.

    This sheet must only store public information, as everyone can see it.

    `name`: visible name
    """

    name = SingleLine(missing=colander.required,
                      validator=deferred_validate_user_name)


userbasic_meta = sheet_meta._replace(
    isheet=IUserBasic,
    schema_class=UserBasicSchema,
    sheet_class=AttributeResourceSheet,
    permission_create='create_user',
)


class UserExtendedSchema(colander.MappingSchema):

    """Extended user sheet data structure.

    Sensitive information (not for everyone's eyes) should be stored here.

    `email`: email address
    `tzname`: time zone
    """

    email = Email(validator=deferred_validate_user_email)
    tzname = TimeZoneName()


userextended_meta = sheet_meta._replace(
    isheet=IUserExtended,
    schema_class=UserExtendedSchema,
    sheet_class=AttributeResourceSheet,
    permission_create='create_user',
    permission_view='view_userextended',
    permission_edit='edit_userextended',
)


@colander.deferred
def deferred_roles_and_group_roles(node: colander.SchemaNode, kw: dict)\
        -> list:
    """Return roles and groups roles for `context`.

    :param kw: dictionary with 'context' key and
              :class:`adhocracy_core.sheets.principal.IPermissions` object.
    :return: list of :term:`roles` or [].
    """
    context = kw.get('context', None)
    if context is None:
        return []
    roles_and_group_roles = set(context.roles)
    groups = [find_resource(context, gid) for gid in context.group_ids]
    for group in groups:
        roles_and_group_roles.update(group.roles)
    return sorted(list(roles_and_group_roles))


class PermissionsSchema(colander.MappingSchema):

    """Permissions sheet data structure.

    `groups`: groups this user joined
    """

    roles = Roles()
    groups = UniqueReferences(reftype=PermissionsGroupsReference)
    roles_and_group_roles = Roles(readonly=True,
                                  default=deferred_roles_and_group_roles)


class PermissionsAttributeResourceSheet(AttributeResourceSheet):

    """Store the groups field references also as object attribute."""

    def _store_references(self, appstruct, registry):
        super()._store_references(appstruct, registry)
        if 'groups' in appstruct:  # pragma: no branch
            groups = appstruct['groups']
            group_ids = [resource_path(g) for g in groups]
            self.context.group_ids = group_ids


permissions_meta = sheet_meta._replace(
    isheet=IPermissions,
    schema_class=PermissionsSchema,
    permission_view='view_userextended',
    permission_create='edit_sheet_permissions',
    permission_edit='edit_sheet_permissions',
    sheet_class=PermissionsAttributeResourceSheet,
)


class IPasswordAuthentication(ISheet):

    """Marker interface for the password sheet."""


class PasswordAuthenticationSchema(colander.MappingSchema):

    """Data structure for password based user authentication.

    `password`: plaintext password :class:`adhocracy_core.schema.Password`.
    """

    password = Password(missing=colander.required)


class PasswordAuthenticationSheet(AnnotationRessourceSheet):

    """Sheet for password based user authentication.

    The `password` data is encrypted and stored in the user object (context).
    This assures compatibility with :class:`substanced.principal.User`.

    The `check_plaintext_password` method can be used to validate passwords.
    """

    def _store_data(self, appstruct):
        password = appstruct.get('password', '')
        if not password:
            return
        manager = getattr(self.context, 'pwd_manager', None)
        if manager is None:
            manager = BCRYPTPasswordManager()
            self.context.pwd_manager = manager
        password_encoded = self.context.pwd_manager.encode(password)
        self.context.password = password_encoded

    def _get_data_appstruct(self):
        password_encoded = getattr(self.context, 'password', '')
        return {'password': password_encoded}

    def check_plaintext_password(self, password: str) -> bool:
        """ Check if `password` matches the stored encrypted password.

        :raises ValueError: if `password` is > 4096 bytes
        """
        if len(password) > 4096:
            # avoid DOS ala
            # https://www.djangoproject.com/weblog/2013/sep/15/security/
            raise ValueError('Not checking password > 4096 bytes')
        stored_password = self.context.password
        return self.context.pwd_manager.check(stored_password, password)


password_meta = sheet_meta._replace(
    isheet=IPasswordAuthentication,
    schema_class=PasswordAuthenticationSchema,
    sheet_class=PasswordAuthenticationSheet,
    readable=False,
    creatable=True,
    editable=True,
    permission_create='create_user',
)


def includeme(config):
    """Register sheets and activate catalog factory."""
    add_sheet_to_registry(userbasic_meta, config.registry)
    add_sheet_to_registry(userextended_meta, config.registry)
    add_sheet_to_registry(password_meta, config.registry)
    add_sheet_to_registry(group_meta, config.registry)
    add_sheet_to_registry(permissions_meta, config.registry)
