"""Adhocarcy sheets."""
from persistent.mapping import PersistentMapping
import colander
from pyramid.registry import Registry
from substanced.property import PropertySheet
from zope.interface import implementer

from adhocracy.utils import find_graph
from adhocracy.interfaces import IResourceSheet
from adhocracy.interfaces import ISheet
from adhocracy.interfaces import sheet_metadata
from adhocracy.interfaces import SheetMetadata
from adhocracy.schema import AbstractReferenceIterable
from adhocracy.utils import remove_keys_from_dict


@implementer(IResourceSheet)
class GenericResourceSheet(PropertySheet):

    """Generic sheet for resources to get/set the sheet data structure."""

    context = None  # resource to adapt
    request = None  # pyramid request object, just to fullfill the interface
    schema = None  # colander.MappingSchema object to define the data structure
    meta = None  # SheetMetadata
    _data_key = ''  # identifier to store data

    def __init__(self, metadata, context):
        schema = metadata.schema_class()
        self.schema = schema.bind(context=context)
        self.context = context
        self.meta = metadata
        self._data_key = self.meta.isheet.__identifier__
        self._graph = find_graph(context)

    @property
    def _data(self):
        if not hasattr(self.context, '_propertysheets'):
            self.context._propertysheets = PersistentMapping()
        if self._data_key not in self.context._propertysheets:
            self.context._propertysheets[self._data_key] = PersistentMapping()
        return self.context._propertysheets[self._data_key]

    @property
    def _key_reftype_map(self):
        refs = {}
        for child in self.schema:
            if isinstance(child, AbstractReferenceIterable):
                refs[child.name] = child.reftype
        return refs

    def get(self) -> dict:
        """Return appstruct."""
        appstruct = {}
        appstruct.update(self._get_non_reference_appstruct())
        appstruct.update(self._get_reference_appstruct())
        return appstruct

    def _get_default_appstruct(self) -> dict:
        appstruct = {}
        for child in self.schema.children:
            assert hasattr(child, 'default')
            appstruct[child.name] = child.default
        return appstruct

    def _get_non_reference_appstruct(self):
        appstruct = {}
        default = self._get_default_appstruct()
        for key, default_value in default.items():
            if key not in self._key_reftype_map:
                appstruct[key] = self._data.get(key, default_value)
        return appstruct

    def _get_reference_appstruct(self):
        appstruct = {}
        references = {}
        if self._graph:
            references = self._graph.get_references_for_isheet(
                self.context,
                self.meta.isheet)
        default = self._get_default_appstruct()
        for key, default_value in default.items():
            if key in self._key_reftype_map:
                appstruct[key] = references.get(key, default_value)
        return appstruct

    def set(self, appstruct: dict, omit=()) -> bool:
        """Store appstruct."""
        struct = remove_keys_from_dict(appstruct, keys_to_remove=omit)
        self._store_references(struct)
        self._store_non_references(struct)
        # FIXME: only store struct if values have changed
        return bool(struct)

    def _store_references(self, appstruct):
        if not self._graph:
            return
        for key, targets in appstruct.items():
            if key in self._key_reftype_map:
                reftyp = self._key_reftype_map[key]
                self._graph.set_references(self.context, targets, reftyp)

    def _store_non_references(self, appstruct):
        self._data.update(appstruct)

    def validate_cstruct(self, cstruct: dict) -> dict:
        """Validate schema :term:`cstruct`."""
        # FIXME: misleading name, it does not validate but deserialize.
        for child in self.schema:
            editable = getattr(child, 'editable', True)
            creatable = getattr(child, 'creatable', True)
            writable = editable or creatable
            if not writable:
                raise colander.Invalid(child, msg=u'This key is readonly')
        appstruct = self.schema.deserialize(cstruct)
        return appstruct

    def get_cstruct(self) -> dict:
        """Return schema :term:`cstruct`."""
        struct = self.get()
        cstruct = self.schema.serialize(struct)
        return cstruct


sheet_metadata_defaults = sheet_metadata._replace(
    isheet=ISheet,
    sheet_class=GenericResourceSheet,
    schema_class=colander.MappingSchema,
    permission_view='view',
    permission_edit='edit',
    permission_create='create',
)


def add_sheet_to_registry(metadata: SheetMetadata, registry: Registry):
    """Add sheet type to registry."""
    assert metadata.isheet.isOrExtends(ISheet)
    if metadata.create_mandatory:
        assert metadata.creatable and metadata.create_mandatory
    schema = metadata.schema_class()
    for child in schema.children:
        assert child.default != colander.null
        assert child.missing == colander.drop
    assert issubclass(schema.__class__, colander.MappingSchema)
    _assert_schema_preserves_super_type_data_structure(schema)

    def generic_resource_property_sheet_adapter(context):
        return metadata.sheet_class(metadata, context)

    registry.registerAdapter(generic_resource_property_sheet_adapter,
                             required=(metadata.isheet,),
                             provided=IResourceSheet,
                             name=metadata.isheet.__identifier__
                             )


def _assert_schema_preserves_super_type_data_structure(
        schema: colander.MappingSchema):
    super_defaults = []
    for super_schema in schema.__class__.__bases__:
        for child in super_schema().children:
            super_defaults.append((child.name, child.default))
    class_defaults = []
    for child in schema.children:
        class_defaults.append((child.name, child.default))
    for name, value in super_defaults:
        assert (name, value) in class_defaults


def includeme(config):  # pragma: no cover
    """Include all sheets in this package."""
    config.include('.name')
    config.include('.pool')
    config.include('.document')
    config.include('.versions')
    config.include('.tags')
