"""Data structures/validation, set/get for an isolated set of resource data."""

from logging import getLogger
from collections import Iterable

from persistent.mapping import PersistentMapping
from pyramid.decorator import reify
from pyramid.registry import Registry
from pyramid.request import Request
from pyramid.threadlocal import get_current_registry
from substanced.util import find_service
from zope.interface import implementer
from zope.interface.interfaces import IInterface
import colander

from adhocracy_core.events import ResourceSheetModified
from adhocracy_core.interfaces import IResourceSheet
from adhocracy_core.interfaces import ISheet
from adhocracy_core.interfaces import SheetMetadata
from adhocracy_core.interfaces import Reference
from adhocracy_core.interfaces import SearchQuery
from adhocracy_core.interfaces import search_query
from adhocracy_core import schema
from adhocracy_core.utils import remove_keys_from_dict
from adhocracy_core.utils import normalize_to_tuple
from adhocracy_core.utils import find_graph

logger = getLogger(__name__)

# TODO refactor PropertySheet


@implementer(IResourceSheet)
class BaseResourceSheet:

    """Basic Resource sheet to get/set resource appstruct data.

    Subclasses have to implement the `_data` property to store appstruct data.
    """

    request = None  # just to follow the interface."""

    def __init__(self, meta, context, registry=None):
        self.schema = meta.schema_class()
        """:class:`colander.MappingSchema` to define the data structure."""
        self.context = context
        """Resource to adapt."""
        self.meta = meta
        """SheetMetadata"""
        self._data_key = self.meta.isheet.__identifier__
        if registry is None:
            registry = get_current_registry(context)
        self.registry = registry
        """Pyramid :class:`pyramid.registry.Registry`. If `None`
           :func:`pyramid.threadlocal.get_current_registry` is used get it.
        """

    def get(self, params: dict={}) -> dict:
        """Return appstruct data.

        :param params: Parameters to update the search query to find
            references data (possible items are described in
            :class:`adhocracy_core.interfaces.SearchQuery`).
            The default search query is set in the `_references_query`
            property.
        """
        query = self._references_query
        if params:
            query = query._replace(**params)
        appstruct = self._default_appstruct
        appstruct.update(self._get_data_appstruct())
        appstruct.update(self._get_reference_appstruct(query))
        appstruct.update(self._get_back_reference_appstruct(query))
        return appstruct

    @property
    def _default_appstruct(self) -> dict:
        """Return schema default values."""
        schema = self._get_schema_for_default_values()
        items = [(n.name, n.default) for n in schema]
        return dict(items)

    def _get_schema_for_default_values(self) -> colander.SchemaNode:
        """Return customized schema to get default values.

        This might be overridden in subclasses.
        """
        schema = self.schema.bind(context=self.context,
                                  registry=self.registry)
        return schema

    def _get_data_appstruct(self) -> iter:
        """Return non references data.

        This might be overridden in subclasses.
        """
        for key in self._data_keys:
            if key in self._data:
                yield (key, self._data[key])

    @reify
    def _data_keys(self) -> list:
        return [n.name for n in self.schema if not hasattr(n, 'reftype')]

    @property
    def _graph(self):
        graph = find_graph(self.context)
        return graph

    @property
    def _catalogs(self):
        catalogs = find_service(self.context, 'catalogs')
        return catalogs

    @property
    def _data(self):
        """Return dictionary to store data."""
        raise NotImplementedError

    @property
    def _references_query(self) -> SearchQuery:
        query = {'only_visible': False,
                 'resolve': True,
                 'allows': (),
                 'references': [],
                 }
        return search_query._replace(**query)

    def _get_reference_appstruct(self, query: SearchQuery) -> iter:
        """Return reference data.

        This might be overridden in subclasses.
        """
        for key, node in self._reference_nodes.items():
            node_references = self._get_references(key, query)
            if len(node_references) == 0:
                continue
            if isinstance(node, schema.Reference):
                yield(key, list(node_references)[0])
            else:
                yield(key, node_references)

    def _get_references(self, field, query) -> Iterable:
        if self._catalogs is None:
            return []  # ease testing
        reference = Reference(self.context, self.meta.isheet, field, None)
        query_field = query._replace(references=[reference])
        result = self._catalogs.search(query_field)
        return result.elements

    @reify
    def _reference_nodes(self) -> dict:
        nodes = {}
        for node in self.schema:
            if hasattr(node, 'reftype') and not node.backref:
                nodes[node.name] = node
        return nodes

    def _get_target_isheet(self, reference_node) -> IInterface:
        reftype = self._reference_nodes[reference_node].reftype
        target_isheet = reftype.getTaggedValue('target_isheet')
        return target_isheet

    def _get_back_reference_appstruct(self, query: SearchQuery) -> dict:
        for key, node in self._back_reference_nodes.items():
            node_backrefs = self._get_backrefs(key, query)
            if not isinstance(node_backrefs, Iterable):  # ease testing
                continue
            if isinstance(node, schema.Reference):
                yield(key, node_backrefs[0])
            else:
                yield(key, node_backrefs)

    def _get_backrefs(self, field, query: SearchQuery) -> Iterable:
        """Return back reference data.

        This might be overridden in subclasses.
        """
        if self._catalogs is None:
            return []  # ease testing
        reftype = self._back_reference_nodes[field].reftype
        isheet = reftype.getTaggedValue('source_isheet')
        isheet_field = reftype.getTaggedValue('source_isheet_field')
        reference = Reference(None, isheet, isheet_field, self.context)
        query_field = query._replace(references=[reference])
        result = self._catalogs.search(query_field)
        return result.elements

    @reify
    def _back_reference_nodes(self) -> dict:
        nodes = {}
        for node in self.schema:
            if hasattr(node, 'reftype') and node.backref:
                nodes[node.name] = node
        return nodes

    def set(self,
            appstruct: dict,
            omit=(),
            send_event=True,
            request: Request=None,
            omit_readonly: bool=True) -> bool:
        """Store appstruct."""
        appstruct_old = self.get()
        appstruct = self._omit_omit_keys(appstruct, omit)
        if omit_readonly:
            appstruct = self._omit_readonly_keys(appstruct)
        self._store_data(appstruct)
        self._store_references(appstruct, self.registry)
        # TODO: only store struct if values have changed
        self._notify_resource_sheet_modified(send_event,
                                             self.registry,
                                             appstruct_old,
                                             appstruct,
                                             request)
        return bool(appstruct)

    def _omit_readonly_keys(self, appstruct: dict):
        omit_keys = tuple(self._readonly_keys)
        return remove_keys_from_dict(appstruct, keys_to_remove=omit_keys)

    def _omit_omit_keys(self, appstruct: dict, omit):
        omit_keys = normalize_to_tuple(omit)
        return remove_keys_from_dict(appstruct, keys_to_remove=omit_keys)

    @reify
    def _readonly_keys(self):
        return [n.name for n in self.schema if getattr(n, 'readonly', False)]

    def _store_data(self, appstruct):
        for key in self._data_keys:
            if key in appstruct:
                self._data[key] = appstruct[key]

    def _store_references(self, appstruct, registry):
        if self._graph:
            self._graph.set_references_for_isheet(self.context,
                                                  self.meta.isheet,
                                                  appstruct,
                                                  registry)

    def _notify_resource_sheet_modified(self,
                                        send_event,
                                        registry,
                                        old,
                                        new,
                                        request: Request):
        if send_event:
            event = ResourceSheetModified(self.context,
                                          self.meta.isheet,
                                          registry,
                                          old,
                                          new,
                                          request)
            registry.notify(event)

    def get_cstruct(self, request: Request, params: dict={}):
        """Return cstruct data.

        Bind `request` and `self.context` to colander schema
        (self.schema). Get sheet appstruct data and serialize.

        :param request: Bind to schema and get principals to filter elements
                        by 'view' permission.
        :param params: Parameters to update the search query to find reference
                       data.

        Automatically set params are: `only_visible` and `allows` view
        permission.
        """
        params['allows'] = (request.effective_principals, 'view')
        params['only_visible'] = True
        schema = self._get_schema_for_cstruct(request, params)
        appstruct = self.get(params=params)
        cstruct = schema.serialize(appstruct)
        return cstruct

    def _get_schema_for_cstruct(self, request, params: dict):
        """Return customized schema to serialize cstruct data.

        This might be overridden in subclasses.
        """
        schema = self.schema.bind(context=self.context,
                                  registry=self.registry,
                                  request=request)
        return schema

    def delete_field_values(self, fields: [str]):
        """Delete value for every field name in `fields`."""
        for key in fields:
            if key in self._data:
                del self._data[key]

    def after_set(self, changed: bool):
        """Hook to run after setting data. Not used."""
        raise NotImplementedError


