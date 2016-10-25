"""Sheets for :term:`principal`s."""
from colander import required
from colander import deferred
from colander import Invalid
from colander import All
from colander import OneOf
from cryptacular.bcrypt import BCRYPTPasswordManager
from pyramid.settings import asbool
from pyramid.traversal import resource_path
from substanced.util import find_service
from urllib.parse import urljoin
from deform.widget import SelectWidget
import requests

from adhocracy_core.interfaces import ISheet
from adhocracy_core.interfaces import ISheetRequirePassword
from substanced.interfaces import IUserLocator
from adhocracy_core.interfaces import SheetToSheet
from adhocracy_core.sheets import BaseResourceSheet
from adhocracy_core.sheets import add_sheet_to_registry
from adhocracy_core.sheets import sheet_meta
from adhocracy_core.sheets import AnnotationRessourceSheet
from adhocracy_core.sheets import AttributeResourceSheet
from adhocracy_core.schema import MappingSchema
from adhocracy_core.schema import SchemaNode
from adhocracy_core.schema import Email
from adhocracy_core.schema import Password
from adhocracy_core.schema import SingleLine
from adhocracy_core.schema import TimeZoneName
from adhocracy_core.schema import UniqueReferences
from adhocracy_core.schema import Roles
from adhocracy_core.schema import Boolean


class IGroup(ISheet):
    """Marker interface for the group sheet."""


class IUserBasic(ISheet):
    """Marker interface for the basic user sheet."""


class IUserExtended(ISheet):
    """Marker interface for the extended user sheet."""


class ICaptcha(ISheet):
    """Marker interface for user-submitted captcha data."""


class IPermissions(ISheet):
    """Marker interface for the permissions sheet."""


class PermissionsGroupsReference(SheetToSheet):
    """permissions sheet reference to preceding versions."""

    source_isheet = IPermissions
    source_isheet_field = 'groups'
    target_isheet = IGroup


class GroupSchema(MappingSchema):
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


@deferred
def deferred_validate_user_name(node: SchemaNode, kw: dict)\
        -> callable:
    """Return validator to check that the user login `name` is unique or None.

    :param kw: dictionary with 'request' key and
               :class:`pyramid.request.Request` object.
               If this is not available the validator is None.
    :raise: Invalid: if name is not unique.
    """
    request = kw['request']
    registry = kw['registry']
    context = kw['context']
    locator = registry.getMultiAdapter((context, request), IUserLocator)

    def validate_user_name_is_unique(node, value):
        if locator.get_user_by_login(value):
            raise Invalid(node, 'The user login name is not unique',
                          value=value)
    return validate_user_name_is_unique


@deferred
def deferred_validate_user_email(node: SchemaNode, kw: dict) -> callable:
    """Return validator to check that the `email` is unique and valid or None.

    :param kw: dictionary with 'request' key and
               :class:`pyramid.request.Request` object
               If this is not available the validator is None.
    :raise: Invalid: if name is not unique or not an email address.
    """
    request = kw['request']
    registry = kw['registry']
    context = kw['context']
    locator = registry.getMultiAdapter((context, request), IUserLocator)

    def validate_user_email_is_unique(node, value):
        if locator.get_user_by_email(value):
            raise Invalid(node, 'The user login email is not unique',
                          value=value)
    validate_email = Email.validator
    return All(validate_email, validate_user_email_is_unique)


class UserBasicSchema(MappingSchema):
    """Basic user sheet data structure.

    This sheet must only store public information, as everyone can see it.

    `name`: visible name
    """

    name = SingleLine(missing=required,
                      validator=deferred_validate_user_name)


userbasic_meta = sheet_meta._replace(
    isheet=IUserBasic,
    schema_class=UserBasicSchema,
    sheet_class=AttributeResourceSheet,
    permission_create='create_user',
)


class UserExtendedSchema(MappingSchema):
    """Extended user sheet data structure.

    Sensitive information (not for everyone's eyes) should be stored here.

    `email`: email address
    `tzname`: time zone
    """

    email = Email(validator=deferred_validate_user_email,)
    tzname = TimeZoneName()


userextended_meta = sheet_meta._replace(
    isheet=IUserExtended,
    schema_class=UserExtendedSchema,
    sheet_class=AttributeResourceSheet,
    permission_create='create_user',
    permission_view='view_userextended',
    permission_edit='edit_userextended',
)


class CaptchaSchema(MappingSchema):
    """Wraps user-submitted captcha data.

    This sheet may be required when creating a new user (if captchas are turned
    on), but the data is discarded after validation.

    `id`: captcha ID (generated by Thentos)
    `solution`: solution to the captcha (entered by a human user)
    """

    id = SingleLine(missing=required)
    solution = SingleLine(missing=required)

    def validator(self, node, value):
        """
        Validate the captcha.

        If 'adhocracy.thentos_captcha.enabled' is true, we ask the
        thentos-captcha service whether the given solution is correct.
        If captchas are not enabled, this validator will always pass.
        """
        request = node.bindings['request']
        settings = request.registry.settings
        if not self._captcha_is_correct(settings, value):
            err = Invalid(node)
            err['solution'] = 'Captcha solution is wrong'
            raise err

    def _captcha_is_correct(self, settings, value) -> bool:
        """Ask the captcha service whether the captcha was solved correctly."""
        captcha_service = settings.get('adhocracy.thentos_captcha.backend_url',
                                       'http://localhost:6542/')
        resp = requests.post(urljoin(captcha_service, 'solve_captcha'),
                             json=value)
        return resp.json()['data']


