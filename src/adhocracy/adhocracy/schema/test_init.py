import unittest

from pyramid import testing
import colander
import pytest


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

class NameUnitTest(unittest.TestCase):

    def setUp(self):
        self.parent = testing.DummyResource()
        self.context = testing.DummyResource(__parent__=self.parent)

    def _make_one(self):
        from adhocracy.schema import Name
        inst = Name()
        return inst.bind(context=self.context)

    def test_valid(self):
        inst = self._make_one()
        assert inst.deserialize('blu.ABC_12-3')

    def test_no_valid_missing_context_binding(self):
        inst = self._make_one()
        inst_no_context = inst.bind()
        with pytest.raises(AttributeError):
            inst_no_context.deserialize('blu.ABC_123')

    def test_no_valid_parent_is_none(self):
        inst = self._make_one()
        self.context.__parent__ = None
        with pytest.raises(colander.Invalid):
            inst.deserialize('blu.ABC_123')

    def test_non_valid_empty(self):
        inst = self._make_one()
        with pytest.raises(colander.Invalid):
            inst.validator(inst, '')

    def test_non_valid_to_long(self):
        inst = self._make_one()
        with pytest.raises(colander.Invalid):
            inst.validator(inst, 'x' * 101)

    def test_non_valid_wrong_characters(self):
        inst = self._make_one()
        with pytest.raises(colander.Invalid):
            inst.validator(inst, 'ä')

    def test_non_valid_not_unique(self):
        inst = self._make_one()
        self.context.__parent__['name'] = testing.DummyRequest()
        with pytest.raises(colander.Invalid):
            inst.validator(inst, 'name')


class EmailUnitTest(unittest.TestCase):

    def make_one(self):
        from adhocracy.schema import Email
        return Email()

    def test_valid(self):
        inst = self.make_one()
        assert inst.validator(inst, 'test@test.de') is None

    def test_non_valid(self):
        inst = self.make_one()
        with pytest.raises(colander.Invalid):
            inst.validator(inst, 'wrong')


class TimeZoneNameUnitTest(unittest.TestCase):

    def make_one(self):
        from adhocracy.schema import TimeZoneName
        return TimeZoneName()

    def test_valid(self):
        inst = self.make_one()
        assert inst.validator(inst, 'Europe/Berlin') is None

    def test_non_valid(self):
        inst = self.make_one()
        with pytest.raises(colander.Invalid):
            inst.validator(inst, 'wrong')

    def test_default(self):
        inst = self.make_one()
        assert inst.default == 'UTC'


class AbsolutePath(unittest.TestCase):

    def make_one(self):
        from . import AbsolutePath
        return AbsolutePath()

    def test_valid(self):
        inst = self.make_one()
        assert inst.validator(inst, '/blu.ABC_12-3/aaa') is None

    def test_non_valid(self):
        inst = self.make_one()
        with pytest.raises(colander.Invalid):
            inst.validator(inst, 'blu.ABC_12-3')


class ResourceObjectUnitTests(unittest.TestCase):

    def make_one(self):
        from adhocracy.schema import ResourceObject
        return ResourceObject()

    def setUp(self):
        self.context = testing.DummyResource()
        self.child = testing.DummyResource()

    def test_serialize_colander_null(self):
        inst = self.make_one()
        result = inst.serialize(None, colander.null)
        assert result == colander.null

    def test_serialize_value_location_aware(self):
        inst = self.make_one()
        self.context['child'] = self.child
        node = add_node_binding(colander.Mapping(), context=self.context)
        result = inst.serialize(node, self.child)
        assert result == '/child'

    def test_serialize_value_not_location_aware(self):
        inst = self.make_one()
        del self.child.__parent__
        del self.child.__name__
        node = add_node_binding(colander.Mapping(), context=self.context)
        with pytest.raises(colander.Invalid):
            inst.serialize(node, self.child)

    def test_serialize_value_location_aware_without_parent_and_name(self):
        inst = self.make_one()
        node = add_node_binding(colander.Mapping(), context=self.context)
        result = inst.serialize(node, self.child)
        assert result == '/'

    def test_deserialize_value_null(self):
        inst = self.make_one()
        node = colander.Mapping()
        result = inst.deserialize(node, colander.null)
        assert result == colander.null

    def test_deserialize_value_valid_path(self):
        inst = self.make_one()
        self.context['child'] = self.child
        node = add_node_binding(colander.Mapping(), context=self.context)
        result = inst.deserialize(node, '/child')
        assert result == self.child

    def test_deserialize_value_invalid_path(self):
        inst = self.make_one()
        node = add_node_binding(colander.Mapping(), context=self.context)
        with pytest.raises(colander.Invalid):
            inst.deserialize(node, ['/wrong_child'])


