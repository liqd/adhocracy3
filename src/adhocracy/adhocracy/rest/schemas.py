"""Cornice colander schemas und validators to validate request data."""
import colander

from adhocracy.schema import AbsolutePath
from adhocracy.schema import AdhocracySchemaNode
from adhocracy.schema import Email
from adhocracy.schema import Interface
from adhocracy.schema import Password
from adhocracy.schema import Resource
from adhocracy.schema import Resources
from adhocracy.schema import SingleLine
from adhocracy.schema import ResourcePathSchema
from adhocracy.schema import ResourcePathAndContentSchema


class ResourceResponseSchema(ResourcePathSchema):

    """Data structure for responses of Resource requests."""


class ItemResponseSchema(ResourceResponseSchema):

    """Data structure for responses of IItem requests."""

    first_version_path = Resource()


class GETResourceResponseSchema(ResourcePathAndContentSchema):

    """Data structure for Resource GET requests."""


class GETItemResponseSchema(ResourcePathAndContentSchema):

    """Data structure for responses of IItem requests."""

    first_version_path = Resource()


def add_put_data_subschemas(node: colander.MappingSchema, kw: dict):
    """Add the resource sheet colander schemas that are 'editable'."""
    context = kw['context']
    request = kw['request']
    sheets = request.registry.content.resource_sheets(context, request,
                                                      onlyeditable=True)
    data = request.json_body.get('data', {})
    sheets_meta = request.registry.content.sheets_meta
    for name in [x for x in sheets if x in data]:
        subschema = sheets_meta[name].schema_class(name=name)
        node.add(subschema.bind(**kw))


class PUTResourceRequestSchema(colander.Schema):

    """Data structure for Resource PUT requests.

    The subschemas for the Resource Sheets
    """

    data = colander.SchemaNode(colander.Mapping(unknown='raise'),
                               after_bind=add_put_data_subschemas,
                               default={})


def add_post_data_subschemas(node: colander.MappingSchema, kw: dict):
    """Add the resource sheet colander schemas that are 'creatable'."""
    context = kw['context']
    request = kw['request']
    resource_type = request.json_body.get('content_type', None)
    data = request.json_body.get('data', {})
    addables = request.registry.content.resource_addables(context, request)
    resource_sheets = addables.get(resource_type, {'sheets_mandatory': [],
                                                   'sheets_optional': []})
    sheets_meta = request.registry.content.sheets_meta
    subschemas = []
    for name in [x for x in resource_sheets['sheets_mandatory'] if x in data]:
        schema = sheets_meta[name].schema_class(name=name)
        subschemas.append(schema)
    for name in [x for x in resource_sheets['sheets_optional'] if x in data]:
        schema = sheets_meta[name].schema_class(name=name, missing={})
        subschemas.append(schema)
    for schema in subschemas:
        node.add(schema.bind(**kw))


@colander.deferred
def deferred_validate_post_content_type(node, kw):
    """Validate the addable content type for post requests."""
    context = kw['context']
    request = kw['request']
    resource_addables = request.registry.content.resource_addables
    addable_content_types = resource_addables(context, request)
    return colander.OneOf(addable_content_types.keys())


class POSTResourceRequestSchema(PUTResourceRequestSchema):

    """Data structure for Resource POST requests."""

    content_type = SingleLine(validator=deferred_validate_post_content_type,
                              missing=colander.required)

    data = colander.SchemaNode(colander.Mapping(unknown='raise'),
                               after_bind=add_post_data_subschemas,
                               default={})


class AbsolutePaths(colander.SequenceSchema):

    """List of resource paths."""

    path = AbsolutePath()


class POSTItemRequestSchema(POSTResourceRequestSchema):

    """Data structure for Item and ItemVersion POST requests."""

    root_versions = Resources(missing=[])


class POSTResourceRequestSchemaList(colander.List):

    """Overview of POST request/response data structure."""

    request_body = POSTResourceRequestSchema()


class GETLocationMapping(colander.Schema):

    """Overview of GET request/response data structure."""

    request_querystring = colander.SchemaNode(colander.Mapping(), default={})
    request_body = colander.SchemaNode(colander.Mapping(), default={})
    response_body = GETResourceResponseSchema()


class PUTLocationMapping(colander.Schema):

    """Overview of PUT request/response data structure."""

    request_body = PUTResourceRequestSchema()
    response_body = ResourceResponseSchema()