class CaptchaSheet(BaseResourceSheet):
    """Dummy sheet that does not store any data."""

    def _store_data(self, appstruct):
        """Dummy store data appstruct."""

    def _get_data_appstruct(self):
        """Dummy get data appstruct."""
        return {}


captcha_meta = sheet_meta._replace(
    isheet=ICaptcha,
    schema_class=CaptchaSchema,
    sheet_class=CaptchaSheet,
    readable=False,
    editable=False,
    creatable=False,
    create_mandatory=False,  # enabled if captchas enabled in configuration
    permission_create='create_user',
)


def get_group_choices(context, request) -> []:
    """Return group choices based on the `/principals/groups` service."""
    groups = find_service(context, 'principals', 'groups')
    if groups is None:
        return []
    target_isheet = PermissionsGroupsReference.getTaggedValue('target_isheet')
    choices = [(request.resource_url(group), name)
               for name, group in groups.items()
               if target_isheet.providedBy(group)]
    return choices


class PermissionsSchema(MappingSchema):
    """Permissions sheet data structure.

    `groups`: groups this user joined
    """

    roles = Roles()
    groups = UniqueReferences(reftype=PermissionsGroupsReference,
                              choices_getter=get_group_choices)


class PermissionsAttributeResourceSheet(AttributeResourceSheet):
    """Store the groups field references also as object attribute."""

    def _store_references(self, appstruct, registry, **kwargs):
        super()._store_references(appstruct, registry, **kwargs)
        if 'groups' in appstruct:  # pragma: no branch
            groups = appstruct['groups']
            group_ids = [resource_path(g) for g in groups]
            self.context.group_ids = group_ids


permissions_meta = sheet_meta._replace(
    isheet=IPermissions,
    schema_class=PermissionsSchema,
    permission_view='view_userextended',
    permission_create='create_edit_sheet_permissions',
    permission_edit='create_edit_sheet_permissions',
    sheet_class=PermissionsAttributeResourceSheet,
)


class IPasswordAuthentication(ISheet, ISheetRequirePassword):
    """Marker interface for the password sheet."""


class PasswordAuthenticationSchema(MappingSchema):
    """Data structure for password based user authentication.

    `password`: plaintext password :class:`adhocracy_core.schema.Password`.
    """

    password = Password(missing=required)


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
        """Check if `password` matches the stored encrypted password.

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


class ActivationSetting(SingleLine):
    """Activation setting.

    Possible values: direct, registration_mail, invitation_mail
    """

    default = 'registration_mail'

    @deferred
    def validator(self, kw: dict):
        """Validator."""
        return OneOf(('direct', 'registration_mail', 'invitation_mail'))

    @deferred
    def widget(self, kw: dict) -> SelectWidget:
        choices = [(x, x) for x in self.validator.choices]
        return SelectWidget(values=choices)


class IActivationConfiguration(ISheet):
    """Marker interface for the user activation configutation sheet."""


class ActivationConfigutationSchema(MappingSchema):
    """Data structure for user activation configuration.

    `activation`: One of 'direct', 'register' or 'invite'
    """

    activation = ActivationSetting()


activation_configuration_meta = sheet_meta._replace(
    isheet=IActivationConfiguration,
    schema_class=ActivationConfigutationSchema,
    readable=True,
    creatable=True,
    editable=False,
    permission_create='activate_user',
    permission_view='view_userextended',
)


class IAnonymizeDefault(ISheet):
    """Marker interface for the user anonymize default sheet."""


class AnonymizeDefaultSchema(MappingSchema):
    """Data structure for user default anonymize setting.

    `anonymize`:  Boolean setting for anonymization default .
    """

    anonymize = Boolean()


anonymize_default_meta = sheet_meta._replace(
    isheet=IAnonymizeDefault,
    schema_class=AnonymizeDefaultSchema,
    permission_create='create_user',
    permission_view='view_userextended',
    permission_edit='edit_userextended',
)


def includeme(config):
    """Register sheets and activate catalog factory."""
    add_sheet_to_registry(userbasic_meta, config.registry)
    add_sheet_to_registry(userextended_meta, config.registry)
    captcha_enabled = asbool(config.registry.settings.get(
        'adhocracy.thentos_captcha.enabled', False))
    if captcha_enabled:
        add_sheet_to_registry(captcha_meta._replace(creatable=True,
                                                    create_mandatory=True),
                              config.registry)
    else:
        add_sheet_to_registry(captcha_meta, config.registry)
    add_sheet_to_registry(password_meta, config.registry)
    add_sheet_to_registry(group_meta, config.registry)
    add_sheet_to_registry(permissions_meta, config.registry)
    add_sheet_to_registry(activation_configuration_meta, config.registry)
    add_sheet_to_registry(anonymize_default_meta, config.registry)
