from pyramid import testing
from pytest import fixture
from pytest import mark
from pytest import raises
from unittest import mock


@fixture
def request_():
    return testing.DummyRequest()


@fixture
def mock_strategy():
    return mock.Mock()


def _create_and_register_mock_strategy(registry, view_or_method):
    from zope.interface import Interface
    from pyramid.interfaces import IRequest
    from adhocracy_core.interfaces import IHTTPCacheStrategy
    mock_strategy = mock.Mock()
    registry.registerAdapter(mock_strategy, (Interface, IRequest),
                             IHTTPCacheStrategy, view_or_method)
    return mock_strategy


def test_get_cache_mode_return_default_mode(registry):
    from adhocracy_core.interfaces import HTTPCacheMode
    from . import _get_cache_mode
    assert _get_cache_mode(registry) == HTTPCacheMode.no_cache


def test_get_cache_mode_return_mode_in_settings(registry):
    from adhocracy_core.interfaces import HTTPCacheMode
    from . import _get_cache_mode
    registry.settings['adhocracy_core.caching.http.mode'] = \
        HTTPCacheMode.with_proxy_cache.name
    assert _get_cache_mode(registry) == HTTPCacheMode.with_proxy_cache


def test_get_cache_mode_raise_if_wrong_mode_in_settings(registry):
    from . import _get_cache_mode
    registry.settings['adhocracy_core.caching.http.mode'] = 'WRONG'
    with raises(KeyError):
        _get_cache_mode(registry)


def test_get_cache_strategy_for_viewname(registry, context, request_):
    from . import _get_cache_strategy
    mock_strategy = _create_and_register_mock_strategy(registry, 'view_name')
    request_.view_name = 'view_name'
    assert _get_cache_strategy(context, request_) is mock_strategy.return_value


def test_get_cache_strategy_for_methodname(registry, context, request_):
    from . import _get_cache_strategy
    mock_strategy = _create_and_register_mock_strategy(registry, 'method_name')
    request_.method = 'method_name'
    assert _get_cache_strategy(context, request_) is mock_strategy.return_value


def test_get_cache_strategy_dont_get_disabled_view_names(registry, context, request_):
    from . import _get_cache_strategy
    _create_and_register_mock_strategy(registry, 'POST')
    request_.method_name = 'POST'
    assert _get_cache_strategy(context, request_) is None


def test_register_cache_strategy(registry, context, request_, mock_strategy):
    from adhocracy_core.interfaces import IResource
    from adhocracy_core.interfaces import IHTTPCacheStrategy
    from . import register_cache_strategy
    register_cache_strategy(mock_strategy, IResource, registry,
                                        'view_or_method_name')
    assert registry.getMultiAdapter((context, request_), IHTTPCacheStrategy,
                                    'view_or_method_name')


def test_register_cache_strategy_dont_register_disabled_views(registry, mock_strategy):
    from adhocracy_core.interfaces import IResource
    from adhocracy_core.exceptions import ConfigurationError
    from . import register_cache_strategy
    with raises(ConfigurationError):
        register_cache_strategy(mock_strategy, IResource, registry, 'POST')
    with raises(ConfigurationError):
        register_cache_strategy(mock_strategy, IResource, registry, 'PATCH')


