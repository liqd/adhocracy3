"""Basic Interfaces used by all packages."""
from pyramid.interfaces import ILocation
from substanced.interfaces import IAutoNamingFolder
from substanced.interfaces import IPropertySheet
from substanced.interfaces import ReferenceClass
from zope.interface import Attribute
from zope.interface import Interface
from zope.interface import taggedValue
from zope.interface.interfaces import IInterface
from zope.interface.interface import InterfaceClass
from zope.interface.interfaces import IObjectEvent


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


class IIResourcePropertySheet(IInterface):

    """Marker interfaces to register the default propertysheet adapter."""


class ISheet(Interface):

    """Interface with tagged values to define resource data."""

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


class ISheetReferenceAutoUpdateMarker(ISheet):

    """Sheet Interface to autoupdate sheets with references.

    If one referenced resource has a new version this sheet
    changes the reference to the new version.

    """


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

    def validate_cstruct(cstruct):
        """ Validate ``cstruct`` data.

        Args:
            cstruct (Dictionary): serialized application data (colander)
        Returns:
            appstruct (Dictionary): deserialized application data (colander)
        Raises:
            colander.Invalid

        """


class IResource(ILocation):

    """Marker interface with tagged values to configure a resource type."""

    taggedValue('content_name', '')
    """Human readable name, subtypes have to override"""
    taggedValue('content_class', 'adhocracy.resource.Resource')
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


class IPool(IResource, IAutoNamingFolder):

    """Folder in the object hierarchy.

    Can contain other Pools (subfolders) and Items of any kind.
    Additional TaggedValue: 'element_types' (types of resources that can be
    added to this pool).

    """

    taggedValue('content_class', 'adhocracy.folder.ResourcesAutolNamingFolder')
    taggedValue('basic_sheets',
                set(['adhocracy.sheets.name.IName',
                     'adhocracy.sheets.pool.IPool']))
    taggedValue('element_types',
                set(['adhocracy.interfaces.IPool']))
    """ Set addable content types, class heritage is honored"""


class IItem(IPool):

    """Pool for any versionable objects (DAG), tags and related Pools.

    Additional TaggedValue: 'item_type'

    """

    taggedValue('content_name', 'Item')
    taggedValue('basic_sheets', set(
                ['adhocracy.sheets.name.IName',
                 'adhocracy.sheets.tags.ITags',
                 'adhocracy.sheets.versions.IVersions',
                 'adhocracy.sheets.pool.IPool']))
    # FIXME: 'adhocracy.resources.IItemVersion' has moved to interfaces
    taggedValue('element_types', set([
                'adhocracy.resources.IItemVersion',
                'adhocracy.resources.ITag',
                ]))
    taggedValue(
        'after_creation',
        ['adhocracy.resources.create_initial_content_for_item'])
    taggedValue('item_type',
                'adhocracy.resources.IItemVersion')
    """Type of versions in this item. Subtypes have to override."""


class ISimple(IResource):

    """Small object without versions and children."""

    taggedValue('content_name', 'Simple')
    taggedValue('basic_sheets', set(
                ['adhocracy.sheets.name.IName']))


class ITag(ISimple):

    """Tag to link specific versions."""

    taggedValue('content_name', 'Tag')
    taggedValue('basic_sheets', set(
                ['adhocracy.sheets.name.IName',
                 'adhocracy.sheets.tags.ITag']))


class IItemVersion(IResource):

    """Versionable object, created during a Participation Process (mainly)."""

    taggedValue('content_name', 'ItemVersion')
    taggedValue('basic_sheets', set(
                ['adhocracy.sheets.versions.IVersionable']))
    taggedValue(
        'after_creation',
        ['adhocracy.resources.notify_new_itemversion_created'])


class SheetReferenceClass(ReferenceClass):

    """Reference a specific ISheet for source and and target.

    Uses class attributes "target_*" and "source_*" to set tagged values.

    """

    def __init__(self, *arg, **kw):
        try:
            attrs = arg[2] or {}
        except IndexError:
            attrs = kw.get('attrs', {})
        # get class attribute values and remove them
        si = attrs.pop('source_integrity', False)
        ti = attrs.pop('target_integrity', False)
        so = attrs.pop('source_ordered', False)
        to = attrs.pop('target_ordered', False)
        sif = attrs.pop('source_isheet', ISheet)
        sifa = attrs.pop('source_isheet_field', u'')
        tif = attrs.pop('target_isheet', ISheet)
        # initialize interface class
        InterfaceClass.__init__(self, *arg, **kw)
        # set tagged values based on attribute values
        self.setTaggedValue('source_integrity', si)
        self.setTaggedValue('target_integrity', ti)
        self.setTaggedValue('source_ordered', so)
        self.setTaggedValue('target_ordered', to)
        self.setTaggedValue('source_isheet', sif)
        self.setTaggedValue('source_isheet_field', sifa)
        self.setTaggedValue('target_isheet', tif)


SheetReferenceType = SheetReferenceClass('SheetReferenceType',
                                         __module__='adhocracy.interfaces')


class SheetToSheet(SheetReferenceType):

    """Base type to reference resource ISheets."""


class NewVersionToOldVersion(SheetReferenceType):

    """Base type to reference an old ItemVersion."""


class IItemVersionNewVersionAdded(IObjectEvent):

    """An event type sent when a new ItemVersion is added."""

    object = Attribute('The old ItemVersion followed by the new one')
    new_version = Attribute('The new ItemVersion')


class ISheetReferencedItemHasNewVersion(IObjectEvent):

    """An event type sent when a referenced ItemVersion has a new follower."""

    object = Attribute('The resource referencing the outdated ItemVersion.')
    isheet = Attribute('The sheet referencing the outdated ItemVersion')
    isheet_field = Attribute('The sheet field referencing the outdated '
                             'ItemVersion')
    old_version = Attribute('The referenced but outdated ItemVersion')
    new_version = Attribute('The follower of the outdated ItemVersion')
    root_versions = Attribute('Non-empty list of roots of the ItemVersion '
                              '(only resources that can be reached from one '
                              'of the roots should be updated)')
