"""Paragraph resource type."""
from adhocracy_core.interfaces import IItemVersion
from adhocracy_core.interfaces import IItem
from adhocracy_core.interfaces import ITag
from adhocracy_core.resources import add_resource_type_to_registry
from adhocracy_core.resources.itemversion import itemversion_meta
from adhocracy_core.resources.item import item_meta

import adhocracy_core.sheets.document


class IParagraphVersion(IItemVersion):

    """Document paragraph (a leaf in the paragraph tree)."""


paragraphversion_meta = itemversion_meta._replace(
    content_name='ParagraphVersion',
    iresource=IParagraphVersion,
    basic_sheets=[adhocracy_core.sheets.versions.IVersionable,
                  adhocracy_core.sheets.metadata.IMetadata,
                  ],
    extended_sheets=[adhocracy_core.sheets.document.IParagraph,
                     ],
    permission_add='edit_paragraph',
)


class IParagraph(IItem):

    """Paragraph Versions Pool."""


paragraph_meta = item_meta._replace(
    content_name='Paragraph',
    iresource=IParagraph,
    element_types=[ITag,
                   IParagraphVersion,
                   ],
    item_type=IParagraphVersion,
    permission_add='add_paragraph',
)


def includeme(config):
    """Add resource type to registry."""
    add_resource_type_to_registry(paragraph_meta, config)
    add_resource_type_to_registry(paragraphversion_meta, config)
