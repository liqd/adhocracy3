"""Root type to create initial object hierarchy and set global Permissions."""
from pyramid.registry import Registry
from pyramid.security import Allow
from substanced.interfaces import IRoot
from substanced.objectmap import ObjectMap
from substanced.util import set_acl
from substanced.util import find_service

from adhocracy_core.interfaces import IResource
from adhocracy_core.interfaces import IPool
from adhocracy_core.resources import add_resource_type_to_registry
from adhocracy_core.resources.pool import pool_meta
from adhocracy_core.resources.pool import IBasicPool
from adhocracy_core.resources.principal import IPrincipalsService
from adhocracy_core.resources.principal import IUser
from adhocracy_core.resources.principal import IGroup
from adhocracy_core.authorization import acm_to_acl
from adhocracy_core.schema import ACM
from adhocracy_core.resources.geo import add_locations_service
from adhocracy_core.catalog import ICatalogsService
import adhocracy_core.sheets.principal
import adhocracy_core.sheets.name


# Access Control Matrix. Permissions are mapped to a role.
# Every role should only have the permission for the specific actions it is
# meant to enable.
root_acm = ACM().deserialize(
    {'principals':                                   ['Everyone', 'annotator', 'contributor', 'creator', 'manager', 'admin', 'god'],  # noqa
     'permissions': [['add_asset',                     None,       Allow,       None,          None,      None,      None,    Allow],  # noqa
                     ['add_comment',                   None,       Allow,       None,          None,      None,      None,    Allow],  # noqa
                     ['add_commentversion',            None,       None,        None,          Allow,     None,      None,    Allow],  # noqa
                     ['add_externalresource',          None,       None,        Allow,         None,      None,      None,    Allow],  # noqa
                     ['add_group',                     None,       None,        None,          None,      None,      Allow,   Allow],  # noqa
                     ['add_paragraph',                 None,       None,        Allow,         None,      None,      None,    Allow],  # noqa
                     ['add_paragraphversion',          None,       None,        None,          Allow,     None,      None,    Allow],  # noqa
                     ['add_pool',                      None,       None,        None,          None,      None,      Allow,   Allow],  # noqa
                     ['add_proposal',                  None,       None,        Allow,         None,      None,      None,    Allow],  # noqa
                     ['add_proposalversion',           None,       None,        None,          Allow,     None,      None,    Allow],  # noqa
                     ['add_rate',                      None,       Allow,       None,          None,      None,      None,    Allow],  # noqa
                     ['add_rateversion',               None,       None,        None,          Allow,     None,      None,    Allow],  # noqa
                     ['add_resource',                  None,       Allow,       Allow,         None,      None,      Allow,   Allow],  # noqa
                     ['add_section',                   None,       None,        Allow,         None,      None,      None,    Allow],  # noqa
                     ['add_sectionversion',            None,       None,        None,          Allow,     None,      None,    Allow],  # noqa
                     ['add_user',                      Allow,      None,        None,          None,      None,      None,    Allow],  # noqa
                     ['create_sheet',                  None,       Allow,       Allow,         None,      None,      Allow,   Allow],  # noqa
                     ['create_sheet_password',         Allow,      None,        None,          None,      None,      None,    Allow],  # noqa
                     ['create_sheet_userbasic',        Allow,      None,        None,          None,      None,      None,    Allow],  # noqa
                     ['edit_group',                    None,       None,        None,          None,      None,      Allow,   Allow],  # noqa
                     ['edit_metadata',                 None,       None,        None,          Allow,     Allow,     None,    Allow],  # noqa
                     ['edit_sheet',                    None,       None,        None,          None,      None,      Allow,   Allow],  # noqa
                     ['edit_some_sheets',              None,       None,        None,          Allow,     Allow,     Allow,   Allow],  # noqa
                     ['edit_userextended',             None,       None,        None,          Allow,     None,      Allow,   Allow],  # noqa
                     ['hide_resource',                 None,       None,        None,          None,      Allow,     None,    Allow],  # noqa
                     ['manage_principals',             None,       None,        None,          None,      None,      Allow,   Allow],  # noqa
                     ['message_to_user',               None,       None,        Allow,         None,      None,      None,    Allow],  # noqa
                     ['view',                          Allow,      Allow,       Allow,         None,      Allow,     Allow,   Allow],  # noqa
                     ['view_sensitive',                None,       None,        None,          None,      None,      Allow,   Allow],  # noqa
                     ['view_userextended',             None,       None,        None,          Allow,     None,      Allow,   Allow],  # noqa
                     ['do_transition',                 None,       None,        None,          None,      None,      None,    Allow],  # noqa
                     # FIXME, move to meinberlin module
                     ['add_kiezkassen_proposal_version',  None,       None,        None,          None,      None,      None,    Allow],  # noqa
                     ['add_kiezkassen_process',           None,       None,        None,          None,      None,      None,    Allow]  # noqa
                     ]})


