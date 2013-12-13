from adhocracy.utils import get_all_taggedvalues
from adhocracy.resources.interfaces import IResource
from adhocracy.interfaces import IResourcePropertySheet
from adhocracy.properties.interfaces import IProperty
from zope.dottedname.resolve import resolve
from zope.interface import providedBy
from substanced.content import ContentRegistry


class ResourceContentRegistry(ContentRegistry):

    def resource_propertysheets(self, context, request):
        """Return dict with name and ResourcepropertySheet objects."""
        propertysheets = {}
        ifaces = [i for i in providedBy(context) if i.isOrExtends(IProperty)]
        for iface in ifaces:
            sheet = self.registry.getMultiAdapter((context, request, iface),
                                                  IResourcePropertySheet)
            propertysheets[iface.__identifier__] = sheet
        return propertysheets

    def resource_addable_types(self, resource):
        """Return a list with addable adhocracy resource types.

        The list is generated base on the "addable_content_interfaces"
        taggedValue and interface inheritage.

        """
        content_type = self.typeof(resource)
        assert content_type is not None
        all_addables = []
        all_types = {}
        for type in self.all():
            try:
                iface = resolve(type)
                if iface.isOrExtends(IResource):
                    tvalues = get_all_taggedvalues(iface)
                    all_types[type] = (iface, tvalues)
            except ValueError:
                pass
        if content_type in all_types:
            iface, tvalues = all_types[content_type]
            adds = [resolve(t) for t in
                    tvalues.get("addable_content_interfaces", [])]
            for i, t in all_types.values():
                for add in adds:
                    if t["is_implicit_addable"] and i.extends(add):
                        all_addables.append(i.__identifier__)
                    if i is add:
                        all_addables.append(i.__identifier__)
        return all_addables


def includeme(config):  # pragma: no cover
    content_old = config.registry.content
    content_new = ResourceContentRegistry(config.registry)
    content_new.__dict__.update(content_old.__dict__)
    config.registry.content = content_new
