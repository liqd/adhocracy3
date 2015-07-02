"""Data structures/validation, set/get for an isolated set of resource data."""

from logging import getLogger
from collections import defaultdict

from persistent.mapping import PersistentMapping
from pyramid.decorator import reify
from pyramid.registry import Registry
from pyramid.request import Request
from pyramid.settings import asbool
from pyramid.threadlocal import get_current_registry
from substanced.util import find_service
from zope.interface import implementer
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
        if registry is None:
            registry = get_current_registry(context)
        self.registry = registry
        """Pyramid :class:`pyramid.registry.Registry`. If `None`
           :func:`pyramid.threadlocal.get_current_registry` is used get it.
        """

    @reify
    def _fields(self) -> dict:
        fields = defaultdict(dict)
        for node in self.schema.children:
            field = node.name
            if not hasattr(node, 'reftype'):
                fields['data'][field] = node
            elif not node.backref:
                fields['reference'][field] = node
            else:
                fields['back_reference'][field] = node
            if getattr(node, 'readonly', False):
                fields['readonly'][field] = node
        return fields

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

    def get(self, params: dict={}, add_back_references=True) -> dict:
        """Return appstruct data.

        :param params: Parameters to update the search query to find
            references data (possible items are described in
            :class:`adhocracy_core.interfaces.SearchQuery`).
            The default search query is set in the `_references_query`
            property.
        :param add_back_references: allow to omit back references
        """
        appstruct = self._get_default_appstruct()
        appstruct.update(self._get_data_appstruct())
        query = self._get_references_query(params)
        appstruct.update(self._get_reference_appstruct(query))
        if add_back_references:
            appstruct.update(self._get_back_reference_appstruct(query))
        return appstruct

    def _get_default_appstruct(self) -> dict:
        schema = self.schema.bind(context=self.context,
                                  registry=self.registry)
        items = [(n.name, n.default) for n in schema]
        return dict(items)

    def _get_data_appstruct(self) -> iter:
        """Might be overridden in subclasses."""
        for key in self._fields['data']:
            if key in self._data:
                yield (key, self._data[key])

    def _get_references_query(self, params: dict) -> SearchQuery:
        """Might be overridden in subclasses."""
        default_params = {'only_visible': False,
                          'resolve': True,
                          'allows': (),
                          'references': [],
                          }
        query = search_query._replace(**default_params)
        if params:
            query = query._replace(**params)
        return query

    def _get_reference_appstruct(self, query: SearchQuery) -> iter:
        """Might be overridden in subclasses."""
        fields = self._fields['reference'].items()
        get_ref = lambda node: Reference(self.context, self.meta.isheet,
                                         node.name, None)
        return self._yield_references(self._catalogs, fields, query, get_ref)

    def _get_back_reference_appstruct(self, query: SearchQuery) -> dict:
        fields = self._fields['back_reference'].items()

        def get_ref(node):
            isheet = node.reftype.getTaggedValue('source_isheet')
            isheet_field = node.reftype.getTaggedValue('source_isheet_field')
            return Reference(None, isheet, isheet_field, self.context)

        return self._yield_references(self._catalogs, fields, query, get_ref)

    def _yield_references(self, catalogs, fields, query, create_ref) -> iter:
        if not catalogs:
            return iter([])  # ease testing
        for field, node in fields:
            reference = create_ref(node)
            query_field = query._replace(references=[reference])
            elements = self._catalogs.search(query_field).elements
            if len(elements) == 0:
                continue
            if isinstance(node, schema.Reference):
                yield(field, elements[0])
            else:
                yield(field, elements)

    def set(self,
            appstruct: dict,
            omit=(),
            send_event=True,
            request: Request=None,
            omit_readonly: bool=True) -> bool:
        """Store appstruct."""
        appstruct_old = self.get(add_back_references=False)
        appstruct = self._omit_omit_keys(appstruct, omit)
        if omit_readonly:
            appstruct = self._omit_readonly_keys(appstruct)
        self._store_data(appstruct)
        self._store_references(appstruct, self.registry)
        if send_event:
            event = ResourceSheetModified(self.context,
                                          self.meta.isheet,
                                          self.registry,
                                          appstruct_old,
                                          appstruct,
                                          request)
            self.registry.notify(event)
        return bool(appstruct)
        # TODO: only store struct if values have changed

    def _omit_readonly_keys(self, appstruct: dict):
        omit_keys = tuple(self._fields['readonly'])
        return remove_keys_from_dict(appstruct, keys_to_remove=omit_keys)

    def _omit_omit_keys(self, appstruct: dict, omit):
        omit_keys = normalize_to_tuple(omit)
        return remove_keys_from_dict(appstruct, keys_to_remove=omit_keys)

    def _store_data(self, appstruct):
        """Might be overridden in subclasses."""
        for key in self._fields['data']:
            if key in appstruct:
                self._data[key] = appstruct[key]

    def _store_references(self, appstruct, registry):
        """Might be overridden in subclasses."""
        if not self._graph:
            return  # ease testing
        self._graph.set_references_for_isheet(self.context,
                                              self.meta.isheet,
                                              appstruct,
                                              registry)

    def get_cstruct(self, request: Request, params: dict=None):
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
        params = params or {}
        filter_view_permission = asbool(self.registry.settings.get(
            'adhocracy.filter_by_view_permission', True))
        if filter_view_permission:
            params['allows'] = (request.effective_principals, 'view')
        filter_visible = asbool(self.registry.settings.get(
            'adhocracy.filter_by_visible', True))
        if filter_visible:
            params['only_visible'] = True
        schema = self._get_schema_for_cstruct(request, params)
        appstruct = self.get(params=params)
        cstruct = schema.serialize(appstruct)
        return cstruct

    def _get_schema_for_cstruct(self, request, params: dict):
        """Might be overridden in subclasses."""
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
class AnnotationRessourceSheet(BaseResourceSheet):

    """Resource Sheet that stores data in dictionary annotation."""

    def __init__(self, meta, context, registry=None):
        super().__init__(meta, context, registry)
        self._data_key = self.meta.isheet.__identifier__

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
class AttributeResourceSheet(BaseResourceSheet):

    """Resource Sheet that stores data as context attributes."""

    @property
    def _data(self):
        return self.context.__dict__


sheet_meta = SheetMetadata(isheet=ISheet,
                           sheet_class=AnnotationRessourceSheet,
                           schema_class=colander.MappingSchema,
                           permission_view='view',
                           permission_edit='edit',
                           permission_create='create',
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
    config.include('.image')
    config.include('.geo')
    config.include('.workflow')
    config.include('.title')
    config.include('.description')
    config.include('.badge')
    config.include('.logbook')