class TestHTTPCacheStrategyBaseAdapter:

    def get_class(self):
        from . import HTTPCacheStrategyBaseAdapter
        return HTTPCacheStrategyBaseAdapter

    @fixture
    def inst(self, context, request_):
        return self.get_class()(context, request_)

    @fixture
    def dummyinst(self):
        dummyinst = mock.MagicMock(spec=self.get_class())
        return dummyinst

    def test_create(self, inst, context, request_):
        from zope.interface.verify import verifyObject
        from adhocracy_core.interfaces import IHTTPCacheStrategy
        assert inst.context is context
        assert inst.request is request_
        assert verifyObject(IHTTPCacheStrategy, inst)
        assert inst.browser_max_age == 0
        assert inst.proxy_max_age == 0
        assert inst.last_modified
        assert inst.etags == ()
        assert inst.vary == ()

    def test_set_do_not_cache(self, inst, request_):
        inst.set_do_not_cache()
        assert request_.response.headers['expires'].startswith('Wed, 31 Dec 1969')
        assert request_.response.headers['pragma'] == 'no-cache'
        assert request_.response.headers['Cache-Control'] == 'no-cache'

    def test_set_cache_control_without_proxy(self, inst, request_):
        inst.browser_max_age = 1
        inst.set_cache_control_without_proxy()
        assert request_.response.headers['Cache-control'] ==\
            'max-age=1, must-revalidate'

    def test_set_cache_control_with_proxy(self, inst, request_):
        inst.browser_max_age = 1
        inst.proxy_max_age = 1
        inst.set_cache_control_with_proxy()
        assert request_.response.headers['Cache-control'] ==\
               'max-age=1, proxy-revalidate, s-maxage=1'

    def test_set_last_modified_context_without_mod_date(self, inst, request_):
        inst.set_last_modified()
        assert 'last-modified' not in request_.response.headers

    def test_set_last_modified_context_with_mod_date(self, inst, request_):
        from datetime import datetime
        inst.context.modification_date = datetime(2015, 1, 1)
        inst.set_last_modified()
        assert request_.response.headers['last-modified'].startswith('Thu, 01')

    def test_set_last_modified_context_with_mod_date_but_last_modified_is_false(
            self, inst, request_):
        from datetime import datetime
        inst.context.modification_date = datetime(2015, 1, 1)
        inst.last_modified = False
        inst.set_last_modified()
        assert 'last-modified' not in request_.response.headers

    def test_set_last_modified_context_with_mod_date_last_modified_is_true(
            self, inst, request_):
        from datetime import datetime
        inst.context.modification_date = datetime(2015, 1, 1)
        inst.last_modified = True
        inst.set_last_modified()
        assert request_.response.headers['last-modified'].startswith('Thu, 01')

    def test_set_debug_info(self, inst, request_):
        from adhocracy_core.interfaces import HTTPCacheMode
        inst.set_debug_info(HTTPCacheMode.no_cache)
        assert request_.response.headers['X-Caching-Mode'] == 'no_cache'
        assert request_.response.headers['X-Caching-Strategy'] ==\
            inst.__class__.__name__

    def test_set_etag_etags_are_empty(self, inst, request_):
        inst.etags = tuple()
        inst.set_etag()
        assert request_.response.etag is None
        assert 'etag' not in request_.response.headers

    def test_set_etag_etags_lists_functions(self, inst, request_):
        def etag_data_dummy_function(context, request):
            return 'tag'
        inst.etags = (etag_data_dummy_function, etag_data_dummy_function)
        inst.set_etag()
        assert request_.response.headers['etag'] == '"tag|tag"'

    def test_set_vary(self, inst, request_):
        inst.vary = ('XX', 'BB')
        inst.set_vary()
        assert request_.response.headers['Vary'] == 'XX, BB'

    def test_set_cache_headers_for_mode_no_cache(self, dummyinst):
        from adhocracy_core.interfaces import HTTPCacheMode
        fut = self.get_class().set_cache_headers_for_mode
        fut(dummyinst, HTTPCacheMode.no_cache)
        assert dummyinst.set_debug_info.called
        assert dummyinst.set_do_not_cache.called

    def test_set_cache_headers_for_mode_without_proxy_cache(self, dummyinst):
        from adhocracy_core.interfaces import HTTPCacheMode
        fut = self.get_class().set_cache_headers_for_mode
        fut(dummyinst, HTTPCacheMode.without_proxy_cache)
        assert dummyinst.set_debug_info.called
        assert dummyinst.set_cache_control_without_proxy.called
        assert dummyinst.set_last_modified.called
        assert dummyinst.set_etag.called

    def test_set_cache_headers_for_mode_with_proxy_cache(self, dummyinst):
        from adhocracy_core.interfaces import HTTPCacheMode
        fut = self.get_class().set_cache_headers_for_mode
        fut(dummyinst, HTTPCacheMode.with_proxy_cache)
        assert dummyinst.set_debug_info.called
        assert dummyinst.set_cache_control_with_proxy.called
        assert dummyinst.set_last_modified.called
        assert dummyinst.set_etag.called
        assert dummyinst.set_vary.called


def test_etag_userid_without_authenticated_user(context, request_):
    from . import etag_userid
    request = testing.DummyResource(authenticated_userid=None)
    assert etag_userid(context, request) == 'None'


def test_etag_userid_with_authenticated_user(context, request_):
    from . import etag_userid
    request = testing.DummyResource(authenticated_userid='userid')
    assert etag_userid(context, request) == 'userid'


class TestHTTPCacheStrategyWeakAdapter:

    @fixture
    def inst(self):
        from . import HTTPCacheStrategyWeakAdapter
        return HTTPCacheStrategyWeakAdapter(None, None)

    def test_create(self, inst):
        from zope.interface.verify import verifyObject
        from adhocracy_core.interfaces import IHTTPCacheStrategy
        from . import etag_backrefs, etag_descendants, etag_modified, \
            etag_userid
        assert verifyObject(IHTTPCacheStrategy, inst)
        assert inst.browser_max_age == 0
        assert inst.proxy_max_age == 31104000
        assert inst.vary == ('X-User-Path', 'X-User-Token')
        assert inst.etags == (etag_backrefs, etag_descendants, etag_modified,
                              etag_userid)


