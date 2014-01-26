"""Basic Interfaces used by all packages."""
from substanced.interfaces import IPropertySheet
from zope.interface import (
    Attribute,
    Interface,
    taggedValue,
)
from zope.interface.interfaces import IInterface


class IISheet(IInterface):

    """Mark ISheet class to allow registering a MultiAdapter.

    See adhocracy.sheets.includme for examples.

    """


class ISheet(Interface):

    """Marker interface with tagged values to define resource data."""

    taggedValue('schema', 'colander.MappingSchema')
    """Reference colander data schema.

    This schema has to define the facade to work with this resource.
    To set/get the data you can adapt to IPropertySheet objects.

    Subtype has to override.

    """
    taggedValue('key', '')
    """Key to store the schema data, defaults to IProperyXY.__identifier__"""
    taggedValue('permission_view', 'view')
    """Permission to view or index this data. Subtype should override."""
    taggedValue('permission_edit', 'edit')
    """Permission to edit this data. Subtype should override."""
    taggedValue('readonly', False)
    """This propertysheet may not be used to set data."""
    taggedValue('createmandatory', False)
    """This propertysheet is mandatory when creating a new resource."""


class IResource(Interface):

    """Marker interface with tagged values to configure a resource type."""

    taggedValue('content_name', '')
    """Human readable name, subtypes have to override"""
    taggedValue('content_class', 'persistent.mapping.PersistentMapping')
    """Class to create content objects"""

    taggedValue('permission_add', 'add')
    """Permission to add this content object to the object hierarchy. """
    taggedValue('permission_view', 'view')
    """Permission to view content data and view in listings"""
    taggedValue('is_implicit_addable', True)
    """Make this content type adddable if supertype is addable."""

    taggedValue('basic_sheets_interfaces', set())
    """Basic property interfaces to define data """
    taggedValue('extended_sheets_interfaces', set())
    """Extended property interfaces to define data, subtypes should override"""
    taggedValue('after_creation', [])
    """Callables to run after creation. They are passed the instance being
    created and the registry."""


class IResourcePropertySheet(IPropertySheet):

    """Adapter for Resources to set/get the data.

    It uses the ISheet ``schema``  taggedvalue to get the wanted data
    schema. The data store must prevent attribute name conflicts.

    """

    iface = Attribute('The ISheet interface used to configure this Sheet.')
    key = Attribute('Internal dictionary key to store the schema data.')
    readonly = Attribute('Bool to indicate you should not set data.')
    createmandatory = Attribute('Bool to indicate you should set data when '
                                'creating a new resource.')

    def get_cstruct():
        """ Return a serialized dictionary representing the propertyt state."""
        pass

    def set_cstruct(cstruct):
        """ Accept ``cstruct``  and persist it to the context.

        (a serialized dictionary representing the property state)

        """
        pass
