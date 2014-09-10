"""Colander schema extensions."""
from collections import Sequence
from collections import OrderedDict
from datetime import datetime
from pyramid.traversal import find_resource
from pyramid.traversal import resource_path
from pytz import UTC
import colander
import pytz

from adhocracy.interfaces import ILocation
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

    """Schema type that serialized a :term:`location`-aware object to its url.

    Example value:  'http://a.org/bluaABC/_123/3'
    """

    def __init__(self, use_resource_location=False):
        self.use_resource_location = use_resource_location
        """If `False` the :term:`request` binding is used to serialize
        to the resource url.
        Else the :term:`context` binding is used to  serialize to
        the :term:`Resource Location`.
        Default `False`.
        """

    def serialize(self, node, value):
        """Serialize object to url.

        :param node: the Colander node.
        :param value: the resource to serialize
        :return: the path of that resource
        """
        if value in (colander.null, ''):
            return ''
        try:
            raise_attribute_error_if_not_location_aware(value)
            return self._serialize_location_or_url(node, value)
        except AttributeError:
            raise colander.Invalid(node,
                                   msg='This resource is not location aware',
                                   value=value)

    def _serialize_location_or_url(self, node, value):
        if self.use_resource_location:
            assert 'context' in node.bindings
            return resource_path(value)
        else:
            assert 'request' in node.bindings
            request = node.bindings['request']
            return request.resource_url(value)

    def deserialize(self, node, value):
        """Deserialize url to object.

        :param node: the Colander node.
        :param value: the url ort :term:`Resource Location` to deserialize
        :return: the resource registered under that path
        :raise colander.Invalid: if the object does not exist.
        """
        if value is colander.null:
            return value
        try:
            resource = self._deserialize_to_location_or_url(node, value)
            raise_attribute_error_if_not_location_aware(resource)
        except (KeyError, AttributeError):
            raise colander.Invalid(
                node,
                msg='This resource path does not exist.', value=value)
        return resource

    def _deserialize_to_location_or_url(self, node, value):
        if self.use_resource_location:
            assert 'context' in node.bindings
            context = node.bindings['context']
            return find_resource(context, value)
        else:
            assert 'request' in node.bindings
            request = node.bindings['request']
            application_url_len = len(request.application_url)
            if application_url_len > len(str(value)):
                raise KeyError
            # Fixme: This does not work with :term:`virtual hosting`
            path = value[application_url_len:]
            return find_resource(request.root, path)


class Resource(AdhocracySchemaNode):

    """A resource SchemaNode.

    Example value:  'http://a.org/bluaABC/_123/3'
    """

    default = ''
    missing = colander.drop
    schema_type = ResourceObject


def _validate_reftype(node: colander.SchemaNode, value: ILocation):
        reftype = node.reftype
        isheet = reftype.getTaggedValue('target_isheet')
        if not isheet.providedBy(value):
            error = 'This Resource does not provide interface %s' % \
                    (isheet.__identifier__)
            raise colander.Invalid(node, msg=error, value=value)


class Reference(Resource):

    """Schema Node to reference a resource that implements a specific sheet.

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

    reftype = SheetReference
    backref = False
    validator = colander.All(_validate_reftype)


class Resources(colander.SequenceSchema):

    """List of :class:`Resource:`s."""

    resource = Resource()
    default = []
    missing = []


def _validate_reftypes(node: colander.SchemaNode, value: Sequence):
    for resource in value:
        _validate_reftype(node, resource)


class References(Resources):

    """Schema Node to reference resources that implements a specific sheet.

    The constructor accepts these additional keyword arguments:

        - ``reftype``: :class:`adhocracy.interfaces.SheetReference`.
                       The `target_isheet` attribute of the `reftype` specifies
                       the sheet that accepted resources must implement.
                       Storing another kind of resource will trigger a
                       validation error.
        - ``backref``: marks this Reference as a back reference.
                       :class:`adhocracy.sheet.ResourceSheet` can use this
                       information to autogenerate the appstruct/cstruct.
                       Default: False.
    """

    reftype = SheetReference
    backref = False
    validator = colander.All(_validate_reftypes)


class UniqueReferences(References):

    """Schema Node to reference resources that implements a specific sheet.

    The order is preserved, duplicates are removed.

    Example value: ["http:a.org/bluaABC"]
    """

    def preparer(self, value: Sequence) -> list:
        if value is colander.null:
            return value
        value_dict = OrderedDict.fromkeys(value)
        return list(value_dict)


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
