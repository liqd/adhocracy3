"""Content registry."""
from pyramid.security import has_permission
from pyramid.path import DottedNameResolver
from pyramid.testing import DummyResource
from substanced.content import ContentRegistry

from adhocracy.interfaces import IResource
from adhocracy.utils import get_resource_interface
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
        assert IResource.providedBy(context)
        wanted_sheets = {}
        for sheet in get_all_sheets(context):
            can_view = has_permission(sheet.meta.permission_view, context,
                                      request)
            can_edit = has_permission(sheet.meta.permission_edit, context,
                                      request)
            if onlyviewable and not can_view:
                continue
            if onlyeditable or onlycreatable or onlymandatorycreatable:
                if sheet.meta.readonly or not can_edit:
                    continue
            if onlymandatorycreatable:
                if not sheet.meta.createmandatory:
                    continue
            wanted_sheets[sheet.meta.isheet.__identifier__] = sheet
        return wanted_sheets

    def resources_metadata(self):
        """Get dictionary with all resource types and metadata.

        Returns:
            dict: resource types

            example::

                {'adhocracy.resources.IResourceA':
                  {
                    'name': "adhocracy.resources.IResourceA",
                    'iface': adhocracy.resource.interface.IResourceA.__class__,
                    'metadata': {"element_types": [...], ...}
                  }
                  ...
                }

        """
        resource_types = {}
        res = DottedNameResolver()
        for type_ in self.all():
            try:
                iface = res.maybe_resolve(type_)
                if iface.isOrExtends(IResource):
                    metadata = self.meta[type_]['resource_metadata']
                    resource_types[type_] = {'name': type_,
                                             'iface': iface,
                                             'metadata': metadata}
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
        resources = self.resources_metadata()
        resources_meta = [x['metadata'] for x in resources.values()]
        for resource in resources_meta:
            isheets.update(resource.basic_sheets)
            isheets.update(resource.extended_sheets)

        isheets_meta = {}
        for isheet in isheets:
            dummy_context = DummyResource(__provides__=isheet)
            sheet = get_sheet(dummy_context, isheet)
            isheets_meta[isheet.__identifier__] = sheet.meta

        return isheets_meta

    def resource_addables(self, context, request):
        """Get dictionary with addable resource types.

        Args:
            context (IResource): parent of the wanted child content
            request (IRequest or None): request object for permission checks

        Returns:
            dic: resource types with property sheet names

            The list is generated based on the 'element_types'
            taggedValue, resource type interface inheritage and permissions.

            example::

                {'adhocracy.resources.IResourceA':
                    'sheets_mandatory': ['adhocracy.sheets.example.IA']
                    'sheets_optional': ['adhocracy.sheets.example.IB']
                }

        """
        assert IResource.providedBy(context)
        all_types = self.resources_metadata()
        name = get_resource_interface(context).__identifier__
        assert name in all_types
        metadata = all_types[name]['metadata']
        addables = metadata.element_types
        #get all addable types
        addable_types = []
        for type in all_types.values():
            is_implicit = type['metadata'].is_implicit_addable
            for i in addables:
                is_subtype = type['iface'].extends(i) and is_implicit
                is_is = type['iface'] is i
                add_permission = type['metadata'].permission_add
                is_allowed = has_permission(add_permission, context, request)
                if is_subtype or is_is and is_allowed:
                    addable_types.append(type['iface'])
        #add propertysheet names
        types_with_sheetnames = {}
        for type_iface in addable_types:
            sheetnames = {}
            dummy_resource = self.create(type_iface.__identifier__,
                                         run_after_creation=False)
            dummy_resource.__parent__ = context
            sheets = self.resource_sheets(dummy_resource, request,
                                          onlycreatable=True)
            sheetnames['sheets_mandatory'] = \
                [k for k, v in sheets.items() if v.meta.createmandatory]
            sheetnames['sheets_optional'] = \
                [k for k, v in sheets.items() if not v.meta.createmandatory]
            types_with_sheetnames[type_iface.__identifier__] = sheetnames

        return types_with_sheetnames


def includeme(config):  # pragma: no cover
    """Run pyramid config."""
    content_old = config.registry.content
    content_new = ResourceContentRegistry(config.registry)
    content_new.__dict__.update(content_old.__dict__)
    config.registry.content = content_new
