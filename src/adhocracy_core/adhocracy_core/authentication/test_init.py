import unittest
from unittest.mock import Mock
import unittest

from pyramid import testing
from pyramid.httpexceptions import HTTPBadRequest
from pytest import fixture
from pytest import raises
from pytest import mark


@fixture
def registry(registry_with_content):
    return registry_with_content


class TestTokenHeaderAuthenticationPolicy:

    def make_one(self, secret, **kw):
        from adhocracy_core.authentication import TokenHeaderAuthenticationPolicy
        return TokenHeaderAuthenticationPolicy(secret, **kw)

    @fixture
    def inst(self):
        return self.make_one('secret')

    def test_create(self):
        inst = self.make_one('secret')
        assert inst.private_key == 'secret'

    def test_implements_authentication_policy(self, inst):
        from pyramid.interfaces import IAuthenticationPolicy
        from zope.interface.verify import verifyObject
        assert verifyObject(IAuthenticationPolicy, inst)
        assert IAuthenticationPolicy.providedBy(inst)

    def test_subclasses_jwt_policy(self, inst):
        from pyramid_jwt import JWTAuthenticationPolicy
        assert isinstance(inst, JWTAuthenticationPolicy)

    def test_create_with_kwargs(self):
        callback = lambda x: x
        timeout = 100
        inst = self.make_one('secret', callback=callback,
                             timeout=timeout, algorithm='HS534')
        assert inst.callback is callback
        assert inst.expiration.seconds == timeout
        assert inst.algorithm == 'HS534'

    def test_effective_principals_returns_super(self, inst, mocker, request_):
        mocker.patch('pyramid_jwt.JWTAuthenticationPolicy.effective_principals',
                     return_value=['principal1'])
        assert inst.effective_principals(request_) == ['principal1']

    def test_effective_principals_set_cache(self, inst, mocker, request_):
        mocker.patch('pyramid_jwt.JWTAuthenticationPolicy.effective_principals',
                     return_value=['principal1'])
        inst.effective_principals(request_)
        assert request_.__cached_principals__ == ['principal1']

    def test_effective_principals_get_cache(self, inst, request_):
        """The result is cached for one request!"""
        request_.__cached_principals__ = ['principal1']
        assert inst.effective_principals(request_) == ['principal1']

    def test_remember_returns_list_with_token_header(self, inst, request_):
        import jwt
        from . import UserTokenHeader
        header = inst.remember(request_, 'userid')[0]
        name = header[0]
        assert name == UserTokenHeader
        token = jwt.decode(header[1], 'secret')
        assert token

    def test_unauthenticated_userid_return_none_if_no_token(
        self, inst, request_):
        assert inst.unauthenticated_userid(request_) is None

    def test_unauthenticated_userid_return_none_if_invalid_jwt_token(
        self, inst, request_, mocker):
        from jwt import InvalidTokenError
        from . import UserTokenHeader
        mocker.patch('jwt.decode', side_effect=InvalidTokenError)
        request_.headers[UserTokenHeader] = 'tokenhash'
        assert inst.unauthenticated_userid(request_) is None

    def test_unauthenticated_userid_return_none_if_not_jwt_token(
        self, inst, request_, mocker):
        from jwt import DecodeError
        from . import UserTokenHeader
        mocker.patch('jwt.decode', side_effect=DecodeError)
        request_.headers[UserTokenHeader] = 'tokenhash'
        assert inst.unauthenticated_userid(request_) is None

    def test_unauthenticated_userid_return_userid_if_valid_jwt_token(
        self, inst, request_, mocker):
        from . import UserTokenHeader
        payload = {'sub': 'userid'}
        mocker.patch('jwt.decode', return_value = payload)
        request_.headers[UserTokenHeader] = 'tokenhash'
        assert inst.unauthenticated_userid(request_) == 'userid'

    def test_unauthenticated_userid_return_cached_userid(
        self, inst, request_, mocker):
        from . import UserTokenHeader
        payload = {'sub': 'userid'}
        mocker.patch('jwt.decode', return_value = payload)
        request_.headers[UserTokenHeader] = 'tokenhash'
        inst.unauthenticated_userid(request_)
        del request_.headers[UserTokenHeader]
        assert inst.unauthenticated_userid(request_) == 'userid'


