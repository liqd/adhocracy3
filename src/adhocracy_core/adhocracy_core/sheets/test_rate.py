from unittest.mock import Mock

from pyramid import testing
from pytest import fixture
from pytest import raises
from pytest import mark
import colander

from adhocracy_core.sheets.rate import IRateable




@fixture
def integration(config):
    config.include('adhocracy_core.content')
    config.include('adhocracy_core.catalog')
    config.include('adhocracy_core.sheets.rate')


def _make_rateable(provides=IRateable):
    return testing.DummyResource(__provides__=provides)


class TestRateableSheet:

    @fixture
    def inst(self, pool, service):
        pool['rates'] = service
        from adhocracy_core.sheets.rate import rateable_meta
        return rateable_meta.sheet_class(rateable_meta, pool)

    def test_create(self, inst):
        from adhocracy_core.sheets import AnnotationRessourceSheet
        from adhocracy_core.sheets.rate import IRateable
        from adhocracy_core.sheets.rate import RateableSchema
        assert isinstance(inst, AnnotationRessourceSheet)
        assert inst.meta.isheet == IRateable
        assert inst.meta.schema_class == RateableSchema
        assert inst.meta.create_mandatory is False

    def test_get_empty(self, inst):
        post_pool = inst.context['rates']
        assert inst.get() == {'post_pool': post_pool,
                              'rates': [],
                              }


class TestRateSheet:

    @fixture
    def meta(self):
        from adhocracy_core.sheets.rate import rate_meta
        return rate_meta

    def test_create(self, meta, context):
        from adhocracy_core.sheets.rate import IRate
        from adhocracy_core.sheets.rate import RateSchema
        from adhocracy_core.sheets import AnnotationRessourceSheet
        inst = meta.sheet_class(meta, context)
        assert isinstance(inst, AnnotationRessourceSheet)
        assert inst.meta.isheet == IRate
        assert inst.meta.schema_class == RateSchema
        assert inst.meta.create_mandatory

    def test_get_empty(self, meta, context):
        inst = meta.sheet_class(meta, context)
        assert inst.get() == {'subject': None,
                              'object': None,
                              'rate': 0,
                              }


class DummyQuery:

    def __init__(self, result=[]):
        self.result = result

    def __iand__(self, other):
        return self

    def execute(self, **kwargs):
        return self.result


class DummyIndex:

    def __init__(self, result=[]):
        self.result = result

    def eq(self, *args, **kwargs):
        return DummyQuery(self.result)

    def noteq(self, *args, **kwargs):
        return DummyQuery(self.result)


