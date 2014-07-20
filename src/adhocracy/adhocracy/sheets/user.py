"""User Sheet."""
import colander
from cryptacular.bcrypt import BCRYPTPasswordManager

from adhocracy.interfaces import ISheet
from adhocracy.sheets import add_sheet_to_registry
from adhocracy.sheets import sheet_metadata_defaults
from adhocracy.sheets import GenericResourceSheet
from adhocracy.schema import Email
from adhocracy.schema import Password
from adhocracy.schema import TimeZoneName


class IUserBasic(ISheet):

    """Market interface for the userbasic sheet."""


class UserBasicSchema(colander.MappingSchema):

    """Userbasic sheet data structure.

    `email`: email address
    `name`: visible name
    """

    email = Email()
    name = colander.SchemaNode(colander.String(),
                               missing=colander.required,
                               default='')
    tzname = TimeZoneName()


userbasic_metadata = sheet_metadata_defaults._replace(
    isheet=IUserBasic,
    schema_class=UserBasicSchema,
)


# @catalog_factory('usercatalog')
#  class UserFactory(object):
#     email = Field()
#     name = Field()


class IPasswordAuthentication(ISheet):

    """Marker interface for the password sheet."""


class PasswordAuthenticationSchema(colander.MappingSchema):

    """Data structure for password based user authentication.

    `password`: plaintext password
    """

    password = Password(missing=colander.required)


class PasswordAuthenticationSheet(GenericResourceSheet):

    """Sheet for password based user authentication.

    The `password` data is encrypted and stored in the user object (context).
    This assures compatibility with :class:`substanced.principal.User`.

    The `check_plaintext_password` method can be used to validate passwords.
    """

    def _store_non_references(self, appstruct):
        password = appstruct.get('password', '')
        if not password:
            return
        if not hasattr(self.context, 'password'):
            self.context.password = ''
        if not hasattr(self.context, 'pwd_manager'):
            self.context.pwd_manager = BCRYPTPasswordManager()
        self.context.password = self.context.pwd_manager.encode(password)

    def _get_non_reference_appstruct(self):
        password = getattr(self.context, 'password', '')
        return {'password': password}

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


password_metadata = sheet_metadata_defaults._replace(
    isheet=IPasswordAuthentication,
    schema_class=PasswordAuthenticationSchema,
    sheet_class=PasswordAuthenticationSheet,
    readable=False,
    creatable=True,
    editable=True,
)


# def add_user_catalog(root):
#     """Add the user catalog if it doesn't exist yet."""
#     catalogs = root['catalogs']
#     if 'usercatalog' not in catalogs:
#        catalogs.add_catalog('usercatalog', update_indexes=True)


def includeme(config):
    """Register sheets and activate catalog factory."""
    add_sheet_to_registry(userbasic_metadata, config.registry)
    add_sheet_to_registry(password_metadata, config.registry)
    # config.scan('.')
    # config.add_evolution_step(add_user_catalog)
