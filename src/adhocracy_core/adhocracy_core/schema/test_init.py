import unittest
from unittest.mock import Mock

from pyramid import testing
import colander
from pytest import raises
from pytest import fixture


############
#  helper  #
############

def add_node_binding(node, context=None, request=None):
    node.bindings = dict()
    if context is not None:
        node.bindings['context'] = context
    if request is not None:
        node.bindings['request'] = request
    return node

###########
#  tests  #
###########

class AdhocracySchemaNodeUnitTest(unittest.TestCase):

    def _make_one(self, *args, **kwargs):
        from adhocracy_core.schema import AdhocracySchemaNode
        return AdhocracySchemaNode(*args, **kwargs)

    def test_serialize_non_readonly(self):
        inst = self._make_one(colander.String())
        assert inst.serialize(1) == '1'

    def test_serialize_readonly(self):
        inst = self._make_one(colander.Integer(), readonly=True)
        assert inst.serialize(1) == '1'

    def test_deserialize_non_readonly(self):
        inst = self._make_one(colander.Integer())
        assert inst.deserialize('1') == 1

    def test_deserialize_readonly(self):
        inst = self._make_one(colander.Integer(), readonly=True)
        with raises(colander.Invalid):
            inst.deserialize('1')


class NameUnitTest(unittest.TestCase):

    def setUp(self):
        self.parent = Mock()

    def _make_one(self):
        from adhocracy_core.schema import Name
        inst = Name()
        return inst.bind(parent_pool=self.parent)

    def test_valid(self):
        inst = self._make_one()
        assert inst.deserialize('blu.ABC_12-3')

    def test_non_valid_missing_parent_pool_binding(self):
        inst = self._make_one()
        inst_no_context = inst.bind()
        with raises(colander.Invalid):
            inst_no_context.deserialize('blu.ABC_123')

    def test_non_valid_empty(self):
        inst = self._make_one()
        with raises(colander.Invalid):
            inst.validator(inst, '')

    def test_non_valid_to_long(self):
        inst = self._make_one()
        with raises(colander.Invalid):
            inst.validator(inst, 'x' * 101)

    def test_non_valid_wrong_characters(self):
        inst = self._make_one()
        with raises(colander.Invalid):
            inst.validator(inst, 'ä')

    def test_non_valid_not_unique(self):
        inst = self._make_one()
        self.parent.check_name.side_effect = KeyError
        with raises(colander.Invalid):
            inst.validator(inst, 'name')

    def test_non_valid_forbbiden_child_name(self):
        inst = self._make_one()
        self.parent.check_name.side_effect = ValueError
        with raises(colander.Invalid):
            inst.validator(inst, '@@')

    def test_invalid_asdict_output(self):
        """Test case added since we had a bug here."""
        inst = self._make_one()
        try:
            inst.validator(inst, 'ä')
            assert False
        except colander.Invalid as err:
            wanted = {'': 'String does not match expected pattern'}
            assert err.asdict() == wanted


class EmailUnitTest(unittest.TestCase):

    def _make_one(self):
        from adhocracy_core.schema import Email
        return Email()

    def test_valid(self):
        inst = self._make_one()
        assert inst.validator(inst, 'test@test.de') is None

    def test_non_valid(self):
        inst = self._make_one()
        with raises(colander.Invalid):
            inst.validator(inst, 'wrong')


class TimeZoneNameUnitTest(unittest.TestCase):

    def _make_one(self):
        from adhocracy_core.schema import TimeZoneName
        return TimeZoneName()

    def test_valid(self):
        inst = self._make_one()
        assert inst.validator(inst, 'Europe/Berlin') is None

    def test_non_valid(self):
        inst = self._make_one()
        with raises(colander.Invalid):
            inst.validator(inst, 'wrong')

    def test_default(self):
        inst = self._make_one()
        assert inst.default == 'UTC'


