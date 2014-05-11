import pytest

################
#  test utils  #
################


def test_diff_dict():
    from . import diff_dict
    old = {'foo': 5, 'bar': 6, 'kaz': 8}
    new = {'bar': 6, 'baz': 7, 'kaz': 9, 'faz': 10}
    diff = diff_dict(old, new)
    assert diff == ({'baz', 'faz'}, {'kaz'}, {'foo'})


def test_diff_dict_omit():
    from . import diff_dict
    old = {'foo': 5, 'bar': 6, 'kaz': 8}
    new = {'bar': 6, 'baz': 7, 'kaz': 9, 'faz': 10}
    diff = diff_dict(old, new, omit=('foo',))
    assert diff == ({'baz', 'faz'}, {'kaz'}, set())


def test_strip_optional_prefix():
    from . import strip_optional_prefix
    assert strip_optional_prefix('footile', 'foo') == 'tile'
    assert strip_optional_prefix('futile', 'foo') == 'futile'
    assert strip_optional_prefix('footile', 'oot') == 'footile'
    assert strip_optional_prefix('footile', 'ile') == 'footile'
    assert strip_optional_prefix('', 'foo') == ''
    assert strip_optional_prefix('footile', '') == 'footile'
    assert strip_optional_prefix(' footile ', 'foo') == ' footile '
    assert strip_optional_prefix('foo', 'foo') == ''
    assert strip_optional_prefix('foo', 'foot') == 'foo'


def test_get_resource_interface_multiple_provided():
    from . import get_resource_interface
    from adhocracy.interfaces import IResource
    from zope.interface import directlyProvides
    from pyramid.testing import DummyResource
    context = DummyResource()

    class IA(IResource):
        pass

    class IB(IResource):
        pass

    directlyProvides(context, IA, IB)
    assert get_resource_interface(context) == IA


def test_get_resource_interface_none_provided():
    from . import get_resource_interface
    from pyramid.testing import DummyResource
    context = DummyResource()
    result = get_resource_interface(context)
    assert result is None


def test_get_sheet_interfaces_multiple_provided():
    from . import get_sheet_interfaces
    from adhocracy.interfaces import ISheet
    from adhocracy.interfaces import IResource
    from pyramid.testing import DummyResource

    class IA(ISheet):
        pass

    class IB(ISheet):
        pass

    context = DummyResource(__provides__=(IResource, IA, IB))
    assert get_sheet_interfaces(context) == [IA, IB]


def test_get_sheet_interfaces_none_provided():
    from . import get_sheet_interfaces
    from adhocracy.interfaces import IResource
    from pyramid.testing import DummyResource
    context = DummyResource(__provides__=IResource)
    assert get_sheet_interfaces(context) == []


def test_get_all_taggedvalues_inheritance():
    from zope.interface import taggedValue
    from zope.interface import Interface
    from . import get_all_taggedvalues

    class IA(Interface):
        taggedValue('a', 'a')

    class IB(IA):
        pass

    metadata_ib = get_all_taggedvalues(IB)
    assert 'a' in metadata_ib


def test_get_all_taggedvalues_iitem_normalize_dotted_string_to_callable():
    from . import get_all_taggedvalues
    from adhocracy.interfaces import IResource
    from adhocracy.interfaces import IItem
    from zope.interface import taggedValue
    from zope.interface import Interface

    class IA(IItem):
        taggedValue('item_type', Interface.__identifier__)
        taggedValue('content_class', Interface.__identifier__)
        taggedValue('after_creation', {Interface.__identifier__})
        taggedValue('basic_sheets', {Interface.__identifier__})
        taggedValue('extended_sheets', {Interface.__identifier__})
        taggedValue('element_types',
                    {Interface.__identifier__})

    metadata = get_all_taggedvalues(IA)
    assert 'after_creation' in IResource.getTaggedValueTags()
    assert metadata['after_creation'] == {Interface}
    assert 'content_class' in IResource.getTaggedValueTags()
    assert metadata['content_class'] == Interface
    assert 'item_type' in IItem.getTaggedValueTags()
    assert metadata['item_type'] == Interface
    assert 'basic_sheets' in IItem.getTaggedValueTags()
    assert metadata['basic_sheets'] == {Interface}
    assert 'extended_sheets' in IResource.getTaggedValueTags()
    assert metadata['extended_sheets'] == {Interface}
    assert 'element_types' in IItem.getTaggedValueTags()
    assert metadata['element_types'] == {Interface}


def test_to_dotted_name_module():
    from . import to_dotted_name
    import os
    assert to_dotted_name(os.walk) == 'os.walk'


def test_to_dotted_name_dotted_string():
    from . import to_dotted_name
    assert to_dotted_name('os.walk') == 'os.walk'

#FIXME tests for get_sheet, get_all_sheets are missing
