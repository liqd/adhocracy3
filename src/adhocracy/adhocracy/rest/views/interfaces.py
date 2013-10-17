import colander


class ContentGETSchema(colander.Schema):

    content_type = colander.SchemaNode(colander.String(), default="")

    path = colander.SchemaNode(colander.String(), default="")

    data = colander.SchemaNode(colander.Mapping(), default={})


class ContentPOSTSchema(colander.Schema):

    content_type = colander.SchemaNode(colander.String())

    data = colander.SchemaNode(colander.Mapping(unknown="preserve"))


class ContentPUTSchema(colander.Schema):

    content_type = colander.SchemaNode(colander.String())

    data = colander.SchemaNode(colander.Mapping(unknown="preserve"))


#class ContentOPTIONSSchema(colander.Schema):

    #GET = colander.SchemaNode(colander.List(), default=[],
                              #required=False)

    #POST = colander.SchemaNode(colander.List(), default=[],
                               #required=False)

    #PUT = colander.SchemaNode(colander.List(), default=[],
                              #required=False)

    #POST = colander.SchemaNode(colander.List(), default=[],
                               #required=False)
