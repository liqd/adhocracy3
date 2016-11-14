"""Root type to create initial object hierarchy and set global Permissions."""

# flake8: noqa

from pyramid.registry import Registry
from substanced.interfaces import IRoot
from substanced.objectmap import ObjectMap
from substanced.util import find_service

from adhocracy_core.interfaces import IPool
from adhocracy_core.interfaces import DEFAULT_USER_GROUP_NAME
from adhocracy_core.resources import add_resource_type_to_registry
from adhocracy_core.resources.activity import add_activiy_service
from adhocracy_core.resources.asset import add_assets_service
from adhocracy_core.resources.organisation import IOrganisation
from adhocracy_core.resources.organisation import organisation_meta
from adhocracy_core.resources.principal import IPrincipalsService
from adhocracy_core.resources.principal import IUser
from adhocracy_core.resources.principal import ISystemUser
from adhocracy_core.resources.principal import IGroup
from adhocracy_core.resources.process import IProcess
from adhocracy_core.resources.geo import add_locations_service
from adhocracy_core.resources.page import add_page_service
from adhocracy_core.catalog import ICatalogsService
import adhocracy_core.sheets.principal
import adhocracy_core.sheets.name


class IRootPool(IOrganisation, IRoot):

    """The application root object."""


def create_initial_content_for_app_root(context: IPool, registry: Registry,
                                        options: dict):
    """Add the Catalog, principals services to the context."""
    _add_objectmap_to_app_root(context)
    _add_graph(context, registry)
    _add_catalog_service(context, registry)
    _add_principals_service(context, registry)
    _add_default_group(context, registry)
    _add_initial_user_and_group(context, registry)
    _add_anonymous_user(context, registry)
    add_locations_service(context, registry, {})
    add_assets_service(context, registry, {})
    add_page_service(context, registry, {})
    add_activiy_service(context, registry, {})


def _add_objectmap_to_app_root(root):
    root.__objectmap__ = ObjectMap(root)
    root.__objectmap__.add(root, ('',))


def _add_graph(context, registry):
    graph = registry.content.create('Graph', context)
    context.__graph__ = graph


def _add_catalog_service(context, registry):
    registry.content.create(ICatalogsService.__identifier__, parent=context,
                            registry=registry)


def _add_principals_service(context, registry):
    registry.content.create(IPrincipalsService.__identifier__,
                            parent=context,
                            registry=registry)


def add_example_process(context: IPool, registry: Registry, options: dict):
    """Add example organisation and process."""
    appstructs = {adhocracy_core.sheets.name.IName.__identifier__:
                  {'name': 'adhocracy'}}
    registry.content.create(IProcess.__identifier__,
                            parent=context,
                            appstructs=appstructs,
                            registry=registry)


def _add_default_group(context, registry):
    if not registry.settings.get('adhocracy.add_default_group',
                                 True):  # pragma: no cover
        return
    group_name = DEFAULT_USER_GROUP_NAME
    groups = find_service(context, 'principals', 'groups')
    appstructs = {adhocracy_core.sheets.name.IName.__identifier__:
                  {'name': group_name},
                  }
    registry.content.create(IGroup.__identifier__, groups,
                            appstructs=appstructs,
                            registry=registry)


def _add_initial_user_and_group(context, registry):

    user_name = registry.settings.get('adhocracy.initial_login', 'god')
    user_password = registry.settings.get('adhocracy.initial_password',
                                          'password')
    user_email = registry.settings.get('adhocracy.initial_email',
                                       'sysadmin@test.de')
    group_name = registry.settings.get('adhocracy.initial_group_name', 'gods')
    group_roles = ['god']
    groups = find_service(context, 'principals', 'groups')
    appstructs = {adhocracy_core.sheets.principal.IGroup.__identifier__:
                  {'roles': group_roles},
                  adhocracy_core.sheets.name.IName.__identifier__:
                  {'name': group_name},
                  }
    group = registry.content.create(IGroup.__identifier__, groups,
                                    appstructs=appstructs,
                                    registry=registry)
    users = find_service(context, 'principals', 'users')
    password_sheet = adhocracy_core.sheets.principal.IPasswordAuthentication
    appstruct = {adhocracy_core.sheets.principal.IUserBasic.__identifier__:
                 {'name': user_name},
                 adhocracy_core.sheets.principal.IUserExtended.__identifier__:
                 {'email': user_email},
                 adhocracy_core.sheets.principal.IPermissions.__identifier__:
                 {'groups': [group]},
                 password_sheet.__identifier__:
                 {'password': user_password},
                 }
    user = registry.content.create(IUser.__identifier__,
                                   users,
                                   appstruct,
                                   run_after_creation=False,
                                   send_event=False,
                                   registry=registry)
    user.activate()



def _add_anonymous_user(context, registry):
    user_name = registry.settings.get('adhocracy.anonymous_user', 'anonymous')
    user_email = registry.settings.get('adhocracy.anonymous_user_email',
                                       'sysadmin@test.de')
    users = find_service(context, 'principals', 'users')
    appstruct = {adhocracy_core.sheets.principal.IUserBasic.__identifier__:
                 {'name': user_name},
                 adhocracy_core.sheets.principal.IUserExtended.__identifier__:
                 {'email': user_email},
                 }
    user = registry.content.create(ISystemUser.__identifier__,
                                   users,
                                   appstruct,
                                   run_after_creation=False,
                                   send_event=False,
                                   registry=registry)
    user.activate()


root_meta = organisation_meta._replace(
    iresource=IRootPool,
    after_creation=(create_initial_content_for_app_root,
                    add_example_process,),
    is_implicit_addable=False,
)


def includeme(config):
    """Add resource types to registry."""
    add_resource_type_to_registry(root_meta, config)
