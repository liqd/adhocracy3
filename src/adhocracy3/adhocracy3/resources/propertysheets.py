from zope.interface import (
    implementer,
    )
from zope.component import adapter
from substanced.interfaces import IPropertySheet

from adhocracy3.property import PropertySheetAdhocracyContent
from adhocracy3.resources import interfaces


@implementer(IPropertySheet)
@adapter(interfaces.IName)
def propertysheet_iname_adapter(context):
    schema = interfaces.IPool.getTaggedValue('schema')
    sheet = PropertySheetAdhocracyContent(context)
    sheet.schema = schema
    return sheet


@implementer(IPropertySheet)
@adapter(interfaces.IVersionable)
def propertysheet_iversionable_adapter(context):
    schema = interfaces.IVersionable.getTaggedValue('schema')
    sheet = PropertySheetAdhocracyContent(context)
    sheet.schema = schema
    return sheet


@implementer(IPropertySheet)
@adapter(interfaces.IText)
def propertysheet_itext_adapter(context):
    schema = interfaces.IText.getTaggedValue('schema')
    sheet = PropertySheetAdhocracyContent(context)
    sheet.schema = schema
    return sheet


def includeme(config): # pragma: no cover

    # TODO more DRY for adapter registration
    config.registry.registerAdapter(
        propertysheet_iname_adapter,
        (interfaces.IPool),
        IPropertySheet,
        interfaces.IPool.__identifier__)

    config.registry.registerAdapter(
        propertysheet_iversionable_adapter,
        (interfaces.IVersionable),
        IPropertySheet,
        interfaces.IVersionable.__identifier__)

    config.registry.registerAdapter(
        propertysheet_itext_adapter,
        (interfaces.IText),
        IPropertySheet,
        interfaces.IText.__identifier__)
