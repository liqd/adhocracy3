from adhocracy.properties.interfaces import IName
from adhocracy.resources.interfaces import (
    IResource,
    IVersionableFubel,
)
from adhocracy.rest.schemas import (
    ResourceResponseSchema,
    PUTResourceRequestSchema,
    POSTResourceRequestSchema,
    GETResourceResponseSchema,
    OPTIONResourceResponseSchema,
)
from cornice.util import json_error
from cornice.schemas import (
    validate_colander_schema,
    CorniceSchema,
)
from pyramid.view import (
    view_config,
    view_defaults,
)
from pyramid.traversal import resource_path
from substanced.folder import FolderKeyError


def validate_request_with_cornice_schema(schema, request):
        """Validate request data with colander schema.
           Add errors to request.errors
           Add validated data to request.validated
        """
        schema = CorniceSchema.from_colander(schema)
        validate_colander_schema(schema, request)


def validate_put_propertysheet_names(context, request):
    sheets = request.registry.content.resource_propertysheets(
        context, request, check_permission_edit=True)
    put_sheets = request.validated.get("data", {})
    wrong_sheets = put_sheets.keys() - sheets.keys()
    if wrong_sheets:
        error = 'The following propertysheets are mispelled or you do not '\
                'have the edit permission: {names}'.format(names=wrong_sheets)
        request.errors.add('body', 'data', error)


def validate_post_propertysheet_names_addables(context, request):
    addables = request.registry.content.resource_addable_types(context)
    content_type = request.validated.get("content_type", "")
    if content_type not in addables:
        error = 'The following resource type is not '\
                'addable: {iresource} '.format(iresource=content_type)
        request.errors.add('body', 'content_type', error)
    else:
        sheets = addables[content_type]
        post_sheets = request.validated.get("data", {})
        wrong_sheets = set(post_sheets.keys()) - sheets
        if wrong_sheets:
            error = 'The following propertysheets are not allowed for this '\
                    'resource type or mispelled: {names}'.format(names=
                                                                 wrong_sheets)
            request.errors.add('body', 'data', error)
        missing_sheets = sheets - set(post_sheets.keys())
        if missing_sheets:
            error = 'The following propertysheets are required to create this'\
                    ' resource: {names}'.format(names=missing_sheets)
            request.errors.add('body', 'data', error)


@view_defaults(
    renderer='simplejson',
    context=IResource
)
class ResourceView(object):
    """Default view for adhocracy resources."""

    validation_map = {'GET': (None, []),
                      'OPTION': (None, []),
                      'PUT': (PUTResourceRequestSchema,
                              [validate_put_propertysheet_names]),
                      'POST': (POSTResourceRequestSchema,
                               [validate_post_propertysheet_names_addables]),
                      }
    reserved_names = []

    def __init__(self, context, request):
        self.context = context
        self.request = request
        registry = request.registry.content
        self.registry = registry
        self.addables = registry.resource_addable_types(context)
        self.sheets_all = registry.resource_propertysheets(context, request)
        self.sheets_view = registry.resource_propertysheets(
            context, request, check_permission_view=True)
        self.sheets_edit = registry.resource_propertysheets(
            context, request, check_permission_edit=True)

    def validate_request_data(self, method):
        """Validates request data.

        Raise 400 error if request.errors is not empty after validation.
        """
        schema = self.validation_map[method][0]
        validators = self.validation_map[method][1]
        if schema:
            validate_request_with_cornice_schema(schema, self.request)
        for val in validators:
            val(self.context, self.request)
        if self.request.errors:
            self.request.validated = {}
            raise json_error(self.request.errors)

    @view_config(request_method='OPTIONS')
    def options(self):
        cstruct = OPTIONResourceResponseSchema().serialize()
        for sheet in self.sheets_edit:
            cstruct["PUT"]["request_body"]["data"][sheet] = {}
        for sheet in self.sheets_view:
            cstruct["GET"]["response_body"]["data"][sheet] = {}
        for type, sheets in self.addables.items():
            sheets = dict([(sheet, {}) for sheet in sheets])
            post_data = {"content_type": type, "data": sheets}
            cstruct["POST"]["request_body"].append(post_data)
        return cstruct

    @view_config(request_method='GET')
    def get(self):
        self.validate_request_data('GET')
        struct = {"data": {}}
        for sheet in self.sheets_view.values():
            key = sheet.iface.__identifier__
            struct["data"][key] = sheet.get_cstruct()
        struct["path"] = resource_path(self.context)
        struct["content_type"] = self.registry.typeof(self.context)
        return GETResourceResponseSchema().serialize(struct)

    @view_config(request_method='PUT')
    def put(self):
        self.validate_request_data('PUT')
        for name, cstruct in self.request.validated["data"].items():
            self.sheets_edit[name].set_cstruct(cstruct)
        struct = {}
        struct["path"] = resource_path(self.context)
        struct["content_type"] = self.registry.typeof(self.context)
        return ResourceResponseSchema().serialize(struct)

    @view_config(request_method='POST')
    def post(self):
        #validate request data
        self.validate_request_data('POST')
        #create resource
        type = self.request.validated["content_type"]
        resource = self.registry.create(type)
        # add to parent
        name = self.request.validated["data"].get(IName.__identifier__, {})\
            .get("name", "")
        if IVersionableFubel.providedBy(resource):
            name = self.context.next_name()
        try:
            name = self.context.check_name(name, self.reserved_names)
        except (FolderKeyError, ValueError):
                name += "_" + self.context.next_name()
        self.context.add(name, resource, send_events=False)
        # store propertysheets
        for name, cstruct in self.request.validated["data"].items():
            self.sheets_edit[name].set_cstruct(cstruct)
        #FIXME use substanced event system
        # response
        struct = {}
        struct["path"] = resource_path(resource)
        struct["content_type"] = self.registry.typeof(self.context)
        return ResourceResponseSchema().serialize(struct)


def includeme(config):  # pragma: no cover
    pass
