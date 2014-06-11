"""Content registry."""
from pyramid.security import has_permission
from pyramid.path import DottedNameResolver
from pyramid.testing import DummyResource
from pyramid.request import Request
from substanced.content import ContentRegistry

from adhocracy.interfaces import IResource
from adhocracy.utils import get_iresource
from adhocracy.utils import get_all_sheets
from adhocracy.utils import get_sheet


class ResourceContentRegistry(ContentRegistry):

    """Extend substanced content registry to work with resources."""

    def resource_sheets(self, context, request,
                        onlyeditable=False,
                        onlyviewable=False,
                        onlycreatable=False,
                        onlymandatorycreatable=False):
        """Get dict with ResourcePropertySheet key/value.

        Args:
            context (IResource): context to list property sheets
            request (IRequest or None): request object for permission checks

        Returns:
            dic: key - sheet name (interface identifier), value - sheet object.

        """
        wanted_sheets = {}
        for sheet in get_all_sheets(context):
            can_view = has_permission(sheet.meta.permission_view, context,
                                      request)
            if onlyviewable:
                if not sheet.meta.readable or not can_view:
                    continue
            can_edit = has_permission(sheet.meta.permission_edit, context,
                                      request)
            if onlyeditable:
                if not sheet.meta.editable or not can_edit:
                    continue
            can_create = has_permission(sheet.meta.permission_create, context,
                                        request)
            if onlycreatable:
                if not sheet.meta.creatable or not can_create:
                    continue
            if onlymandatorycreatable:
                if not sheet.meta.create_mandatory:
                    continue
            wanted_sheets[sheet.meta.isheet.__identifier__] = sheet
        return wanted_sheets

    def resources_metadata(self) -> dict:
        """Get resource types with resource_metadata."""
        resource_types = {}
        resolve = DottedNameResolver()
        for type_id, type_metadata in self.meta.items():
            try:
                iresource = resolve.maybe_resolve(type_id)
                if iresource.isOrExtends(IResource):
                    metadata = type_metadata['resource_metadata']
                    resource_types[type_id] = metadata
            except (ValueError, ImportError):
                pass
        return resource_types

    def sheets_metadata(self):
        """Get dictionary with all sheet metadata.

        Returns:
            dict: key = isheet identifier (dotted_name),
                  value = isheet metadata

        """
        isheets = set()
        for resource_meta in self.resources_metadata().values():
            isheets.update(resource_meta.basic_sheets)
            isheets.update(resource_meta.extended_sheets)

        isheets_meta = {}
        for isheet in isheets:
            dummy_context = DummyResource(__provides__=isheet)
            sheet = get_sheet(dummy_context, isheet)
            isheets_meta[isheet.__identifier__] = sheet.meta

        return isheets_meta

    def resource_addables(self, context, request: Request) -> dict:
        """Get dictionary with addable resource types.

        :param context: parent of the wanted child content
        :param request: request or None for permission checks

        :returns: resource types with sheet identifier

        The  sheet identifiers are generated based on the 'element_types'
        resource type metadata, resource type inheritage and local permissions.

        example ::

            {'adhocracy.resources.IResourceA':
                'sheets_mandatory': ['adhocracy.sheets.example.IA']
                'sheets_optional': ['adhocracy.sheets.example.IB']
            }

        """
        iresource = get_iresource(context)
        if iresource is None:
            return {}
        resources_metadata = self.resources_metadata()
        assert iresource.__identifier__ in resources_metadata
        metadata = resources_metadata[iresource.__identifier__]
        addables = metadata.element_types
        # get all addable types
        addable_types = []
        for metdata in resources_metadata.values():
            is_implicit = metdata.is_implicit_addable
            for addable in addables:
                is_subtype = is_implicit and metdata.iresource.extends(addable)
                is_is = metdata.iresource is addable
                add_permission = metdata.permission_add
                is_allowed = has_permission(add_permission, context, request)
                if is_subtype or is_is and is_allowed:
                    addable_types.append(metdata.iresource)
        # add propertysheet names
        types_with_sheetnames = {}
        for type_iface in addable_types:
            sheetnames = {}
            dummy_resource = self.create(type_iface.__identifier__,
                                         run_after_creation=False)
            dummy_resource.__parent__ = context
            sheets = self.resource_sheets(dummy_resource, request,
                                          onlycreatable=True)
            sheetnames['sheets_mandatory'] = \
                [k for k, v in sheets.items() if v.meta.create_mandatory]
            sheetnames['sheets_optional'] = \
                [k for k, v in sheets.items() if not v.meta.create_mandatory]
            types_with_sheetnames[type_iface.__identifier__] = sheetnames

        return types_with_sheetnames


def includeme(config):  # pragma: no cover
    """Run pyramid config."""
    content_old = config.registry.content
    content_new = ResourceContentRegistry(config.registry)
    content_new.__dict__.update(content_old.__dict__)
    config.registry.content = content_new
