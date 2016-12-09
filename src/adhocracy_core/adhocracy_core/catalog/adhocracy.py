"""Adhocracy catalog and index views."""
import math

from pyramid.traversal import resource_path
from pyramid.traversal import find_interface
from pyramid.traversal import get_current_registry
from substanced import catalog
from substanced.catalog import IndexFactory
from substanced.util import find_service
from adhocracy_core.catalog.index import ReferenceIndex
from adhocracy_core.exceptions import RuntimeConfigurationError
from adhocracy_core.utils import is_hidden
from adhocracy_core.interfaces import IItem
from adhocracy_core.interfaces import search_query
from adhocracy_core.resources.comment import ICommentVersion
from adhocracy_core.sheets.comment import ICommentable
from adhocracy_core.sheets.comment import IComment
from adhocracy_core.sheets.metadata import IMetadata
from adhocracy_core.sheets.rate import IRate
from adhocracy_core.sheets.rate import IRateable
from adhocracy_core.sheets.tags import ITags
from adhocracy_core.sheets.title import ITitle
from adhocracy_core.sheets.badge import IBadgeAssignment
from adhocracy_core.sheets.badge import IBadgeable
from adhocracy_core.sheets.versions import IVersionable
from adhocracy_core.sheets.workflow import IWorkflowAssignment
from adhocracy_core.sheets.principal import IUserBasic
from adhocracy_core.sheets.principal import IUserExtended
from adhocracy_core.sheets.principal import IServiceKonto


class Reference(IndexFactory):
    """TODO: comment."""

    index_type = ReferenceIndex


class AdhocracyCatalogIndexes:
    """Default indexes for the adhocracy catalog.

    Indexes starting with `private_` are private (not queryable from the
    frontend).
    """

    tag = catalog.Keyword()
    private_visibility = catalog.Keyword()  # visible / hidden
    badge = catalog.Keyword()
    item_badge = catalog.Keyword()
    title = catalog.Field()
    rate = catalog.Field()
    rates = catalog.Field()
    comments = catalog.Field()
    controversiality = catalog.Field()
    creator = catalog.Field()
    item_creation_date = catalog.Field()
    workflow_state = catalog.Field()
    reference = Reference()
    user_name = catalog.Field()
    private_user_email = catalog.Field()
    private_user_activation_path = catalog.Field()
    private_service_konto_userid = catalog.Field()


def index_creator(resource, default) -> str:
    """Return creator userid value for the creator index."""
    registry = get_current_registry(resource)
    creator = registry.content.get_sheet_field(resource, IMetadata, 'creator')
    if creator == '':  # FIXME the default value should be None
        return creator
    userid = resource_path(creator)
    return userid


def index_item_creation_date(resource, default) -> str:
    """Return creator userid value for the creator index."""
    registry = get_current_registry(resource)
    date = registry.content.get_sheet_field(resource, IMetadata,
                                            'item_creation_date')
    return date


def index_visibility(resource, default) -> [str]:
    """Return value for the private_visibility index.

    Te return value will be one of [visible], [hidden]
    """
    if is_hidden(resource):
        result = ['hidden']
    else:
        result = ['visible']
    return result


def index_title(resource, default) -> str:
    """Return the value of field name ` title`."""
    registry = get_current_registry(resource)
    title = registry.content.get_sheet_field(resource, ITitle, 'title')
    return title


def index_rate(resource, default) -> int:
    """Return the value of field name `rate` for :class:`IRate` resources."""
    registry = get_current_registry(resource)
    rate = registry.content.get_sheet_field(resource, IRate, 'rate')
    return rate


def index_rates(resource, default) -> int:
    """
    Return aggregated values of referenceing :class:`IRate` resources.

    Only the LAST version of each rate is counted.
    """
    catalogs = find_service(resource, 'catalogs')
    query = search_query._replace(interfaces=IRate,
                                  frequency_of='rate',
                                  indexes={'tag': 'LAST'},
                                  references=[(None, IRate, 'object', resource)
                                              ],
                                  )
    result = catalogs.search(query)
    rate_sum = 0
    for value, count in result.frequency_of.items():
        rate_sum += value * count
    return rate_sum


def index_controversiality(resource, default) -> int:
    """Return metric based on number up/down rates and comments.

    Only the LAST version of each rate is counted.
    """
    catalogs = find_service(resource, 'catalogs')
    query = search_query._replace(interfaces=IRate,
                                  frequency_of='rate',
                                  indexes={'tag': 'LAST'},
                                  only_visible=True,
                                  references=[(None, IRate, 'object', resource)
                                              ],
                                  )
    result = catalogs.search(query)
    up_rates = result.frequency_of.get(1, 0)
    down_rates = result.frequency_of.get(-1, 0)
    controversiality = math.sqrt(up_rates * down_rates)
    return controversiality


def index_comments(resource, default) -> int:
    """
    Return aggregated values of comments below the `item` parent of `resource`.

    Only the LAST version of each rate is counted.
    """
    catalogs = find_service(resource, 'catalogs')
    query = search_query._replace(interfaces=ICommentVersion,
                                  indexes={'tag': 'LAST'},
                                  only_visible=True,
                                  references=[(None, IComment, 'refers_to',
                                               resource)
                                              ],
                                  )
    result = catalogs.search(query)
    comment_count = result.count
    if comment_count:
        comment_count += _index_comment_replies(result.elements, default)
    return comment_count


