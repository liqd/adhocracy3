"""Basic versionable type typically for process content."""
from adhocracy_core.events import ItemVersionNewVersionAdded
from adhocracy_core.events import SheetReferenceNewVersion
from adhocracy_core.interfaces import IItemVersion
from adhocracy_core.interfaces import SheetToSheet
from adhocracy_core.resources import add_resource_type_to_registry
from adhocracy_core.resources.resource import resource_metadata_defaults
from adhocracy_core.sheets.versions import IVersionable
from adhocracy_core.utils import get_sheet
from adhocracy_core.utils import find_graph
import adhocracy_core.sheets.metadata
import adhocracy_core.sheets.versions


def notify_new_itemversion_created(context, registry, options):
    """Notify referencing Resources after creating a new ItemVersion.

    Args:
        context (IItemversion): the newly created resource
        registry (pyramid registry):
        option (dict):
            `root_versions`: List with root resources. Will be passed along to
                            resources that reference old versions so they can
                            decide whether they should update themselfes.
            `creator`: User resource that passed to the creation events.

    Returns:
        None

    """
    new_version = context
    root_versions = options.get('root_versions', [])
    creator = options.get('creator', None)
    is_batchmode = options.get('is_batchmode', False)
    old_versions = []
    versionable = get_sheet(context, IVersionable, registry=registry)
    follows = versionable.get()['follows']
    for old_version in follows:
        old_versions.append(old_version)
        _notify_itemversion_has_new_version(old_version, new_version, registry,
                                            creator)
        _notify_referencing_resources_about_new_version(old_version,
                                                        new_version,
                                                        root_versions,
                                                        registry,
                                                        creator,
                                                        is_batchmode)


def _notify_itemversion_has_new_version(old_version, new_version, registry,
                                        creator):
    event = ItemVersionNewVersionAdded(old_version, new_version, registry,
                                       creator)
    registry.notify(event)


def _notify_referencing_resources_about_new_version(old_version,
                                                    new_version,
                                                    root_versions,
                                                    registry,
                                                    creator,
                                                    is_batchmode,
                                                    ):
    graph = find_graph(old_version)
    references = graph.get_back_references(old_version,
                                           base_reftype=SheetToSheet)
    for source, isheet, isheet_field, target in references:
        event = SheetReferenceNewVersion(source,
                                         isheet,
                                         isheet_field,
                                         old_version,
                                         new_version,
                                         registry,
                                         creator,
                                         root_versions=root_versions,
                                         is_batchmode=is_batchmode,
                                         )
        registry.notify(event)


itemversion_metadata = resource_metadata_defaults._replace(
    content_name='ItemVersion',
    iresource=IItemVersion,
    basic_sheets=[adhocracy_core.sheets.versions.IVersionable,
                  adhocracy_core.sheets.metadata.IMetadata,
                  ],
    after_creation=[notify_new_itemversion_created] +
    resource_metadata_defaults.after_creation,
    use_autonaming=True,
    autonaming_prefix='VERSION_',
)


def includeme(config):
    """Add resource type to registry."""
    add_resource_type_to_registry(itemversion_metadata, config)
