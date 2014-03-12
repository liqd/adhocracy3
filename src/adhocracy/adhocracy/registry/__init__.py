"""Content registry."""
from adhocracy.interfaces import IResourcePropertySheet
from adhocracy.interfaces import ISheet
from adhocracy.utils import get_all_taggedvalues
from adhocracy.utils import get_resource_interface
from adhocracy.resources import ResourceFactory
from adhocracy.interfaces import IResource
from pyramid.security import has_permission
from pyramid.path import DottedNameResolver
from substanced.content import ContentRegistry
from zope.interface import providedBy


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
        sheets = {}
        ifaces = [i for i in providedBy(context) if i.isOrExtends(ISheet)]
        for iface in ifaces:
            sheet = self.registry.getMultiAdapter((context, iface),
                                                  IResourcePropertySheet)
            if onlyviewable:
                if not has_permission(sheet.permission_view, context, request):
                    continue
            if onlyeditable or onlycreatable or onlymandatorycreatable:
                if not has_permission(sheet.permission_edit, context, request):
                    continue
                if sheet.readonly:
                    continue
            if onlymandatorycreatable:
                if sheet.createmandatory:
                    continue
            sheets[iface.__identifier__] = sheet
        if 'adhocracy.sheets.versions.IVersions' in sheets:
            sheets['adhocracy.sheets.versions.IVersions'].get()
        return sheets

    def sheet_metadata(self, sheets):
        """Get dictionary with metadata about sheets.

        Expects an iterable of types or dotted names listing the sheets to
        retrieve as argument.

        Returns a mapping from sheet identifiers (dotted names) to metadata
        describing the sheet.

        """
        sheet_metadata = {}
        res = DottedNameResolver()

        for sheet in sheets:
            iface = res.maybe_resolve(sheet)
            if iface.isOrExtends(ISheet):
                metadata = get_all_taggedvalues(iface)
            sheet_metadata[iface.__identifier__] = metadata

        return sheet_metadata

    def resource_types(self):
        """Get dictionary with all resource types and metadata.

        Returns:
            dic: resource types

            example::

                {'adhocracy.resources.IResourceA':
                  {
                    'name': "adhocracy.resources.IResourceA",
                    'iface': adhocracy.resource.interface.IResourceA.__class__,
                    'metadata': {"addable_content_interfaces": [...], ...}
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
                    metadata = get_all_taggedvalues(iface)
                    resource_types[type_] = {'name': type_,
                                             'iface': iface,
                                             'metadata': metadata}
            except (ValueError, ImportError):
                pass
        return resource_types

    def resource_addables(self, context, request):
        """Get dictionary with addable resource types.

        Args:
            context (IResource): parent of the wanted child content
            request (IRequest or None): request object for permission checks

        Returns:
            dic: resource types with property sheet names

            The list is generated based on the 'addable_content_interfaces'
            taggedValue, resource type interface inheritage and permissions.

            example::

                {'adhocracy.resources.IResourceA':
                    'sheets_mandatory': ['adhocracy.sheets.example.IA']
                    'sheets_optional': ['adhocracy.sheets.example.IB']
                }

        """
        assert IResource.providedBy(context)
        all_types = self.resource_types()
        name = get_resource_interface(context).__identifier__
        assert name in all_types
        res = DottedNameResolver()
        metadata = all_types[name]['metadata']
        addables = [res.maybe_resolve(i) for i
                    in metadata.get('addable_content_interfaces', [])]
        #get all addable types
        addable_types = []
        for type in all_types.values():
            is_implicit = type['metadata']['is_implicit_addable']
            for i in addables:
                is_subtype = type['iface'].extends(i) and is_implicit
                is_is = type['iface'] is i
                add_permission = type['metadata']['permission_add']
                is_allowed = has_permission(add_permission, context, request)
                if is_subtype or is_is and is_allowed:
                    addable_types.append(type['iface'])
        #add propertysheet names
        types_with_sheetnames = {}
        for type_iface in addable_types:
            sheetnames = {}
            resource = ResourceFactory(type_iface)(context,
                                                   add_to_context=False,
                                                   run_after_creation=False)
            resource.__parent__ = context
            sheets = self.resource_sheets(resource, request,
                                          onlycreatable=True)
            sheetnames['sheets_mandatory'] = \
                [k for k, v in sheets.items() if v.createmandatory]
            sheetnames['sheets_optional'] = \
                [k for k, v in sheets.items() if not v.createmandatory]
            types_with_sheetnames[type_iface.__identifier__] = sheetnames

        return types_with_sheetnames


def includeme(config):  # pragma: no cover
    """Run pyramid config."""
    content_old = config.registry.content
    content_new = ResourceContentRegistry(config.registry)
    content_new.__dict__.update(content_old.__dict__)
    config.registry.content = content_new
