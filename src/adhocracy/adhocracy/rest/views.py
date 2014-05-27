"""Rest API views."""
from copy import deepcopy
import functools
import logging

from colander import SchemaNode
from cornice.util import json_error
from cornice.schemas import validate_colander_schema
from cornice.schemas import CorniceSchema
from pyramid.view import view_config
from pyramid.view import view_defaults
from pyramid.traversal import resource_path
from pyramid.traversal import find_resource
from substanced.interfaces import IRoot

from adhocracy.interfaces import IResource
from adhocracy.interfaces import IItem
from adhocracy.interfaces import IItemVersion
from adhocracy.interfaces import ISimple
from adhocracy.interfaces import IPool
from adhocracy.rest.schemas import ResourceResponseSchema
from adhocracy.rest.schemas import ItemResponseSchema
from adhocracy.rest.schemas import POSTItemRequestSchema
from adhocracy.rest.schemas import POSTResourceRequestSchema
from adhocracy.rest.schemas import PUTResourceRequestSchema
from adhocracy.rest.schemas import GETResourceResponseSchema
from adhocracy.rest.schemas import GETItemResponseSchema
from adhocracy.rest.schemas import OPTIONResourceResponseSchema
from adhocracy.schema import AbsolutePath
from adhocracy.schema import AbstractReferenceIterable
from adhocracy.utils import get_iresource
from adhocracy.utils import strip_optional_prefix
from adhocracy.utils import to_dotted_name


logger = logging.getLogger(__name__)


def validate_sheet_cstructs(context, request, sheets):
    """Validate sheet data."""
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
    """Validate sheet data for put requests."""
    sheets = request.registry.content.resource_sheets(
        context, request, onlyeditable=True)
    validate_sheet_cstructs(context, request, sheets)


def validate_post_sheet_cstructs(context, request):
    """Validate sheet data for post requests."""
    type_ = request.validated.get('content_type', '')
    dummy = object()
    sheets = {}
    if type_ in request.registry.content.resources_metadata():
        dummy = request.registry.content.create(
            type_, run_after_creation=False)
        dummy.__parent__ = context
        sheets = request.registry.content.resource_sheets(
            dummy, request, onlycreatable=True)
    validate_sheet_cstructs(dummy, request, sheets)


def validate_post_root_versions(context, request):
    """Check and transform the 'root_version' paths to resources."""
    root_paths = request.validated.get('root_versions', [])
    root_resources = []
    for path in root_paths:
        path_tuple = tuple(str(path).split('/'))
        res = None
        try:
            res = find_resource(context, path_tuple)
        except KeyError:
            error = 'This resource path does not exist: {p}'.format(p=path)
            request.errors.add('body", "root_versions', error)
            continue
        if not IItemVersion.providedBy(res):
            error = 'This resource is not a valid ' \
                    'root version: {p}'.format(p=path)
            request.errors.add('body', 'root_versions', error)
            continue
        root_resources.append(res)

    request.validated['root_versions'] = root_resources


def validate_put_sheet_names(context, request):
    """Validate sheet names for put requests. Return None."""
    sheets = request.registry.content.resource_sheets(
        context, request, onlyeditable=True)
    puted = request.validated.get('data', {}).keys()
    wrong_sheets = set(puted) - set(sheets)
    if wrong_sheets:
        error = 'The following sheets are mispelled or you do not ' \
                'have the edit permission: {names}'.format(names=wrong_sheets)
        request.errors.add('body', 'data', error)


def validate_post_sheet_names_and_resource_type(context, request):
    """Validate addable sheet names for post requests."""
    addables = request.registry.content.resource_addables(context, request)
    content_type = request.validated.get('content_type', '')
    if content_type not in addables:
        error = 'The following resource type is not ' \
                'addable: {iresource} '.format(iresource=content_type)
        request.errors.add('body', 'content_type', error)
    else:
        optional = addables[content_type]['sheets_optional']
        mandatory = addables[content_type]['sheets_mandatory']
        posted = request.validated.get('data', {}).keys()
        wrong_sheets = set(posted) - set(optional + mandatory)
        if wrong_sheets:
            error = 'The following sheets are not allowed for this resource '\
                    'type or misspelled: {names}'.format(names=wrong_sheets)
            request.errors.add('body', 'data', error)
        missing_sheets = set(mandatory) - set(posted)
        if missing_sheets:
            error = 'The following sheets are mandatory to create '\
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
        # FIXME workaround for Cornice not finding a request body
        if (not hasattr(request, 'deserializer') and
                hasattr(request, 'json')):
            request.deserializer = lambda req: req.json
        validate_colander_schema(schemac, request)
    for val in extra_validators:
        val(context, request)
    if request.errors:
        request.validated = {}
        _log_request_errors(request)
        raise json_error(request.errors)


