"""Data structures/validation, set/get for an isolated set of resource data."""

from itertools import chain
from logging import getLogger
from collections import Iterable

from persistent.mapping import PersistentMapping
from pyramid.decorator import reify
from pyramid.registry import Registry
from pyramid.request import Request
from pyramid.threadlocal import get_current_registry
from pyramid.traversal import resource_path
from substanced.property import PropertySheet
from transaction.interfaces import TransientError
from ZODB.POSException import POSError
from ZODB.POSException import ConnectionStateError
from zope.interface import implementer
import colander

from adhocracy_core.utils import find_graph
from adhocracy_core.utils import is_hidden
from adhocracy_core.utils import is_deleted
from adhocracy_core.events import ResourceSheetModified
from adhocracy_core.interfaces import IResourceSheet
from adhocracy_core.interfaces import ISheet
from adhocracy_core.interfaces import sheet_metadata
from adhocracy_core.interfaces import SheetMetadata
from adhocracy_core.schema import Reference
from adhocracy_core.utils import remove_keys_from_dict
from adhocracy_core.utils import normalize_to_tuple

logger = getLogger(__name__)


@implementer(IResourceSheet)
class AnnotationStorageSheet(PropertySheet):

    """Generic sheet for to get/set resource data as context annotation."""

    request = None
    """Pyramid request object, just to fulfill the interface."""

    def __init__(self, metadata, context):
        self.schema = metadata.schema_class()
        """:class:`colander.MappingSchema` to define the data structure."""
        self.context = context
        """Resource to adapt."""
        self.meta = metadata
        """SheetMetadata"""
        self._data_key = self.meta.isheet.__identifier__

    def get(self, params: dict={}) -> dict:
        """Return appstruct."""
        try:
            appstruct = self._default_appstruct
            appstruct.update(self._get_data_appstruct(params))
            appstruct.update(self._get_reference_appstruct(params))
            appstruct.update(self._get_back_reference_appstruct(params))
        except (ValueError, AttributeError, KeyError, ConnectionStateError,
                POSError) as err:  # pragma: no cover
            # If an error is raises here it is most likely because the Database
            # connection is closed (ConnectionStateError) somehow.
            # FIXME!! This should never happen, TEMPORALLY WORKAROUND
            msg = '\nError getting the sheet data for context {path}: ·{err}.'\
                  '\nRaising TransientError instead to reattemp the request.'
            logger.error(msg.format(path=resource_path(self.context),
                                    err=str(err)))
            raise TransientError(str(err))
            # Raise TransientError to make the pyramid_tm tween reattemp the
            # request. Hopefully it will work then.
        return appstruct

    @property
    def _default_appstruct(self) -> dict:
        """Bind `context` to schema and return schema node default values."""
        # context might have changed, so we don`t bind it until needed
        schema = self.schema.bind(context=self.context)
        items = [(n.name, n.default) for n in schema]
        return dict(items)

    def _get_data_appstruct(self, params: dict={}) -> iter:
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
        return find_graph(self.context)

    @property
    def _data(self):
        """Return dictionary to store data.

        This might be overridden in subclasses.
        """
        sheets_data = getattr(self.context, '_sheets', None)
        if sheets_data is None:
            sheets_data = PersistentMapping()
            setattr(self.context, '_sheets', sheets_data)
        data = sheets_data.get(self._data_key, None)
        if data is None:
            data = PersistentMapping()
            sheets_data[self._data_key] = data
        return data

    def _get_reference_appstruct(self, params: dict={}) -> iter:
        """Return reference data.

        This might be overridden in subclasses.
        """
        references = self._get_references()
        for key, node in self._reference_nodes.items():
            node_references = references.get(key, None)
            if not node_references:
                continue
            if isinstance(node, Reference):
                yield(key, node_references[0])
            else:
                yield(key, node_references)

    def _get_references(self) -> dict:
        if not self._graph:
            return {}
        return self._graph.get_references_for_isheet(self.context,
                                                     self.meta.isheet)

    @reify
    def _reference_nodes(self) -> dict:
        nodes = {}
        for node in self.schema:
            if hasattr(node, 'reftype') and not node.backref:
                nodes[node.name] = node
        return nodes

    def _get_back_reference_appstruct(self, params: dict={}) -> dict:
        for key, node in self._back_reference_nodes.items():
            node_backrefs = self._get_backrefs(node)
            if not isinstance(node_backrefs, Iterable):  # ease testing
                continue
            visible_node_backrefs = []
            for resource in node_backrefs:
                if is_deleted(resource):
                    continue
                if is_hidden(resource):
                    continue
                visible_node_backrefs.append(resource)
            if isinstance(node, Reference):
                yield(key, visible_node_backrefs[0])
            else:
                yield(key, visible_node_backrefs)

    def _get_backrefs(self, node: Reference) -> Iterable:
        """Return backreference data.

        This might be overridden in subclasses.
        """
        if not self._graph:
            return {}
        isheet = node.reftype.getTaggedValue('source_isheet')
        backrefs = self._graph.get_back_references_for_isheet(self.context,
                                                              isheet)
        field = node.reftype.getTaggedValue('source_isheet_field')
        if field:
            return backrefs.get(field, None)
        else:
            # return all backrefs regardless of field name
            return list(chain(*backrefs.values()))

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
            registry=None,
            request: Request=None,
            omit_readonly: bool=True) -> bool:
        """Store appstruct."""
        appstruct_old = self.get()
        appstruct = self._omit_omit_keys(appstruct, omit)
        if omit_readonly:
            appstruct = self._omit_readonly_keys(appstruct)
        self._store_data(appstruct)
        if registry is None:
            registry = get_current_registry(self.context)
        self._store_references(appstruct, registry)
        # FIXME: only store struct if values have changed
        self._notify_resource_sheet_modified(send_event,
                                             registry,
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

        Bind `request` and `context` (self.context) to colander schema
        (self.schema). Get sheet appstruct data and serialize.

        :param params: optional parameters that can modify the appearance
        of the returned dictionary, e.g. query parameters in a GET request
        """
        schema = self._get_schema_for_cstruct(request, params)
        appstruct = self.get(params=params)
        cstruct = schema.serialize(appstruct)
        return cstruct

    def _get_schema_for_cstruct(self, request, params: dict):
        """Return customized schema to serialize cstruct data.

        This might be overridden in subclasses.
        """
        schema = self.schema.bind(context=self.context,
                                  request=request)
        return schema


@implementer(IResourceSheet)
class AttributeStorageSheet(AnnotationStorageSheet):

    """Sheet class that stores data as context attributes."""

    @property
    def _data(self):
        return self.context.__dict__


sheet_metadata_defaults = sheet_metadata._replace(
    isheet=ISheet,
    sheet_class=AnnotationStorageSheet,
    schema_class=colander.MappingSchema,
    permission_view='view',
    permission_edit='edit_sheet',
    permission_create='create_sheet',
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
