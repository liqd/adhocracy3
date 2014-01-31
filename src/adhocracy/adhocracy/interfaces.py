"""Basic Interfaces used by all packages."""
from substanced.interfaces import IPropertySheet
from substanced.interfaces import IAutoNamingFolder
from pyramid.interfaces import ILocation
from zope.interface import Attribute
from zope.interface import Interface
from zope.interface import taggedValue
from zope.interface import provider
from zope.interface.interfaces import IInterface


class IAutoNamingManualFolder(IAutoNamingFolder):

    """Auto-nameing Folder that allows to set manul names in addition."""

    def next_name(subobject, prefix=''):
        """Return Name for subobject."""

    def add_next(subobject,
                 send_events=True,
                 duplicating=None,
                 moving=None,
                 registry=None,
                 prefix='',
                 ):
        """Add new child object and autgenerate name."""


class IISheet(IInterface):

    """Mark ISheet classes to ease overriding registered adapters."""


@provider(IISheet)
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


class IResource(ILocation):

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

    taggedValue('basic_sheets', set())
    """Basic property interfaces to define data """
    taggedValue('extended_sheets', set())
    """Extended property interfaces to define data, subtypes should override"""
    taggedValue('after_creation', [])
    """Callables to run after creation. They are passed the instance being
    created and the registry."""


class IResourcePropertySheet(IPropertySheet):

    """PropertySheet object to set/get resource data.

    It uses the ISheet ``schema``  taggedvalue to get the wanted data
    schema. The data store must prevent attribute name conflicts.

    """

    iface = Attribute('The ISheet interface used to configure this Sheet.')
    key = Attribute('Internal dictionary key to store the schema data.')
    readonly = Attribute('Bool to indicate you should not set data.')
    createmandatory = Attribute('Bool to indicate you should set data when '
                                'creating a new resource.')

    def get_cstruct():
        """ Return a serialized dictionary representing the property state."""
        pass

    def validate_cstruct(cstruct):
        """ Validate ``cstruct`` data.

        Args:
            cstruct (Dictionary): serialized application data (colander)
        Returns:
            appstruct (Dictionary): deserialized application data (colander)
        Raises:
            colander.Invalid

        """
        pass