def _index_comment_replies(comment_list, default) -> int:
    comment_count = 0
    for comment in comment_list:
        comment_count += index_comments(comment, default)
    return comment_count


def index_tag(resource, default) -> [str]:
    """Return value for the tag index."""
    item = find_interface(resource, IItem)
    if item is None:  # ease testing
        return
    registry = get_current_registry(resource)
    tags_sheet = registry.content.get_sheet(item, ITags)
    tagnames = [f for f, v in tags_sheet.get().items() if v is resource]
    return tagnames if tagnames else default


def index_badge(resource, default) -> [str]:
    """Return value for the badge index."""
    catalogs = find_service(resource, 'catalogs')
    reference = (None, IBadgeAssignment, 'object', resource)
    query = search_query._replace(references=[reference],
                                  only_visible=True,
                                  )
    assignments = catalogs.search(query).elements
    badge_names = []
    for assignment in assignments:
        reference = (assignment, IBadgeAssignment, 'badge', None)
        query = search_query._replace(references=[reference],
                                      only_visible=True,
                                      )
        badges = catalogs.search(query).elements
        badge_names += [b.__name__ for b in badges]
    return badge_names


def index_item_badge(resource, default) -> [str]:
    """Find item and return its badge names for the item_badge index."""
    item = find_interface(resource, IItem)
    if item is None:
        return default
    badge_names = index_badge(item, default)
    return badge_names


def index_workflow_state(resource, default) -> str:
    """Return value for the workflow_state index."""
    registry = get_current_registry(resource)
    try:
        state = registry.content.get_sheet_field(resource,
                                                 IWorkflowAssignment,
                                                 'workflow_state')
    except (RuntimeConfigurationError, KeyError):
        return default
    return state


def index_workflow_state_of_item(resource, default) -> [str]:
    """Find item and return it`s value for the workflow_state index."""
    item = find_interface(resource, IItem)
    if item:
        return index_workflow_state(item, default)
    else:
        return default


def index_user_name(resource, default) -> str:
    """Return value for the user_name index."""
    registry = get_current_registry(resource)
    name = registry.content.get_sheet_field(resource,
                                            IUserBasic,
                                            'name')
    return name


def index_user_email(resource, default) -> str:
    """Return value for the private_user_email index."""
    registry = get_current_registry(resource)
    name = registry.content.get_sheet_field(resource,
                                            IUserExtended,
                                            'email')
    return name


def index_user_activation_path(resource, default) -> str:
    """Return value for the private_user_activationpath index."""
    path = getattr(resource, 'activation_path', None)
    if path is None:
        return default
    return path


def index_service_konto_userid(resource, default) -> str:
    """Return value for the service konto index."""
    registry = get_current_registry(resource)
    userid = registry.content.get_sheet_field(resource,
                                              IServiceKonto,
                                              'userid')
    return userid


def includeme(config):
    """Register adhocracy catalog factory."""
    config.add_catalog_factory('adhocracy', AdhocracyCatalogIndexes)
    config.add_indexview(index_visibility,
                         catalog_name='adhocracy',
                         index_name='private_visibility',
                         context=IMetadata,
                         )
    config.add_indexview(index_creator,
                         catalog_name='adhocracy',
                         index_name='creator',
                         context=IMetadata,
                         )
    config.add_indexview(index_item_creation_date,
                         catalog_name='adhocracy',
                         index_name='item_creation_date',
                         context=IMetadata,
                         )
    config.add_indexview(index_title,
                         catalog_name='adhocracy',
                         index_name='title',
                         context=ITitle,
                         )
    config.add_indexview(index_rate,
                         catalog_name='adhocracy',
                         index_name='rate',
                         context=IRate)
    config.add_indexview(index_rates,
                         catalog_name='adhocracy',
                         index_name='rates',
                         context=IRateable)
    config.add_indexview(index_controversiality,
                         catalog_name='adhocracy',
                         index_name='controversiality',
                         context=IRateable)
    config.add_indexview(index_comments,
                         catalog_name='adhocracy',
                         index_name='comments',
                         context=ICommentable)
    config.add_indexview(index_tag,
                         catalog_name='adhocracy',
                         index_name='tag',
                         context=IVersionable,
                         )
    config.add_indexview(index_badge,
                         catalog_name='adhocracy',
                         index_name='badge',
                         context=IBadgeable,
                         )
    config.add_indexview(index_item_badge,
                         catalog_name='adhocracy',
                         index_name='item_badge',
                         context=IVersionable,
                         )
    config.add_indexview(index_workflow_state,
                         catalog_name='adhocracy',
                         index_name='workflow_state',
                         context=IWorkflowAssignment,
                         )
    config.add_indexview(index_workflow_state_of_item,
                         catalog_name='adhocracy',
                         index_name='workflow_state',
                         context=IVersionable,
                         )
    config.add_indexview(index_user_name,
                         catalog_name='adhocracy',
                         index_name='user_name',
                         context=IUserBasic,
                         )
    config.add_indexview(index_user_email,
                         catalog_name='adhocracy',
                         index_name='private_user_email',
                         context=IUserExtended,
                         )
    config.add_indexview(index_user_activation_path,
                         catalog_name='adhocracy',
                         index_name='private_user_activation_path',
                         context=IUserBasic,
                         )
    config.add_indexview(index_service_konto_userid,
                         catalog_name='adhocracy',
                         index_name='private_service_konto_userid',
                         context=IServiceKonto,
                         )