class TokenHeaderAuthenticationPolicyIntegrationTest(unittest.TestCase):

    def setUp(self):
        from substanced.interfaces import IService
        config = testing.setUp()
        config.include('adhocracy_core.content')
        config.include('adhocracy_core.resources.principal')
        self.config = config
        context = testing.DummyResource(__provides__=IService)
        context['principals'] = testing.DummyResource(__provides__=IService)
        context['principals']['users'] = testing.DummyResource(
            __provides__=IService)
        user = testing.DummyResource()
        context['principals']['users']['1'] = user
        self.user_id = '/principals/users/1'
        self.request = testing.DummyRequest(registry=config.registry,
                                            root=context,
                                            context=user)
        self.user_url = self.request.application_url + self.user_id + '/'

    def _register_authentication_policy(self):
        from adhocracy_core.authentication import TokenHeaderAuthenticationPolicy
        from pyramid.authorization import ACLAuthorizationPolicy
        authz_policy = ACLAuthorizationPolicy()
        self.config.set_authorization_policy(authz_policy)
        authn_policy = TokenHeaderAuthenticationPolicy('secret')
        self.config.set_authentication_policy(authn_policy)

    def test_remember(self):
        from pyramid.security import remember
        self._register_authentication_policy()
        headers = dict(remember(self.request, self.user_id))
        assert headers['X-User-Token'] is not None


def test_validate_user_headers_call_view_if_authenticated(context, request_):
    from . import validate_user_headers
    view = Mock()
    request_.headers['X-User-Token'] = 2
    request_.authenticated_userid = object()
    validate_user_headers(view)(context, request_)
    view.assert_called_with(context, request_)


def test_validate_user_headers_raise_if_authentication_failed(context,
                                                               request_):
    from pyramid.httpexceptions import HTTPBadRequest
    from . import validate_user_headers
    view = Mock()
    request_.headers['X-User-Token'] = 2
    request_.authenticated_userid = None
    with raises(HTTPBadRequest):
        validate_user_headers(view)(context, request_)


