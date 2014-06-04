"""Colander schema extensions."""
from pyramid.traversal import resource_path
from pyramid.traversal import find_resource
from substanced import schema
from substanced.schema import IdSet
import colander
import pytz

from adhocracy.interfaces import SheetReference


def name_is_unique_validator(node: colander.SchemaNode, value: str):
    """Validate if `value` is name that does not exists in the parent object.

    Node must a have a `context` binding object with an __parent__ attribute
    that points to a dictionary like object.

    :raises colander.Invalid: if `name` already exists in the parent or parent
                              is None.
    """
    context = node.bindings.get('context')
    parent = context.__parent__
    if parent is None:
        msg = 'This resource has no parent pool to validate that the name is'\
              ' unique'
        raise colander.Invalid(node, msg)
    if value in parent:
        msg = 'The name "{0}" already exists in the parent pool.'.format(value)
        raise colander.Invalid(node, msg)


class Name(colander.SchemaNode):

    """ The unique `name` of a resource inside the parent pool.

    Allowed characters are: "alpha" "numeric" "_"  "-" "."
    The maximal length is 100 characters, the minimal length 1.

    Example value: blu.ABC_12-3
    """

    schema_type = colander.String
    default = '',
    missing = colander.drop
    validator = colander.All(colander.Regex(u'^[a-zA-Z0-9\_\-\.]+$'),
                             colander.Length(min=1, max=100),
                             name_is_unique_validator)


class Email(colander.SchemaNode):

    """String with email address.

    Example value: test@test.de

    """

    schema_type = colander.String
    default = ''
    missing = colander.drop
    validator = colander.Email()


_ZONES = pytz.all_timezones


class TimeZoneName(colander.SchemaNode):

    """String with time zone.

    Example value: UTC
    """

    schema_type = colander.String
    default = 'UTC'
    missing = colander.drop
    validator = colander.OneOf(_ZONES)


class AbsolutePath(colander.SchemaNode):

    """Absolute path made with  Identifier Strings.

    Example value: /bluaABC/_123/3

    """

    schema_type = colander.String
    validator = colander.Regex(u'^/[a-zA-Z0-9\_\-\.\/]+$')


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

    def _raise_attribute_error_if_not_location_aware(self, context):
        context.__parent__
        context.__name__

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
                self._raise_attribute_error_if_not_location_aware(resource)
                path = resource_path(resource)
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
                self._raise_attribute_error_if_not_location_aware(resource)
            except (KeyError, AttributeError):
                raise colander.Invalid(
                    node,
                    msg='This resource path does not exist.', value=path)
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
