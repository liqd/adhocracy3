"""Section resource type."""
from adhocracy.interfaces import IItemVersion
from adhocracy.interfaces import IItem
from adhocracy.interfaces import ITag
from adhocracy.resources import add_resource_type_to_registry
from adhocracy.resources.itemversion import itemversion_metadata
from adhocracy.resources.item import item_metadata

import adhocracy.sheets.document


class ISectionVersion(IItemVersion):

    """Document section."""


sectionversion_meta = itemversion_metadata._replace(
    content_name='SectionVersion',
    iresource=ISectionVersion,
    extended_sheets=[adhocracy.sheets.document.ISection,
                     ],
)


class ISection(IItem):

    """Section Versions Pool."""


section_meta = item_metadata._replace(
    content_name='Section',
    iresource=ISection,
    element_types=[ITag,
                   ISectionVersion,
                   ],
    item_type=ISectionVersion,
)


def includeme(config):
    """Register resource type factory in substanced content registry."""
    add_resource_type_to_registry(sectionversion_meta, config)
    add_resource_type_to_registry(section_meta, config)
