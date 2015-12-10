"""Create resources, get sheets/metadata, permission checks."""
from pyramid.request import Request
from adhocracy_core.content import ResourceContentRegistry
from adhocracy_core.interfaces import ResourceMetadata
from adhocracy_core.interfaces import IPool
from adhocracy_core.utils import has_annotation_sheet_data
from adhocracy_meinberlin.resources.bplan import IProposalVersion


class MeinBerlinResourceContentRegistry(ResourceContentRegistry):
    """Extend content registry to allow anonymous to post bplan versions."""

    def can_add_resource(self, request: Request, meta: ResourceMetadata,
                         context: IPool) -> bool:
        """Check that the resource type in `meta` is addable to `context`.

        For the `bplan` process we want anonymous to create proposal items
        and the first non empty version. To make this work we check
        the item create permission instead of the version create permission if
        the first version is empty (without sheet data).
        """
        if self._is_bplan_and_has_no_version_with_sheet_data(meta, context):
            from adhocracy_core.utils import get_iresource
            iresource = get_iresource(context)
            permission = self.resources_meta[iresource].permission_create
        else:
            permission = meta.permission_create
        allowed = request.has_permission(permission, context)
        return allowed

    def _is_bplan_and_has_no_version_with_sheet_data(self,
                                                     meta: ResourceMetadata,
                                                     context: IPool) -> bool:
        is_bplan_version = meta.iresource.isOrExtends(IProposalVersion)
        if not is_bplan_version:
            return False
        versions_with_data = [x for x in context.values()
                              if IProposalVersion.providedBy(x)
                              and has_annotation_sheet_data(x)]
        return versions_with_data == []


def includeme(config):  # pragma: no cover
    """Override content registry."""
    old_content = config.registry.content
    new_content = MeinBerlinResourceContentRegistry(config.registry)
    new_content.__dict__.update(old_content.__dict__)
    config.registry.content = new_content
