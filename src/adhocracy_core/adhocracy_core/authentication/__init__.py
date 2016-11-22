"""Authentication with support for token http headers."""
from pyramid_jwt import JWTAuthenticationPolicy
from collections import OrderedDict
from pyramid.authentication import CallbackAuthenticationPolicy
from pyramid.interfaces import IAuthenticationPolicy
from pyramid.interfaces import IRequest
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.security import Everyone
from zope.interface import implementer

from adhocracy_core.interfaces import error_entry


UserTokenHeader = 'X-User-Token'
"""The request header parameter to set the authentication token."""

UserPasswordHeader = 'X-User-Password'
"""The request header parameter to set the user password."""

UserPathHeader = 'X-User-Path'
"""Deprecated: The optional request header to set the userid."""


AnonymizeHeader = 'X-Anonymize'
"""Mark this request to be anonymized."""


@implementer(IAuthenticationPolicy)
class TokenHeaderAuthenticationPolicy(JWTAuthenticationPolicy):
    """Http header token authentication based on :mod:`pyramid_jwt`.

    The following methods are extendend:

    * `remember` return a list with the header/value to authenticate

    * `effective_principals` cache principals for one request
    """

    def __init__(self, private_key: str,
                 callback: callable=None,
                 timeout: int=10,
                 algorithm='HS512',
                 ):
        super().__init__(private_key,
                         http_header=UserTokenHeader,
                         expiration=timeout,
                         callback=callback,
                         algorithm=algorithm,
                         )

    def remember(self, request, userid, **kw) -> [tuple]:
        """Create persistent user session and return authentication headers."""
        token = self.create_token(userid)
        return [(UserTokenHeader, token)]

    def unauthenticated_userid(self, request):
        claims = getattr(request, 'jwt_claims', None)
        if claims is None:
            claims = self.get_claims(request)
            setattr(request, 'jwt_claims', claims)
        return claims.get('sub', None)

    def effective_principals(self, request: IRequest) -> list:
        """Return userid, roles and groups for the authenticated user.

        THE RESULT IS CACHED for the current request in the request attribute
        called: __cached_principals__ .
        """
        cached_principals = getattr(request, '__cached_principals__', None)
        if cached_principals:
            return cached_principals
        else:
            principals = super().effective_principals(request)
            request.__cached_principals__ = principals
            return principals


def validate_user_headers(view: callable):
    """Decorator vor :term:`view` to check if the user token.

    :raise pyramid.httpexceptions.HTTPBadRequest: if user token is invalid
    """
    def wrapped_view(context, request):
        token_is_set = UserTokenHeader in request.headers
        authenticated_is_empty = request.authenticated_userid is None
        if token_is_set and authenticated_is_empty:
            error = error_entry('header',
                                UserTokenHeader,
                                'Invalid user token')
            request.errors.append(error)
            raise HTTPBadRequest()
        return view(context, request)
    return wrapped_view


def has_password_header(request: IRequest) -> bool:
    """Check if request provided the password in the Password header."""
    return UserPasswordHeader in request.headers


def get_header_password(request: IRequest) -> str:
    """Return the password in the Password header."""
    return request.headers.get(UserPasswordHeader, None)


def validate_password_header(view: callable):
    """Decorator vor :term:`view` to check if the password header may be set.

    :raise pyramid.httpexceptions.HTTPBadRequest: if password is invalid or not
    required. The case that a password is required by a sheet but not set
    cannot be handled here, as we do not know which sheets are edited by the
    request.
    """
    def wrapped_view(context, request):
        password_is_set = has_password_header(request)
        error = None
        if password_is_set:
            content = request.registry.content
            user = request.user
            password = get_header_password(request)
            is_valid = user.is_password_valid(request.registry, password)
            if not is_valid:
                error = error_entry('header',
                                    UserPasswordHeader,
                                    'Invalid password')
            is_required_by_some_sheets = \
                content.is_password_required(context, request)
            if not is_required_by_some_sheets:
                error = error_entry('header',
                                    UserPasswordHeader,
                                    'Password not required')
        if error:
            request.errors.append(error)
            raise HTTPBadRequest()
        return view(context, request)
    return wrapped_view


