"""Rest API views."""
from adhocracy.interfaces import IResource
from adhocracy.interfaces import IItem
from adhocracy.interfaces import IItemVersion
from adhocracy.interfaces import ISimple
from adhocracy.interfaces import IPool
from adhocracy.interfaces import ISheet
from adhocracy.rest.schemas import ResourceResponseSchema
from adhocracy.rest.schemas import ItemResponseSchema
from adhocracy.rest.schemas import POSTItemRequestSchema
from adhocracy.rest.schemas import POSTResourceRequestSchema
from adhocracy.rest.schemas import PUTResourceRequestSchema
from adhocracy.rest.schemas import GETResourceResponseSchema
from adhocracy.rest.schemas import GETItemResponseSchema
from adhocracy.rest.schemas import OPTIONResourceResponseSchema
from adhocracy.sheets.versions import followed_by
from adhocracy.sheets.versions import IVersionable
from adhocracy.schema import AbsolutePath
from adhocracy.schema import AbstractReferenceIterableSchemaNode
from adhocracy.utils import get_resource_interface
from adhocracy.utils import strip_optional_prefix
from adhocracy.utils import to_dotted_name
from adhocracy.utils import get_all_taggedvalues
from colander import SchemaNode
from copy import deepcopy
from cornice.util import json_error
from cornice.schemas import validate_colander_schema
from cornice.schemas import CorniceSchema
from pyramid.path import DottedNameResolver
from pyramid.view import view_config
from pyramid.view import view_defaults
from pyramid.traversal import resource_path
from substanced.interfaces import IRoot
from substanced.util import find_objectmap

import functools


def validate_sheet_cstructs(context, request, sheets):
    """Validate propertysheet data."""
    validated = request.validated.get('data', {})
    sheetnames_wrong = []
    for sheetname, cstruct in validated.items():
        if sheetname in sheets:
            sheet = sheets[sheetname]
            appstruct = sheet.validate_cstruct(cstruct)
            validated[sheetname] = appstruct
        else:
            sheetnames_wrong.append(sheetname)
    for sheetname in sheetnames_wrong:
        del validated[sheetname]


def validate_put_sheet_cstructs(context, request):
    """Validate propertysheet data for put requests."""
    sheets = request.registry.content.resource_sheets(
        context, request, onlyeditable=True)
    validate_sheet_cstructs(context, request, sheets)


def validate_post_sheet_cstructs(context, request):
    """Validate propertysheet data for post requests."""
    type_ = request.validated.get('content_type', '')
    dummy = object()
    sheets = {}
    if type_ in request.registry.content.resource_types():
        dummy = request.registry.content.create(
            type_, run_after_creation=False)
        dummy.__parent__ = context
        sheets = request.registry.content.resource_sheets(
            dummy, request, onlycreatable=True)
    validate_sheet_cstructs(dummy, request, sheets)


def validate_post_root_versions(context, request):
    """Check and transform the 'root_version' paths to resources."""
    root_paths = request.validated.get('root_versions', [])
    om = find_objectmap(context)
    if not om:
        root_paths = []

    root_resources = []
    for path in root_paths:
        path_tuple = tuple(str(path).split('/'))
        res = om.object_for(path_tuple)
        if res is None:
            error = 'This resource path does not exist: {p}'.format(p=path)
            request.errors.add('body", "root_versions', error)
            continue
        if not IItemVersion.providedBy(res):
            error = 'This resource is not a valid '\
                    'root version: {p}'.format(p=path)
            request.errors.add('body', 'root_versions', error)
            continue
        root_resources.append(res)

    request.validated['root_versions'] = root_resources


def validate_put_sheet_names(context, request):
    """Validate propertysheet names for put requests. Return None."""
    sheets = request.registry.content.resource_sheets(
        context, request, onlyeditable=True)
    puted = request.validated.get('data', {}).keys()
    wrong_sheets = set(puted) - set(sheets)
    if wrong_sheets:
        error = 'The following propertysheets are mispelled or you do not '\
                'have the edit permission: {names}'.format(names=wrong_sheets)
        request.errors.add('body', 'data', error)


