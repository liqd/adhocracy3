"""Root module to set global permissions."""

# flake8: noqa

from adhocracy_core.schema import ACM

euth_acm = ACM().deserialize(
    {'principals':            ['anonymous', 'authenticated', 'participant', 'moderator',  'creator', 'initiator', 'admin'],
     'permissions': [['view',  'Allow',      'Deny',          'Allow',       'Allow',      'Allow',   'Allow',     'Allow'],
                     ]})