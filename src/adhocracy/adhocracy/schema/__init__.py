"""Colander schema extensions."""
from pyramid.traversal import resource_path
from pyramid.traversal import find_resource
from substanced import schema
from substanced.schema import IdSet
import colander

from adhocracy.interfaces import SheetReference


def raise_attribute_error_if_not_location_aware(context) -> None:
    """Ensure that the argument is location-aware.

    :raise AttributeError: if it isn't

    """
    context.__parent__
    context.__name__


def serialize_path(node, value):
    """Serialize object to path with 'pyramid.traveral.resource_path'.

    :param node: the Colander node
    :param value: the resource to serialize
    :return: the path of that resource

    """
    if value is colander.null:
        return value
    try:
        raise_attribute_error_if_not_location_aware(value)
        return resource_path(value)
    except AttributeError:
        raise colander.Invalid(
            node,
            msg='This resource is not location aware', value=value)


def deserialize_path(node, value):
    """Deserialize path to object.

    :param node: the Colander node
    :param value: the path to deserialize
    :return: the resource registered under that path

    """
    if value is colander.null:
        return value
    context = node.bindings['context']
    try:
        resource = find_resource(context, value)
        raise_attribute_error_if_not_location_aware(resource)
    except (KeyError, AttributeError):
        raise colander.Invalid(
            node,
            msg='This resource path does not exist.', value=value)
    return resource


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


class AutomaticAbsolutePath(AbsolutePath):

    """Absolute path that automatically deserialized itself to a resource."""

    def serialize(self, value):
        return serialize_path(self, value)

    def deserialize(self, value):
        # TODO now to get the binding??
        return deserialize_path(self, value)


class AbstractIterableOfPaths(IdSet):

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

    def serialize(self, node, value):
        """Serialize object to path with 'pyramid.traveral.resource_path'.

        Return list with paths.

        """
        if value is colander.null:
            return value
        self._check_iterable(node, value)
        paths = []
        for resource in value:
            paths.append(serialize_path(node, resource))
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
        resources = self.create_empty_appstruct()
        for path in value:
            resource = deserialize_path(node, path)
            self.add_to_appstruct(resources, resource)
        return resources


class ListOfUniquePaths(AbstractIterableOfPaths):

    """List of :class:`AbsolutePath`.

    The order is preserved, duplicates are removed.

    Example value: [/bluaABC, /_123/3]

    """

    def create_empty_appstruct(self):
        """Create and return an empty list."""
        return []

    def add_to_appstruct(self, appstruct, element):
        """Add an element to a list if it is no duplicate."""
        if not hasattr(self, '_elements'):
            self._elements = set()
        if element not in self._elements:
            appstruct.append(element)
            self._elements.add(element)


class SetOfPaths(AbstractIterableOfPaths):

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
    # FIXME: we need this to make the sdi work
    # interfaces = [node.interfaces]
    # catalog = find_catalog(context, 'system')
    # if catalog:
    #     interfaces = catalog['interfaces']
    #     docs = interfaces.eq(interface).execute().all()
    #     return map(lambda x: (get_oid(x), getattr(x, 'name', None) or
    #                           x.__name__),
    #                [d for d in docs if d])


class AbstractReferenceIterable(schema.MultireferenceIdSchemaNode):

    """Abstract Colander SchemaNode to store multiple references.

    This is is an abstract class, only subclasses that set `schema_type` to a
    concrete subclass of `AbstractIterableOfPaths` can be instantiated.

    """

    schema_type = AbstractIterableOfPaths

    default = []
    missing = colander.drop
    reftype = SheetReference
    choices_getter = get_all_resources

    def _get_choices(self):
        context = self.bindings['context']
        return self.choices_getter(context)

    def validator(self, node, value):
        """Validate."""
        reftype = self.reftype
        isheet = reftype.getTaggedValue('target_isheet')
        for resource in value:
            if not isheet.providedBy(resource):
                error = 'This Resource does not provide interface %s' % \
                        (isheet.__identifier__)
                raise colander.Invalid(node, msg=error, value=resource)


class ListOfUniqueReferences(AbstractReferenceIterable):

    """Colander SchemaNode to store a list of references without duplicates."""

    schema_type = ListOfUniquePaths
