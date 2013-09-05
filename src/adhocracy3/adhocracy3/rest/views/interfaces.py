import colander


class MetaSchema(colander.MappingSchema):

    name = colander.SchemaNode(colander.String(), default=u"")

    path = colander.SchemaNode(colander.String(), default=u"")

    content_type = colander.SchemaNode(colander.String(), default=u"")

    content_type_name = colander.SchemaNode(colander.String(), default=u"")

    workflow_state = colander.SchemaNode(colander.String(), default=u"")

    creator = colander.SchemaNode(colander.String(), default=u"")

    creation_date = colander.SchemaNode(colander.String(), default=u"")


class MetaListSchema(colander.SequenceSchema):

    children = MetaSchema()


class ContentGETSchema(colander.Schema):

    content_type = colander.SchemaNode(colander.String(), default="")

    meta = MetaSchema()

    data = colander.SchemaNode(colander.Mapping(), default={})

    children = MetaListSchema(default=[])


class ContentPOSTSchema(colander.Schema):

    content_type = colander.SchemaNode(colander.String())

    data = colander.SchemaNode(colander.Mapping(unknown="preserve"))


class ContentPUTSchema(colander.Schema):

    content_type = colander.SchemaNode(colander.String())

    data = colander.SchemaNode(colander.Mapping())


#class ContentOPTIONSSchema(colander.Schema):

    #GET = colander.SchemaNode(colander.List(), default=[],
                              #required=False)

    #POST = colander.SchemaNode(colander.List(), default=[],
                               #required=False)

    #PUT = colander.SchemaNode(colander.List(), default=[],
                              #required=False)

    #POST = colander.SchemaNode(colander.List(), default=[],
                               #required=False)