@fixture()
def integration(config):
    config.include('adhocracy_core.caching')


@mark.usefixtures('integration')
class TestIntegrationCaching:

    @staticmethod
    def dummyview(context, request):
        from . import set_cache_header
        from cornice.util import _JSONError
        if 'error' in request.params:
            raise _JSONError({})
        set_cache_header(context, request)
        return {}

    @fixture
    def config(self, config):
        config.include('cornice')
        from adhocracy_core.interfaces import IResource
        config.add_view(self.dummyview, renderer='json', request_method='GET',
                        context=IResource, name='no_strategy_registered')
        config.add_view(self.dummyview, renderer='json', request_method='GET',
                        context=IResource)
        config.add_view(self.dummyview, renderer='json', request_method='OPTIONS',
                        context=IResource)
        return config

    @fixture
    def app_user(self, config, context):
        from webtest import TestApp
        app = config.make_wsgi_app()
        app.root_factory = lambda x: context
        return TestApp(app)

    def test_registered_strategies_iresource(self, context, registry, request_):
        from adhocracy_core.interfaces import IHTTPCacheStrategy
        from . import HTTPCacheStrategyWeakAdapter
        strategies = dict(registry.getAdapters((context, request_),
                                               IHTTPCacheStrategy))
        assert isinstance(strategies['GET'], HTTPCacheStrategyWeakAdapter)
        assert isinstance(strategies['OPTIONS'], HTTPCacheStrategyWeakAdapter)
        assert isinstance(strategies['HEAD'], HTTPCacheStrategyWeakAdapter)

    def test_registered_strategy_modifies_headers(self, app_user):
        resp = app_user.get('/', status=200)
        assert resp.headers['X-Caching-Strategy'].startswith('HTTPCacheStrat')

    def test_mode_default_is_no_cache(self, app_user):
        resp = app_user.get('/', status=200)
        assert resp.headers['X-Caching-Mode'] == 'no_cache'

    def test_strategy_and_error_is_raised_no_header_is_modified(self, app_user):
        resp = app_user.get('/?error=True', status=400)
        assert 'X-Caching-Strategy' not in resp.headers

    def test_strategy_not_registered_no_header_is_modified(self, app_user):
        resp = app_user.get('/no_strategy_registered', status=200)
        assert 'X-Caching-Strategy' not in resp.headers

    def test_strategy_with_mode_without_proxy_cache_get(self, app_user, registry):
        from adhocracy_core.interfaces import HTTPCacheMode
        registry.settings['adhocracy_core.caching.http.mode'] =\
             HTTPCacheMode.without_proxy_cache.name
        resp = app_user.get('/', status=200)
        assert resp.headers['Cache-control'] == 'max-age=0, must-revalidate'
        assert resp.headers['etag'] == '"None|None|None|None"'

    def test_strategy_with_mode_proxy_cache_get(self, app_user, registry):
        from adhocracy_core.interfaces import HTTPCacheMode
        registry.settings['adhocracy_core.caching.http.mode'] =\
             HTTPCacheMode.with_proxy_cache.name
        resp = app_user.get('/', status=200)
        assert resp.headers['Cache-control'] ==\
               'max-age=0, proxy-revalidate, s-maxage=31104000'
        assert resp.headers['Vary'] == 'X-User-Path, X-User-Token'
        assert resp.headers['etag'] == '"None|None|None|None"'

    def test_strategy_not_modified_if_modified_since_request(self, app_user,
                                                             context):
        from datetime import datetime
        context.modification_date = datetime(2015, 1, 1)
        resp = app_user.get('/', status=304, headers={'If-Modified-Since':
                                                      'Fri, 23 Jan 2000 15:19:22 GMT'})
        assert resp.status == '304 Not Modified'

    def test_strategy_ok_if_modified_since_request_without_modification_date(
            self, app_user):
        resp = app_user.get('/', status=200)
        assert resp.status == '200 OK'

    def test_strategy_not_modified_if_none_match_request(self, app_user):
        resp = app_user.get('/', status=304, headers={'If-None-Match':
                                                      'None|None|None|None'})
        assert resp.status == '304 Not Modified'

    def test_strategy_ok_if_none_match_request_without_etag(self, app_user):
        from adhocracy_core.caching import HTTPCacheStrategyWeakAdapter
        HTTPCacheStrategyWeakAdapter.etags = tuple()  # braking test isolation
        resp = app_user.get('/', status=200, headers={'If-None-Match':
                                                      'None|None|None|None'})
        assert resp.status == '200 OK'

