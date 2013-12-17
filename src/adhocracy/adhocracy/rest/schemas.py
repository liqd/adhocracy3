"""Cornice  https://github.com/mozilla-services/cornice
colander schemas und validators to validate request data."""
from adhocracy.schema import AbsolutePath

import colander


class ResourceResponseSchema(colander.Schema):

    content_type = colander.SchemaNode(colander.String())

    path = AbsolutePath()


class GETResourceResponseSchema(ResourceResponseSchema):

    data = colander.SchemaNode(colander.Mapping(unknown="preserve"),
                               default={})


class ResourceRequestSchema(colander.Schema):

    content_type = colander.SchemaNode(colander.String())

    data = colander.SchemaNode(colander.Mapping(unknown="preserve"))
