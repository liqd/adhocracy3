from adhocracy.properties.interfaces import IProperty
from pyramid.testing import DummyRequest
from substanced.interfaces import IFolder
from unittest.mock import patch
from zope.interface import (
    Interface,
    implementer,
    taggedValue,
)
import colander
import pytest

############
#  helper  #
############


@implementer(IFolder)
class DummyFolder(dict):
    interfaces = []


class InterfaceY(Interface):
    pass


class IPropertyA(IProperty):
    taggedValue("schema", "adhocracy.properties.test_.CountSchema")


class IPropertyB(IProperty):
    taggedValue("schema", "adhocracy.properties.test_.CountSchema")


class CountSchema(colander.MappingSchema):
    count = colander.SchemaNode(colander.Int(),
                                default=0,
                                missing=colander.drop)


class IPropertyZ(IProperty):
    taggedValue("schema",
                "adhocracy.properties.test_.CountSchemaMissingDefault")


class CountSchemaMissingDefault(colander.MappingSchema):
    count = colander.SchemaNode(colander.Int(),
                                missing=colander.drop)


class IPropertyY(IProperty):
    taggedValue("schema",
                "adhocracy.properties.test_.CountSchemaMissingMissing")


class CountSchemaMissingMissing(colander.MappingSchema):
    count = colander.SchemaNode(colander.Int(),
                                default=0)


class IExtendPropertyB(IPropertyB):
    taggedValue("schema",
                "adhocracy.properties.test_.ExtendCountSchema")
    taggedValue("key", IPropertyB.__identifier__)


class ExtendCountSchema(CountSchema):
    newattribute = colander.SchemaNode(colander.String(),
                                       default="",
                                       missing=colander.drop)


################################
#  test ResourcePropertySheet  #
################################

def _resourcepropertysheet_make_one(*args):
    from . import ResourcePropertySheetAdapter
    return ResourcePropertySheetAdapter(*args)


@patch('substanced.objectmap.ObjectMap', autospec=True)
def _make_folder_with_objectmap(dummyobjectmap=None):
    folder = DummyFolder()
    folder.__objectmap__ = dummyobjectmap.return_value
    return folder


def test_resourcepropertysheet_create_valid():
    from adhocracy.interfaces import IResourcePropertySheet
    from zope.interface.verify import verifyObject
    context = DummyFolder()
    request = None
    iproperty = IPropertyB
    inst = _resourcepropertysheet_make_one(context, request, iproperty)
    assert inst.context == context
    assert inst.request == request
    assert isinstance(inst.schema, CountSchema)
    assert inst.key == IPropertyB.__identifier__
    assert verifyObject(IResourcePropertySheet, inst) is True


def test_resourcepropertysheet_create_non_valid_non_mapping_context():
    with pytest.raises(AssertionError):
        _resourcepropertysheet_make_one(object(), None, IPropertyB)


def test_resourcepropertysheet_create_non_valid_non_iproperty_iface():
    with pytest.raises(AssertionError):
        _resourcepropertysheet_make_one(DummyFolder(), None, InterfaceY)


@patch('adhocracy.schema.ReferenceSetSchemaNode', autospec=True)
def test_resourcepropertysheet_create_references(dummy_reference_node=None):
    node = dummy_reference_node.return_value
    node.name = "references"
    inst = _resourcepropertysheet_make_one(DummyFolder(), None, IPropertyB)
    inst.schema.children.append(node)
    assert inst._references == {"references": IPropertyB.__identifier__ + ":references"}


def test_resourcepropertysheet_get_empty():
    inst = _resourcepropertysheet_make_one(DummyFolder(), None, IPropertyB)
    assert inst.get() == {"count": 0}


def test_resourcepropertysheet_get_non_empty():
    inst = _resourcepropertysheet_make_one(DummyFolder(), None, IPropertyB)
    inst._data["count"] = 11
    assert inst.get() == {"count": 11}


def test_resourcepropertysheet_set_valid():
    inst = _resourcepropertysheet_make_one(DummyFolder(), None, IPropertyB)
    assert inst.set({"count": 11}) is True
    assert inst.get() == {"count": 11}


def test_resourcepropertysheet_set_valid_empty():
    inst = _resourcepropertysheet_make_one(DummyFolder(), None, IPropertyB)
    assert inst.set({}) is False
    assert inst.get() == {"count": 0}


