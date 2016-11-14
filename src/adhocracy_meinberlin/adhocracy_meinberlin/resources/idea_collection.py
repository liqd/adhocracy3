"""Shared idea collection process."""
from pyramid.i18n import TranslationStringFactory
from adhocracy_core.resources import add_resource_type_to_registry
from adhocracy_core.resources import process
from adhocracy_core.resources import proposal
from adhocracy_core.sheets.geo import ILocationReference
from adhocracy_core.sheets.image import IImageReference


_ = TranslationStringFactory('adhocracy')


class IProcess(process.IProcess):
    """Idea collection participation process."""


process_meta = process.process_meta._replace(
    content_name=_('IdeaCollectionProcess'),
    iresource=IProcess,
    element_types=(proposal.IGeoProposal,
                   ),
    is_implicit_addable=True,
    extended_sheets=(
        ILocationReference,
        IImageReference,
    ),
    default_workflow='standard',
)


def includeme(config):
    """Add resource type to content."""
    add_resource_type_to_registry(process_meta, config)
