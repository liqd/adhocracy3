"""Rest API views."""
from copy import deepcopy
from logging import getLogger
import functools

from colander import SchemaNode
from colander import MappingSchema
from cornice.util import json_error
from cornice.util import to_list
from cornice.schemas import validate_colander_schema
from substanced.interfaces import IUserLocator
from pyramid.httpexceptions import HTTPMethodNotAllowed
from pyramid.request import Request
from pyramid.view import view_config
from pyramid.view import view_defaults
from pyramid.security import remember
from pyramid.traversal import resource_path
from pyramid.traversal import find_resource

from adhocracy.interfaces import IResource
from adhocracy.interfaces import IItem
from adhocracy.interfaces import IItemVersion
from adhocracy.interfaces import ISimple
from adhocracy.interfaces import IPool
from adhocracy.interfaces import ILocation
from adhocracy.rest.schemas import ResourceResponseSchema
from adhocracy.rest.schemas import ItemResponseSchema
from adhocracy.rest.schemas import POSTItemRequestSchema
from adhocracy.rest.schemas import POSTLoginEmailRequestSchema
from adhocracy.rest.schemas import POSTLoginUsernameRequestSchema
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
from adhocracy.utils import get_sheet
from adhocracy.utils import get_user
from adhocracy.resources.root import IRootPool
from adhocracy.sheets.user import IPasswordAuthentication


logger = getLogger(__name__)


def validate_post_root_versions(context, request: Request):
    """Check and transform the 'root_version' paths to resources."""
    # FIXME: make this a colander validator and move to schema.py
    # use the catalog to find IItemversions
    root_paths = request.validated.get('root_versions', [])
    root_resources = []
    for path in root_paths:
        path_tuple = tuple(str(path).split('/'))
        res = None
        try:
            res = find_resource(context, path_tuple)
        except KeyError:
            error = 'This resource path does not exist: {p}'.format(p=path)
            request.errors.add('body', 'root_versions', error)
            continue
        if not IItemVersion.providedBy(res):
            error = 'This resource is not a valid ' \
                    'root version: {p}'.format(p=path)
            request.errors.add('body', 'root_versions', error)
            continue
        root_resources.append(res)

    request.validated['root_versions'] = root_resources


def validate_request_data(context: ILocation, request: Request,
                          schema=MappingSchema(), extra_validators=[]):
    """ Validate request data.

    :param context: passed to validator functions
    :param request: passed to validator functions
    :param schema: Schema to validate the request data with
        :func:`cornice.schemas.validate_colander_schema`.
        `None` value is allowed.
    :extra_validators: additional validator functions. The have to accept
        the arguments `context` and `request`.

    :raises _JSONError: HTTP 400 for bad request data.

    """
    parent = context if request.method == 'POST' else context.__parent__
    schema_with_binding = schema.bind(context=context, request=request,
                                      parent_pool=parent)
    schema_cornice = _CorniceSchemaAdapter(schema_with_binding)
    validate_colander_schema(schema_cornice, request)
    if request.errors:
        extra_validators = []
    for val in extra_validators:
        val(context, request)
    if request.errors:
        request.validated = {}
        _log_request_errors(request)
        raise json_error(request.errors)


class _CorniceSchemaAdapter:

    def __init__(self, colander_schema):
        self._c_schema = colander_schema

    def get_attributes(self, location=('body', 'header', 'querystring'),
                       required=(True, False), request=None):
        def _filter(attr):
            if not hasattr(attr, 'location'):
                valid_location = 'body' in location
            else:
                valid_location = attr.location in to_list(location)
            return valid_location and attr.required in to_list(required)

        attributes = self._c_schema.children
        return list(filter(_filter, attributes))


def _log_request_errors(request: Request):
    logger.warning('Found %i validation errors in request: <%s>',
                   len(request.errors), request.body)
    for error in request.errors:
        logger.warning('  %s', error)


