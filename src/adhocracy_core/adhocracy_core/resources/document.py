"""Proposal resource type."""
from adhocracy_core.interfaces import IItemVersion
from adhocracy_core.interfaces import ITag
from adhocracy_core.interfaces import IItem
from adhocracy_core.resources.comment import add_commentsservice
from adhocracy_core.resources.paragraph import IParagraph
from adhocracy_core.resources import add_resource_type_to_registry
from adhocracy_core.resources.itemversion import itemversion_meta
from adhocracy_core.resources.item import item_meta
from adhocracy_core.resources.rate import add_ratesservice

import adhocracy_core.sheets.document
import adhocracy_core.sheets.comment
import adhocracy_core.sheets.workflow
import adhocracy_core.sheets.image


class IDocumentVersion(IItemVersion):

    """Versionable item with Document propertysheet."""


document_version_meta = itemversion_meta._replace(
    iresource=IDocumentVersion,
    extended_sheets=[adhocracy_core.sheets.document.IDocument,
                     adhocracy_core.sheets.comment.ICommentable,
                     adhocracy_core.sheets.rate.IRateable,
                     adhocracy_core.sheets.image.IImageReference,
                     ],
    permission_create='edit_proposal',
)


class IDocument(IItem):

    """All versions of a Proposal."""


document_meta = item_meta._replace(
    iresource=IDocument,
    extended_sheets=[adhocracy_core.sheets.workflow.ISample],
    element_types=[ITag,
                   IParagraph,
                   IDocumentVersion,
                   ],
    after_creation=item_meta.after_creation + [
        add_commentsservice,
        add_ratesservice,
    ],
    item_type=IDocumentVersion,
    permission_create='create_proposal',
    is_implicit_addable=True,
)


def includeme(config):
    """Add resource type to registry."""
    add_resource_type_to_registry(document_version_meta, config)
    add_resource_type_to_registry(document_meta, config)
