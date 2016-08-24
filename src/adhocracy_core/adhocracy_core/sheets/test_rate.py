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


@fixture
def user():
    return testing.DummyResource(__name__='user')


@fixture
def anonymous():
    return testing.DummyResource(__name__='anonymous')


@fixture
def mock_get_anonymous(mocker, anonymous):
    mock = mocker.patch('adhocracy_core.resources.principal'
                        '.get_system_user_anonymous',
                        return_value=anonymous)
    return mock

def _make_rateable(provides=IRateable):
    return testing.DummyResource(__provides__=provides)


class TestRateableSheet:

    @fixture
    def meta(self):
        from .rate import rateable_meta
        return rateable_meta

    @fixture
    def inst(self, pool, meta, service):
        pool['rates'] = service
        return meta.sheet_class(meta, pool, None)

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
        assert inst.get() == {'post_pool': post_pool}


class TestRateSheet:

    @fixture
    def meta(self):
        from adhocracy_core.sheets.rate import rate_meta
        return rate_meta

    @fixture
    def inst(self, meta, context, registry):
        return meta.sheet_class(meta, context, registry)

    def test_meta(self, meta):
        from adhocracy_core.sheets.rate import IRate
        from adhocracy_core.sheets.rate import RateSchema
        from adhocracy_core.sheets import AttributeResourceSheet
        assert issubclass(meta.sheet_class, AttributeResourceSheet)
        assert meta.isheet == IRate
        assert meta.schema_class == RateSchema
        assert meta.create_mandatory

    def test_create(self, meta, context):
        inst = meta.sheet_class(meta, context, None)
        assert inst

    def test_get_empty(self, inst):
        assert inst.get() == {'subject': None,
                              'object': None,
                              'rate': 0,
                              }

    def test_validators(self, mocker, inst, kw):
        from . import rate
        validate_value = mocker.patch.object(rate, 'create_validate_rate_value')
        validate_subject = mocker.patch.object(rate, 'create_validate_subject')
        validate_unique = mocker.patch.object(rate,
                                              'create_validate_is_unique')
        validators = inst.schema.validator(inst.schema, kw)

        validate_value.assert_called_with(kw['registry'])
        validate_subject.assert_called_with(kw['request'])
        validate_unique.assert_called_with(kw['context'], kw['request'])

    def test_preparer(self, mocker, inst, kw):
        from .rate import deferred_anonymize_rate_subject
        assert inst.schema.preparer == deferred_anonymize_rate_subject

    @mark.usefixtures('integration')
    def test_includeme_register(self, meta, registry):
        context = testing.DummyResource(__provides__=meta.isheet)
        assert registry.content.get_sheet(context, meta.isheet)


class TestDeferredAnonymizeRateSubject:

    def call_fut(self, *args):
        from .rate import deferred_anonymize_rate_subject
        return deferred_anonymize_rate_subject(*args)

    def test_ignore_if_no_anonymized_request(self, node, kw, user):
        preparer = self.call_fut(node, kw)
        assert preparer({'subject': user}) == {'subject': user}

    def test_replace_subject_with_anonymous_if_anonymized_request(
            self, node, kw, user, anonymous, mock_get_anonymous):
        kw['request'].user = anonymous
        kw['request'].anonymized_user = user
        preparer = self.call_fut(node, kw)
        assert preparer({'subject': user}) == {'subject': anonymous}


class TestCreateValidateRateValue:

    @fixture
    def registry(self, registry_with_content):
        return registry_with_content

    def call_fut(self, *args):
        from .rate import create_validate_rate_value
        return create_validate_rate_value(*args)

    def test_ignore_if_validation_passes(self, node, registry):
        from pyramid.registry import Registry
        from .rate import IRateValidator
        mock_validator = Mock()
        mock_validator.validate.return_value = True
        registry.getAdapter = Mock(spec=Registry.getAdapter,
                                   return_value=mock_validator)
        object_ = testing.DummyResource()
        validator = self.call_fut(registry)

        validator(node, {'object': object_,
                         'rate': 1})

        mock_validator.validate.assert_called_with(1)
        assert registry.getAdapter.call_args[0] == (object_, IRateValidator)

    def test_raise_if_validation_not_passes(self, node, registry):
        from pyramid.registry import Registry
        mock_validator = Mock()
        mock_validator.validate.return_value = False
        registry.getAdapter = Mock(spec=Registry.getAdapter,
                                   return_value=mock_validator)
        object_ = testing.DummyResource()
        validator = self.call_fut(registry)
        with raises(colander.Invalid):
            node['rate'] = Mock()  # needed create the Error
            validator(node,
                      {'object': object_,
                       'rate': 'WRONG'})