class AbsolutePath(unittest.TestCase):

    def _make_one(self):
        from adhocracy_core.schema import AbsolutePath
        return AbsolutePath()

    def test_valid(self):
        inst = self._make_one()
        assert inst.validator(inst, '/blu.ABC_12-3/aaa') is None

    def test_non_valid(self):
        inst = self._make_one()
        with raises(colander.Invalid):
            inst.validator(inst, 'blu.ABC_12-3')


class ResourceObjectUnitTests(unittest.TestCase):

    def _make_one(self, **kwargs):
        from adhocracy_core.schema import ResourceObject
        return ResourceObject(**kwargs)

    def setUp(self):
        self.context = testing.DummyResource()
        self.child = testing.DummyResource()
        request = testing.DummyRequest()
        request.root = self.context
        self.request = request

    def test_serialize_colander_null(self):
        inst = self._make_one()
        result = inst.serialize(None, colander.null)
        assert result == ''

    def test_serialize_value_location_aware(self):
        inst = self._make_one()
        self.context['child'] = self.child
        node = add_node_binding(colander.Mapping(), request=self.request)
        result = inst.serialize(node, self.child)
        assert result == self.request.application_url + '/child/'

    def test_serialize_value_location_aware_but_missing_request(self):
        inst = self._make_one()
        self.context['child'] = self.child
        node = add_node_binding(colander.Mapping())
        with raises(AssertionError):
            inst.serialize(node, self.child)

    def test_serialize_value_not_location_aware(self):
        inst = self._make_one()
        del self.child.__parent__
        del self.child.__name__
        node = add_node_binding(colander.Mapping(), request=self.request)
        with raises(colander.Invalid):
            inst.serialize(node, self.child)

    def test_serialize_value_location_aware_without_parent_and_name(self):
        inst = self._make_one()
        node = add_node_binding(colander.Mapping(), request=self.request)
        result = inst.serialize(node, self.child)
        assert result == self.request.application_url + '/'

    def test_serialize_value_location_aware_with_use_resource_location(self):
        inst = self._make_one(use_resource_location=True)
        self.context['child'] = self.child
        node = add_node_binding(colander.Mapping(), context=self.context)
        result = inst.serialize(node, self.child)
        assert result == '/child'

    def test_serialize_value_location_aware_with_use_resource_location_without_context_binding(self):
        inst = self._make_one(use_resource_location=True)
        self.context['child'] = self.child
        node = add_node_binding(colander.Mapping())
        with raises(AssertionError):
            inst.serialize(node, self.child)

    def test_deserialize_value_null(self):
        inst = self._make_one()
        node = colander.Mapping()
        result = inst.deserialize(node, colander.null)
        assert result == colander.null

    def test_deserialize_value_valid_path(self):
        inst = self._make_one()
        self.context['child'] = self.child
        node = add_node_binding(colander.Mapping(), request=self.request)
        result = inst.deserialize(node, self.request.application_url + '/child')
        assert result == self.child

    def test_deserialize_value_invalid_path_wrong_child_name(self):
        inst = self._make_one()
        node = add_node_binding(colander.Mapping(), request=self.request)
        with raises(colander.Invalid):
            inst.deserialize(node, self.request.application_url + '/wrong_child')

    def test_deserialize_value_invalid_path_to_short(self):
        inst = self._make_one()
        node = add_node_binding(colander.Mapping(), request=self.request)
        with raises(colander.Invalid):
            inst.deserialize(node, '/wrong_child')

    def test_deserialize_value_location_aware_with_use_resource_location(self):
        inst = self._make_one(use_resource_location=True)
        self.context['child'] = self.child
        node = add_node_binding(colander.Mapping(), context=self.context)
        child_url = self.request.application_url + '/child/'
        result = inst.deserialize(node, child_url)
        assert result == self.child

    def test_deserialize_value_location_aware_with_use_resource_location_without_context_binding(self):
        inst = self._make_one(use_resource_location=True)
        self.context['child'] = self.child
        node = add_node_binding(colander.Mapping())
        child_url = self.request.application_url + '/child/'
        with raises(AssertionError):
            inst.deserialize(node, child_url)


