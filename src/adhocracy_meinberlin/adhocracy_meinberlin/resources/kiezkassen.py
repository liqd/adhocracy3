"""Mercator proposal."""
from adhocracy_core.interfaces import IItemVersion
from adhocracy_core.interfaces import IItem
from adhocracy_core.resources import add_resource_type_to_registry
from adhocracy_core.resources.itemversion import itemversion_meta
from adhocracy_core.resources.item import item_meta
from adhocracy_core.resources import process
from adhocracy_core.resources.comment import add_commentsservice
from adhocracy_core.resources.rate import add_ratesservice
from adhocracy_core.sheets.description import IDescription
from adhocracy_core.sheets.geo import IPoint
from adhocracy_core.sheets.rate import IRateable
from adhocracy_core.sheets.comment import ICommentable
from adhocracy_core.sheets.title import ITitle
from adhocracy_core.sheets.geo import ILocationReference
from adhocracy_core.sheets.image import IImageReference
import adhocracy_meinberlin.sheets.kiezkassen


class IProposalVersion(IItemVersion):

    """Kiezkassen proposal version."""


proposal_version_meta = itemversion_meta._replace(
    content_name='ProposalVersion',
    iresource=IProposalVersion,
    extended_sheets=[ITitle,
                     IDescription,
                     adhocracy_meinberlin.sheets.kiezkassen.IProposal,
                     IPoint,
                     ICommentable,
                     IRateable],
    permission_create='edit_kiezkassen_proposal',
)


class IProposal(IItem):

    """Kiezkassen proposal versions pool."""


proposal_meta = item_meta._replace(
    content_name='Proposal',
    iresource=IProposal,
    element_types=[IProposalVersion],
    after_creation=item_meta.after_creation + [
        add_commentsservice,
        add_ratesservice,
    ],
    item_type=IProposalVersion,
    is_implicit_addable=True,
    permission_create='create_kiezkassen_proposal',
)


class IProcess(process.IProcess):

    """Kiezkassen participation process."""


process_meta = process.process_meta._replace(
    iresource=IProcess,
    element_types=[IProposal,
                   ],
    is_implicit_addable=True,
    extended_sheets=[
        IDescription,
        adhocracy_meinberlin.sheets.kiezkassen.IWorkflowAssignment,
        ILocationReference,
        IImageReference,
    ],
    permission_create='create_kiezkassen_process',
)


def includeme(config):
    """Add resource type to content."""
    add_resource_type_to_registry(proposal_meta, config)
    add_resource_type_to_registry(proposal_version_meta, config)
    add_resource_type_to_registry(process_meta, config)