class POSTLocationMapping(colander.Schema):

    """Overview of POST request/response data structure."""

    request_body = colander.SchemaNode(POSTResourceRequestSchemaList(),
                                       default=[])
    response_body = ResourceResponseSchema()


class POSTLoginUsernameRequestSchema(colander.Schema):

    """Schema for login requests via username and password."""

    name = colander.SchemaNode(colander.String(),
                               missing=colander.required)
    password = Password(missing=colander.required)


class POSTLoginEmailRequestSchema(colander.Schema):

    """Schema for login requests via email and password."""

    email = Email(missing=colander.required)
    password = Password(missing=colander.required)


class BatchHTTPMethod(colander.SchemaNode):

    """An HTTP method in a batch request."""

    schema_type = colander.String
    validator = colander.OneOf(['GET', 'POST', 'PUT', 'OPTION'])
    missing = colander.required


class BatchRequestPath(AdhocracySchemaNode):

    """A path in a batch request.

    Either a resource url or a preliminary resource path (a relative path
    preceded by '@') or an absolute path.

    Example values: '@item/v1', 'http://a.org/adhocracy/item/v1', '/item/v1/'
    """

    schema_type = colander.String
    default = ''
    missing = colander.required
    absolutpath = AbsolutePath.relative_regex
    preliminarypath = '[a-zA-Z0-9\_\-\.\/]+'
    validator = colander.All(colander.Regex('^' + colander.URL_REGEX + '|'
                                            + absolutpath + '|@'
                                            + preliminarypath + '$'),
                             colander.Length(min=1, max=200))


class POSTBatchRequestItem(colander.Schema):

    """A single item in a batch request, encoding a single request."""

    method = BatchHTTPMethod()
    path = BatchRequestPath()
    body = colander.SchemaNode(colander.Mapping(unknown='preserve'),
                               missing={})
    result_path = BatchRequestPath(missing='')
    result_first_version_path = BatchRequestPath(missing='')


class POSTBatchRequestSchema(colander.SequenceSchema):

    """Schema for batch requests (list of POSTBatchRequestItem's)."""

    items = POSTBatchRequestItem()


class PoolElementsForm(colander.SchemaNode):

    """The form of the elements attribute returned by the pool sheet."""

    schema_type = colander.String
    validator = colander.OneOf(['paths', 'content', 'omit'])
    missing = 'paths'


class PoolQueryDepth(colander.SchemaNode):

    """The nesting depth of descendants in a pool response.

    Either a positive number or the string 'all' to return descendants of
    arbitrary depth.
    """

    schema_type = colander.String
    validator = colander.Regex(r'^\d+|all$')
    missing = '1'


class GETPoolRequestSchema(colander.MappingSchema):

    """GET parameters accepted for pool queries."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Extra key/value pairs should be preserved when deserializing data
        self.typ.unknown = 'preserve'

    # FIXME For now we don't have a way to specify GET parameters that can
    # be repeated, e.g. 'sheet=Blah&sheet=Blub'. The querystring is converted
    # by Cornice into a MultiDict (http://docs.pylonsproject.org/projects
    # /pyramid/en/master/api/interfaces.html#pyramid.interfaces.IMultiDict),
    # which by default will only return the LAST value if a key is specified
    # several times. One possible workaround is to allow specifying multiple
    # values as a comma-separated list instead of repeated key=value pairs,
    # e.g. 'sheet=Blah,Blub'. This would require a custom Multiple SchemaNode
    # that wraps a SchemaType, e.g.
    # sheet = Multiple(Interface(), missing=None, sep=',')
    # Elements in this schema were multiple values should be allowed:
    # sheet, aggregateby, tag.

    content_type = colander.SchemaNode(Interface(), missing=colander.drop)
    sheet = colander.SchemaNode(Interface(), missing=colander.drop)
    depth = PoolQueryDepth(missing=colander.drop)
    elements = PoolElementsForm(missing=colander.drop)
    count = colander.SchemaNode(colander.Boolean(), missing=colander.drop)
    aggregateby = colander.SchemaNode(colander.String(), missing=colander.drop)


class OPTIONResourceResponseSchema(colander.Schema):

    """Overview of all request/response data structures."""

    GET = GETLocationMapping()
    PUT = PUTLocationMapping()
    POST = POSTLocationMapping()
    HEAD = colander.MappingSchema(default={})
    OPTION = colander.MappingSchema(default={})