@mark.usefixtures('integration')
class TestRateSchema:

    @fixture
    def schema_with_mock_ensure_rate(self, request_, context):
        from adhocracy_core.sheets.rate import RateSchema
        schema = RateSchema().bind(request=request_, context=context)
        schema._ensure_rate_is_unique = Mock()
        return schema

    @fixture
    def subject(self, monkeypatch):
        from adhocracy_core.sheets import rate
        from adhocracy_core.sheets.rate import ICanRate
        subject = testing.DummyResource(__provides__=ICanRate)
        mock_get_user = Mock(return_value=subject)
        monkeypatch.setattr(rate, 'get_user', mock_get_user)
        return subject

    def test_deserialize_valid(self, context, schema_with_mock_ensure_rate,
                               subject):
        context['subject'] = subject
        object = _make_rateable()
        context['object'] = object
        data = {'subject': '/subject', 'object': '/object', 'rate': '1'}
        assert schema_with_mock_ensure_rate.deserialize(data) == {
            'subject': subject, 'object': object, 'rate': 1}

    def test_deserialize_valid_minus_one(self, context,
                                         schema_with_mock_ensure_rate,
                                         subject):
        context['subject'] = subject
        object = _make_rateable()
        context['object'] = object
        data = {'subject': '/subject', 'object': '/object', 'rate': '-1'}
        assert schema_with_mock_ensure_rate.deserialize(data) == {
            'subject': subject, 'object': object, 'rate': -1}

    def test_deserialize_invalid_rate(self, context,
                                      schema_with_mock_ensure_rate, subject):
        context['subject'] = subject
        object = _make_rateable()
        context['object'] = object
        data = {'subject': '/subject', 'object': '/object', 'rate': '77'}
        with raises(colander.Invalid):
            schema_with_mock_ensure_rate.deserialize(data)

    def test_deserialize_invalid_subject(self, context,
                                         schema_with_mock_ensure_rate):
        subject = testing.DummyResource()
        context['subject'] = subject
        object = _make_rateable()
        context['object'] = object
        data = {'subject': '/subject', 'object': '/object', 'rate': '0'}
        with raises(colander.Invalid):
            schema_with_mock_ensure_rate.deserialize(data)

    def test_deserialize_invalid_subject_missing(self, context,
                                                 schema_with_mock_ensure_rate):
        object = _make_rateable()
        context['object'] = object
        data = {'subject': '', 'object': '/object', 'rate': '0'}
        with raises(colander.Invalid):
            schema_with_mock_ensure_rate.deserialize(data)

    def test_deserialize_subject_isnt_current_user(
            self, context, monkeypatch, schema_with_mock_ensure_rate):
        from adhocracy_core.sheets import rate
        from adhocracy_core.sheets.rate import ICanRate
        subject = testing.DummyResource(__provides__=ICanRate)
        user = testing.DummyResource(__provides__=ICanRate)
        mock_get_user = Mock(return_value=user)
        monkeypatch.setattr(rate, 'get_user', mock_get_user)
        context['subject'] = subject
        object = _make_rateable()
        context['object'] = object
        data = {'subject': '/subject', 'object': '/object', 'rate': '0'}
        with raises(colander.Invalid):
            schema_with_mock_ensure_rate.deserialize(data)

    def test_deserialize_invalid_object(self, context,
                                        schema_with_mock_ensure_rate,
                                        subject):
        context['subject'] = subject
        object = testing.DummyResource()
        context['object'] = object
        data = {'subject': '/subject', 'object': '/object', 'rate': '0'}
        with raises(colander.Invalid):
            schema_with_mock_ensure_rate.deserialize(data)

    def test_deserialize_invalid_object_missing(self, context,
                                        schema_with_mock_ensure_rate, subject):
        context['subject'] = subject
        data = {'subject': '/subject', 'object': '', 'rate': '0'}
        with raises(colander.Invalid):
            schema_with_mock_ensure_rate.deserialize(data)

    def test_deserialize_valid_likeable(self, context,
                                        schema_with_mock_ensure_rate,
                                        subject):
        from adhocracy_core.sheets.rate import ILikeable
        context['subject'] = subject
        object = _make_rateable(ILikeable)
        context['object'] = object
        data = {'subject': '/subject', 'object': '/object', 'rate': '1'}
        assert schema_with_mock_ensure_rate.deserialize(data) == {
            'subject': subject, 'object': object, 'rate': 1}

    def test_deserialize_invalid_rate_with_likeable(
            self, context, schema_with_mock_ensure_rate, subject):
        from adhocracy_core.sheets.rate import ILikeable
        context['subject'] = subject
        object = _make_rateable(ILikeable)
        context['object'] = object
        data = {'subject': '/subject', 'object': '/object', 'rate': '-1'}
        with raises(colander.Invalid):
            schema_with_mock_ensure_rate.deserialize(data)

    def test_ensure_rate_is_unique_ok(self, monkeypatch, request_,
                                      context, subject):
        from adhocracy_core.sheets.rate import RateSchema
        from adhocracy_core.sheets import rate
        mock_find_catalog = Mock(return_value={'reference': DummyIndex(),
                                               'path': DummyIndex()})
        monkeypatch.setattr(rate, 'find_catalog', mock_find_catalog)
        schema = RateSchema().bind(request=request_, context=context)
        object = _make_rateable()
        node = Mock()
        value = {'subject': subject, 'object': object, 'rate': '1'}
        result = schema._ensure_rate_is_unique(node, value, request_)
        assert result is None

    def test_ensure_rate_is_unique_error(self, monkeypatch, request_,
                                         context, subject):
        from adhocracy_core.sheets.rate import RateSchema
        from adhocracy_core.sheets import rate
        from adhocracy_core.utils import named_object
        mock_find_catalog = Mock(
            return_value={'reference': DummyIndex(['dummy']),
                          'path': DummyIndex()})
        monkeypatch.setattr(rate, 'find_catalog', mock_find_catalog)
        schema = RateSchema().bind(request=request_, context=context)
        object = _make_rateable()
        node = Mock()
        node.children = [named_object('object')]
        value = {'subject': subject, 'object': object, 'rate': '1'}
        with raises(colander.Invalid):
            schema._ensure_rate_is_unique(node, value, request_)


@mark.usefixtures('integration')
class TestRateValidators:

    def test_rateable_rate_validator(self, registry):
        from adhocracy_core.interfaces import IRateValidator
        rateable = _make_rateable()
        validator = registry.getAdapter(rateable, IRateValidator)
        assert validator.validate(1) is True
        assert validator.validate(0) is True
        assert validator.validate(-1) is True
        assert validator.validate(2) is False
        assert validator.validate(-2) is False

    def test_likeable_rate_validator(self, registry):
        from adhocracy_core.interfaces import IRateValidator
        from adhocracy_core.sheets.rate import ILikeable
        rateable = _make_rateable(ILikeable)
        validator = registry.getAdapter(rateable, IRateValidator)
        assert validator.validate(1) is True
        assert validator.validate(0) is True
        assert validator.validate(-1) is False
        assert validator.validate(2) is False


@mark.usefixtures('integration')
def test_includeme_register_rate_sheet(config, context):
    from adhocracy_core.sheets.rate import IRate
    from adhocracy_core.utils import get_sheet
    context = testing.DummyResource(__provides__=IRate)
    inst = get_sheet(context, IRate)
    assert inst.meta.isheet is IRate