def test_resourcepropertysheet_set_valid_omit_str():
    inst = _resourcepropertysheet_make_one(DummyFolder(), None, IPropertyB)
    assert inst.set({"count": 11}, omit="count") is False


def test_resourcepropertysheet_set_valid_omit_tuple():
    inst = _resourcepropertysheet_make_one(DummyFolder(), None, IPropertyB)
    assert inst.set({"count": 11}, omit=("count",)) is False


def test_resourcepropertysheet_set_valid_omit_wrong_key():
    inst = _resourcepropertysheet_make_one(DummyFolder(), None, IPropertyB)
    assert inst.set({"count": 11}, omit=("wrongkey",)) is True


@patch('adhocracy.schema.ReferenceSetSchemaNode', autospec=True)
def test_resourcepropertysheet_set_valid_references(dummy_reference_node=None):
    node = dummy_reference_node.return_value
    node.name = "references"
    node.deserialize.return_value = []
    context = _make_folder_with_objectmap()
    inst = _resourcepropertysheet_make_one(context, None, IPropertyB)
    inst.schema.children.append(node)
    inst.set({"references": [1]})
    om = context.__objectmap__
    reftype = inst._references["references"]
    assert om.connect.assert_called_once_with(context, 1, reftype) is None


def test_resourcepropertysheet_get_cstruct_empty():
    inst = _resourcepropertysheet_make_one(DummyFolder(), None, IPropertyB)
    assert inst.get_cstruct() == {"count": "0"}


def test_resourcepropertysheet_get_cstruct_non_empty():
    inst = _resourcepropertysheet_make_one(DummyFolder(), None, IPropertyB)
    inst._data["count"] = 11
    assert inst.get_cstruct() == {"count": "11"}


def test_resourcepropertysheet_set_cstruct_valid():
    inst = _resourcepropertysheet_make_one(DummyFolder(), None, IPropertyB)
    inst.set_cstruct({"count": "11"})
    assert inst.get_cstruct() == {"count": "11"}


def test_resourcepropertysheet_set_cstruct_valid_empty():
    inst = _resourcepropertysheet_make_one(DummyFolder(), None, IPropertyB)
    inst.set_cstruct({})
    assert inst.get_cstruct() == {"count": "0"}


def test_resourcepropertysheet_set_cstruct_valid_with_name_conflicts():
    context = DummyFolder()
    inst1 = _resourcepropertysheet_make_one(context, None, IPropertyB)
    inst1.set_cstruct({"count": "1"})
    inst2 = _resourcepropertysheet_make_one(context, None, IPropertyA)
    inst2.set_cstruct({"count": "2"})
    assert inst1.get_cstruct() == {"count": "1"}
    assert inst2.get_cstruct() == {"count": "2"}


def test_resourcepropertysheet_set_cstruct_valid_readonly():
    inst = _resourcepropertysheet_make_one(DummyFolder(), None, IPropertyB)
    inst.schema.children[0].readonly = True
    inst.set_cstruct({"count": "1"})
    assert inst.get_cstruct() == {"count": "0"}


def test_resourcepropertysheet_get_cstruct_non_valid_missing_default_value():
    with pytest.raises(AssertionError):
        _resourcepropertysheet_make_one(DummyFolder(), None, IPropertyZ)


def test_resourcepropertysheet_get_cstruct_non_valid_missing_missing_value():
    with pytest.raises(AssertionError):
        _resourcepropertysheet_make_one(DummyFolder(), None, IPropertyY)


def test_resourcepropertysheet_set_cstruct_non_valid_wrong_type():
    inst = _resourcepropertysheet_make_one(DummyFolder(), None, IPropertyB)
    with pytest.raises(colander.Invalid):
        inst.set_cstruct({"count": "wrongnumber"})


def test_resourcepropertysheet_set_cstruct_non_valid_required():
    inst = _resourcepropertysheet_make_one(DummyFolder(), None, IPropertyB)
    inst.schema.children[0].required_ = True
    #FIXME: the attriute required is automatically set without "missing" value
    with pytest.raises(colander.Invalid):
        inst.set_cstruct({})


