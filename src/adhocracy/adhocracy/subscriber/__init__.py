"""adhocracy.event event subcriber to handle auto updates of resources."""

from adhocracy.graph import is_in_subtree
from adhocracy.interfaces import IItemVersion
from adhocracy.interfaces import ISheetReferenceAutoUpdateMarker
from adhocracy.interfaces import ISheetReferencedItemHasNewVersion
from adhocracy.sheets.versions import IVersionable
from adhocracy.utils import get_sheet
from adhocracy.utils import get_all_sheets
from adhocracy.utils import get_resource_interface
from adhocracy.utils import get_all_taggedvalues
from pyramid.threadlocal import get_current_registry
from copy import deepcopy


def _get_not_readonly_appstructs(resource):
    # FIXME maybe move this to utils or better use resource registry
    appstructs = {}
    for sheet in get_all_sheets(resource):
        if not sheet.readonly:
            appstructs[sheet.iface.__identifier__] = sheet.get()
    return appstructs


def _update_versionable(resource, isheet, appstruct, root_versions):
    if root_versions and not is_in_subtree(resource, root_versions):
        return resource
    else:
        registry = get_current_registry()
        appstructs = _get_not_readonly_appstructs(resource)
        appstructs[IVersionable.__identifier__]['follows'] = [resource.__oid__]
        appstructs[isheet.__identifier__] = appstruct
        iresource = get_resource_interface(resource)
        new_resource = registry.content.create(iresource.__identifier__,
                                               parent=resource.__parent__,
                                               appstructs=appstructs,
                                               options=root_versions)
        return new_resource


def _update_resource(resource, isheet, appstruct):
    sheet = get_sheet(resource, isheet)
    if not sheet.readonly:
        sheet.set(appstruct)
        #FIXME: make sure modified event is send
    return resource


def reference_has_new_version_subscriber(event):
    """Auto updated resource if a referenced Item has a new version.

    Args:
        event (ISheetReferencedItemHasNewVersion)

    """
    assert ISheetReferencedItemHasNewVersion.providedBy(event)
    resource = event.object
    root_versions = event.root_versions
    isheet = event.isheet
    readonly = get_all_taggedvalues(isheet)['readonly']
    autoupdate = isheet.extends(ISheetReferenceAutoUpdateMarker)

    if autoupdate and not readonly:
        sheet = get_sheet(resource, isheet)
        appstruct = deepcopy(sheet.get())
        field = appstruct[event.isheet_field]
        old_version_index = field.index(event.old_version_oid)
        field.pop(old_version_index)
        field.insert(old_version_index, event.new_version_oid)
        if IItemVersion.providedBy(resource):
            _update_versionable(resource, isheet, appstruct, root_versions)
        else:
            _update_resource(resource, isheet, appstruct)


def includeme(config):
    """Register subrscriber to autoupdate resource references."""
    config.include('adhocracy.events')
    config.add_subscriber(reference_has_new_version_subscriber,
                          ISheetReferencedItemHasNewVersion,
                          isheet=ISheetReferenceAutoUpdateMarker)
