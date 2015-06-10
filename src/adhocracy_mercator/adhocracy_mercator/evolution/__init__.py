"""Scripts to migrate legacy objects in existing databases."""
import logging  # pragma: no cover
from substanced.util import find_catalog  # pragma: no cover
from substanced.util import find_service
from adhocracy_core.evolution import migrate_new_sheet
from zope.interface import alsoProvides
from zope.interface import directlyProvides
from zope.interface import noLongerProvides

logger = logging.getLogger(__name__)  # pragma: no cover


def evolve1_add_ititle_sheet_to_proposals(root):  # pragma: no cover
    """Migrate title value from ole IIntroduction sheet to ITitle sheet."""
    from pyramid.threadlocal import get_current_registry
    from adhocracy_mercator.resources.mercator import IMercatorProposalVersion
    from adhocracy_mercator.sheets.mercator import ITitle
    from adhocracy_mercator.sheets.mercator import IMercatorSubResources
    from adhocracy_mercator.sheets.mercator import IIntroduction
    from zope.interface import alsoProvides
    from adhocracy_core.utils import get_sheet_field
    logger.info('Running substanced evolve step 1: add new ITitle sheet')
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
    logger.info('Finished substanced evolve step 1: add new ITitle sheet')


def evolve2_disable_add_proposal_permission(root):  # pragma: no cover
    """Disable add_proposal permissions."""
    from adhocracy_core.authorization import set_acl
    from substanced.util import get_acl
    from pyramid.threadlocal import get_current_registry
    from pyramid.security import Deny

    logger.info('Running substanced evolve step 2:'
                'remove add_proposal permission')

    registry = get_current_registry()
    acl = get_acl(root)
    deny_acl = [(Deny, 'role:contributor', 'add_proposal'),
                (Deny, 'role:creator', 'edit_mercator_proposal')]
    updated_acl = deny_acl + acl
    set_acl(root, updated_acl, registry=registry)

    logger.info('Finished substanced evolve step 2:'
                'remove add_proposal permission')


def evolve3_use_adhocracy_core_title_sheet(root):  # pragma: no cover
    """Migrate mercator title sheet to adhocracy_core title sheet."""
    from adhocracy_core.sheets.title import ITitle
    from adhocracy_mercator.sheets import mercator
    from adhocracy_mercator.resources.mercator import IMercatorProposalVersion
    migrate_new_sheet(root, IMercatorProposalVersion, ITitle, mercator.ITitle,
                      remove_isheet_old=True,
                      fields_mapping=[('title', 'title')])


def evolve4_disable_voting_and_commenting(root):
    """Disable rate and comment permissions."""
    from adhocracy_core.authorization import set_acl
    from substanced.util import get_acl
    from pyramid.threadlocal import get_current_registry
    from pyramid.security import Deny

    logger.info('Running substanced evolve step 3:'
                'remove add_rate, edit_rate, add_comment and'
                'edit_comment permissions')

    registry = get_current_registry()
    acl = get_acl(root)
    deny_acl = [(Deny, 'role:annotator', 'add_comment'),
                (Deny, 'role:annotator', 'add_rate'),
                (Deny, 'role:creator', 'edit_comment'),
                (Deny, 'role:creator', 'edit_rate')]
    updated_acl = deny_acl + acl
    set_acl(root, updated_acl, registry=registry)

    logger.info('Finished substanced evolve step 3:'
                'remove add_rate, edit_rate, add_comment and'
                'edit_comment permissions')


def change_mercator_type_to_iprocess(root):
    """Change mercator type from IBasicPoolWithAssets to IProcess with badges service."""
    from adhocracy_mercator.resources.mercator import IProcess
    from pyramid.threadlocal import get_current_registry
    from adhocracy_core.resources.asset import IPoolWithAssets
    from adhocracy_mercator.resources.mercator import process_meta
    from adhocracy_core.resources.badge import add_badges_service

    logger.info('Running evolve step:' + change_mercator_type_to_iprocess.__doc__)
    mercator = root['mercator']
    noLongerProvides(mercator, IPoolWithAssets)
    directlyProvides(mercator, IProcess)

    for sheet in process_meta.basic_sheets + process_meta.extended_sheets:
        alsoProvides(mercator, sheet)

    registry = get_current_registry()
    add_badges_service(mercator, registry, {})
    catalogs = find_service(root, 'catalogs')
    catalogs.reindex_index(mercator, 'interfaces')
    logger.info('Finished evolve step:' + change_mercator_type_to_iprocess.__doc__)


def includeme(config):  # pragma: no cover
    """Register evolution utilities and add evolution steps."""
    config.add_evolution_step(evolve1_add_ititle_sheet_to_proposals)
    config.add_evolution_step(evolve2_disable_add_proposal_permission)
    config.add_evolution_step(evolve3_use_adhocracy_core_title_sheet)
    config.add_evolution_step(evolve4_disable_voting_and_commenting)
    config.add_evolution_step(change_mercator_type_to_iprocess)
