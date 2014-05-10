from unittest.mock import patch
from pyramid import testing

import colander
import pytest
import unittest


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

class IdentifierUnitTest(unittest.TestCase):

    def make_one(self):
        from . import Identifier
        return Identifier()

    def test_valid(self):
        inst = self.make_one()
        assert inst.validator(inst, 'blu.ABC_12-3') is None

    def test_non_valid(self):
        inst = self.make_one()
        with pytest.raises(colander.Invalid):
            inst.validator(inst, 'blu./ABC_12-3')


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


class PathListSetUnitTest(unittest.TestCase):

    def make_one(self):
        from . import PathListSet
        return PathListSet()

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
        from . import PathSet
        return PathSet()

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
        result = inst.serialize(node, set([self.child]))
        assert result == ['/child']

    def test_serialize_value_not_location_aware(self):
        inst = self.make_one()
        node = add_node_binding(colander.Mapping(), context=self.context)
        del self.child.__parent__
        del self.child.__name__
        node = add_node_binding(colander.Mapping(), context=self.context)
        with pytest.raises(colander.Invalid):
            inst.serialize(node, set([self.child]))

    def test_serialize_value_location_aware_without_parent_and_name(self):
        inst = self.make_one()
        node = add_node_binding(colander.Mapping(), context=self.context)
        result = inst.serialize(node, set([self.child]))
        assert result == ['/']

    def test_deserialize_value_valid_path(self):
        inst = self.make_one()
        self.context['child'] = self.child
        node = add_node_binding(colander.Mapping(), context=self.context)
        result = inst.deserialize(node, ['/child'])
        assert result == set([self.child])

    def test_deserialize_value_none_valid_path(self):
        inst = self.make_one()
        node = add_node_binding(colander.Mapping(), context=self.context)
        with pytest.raises(colander.Invalid):
            inst.deserialize(node, ['/wrong_child'])


class ReferenceSetSchemaNodeUnitTest(unittest.TestCase):

    def make_one(self):
        from . import ReferenceListSetSchemaNode
        return ReferenceListSetSchemaNode()

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