class TestResource:

    def _make_one(self):
        from adhocracy_core.schema import Resource
        return Resource()

    def test_create(self):
        from adhocracy_core.schema import ResourceObject
        inst = self._make_one()
        assert inst.default == ''
        assert inst.missing == colander.drop
        assert inst.schema_type == ResourceObject


class ReferenceUnitTest(unittest.TestCase):

    def _make_one(self, **kwargs):
        from adhocracy_core.schema import Reference
        return Reference(**kwargs)

    def setUp(self):
        self.context = testing.DummyResource()
        self.target = testing.DummyResource()
        self.child = testing.DummyResource()
        request = testing.DummyRequest()
        request.root = self.context
        self.request = request

    def test_create(self):
        from adhocracy_core.interfaces import SheetReference
        from adhocracy_core.schema import _validate_reftype
        inst = self._make_one()
        assert inst.backref is False
        assert inst.reftype == SheetReference
        assert inst.validator.validators == (_validate_reftype,)

    def test_with_backref(self):
        inst = self._make_one(backref=True)
        assert inst.backref

    def test_valid_interface(self):
        from zope.interface import alsoProvides
        inst = self._make_one()
        isheet = inst.reftype.getTaggedValue('target_isheet')
        alsoProvides(self.target, isheet)
        inst = add_node_binding(node=inst, request=self.request)
        assert inst.validator(inst, self.target) is None

    def test_nonvalid_interface(self):
        inst = self._make_one()
        inst = add_node_binding(node=inst, request=self.request)
        with raises(colander.Invalid):
            inst.validator(inst, self.target)


class TestResources:

    @fixture
    def request(self, context):
        request = testing.DummyRequest()
        request.root = context
        return request

    def _make_one(self):
        from adhocracy_core.schema import Resources
        return Resources()

    def test_create(self):
        from adhocracy_core.schema import ResourceObject
        inst = self._make_one()
        assert isinstance(inst, colander.SequenceSchema)
        assert inst.default == []
        assert inst['resource'].schema_type == ResourceObject

    def test_serialize(self, request):
        inst = self._make_one().bind(request=request)
        child = testing.DummyResource()
        request.root['child'] = child
        child_url = request.resource_url(child)
        assert inst.serialize([child]) == [child_url]

    def test_deserialize(self, request):
        inst = self._make_one().bind(request=request)
        child = testing.DummyResource()
        request.root['child'] = child
        child_url = request.resource_url(child)
        assert inst.deserialize([child_url]) == [child]


class TestReferences:

    @fixture
    def request(self, context):
        context['target'] = testing.DummyResource()
        request = testing.DummyRequest()
        request.root = context
        return request

    def _make_one(self, **kwargs):
        from adhocracy_core.schema import References
        return References(**kwargs)

    def test_create(self):
        from adhocracy_core.interfaces import SheetReference
        from adhocracy_core.schema import _validate_reftypes
        from adhocracy_core.schema import Resources
        inst = self._make_one()
        assert inst.backref is False
        assert inst.reftype == SheetReference
        assert inst.validator.validators == (_validate_reftypes,)
        assert isinstance(inst, Resources)

    def test_with_backref(self):
        inst = self._make_one(backref=True)
        assert inst.backref

    def test_valid_interface(self, request):
        from zope.interface import alsoProvides
        inst = self._make_one().bind(request=request)
        isheet = inst.reftype.getTaggedValue('target_isheet')
        target = request.root['target']
        alsoProvides(target, isheet)
        assert inst.validator(inst, [target]) is None

    def test_nonvalid_interface(self, request):
        inst = self._make_one().bind(request=request)
        target = request.root['target']
        with raises(colander.Invalid):
            inst.validator(inst, [target])


