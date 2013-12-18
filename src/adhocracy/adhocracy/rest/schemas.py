"""Cornice  https://github.com/mozilla-services/cornice
colander schemas und validators to validate request data."""
from adhocracy.schema import AbsolutePath

import colander


class ResourceResponseSchema(colander.Schema):

    content_type = colander.SchemaNode(colander.String(), default="")

    path = AbsolutePath(default="")


class GETResourceResponseSchema(ResourceResponseSchema):

    data = colander.SchemaNode(colander.Mapping(unknown="preserve"),
                               default={})


class PUTResourceRequestSchema(colander.Schema):

    data = colander.SchemaNode(colander.Mapping(unknown="preserve"),
                               default={})


class POSTResourceRequestSchema(PUTResourceRequestSchema):

    content_type = colander.SchemaNode(colander.String(), default="")


class POSTResourceRequestSchemaList(colander.List):

    request_body = POSTResourceRequestSchema()


class GETLocationMapping(colander.Schema):

    request_querystring = colander.SchemaNode(colander.Mapping(), default={})
    request_body = colander.SchemaNode(colander.Mapping(), default={})
    response_body = GETResourceResponseSchema()


class PUTLocationMapping(colander.Schema):

    request_body = PUTResourceRequestSchema()
    response_body = ResourceResponseSchema()


class POSTLocationMapping(colander.Schema):

    request_body = colander.SchemaNode(POSTResourceRequestSchemaList(),
                                       default=[])
    response_body = ResourceResponseSchema()


class OPTIONResourceResponseSchema(colander.Schema):

    GET = GETLocationMapping()
    PUT = PUTLocationMapping()
    POST = POSTLocationMapping()
    HEAD = colander.SchemaNode(colander.Mapping(), default={})
    OPTION = colander.SchemaNode(colander.Mapping(), default={})
