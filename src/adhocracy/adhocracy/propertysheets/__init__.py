from zope.interface import (
    implementer,
    )
from zope.dottedname.resolve import resolve
from pyramid.interfaces import IRequest
from substanced.interfaces import IPropertySheet

from adhocracy.property import PropertySheetAdhocracyContent
from adhocracy import propertysheets

# PropertySheet adapters
# read sdi/views/property for adapter lookup examples

@implementer(IPropertySheet)
def propertysheet_iname_adapter(context, request):
    schema_dotted = propertysheets.interfaces.IName.getTaggedValue('schema')
    schema = resolve(schema_dotted)
    sheet = PropertySheetAdhocracyContent(context, request)
    sheet.schema = schema()
    return sheet


@implementer(IPropertySheet)
def propertysheet_iversionable_adapter(context, request):
    schema_dotted = propertysheets.interfaces.IVersionable.getTaggedValue('schema')
    schema = resolve(schema_dotted)
    sheet = PropertySheetAdhocracyContent(context, request)
    sheet.schema = schema()
    return sheet


@implementer(IPropertySheet)
def propertysheet_idocument_adapter(context, request):
    schema_dotted = propertysheets.interfaces.IDocument.getTaggedValue('schema')
    schema = resolve(schema_dotted)
    sheet = PropertySheetAdhocracyContent(context, request)
    sheet.schema = schema()
    return sheet


@implementer(IPropertySheet)
def propertysheet_itext_adapter(context, request):
    schema_dotted = propertysheets.interfaces.IText.getTaggedValue('schema')
    schema = resolve(schema_dotted)
    sheet = PropertySheetAdhocracyContent(context, request)
    sheet.schema = schema()
    return sheet


def includeme(config): # pragma: no cover

    # TODO more DRY for adapter registration
    config.registry.registerAdapter(
        propertysheet_iname_adapter,
        (propertysheets.interfaces.IName, IRequest),
        IPropertySheet,
        propertysheets.interfaces.IName.__identifier__)

    config.registry.registerAdapter(
        propertysheet_iversionable_adapter,
        (propertysheets.interfaces.IVersionable, IRequest),
        IPropertySheet,
        propertysheets.interfaces.IVersionable.__identifier__)

    config.registry.registerAdapter(
        propertysheet_idocument_adapter,
        (propertysheets.interfaces.IDocument, IRequest),
        IPropertySheet,
        propertysheets.interfaces.IDocument.__identifier__)

    config.registry.registerAdapter(
        propertysheet_itext_adapter,
        (propertysheets.interfaces.IText, IRequest),
        IPropertySheet,
        propertysheets.interfaces.IText.__identifier__)