class IRootPool(IPool, IRoot):

    """The application root object."""


def create_initial_content_for_app_root(context: IPool, registry: Registry,
                                        options: dict):
    """Add the platform object, Catalog, principals services to the context."""
    _add_objectmap_to_app_root(context)
    _add_graph(context, registry)
    _add_catalog_service(context, registry)
    _add_principals_service(context, registry)
    _add_acl_to_app_root(context, registry)
    _add_default_group(context, registry)
    _add_initial_user_and_group(context, registry)
    add_locations_service(context, registry, {})


def _add_objectmap_to_app_root(root):
    root.__objectmap__ = ObjectMap(root)
    root.__objectmap__.add(root, ('',))


def _add_graph(context, registry):
    graph = registry.content.create('Graph', context)
    context.__graph__ = graph


def _add_catalog_service(context, registry):
    registry.content.create(ICatalogsService.__identifier__, parent=context)


def _add_principals_service(context, registry):
    registry.content.create(IPrincipalsService.__identifier__,
                            parent=context,
                            registry=registry)


def _add_acl_to_app_root(context, registry):
    acl = acm_to_acl(root_acm, registry)
    set_acl(context, acl, registry=registry)


def add_platform(context, registry, platform_id=None,
                 resource_type: IResource=IBasicPool):
    """Register the platform in the content registry."""
    if platform_id is None:
        platform_id = registry.settings.get('adhocracy.platform_id',
                                            'adhocracy')
    appstructs = {'adhocracy_core.sheets.name.IName': {'name': platform_id}}
    registry.content.create(resource_type.__identifier__, context,
                            appstructs=appstructs, registry=registry)


def _add_adhocracy_platform(context: IPool, registry: Registry,
                            options: dict):
    add_platform(context, registry)


def _add_default_group(context, registry):
    if not registry.settings.get('adhocracy.add_default_group',
                                 True):  # pragma: no cover
        return
    # the 'app' fixture in adhocracy_core.testing does not work with
    # setting a default group. So we allow to disable here.
    group_name = 'authenticated'
    group_roles = ['reader', 'annotator', 'contributor']
    # TODO these rules only makes sense for mercator
    #      groups should be created with an evolve script
    groups = find_service(context, 'principals', 'groups')
    appstructs = {adhocracy_core.sheets.principal.IGroup.__identifier__:
                  {'roles': group_roles},
                  adhocracy_core.sheets.name.IName.__identifier__:
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
    user = registry.content.create(IUser.__identifier__, users, appstruct,
                                   run_after_creation=False,
                                   registry=registry)

    user.activate()


root_meta = pool_meta._replace(
    iresource=IRootPool,
    after_creation=[create_initial_content_for_app_root,
                    _add_adhocracy_platform]
)


def includeme(config):
    """Add resource types to registry."""
    add_resource_type_to_registry(root_meta, config)
