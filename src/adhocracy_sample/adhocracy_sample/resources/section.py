"""Section resource type."""
from adhocracy.interfaces import IItemVersion
from adhocracy.interfaces import IItem
from adhocracy.interfaces import ITag
from adhocracy.resources import add_resource_type_to_registry
from zope.interface import taggedValue


class ISectionVersion(IItemVersion):

    """Document section."""

    taggedValue('extended_sheets',
                set(['adhocracy.sheets.document.ISection']))


class ISection(IItem):

    """Section Versions Pool."""

    taggedValue('element_types', set([ITag, ISectionVersion]))
    taggedValue('item_type', ISectionVersion)


def includeme(config):
    """Register resource type factory in substanced content registry."""
    add_resource_type_to_registry(ISectionVersion, config)
    add_resource_type_to_registry(ISection, config)
