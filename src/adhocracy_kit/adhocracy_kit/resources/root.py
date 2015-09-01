"""Root resource type."""

# flake8: noqa

from pyramid.security import Allow
from pyramid.security import Deny

from adhocracy_core.schema import ACM


kit_acm = ACM().deserialize(
    {'principals':                                   ['anonymous', 'participant', 'moderator',  'creator', 'initiator', 'admin'],
     'permissions': [['create_user',                   Deny,       None,          None,         None,      None,        Allow],
                     ]})


def includeme(config):
    """Add resource type to content."""
