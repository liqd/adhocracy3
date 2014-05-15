"""Section resource type."""
from adhocracy.interfaces import IItemVersion
from adhocracy.interfaces import IItem
from adhocracy.interfaces import ITag
from adhocracy.resources import ResourceFactory
from adhocracy.resources.itemversion import itemversion_meta_defaults
from adhocracy.resources.item import item_meta_defaults
from substanced.content import add_content_type

import adhocracy.sheets.document


class ISectionVersion(IItemVersion):

    """Document section."""


sectionversion_meta = itemversion_meta_defaults._replace(
    content_name='SectionVersion',
    iresource=ISectionVersion,
    extended_sheets=[adhocracy.sheets.document.ISection,
                     ],
    )

class ISection(IItem):

    """Section Versions Pool."""


section_meta = item_meta_defaults._replace(
    content_name='Section',
    iresource=ISection,
    element_types=[ITag,
                   ISectionVersion,
                   ],
    item_type=ISectionVersion,
)


def includeme(config):
    """Register resource type factory in substanced content registry."""
    metadatas = [section_meta, sectionversion_meta]
    for metadata in metadatas:
        identifier = metadata.iresource.__identifier__
        add_content_type(config,
                         identifier,
                         ResourceFactory(metadata),
                         factory_type=identifier, resource_metadata=metadata)
