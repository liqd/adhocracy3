"""Cornice colander schemas und validators to validate request data."""
import colander

from adhocracy.schema import AbsolutePath
from adhocracy.schema import Password


class ResourceResponseSchema(colander.Schema):

    """Data structure for responses of Resource requests."""

    content_type = colander.SchemaNode(colander.String(), default='')

    path = AbsolutePath(default='')


class ItemResponseSchema(ResourceResponseSchema):

    """Data structure for responses of IItem requests."""

    first_version_path = AbsolutePath(default='')


class GETResourceResponseSchema(ResourceResponseSchema):

    """Data structure for Resource GET requests."""

    data = colander.SchemaNode(colander.Mapping(unknown='preserve'),
                               default={})


class GETItemResponseSchema(GETResourceResponseSchema):

    """Data structure for responses of IItem requests."""

    first_version_path = AbsolutePath(default='')


class PUTResourceRequestSchema(colander.Schema):

    """Data structure for Resource PUT requests."""

    data = colander.SchemaNode(colander.Mapping(unknown='preserve'),
                               default={})


class POSTResourceRequestSchema(PUTResourceRequestSchema):

    """Data structure for Resource POST requests."""

    content_type = colander.SchemaNode(colander.String(), default='')


class AbsolutePaths(colander.SequenceSchema):

    """List of resource paths."""

    path = AbsolutePath()


class POSTItemRequestSchema(POSTResourceRequestSchema):

    """Data structure for Item and ItemVersion POST requests."""

    root_versions = AbsolutePaths(missing=[])


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

    """"""

    name = colander.SchemaNode(colander.String(),
                               missing=colander.required)
    password = Password(missing=colander.required)


class OPTIONResourceResponseSchema(colander.Schema):

    """Overview of all request/response data structures."""

    GET = GETLocationMapping()
    PUT = PUTLocationMapping()
    POST = POSTLocationMapping()
    HEAD = colander.SchemaNode(colander.Mapping(), default={})
    OPTION = colander.SchemaNode(colander.Mapping(), default={})
