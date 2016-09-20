""":term:`local roles` sheet."""
from colander import OneOf
from colander import drop
from colander import required
from colander import deferred
from deform.widget import SelectWidget
from substanced.util import find_service

from adhocracy_core.authorization import get_local_roles
from adhocracy_core.authorization import set_local_roles
from adhocracy_core.interfaces import ISheet
from adhocracy_core.interfaces import ISheetReferenceAutoUpdateMarker
from adhocracy_core.sheets import AnnotationRessourceSheet
from adhocracy_core.sheets import add_sheet_to_registry
from adhocracy_core.sheets import sheet_meta
from adhocracy_core.schema import ACEPrincipals
from adhocracy_core.schema import MappingSchema
from adhocracy_core.schema import SequenceSchema
from adhocracy_core.schema import SingleLine


class ILocalRoles(ISheet, ISheetReferenceAutoUpdateMarker):
    """Marker interface for the local_roles sheet."""


class GroupID(SingleLine):
    """:term:`groupid` ."""

    missing = required

    @deferred
    def validator(self, kw: dict):
        from adhocracy_core.resources.principal import IGroup
        context = kw['context']
        groups = find_service(context, 'principals', 'groups')
        groupids = ['group:' + x for x, y in groups.items()
                    if IGroup.providedBy(y)]
        return OneOf(groupids)

    @deferred
    def widget(self, kw: dict) -> []:
        """Return widget  based on the `/principals/groups` service."""
        from adhocracy_core.resources.principal import IGroup
        context = kw['context']
        groups = find_service(context, 'principals', 'groups')
        values = [('group:' + x, x) for x, y in groups.items()
                  if IGroup.providedBy(y)]
        return SelectWidget(values=values)


class LocalRole(MappingSchema):
    """Local role entry."""

    principal = GroupID()
    roles = ACEPrincipals()


class LocalRoles(SequenceSchema):
    """Local role entries."""

    local_role = LocalRole()


class LocalRolesSchema(MappingSchema):
    """LocalRoles sheet data structure.

    `local_roles`: :term:`local roles`
    """

    local_roles = LocalRoles(missing=drop)


class LocalRolesSheet(AnnotationRessourceSheet):
    """Sheet to set/get local roles."""

    def _get_data_appstruct(self):
        roles = get_local_roles(self.context)
        roles_list = [{'principal': x, 'roles': list(y)}
                      for x, y in roles.items()]
        return {'local_roles': roles_list}

    def _store_data(self, appstruct):
        roles_list = appstruct.get('local_roles', [])
        if not roles_list:
            return
        roles = {x['principal']: set(x['roles']) for x in roles_list}
        set_local_roles(self.context, roles, self.registry)


local_roles_meta = sheet_meta._replace(
    isheet=ILocalRoles,
    schema_class=LocalRolesSchema,
    sheet_class=LocalRolesSheet,
    creatable=False,
    permission_edit='manage_sheet_local_roles',
    permission_view='manage_sheet_local_roles',
)


def includeme(config):
    """Register sheets."""
    add_sheet_to_registry(local_roles_meta, config.registry)
