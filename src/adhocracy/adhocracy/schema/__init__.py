from substanced import schema
from substanced.objectmap import reference_sourceid_property
from substanced.schema import IdSet
from substanced.util import find_objectmap
from zope.interface import Interface

import colander


class Identifier(colander.SchemaNode):
    """Alpha/numeric/_/-/. String.

    Example value: blu.ABC_12-3
    """

    schema_type = colander.String
    validator = colander.Regex(u'^[a-zA-Z0-9\_\-\.]+$')


class AbsolutePath(colander.SchemaNode):
    """Absolute path made with Identifier Strings.

     Example value: /bluaABC/_123/3
    """

    schema_type = colander.String
    validator = colander.Regex(u'^/[a-zA-Z0-9\_\-\.\/]+$')


class PathSet(IdSet):
    """ Colander Type to store object paths.

    Serialize to a list of absolute object paths (["/o1/o2", "/o3"]).
    Deserialize to a list of zodb oids [123123, 4324324].

    Raise colander.Invalid if path or oid does not exist.
    """

    def serialize(self, node, value):
        if value is colander.null:
            return value
        self._check_iterable(node, value)
        context = node.bindings["context"]
        object_map = find_objectmap(context)
        paths = []
        for oid in value:
            path_tuple = object_map.path_for(oid)
            if path_tuple is None:
                raise colander.Invalid(node,
                                       msg="This oid does not exist.",
                                       value=oid)
            path = "/".join(path_tuple)
            paths.append(path)
        return paths

    def deserialize(self, node, value):
        if value is colander.null:
            return value
        self._check_iterable(node, value)
        context = node.bindings["context"]
        object_map = find_objectmap(context)
        oids = []
        for path in value:
            path_tuple = tuple(str(path).split("/"))
            oid = object_map.objectid_for(path_tuple)
            if oid is None:
                raise colander.Invalid(node,
                                       msg="This object path does not exist.",
                                       value=path)
            oids.append(oid)
        return oids


def get_all_resources(node, context, request):
    return []
    #FIXME: we need this to make the sdi work
    # interfaces = [node.interfaces]
    # catalog = find_catalog(context, 'system')
    # if catalog:
    #     interfaces = catalog['interfaces']
    #     docs = interfaces.eq(interface).execute().all()
    #     return map(lambda x: (get_oid(x), getattr(x, "name", None) or
    #                           x.__name__),
    #                [d for d in docs if d])


class ReferenceSetSchemaNode(schema.MultireferenceIdSchemaNode):
    """Colander SchemaNode to store a set of references"""

    schema_type = PathSet

    default = []
    missing = []
    interfaces = [Interface]
    # FIXME: add coices getter to make sdi view work
    choices_getter = get_all_resources

    @property
    def property_object(self):
        """Property object to store reference values"""

        reference_type = self.name
        return reference_sourceid_property(reference_type)

    def validator(self, node, value):
        context = node.bindings["context"]
        object_map = find_objectmap(context)
        for oid in value:
            resource = object_map.object_for(oid)
            for i in node.interfaces:
                if not i.providedBy(resource):
                    error = "This Resource does not provide interface %s" % \
                            (i.__identifier__)
                    raise colander.Invalid(node, msg=error, value=oid)