def is_marked_anonymize(request: IRequest) -> bool:
    """Check if request is marked with the Anonymize header."""
    return AnonymizeHeader in request.headers


def validate_anonymize_header(view: callable):
    """Decorator vor :term:`view` to check if the anonymize header may be set.

    :raise pyramid.httpexceptions.HTTPBadRequest: if anonymize header is set
        but is not allowed
    """
    def wrapped_view(context, request):
        has_anonymize_header = is_marked_anonymize(request)
        content = request.registry.content
        if has_anonymize_header:
            if request.method == 'POST':
                if request.path == '/batch' or request.path == '/api/batch':
                    allowed = True
                else:
                    allowed = content.can_add_anonymized(context, request)
            elif request.method == 'PUT':
                allowed = content.can_edit_anonymized(context, request)
            elif request.method == 'DELETE':
                allowed = content.can_delete_anonymized(context, request)
            else:
                # for other methods the header makes no sense,
                # we ignore it to simplify the frontend code
                allowed = True
            if not allowed:
                error = error_entry('header',
                                    AnonymizeHeader,
                                    'Anonymize header not allowed')
                request.errors.append(error)
                raise HTTPBadRequest()
        return view(context, request)
    return wrapped_view


@implementer(IAuthenticationPolicy)
class MultiRouteAuthenticationPolicy(CallbackAuthenticationPolicy):
    """Use different policy to authenticate depending on the request route."""

    def __init__(self):
        self.policies = OrderedDict()

    def add_policy(self, route_name: str, policy: IAuthenticationPolicy):
        """Add `policy` for `route_name`."""
        self.policies[route_name] = policy

    def unauthenticated_userid(self, request: IRequest) -> str:
        """Return unauthenticated_userid of policy with matching route name."""
        policy = self._get_matching_policy(request)
        if policy:
            return policy.unauthenticated_userid(request)
        else:
            return None

    def effective_principals(self, request: IRequest):
        """Return principals of policy with matching route name."""
        policy = self._get_matching_policy(request)
        if policy:
            return policy.effective_principals(request)
        else:
            return [Everyone]

    def _get_matching_policy(self, request: IRequest) -> IAuthenticationPolicy:
        route_name = getattr(request.matched_route, 'name', None)
        for policy_route_name, policy in self.policies.items():
            if policy_route_name == route_name:
                return policy
        return None

    def remember(self, request: IRequest, principal, **kwargs) -> [tuple]:
        """Return headers to remember authenticated user for all policies."""
        headers = []
        for policy in self.policies.values():
            policy_headers = policy.remember(request, principal, **kwargs)
            headers.extend(policy_headers)
        return headers

    def forget(self, request: IRequest) -> [tuple]:
        """Return headers to forget authenticated user for all policies."""
        headers = []
        for policy in self.policies.values():
            policy_headers = policy.forget(request)
            headers.extend(policy_headers)
        return headers


def set_anonymized_creator(context: object, userid: str):
    """Store userid of anonymized creator of `context`."""
    setattr(context, '__anonymized_creator__', userid)


def get_anonymized_creator(context: object) -> str:
    """Get userid of anonymized creator of `context` or empty string."""
    userid = getattr(context, '__anonymized_creator__', '')
    return userid


def is_created_anonymized(context: object) -> bool:
    """Check if `context` was created anonymized."""
    is_created_anonymized = bool(get_anonymized_creator(context))
    return is_created_anonymized


def includeme(config):  # pragma: no cover
    """Add request properties."""
    from adhocracy_core.resources.principal import get_user_or_anonymous
    from adhocracy_core.resources.principal import get_anonymized_user
    config.add_request_method(get_user_or_anonymous,
                              name='user',
                              reify=True)
    config.add_request_method(get_anonymized_user,
                              name='anonymized_user',
                              reify=True)
    config.add_request_method(get_header_password,
                              name='password',
                              reify=True)
    config.include('.service_konto')
