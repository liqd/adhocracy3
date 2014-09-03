import unittest
from unittest.mock import Mock

from pyramid import testing
import colander
from pytest import raises


############
#  helper  #
############

def add_node_binding(node, context=None):
    node.bindings = dict()
    node.bindings['context'] = context
    return node

###########
#  tests  #
###########

class AdhocracySchemaNodeUnitTest(unittest.TestCase):

    def _make_one(self, *args, **kwargs):
        from adhocracy.schema import AdhocracySchemaNode
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
        from adhocracy.schema import Name
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
        from adhocracy.schema import Email
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
        from adhocracy.schema import TimeZoneName
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
        from adhocracy.schema import AbsolutePath
        return AbsolutePath()

    def test_valid(self):
        inst = self._make_one()
        assert inst.validator(inst, '/blu.ABC_12-3/aaa') is None

    def test_non_valid(self):
        inst = self._make_one()
        with raises(colander.Invalid):
            inst.validator(inst, 'blu.ABC_12-3')


class ResourceObjectUnitTests(unittest.TestCase):

    def _make_one(self):
        from adhocracy.schema import ResourceObject
        return ResourceObject()

    def setUp(self):
        self.context = testing.DummyResource()
        self.child = testing.DummyResource()

    def test_serialize_colander_null(self):
        inst = self._make_one()
        result = inst.serialize(None, colander.null)
        assert result == colander.null

    def test_serialize_value_location_aware(self):
        inst = self._make_one()
        self.context['child'] = self.child
        node = add_node_binding(colander.Mapping(), context=self.context)
        result = inst.serialize(node, self.child)
        assert result == '/child'

    def test_serialize_value_not_location_aware(self):
        inst = self._make_one()
        del self.child.__parent__
        del self.child.__name__
        node = add_node_binding(colander.Mapping(), context=self.context)
        with raises(colander.Invalid):
            inst.serialize(node, self.child)

    def test_serialize_value_location_aware_without_parent_and_name(self):
        inst = self._make_one()
        node = add_node_binding(colander.Mapping(), context=self.context)
        result = inst.serialize(node, self.child)
        assert result == '/'

    def test_deserialize_value_null(self):
        inst = self._make_one()
        node = colander.Mapping()
        result = inst.deserialize(node, colander.null)
        assert result == colander.null

    def test_deserialize_value_valid_path(self):
        inst = self._make_one()
        self.context['child'] = self.child
        node = add_node_binding(colander.Mapping(), context=self.context)
        result = inst.deserialize(node, '/child')
        assert result == self.child

    def test_deserialize_value_invalid_path(self):
        inst = self._make_one()
        node = add_node_binding(colander.Mapping(), context=self.context)
        with raises(colander.Invalid):
            inst.deserialize(node, '/wrong_child')


class ReferenceUnitTest(unittest.TestCase):

    def _make_one(self, **kwargs):
        from adhocracy.schema import Reference
        return Reference(**kwargs)

    def setUp(self):
        self.context = testing.DummyResource()
        self.target = testing.DummyResource()
        self.child = testing.DummyResource()

    def test_missing(self):
        inst = self._make_one()
        assert inst.missing == colander.drop

    def test_with_backref(self):
        inst = self._make_one(backref=True)
        assert inst.backref

    def test_without_backref(self):
        inst = self._make_one()
        assert inst.backref is False

    def test_valid_interface(self):
        from zope.interface import alsoProvides
        inst = self._make_one()
        isheet = inst.reftype.getTaggedValue('target_isheet')
        alsoProvides(self.target, isheet)
        inst = add_node_binding(node=inst, context=self.context)
        assert inst.validator(inst, self.target) is None

    def test_nonvalid_interface(self):
        inst = self._make_one()
        inst = add_node_binding(node=inst, context=self.context)
        with raises(colander.Invalid):
            inst.validator(inst, self.target)

    def test_serialize_value_location_aware(self):
        inst = self._make_one()
        self.context['child'] = self.child
        inst = add_node_binding(node=inst, context=self.context)
        result = inst.serialize(self.child)
        assert result == '/child'

    def test_deserialize_value_valid_path(self):
        from zope.interface import alsoProvides
        inst = self._make_one()
        self.context['child'] = self.child
        inst = add_node_binding(node=inst, context=self.context)
        isheet = inst.reftype.getTaggedValue('target_isheet')
        alsoProvides(self.child, isheet)
        result = inst.deserialize('/child')
        assert result == self.child

    def test_deserialize_value_invalid_path(self):
        inst = self._make_one()
        inst = add_node_binding(node=inst, context=self.context)
        with raises(colander.Invalid):
            inst.deserialize('/wrong_child')


