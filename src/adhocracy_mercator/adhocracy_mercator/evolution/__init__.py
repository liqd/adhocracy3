"""Scripts to migrate legacy objects in existing databases."""
import logging  # pragma: no cover
from substanced.util import find_catalog  # pragma: no cover
from adhocracy_core.evolution import migrate_new_sheet

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


def evolve3_use_adhocracy_core_title_sheet(root):  # pragma: no cover
    """Migrate mercator title sheet to adhocracy_core title sheet."""
    from adhocracy_core.sheets.title import ITitle
    from adhocracy_mercator.sheets import mercator
    from adhocracy_mercator.resources.mercator import IMercatorProposalVersion
    migrate_new_sheet(root, IMercatorProposalVersion, ITitle, mercator.ITitle,
                      remove_isheet_old=True,
                      fields_mapping=[('title', 'title')])


def includeme(config):  # pragma: no cover
    """Register evolution utilities and add evolution steps."""
    config.add_evolution_step(evolve1_add_ititle_sheet_to_proposals)
    config.add_evolution_step(evolve3_use_adhocracy_core_title_sheet)
