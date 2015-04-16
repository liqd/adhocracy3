"""Scripts to migrate legacy objects in existing databases."""
import logging  # pragma: no cover
from substanced.util import find_catalog  # pragma: no cover

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
    from substanced.util import set_acl
    from substanced.util import get_acl
    from pyramid.threadlocal import get_current_registry
    from pyramid.security import Deny

    logger.info('Running substanced evolve step 2:'
                'remove add_proposal permission')

    registry = get_current_registry()
    acl = get_acl(root)
    deny_acl = [(Deny, 'role:contributor', 'add_proposal'),
                (Deny, 'role:creator', 'add_mercator_proposal_version')]
    updated_acl = deny_acl + acl
    set_acl(root, updated_acl, registry=registry)
    # TODO substanced bug, _p_changed is not set
    root._p_changed = True

    logger.info('Finished substanced evolve step 2:'
                'remove add_proposal permission')


def evolve3_disable_voting_and_commenting(root):
    """Disable rate and comment permissions."""
    from substanced.util import set_acl
    from substanced.util import get_acl
    from pyramid.threadlocal import get_current_registry
    from pyramid.security import Deny

    logger.info('Running substanced evolve step 3:'
                'remove add_rate, add_rateversion, add_comment and'
                'add_commentversion permissions')

    registry = get_current_registry()
    acl = get_acl(root)
    deny_acl = [(Deny, 'role:annotator', 'add_comment'),
                (Deny, 'role:annotator', 'add_rate'),
                (Deny, 'role:creator', 'add_commentversion'),
                (Deny, 'role:creator', 'add_rateversion')]
    updated_acl = deny_acl + acl
    set_acl(root, updated_acl, registry=registry)
    # TODO substanced bug, _p_changed is not set
    root._p_changed = True

    logger.info('Finished substanced evolve step 3:'
                'remove add_rate, add_rateversion, add_comment and'
                'add_commentversion permissions')


def includeme(config):  # pragma: no cover
    """Register evolution utilities and add evolution steps."""
    config.add_evolution_step(evolve1_add_ititle_sheet_to_proposals)
    config.add_evolution_step(evolve2_disable_add_proposal_permission)
    config.add_evolution_step(evolve3_disable_voting_and_commenting)
