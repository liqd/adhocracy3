"""Cornice colander schemas und validators to validate request data."""
from adhocracy.schema import AbsolutePath

import colander


class ResourceResponseSchema(colander.Schema):

    """Data structure for responses of Resource requests."""

    content_type = colander.SchemaNode(colander.String(), default="")

    path = AbsolutePath(default="")


class GETResourceResponseSchema(ResourceResponseSchema):

    """Data structure for Resource GET requests."""

    data = colander.SchemaNode(colander.Mapping(unknown="preserve"),
                               default={})


class PUTResourceRequestSchema(colander.Schema):

    """Data structure for Resource PUT requests."""

    data = colander.SchemaNode(colander.Mapping(unknown="preserve"),
                               default={})


class POSTResourceRequestSchema(PUTResourceRequestSchema):

    """Data structure for Resource POST requests."""

    content_type = colander.SchemaNode(colander.String(), default="")


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


class OPTIONResourceResponseSchema(colander.Schema):

    """Overview of all request/response data structures."""

    GET = GETLocationMapping()
    PUT = PUTLocationMapping()
    POST = POSTLocationMapping()
    HEAD = colander.SchemaNode(colander.Mapping(), default={})
    OPTION = colander.SchemaNode(colander.Mapping(), default={})
