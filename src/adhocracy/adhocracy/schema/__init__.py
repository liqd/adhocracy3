"""Colander schema extensions."""
from adhocracy.interfaces import AdhocracyReferenceType
from pyramid.path import DottedNameResolver
from substanced import schema
from substanced.objectmap import reference_sourceid_property
from substanced.schema import IdSet
from substanced.util import find_objectmap

import colander


class Identifier(colander.SchemaNode):

    """Alpha/numeric/_/-/. String.

    Example value: blu.ABC_12-3

    """

    schema_type = colander.String
    validator = colander.Regex(u'^[a-zA-Z0-9\_\-\.]+$')


class AbsolutePath(colander.SchemaNode):

    """Absolute path made with  Identifier Strings.

    Example value: /bluaABC/_123/3

    """

    schema_type = colander.String
    validator = colander.Regex(u'^/[a-zA-Z0-9\_\-\.\/]+$')


class PathSet(IdSet):

    """ Colander Type to store object paths.

    Serialize to a list of absolute object paths (['/o1/o2', '/o3']).
    Deserialize to a list of zodb oids [123123, 4324324].

    Raise colander.Invalid if path or oid does not exist.

    """

    def serialize(self, node, value):
        """Serialize oid to path.

        Return List with paths.

        """

        if value is colander.null:
            return value
        self._check_iterable(node, value)
        context = node.bindings['context']
        object_map = find_objectmap(context)
        paths = []
        for oid in value:
            path_tuple = object_map.path_for(oid)
            if path_tuple is None:
                raise colander.Invalid(node,
                                       msg='This oid does not exist.',
                                       value=oid)
            path = '/'.join(path_tuple)
            paths.append(path)
        return paths

    def deserialize(self, node, value):
        """Deserialize path to oid.

        Return List with oids.

        """
        if value is colander.null:
            return value
        self._check_iterable(node, value)
        context = node.bindings['context']
        object_map = find_objectmap(context)
        oids = []
        for path in value:
            path_tuple = tuple(str(path).split('/'))
            oid = object_map.objectid_for(path_tuple)
            if oid is None:
                raise colander.Invalid(node,
                                       msg='This object path does not exist.',
                                       value=path)
            oids.append(oid)
        return oids


def get_all_resources(node, context):
    """Return List with all resources."""
    return []
    #FIXME: we need this to make the sdi work
    # interfaces = [node.interfaces]
    # catalog = find_catalog(context, 'system')
    # if catalog:
    #     interfaces = catalog['interfaces']
    #     docs = interfaces.eq(interface).execute().all()
    #     return map(lambda x: (get_oid(x), getattr(x, 'name', None) or
    #                           x.__name__),
    #                [d for d in docs if d])


class ReferenceSetSchemaNode(schema.MultireferenceIdSchemaNode):

    """Colander SchemaNode to store a set of references."""

    schema_type = PathSet

    default = []
    missing = colander.drop
    reftype = AdhocracyReferenceType
    choices_getter = get_all_resources

    def _get_choices(self):
        context = self.bindings['context']
        return self.choices_getter(context)

    @property
    def property_object(self):
        """Return property object to store reference values."""
        return reference_sourceid_property(self.reftype)

    def validator(self, node, value):
        """Validate."""
        context = node.bindings['context']
        object_map = find_objectmap(context)
        res = DottedNameResolver()
        reftype = res.maybe_resolve(self.reftype)
        isheet = reftype.getTaggedValue('target_isheet')
        for oid in value:
            resource = object_map.object_for(oid)
            if not isheet.providedBy(resource):
                    error = 'This Resource does not provide interface %s' % \
                            (isheet.__identifier__)
                    raise colander.Invalid(node, msg=error, value=oid)
