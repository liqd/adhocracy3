"""Token based pyramid authentication policy."""
import hashlib
from datetime import datetime

from persistent.dict import PersistentDict
from pyramid.authentication import CallbackAuthenticationPolicy
from pyramid.interfaces import IAuthenticationPolicy
from pyramid.request import Request
from zope.interface import implementer
from zope.interface import Interface

from adhocracy.interfaces import ITokenManger


@implementer(ITokenManger)
class TokenMangerAnnotationStorage:

    """Manage authentication tokens and use object annotation to store them.

    Constructor arguments::

    :param context: the object to annotate the authentication token storage.
    :param secret:  the secret used to salt the generated authentication token.
    :param hashalg: Any hash algorithm supported by :func: `hashlib.new`.
                    This is used to create the authentication token.
    :param timeout:  Maximum number of seconds which a newly create token
                     will be considered valid.
                     The `None` value is allowed to disable the timeout.
    """

    annotation_key = '_tokenmanager_storage'

    def __init__(self, context, secret: str='', hashalg='sha512',
                 timeout: float=None):
        self.context = context
        self.secret = secret
        self.hash_function = getattr(hashlib, hashalg)
        self.timeout = timeout

    @property
    def _token_to_user_id_date(self):
        if not hasattr(self.context, self.annotation_key):
            setattr(self.context, self.annotation_key, PersistentDict())
        return getattr(self.context, self.annotation_key)

    def create_token(self, user_id: str) -> str:
        """Create authentication token for user_id."""
        timestamp = datetime.now()
        token = self._build_token(user_id, timestamp)
        self._token_to_user_id_date[token] = (user_id, timestamp)
        return token

    def _build_token(self, user_id: str, timestamp: datetime) -> str:
        time_bytes = timestamp.isoformat().encode('UTF-8')
        secret_bytes = self.secret.encode('UTF-8', 'replace')
        user_bytes = user_id.encode('UTF-8', 'replace')
        hash_obj = self.hash_function(secret_bytes + time_bytes + user_bytes)
        return hash_obj.hexdigest()

    def get_user_id(self, token: str) -> str:
        """Get user_id for authentication token.

        :returns: user id for this token
        :raises KeyError: if there is no corresponding user_id
        """
        user_id, timestamp = self._token_to_user_id_date[token]
        if self._is_expired(timestamp):
            del self._token_to_user_id_date[token]
            raise KeyError
        return user_id

    def _is_expired(self, timestamp: datetime) -> bool:
        if self.timeout is None:
            return False
        now = datetime.now()
        delta = now - timestamp
        return delta.total_seconds() >= self.timeout

    def delete_token(self, token: str):
        """Delete authentication token."""
        if token in self._token_to_user_id_date:
            del self._token_to_user_id_date[token]


def _get_x_user_headers(request: Request) -> tuple:
    """Return tuple with the X-User-Path/Token values or (None, None)."""
    return (request.headers.get('X-User-Path', None),
            request.headers.get('X-User-Token', None))


class CallbackToTokenMangerAdapter:

    """Callback adapter for :class: `adhocracy.interfaces.ITokenManager`.

    `Callback` is a function to check authentication and return the ACL groups
    of the authenticated user, that can be passed to:
    :class:'pyramid.authentication.CallbackAuthenticationPolicy`.
    """

    def __init__(self, tokenmanager: ITokenManger):
        self.tokenmanager = tokenmanager

    def __call__(self, user_id, request) -> list:
        unauthenticated_user_id, token = _get_x_user_headers(request)
        try:
            authenticated_user_id = self.tokenmanager.get_user_id(token)
            if authenticated_user_id == unauthenticated_user_id:
                return authenticated_user_id
        except KeyError:
            pass


@implementer(IAuthenticationPolicy)
class TokenHeaderAuthenticationPolicy(CallbackAuthenticationPolicy):

    """A :term:`authentication policy` based on the the X-User-* header.

    To authenticate the client has to send http header with `X-User-Token`
    and `X-User-Path`.

    Constructor Arguments

    :param tokenmanager: TokenManger to generate the callback function
    :param secret: random string to salt the generated token.
    :param timeout:  Maximum number of seconds which a newly create token
                     will be considered valid.
                     The `None` value is allowed to disable the timeout.
    """

    debug = False  # enable debug logging
    callback = None  # callable to check

    def __init__(self, tokenmanager, secret, timeout=None):
        if tokenmanager:
            self.callback = CallbackToTokenMangerAdapter(tokenmanager)
            tokenmanager.secret = secret
            tokenmanager.timeout = timeout
        self._tokenmanager = tokenmanager

    def unauthenticated_userid(self, request):
        return _get_x_user_headers(request)[0]

    def remember(self, request, user_id, **kw):
        if self._tokenmanager:
            token = self._tokenmanager.create_token(user_id)
        else:
            token = None
            user_id = None
        return {'X-User-Path': user_id,
                'X-User-Token': token}

    def forget(self, request):
        if self._tokenmanager:
            token = _get_x_user_headers(request)[0]
            self._tokenmanager.delete_token(token)
        return {}


def includeme(config):
    """Register the TokenManger adapter."""
    config.registry.registerAdapter(TokenMangerAnnotationStorage,
                                    required=(Interface,),
                                    provided=ITokenManger,
                                    )