def test_resourcepropertysheet_set_cstruct_non_valid_required_and_readonly():
    inst = _resourcepropertysheet_make_one(DummyFolder(), None, IPropertyB)
    inst.schema.children[0].required_ = True
    inst.schema.children[0].readonly = True
    with pytest.raises(AssertionError):
        inst.set_cstruct({})


############################################
#  test includeme and adapter registration #
############################################

def _includeme_make_one(config, context, request, iface):
    from adhocracy.interfaces import IResourcePropertySheet
    from zope.interface import alsoProvides
    request = DummyRequest()
    alsoProvides(context, iface)
    inst = config.registry.getMultiAdapter((context, request, iface),
                                           IResourcePropertySheet)
    return inst


def _includeme_register_propertysheet_adapter(config, iface):
    from adhocracy.interfaces import IResourcePropertySheet
    from adhocracy.properties.interfaces import IIProperty
    from adhocracy.properties import ResourcePropertySheetAdapter
    from pyramid.interfaces import IRequest
    from zope.interface import alsoProvides
    alsoProvides(iface, IIProperty)
    config.registry.registerAdapter(ResourcePropertySheetAdapter,
                                    (iface, IRequest, IIProperty),
                                    IResourcePropertySheet)


def test_includeme_register_ipropertysheet_adapter_inheritance(config):
    _includeme_register_propertysheet_adapter(config, IExtendPropertyB)
    context = DummyFolder()
    inst_extend = _includeme_make_one(config, context,
                                      DummyRequest(), IExtendPropertyB)
    assert IPropertyB.providedBy(context)
    assert IExtendPropertyB.providedBy(context)
    assert "count" in inst_extend.get()
    assert "newattribute" in inst_extend.get()


def test_includeme_register_ipropertysheet_adapter_extend(config):
    _includeme_register_propertysheet_adapter(config, IPropertyB)
    _includeme_register_propertysheet_adapter(config, IExtendPropertyB)
    context = DummyFolder()
    inst_extend = _includeme_make_one(config, context,
                                      DummyRequest(), IExtendPropertyB)
    inst = _includeme_make_one(config, context,
                               DummyRequest(), IPropertyB)
    inst_extend.set({"count": 1})
    assert inst_extend.key == inst.key
    assert inst.get() == {"count": 1}
    assert inst_extend.get() == {"count": 1, "newattribute": ""}
    inst.set({"count": 2})
    assert inst_extend.get() == {"count": 2, "newattribute": ""}
    assert inst.get() == {"count": 2}


def test_includeme_register_ipropertysheet_adapter_iname(config):
    from adhocracy.properties.interfaces import IName
    config.include("adhocracy.properties")
    inst = _includeme_make_one(config, DummyFolder(), DummyRequest(), IName)
    assert inst.iface is IName


def test_includeme_register_ipropertysheet_adapter_inamereadonly(config):
    from adhocracy.properties.interfaces import INameReadOnly
    config.include("adhocracy.properties")
    inst = _includeme_make_one(config, DummyFolder(), DummyRequest(),
                               INameReadOnly)
    assert inst.iface is INameReadOnly


def test_includeme_register_ipropertysheet_adapter_iversions(config):
    from adhocracy.properties.interfaces import IVersions
    config.include("adhocracy.properties")
    inst = _includeme_make_one(config, DummyFolder(), DummyRequest(),
                               IVersions)
    assert inst.iface is IVersions


def test_includeme_register_ipropertysheet_adapter_itags(config):
    from adhocracy.properties.interfaces import ITags
    config.include("adhocracy.properties")
    inst = _includeme_make_one(config, DummyFolder(), DummyRequest(), ITags)
    assert inst.iface is ITags


def test_includeme_register_ipropertysheet_adapter_iversionable(config):
    from adhocracy.properties.interfaces import IVersionable
    config.include("adhocracy.properties")
    inst = _includeme_make_one(config, DummyFolder(), DummyRequest(),
                               IVersionable)
    assert inst.iface is IVersionable


def test_includeme_register_ipropertysheet_adapter_ipool(config):
    from adhocracy.properties.interfaces import IPool
    config.include("adhocracy.properties")
    inst = _includeme_make_one(config, DummyFolder(), DummyRequest(), IPool)
    assert inst.iface is IPool
