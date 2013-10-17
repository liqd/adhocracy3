from zope.dottedname.resolve import resolve
from pyramid.interfaces import IRequest
from substanced.interfaces import IPropertySheet

from adhocracy.property import PropertySheetAdhocracyContent
from adhocracy.propertysheets import interfaces

# PropertySheet adapters
# read sdi/views/property for adapter lookup examples

class PropertysheetGenericAdapter:

    def __init__(self, propsheetmarker_iface):
        self.propsheetmarker_iface = propsheetmarker_iface

    def __call__(self, context, request):
        schema_dotted = self.propsheetmarker_iface.getTaggedValue('schema')
        schema = resolve(schema_dotted)
        sheet = PropertySheetAdhocracyContent(context, request)
        sheet.schema = schema()
        return sheet


def includeme(config): # pragma: no cover

    # get all IPropertySheetMarker interfaces
    # inspect.isclass is not working with interfaces,
    # so we have to do it manually
    propsheetmarker_ifaces = []
    for key in dir(interfaces):
        value = getattr(interfaces, key)
        if value is interfaces.IPropertySheetMarker:
            continue
        try:
            if issubclass(value, interfaces.IPropertySheetMarker):
                propsheetmarker_ifaces.append(value)
        except TypeError:
            continue
    # register generic adapter for all IPropertySheetMarkers
    for iface in propsheetmarker_ifaces:
        config.registry.registerAdapter(
            PropertysheetGenericAdapter(iface),
            (iface, IRequest),
            IPropertySheet,
            iface.__identifier__)
