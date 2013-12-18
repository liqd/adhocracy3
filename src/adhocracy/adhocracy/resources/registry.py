from adhocracy.utils import get_all_taggedvalues
from adhocracy.resources.interfaces import IResource
from adhocracy.interfaces import IResourcePropertySheet
from adhocracy.properties.interfaces import IProperty
from pyramid.security import has_permission
from zope.dottedname.resolve import resolve
from zope.interface import providedBy
from substanced.content import ContentRegistry


class ResourceContentRegistry(ContentRegistry):

    def resource_propertysheets(self, context, request,
                                onlyeditable=False,
                                onlyviewable=False):
        """Return dict with name and ResourcepropertySheet objects."""
        propertysheets = {}
        ifaces = [i for i in providedBy(context) if i.isOrExtends(IProperty)]
        for iface in ifaces:
            sheet = self.registry.getMultiAdapter((context, request, iface),
                                                  IResourcePropertySheet)
            if onlyviewable:
                permission = getattr(sheet, "permission_view")
                if not has_permission(permission, context, request):
                    continue
            if onlyeditable:
                permission = getattr(sheet, "permission_edit")
                if not has_permission(permission, context, request):
                    continue
                if getattr(sheet, "readonly"):
                    continue
            propertysheets[iface.__identifier__] = sheet
        return propertysheets

    def resource_addable_types(self, resource):
        """Return a dictionary with addable resource types and iproperties.

        The list is generated base on the "addable_content_interfaces"
        taggedValue and interface inheritage.

        """
        type = self.typeof(resource)
        assert type is not None
        all_types = {}
        # get all resource types
        for type_ in self.all():
            try:
                iface = resolve(type_)
                if iface.isOrExtends(IResource):
                    tvalues = get_all_taggedvalues(iface)
                    all_types[type_] = (iface, tvalues)
            except (ValueError, ImportError):
                pass
        # get all addable resource types and map iproperties
        all_addables = []
        if type in all_types:
            addables_ = all_types[type][1].get("addable_content_interfaces",
                                               [])
            addables = [resolve(a) for a in addables_]
            for type_ in all_types:
                iface = all_types[type_][0]
                tvalues = all_types[type_][1]
                # get resource type propertysheet interfaces
                sheet_names = tvalues["basic_properties_interfaces"]\
                    .union(tvalues["extended_properties_interfaces"])
                sheets_no_readonly = set([])
                for sheet_name in sheet_names:
                    sheet_iface = resolve(sheet_name)
                    sheet_tvalues = get_all_taggedvalues(sheet_iface)
                    readonly = sheet_tvalues["readonly"]
                    if not readonly:
                        sheets_no_readonly.add(sheet_name)
                # check resource type inheritance and add
                is_implicit = tvalues["is_implicit_addable"]
                for addable in addables:
                    is_extending = iface.extends(addable)
                    is_is = iface is addable
                    if is_implicit and is_extending or is_is:
                        all_addables.append((iface.__identifier__,
                                             sheets_no_readonly))
        return dict(all_addables)


def includeme(config):  # pragma: no cover
    content_old = config.registry.content
    content_new = ResourceContentRegistry(config.registry)
    content_new.__dict__.update(content_old.__dict__)
    config.registry.content = content_new
