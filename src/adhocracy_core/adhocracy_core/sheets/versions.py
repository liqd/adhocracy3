"""Sheets to work with versionable resources."""
from pyramid.traversal import resource_path
import colander

from adhocracy_core.interfaces import ISheet
from adhocracy_core.interfaces import SheetToSheet
from adhocracy_core.interfaces import NewVersionToOldVersion
from adhocracy_core.sheets import add_sheet_to_registry
from adhocracy_core.sheets import sheet_meta
from adhocracy_core.sheets.pool import PoolSheet
from adhocracy_core.schema import UniqueReferences
from adhocracy_core.utils import is_created_in_current_transaction
from adhocracy_core.utils import is_batchmode
from adhocracy_core.utils import get_sheet_field


class IVersionable(ISheet):
    """Maker interface for resources with the versionable sheet."""


class VersionableFollowsReference(NewVersionToOldVersion):
    """versionable sheet reference to preceding versions."""

    source_isheet = IVersionable
    source_isheet_field = 'follows'
    target_isheet = IVersionable


def validate_linear_history_no_merge(node: colander.SchemaNode, value: list):
    """Validate lineare history (no merge) for the `follows` field.

    :raises colander.Invalid: if len(value) != 1
    """
    if len(value) != 1:
        msg = 'No merge allowed - you must set only one follows reference'
        raise colander.Invalid(node, msg, value=value)


def validate_linear_history_no_fork(node: colander.SchemaNode, value: list):
    """Validate lineare history (no fork) for the follows field.

    :param:'value': list of one 'follows' resource.

    :raises colander.Invalid: if value does not reference the last version.
    """
    from adhocracy_core.sheets.tags import ITags  # prevent circle dependencies
    context = node.bindings['context']
    request = node.bindings['request']
    registry = node.bindings['registry']
    batchmode = is_batchmode(request)
    last = get_sheet_field(context, ITags, 'LAST', registry=registry)
    if batchmode and is_created_in_current_transaction(last, registry):
        # In batchmode there is only one new last version created that is
        # updated by the following versions. See
        # func:`adhocracy_core.rest.views.IItemRestView.post` and
        # func:`adhocracy_core.resource.subscriber` for more information.
        return
    _assert_follows_last_version(node, value, last)


def _assert_follows_last_version(node: colander.SchemaNode, value: list,
                                 last: object):
    follows = value[0]
    if follows is not last:
        last_path = resource_path(last)
        msg = 'No fork allowed - valid follows resources are: {0}'
        msg = msg.format(str(last_path))
        raise colander.Invalid(node, msg, value=value)


@colander.deferred
def deferred_validate_follows(node: colander.SchemaNode, kw: dict) -> callable:
    """Validate lineare history for the `follows` field."""
    # TODO add validation for ForkableVersionables
    return colander.All(validate_linear_history_no_merge,
                        validate_linear_history_no_fork,
                        )


class VersionableSchema(colander.MappingSchema):
    """Versionable sheet data structure.

    Set/get predecessor (`follows`) versions of this resource.
    """

    follows = UniqueReferences(reftype=VersionableFollowsReference,
                               validator=deferred_validate_follows)


versionable_meta = sheet_meta._replace(
    isheet=IVersionable,
    schema_class=VersionableSchema,
)


class IForkableVersionable(IVersionable):
    """Maker interface for resources that support forking.

    This means that the multiple heads are allowed (the LAST tag can point
    to two or more versions).
    """


forkable_versionable_meta = versionable_meta._replace(
    isheet=IForkableVersionable,
)


class IVersions(ISheet):
    """Marker interface for the versions sheet."""


class IVersionsElementsReference(SheetToSheet):
    """Version sheet elements reference."""

    source_isheet = IVersions
    source_isheet_field = 'elements'
    target_isheet = IVersionable


class VersionsSchema(colander.MappingSchema):
    """Versions sheet data structure.

    `elements`: Dag for collecting all versions of one item.
    """

    elements = UniqueReferences(
        reftype=IVersionsElementsReference)


versions_meta = sheet_meta._replace(
    isheet=IVersions,
    sheet_class=PoolSheet,
    schema_class=VersionsSchema,
    editable=False,
    creatable=False,
)


def includeme(config):
    """Register sheets."""
    add_sheet_to_registry(versionable_meta, config.registry)
    add_sheet_to_registry(forkable_versionable_meta, config.registry)
    add_sheet_to_registry(versions_meta, config.registry)
