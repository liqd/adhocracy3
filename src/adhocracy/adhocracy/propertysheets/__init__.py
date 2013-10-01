from zope.dottedname.resolve import resolve
from pyramid.interfaces import IRequest
from substanced.interfaces import IPropertySheet

from adhocracy.property import PropertySheetAdhocracyContent
from adhocracy.propertysheets import interfaces

# PropertySheet adapters
# read sdi/views/property for adapter lookup examples

class PropertysheetGenericAdapter:

    def __init__(self, isheetmarker):
        self.isheetmarker = isheetmarker

    def __call__(self, context, request):
        schema_dotted = self.isheetmarker.getTaggedValue('schema')
        schema = resolve(schema_dotted)
        sheet = PropertySheetAdhocracyContent(context, request)
        sheet.schema = schema()
        return sheet


def includeme(config): # pragma: no cover

    # get all IPropertySheetMarker interfaces
    # inspect.isclass is not working with interfaces,
    # so we have to do it manually
    isheetmarkers = []
    for key in dir(interfaces):
        try:
            value = getattr(interfaces, key)
            if value is interfaces.IPropertySheetMarker:
                continue
            if issubclass(value, interfaces.IPropertySheetMarker):
                isheetmarkers.append(value)
        except TypeError:
            continue
    # register generic adapter for all IPropertySheetMarkers
    for isheetmarker in isheetmarkers:
        config.registry.registerAdapter(
            PropertysheetGenericAdapter(isheetmarker),
            (isheetmarker, IRequest),
            IPropertySheet,
            isheetmarker.__identifier__)