class PathListSetUnitTest(unittest.TestCase):

    def make_one(self):
        from . import ListOfUniquePaths
        return ListOfUniquePaths()

    def setUp(self):
        self.context = testing.DummyResource()
        self.child = testing.DummyResource()

    def test_serialize_colander_null(self):
        inst = self.make_one()
        result = inst.serialize(None, colander.null)
        assert result == colander.null

    def test_serialize_noniterable(self):
        inst = self.make_one()
        with pytest.raises(colander.Invalid):
            inst.serialize(None, None)

    def test_serialize_iterable(self):
        inst = self.make_one()
        node = add_node_binding(colander.Mapping(), context=self.context)
        result = inst.serialize(node, [])
        assert result == []

    def test_serialize_value_location_aware(self):
        inst = self.make_one()
        self.context['child'] = self.child
        node = add_node_binding(colander.Mapping(), context=self.context)
        result = inst.serialize(node, [self.child])
        assert result == ['/child']

    def test_serialize_value_not_location_aware(self):
        inst = self.make_one()
        node = add_node_binding(colander.Mapping(), context=self.context)
        del self.child.__parent__
        del self.child.__name__
        node = add_node_binding(colander.Mapping(), context=self.context)
        with pytest.raises(colander.Invalid):
            inst.serialize(node, [self.child])

    def test_serialize_value_location_aware_without_parent_and_name(self):
        inst = self.make_one()
        node = add_node_binding(colander.Mapping(), context=self.context)
        result = inst.serialize(node, [self.child])
        assert result == ['/']

    def test_deserialize_value_null(self):
        inst = self.make_one()
        node = colander.Mapping()
        result = inst.deserialize(node, colander.null)
        assert result == colander.null

    def test_deserialize_value_valid_path(self):
        inst = self.make_one()
        self.context['child'] = self.child
        node = add_node_binding(colander.Mapping(), context=self.context)
        result = inst.deserialize(node, ['/child'])
        assert result == [self.child]

    def test_deserialize_value_valid_path_with_duplicates(self):
        inst = self.make_one()
        self.context['child'] = self.child
        node = add_node_binding(colander.Mapping(), context=self.context)
        result = inst.deserialize(node, ['/child', '/child'])
        assert result == [self.child]

    def test_deserialize_value_none_valid_path(self):
        inst = self.make_one()
        node = add_node_binding(colander.Mapping(), context=self.context)
        with pytest.raises(colander.Invalid):
            inst.deserialize(node, ['/wrong_child'])


class PathSetUnitTest(unittest.TestCase):

    def make_one(self):
        from . import SetOfPaths
        return SetOfPaths()

    def setUp(self):
        self.context = testing.DummyResource()
        self.child = testing.DummyResource()

    def test_serialize_colander_null(self):
        inst = self.make_one()
        result = inst.serialize(None, colander.null)
        assert result == colander.null

    def test_serialize_noniterable(self):
        inst = self.make_one()
        with pytest.raises(colander.Invalid):
            inst.serialize(None, None)

    def test_serialize_iterable(self):
        inst = self.make_one()
        node = add_node_binding(colander.Mapping(), context=self.context)
        result = inst.serialize(node, set())
        assert result == []

    def test_serialize_value_location_aware(self):
        inst = self.make_one()
        self.context['child'] = self.child
        node = add_node_binding(colander.Mapping(), context=self.context)
        result = inst.serialize(node, {self.child})
        assert result == ['/child']

    def test_serialize_value_not_location_aware(self):
        inst = self.make_one()
        node = add_node_binding(colander.Mapping(), context=self.context)
        del self.child.__parent__
        del self.child.__name__
        node = add_node_binding(colander.Mapping(), context=self.context)
        with pytest.raises(colander.Invalid):
            inst.serialize(node, {self.child})

    def test_serialize_value_location_aware_without_parent_and_name(self):
        inst = self.make_one()
        node = add_node_binding(colander.Mapping(), context=self.context)
        result = inst.serialize(node, {self.child})
        assert result == ['/']

    def test_deserialize_value_valid_path(self):
        inst = self.make_one()
        self.context['child'] = self.child
        node = add_node_binding(colander.Mapping(), context=self.context)
        result = inst.deserialize(node, ['/child'])
        assert result == {self.child}

    def test_deserialize_value_none_valid_path(self):
        inst = self.make_one()
        node = add_node_binding(colander.Mapping(), context=self.context)
        with pytest.raises(colander.Invalid):
            inst.deserialize(node, ['/wrong_child'])


class ReferenceSetSchemaNodeUnitTest(unittest.TestCase):

    def make_one(self):
        from . import ListOfUniqueReferences
        return ListOfUniqueReferences()

    def setUp(self):
        self.context = testing.DummyResource()
        self.target = testing.DummyResource()

    def test_default(self):
        inst = self.make_one()
        assert inst.default == []

    def test_missing(self):
        inst = self.make_one()
        assert inst.missing == colander.drop

    def test_valid_interface(self):
        from zope.interface import alsoProvides
        inst = self.make_one()
        isheet = inst.reftype.getTaggedValue('target_isheet')
        alsoProvides(self.target, isheet)
        inst = add_node_binding(node=inst, context=self.context)
        assert inst.validator(inst, [self.target]) is None

    def test_nonvalid_interface(self):
        inst = self.make_one()
        inst = add_node_binding(node=inst, context=self.context)
        with pytest.raises(colander.Invalid):
            inst.validator(inst, [self.target])
