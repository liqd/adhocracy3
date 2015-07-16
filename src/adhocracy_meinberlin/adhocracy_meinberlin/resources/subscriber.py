"""Initialize meinberlin ACM."""
from pyramid.events import ApplicationCreated
from pyramid.traversal import find_interface
from pyramid.renderers import render

from adhocracy_core.interfaces import IResourceCreatedAndAdded
from adhocracy_core.authorization import set_acms_for_app_root
from adhocracy_core.resources.root import root_acm
from adhocracy_core.utils import get_sheet
from adhocracy_core.utils import get_sheet_field
from adhocracy_meinberlin.resources.root import meinberlin_acm
from adhocracy_meinberlin.resources.bplan import IProposalVersion
from adhocracy_meinberlin.resources.bplan import IProposal
from adhocracy_meinberlin import sheets
from adhocracy_meinberlin import resources


def _send_bplan_submission_confirmation_email_subscriber(event):
    if not hasattr(event.registry, 'messenger'):  # ease testing
        return
    messenger = event.registry.messenger
    proposal_version = event.object
    proposal_item = find_interface(proposal_version, IProposal)
    if not _bplan_proposal_has_been_created(proposal_item):
        return
    proposal_values = _get_proposal_values(proposal_version)
    process_settings = _get_process_settings(proposal_item)
    if process_settings['plan_number'] == 0 or process_settings['office_worker'] is None:
        return
    templates_values = _get_templates_values(process_settings, proposal_values)
    subject = 'Ihre Stellungnahme zum Bebauungsplan {plan_number}, ' \
              '{participation_kind}, von {participation_start_date:%d/%m/%Y} - {participation_end_date:%d/%m/%Y}.' \
              .format(**process_settings)
    messenger.send_mail(subject,
                        [proposal_values['email']],
                        'noreply@mein.berlin.de',
                        render('adhocracy_meinberlin:templates/bplan_submission_confirmation.txt.mako',
                               templates_values))
    messenger.send_mail(subject,
                        [process_settings['office_worker'].email],
                        'noreply@mein.berlin.de',
                        render('adhocracy_meinberlin:templates/bplan_submission_confirmation.txt.mako',
                               templates_values))


def _get_templates_values(process_settings, proposal_values):
    templates_values = proposal_values.copy()
    templates_values.update(process_settings)
    return templates_values


def _get_process_settings(proposal_item):
    process = find_interface(proposal_item, resources.bplan.IProcess)
    process_settings = get_sheet(process, sheets.bplan.IProcessSettings).get()
    return process_settings


def _get_proposal_values(proposal_version):
    proposal_sheet = get_sheet(proposal_version, sheets.bplan.IProposal)
    proposal_values = proposal_sheet.get()
    return proposal_values


def _bplan_proposal_has_been_created(proposal):
    return len([version for version in proposal.values() if
                IProposalVersion.providedBy(version)]) == 2


def set_root_acms(event):
    """Set :term:`acm`s for root if the Pyramid application starts."""
    set_acms_for_app_root(event.app, (meinberlin_acm, root_acm))


def includeme(config):
    """Register subscribers."""
    config.add_subscriber(set_root_acms, ApplicationCreated)
    config.add_subscriber(_send_bplan_submission_confirmation_email_subscriber,
                          IResourceCreatedAndAdded, object_iface=IProposalVersion)