def validate_post_sheet_names_and_resource_type(context, request):
    """Validate addable propertysheet names for post requests."""
    addables = request.registry.content.resource_addables(context, request)
    content_type = request.validated.get('content_type', '')
    if content_type not in addables:
        error = 'The following resource type is not '\
                'addable: {iresource} '.format(iresource=content_type)
        request.errors.add('body', 'content_type', error)
    else:
        optional = addables[content_type]['sheets_optional']
        mandatory = addables[content_type]['sheets_mandatory']
        posted = request.validated.get('data', {}).keys()
        wrong_sheets = set(posted) - set(optional + mandatory)
        if wrong_sheets:
            error = 'The following propertysheets are not allowed for this '\
                    'resource type or mispelled: {names}'.format(names=
                                                                 wrong_sheets)
            request.errors.add('body', 'data', error)
        missing_sheets = set(mandatory) - set(posted)
        if missing_sheets:
            error = 'The following propertysheets are mandatory to create '\
                    'this resource: {names}'.format(names=missing_sheets)
            request.errors.add('body', 'data', error)


def validate_request_data(context, request, schema=None, extra_validators=[]):
        """ Validate request data.

        Args:
            context (class): context passed to validator functions
            request (IRequest): request object passed to validator functions
            schema (colander.Schema): Schema to validate request body with json
                data, request url parameters or headers (based on Cornice).
            extra_validators (List): validator functions with parameter context
                and request.

        Raises:
            _JSONError: HTTP 400 error based on Cornice if bad request data.

        """
        if schema:
            schemac = CorniceSchema.from_colander(schema)
            validate_colander_schema(schemac, request)
        for val in extra_validators:
            val(context, request)
        if request.errors:
            request.validated = {}
            raise json_error(request.errors)


def validate_request_data_decorator():
    """Validate request data for every http method of your RESTView class.

    Runs validate_request_data with schema and validators set in the attribute
    `validation_<http method>`.

    Returns:
        class: view class
    Raises:
        _JSONError: HTTP 400 error based on Cornice if bad request data.

    """
    def _dec(f):
        @functools.wraps(f)
        def wrapper(context, request):
            http_method = request.method.upper()
            view_class = f.__original_view__
            vals = getattr(view_class, 'validation_' + http_method, (None, []))
            validate_request_data(context, request, schema=vals[0],
                                  extra_validators=vals[1])
            return f(context, request)
        return wrapper
    return _dec


class RESTView(object):

    """Class stub with request data validation support.

    Subclasses must implement the wanted request methods
    and configure the pyramid view::

        @view_defaults(
            renderer='simplejson',
            context=IResource,
            decorator=validate_request_data_decorator(),
        )
        class MySubClass(RESTView):
            validation_GET = (MyColanderSchema, [my_extra_validation_function])

            @view_config(request_method='GET')
            def get(self):
            ...

    """

    validation_OPTIONS = (None, [])
    validation_HEAD = (None, [])
    validation_GET = (None, [])
    validation_PUT = (None, [])
    validation_POST = (None, [])

    reserved_names = []

    def __init__(self, context, request):
        self.context = context
        self.request = request
        registry = request.registry.content
        self.registry = registry


