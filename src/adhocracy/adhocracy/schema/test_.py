from substanced.interfaces import IFolder
from unittest.mock import patch
from zope.interface import (
    Interface,
    implementer,
)

import colander
import pytest

############
#  helper  #
############

@implementer(IFolder)
class DummyFolder(dict):

    """Dummy dictionary with IFolder interface"""

    interfaces = []


class InterfaceY(Interface):

    """Useless Interface for testing"""


@patch('substanced.objectmap.ObjectMap', autospec=True)
def _make_folder_with_objectmap(dummyobjectmap=None):
    folder = DummyFolder()
    folder.__objectmap__ = dummyobjectmap.return_value
    return folder


def _add_node_binding(node, context=None, request=None):
    from pyramid import testing
    request = request if request is not None else testing.DummyRequest()
    context = context if context is not None else testing.DummyResource()
    node.bindings = dict()
    node.bindings["context"] = context
    node.bindings["request"] = request
    return node

##################
#  test PathSet  #
##################

def _pathset_make_one():
    from . import PathSet
    return PathSet()


def test_pathset_serialize_valid_null():
    inst = _pathset_make_one()
    result = inst.serialize(None, colander.null)
    assert result == colander.null


def test_pathset_serialize_valid_non_null():
    inst = _pathset_make_one()
    context = _make_folder_with_objectmap()
    context.__objectmap__.path_for.return_value = ("", "o1")
    node = _add_node_binding(colander.Mapping(), context=context)
    result = inst.serialize(node, [1])
    assert result == ["/o1"]


def test_pathset_serialize_non_valid_noniterable():
    inst = _pathset_make_one()
    with pytest.raises(colander.Invalid):
        inst.serialize(None, None)


def test_pathset_serialize_non_valid_non_null():
    inst = _pathset_make_one()
    context = _make_folder_with_objectmap()
    context.__objectmap__.path_for.return_value = None
    node = _add_node_binding(colander.Mapping(), context=context)
    with pytest.raises(colander.Invalid):
        inst.serialize(node, [0])


def test_pathset_deserialize_valid_non_null():
    inst = _pathset_make_one()
    context = _make_folder_with_objectmap()
    context.__objectmap__.objectid_for.return_value = 1
    node = _add_node_binding(colander.Mapping(), context=context)
    result = inst.deserialize(node, ["/o1"])
    assert result == [1]


def test_pathset_deserialize_non_valid_non_null():
    inst = _pathset_make_one()
    context = _make_folder_with_objectmap()
    context.__objectmap__.objectid_for.return_value = None
    node = _add_node_binding(colander.Mapping(), context=context)
    with pytest.raises(colander.Invalid):
        inst.deserialize(node, ["/wrong_path"])

#################################
#  test ReferenceSetSchemaNode  #
#################################

def _referencesetschemanode_make_one():
    from . import ReferenceSetSchemaNode
    return ReferenceSetSchemaNode()


def test_referencesetschemanode_default():
    inst = _referencesetschemanode_make_one()
    assert inst.default == []


def test_referencesetschemanode_missing():
    inst = _referencesetschemanode_make_one()
    assert inst.missing == []


def test_referencesetschemanode_valid_interface():
    inst = _referencesetschemanode_make_one()
    context = _make_folder_with_objectmap()
    context.__objectmap__.object_for.return_value = lambda *arg: context
    inst = _add_node_binding(node=inst, context=context)
    assert inst.validator(inst, [1]) is None


def test_referencesetschemanode_non_valid_interface():
    inst = _referencesetschemanode_make_one()
    inst.interfaces = [InterfaceY]
    context = _make_folder_with_objectmap()
    context.__objectmap__.object_for.return_value = lambda *arg: context
    inst = _add_node_binding(node=inst, context=context)
    with pytest.raises(colander.Invalid):
        inst.validator(inst, [1])
