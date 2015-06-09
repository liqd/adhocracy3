"""Scripts to migrate legacy objects in existing databases."""
import logging  # pragma: no cover
from substanced.util import find_catalog  # pragma: no cover
from adhocracy_core.evolution import migrate_new_sheet
from adhocracy_core.evolution import migration_script

logger = logging.getLogger(__name__)  # pragma: no cover


@migration_script
def evolve1_add_ititle_sheet_to_proposals(root):  # pragma: no cover
    """Migrate title value from ole IIntroduction sheet to ITitle sheet."""
    from pyramid.threadlocal import get_current_registry
    from adhocracy_mercator.resources.mercator import IMercatorProposalVersion
    from adhocracy_mercator.sheets.mercator import ITitle
    from adhocracy_mercator.sheets.mercator import IMercatorSubResources
    from adhocracy_mercator.sheets.mercator import IIntroduction
    from zope.interface import alsoProvides
    from adhocracy_core.utils import get_sheet_field
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


@migration_script
def evolve2_disable_add_proposal_permission(root):  # pragma: no cover
    """Disable add_proposal permissions."""
    from adhocracy_core.authorization import set_acl
    from substanced.util import get_acl
    from pyramid.threadlocal import get_current_registry
    from pyramid.security import Deny

    registry = get_current_registry()
    acl = get_acl(root)
    deny_acl = [(Deny, 'role:contributor', 'add_proposal'),
                (Deny, 'role:creator', 'edit_mercator_proposal')]
    updated_acl = deny_acl + acl
    set_acl(root, updated_acl, registry=registry)


@migration_script
def evolve3_use_adhocracy_core_title_sheet(root):  # pragma: no cover
    """Migrate mercator title sheet to adhocracy_core title sheet."""
    from adhocracy_core.sheets.title import ITitle
    from adhocracy_mercator.sheets import mercator
    from adhocracy_mercator.resources.mercator import IMercatorProposalVersion
    migrate_new_sheet(root, IMercatorProposalVersion, ITitle, mercator.ITitle,
                      remove_isheet_old=True,
                      fields_mapping=[('title', 'title')])


@migration_script
def evolve4_disable_voting_and_commenting(root):
    """Disable rate and comment permissions."""
    from adhocracy_core.authorization import set_acl
    from substanced.util import get_acl
    from pyramid.threadlocal import get_current_registry
    from pyramid.security import Deny

    registry = get_current_registry()
    acl = get_acl(root)
    deny_acl = [(Deny, 'role:annotator', 'add_comment'),
                (Deny, 'role:annotator', 'add_rate'),
                (Deny, 'role:creator', 'edit_comment'),
                (Deny, 'role:creator', 'edit_rate')]
    updated_acl = deny_acl + acl
    set_acl(root, updated_acl, registry=registry)


@migration_script
def change_mercator_type_to_iprocess(root):
    """Change mercator type from IBasicPoolWithAssets to IProcess."""
    from adhocracy_mercator.resources.mercator import IProcess
    from pyramid.threadlocal import get_current_registry
    from adhocracy_core import sheets

    registry = get_current_registry()
    old_mercator = root['mercator']
    root.rename('mercator', 'old_mercator')
    appstructs = {sheets.name.IName.__identifier__: {'name': 'mercator'}}
    new_mercator = registry.content.create(IProcess.__identifier__,
                                           parent=root,
                                           appstructs=appstructs)
    for name in old_mercator.keys():
        old_mercator.move(name, new_mercator)
    root.remove('old_mercator')


def includeme(config):  # pragma: no cover
    """Register evolution utilities and add evolution steps."""
    config.add_evolution_step(evolve1_add_ititle_sheet_to_proposals)
    config.add_evolution_step(evolve2_disable_add_proposal_permission)
    config.add_evolution_step(evolve3_use_adhocracy_core_title_sheet)
    config.add_evolution_step(evolve4_disable_voting_and_commenting)
    config.add_evolution_step(change_mercator_type_to_iprocess)
