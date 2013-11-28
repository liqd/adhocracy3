from zope.dottedname.resolve import resolve
from pyramid.interfaces import IRequest
from substanced.interfaces import IPropertySheet

from adhocracy.property import PropertySheetAdhocracyContent
from adhocracy.propertysheets import interfaces

# PropertySheet adapters
# read sdi/views/property for adapter lookup examples

class PropertysheetGenericAdapter:

    def __init__(self, propertysheet_interf):
        self.propertysheet_interf = propertysheet_interf

    def __call__(self, context, request):
        import pdb; pdb.set_trace
        schema_dotted = self.propertysheet_interf.getTaggedValue('schema')
        schema = resolve(schema_dotted)
        sheet = PropertySheetAdhocracyContent(context, request)
        sheet.schema = schema()
        return sheet


def includeme(config): # pragma: no cover

    ## TODO auto generate
    config.registry.registerAdapter(
        PropertysheetGenericAdapter(interfaces.IName),
        (interfaces.IName, IRequest),
        IPropertySheet,
        interfaces.IName.__identifier__)

    config.registry.registerAdapter(
        PropertysheetGenericAdapter(interfaces.IVersionable),
        (interfaces.IVersionable, IRequest),
        IPropertySheet,
        interfaces.IVersionable.__identifier__)

    config.registry.registerAdapter(
        PropertysheetGenericAdapter(interfaces.IDocument),
        (interfaces.IDocument, IRequest),
        IPropertySheet,
        interfaces.IDocument.__identifier__)

    config.registry.registerAdapter(
        PropertysheetGenericAdapter(interfaces.IText),
        (interfaces.IText, IRequest),
        IPropertySheet,
        interfaces.IText.__identifier__)
