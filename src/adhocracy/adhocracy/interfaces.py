"""Basic Interfaces used by all packages."""
from collections import Iterable
from collections import namedtuple
from collections import OrderedDict

from pyramid.interfaces import ILocation
from substanced.interfaces import IPropertySheet
from substanced.interfaces import ReferenceClass
from zope.interface import Attribute
from zope.interface import Interface
from zope.interface.interface import InterfaceClass
from zope.interface.interfaces import IObjectEvent


class ISheet(Interface):

    """Marker interface for resources to enable a specific sheet type."""


SHEET_METADATA = {'isheet': None,
                  'sheet_class': None,
                  'schema_class': None,
                  'permission_view': '',
                  'permission_edit': '',
                  'readonly': False,
                  'createmandatory': False,
                  }


class SheetMetadata(namedtuple('SheetMetadata', SHEET_METADATA.keys())):

    """Metadata to register a sheet type to set/get resource data.

    Fields:
    -------

    isheet: Marker interface for this sheet type, a subtype of :class ISheet:.
            Subtype has to override.
    sheet_class: :class IResourceSheet: implementation for this sheet
    schema_class: :class colander.MappingSchema: to define the data structure
                  for this sheet.
                  Subtype must preserve the super type data structure.
    permission_view: Permission to view or index this data.
                     Subtype should override.
    permission_edit: Permission to edit this data.
                     Subtype should override.
    readonly: This Sheet may not be used to set data

    """


sheet_metadata = SheetMetadata(**SHEET_METADATA)


class ISheetReferenceAutoUpdateMarker(ISheet):

    """Sheet Interface to autoupdate sheets with references.

    If one referenced resource has a new version this sheet
    changes the reference to the new version.

    """


class IResourceSheet(IPropertySheet):

    """Sheet for resources to get/set the sheet data structure."""

    meta = Attribute('SheetMetadata')

    def get_cstruct() -> dict:
        """ Return a serialized dictionary representing the sheet state."""

    def validate_cstruct(cstruct: dict) -> dict:
        """ Validate ``cstruct`` data.

        : param cstruct: serialized application data (colander)
        : return: appstruct: deserialized application data (colander)
        : raises: :class colander.Invalid:

        """


RESOURCE_METADATA = OrderedDict({
    'content_name': '',
    'iresource': None,
    'content_class': None,
    'permission_add': '',
    'permission_view': '',
    'is_implicit_addable': True,
    'basic_sheets': [],
    'extended_sheets': [],
    'after_creation': [],
    'element_types': [],
    'item_type': None,
    'use_autonaming': False,
    'autonaming_prefix': '',
})


class ResourceMetadata(namedtuple('ResourceMetadata',
                                  RESOURCE_METADATA.keys())):

    """Metadata to register Resource Types.

    Basic fields:
    -------------

    content_name: Human readable name,
                  subtypes have to override
    iresource: the resource type interface,
               subtypes have to override
    content_class: Class to create content objects
    permission_add: Permission to add this resource to the object hierarchy.
    permission_view: Permission to view resource data and view in listings
    is_implicit_addable: Make this type adddable if supertype is addable.
    basic_sheets: Basic property interfaces to define data
    extended_sheets: Extended property interfaces to define data,
                     subtypes should override
    after_creation: callables to run after creation. They are passed the
                    instance being created and the registry.
    use_autonaming: automatically generate the name if the new content object
                    is added to the parent.
    autonaming_prefix: uses this prefix for autonaming.

    IPool fields:
    -------------

    element_types: Set addable content types, class heritage is honored.

    IItem fields:
    -------------

    item_type: Set addable content types, class heritage is honored

    """


resource_metadata = ResourceMetadata(**RESOURCE_METADATA)


class IResource(ILocation):

    """Basic resource type."""


class IPool(IResource):

    """Resource with children - a folder in the object hierarchy. """

    def keys() -> Iterable:
        """ Return subobject names present in this pool."""

    def __iter__() -> Iterable:
        """ An alias for ``keys``."""

    def values() -> Iterable:
        """ Return subobjects present in this pool."""

    def items() -> Iterable:
        """ Return (name, value) pairs of subobjects in the folder."""

    def get(name: str, default=None) -> object:
        """ Get subobject by name.

        :raises `substanced.folder.FolderKeyError`: if name not in pool
        """

    def __contains__(name) -> bool:
        """Check if this pool contains an subobject named by name."""

    def add(name: str, other) -> str:
        """ Add subobject other.

        This method returns the name used to place the subobject in the
        folder (a derivation of ``name``, usually the result of
        ``self.check_name(name)``).
        """

    def check_name(name: str) -> str:
        """ Check and modify the name passed for validity.

        :return: the name (with any needed modifications).
        :raises `substanced.folder.FolderKeyError`: if name already in pool
        """

    def next_name(subobject, prefix='') -> str:
        """Return Name for subobject."""

    def add_next(subobject, prefix='') -> str:
        """Add new subobject and autgenerate name."""


class IItem(IPool):

    """Pool for any versionable objects (DAG), tags and related Pools. """


class ISimple(IResource):

    """Simple resource without versions and children."""


class ITag(ISimple):

    """Tag to link specific versions."""


class IItemVersion(ISimple):

    """Versionable resource, created during a Participation Process."""


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