def validate_request_data_decorator():
    """Validate request data for every http method of your RESTView class.

    Run :func:`validate_request_data* with schema and additional validators
    from the class attribute `validation_<http method>`.

    :returns: decorated method

    """
    def _dec(f):
        @functools.wraps(f)
        def wrapper(context, request):
            view_class = f.__original_view__
            schema_class, validators = _get_schema_and_validators(view_class,
                                                                  request)
            validate_request_data(context, request,
                                  schema=schema_class(),
                                  extra_validators=validators)
            return f(context, request)

        return wrapper

    return _dec


def _get_schema_and_validators(view_class, request: Request) -> tuple:
    http_method = request.method.upper()
    validation_attr = 'validation_' + http_method
    schema, validators = getattr(view_class, validation_attr, (None, []))
    return schema or MappingSchema, validators


class RESTView:

    """Class stub with request data validation support.

    Subclasses must implement the wanted request methods
    and configure the pyramid view::

        @view_defaults(
            renderer='simplejson',
            context=IResource,
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

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.registry = request.registry.content
        schema_class, validators = _get_schema_and_validators(self, request)
        validate_request_data(context, request,
                              schema=schema_class(),
                              extra_validators=validators)

    def options(self) -> dict:
        raise HTTPMethodNotAllowed()

    def get(self) -> dict:
        raise HTTPMethodNotAllowed()

    def put(self) -> dict:
        raise HTTPMethodNotAllowed()

    def post(self) -> dict:
        raise HTTPMethodNotAllowed()

    def delete(self) -> dict:
        raise HTTPMethodNotAllowed()


@view_defaults(
    renderer='simplejson',
    context=IResource,
)
class ResourceRESTView(RESTView):

    """Default view for Resources, implements get and options."""

    @view_config(request_method='OPTIONS')
    def options(self) -> dict:
        """Get possible request/response data structures and http methods."""
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
    def get(self) -> dict:
        """Get resource data."""
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
)
class SimpleRESTView(ResourceRESTView):

    """View for simples (non versionable), implements get, options and put."""

    validation_PUT = (PUTResourceRequestSchema, [])

    @view_config(request_method='PUT',
                 content_type='application/json')
    def put(self) -> dict:
        """Edit resource and get response data."""
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

    validation_POST = (POSTResourceRequestSchema, [])

    def build_post_response(self, resource) -> dict:
        """Build response data structure for a POST request. """
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

    @view_config(request_method='POST',
                 content_type='application/json')
    def post(self) -> dict:
        """Create new resource and get response data."""
        resource_type = self.request.validated['content_type']
        appstructs = self.request.validated.get('data', {})
        creator = get_user(self.request)
        resource = self.registry.create(resource_type, self.context,
                                        creator=creator,
                                        appstructs=appstructs)
        return self.build_post_response(resource)


@view_defaults(
    renderer='simplejson',
    context=IItem,
)
class ItemRESTView(PoolRESTView):

    """View for Items and ItemVersions, overwrites GET and  POST handling."""

    validation_POST = (POSTItemRequestSchema, [validate_post_root_versions])

    @view_config(request_method='GET')
    def get(self) -> dict:
        """Get resource data."""
        struct = super().get()
        struct.update(self._get_dict_with_first_version_path(self.context))
        return GETItemResponseSchema().serialize(struct)

    @view_config(request_method='POST',
                 content_type='application/json')
    def post(self):
        """Create new resource and get response data."""
        resource_type = self.request.validated['content_type']
        appstructs = self.request.validated.get('data', {})
        creator = get_user(self.request)
        root_versions = self.request.validated.get('root_versions', [])
        resource = self.registry.create(resource_type, self.context,
                                        appstructs=appstructs,
                                        creator=creator,
                                        root_versions=root_versions)
        return self.build_post_response(resource)


@view_defaults(
    renderer='simplejson',
    context=IRootPool,
    name='meta_api'
)
class MetaApiView(RESTView):

    """Access to metadata about the API specification of this installation.

    Returns a JSON document describing the existing resources and sheets.
    """

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

        for name, metadata in resource_types.items():
            prop_map = {}

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
            # readable and create_mandatory flags are currently defined for
            # the whole sheet, but we copy them as attributes into each field
            # definition, since this might change in the future.
            # (The _sheet_field_readable method already allows overwriting the
            # readable flag on a field-by-field basis, but it's somewhat
            # ad-hoc.)
            fields = []

            # Create field definitions
            for node in metadata.schema_class().children:

                fieldname = node.name
                valuetype = type(node)
                valuetyp = type(node.typ)
                typ = to_dotted_name(valuetyp)
                containertype = None
                targetsheet = None
                readonly = getattr(node, 'readonly', False)

                # If the outer type is not a container and it's not
                # just a generic SchemaNode, we use the outer type
                # as "valuetype" since it provides most specific
                # information (e.g. "adhocracy.schema.Identifier"
                # instead of just "SingleLIne")
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
                    'create_mandatory':
                        False if readonly else metadata.create_mandatory,
                    'editable': False if readonly else metadata.editable,
                    'creatable': False if readonly else metadata.creatable,
                    'readable': metadata.readable,
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
    def get(self) -> dict:
        """Get the API specification of this installation as JSON."""
        # Collect info about all resources
        resource_types = self.registry.resources_metadata()
        resource_map = self._describe_resources(resource_types)

        # Collect info about all sheets referenced by any of the resources
        sheet_metadata = self.registry.sheets_metadata()
        sheet_map = self._describe_sheets(sheet_metadata)

        struct = {'resources': resource_map,
                  'sheets': sheet_map,
                  }
        return struct


def _add_no_such_user_or_wrong_password_error(request: Request):
    request.errors.add('body', 'password',
                       'User doesn\'t exist or password is wrong')


def validate_login_name(context, request: Request):
    """Validate the user name of a login request.

    If valid, the user object is added as 'user' to
    `request.validated`.
    """
    name = request.validated['name']
    locator = request.registry.getMultiAdapter((context, request),
                                               IUserLocator)
    user = locator.get_user_by_login(name)
    if user is None:
        _add_no_such_user_or_wrong_password_error(request)
    else:
        request.validated['user'] = user


def validate_login_email(context, request: Request):
    """Validate the email address of a login request.

    If valid, the user object is added as 'user' to
    `request.validated`.
    """
    email = request.validated['email']
    locator = request.registry.getMultiAdapter((context, request),
                                               IUserLocator)
    user = locator.get_user_by_email(email)
    if user is None:
        _add_no_such_user_or_wrong_password_error(request)
    else:
        request.validated['user'] = user


def validate_login_password(context, request: Request):
    """Validate the password of a login request.

    Requires the user object as `user` in `request.validated`.
    """
    user = request.validated.get('user', None)
    if user is None:
        return
    password_sheet = get_sheet(user, IPasswordAuthentication)
    password = request.validated['password']
    if not password_sheet.check_plaintext_password(password):
        _add_no_such_user_or_wrong_password_error(request)


@view_defaults(
    renderer='simplejson',
    context=IRootPool,
)
class LoginUsernameView(RESTView):

    """Log in a user via their name."""

    validation_POST = (POSTLoginUsernameRequestSchema,
                       [validate_login_name, validate_login_password])

    @view_config(name='login_username',
                 request_method='POST',
                 content_type='application/json')
    def post(self) -> dict:
        """Create new resource and get response data."""
        return _login_user(self.request)


def _login_user(request: Request) -> dict:
    """Log-in a user and return a response indicating success."""
    user = request.validated['user']
    user_path = resource_path(user)
    headers = remember(request, user_path)
    user_path = headers['X-User-Path']
    user_token = headers['X-User-Token']
    return {'status': 'success',
            'user_path': user_path,
            'user_token': user_token}


@view_defaults(
    renderer='simplejson',
    context=IRootPool,
)
class LoginEmailView(RESTView):

    """Log in a user via their email address."""

    validation_POST = (POSTLoginEmailRequestSchema,
                       [validate_login_email, validate_login_password])

    @view_config(name='login_email',
                 request_method='POST',
                 content_type='application/json')
    def post(self) -> dict:
        """Create new resource and get response data."""
        return _login_user(self.request)


def includeme(config):  # pragma: no cover
    """Register Views."""
    config.scan('.views')
