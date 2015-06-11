"""Scripts to migrate legacy objects in existing databases."""
import logging  # pragma: no cover
from pyramid.threadlocal import get_current_registry
from pyramid.security import Deny
from substanced.util import get_acl
from substanced.util import find_catalog  # pragma: no cover
from adhocracy_core.authorization import set_acl
from adhocracy_core.evolution import migrate_new_sheet
from adhocracy_core.evolution import migrate_new_iresource
from adhocracy_core.evolution import log_migration
from adhocracy_core.utils import get_sheet_field
from substanced.util import find_service
from zope.interface import alsoProvides
from adhocracy_core.interfaces import search_query
from adhocracy_core.resources.badge import add_badge_assignments_service
from adhocracy_core.sheets.badge import IBadgeable
from adhocracy_mercator.resources.mercator import IMercatorProposalVersion
from adhocracy_mercator.sheets.mercator import ITitle
from adhocracy_mercator.sheets.mercator import IMercatorSubResources
from adhocracy_mercator.sheets.mercator import IIntroduction
from adhocracy_mercator.resources.mercator import IMercatorProposal

logger = logging.getLogger(__name__)  # pragma: no cover


@log_migration
def evolve1_add_ititle_sheet_to_proposals(root):  # pragma: no cover
    """Migrate title value from ole IIntroduction sheet to ITitle sheet."""
    registry = get_current_registry()
    catalog = find_catalog(root, 'system')
    path = catalog['path']
    interfaces = catalog['interfaces']
    query = path.eq('/mercator') \
        & interfaces.eq(IMercatorProposalVersion) \
        & interfaces.noteq(ITitle)
    proposals = query.execute()
    for proposal in proposals:
        logger.info('updating {0}'.format(proposal))
        introduction = get_sheet_field(proposal, IMercatorSubResources,
                                       'introduction')
        if introduction == '' or introduction is None:
            continue
        alsoProvides(proposal, ITitle)
        if 'title' not in introduction._sheets[IIntroduction.__identifier__]:
            continue
        value = introduction._sheets[IIntroduction.__identifier__]['title']
        title = registry.content.get_sheet(proposal, ITitle)
        title.set({'title': value})
        del introduction._sheets[IIntroduction.__identifier__]['title']


@log_migration
def evolve2_disable_add_proposal_permission(root):  # pragma: no cover
    """Disable add_proposal permissions."""
    registry = get_current_registry()
    acl = get_acl(root)
    deny_acl = [(Deny, 'role:contributor', 'add_proposal'),
                (Deny, 'role:creator', 'edit_mercator_proposal')]
    updated_acl = deny_acl + acl
    set_acl(root, updated_acl, registry=registry)


@log_migration
def evolve3_use_adhocracy_core_title_sheet(root):  # pragma: no cover
    """Migrate mercator title sheet to adhocracy_core title sheet."""
    from adhocracy_core.sheets.title import ITitle
    from adhocracy_mercator.sheets import mercator
    migrate_new_sheet(root, IMercatorProposalVersion, ITitle, mercator.ITitle,
                      remove_isheet_old=True,
                      fields_mapping=[('title', 'title')])


@log_migration
def evolve4_disable_voting_and_commenting(root):
    """Disable rate and comment permissions."""
    registry = get_current_registry()
    acl = get_acl(root)
    deny_acl = [(Deny, 'role:annotator', 'add_comment'),
                (Deny, 'role:annotator', 'add_rate'),
                (Deny, 'role:creator', 'edit_comment'),
                (Deny, 'role:creator', 'edit_rate')]
    updated_acl = deny_acl + acl
    set_acl(root, updated_acl, registry=registry)


@log_migration
def change_mercator_type_to_iprocess(root):
    """Change mercator type from IBasicPoolWithAssets to IProcess."""
    from adhocracy_mercator.resources.mercator import IProcess
    from adhocracy_core.resources.asset import IPoolWithAssets
    from adhocracy_core.resources.badge import add_badges_service
    migrate_new_iresource(root, IPoolWithAssets, IProcess)
    registry = get_current_registry()
    mercator = root['mercator']
    if find_service(mercator, 'badges') is None:
        add_badges_service(mercator, registry, {})


@log_migration
def add_badge_assignments_services_to_proposal_items(root):
    """Add badge assignments services to proposals."""
    catalogs = find_service(root, 'catalogs')
    query = search_query._replace(interfaces=IMercatorProposal)
    proposals = catalogs.search(query).elements
    registry = get_current_registry(root)
    for proposal in proposals:
        if find_service(proposal, 'badge_assignments') is None:
            logger.info('add badge assignments to {0}'.format(proposal))
            add_badge_assignments_service(proposal, registry, {})


@log_migration
def add_badgeable_sheet_to_proposal_versions(root):
    """Add badgeable sheet to proposals versions."""
    migrate_new_sheet(root, IMercatorProposalVersion, IBadgeable)


def includeme(config):  # pragma: no cover
    """Register evolution utilities and add evolution steps."""
    config.add_evolution_step(evolve1_add_ititle_sheet_to_proposals)
    config.add_evolution_step(evolve2_disable_add_proposal_permission)
    config.add_evolution_step(evolve3_use_adhocracy_core_title_sheet)
    config.add_evolution_step(evolve4_disable_voting_and_commenting)
    config.add_evolution_step(change_mercator_type_to_iprocess)
    config.add_evolution_step(add_badge_assignments_services_to_proposal_items)
    config.add_evolution_step(add_badgeable_sheet_to_proposal_versions)
