"""Colander schema extensions."""
from datetime import datetime
from pyramid.traversal import resource_path
from pyramid.traversal import find_resource
from pytz import UTC
from substanced.schema import IdSet
import colander
import pytz

from adhocracy.interfaces import SheetReference


class AdhocracySchemaNode(colander.SchemaNode):

    """Subclass of :class: `colander.SchemaNode` with extended keyword support.

    The constructor accepts these additional keyword arguments:

        - ``readonly``: Disable deserialization. Default: False
    """

    readonly = False

    def deserialize(self, cstruct=colander.null):
        """ Deserialize the :term:`cstruct` into an :term:`appstruct`. """
        if self.readonly and cstruct != colander.null:
            raise colander.Invalid(self, 'This field is ``readonly``.')
        return super().deserialize(cstruct)


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
    if value in (colander.null, ''):
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


def validate_name_is_unique(node: colander.SchemaNode, value: str):
    """Validate if `value` is name that does not exists in the parent object.

    Node must a have a `parent_pool` binding object attribute
    that points to the parent pool object :class:`adhocracy.interfaces.IPool`.

    :raises colander.Invalid: if `name` already exists in the parent or parent
                              is None.
    """
    parent = node.bindings.get('parent_pool', None)
    try:
        parent.check_name(value)
    except AttributeError:
        msg = 'This resource has no parent pool to validate the name.'
        raise colander.Invalid(node, msg)
    except KeyError:
        msg = 'The name already exists in the parent pool.'
        raise colander.Invalid(node, msg, value=value)
    except ValueError:
        msg = 'The name has forbidden characters or is not a string.'
        raise colander.Invalid(node, msg, value=value)


class Identifier(AdhocracySchemaNode):

    """Like :class:`Name`, but doesn't check uniqueness..

    Example value: blu.ABC_12-3
    """

    schema_type = colander.String
    default = ''
    missing = colander.drop
    relative_regex = '[a-zA-Z0-9\_\-\.]+'
    validator = colander.All(colander.Regex('^' + relative_regex + '$'),
                             colander.Length(min=1, max=100))


@colander.deferred
def deferred_validate_name(node: colander.SchemaNode, kw: dict) -> callable:
    """Check that the node value is a valid child name."""
    return colander.All(validate_name_is_unique,
                        *Identifier.validator.validators)


class Name(AdhocracySchemaNode):

    """ The unique `name` of a resource inside the parent pool.

    Allowed characters are: "alpha" "numeric" "_"  "-" "."
    The maximal length is 100 characters, the minimal length 1.

    Example value: blu.ABC_12-3

    This node needs a `parent_pool` binding to validate.
    """

    schema_type = colander.String
    default = ''
    missing = colander.drop
    validator = deferred_validate_name


class Email(AdhocracySchemaNode):

    """String with email address.

    Example value: test@test.de
    """

    schema_type = colander.String
    default = ''
    missing = colander.drop
    validator = colander.Email()


_ZONES = pytz.all_timezones


class TimeZoneName(AdhocracySchemaNode):

    """String with time zone.

    Example value: UTC
    """

    schema_type = colander.String
    default = 'UTC'
    missing = colander.drop
    validator = colander.OneOf(_ZONES)


class AbsolutePath(AdhocracySchemaNode):

    """Absolute path made with  Identifier Strings.

    Example value: /bluaABC/_123/3
    """

    schema_type = colander.String
    relative_regex = '/[a-zA-Z0-9\_\-\.\/]+'
    validator = colander.Regex('^' + relative_regex + '$')


class ResourceObject(colander.SchemaType):

    """Resource object that automatically deserialized itself to a path.

    Example value: like AbsolutePath, e.g. '/bluaABC/_123/3'
    """

    def serialize(self, node, value):
        """Serialize object to path."""
        return serialize_path(node, value)

    def deserialize(self, node, value):
        """Deserialize path to object."""
        return deserialize_path(node, value)


