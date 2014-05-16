"""Paragraph resource type."""
from adhocracy.interfaces import IItemVersion
from adhocracy.interfaces import IItem
from adhocracy.interfaces import ITag
from adhocracy.resources import add_resource_type_to_registry
from zope.interface import taggedValue


class IParagraphVersion(IItemVersion):

    """Document paragraph (a leaf in the section tree)."""

    taggedValue('extended_sheets',
                set(['adhocracy.sheets.document.IParagraph']))


class IParagraph(IItem):

    """Paragraph Versions Pool."""

    taggedValue('element_types', set([ITag, IParagraphVersion]))
    taggedValue('item_type', IParagraphVersion)


def includeme(config):
    """Register resource type factory in substanced content registry."""
    add_resource_type_to_registry(IParagraph, config)
    add_resource_type_to_registry(IParagraphVersion, config)
