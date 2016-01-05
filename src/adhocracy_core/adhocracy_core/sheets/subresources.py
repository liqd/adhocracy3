"""Sheet interfaces to reference subresources."""
from adhocracy_core.interfaces import ISheet
from adhocracy_core.interfaces import ISheetReferenceAutoUpdateMarker


class ISubResources(ISheet, ISheetReferenceAutoUpdateMarker):
    """Meta Marker interface for the sheets that reference subresources.

    For example references to document parts or form fields.
    These are :term:``essence`` references, if the referenced Resource
    has a new Version the referecing resource is also updated.
    """