@view_defaults(
    renderer='simplejson',
    context=IResource,
    decorator=validate_request_data_decorator(),
)
class ResourceRESTView(RESTView):

    """Default view for Resources, implements get and options."""

    @view_config(request_method='OPTIONS')
    def options(self):
        """Handle OPTIONS requests.

        Return dictionary describing the available request and response
        data structures.

        """
        addables = self.registry.resource_addables(self.context, self.request)
        sheets_view = self.registry.resource_sheets(self.context, self.request,
                                                    onlyviewable=True)
        sheets_edit = self.registry.resource_sheets(self.context, self.request,
                                                    onlyeditable=True)

        cstruct_singleton = OPTIONResourceResponseSchema().serialize()
        cstruct = deepcopy(cstruct_singleton)
        for sheet in sheets_edit:
            cstruct['PUT']['request_body']['data'][sheet] = {}
        for sheet in sheets_view:
            cstruct['GET']['response_body']['data'][sheet] = {}
        for type, sheets in addables.items():
            names = sheets['sheets_optional'] + sheets['sheets_mandatory']
            sheets_dict = dict([(s, {}) for s in names])
            post_data = {'content_type': type, 'data': sheets_dict}
            cstruct['POST']['request_body'].append(post_data)
        return cstruct

    @view_config(request_method='GET')
    def get(self):
        """Handle GET requests. Return dict with resource data structure."""
        sheets_view = self.registry.resource_sheets(self.context, self.request,
                                                    onlyviewable=True)
        response_schema = GETResourceResponseSchema()
        struct = {'data': {}}
        for sheet in sheets_view.values():
            key = sheet.iface.__identifier__
            struct['data'][key] = sheet.get_cstruct()
            if issubclass(IVersionable, sheet.iface):
                # Calculate followed_by attribute of IVersionable

                # FIXME: The RestView is generic and should not care
                # for specific sheets/Resource types at all.
                # The right place to calculate followed_by is a custom
                # adapter for IVersionable sheets or better find an abstract
                # way to handle backrefs - joka
                struct['data'][key]['followed_by'] = followed_by(self.context)
        struct['path'] = resource_path(self.context)
        iresource = get_resource_interface(self.context)
        struct['content_type'] = iresource.__identifier__
        if IItem.providedBy(self.context):
            response_schema = GETItemResponseSchema()
            for v in self.context.values():
                if IItemVersion.providedBy(v):
                    struct['first_version_path'] = resource_path(v)
                    break
        return response_schema.serialize(struct)


@view_defaults(
    renderer='simplejson',
    context=ISimple,
    decorator=validate_request_data_decorator(),
)
class SimpleRESTView(ResourceRESTView):

    """View for simples (non versionable), implements get, options and put."""

    validation_PUT = (PUTResourceRequestSchema,
                      [validate_put_sheet_names,
                       validate_put_sheet_cstructs])

    @view_config(request_method='OPTIONS')
    def options(self):
        """Handle OPTIONS requests. Return dict."""
        return super(SimpleRESTView, self).options()

    @view_config(request_method='GET')
    def get(self):
        """Handle GET requests. Return dict."""
        return super(SimpleRESTView, self).get()

    @view_config(request_method='PUT')
    def put(self):
        """Handle HTTP PUT. Return dict with PATH of modified resource."""
        sheets = self.registry.resource_sheets(self.context, self.request,
                                               onlyeditable=True)
        appstructs = self.request.validated.get('data', {})
        for sheetname, appstruct in appstructs.items():
            sheet = sheets[sheetname]
            sheet.set(appstruct)
        struct = {}
        struct['path'] = resource_path(self.context)
        iresource = get_resource_interface(self.context)
        struct['content_type'] = iresource.__identifier__
        return ResourceResponseSchema().serialize(struct)