def _log_request_errors(request):
    logger.warn('Found %i validation errors in request: <%s>',
                len(request.errors), request.body)
    for error in request.errors:
        logger.warn('  %s', error)


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


class RESTView:

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
        struct = {'data': {}}
        for sheet in sheets_view.values():
            key = sheet.meta.isheet.__identifier__
            struct['data'][key] = sheet.get_cstruct()
        struct['path'] = resource_path(self.context)
        iresource = get_iresource(self.context)
        struct['content_type'] = iresource.__identifier__
        return GETResourceResponseSchema().serialize(struct)


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
        return super().options()  # pragma: no cover

    @view_config(request_method='GET')
    def get(self):
        """Handle GET requests. Return dict."""
        return super().get()  # pragma: no cover

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
        iresource = get_iresource(self.context)
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
        return super().options()  # pragma: no cover

    @view_config(request_method='GET')
    def get(self):
        """Handle GET requests. Return dict."""
        return super().get()  # pragma: no cover

    @view_config(request_method='PUT')
    def put(self):
        """Handle HTTP PUT. Return dict with PATH of modified resource."""
        return super().put()  # pragma: no cover



    def build_post_response(self, resource):
        """Helper method that builds a response for a POST request.

        Returns:
            the serialized response

        """
        struct = {}
        struct['path'] = resource_path(resource)
        iresource = get_iresource(resource)
        struct['content_type'] = iresource.__identifier__
        if IItem.providedBy(resource):
            struct.update(self._get_dict_with_first_version_path(resource))
            return ItemResponseSchema().serialize(struct)
        else:
            return ResourceResponseSchema().serialize(struct)

    def _get_dict_with_first_version_path(self, item: IItem) -> dict:
        first_path = ''
        for child in item.values():
            if IItemVersion.providedBy(child):
                first_path = resource_path(child)
        return {'first_version_path': first_path}

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

    @view_config(request_method='GET')
    def get(self):
        struct = super().get()
        struct.update(self._get_dict_with_first_version_path(self.context))
        return GETItemResponseSchema().serialize(struct)

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

    def _describe_resources(self, resource_types):
        """Build a description of the resources registered in the system.

        Args:
          resources_metadata (list): resource metadata

        Returns:
          resource_map (dict): a dict (suitable for JSON serialization) that
                               describes all the resources registered in the
                               system.

        """
        resource_map = {}

        for name, value in resource_types.items():
            prop_map = {}
            metadata = value['metadata']

            # List of sheets
            sheets = []
            sheets.extend(metadata.basic_sheets)
            sheets.extend(metadata.extended_sheets)
            prop_map['sheets'] = [to_dotted_name(s) for s in sheets]

            # Main element type if this is a pool or item
            if metadata.item_type:
                prop_map['item_type'] = to_dotted_name(metadata.item_type)

            # Other addable element types
            if metadata.element_types:
                element_names = []
                for typ in metadata.element_types:
                    element_names.append(to_dotted_name(typ))
                prop_map['element_types'] = element_names

            resource_map[name] = prop_map
        return resource_map

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
            createmandatory = metadata.createmandatory
            readonly = metadata.readonly
            fields = []

            # Create field definitions
            for node in metadata.schema_class().children:

                fieldname = node.name
                valuetype = type(node)
                valuetyp = type(node.typ)
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
                              AbstractReferenceIterable):
                    # Workaround for AbstractIterableOfPaths:
                    # it's a list/set of AbsolutePath's
                    empty_appstruct = valuetyp().create_empty_appstruct()
                    containertype = empty_appstruct.__class__.__name__
                    typ = to_dotted_name(AbsolutePath)
                    # set targetsheet
                    reftype = node.reftype
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

    @view_config(request_method='GET')
    def get(self):
        """Return the API specification of this installation as JSON."""
        # Collect info about all resources
        resource_types = self.registry.resources_metadata()
        resource_map = self._describe_resources(resource_types)

        # Collect info about all sheets referenced by any of the resources
        sheet_metadata = self.registry.sheets_metadata()
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
