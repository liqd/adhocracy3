"""Paragraph resource type."""
from adhocracy.interfaces import IItemVersion
from adhocracy.interfaces import IItem
from adhocracy.interfaces import ITag
from adhocracy.resources import add_resource_type_to_registry
from adhocracy.resources.itemversion import itemversion_metadata
from adhocracy.resources.item import item_metadata

import adhocracy.sheets.document


class IParagraphVersion(IItemVersion):

    """Document paragraph (a leaf in the paragraph tree)."""


paragraphversion_meta = itemversion_metadata._replace(
    content_name='ParagraphVersion',
    iresource=IParagraphVersion,
    extended_sheets=[adhocracy.sheets.document.IParagraph,
                     ],
)


class IParagraph(IItem):

    """Paragraph Versions Pool."""


paragraph_meta = item_metadata._replace(
    content_name='Paragraph',
    iresource=IParagraph,
    element_types=[ITag,
                   IParagraphVersion,
                   ],
    item_type=IParagraphVersion,
)


def includeme(config):
    """Add resource type to registry."""
    add_resource_type_to_registry(paragraph_meta, config)
    add_resource_type_to_registry(paragraphversion_meta, config)