@view_defaults(
    renderer='simplejson',
    context=IPool,
    decorator=validate_request_data_decorator(),
)
class PoolRESTView(SimpleRESTView):

    """View for Pools, implements get, options, put and post."""

    validation_POST = (POSTResourceRequestSchema,
                       [validate_post_sheet_names_and_resource_type,
                        validate_post_sheet_cstructs])

    @view_config(request_method='OPTIONS')
    def options(self):
        """Handle OPTIONS requests. Return dict."""
        return super(PoolRESTView, self).options()

    @view_config(request_method='GET')
    def get(self):
        """Handle GET requests. Return dict."""
        return super(PoolRESTView, self).get()

    @view_config(request_method='PUT')
    def put(self):
        """Handle HTTP PUT. Return dict with PATH of modified resource."""
        return super(PoolRESTView, self).put()

    def build_post_response(self, resource):
        """Helper method that builds a response for a POST request.

        Returns:
            the serialized response

        """
        response_schema = ResourceResponseSchema()
        struct = {}
        struct['path'] = resource_path(resource)
        iresource = get_resource_interface(resource)
        struct['content_type'] = iresource.__identifier__
        if IItem.providedBy(resource):
            response_schema = ItemResponseSchema()
            for v in resource.values():
                if IItemVersion.providedBy(v):
                    struct['first_version_path'] = resource_path(v)
                    break
        return response_schema.serialize(struct)

    @view_config(request_method='POST')
    def post(self):
        """HTTP POST. Return dictionary with PATH of new resource."""
        resource_type = self.request.validated['content_type']
        appstructs = self.request.validated.get('data', {})
        resource = self.registry.create(resource_type, self.context,
                                        appstructs=appstructs)
        return self.build_post_response(resource)


@view_defaults(
    renderer='simplejson',
    context=IItem,
    decorator=validate_request_data_decorator(),
)
class ItemRESTView(PoolRESTView):

    """View for Items and ItemVersions, overwrites POST handling."""

    validation_POST = (POSTItemRequestSchema,
                       [validate_post_sheet_names_and_resource_type,
                        validate_post_root_versions,
                        validate_post_sheet_cstructs])

    @view_config(request_method='POST')
    def post(self):
        """HTTP POST. Return dictionary with PATH of new resource."""
        resource_type = self.request.validated['content_type']
        appstructs = self.request.validated.get('data', {})
        root_versions = self.request.validated.get('root_versions', [])
        resource = self.registry.create(resource_type, self.context,
                                        appstructs=appstructs,
                                        root_versions=root_versions)
        return self.build_post_response(resource)


