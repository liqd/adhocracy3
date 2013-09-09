from zope.interface import (
    implementer,
    )
from zope.dottedname.resolve import resolve
from pyramid.interfaces import IRequest
from substanced.interfaces import IPropertySheet

from adhocracy.property import PropertySheetAdhocracyContent
from adhocracy import interfaces

# PropertySheet adapters
# read sdi/views/property for adapter lookup examples

@implementer(IPropertySheet)
def propertysheet_iname_adapter(context, request):
    schema_dotted = interfaces.IName.getTaggedValue('schema')
    schema = resolve(schema_dotted)
    sheet = PropertySheetAdhocracyContent(context, request)
    sheet.schema = schema()
    return sheet


@implementer(IPropertySheet)
def propertysheet_iversionable_adapter(context, request):
    schema_dotted = interfaces.IVersionable.getTaggedValue('schema')
    schema = resolve(schema_dotted)
    sheet = PropertySheetAdhocracyContent(context, request)
    sheet.schema = schema()
    return sheet


@implementer(IPropertySheet)
def propertysheet_itext_adapter(context, request):
    schema_dotted = interfaces.IDocument.getTaggedValue('schema')
    schema = resolve(schema_dotted)
    sheet = PropertySheetAdhocracyContent(context, request)
    sheet.schema = schema()
    return sheet


def includeme(config): # pragma: no cover

    # TODO more DRY for adapter registration
    config.registry.registerAdapter(
        propertysheet_iname_adapter,
        (interfaces.IName, IRequest),
        IPropertySheet,
        interfaces.IName.__identifier__)

    config.registry.registerAdapter(
        propertysheet_iversionable_adapter,
        (interfaces.IVersionable, IRequest),
        IPropertySheet,
        interfaces.IVersionable.__identifier__)

    config.registry.registerAdapter(
        propertysheet_itext_adapter,
        (interfaces.IDocument, IRequest),
        IPropertySheet,
        interfaces.IDocument.__identifier__)
