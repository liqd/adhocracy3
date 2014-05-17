"""Paragraph resource type."""
from adhocracy.interfaces import IItemVersion
from adhocracy.interfaces import IItem
from adhocracy.interfaces import ITag
from adhocracy.resources import ResourceFactory
from adhocracy.resources.itemversion import itemversion_meta_defaults
from adhocracy.resources.item import item_meta_defaults
from substanced.content import add_content_type

import adhocracy.sheets.document


class IParagraphVersion(IItemVersion):

    """Document paragraph (a leaf in the paragraph tree)."""


paragraphversion_meta = itemversion_meta_defaults._replace(
    content_name='ParagraphVersion',
    iresource=IParagraphVersion,
    extended_sheets=[adhocracy.sheets.document.IParagraph,
                     ],
)


class IParagraph(IItem):

    """Paragraph Versions Pool."""


paragraph_meta = item_meta_defaults._replace(
    content_name='Paragraph',
    iresource=IParagraph,
    element_types=[ITag,
                   IParagraphVersion,
                   ],
    item_type=IParagraphVersion,
)


def includeme(config):
    """Register resource type factory in substanced content registry."""
    metadatas = [paragraph_meta, paragraphversion_meta]
    for metadata in metadatas:
        identifier = metadata.iresource.__identifier__
        add_content_type(config,
                         identifier,
                         ResourceFactory(metadata),
                         factory_type=identifier, resource_metadata=metadata)
