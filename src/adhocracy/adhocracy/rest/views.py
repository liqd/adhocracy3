"""Rest API views."""
from adhocracy.interfaces import IResource
from adhocracy.interfaces import IItem
from adhocracy.interfaces import IItemVersion
from adhocracy.interfaces import ISimple
from adhocracy.interfaces import IPool
from adhocracy.rest.schemas import ResourceResponseSchema
from adhocracy.rest.schemas import ItemResponseSchema
from adhocracy.rest.schemas import POSTResourceRequestSchema
from adhocracy.rest.schemas import PUTResourceRequestSchema
from adhocracy.rest.schemas import GETResourceResponseSchema
from adhocracy.rest.schemas import GETItemResponseSchema
from adhocracy.rest.schemas import OPTIONResourceResponseSchema
from adhocracy.utils import get_resource_interface
from adhocracy.utils import strip_optional_prefix
from adhocracy.utils import to_dotted_name
from copy import deepcopy
from cornice.util import json_error
from cornice.schemas import validate_colander_schema
from cornice.schemas import CorniceSchema
from pyramid.view import view_config
from pyramid.view import view_defaults
from pyramid.traversal import resource_path
from substanced.interfaces import IRoot
from substanced.schema import IdSet

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
    """Validate propertysheet data for put requests."""
    type_ = request.validated.get('content_type', '')
    dummy = object()
    sheets = {}
    if type_ in request.registry.content.resource_types():
        dummy = request.registry.content.create(
            type_, context, add_to_context=False, run_after_creation=False)
        dummy.__parent__ = context
        sheets = request.registry.content.resource_sheets(
            dummy, request, onlycreatable=True)
    validate_sheet_cstructs(dummy, request, sheets)


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
            schema = CorniceSchema.from_colander(schema)
            validate_colander_schema(schema, request)
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

    @view_config(request_method='POST')
    def post(self):
        """HTTP POST. Return dictionary with PATH of new resource."""
        #create resource
        resource_type = self.request.validated['content_type']
        appstructs = self.request.validated.get('data', {})
        resource = self.registry.create(resource_type, self.context,
                                        appstructs=appstructs)
        # response
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


@view_defaults(
    renderer='simplejson',
    context=IRoot,
    name='meta_api'
)
class MetaApiView(RESTView):

    """Access to metadata about the API specification of this installation.

    Returns a JSON document describing the existing resources and sheets.

    """

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
            prop_map['sheets'] = sheets
            sheet_set.update(sheets)

            # Main element type if this is a pool or item
            if 'item_type' in metadata:
                main_element_type = to_dotted_name(metadata['item_type'])
                prop_map['main_element_type'] = main_element_type
            else:
                main_element_type = None

            # Other addable element types
            if 'addable_content_interfaces' in metadata:
                extra_element_types = metadata['addable_content_interfaces']
                extra_element_names = []

                for typ in extra_element_types:
                    dotted_name = to_dotted_name(typ)
                    # Skip main element type
                    if not dotted_name == main_element_type:
                        extra_element_names.append(dotted_name)

                prop_map['extra_element_types'] = extra_element_names
            resource_map[name] = prop_map
        return resource_map, sheet_set

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
            # definition, since this might change in the future
            createmandatory = metadata['createmandatory']
            readonly = metadata['readonly']
            fields = []

            # Create field definitions
            for key, value in metadata.items():
                fieldname = strip_optional_prefix(key, 'field:')

                # Only process 'field:...' definitions
                if fieldname != key:
                    valuetype = type(value.typ)

                    # FIXME: Add additional listtypes such as "list" as the
                    # need arised
                    if issubclass(valuetype, IdSet):
                        listtype = 'set'
                    else:
                        listtype = 'single'

                    typ = to_dotted_name(valuetype)
                    typ = strip_optional_prefix(typ, 'colander.')

                    # Workaround for PathSet: it's actally a set of
                    # AbsolutePath's
                    if typ == 'adhocracy.schema.PathSet':
                        typ = 'adhocracy.schema.AbsolutePath'

                    fielddesc = {
                        'name': fieldname,
                        'valuetype': typ,
                        'listtype': listtype,
                        'createmandatory': createmandatory,
                        'readonly': readonly,
                    }
                    fields.append(fielddesc)

            # For now, each sheet definition only contains a 'fields' attribute
            # listing the defined fields
            sheet_map[sheet_name] = {'fields': fields}

        return sheet_map

    @view_config(request_method='GET')
    def get(self):
        """Return the API specification of this installation as JSON."""
        # Collect info about all resources
        resource_types = self.registry.resource_types()
        resource_map, sheet_set = self._describe_resources(resource_types)

        # Collect info about all sheets referenced by any of the resources
        sheet_metadata = self.registry.sheet_metadata(sheet_set)
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
