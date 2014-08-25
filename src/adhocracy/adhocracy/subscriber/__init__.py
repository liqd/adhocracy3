"""adhocracy.event event subcriber to handle auto updates of resources."""
from pyramid.traversal import resource_path

from adhocracy.interfaces import IItemVersion
from adhocracy.interfaces import ISheetReferenceAutoUpdateMarker
from adhocracy.interfaces import ISheetReferencedItemHasNewVersion
from adhocracy.sheets.versions import IVersionable
from adhocracy.utils import get_sheet
from adhocracy.utils import get_all_sheets
from adhocracy.utils import get_iresource
from adhocracy.utils import find_graph


def _get_writable_appstructs(resource):
    # FIXME maybe move this to utils or better use resource registry
    appstructs = {}
    for sheet in get_all_sheets(resource):
        editable = sheet.meta.editable
        creatable = sheet.meta.creatable
        writable = editable or creatable
        if writable:
            appstructs[sheet.meta.isheet.__identifier__] = sheet.get()
    return appstructs


def _update_versionable(resource, isheet, appstruct, root_versions, registry,
                        creator):
    graph = find_graph(resource)
    if root_versions and not graph.is_in_subtree(resource, root_versions):
        return resource
    else:
        appstructs = _get_writable_appstructs(resource)
        appstructs[IVersionable.__identifier__]['follows'] = [resource]
        appstructs[isheet.__identifier__] = appstruct
        iresource = get_iresource(resource)
        new_resource = registry.content.create(iresource.__identifier__,
                                               parent=resource.__parent__,
                                               appstructs=appstructs,
                                               creator=creator,
                                               options=root_versions)
        return new_resource


def _update_resource(resource, sheet, appstruct):
    sheet.set(appstruct)
    return resource


def reference_has_new_version_subscriber(event):
    """Auto updated resource if a referenced Item has a new version.

    Args:
        event (ISheetReferencedItemHasNewVersion)

    """
    resource = event.object
    root_versions = event.root_versions
    isheet = event.isheet
    registry = event.registry
    creator = event.creator
    sheet = get_sheet(resource, isheet)
    autoupdate = isheet.extends(ISheetReferenceAutoUpdateMarker)
    editable = sheet.meta.editable

    if autoupdate and editable:
        appstruct = sheet.get()
        field = appstruct[event.isheet_field]
        old_version_index = field.index(event.old_version)
        field.pop(old_version_index)
        field.insert(old_version_index, event.new_version)
        new_version = _get_new_version_created_in_this_transaction(registry,
                                                                   resource)
        if IItemVersion.providedBy(resource) and new_version is None:
            _update_versionable(resource, isheet, appstruct, root_versions,
                                registry, creator)
        else:
            _update_resource(resource, sheet, appstruct)


def _get_new_version_created_in_this_transaction(registry, resource):
        if not hasattr(registry, '_transaction_changelog'):
            return
        path = resource_path(resource)
        changelog_metadata = registry._transaction_changelog[path]
        return changelog_metadata.followed_by


def includeme(config):
    """Register subrscriber to autoupdate resource references."""
    config.include('adhocracy.events')
    config.add_subscriber(reference_has_new_version_subscriber,
                          ISheetReferencedItemHasNewVersion,
                          isheet=ISheetReferenceAutoUpdateMarker)
