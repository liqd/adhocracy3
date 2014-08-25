"""Content registry."""
from pyramid.security import has_permission
from pyramid.request import Request
from substanced.content import ContentRegistry
from substanced.content import add_content_type
from substanced.content import add_service_type

from adhocracy.utils import get_iresource
from adhocracy.utils import get_all_sheets


class ResourceContentRegistry(ContentRegistry):

    """Extend substanced content registry to work with resources."""

    def __init__(self, registry):
        super().__init__(registry)
        self.resources_meta = {}
        """Dictionary with key `resource type` and value
        :class:`adhocracy.interfaces.ResourceMetadata`.
        """
        self.sheets_meta = {}
        """Dictionary with key `resource type` and value
        :class:`adhocracy.interfaces.SheetMetadata`.
        """

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
        assert iresource.__identifier__ in self.resources_meta
        metadata = self.resources_meta[iresource.__identifier__]
        addables = metadata.element_types
        # get all addable types
        addable_types = []
        for metdata in self.resources_meta.values():
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
    """Add content registry, register substanced content_type decorators."""
    config.registry.content = ResourceContentRegistry(config.registry)
    config.add_directive('add_content_type', add_content_type)
    config.add_directive('add_service_type', add_service_type)
    # FIXME we cannot add the substanced view_predicate `content_type` here,
    # this conflicts with _:class:`cornice.ContentTypePredicate`
