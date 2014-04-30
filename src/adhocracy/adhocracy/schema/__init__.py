"""Colander schema extensions."""
from adhocracy.interfaces import SheetReferenceType
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


class AbstractPathIterable(IdSet):

    """Abstract Colander type to store multiple object paths.

    Serialize to a list of absolute object paths (['/o1/o2', '/o3']).
    Deserialize to an iterable of zodb oids [123123, 4324324].

    Raise colander.Invalid if path or oid does not exist.

    Child classes must overwrite the `create_empty_appstruct` and
    `add_to_appstruct` methods for the specific iterable to use for
    deserialization (e.g. list or set).

    """

    def create_empty_appstruct(self):
        """Create an empty iterable container."""
        raise NotImplementedError()  # pragma: no cover

    def add_to_appstruct(self, appstruct, element):
        """Add an element to the container to used to store paths."""
        raise NotImplementedError()  # pragma: no cover

    def serialize(self, node, value):
        """Serialize oid to path.

        Return list with paths.

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

        Return iterable with oids.

        """
        if value is colander.null:
            return value
        self._check_iterable(node, value)
        context = node.bindings['context']
        object_map = find_objectmap(context)
        oids = self.create_empty_appstruct()
        for path in value:
            path_tuple = tuple(str(path).split('/'))
            oid = object_map.objectid_for(path_tuple)
            if oid is None:
                raise colander.Invalid(
                    node,
                    msg='This resource path does not exist.', value=path)
            self.add_to_appstruct(oids, oid)
        return oids


class PathList(AbstractPathIterable):

    """List of :class:`AbsolutePath`.

    Example value: [/bluaABC, /_123/3]

    """

    def create_empty_appstruct(self):
        """Create and return an empty list."""
        return []

    def add_to_appstruct(self, appstruct, element):
        """Add an element to a list."""
        appstruct.append(element)


class PathSet(AbstractPathIterable):

    """Set of :class:`AbsolutePath`.

    The order is not preserved, duplicates are removed.

    Example value: [/bluaABC, /_123/3]

    """

    def create_empty_appstruct(self):
        """Create and return an empty set."""
        return set()

    def add_to_appstruct(self, appstruct, element):
        """Add an element to a set."""
        appstruct.add(element)


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


class AbstractReferenceIterableSchemaNode(schema.MultireferenceIdSchemaNode):

    """Abstract Colander SchemaNode to store multiple references.

    This is is an abstract class, only subclasses that set `schema_type` to a
    concrete subclass of `AbstractPathIterable` can be instantiated.

    """

    schema_type = AbstractPathIterable

    default = []
    missing = colander.drop
    reftype = SheetReferenceType
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


class ReferenceSetSchemaNode(AbstractReferenceIterableSchemaNode):

    """Colander SchemaNode to store a set of references."""

    schema_type = PathSet


class ReferenceListSchemaNode(AbstractReferenceIterableSchemaNode):

    """Colander SchemaNode to store a list of references."""

    schema_type = PathList
