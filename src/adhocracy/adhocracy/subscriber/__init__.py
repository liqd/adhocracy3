"""adhocracy.event event subcriber to handle auto updates of resources."""

from adhocracy.graph import is_in_subtree
from adhocracy.interfaces import IResourcePropertySheet
from adhocracy.interfaces import IResource
from adhocracy.interfaces import ISheetReferenceAutoUpdateMarker
from adhocracy.interfaces import ISheetReferencedItemHasNewVersion
from adhocracy.sheets.versions import IVersionable
from adhocracy.utils import get_sheet_interfaces
from adhocracy.utils import get_resource_interface
from adhocracy.utils import get_all_taggedvalues
from copy import deepcopy
from zope.component import getMultiAdapter


def _get_not_readonly_appstructs(resource):
    # FIXME move this to utils or better use resource registry
    isheets = get_sheet_interfaces(resource)
    appstructs = {}
    for isheet in isheets:
        sheet = getMultiAdapter((resource, isheet), IResourcePropertySheet)
        if not sheet.readonly:
            appstructs[isheet.__identifier__] = sheet.get()
    return appstructs


def _update_versionable(resource, isheet, appstruct, root_versions):
    from adhocracy.resources import ResourceFactory  # make unit test mock work
    if root_versions and not is_in_subtree(resource, root_versions):
        return resource
    else:
        appstructs = _get_not_readonly_appstructs(resource)
        appstructs[IVersionable.__identifier__]['follows'] = [resource.__oid__]
        appstructs[isheet.__identifier__] = appstruct
        iresource = get_resource_interface(resource)
        return ResourceFactory(iresource)(parent=resource.__parent__,
                                          appstructs=appstructs,
                                          options=root_versions)


def _update_resource(resource, isheet, appstruct):
    sheet = getMultiAdapter((resource, isheet), IResourcePropertySheet)
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
    assert IResource.providedBy(event.object)
    resource = event.object
    root_versions = event.root_versions
    isheet = event.isheet
    readonly = get_all_taggedvalues(isheet)['readonly']
    autoupdate = isheet.extends(ISheetReferenceAutoUpdateMarker)

    if autoupdate and not readonly:
        sheet = getMultiAdapter((resource, isheet), IResourcePropertySheet)
        appstruct = deepcopy(sheet.get())
        field = appstruct[event.isheet_field]
        old_version_index = field.index(event.old_version_oid)
        field.pop(old_version_index)
        field.insert(old_version_index, event.new_version_oid)
        if IVersionable.providedBy(resource):
            _update_versionable(resource, isheet, appstruct, root_versions)
        else:
            _update_resource(resource, isheet, appstruct)


def includeme(config):
    """Register subrscriber to autoupdate resource references."""
    config.include('adhocracy.events')
    config.add_subscriber(reference_has_new_version_subscriber,
                          ISheetReferencedItemHasNewVersion,
                          isheet=ISheetReferenceAutoUpdateMarker)