@implementer(IResourceSheet)
class AnnotationStorageSheet(BaseResourceSheet):

    """Resource Sheet that stores data in dictionary annotation."""

    @property
    def _data(self):
        """Return dictionary to store data."""
        sheets_data = getattr(self.context, '_sheets', None)
        if sheets_data is None:
            sheets_data = PersistentMapping()
            setattr(self.context, '_sheets', sheets_data)
        data = sheets_data.get(self._data_key, None)
        if data is None:
            data = PersistentMapping()
            sheets_data[self._data_key] = data
        return data


@implementer(IResourceSheet)
class AttributeStorageSheet(AnnotationStorageSheet):

    """Resource Sheet that stores data as context attributes."""

    @property
    def _data(self):
        return self.context.__dict__


sheet_meta = SheetMetadata(isheet=ISheet,
                           sheet_class=AnnotationStorageSheet,
                           schema_class=colander.MappingSchema,
                           permission_view='view',
                           permission_edit='edit_sheet',
                           permission_create='create_sheet',
                           readable=True,
                           editable=True,
                           creatable=True,
                           create_mandatory=False,
                           mime_type_validator=None,
                           image_sizes=None,
                           )


def add_sheet_to_registry(metadata: SheetMetadata, registry: Registry):
    """Register sheet adapter and metadata to registry.

    There registry should have an `content` attribute with
    :class:`adhocracy_core.registry.ResourceRegistry` to store the metadata.
    """
    assert metadata.isheet.isOrExtends(ISheet)
    isheet = metadata.isheet
    if metadata.create_mandatory:
        assert metadata.creatable and metadata.create_mandatory
    schema = metadata.schema_class()
    for child in schema.children:
        assert child.default != colander.null
        assert child.default != colander.drop
    assert issubclass(schema.__class__, colander.MappingSchema)
    _assert_schema_preserves_super_type_data_structure(schema)
    registry.content.sheets_meta[isheet] = metadata


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
    """Include the sheets in this package."""
    config.include('.name')
    config.include('.pool')
    config.include('.document')
    config.include('.versions')
    config.include('.tags')
    config.include('.principal')
    config.include('.metadata')
    config.include('.comment')
    config.include('.rate')
    config.include('.asset')
    config.include('.sample_image')
    config.include('.geo')
    config.include('.workflow')
    config.include('.title')
    config.include('.description')
