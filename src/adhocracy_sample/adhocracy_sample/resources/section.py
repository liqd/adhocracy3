"""Section resource type."""
from adhocracy.interfaces import IItemVersion
from adhocracy.interfaces import IItem
from adhocracy.interfaces import ITag
from adhocracy.resources import add_resource_type_to_registry
from adhocracy.resources.itemversion import itemversion_meta_defaults
from adhocracy.resources.item import item_meta_defaults

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
    add_resource_type_to_registry(ISectionVersion, config)
    add_resource_type_to_registry(ISection, config)