class TestMultiRouteAuthenticationPolicy:

    @fixture
    def inst(self):
        from . import MultiRouteAuthenticationPolicy
        return MultiRouteAuthenticationPolicy()

    @fixture
    def policy(self, mocker):
        from pyramid.interfaces import IAuthenticationPolicy
        return mocker.Mock(spec=IAuthenticationPolicy)()

    @fixture
    def other_policy(self, mocker):
        from pyramid.interfaces import IAuthenticationPolicy
        return mocker.Mock(spec=IAuthenticationPolicy)()

    @fixture
    def route(self, mocker):
        from pyramid.interfaces import IRoute
        return mocker.Mock(spec=IRoute,
                           name='route_name')()

    def test_is_authentication_policy(self, inst):
        from pyramid.interfaces import IAuthenticationPolicy
        from zope.interface.verify import verifyObject
        assert IAuthenticationPolicy.providedBy(inst)
        assert verifyObject(IAuthenticationPolicy, inst)

    def test_is_subclass_of_callback_policy(self, inst):
        from pyramid.authentication import CallbackAuthenticationPolicy
        assert isinstance(inst, CallbackAuthenticationPolicy)

    def test_add_policy(self, inst, policy):
        inst.add_policy('route_name', policy)
        assert inst.policies['route_name'] is policy

    def test_get_matching_policy_return_none_if_no_policy(self, request_, inst):
        request_.matched_route = None
        inst.policies = {}
        assert inst._get_matching_policy(request_) is None

    def test_get_matching_policy_return_none_if_wrong_policy(
        self, request_, inst, policy):
        request_.matched_route = None
        inst.policies = {'other_policy': policy}
        assert inst._get_matching_policy(request_) is None

    def test_get_matching_policy_return_policy_if_none_matches(
        self, request_, inst, policy):
        request_.matched_route = None
        inst.policies = {None: policy}
        assert inst._get_matching_policy(request_) is policy

    def test_get_matching_policy_return_policy_if_route_name_matches(
        self, request_, inst, policy, other_policy, route):
        request_.matched_route = route
        inst.policies = {route.name: policy,
                         'other_route': other_policy}
        assert inst._get_matching_policy(request_) is policy

    def test_unauthenticated_userid_return_none_if_no_policy_policy_machted(
        self, request_, inst, mocker):
        inst._get_matching_policy = mocker.Mock(return_value=None)
        assert inst.unauthenticated_userid(request_) is None

    def test_unauthenticated_userid_return_userid_of_matched_policy(
        self, inst, request_, policy, mocker):
        inst._get_matching_policy = mocker.Mock(return_value=policy)
        policy.unauthenticated_userid.return_value = 'userid'
        assert inst.unauthenticated_userid(request_) == 'userid'

    def test_effective_principals_return_everyone_if_no_policy_policy_machted(
        self, request_, inst, mocker):
        from pyramid.security import Everyone
        inst._get_matching_policy = mocker.Mock(return_value=None)
        assert inst.effective_principals(request_) == [Everyone]

    def test_effective_principals_return_principals_of_matched_policy(
        self, inst, request_, policy, mocker):
        inst._get_matching_policy = mocker.Mock(return_value=policy)
        policy.effective_principals.return_value = ['Group1']
        assert inst.effective_principals(request_) == ['Group1']

    def test_remember_return_empty_list_if_no_policies(self, inst, request_):
        assert inst.remember(request_, 'principal') == []

    def test_remember_return_headers_of_all_policies(
        self, inst, request_, policy, other_policy):
        inst.policies['route1'] = policy
        policy.remember.return_value = [('1', '1')]
        inst.policies['route2'] = other_policy
        other_policy.remember.return_value = [('2', '2')]
        assert inst.remember(request_, 'principal') == [('1','1'), ('2', '2')]

    def test_forget_return_empty_list_if_no_policies(self, inst, request_):
        assert inst.forget(request_) == []

    def test_forget_return_headers_of_all_policies(
        self, inst, request_, policy, other_policy):
        inst.policies['route1'] = policy
        policy.forget.return_value = [('1', '1')]
        inst.policies['route2'] = other_policy
        other_policy.forget.return_value = [('2', '2')]
        assert inst.forget(request_) == [('1','1'), ('2', '2')]


def test_is_header_password_true_if_password_header(request_):
    from . import is_header_password
    from . import UserPasswordHeader
    request_.headers[UserPasswordHeader] = 'pwd'
    assert is_header_password(request_) is True


def test_is_header_password_false_if_no_password_header(request_):
    from . import is_header_password
    assert is_header_password(request_) is False


def test_get_header_password_true_if_password_header(request_):
    from . import get_header_password
    from . import UserPasswordHeader
    request_.headers[UserPasswordHeader] = 'pwd'
    assert get_header_password(request_) is 'pwd'


def test_get_header_password_false_if_no_password_header(request_):
    from . import get_header_password
    assert get_header_password(request_) is None


class TestValidatePasswordHeader:

    def call_fut(self, *args):
        from . import validate_password_header
        return validate_password_header(*args)

    @fixture
    def view(self):
        return Mock()

    @fixture
    def mock_header_password(self, mocker):
        return mocker.patch(
            'adhocracy_core.authentication.is_header_password',
            return_value=True)

    @fixture
    def mock_get_password(self, mocker):
        return mocker.patch(
            'adhocracy_core.authentication.get_header_password',
            return_value='123456')

    @fixture
    def request_(self, request_, registry):
        from adhocracy_core.resources.principal import  User
        user = Mock(spec=User)
        request_.user = user
        request_.registry = registry
        return request_

    def test_ignore_if_no_password_header(self, context, request_, view):
        self.call_fut(view)(context, request_)
        view.assert_called_with(context, request_)

    def test_invalid_password(self, context, request_, view,
                                   mock_header_password,
                                   mock_get_password):
        request_.user.is_password_valid.return_value = False
        with raises(HTTPBadRequest):
            self.call_fut(view)(context, request_)

    def test_password_not_required(self, context, request_, registry, view,
                                   mock_header_password,
                                   mock_get_password):
        request_.user.is_password_valid.return_value = True
        registry.content.is_password_required.return_value = False
        with raises(HTTPBadRequest):
            self.call_fut(view)(context, request_)

    def test_valid_and_required(self, context, request_, registry, view,
                                   mock_header_password,
                                   mock_get_password):
        request_.user.is_password_valid.return_value = True
        registry.content.is_password_required.return_value = True
        self.call_fut(view)(context, request_)
        view.assert_called_with(context, request_)

