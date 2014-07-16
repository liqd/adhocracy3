import unittest
from mock import Mock

from pyramid import testing
import pytest


class TokenManagerUnitTest(unittest.TestCase):

    def setUp(self):
        from datetime import datetime
        self.context = testing.DummyResource()
        self.secret = 'secret'
        self.user_id = '/principals/user/1'
        self.token = 'secret'
        self.timestamp = datetime.now()

    def _make_one(self, context, **kw):
        from adhocracy.authentication import TokenMangerAnnotationStorage
        return TokenMangerAnnotationStorage(context, **kw)

    def test_create(self):
        from adhocracy.interfaces import ITokenManger
        from zope.interface.verify import verifyObject
        inst = self._make_one(self.context, secret=self.secret, timeout=1)
        assert verifyObject(ITokenManger, inst)
        assert ITokenManger.providedBy(inst)

    def test_create_token_with_user_id_first_time(self):
        inst = self._make_one(self.context)
        token = inst.create_token(self.user_id)
        assert len(token) >= 128

    def test_create_token_with_user_id_second_time(self):
        inst = self._make_one(self.context)
        token = inst.create_token(self.user_id)
        token_second = inst.create_token(self.user_id)
        assert token != token_second

    def test_get_user_id_with_existing_token(self):
        inst = self._make_one(self.context)
        inst._token_to_user_id_date[self.token] = (self.user_id, self.timestamp)
        assert inst.get_user_id(self.token) == self.user_id

    def test_get_user_id_with_multiple_existing_token(self):
        inst = self._make_one(self.context)
        inst._token_to_user_id_date[self.token] = (self.user_id, self.timestamp)
        token_second = 'secret_second'
        inst._token_to_user_id_date[token_second] = (self.user_id, self.timestamp)
        assert inst.get_user_id(token_second) == self.user_id

    def test_get_user_id_with_non_existing_token(self):
        inst = self._make_one(self.context)
        with pytest.raises(KeyError):
            inst.get_user_id('wrong_token')

    def test_get_user_id_with_existing_token_but_passed_timeout(self):
        inst = self._make_one(self.context, timeout=0)
        inst._token_to_user_id_date[self.token] = (self.user_id, self.timestamp)
        with pytest.raises(KeyError):
            inst.get_user_id(self.token)

    def test_delete_token_with_non_existing_user_id(self):
        inst = self._make_one(self.context)
        assert inst.delete_token('wrong_token') == None

    def test_delete_token_with_existing_user_id(self):
        inst = self._make_one(self.context)
        inst._token_to_user_id_date[self.token] = (self.user_id, self.timestamp)
        inst.delete_token(self.token)
        assert self.token not in inst._token_to_user_id_date


class TokenHeaderAuthenticationPolicy(unittest.TestCase):

    def _make_one(self, tokenmanager,  secret, **kw):
        from adhocracy.authentication import TokenHeaderAuthenticationPolicy
        return TokenHeaderAuthenticationPolicy(tokenmanager, secret, **kw)

    def setUp(self):
        self.request = testing.DummyRequest()
        self.user_id = 'principals/users/1'
        self.token = 'secret'
        self.token_and_user_id_headers = {'X-User-Token': self.token,
                                          'X-User-Path': self.user_id}

    def test_create_without_tokenmanager(self):
        from pyramid.interfaces import IAuthenticationPolicy
        from zope.interface.verify import verifyObject
        inst = self._make_one(None, 'secret')
        assert verifyObject(IAuthenticationPolicy, inst)
        assert inst.callback is None
        assert inst._tokenmanager is None

    def test_create_with_tokenmanager_and_secret_and_timeout(self):
        from adhocracy.authentication import CallbackToTokenMangerAdapter
        tokenmanager = testing.DummyResource()
        inst = self._make_one(tokenmanager, 'secret', timeout=1)
        assert isinstance(inst.callback, CallbackToTokenMangerAdapter)
        assert inst._tokenmanager is tokenmanager
        assert inst._tokenmanager.secret == 'secret'
        assert inst._tokenmanager.timeout == 1

    def test_unauthenticated_userid_without_header(self):
        inst = self._make_one(None, 'secret')
        assert inst.unauthenticated_userid(self.request) is None

    def test_unauthenticated_userid_with_header(self):
        inst = self._make_one(None, 'secret')
        self.request.headers = self.token_and_user_id_headers
        assert inst.unauthenticated_userid(self.request) == self.user_id

    def test_authenticated_userid_withou_headers_and_callback_returns_None(self):
        def callback(userid, request):
            return None
        inst = self._make_one(None, 'secret')
        inst.callback = callback
        assert inst.authenticated_userid(self.request) is None

    def test_authenticated_userid_with_header_and_callback_returns_groups(self):
        def callback(userid, request):
            return ['group']
        inst = self._make_one(None, 'secret')
        inst.callback = callback
        self.request.headers = self.token_and_user_id_headers
        assert inst.authenticated_userid(self.request) == self.user_id

    def test_effective_principals_without_headers(self):
        from pyramid.security import Everyone
        inst = self._make_one(None, 'secret')
        assert inst.effective_principals(self.request) == [Everyone]

    def test_effective_principals_without_headers_and_callback_returns_None(self):
        from pyramid.security import Everyone
        def callback(userid, request):
            return None
        inst = self._make_one(None, 'secret')
        inst.callback = callback
        assert inst.effective_principals(self.request) == [Everyone]

    def test_effective_principals_with_headers_and_call_returns_groups(self):
        from pyramid.security import Everyone
        from pyramid.security import Authenticated
        def callback(userid, request):
            return ['group']
        inst = self._make_one(None, 'secret')
        inst.callback = callback
        self.request.headers = self.token_and_user_id_headers
        result = inst.effective_principals(self.request)
        assert result == [Everyone, Authenticated, self.user_id, 'group']

    def test_remember_without_tokenmanager(self):
        inst = self._make_one(None, 'secret')
        result = inst.remember(self.request, self.user_id)
        assert result == {'X-User-Path': None, 'X-User-Token': None}

    def test_remember_with_tokenmanger(self):
        tokenmanager = Mock()
        inst = self._make_one(tokenmanager, 'secret')
        tokenmanager.create_token.return_value = self.token
        result = inst.remember(self.request, self.user_id)
        assert result == self.token_and_user_id_headers

    def test_forget_without_tokenmanager(self):
        inst = self._make_one(None, 'secret')
        self.request.headers = self.token_and_user_id_headers
        assert inst.forget(self.request) == {}

    def test_forget_with_tokenmanger(self):
        tokenmanager = Mock()
        inst = self._make_one(tokenmanager, 'secret')
        self.request.headers = self.token_and_user_id_headers
        assert inst.forget(self.request) == {}
        assert tokenmanager.delete_token.is_called