@view_defaults(
    renderer='simplejson',
    context=IRoot,
    name='meta_api'
)
class MetaApiView(RESTView):

    """Access to metadata about the API specification of this installation.

    Returns a JSON document describing the existing resources and sheets.

    """

    def __init__(self, context, request):
        """Create a new instance."""
        super().__init__(context, request)
        self.resolv = DottedNameResolver()

    def _describe_resources(self, resource_types):
        """Build a description of the resources registered in the system.

        Args:
          resource_types: list of resource types as returned by the registry

        Returns:
          A 2-tuple of (resource_map, sheet_set)

          resource_map is a dict (suitable for JSON serialization) that
          describes all the resources registered in the system.

          sheet_set is a set containing the names of all sheets references by
          resources.

        """
        resource_map = {}
        sheet_set = set()

        for name, value in resource_types.items():
            prop_map = {}
            metadata = value['metadata']

            # List of sheets
            sheets = []
            if 'basic_sheets' in metadata:
                sheets.extend(metadata['basic_sheets'])
            if 'extended_sheets' in metadata:
                sheets.extend(metadata['extended_sheets'])
            prop_map['sheets'] = [to_dotted_name(s) for s in sheets]
            sheet_set.update(sheets)

            # Main element type if this is a pool or item
            if 'item_type' in metadata:
                item_type = to_dotted_name(metadata['item_type'])
                prop_map['item_type'] = item_type
            else:
                item_type = None

            # Other addable element types
            if 'element_types' in metadata:
                element_types = metadata['element_types']
                element_names = []

                for typ in element_types:
                    element_names.append(to_dotted_name(typ))

                prop_map['element_types'] = element_names
            resource_map[name] = prop_map
        return resource_map, sheet_set

    def _sheet_field_readable(self, sheetname, fieldname, sheet_readonly):
        """Hook that allows modifying the read-only status for fields.

        This allows setting a field read-only even if the whole sheet is
        writeable in the backend.

        Returns True or False.

        FIXME: this is just a cosmetic ad-hoc solution since the read-only
        status in the backend is not affected.

        """
        if (sheetname, fieldname) == ('adhocracy.sheets.versions.IVersionable',
                                      'followed_by'):
            return True
        else:
            return sheet_readonly

    def _describe_sheets(self, sheet_metadata):
        """Build a description of the sheets used in the system.

        Args:
          sheet_metadata: mapping of sheet names to metadata about them, as
            returned by the registry

        Returns:
          A dict (suitable for JSON serialization) that describes the sheets
          and their fields

        """
        sheet_map = {}
        for sheet_name, metadata in sheet_metadata.items():
            # readonly and createmandatory flags are currently defined for
            # the whole sheet, but we copy them as attributes into each field
            # definition, since this might change in the future.
            # (The _sheet_field_readable method already allows overwriting the
            # readable flag on a field-by-field basis, but it's somewhat
            # ad-hoc.)
            createmandatory = metadata['createmandatory']
            readonly = metadata['readonly']
            fields = []

            # Create field definitions
            for key, value in metadata.items():
                fieldname = strip_optional_prefix(key, 'field:')

                # Only process 'field:...' definitions
                if fieldname != key:

                    valuetype = type(value)
                    valuetyp = type(value.typ)
                    typ = to_dotted_name(valuetyp)
                    containertype = None
                    targetsheet = None

                    # If the outer type is not a container and it's not
                    # just a generic SchemaNode, we use the outer type
                    # as "valuetype" since it provides most specific
                    # information (e.g. "adhocracy.schema.Identifier"
                    # instead of just "String")
                    if valuetype is not SchemaNode:
                        typ = to_dotted_name(valuetype)

                    if issubclass(valuetype,
                                  AbstractReferenceIterableSchemaNode):
                        # Workaround for AbstractPathIterable:
                        # it's a list/set of AbsolutePath's
                        empty_appstruct = valuetyp().create_empty_appstruct()
                        containertype = empty_appstruct.__class__.__name__
                        typ = to_dotted_name(AbsolutePath)
                        # set targetsheet
                        reftype = self.resolv.maybe_resolve(value.reftype)
                        target_isheet = reftype.getTaggedValue('target_isheet')
                        targetsheet = to_dotted_name(target_isheet)

                    typ_stripped = strip_optional_prefix(typ, 'colander.')

                    fielddesc = {
                        'name': fieldname,
                        'valuetype': typ_stripped,
                        'createmandatory': createmandatory,
                        'readonly': self._sheet_field_readable(
                            sheet_name, fieldname, readonly)
                    }
                    if containertype is not None:
                        fielddesc['containertype'] = containertype
                    if targetsheet is not None:
                        fielddesc['targetsheet'] = targetsheet

                    fields.append(fielddesc)

            # For now, each sheet definition only contains a 'fields' attribute
            # listing the defined fields
            sheet_map[sheet_name] = {'fields': fields}

        return sheet_map

    def _sheet_metadata(self, isheets):
        """Get dictionary with metadata about sheets.

        Expects an iterable of ISheet interface classes.

        Returns a mapping from sheet identifiers (dotted names) to metadata
        describing the sheet.

        """
        sheet_metadata = {}

        for isheet in isheets:
            if isheet.isOrExtends(ISheet):
                metadata = get_all_taggedvalues(isheet)
            sheet_metadata[isheet.__identifier__] = metadata

        return sheet_metadata

    @view_config(request_method='GET')
    def get(self):
        """Return the API specification of this installation as JSON."""
        # Collect info about all resources
        resource_types = self.registry.resource_types()
        resource_map, sheet_set = self._describe_resources(resource_types)

        # Collect info about all sheets referenced by any of the resources
        sheet_metadata = self._sheet_metadata(sheet_set)
        sheet_map = self._describe_sheets(sheet_metadata)

        struct = {
            'resources':
            resource_map,
            'sheets':
            sheet_map
        }
        return struct


def includeme(config):  # pragma: no cover
    """Run Pyramid configuration."""
    pass
