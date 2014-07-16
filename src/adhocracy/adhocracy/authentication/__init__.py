"""Token based pyramid authentication policy."""
import hashlib
from datetime import datetime

from persistent.dict import PersistentDict
from zope.interface import implementer

from adhocracy.interfaces import ITokenManger
from adhocracy.interfaces import ILocation


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

    def __init__(self, context: ILocation, secret: str='', hashalg='sha512',
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


def includeme(config):
    """Register the TokenManger adapter."""
    config.registry.registerAdapter(TokenMangerAnnotationStorage,
                                    required=(ILocation,),
                                    provided=ITokenManger,
                                    )
