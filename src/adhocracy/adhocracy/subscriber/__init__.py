"""adhocracy.event event subcriber to hanle auto updates of resources."""

from adhocracy.interfaces import IResourcePropertySheet
from adhocracy.interfaces import IResource
from adhocracy.interfaces import ISheetReferenceAutoUpdateMarker
from adhocracy.interfaces import ISheetReferencedItemHasNewVersion
from adhocracy.sheets.versions import IVersionable
from adhocracy.utils import get_sheet_interfaces
from adhocracy.utils import get_resource_interface
from adhocracy.utils import get_all_taggedvalues
from substanced.util import get_oid
from zope.component import getMultiAdapter
from copy import deepcopy


def _update_resource(resource, isheet, appstruct):
    from adhocracy.resources import ResourceFactory  # make unit test mock work
    updated_resource = resource
    if IVersionable.providedBy(resource):
        iresource = get_resource_interface(resource)
        isheets_ = get_sheet_interfaces(resource)
        appstructs = {}
        for isheet_ in isheets_:
            sheet_ = getMultiAdapter((resource, isheet_),
                                     IResourcePropertySheet)
            if sheet_.readonly:
                continue
            appstructs[isheet_.__identifier__] = sheet_.get()
        oid = get_oid(resource)
        appstructs[IVersionable.__identifier__]['follows'] = [oid]
        appstructs[isheet.__identifier__] = appstruct
        updated_resource = ResourceFactory(iresource)(resource.__parent__,
                                                      appstructs=appstructs)
    else:
        sheet = getMultiAdapter((resource, isheet), IResourcePropertySheet)
        if not sheet.readonly:
            sheet.set(appstruct)
        #FIXME: make sure modified event is send
    return updated_resource


def reference_has_new_version_subscriber(event):
    """Auto updated resource if a referenced Item has a new version."""
    assert ISheetReferencedItemHasNewVersion.providedBy(event)
    assert IResource.providedBy(event.object)
    readonly = get_all_taggedvalues(event.isheet)['readonly']
    if event.isheet.extends(ISheetReferenceAutoUpdateMarker) and not readonly:
        resource = event.object
        sheet = getMultiAdapter((resource, event.isheet),
                                IResourcePropertySheet)
        appstruct = deepcopy(sheet.get())
        field = appstruct[event.isheet_field]
        old_oid_index = field.index(event.old_version_oid)
        field.pop(old_oid_index)
        field.insert(old_oid_index, event.new_version_oid)
        _update_resource(event.object, event.isheet, appstruct)


def includeme(config):
    """Register subrscriber to autoupdate resource references."""
    config.include('adhocracy.events')
    config.add_subscriber(reference_has_new_version_subscriber,
                          ISheetReferencedItemHasNewVersion,
                          isheet=ISheetReferenceAutoUpdateMarker)