class TestCreateValidateSubject:

    def call_fut(self, *args):
        from .rate import create_validate_subject
        return create_validate_subject(*args)

    def test_ignore_if_subject_is_authenticated_user(self, node, request_, user):
        request_.user = user
        validator = self.call_fut(request_)
        assert validator(node, {'subject': user}) is None

    def test_raise_if_subject_is_not_authenticated_user(
            self, node, request_, user):
        request_.user = user
        other_user = testing.DummyResource()
        validator = self.call_fut(request_)
        with raises(colander.Invalid):
            node['subject'] = other_user  # used to generate the error message
            validator(node,  {'subject': other_user})

    def test_raise_if_subject_is_not_authenticated_user_and_anonymized_request(
            self, node, request_, user, anonymous):
        request_.user = anonymous
        request_.anonymized_user = user
        other_user = testing.DummyResource()
        validator = self.call_fut(request_)
        with raises(colander.Invalid):
            node['subject'] = other_user  # used to generate the error message
            validator(node,  {'subject': other_user})

    def test_ignore_if_subject_is_anonymous_user_and_anonymized_request(
            self, node, request_, user, anonymous):
        request_.user = anonymous
        request_.anonymized_user = user
        validator = self.call_fut(request_)
        assert validator(node, {'subject': anonymous}) is None


class TestCreateValidateIsUnique:

    def call_fut(self, *args):
        from .rate import create_validate_is_unique
        return create_validate_is_unique(*args)

    @fixture
    def registry(self, registry_with_content):
        return registry_with_content

    @fixture
    def mock_versions_sheet(self, registry, mock_sheet):
        mock_sheet.get.return_value = {'elements': []}
        registry.content.get_sheet = Mock(return_value=mock_sheet)
        return mock_sheet

    @fixture
    def mock_catalogs(self, mock_catalogs, monkeypatch):
        from . import rate
        monkeypatch.setattr(rate, 'find_service', lambda x, y: mock_catalogs)
        return mock_catalogs

    @fixture
    def mock_anonymized_creator(self, mocker):
        return mocker.patch('adhocracy_core.sheets.rate.get_anonymized_creator',
                            return_value='')

    @fixture
    def value(self):
        return {'subject': testing.DummyResource(),
                'object': testing.DummyResource(),
                'rate': '1'}
    @fixture
    def request_(self, request_, user):
        request_.user = user
        return request_

    def test_ignore_if_no_equal_rates(
            self, node, context, request_, value, query, mock_catalogs,
            anonymous, mock_get_anonymous, version, search_result):
        from adhocracy_core.interfaces import Reference
        from .rate import IRate
        mock_catalogs.search.side_effect =\
            [search_result,
             search_result._replace(elements=[version]),
             ]
        validator = self.call_fut(context, request_)
        assert validator(node, value) is None
        assert mock_catalogs.search.call_args_list[0][0][0] == query._replace(
                references=(Reference(None, IRate, 'subject', request_.user),
                            Reference(None, IRate, 'object', value['object'])),
                resolve=True)
        assert mock_catalogs.search.call_args_list[1][0][0] == query._replace(
                references=(Reference(None, IRate, 'subject', anonymous),
                            Reference(None, IRate, 'object', value['object'])),
                resolve=True)

    def test_ignore_if_older_versions_of_same_rate(
            self, node, context, request_, value, search_result, mock_catalogs,
            mock_versions_sheet):
        old_version = testing.DummyResource()
        mock_catalogs.search.side_effect =\
            [search_result._replace(elements=[old_version]),
             search_result]
        mock_versions_sheet.get.return_value = \
            {'elements': [old_version]}

        validator = self.call_fut(context, request_)
        assert validator(node, value) is None

    def test_raise_if_non_anonymized_equal_rates(
            self, node, context, request_, value, search_result, mock_catalogs,
            mock_versions_sheet, version):
        mock_catalogs.search.side_effect =\
            [search_result._replace(elements=[version]),
             search_result]
        validator = self.call_fut(context, request_)
        with raises(colander.Invalid):
            node['object'] = Mock()
            validator(node, value)

    def test_raise_if_anonymized_equal_rates(
            self, node, context, request_, value, search_result, mock_catalogs,
            mock_versions_sheet, mock_anonymized_creator, version):
        mock_catalogs.search.side_effect =\
            [search_result,
             search_result._replace(elements=[version])]
        mock_anonymized_creator.return_value = 'user'

        validator = self.call_fut(context, request_)
        with raises(colander.Invalid):
            node['object'] = Mock()
            validator(node, value)


@mark.usefixtures('integration')
class TestRateValidators:

    def test_validate_rateable_rate_validator(self, registry):
        from adhocracy_core.interfaces import IRateValidator
        rateable = _make_rateable()
        validator = registry.getAdapter(rateable, IRateValidator)
        assert validator.validate(1) is True
        assert validator.validate(0) is True
        assert validator.validate(-1) is True
        assert validator.validate(2) is False
        assert validator.validate(-2) is False

    def test_validate_likeable_rate_validator(self, registry):
        from adhocracy_core.interfaces import IRateValidator
        from adhocracy_core.sheets.rate import ILikeable
        rateable = _make_rateable(ILikeable)
        validator = registry.getAdapter(rateable, IRateValidator)
        assert validator.validate(1) is True
        assert validator.validate(0) is True
        assert validator.validate(-1) is False
        assert validator.validate(2) is False

    def test_helpfull_error_message(self, registry):
        from adhocracy_core.interfaces import IRateValidator
        from adhocracy_core.sheets.rate import ILikeable
        rateable = _make_rateable(ILikeable)
        validator = registry.getAdapter(rateable, IRateValidator)
        assert validator.helpful_error_message() == \
               "rate must be one of (1, 0)"