class Reference(AbsolutePath):

    """Reference to a resource that implements a specific sheet.

    The constructor accepts these additional keyword arguments:

        - ``reftype``: :class:` adhocracy.interfaces.SheetReference`.
                       The `target_isheet` attribute of the `reftype` specifies
                       the sheet that accepted resources must implement.
                       Storing another kind of resource will trigger a
                       validation error.
        - ``backref``: marks this Reference as a back reference.
                       :class:`adhocracy.sheet.ResourceSheet` can use this
                       information to autogenerate the appstruct/cstruct.
                       Default: False.
    """

    default = ''
    missing = colander.drop
    schema_type = ResourceObject
    reftype = SheetReference
    backref = False

    def validator(self, node, value):
        """Validate."""
        reftype = self.reftype
        isheet = reftype.getTaggedValue('target_isheet')
        if not isheet.providedBy(value):
            error = 'This Resource does not provide interface %s' % \
                    (isheet.__identifier__)
            raise colander.Invalid(node, msg=error, value=value)


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
        self._check_nonstr_iterable(node, value)
        paths = []
        for resource in value:
            paths.append(serialize_path(node, resource))
        return paths

    def _check_nonstr_iterable(self, node, value):
        if isinstance(value, str) or not hasattr(value, '__iter__'):
            raise colander.Invalid(node, '{} is not list-like'.format(value))

    def deserialize(self, node, value):
        """Deserialize path to object.

        Return iterable with objects.

        Raises:
            KeyError: if path cannot be traversed to an ILocation aware object.
        """
        if value is colander.null:
            return value
        self._check_nonstr_iterable(node, value)
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


class AbstractReferenceIterable(AdhocracySchemaNode):

    """Abstract Colander SchemaNode to store multiple references.

    This is is an abstract class, only subclasses that set `schema_type` to a
    concrete subclass of `AbstractIterableOfPaths` can be instantiated.
    """

    schema_type = AbstractIterableOfPaths

    default = []
    missing = colander.drop
    reftype = SheetReference
    backref = False

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


def string_has_no_newlines_validator(value: str) -> bool:
    """Check for new line characters."""
    return False if '\n' in value or '\r' in value else True  # noqa


class SingleLine(colander.SchemaNode):  # noqa

    """ UTF-8 encoded String without line breaks.

    Disallowed characters are linebreaks like: \n, \r.
    Example value: This is a something.
    """

    schema_type = colander.String
    default = ''
    missing = colander.drop
    validator = colander.Function(string_has_no_newlines_validator,
                                  msg='New line characters are not allowed.')


class Text(AdhocracySchemaNode):

    """ UTF-8 encoded String with line breaks.

    Example value: This is a something
                   with new lines.
    """

    schema_type = colander.String
    default = ''
    missing = colander.drop


class Password(AdhocracySchemaNode):

    """ UTF-8 encoded text.

    Minimal length=6, maximal length=100 characters.
    Example value: secret password?
    """

    schema_type = colander.String
    default = ''
    missing = colander.drop
    validator = colander.Length(min=6, max=100)


@colander.deferred
def deferred_date_default(node: colander.MappingSchema, kw: dict) -> datetime:
    """Return current date."""
    return datetime.utcnow().replace(tzinfo=UTC)


class DateTime(AdhocracySchemaNode):

    """ DateTime object.

    This type serializes python ``datetime.datetime`` objects to a
    `ISO8601 <http://en.wikipedia.org/wiki/ISO_8601>`_ string format.
    The format includes the date, the time, and the timezone of the
    datetime.

    Example values: 2014-07-21, 2014-07-21T09:10:37, 2014-07-21T09:10:37+00:00

    The default/missing value is the current datetime.

    Constructor arguments:

    :param 'tzinfo': This timezone is used if the :term:`cstruct` is missing
                     the tzinfo. Defaults to UTC
    """

    schema_type = colander.DateTime
    default = deferred_date_default
    missing = deferred_date_default
