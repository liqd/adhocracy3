"""Colander schema extensions."""
from adhocracy.interfaces import SheetReferenceType
from pyramid.path import DottedNameResolver
from pyramid.traversal import resource_path
from pyramid.traversal import find_resource
from substanced import schema
from substanced.schema import IdSet

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

    Serialize a list of ILocation aware objects to paths (['/o1/o2', '/o3']).
    Deserialize to an iterable of objects.

    Raise colander.Invalid if path does not exist.

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

    def _is_location_aware(self, resource):
        """Check that resource is location aware.

        Raises:
            AttributeError

        """
        resource.__parent__
        resource.__name__

    def serialize(self, node, value):
        """Serialize object to path with 'pyramid.traveral.resource_path'.

        Return list with paths.

        """
        if value is colander.null:
            return value
        self._check_iterable(node, value)
        paths = []
        for resource in value:
            try:
                path = resource_path(resource)
                self._is_location_aware(resource)
            except AttributeError:
                raise colander.Invalid(
                    node,
                    msg='This resource is not location aware', value=resource)
            paths.append(path)
        return paths

    def deserialize(self, node, value):
        """Deserialize path to object.

        Return iterable with objects.

        Raises:
            KeyError: if path cannot be traversed to an ILocation aware object.

        """
        if value is colander.null:
            return value
        self._check_iterable(node, value)
        context = node.bindings['context']
        resources = self.create_empty_appstruct()
        for path in value:
            try:
                resource = find_resource(context, path)
                self._is_location_aware(resource)
            except (KeyError, AttributeError):
                raise colander.Invalid(
                    node,
                    msg='This resource path does not exist.', value=path)
            self.add_to_appstruct(resources, resource)
        return resources


class PathListSet(AbstractPathIterable):

    """List of :class:`AbsolutePath`.

    The order is preserved, duplicates are removed.

    Example value: [/bluaABC, /_123/3]

    """

    def create_empty_appstruct(self):
        """Create and return an empty list."""
        return []

    def add_to_appstruct(self, appstruct, element):
        """Add an element to a list."""
        # FIXME this means very bad performance for long lists.
        if element not in appstruct:
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

    def validator(self, node, value):
        """Validate."""
        res = DottedNameResolver()
        reftype = res.maybe_resolve(self.reftype)
        isheet = reftype.getTaggedValue('target_isheet')
        for resource in value:
            if not isheet.providedBy(resource):
                    error = 'This Resource does not provide interface %s' % \
                            (isheet.__identifier__)
                    raise colander.Invalid(node, msg=error, value=resource)


class ReferenceListSetSchemaNode(AbstractReferenceIterableSchemaNode):

    """Colander SchemaNode to store a list of references without duplicates."""

    schema_type = PathListSet