class TestUniqueReferences:

    @fixture
    def request(self, context):
        from adhocracy_core.interfaces import ISheet
        context['target'] = testing.DummyResource(__provides__=ISheet)
        context['target1'] = testing.DummyResource(__provides__=ISheet)
        request = testing.DummyRequest()
        request.root = context
        return request

    def _make_one(self, **kwargs):
        from adhocracy_core.schema import UniqueReferences
        return UniqueReferences(**kwargs)

    def test_create(self):
        from adhocracy_core.schema import References
        inst = self._make_one()
        assert isinstance(inst, References)

    def test_valid_deserialize_with_duplication(self, request):
        inst = self._make_one().bind(request=request)
        target = request.root['target']
        target_url = request.resource_url(target)
        assert inst.deserialize([target_url, target_url]) == [target]

    def test_valid_deserialize_without_duplication(self, request):
        inst = self._make_one().bind(request=request)
        target = request.root['target']
        target1 = request.root['target1']
        target_url = request.resource_url(target)
        target1_url = request.resource_url(target1)
        assert inst.deserialize([target_url, target1_url]) == [target, target1]


class StringUnitTest(unittest.TestCase):

    def _make_one(self):
        from adhocracy_core.schema import SingleLine
        return SingleLine()

    def test_serialize_valid_emtpy(self):
        inst = self._make_one()
        assert inst.deserialize() == colander.drop

    def test_deserialize_valid_emtpy(self):
        inst = self._make_one()
        assert inst.serialize() == ''

    def test_deserialize_valid(self):
        inst = self._make_one()
        assert inst.deserialize('line') == 'line'

    def test_deserialize_non_valid_with_newline(self):
        inst = self._make_one()
        with raises(colander.Invalid):
            inst.deserialize('line\n')

    def test_deserialize_non_valid_with_carriage_return(self):
        inst = self._make_one()
        with raises(colander.Invalid):
            inst.deserialize('line\r')


class TextUnitTest(unittest.TestCase):

    def _make_one(self):
        from adhocracy_core.schema import Text
        return Text()

    def test_serialize_valid_emtpy(self):
        inst = self._make_one()
        assert inst.deserialize() == colander.drop

    def test_deserialize_valid_emtpy(self):
        inst = self._make_one()
        assert inst.serialize() == ''

    def test_deserialize_valid_with_newlines(self):
        inst = self._make_one()
        assert inst.deserialize('line\n\r') == 'line\n\r'

    def test_deserialize_non_valid_no_str(self):
        inst = self._make_one()
        with raises(colander.Invalid):
            inst.deserialize(1)


class PasswordUnitTest(unittest.TestCase):

    def _make_one(self):
        from adhocracy_core.schema import Password
        return Password()

    def test_serialize_valid_emtpy(self):
        inst = self._make_one()
        assert inst.deserialize() == colander.drop

    def test_deserialize_valid_emtpy(self):
        inst = self._make_one()
        assert inst.serialize() == ''

    def test_deserialize_valid_with_newlines(self):
        inst = self._make_one()
        assert inst.deserialize('line\n\r') == 'line\n\r'

    def test_deserialize_non_valid_no_str(self):
        inst = self._make_one()
        with raises(colander.Invalid):
            inst.deserialize(1)


class DateTimeUnitTest(unittest.TestCase):

    def _make_one(self, **kwargs):
        from adhocracy_core.schema import DateTime
        return DateTime(**kwargs)

    def test_create(self):
        from colander import DateTime
        inst = self._make_one()
        assert inst.schema_type is DateTime
        assert isinstance(inst.default, colander.deferred)
        assert isinstance(inst.missing, colander.deferred)

    def test_deserialize_empty(self):
        inst = self._make_one()
        with raises(colander.Invalid):
            inst.deserialize()

    def test_bind_and_deserialize_empty(self):
        from datetime import datetime
        inst = self._make_one().bind()
        result = inst.deserialize()
        assert isinstance(result, datetime)
        assert result.tzname() == 'UTC'

    def test_serialize_empty(self):
        inst = self._make_one()
        assert inst.serialize() is colander.null

    def test_bind_and_serialize_empty(self):
        from datetime import datetime
        inst = self._make_one().bind()
        result = inst.serialize()
        # we want an iso 8601 string with the current datetime
        today = datetime.utcnow().strftime('%Y-%m-%d')
        assert today in result