def test_is_marked_anonymize_true_if_anonymize_header(request_):
    from . import is_marked_anonymize
    from . import AnonymizeHeader
    request_.headers[AnonymizeHeader] = ''
    assert is_marked_anonymize(request_) is True


def test_is_marked_anonymize_false_if_no_anonymize_header(request_):
    from . import is_marked_anonymize
    assert is_marked_anonymize(request_) is False


def test_is_created_anonymized_true_if_anonymized_creator(context, mocker):
    from . import is_created_anonymized
    mocker.patch('adhocracy_core.authentication.get_anonymized_creator',
                 return_value='userid')
    assert is_created_anonymized(context)


def test_is_created_anonymized_false_if_no_anonymized_creator(context, mocker):
    from . import is_created_anonymized
    mocker.patch('adhocracy_core.authentication.get_anonymized_creator',
                 return_value=None)
    assert not is_created_anonymized(context)


def test_set_anonymized_creator(context):
    from . import set_anonymized_creator
    set_anonymized_creator(context, 'userid')
    assert context.__anonymized_creator__ == 'userid'


def test_get_anonymized_creator_return_emptry_string_if_not_set(context):
    from . import get_anonymized_creator
    assert get_anonymized_creator(context) == ''


def test_get_anonymized_creator_return_userid_if_set(context):
    from . import get_anonymized_creator
    context.__anonymized_creator__ = 'userid'
    assert get_anonymized_creator(context) == 'userid'


class TestValidateAnonymizeHeader:

    def call_fut(self, *args):
        from . import validate_anonymize_header
        return validate_anonymize_header(*args)

    @fixture
    def view(self):
        return Mock()

    @fixture
    def mock_is_anonymized(self, mocker):
        return mocker.patch('adhocracy_core.authentication.is_marked_anonymize')

    @fixture
    def request_(self, request_, registry):
        request_.registry = registry
        return request_

    def test_ignore_if_not_anonymized_request(self, context, request_, view,
                                              mock_is_anonymized):
        mock_is_anonymized.return_value = False
        self.call_fut(view)(context, request_)
        view.assert_called_with(context, request_)

    def test_ignore_if_anonymied_post_batch_request(
            self, context, request_, view, mock_is_anonymized):
        mock_is_anonymized.return_value = True
        request_.method = 'POST'
        request_.path = '/batch'
        self.call_fut(view)(context, request_)

    @mark.parametrize("request_method, allow_method, allowed, expected",
                      [('POST', 'can_add_anonymized', True, None),
                       ('POST', 'can_add_anonymized', False, HTTPBadRequest),
                       ('PUT', 'can_edit_anonymized', True, None),
                       ('PUT', 'can_edit_anonymized', False, HTTPBadRequest),
                       ('DELETE', 'can_delete_anonymized', True, None),
                       ('DELETE', 'can_delete_anonymized', False, HTTPBadRequest),
                       ('GET',    '',                      None,  None),
                       ('OPTIONS','',                      None,  None),
                       ])
    def test_validate_anonymized_request(
            self, context, request_, registry, view, mock_is_anonymized,
            request_method, allow_method, allowed, expected):
        mock_is_anonymized.return_value = True
        if allow_method:
            mock_allow = getattr(registry.content, allow_method)
            mock_allow.return_value = allowed
        request_.method = request_method

        if expected is None:
            self.call_fut(view)(context, request_)
            view.assert_called_with(context, request_)
        else:
            with raises(HTTPBadRequest):
                self.call_fut(view)(context, request_)