class CallbackToTokenMangerAdapter(unittest.TestCase):

    def _make_one(self, tokenmanager):
        from adhocracy.authentication import CallbackToTokenMangerAdapter
        return CallbackToTokenMangerAdapter(tokenmanager)

    def setUp(self):
        self.request = testing.DummyRequest()
        self.user_id = 'principals/users/1'
        self.token = 'secret'
        self.token_and_user_id_headers = {'X-User-Token': self.token,
                                          'X-User-Path': self.user_id}
        self.tokenmanager = Mock()

    def test_create(self):
        inst = self._make_one(self.tokenmanager)
        assert callable(inst)

    def test_without_headers(self):
        inst = self._make_one(self.tokenmanager)
        assert inst(self.user_id, self.request) is None

    def test_with_headers(self):
        inst = self._make_one(self.tokenmanager)
        self.request.headers = self.token_and_user_id_headers
        self.tokenmanager.get_user_id.return_value = self.user_id
        assert inst(self.user_id, self.request) == self.user_id

    def test_with_headers_but_wrong_user_id(self):
        inst = self._make_one(self.tokenmanager)
        self.request.headers = self.token_and_user_id_headers
        user_id = 'wrong'
        assert inst(user_id, self.request) is None


class TokenHeaderAuthenticationPolicyIntegrationTest(unittest.TestCase):

    def setUp(self):
        config = testing.setUp()
        config.include('adhocracy.authentication')
        self.config = config
        self.request = testing.DummyRequest(registry=self.config.registry)
        self.context = testing.DummyResource()
        self.user_id = '/principals/user/1'

    def _register_authentication_policy(self):
        from adhocracy.authentication import TokenHeaderAuthenticationPolicy
        from adhocracy.authentication import TokenMangerAnnotationStorage
        from pyramid.authorization import ACLAuthorizationPolicy
        tokenmanager = TokenMangerAnnotationStorage(self.context)
        authz_policy = ACLAuthorizationPolicy()
        self.config.set_authorization_policy(authz_policy)
        authn_policy = TokenHeaderAuthenticationPolicy(tokenmanager, 'secret')
        self.config.set_authentication_policy(authn_policy)

    def test_remember(self):
        from pyramid.security import remember
        self._register_authentication_policy()
        headers = remember(self.request, self.user_id)
        assert headers['X-User-Path'] == self.user_id
        assert headers['X-User-Token'] is not None


class IncludemeIntegrationTest(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.config.include('adhocracy.authentication')
        self.context = testing.DummyResource()

    def test_get_adapter(self):
        from zope.component import getAdapter
        from adhocracy.interfaces import ITokenManger
        from zope.interface.verify import verifyObject
        inst = getAdapter(self.context, ITokenManger)
        assert verifyObject(ITokenManger, inst)
