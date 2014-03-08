from unittest.mock import patch
from zope.interface import Interface
from pyramid import testing

import colander
import pytest
import unittest


############
#  helper  #
############

class InterfaceY(Interface):

    """Useless Interface for testing"""


@patch('substanced.objectmap.ObjectMap', autospec=True)
def make_folder_with_objectmap(dummyobjectmap=None):
    folder = testing.DummyResource()
    folder.__objectmap__ = dummyobjectmap.return_value
    return folder


def add_node_binding(node, context=None, request=None):
    request = request if request is not None else testing.DummyRequest()
    context = context if context is not None else testing.DummyResource()
    node.bindings = dict()
    node.bindings['context'] = context
    node.bindings['request'] = request
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


class PathSetUnitTest(unittest.TestCase):

    def make_one(self):
        from . import PathSet
        return PathSet()

    def test_serialize_valid_null(self):
        inst = self.make_one()
        result = inst.serialize(None, colander.null)
        assert result == colander.null

    def test_serialize_valid_non_null(self):
        inst = self.make_one()
        context = make_folder_with_objectmap()
        context.__objectmap__.path_for.return_value = ('', 'o1')
        node = add_node_binding(colander.Mapping(), context=context)
        result = inst.serialize(node, [1])
        assert result == ['/o1']

    def test_serialize_non_valid_noniterable(self):
        inst = self.make_one()
        with pytest.raises(colander.Invalid):
            inst.serialize(None, None)

    def test_serialize_non_valid_non_null(self):
        inst = self.make_one()
        context = make_folder_with_objectmap()
        context.__objectmap__.path_for.return_value = None
        node = add_node_binding(colander.Mapping(), context=context)
        with pytest.raises(colander.Invalid):
            inst.serialize(node, [0])

    def test_deserialize_valid_non_null(self):
        inst = self.make_one()
        context = make_folder_with_objectmap()
        context.__objectmap__.objectid_for.return_value = 1
        node = add_node_binding(colander.Mapping(), context=context)
        result = inst.deserialize(node, ['/o1'])
        assert result == [1]

    def test_deserialize_non_valid_non_null(self):
        inst = self.make_one()
        context = make_folder_with_objectmap()
        context.__objectmap__.objectid_for.return_value = None
        node = add_node_binding(colander.Mapping(), context=context)
        with pytest.raises(colander.Invalid):
            inst.deserialize(node, ['/wrong_path'])


class ReferenceSetSchemaNodeUnitTest(unittest.TestCase):

    def make_one(self):
        from . import ReferenceSetSchemaNode
        return ReferenceSetSchemaNode()

    def test_default(self):
        inst = self.make_one()
        assert inst.default == []

    def test_missing(self):
        inst = self.make_one()
        assert inst.missing == []

    def test_valid_interface(self):
        from zope.interface import alsoProvides
        inst = self.make_one()
        isheet = inst.reftype.getTaggedValue('target_isheet')
        context = make_folder_with_objectmap()
        alsoProvides(context, isheet)
        context.__objectmap__.object_for.return_value = context
        inst = add_node_binding(node=inst, context=context)
        assert inst.validator(inst, [1]) is None

    def test_nonvalid_interface(self):
        inst = self.make_one()
        context = make_folder_with_objectmap()
        context.__objectmap__.object_for.return_value = context
        inst = add_node_binding(node=inst, context=context)
        with pytest.raises(colander.Invalid):
            inst.validator(inst, [1])
