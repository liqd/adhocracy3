"""Custom system index views."""
from pyramid.traversal import get_current_registry

from adhocracy_core.sheets.principal import IUserBasic
from adhocracy_core.sheets.principal import IUserExtended


def index_user_text(resource, default) -> str:
    """Return text index for users."""
    registry = get_current_registry(resource)
    name = getattr(resource, '__name__', '')
    name_text_index = _get_text_index(name)
    user_name = registry.content.get_sheet_field(resource, IUserBasic, 'name')
    user_name_text_index = _get_text_index(user_name)
    user_email = registry.content.get_sheet_field(resource,
                                                  IUserExtended,
                                                  'email')
    user_email_text_index = _get_text_index(user_email)
    text_index = ' '.join([name_text_index,
                           user_name_text_index,
                           user_email_text_index])
    return text_index


def _get_text_index(string):
    """Copied from substanced/catalog/system.py."""
    val = string
    for char in (',', '-', '_', '.'):
        val = ' '.join([x.strip() for x in val.split(char)])
    if val != string:
        return string + ' ' + val
    return string


def includeme(config):
    """Overload system catalog index views."""
    config.add_indexview(index_user_text,
                         catalog_name='system',
                         index_name='text',
                         context=IUserBasic,
                         )
    config.add_indexview(index_user_text,
                         catalog_name='system',
                         index_name='text',
                         context=IUserExtended,
                         )
