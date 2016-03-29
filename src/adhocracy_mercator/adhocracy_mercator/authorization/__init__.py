from pyramid.security import Allow
from adhocracy_core.authorization import IRootACMExtension
from adhocracy_core.interfaces import IResource
from adhocracy_core.schema import  ACM


# flake8: noqa


def root_acm_extension_adapter(root: IResource) -> dict:
    """Adpater to extend the `root_acm`."""
    acm = \
        {'principals':                                   ['everyone', 'authenticated', 'participant', 'moderator',  'creator', 'initiator', 'admin'],
         'permissions': [  # general
                         ['view',                          Allow,      Allow,          Allow,         Allow,        Allow,     Allow,       Allow],
                         ['create',                        None,       None,           Allow,         Allow,        None,      Allow,       Allow],
                         ]}
    return acm


def includeme(config):
    config.registry.registerAdapter(root_acm_extension_adapter,
                                    (IResource,),
                                    IRootACMExtension)