class PathListSetUnitTest(unittest.TestCase):

    def _make_one(self):
        from adhocracy.schema import ListOfUniquePaths
        return ListOfUniquePaths()

    def setUp(self):
        self.context = testing.DummyResource()
        self.child = testing.DummyResource()

    def test_serialize_colander_null(self):
        inst = self._make_one()
        result = inst.serialize(None, colander.null)
        assert result == colander.null

    def test_serialize_noniterable(self):
        inst = self._make_one()
        with raises(colander.Invalid):
            inst.serialize(None, None)

    def test_serialize_string(self):
        inst = self._make_one()
        node = add_node_binding(colander.Mapping(), context=self.context)
        with raises(colander.Invalid):
            inst.serialize(node, 'blah')

    def test_serialize_iterable(self):
        inst = self._make_one()
        node = add_node_binding(colander.Mapping(), context=self.context)
        result = inst.serialize(node, [])
        assert result == []

    def test_serialize_value_location_aware(self):
        inst = self._make_one()
        self.context['child'] = self.child
        node = add_node_binding(colander.Mapping(), context=self.context)
        result = inst.serialize(node, [self.child])
        assert result == ['/child']

    def test_serialize_value_not_location_aware(self):
        inst = self._make_one()
        node = add_node_binding(colander.Mapping(), context=self.context)
        del self.child.__parent__
        del self.child.__name__
        node = add_node_binding(colander.Mapping(), context=self.context)
        with raises(colander.Invalid):
            inst.serialize(node, [self.child])

    def test_serialize_value_location_aware_without_parent_and_name(self):
        inst = self._make_one()
        node = add_node_binding(colander.Mapping(), context=self.context)
        result = inst.serialize(node, [self.child])
        assert result == ['/']

    def test_deserialize_value_null(self):
        inst = self._make_one()
        node = colander.Mapping()
        result = inst.deserialize(node, colander.null)
        assert result == colander.null

    def test_deserialize_value_valid_path(self):
        inst = self._make_one()
        self.context['child'] = self.child
        node = add_node_binding(colander.Mapping(), context=self.context)
        result = inst.deserialize(node, ['/child'])
        assert result == [self.child]

    def test_deserialize_value_valid_path_with_duplicates(self):
        inst = self._make_one()
        self.context['child'] = self.child
        node = add_node_binding(colander.Mapping(), context=self.context)
        result = inst.deserialize(node, ['/child', '/child'])
        assert result == [self.child]

    def test_deserialize_value_none_valid_path(self):
        inst = self._make_one()
        node = add_node_binding(colander.Mapping(), context=self.context)
        with raises(colander.Invalid):
            inst.deserialize(node, ['/wrong_child'])


class PathSetUnitTest(unittest.TestCase):

    def _make_one(self):
        from adhocracy.schema import SetOfPaths
        return SetOfPaths()

    def setUp(self):
        self.context = testing.DummyResource()
        self.child = testing.DummyResource()

    def test_serialize_colander_null(self):
        inst = self._make_one()
        result = inst.serialize(None, colander.null)
        assert result == colander.null

    def test_serialize_noniterable(self):
        inst = self._make_one()
        with raises(colander.Invalid):
            inst.serialize(None, None)

    def test_serialize_iterable(self):
        inst = self._make_one()
        node = add_node_binding(colander.Mapping(), context=self.context)
        result = inst.serialize(node, set())
        assert result == []

    def test_serialize_value_location_aware(self):
        inst = self._make_one()
        self.context['child'] = self.child
        node = add_node_binding(colander.Mapping(), context=self.context)
        result = inst.serialize(node, {self.child})
        assert result == ['/child']

    def test_serialize_value_not_location_aware(self):
        inst = self._make_one()
        node = add_node_binding(colander.Mapping(), context=self.context)
        del self.child.__parent__
        del self.child.__name__
        node = add_node_binding(colander.Mapping(), context=self.context)
        with raises(colander.Invalid):
            inst.serialize(node, {self.child})

    def test_serialize_value_location_aware_without_parent_and_name(self):
        inst = self._make_one()
        node = add_node_binding(colander.Mapping(), context=self.context)
        result = inst.serialize(node, {self.child})
        assert result == ['/']

    def test_deserialize_value_valid_path(self):
        inst = self._make_one()
        self.context['child'] = self.child
        node = add_node_binding(colander.Mapping(), context=self.context)
        result = inst.deserialize(node, ['/child'])
        assert result == {self.child}

    def test_deserialize_value_none_valid_path(self):
        inst = self._make_one()
        node = add_node_binding(colander.Mapping(), context=self.context)
        with raises(colander.Invalid):
            inst.deserialize(node, ['/wrong_child'])


class ReferenceSetSchemaNodeUnitTest(unittest.TestCase):

    def _make_one(self):
        from adhocracy.schema import ListOfUniqueReferences
        return ListOfUniqueReferences()

    def setUp(self):
        self.context = testing.DummyResource()
        self.target = testing.DummyResource()

    def test_default(self):
        inst = self._make_one()
        assert inst.default == []

    def test_missing(self):
        inst = self._make_one()
        assert inst.missing == colander.drop

    def test_valid_interface(self):
        from zope.interface import alsoProvides
        inst = self._make_one()
        isheet = inst.reftype.getTaggedValue('target_isheet')
        alsoProvides(self.target, isheet)
        inst = add_node_binding(node=inst, context=self.context)
        assert inst.validator(inst, [self.target]) is None

    def test_nonvalid_interface(self):
        inst = self._make_one()
        inst = add_node_binding(node=inst, context=self.context)
        with raises(colander.Invalid):
            inst.validator(inst, [self.target])


class StringUnitTest(unittest.TestCase):

    def _make_one(self):
        from adhocracy.schema import SingleLine
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
        from adhocracy.schema import Text
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
        from adhocracy.schema import Password
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
        from adhocracy.schema import DateTime
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
